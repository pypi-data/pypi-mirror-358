import six
import time
import json
import logging
import queue
import websocket
import shlex
from threading import Thread
from concurrent.futures.thread import ThreadPoolExecutor

from portainer_api.api_client import ApiClient
from portainer_api.rest import ApiException
from portainer_api.configuration import Configuration as Config
from portainer_api.api import AuthApi
from portainer_api.models import AuthenticateUserRequest
from .endpoints_api import EndpointsApi

from janus.api.service import Service
from janus.api.constants import Constants, EPType
from janus.api.models import (
    Node,
    Network,
    ContainerProfile,
    SessionRequest,
    AddEndpointRequest
)
from janus.settings import REGISTRIES as iregs
from janus.settings import cfg, IGNORE_EPS
from janus.api.utils import (
    get_next_cport,
    get_next_sport,
    get_next_vf,
    get_next_ipv4,
    get_next_ipv6,
    get_numa,
    get_cpuset,
    get_mem,
    is_subset
)


log = logging.getLogger(__name__)
EDGE_AGENT_TYPE = 4

def auth(func):
    def wrapper(self, *args, **kwargs):
        def authenticate():
            pcfg = Config()
            pcfg.host = cfg.PORTAINER_URI
            pcfg.username = cfg.PORTAINER_USER
            pcfg.password = cfg.PORTAINER_PASSWORD
            pcfg.verify_ssl = cfg.PORTAINER_VERIFY_SSL

            if not pcfg.username or not pcfg.password:
                raise Exception("No Portainer username or password defined")
            self.client = ApiClient(pcfg)
            aa_api = AuthApi(self.client)
            res = aa_api.authenticate_user(AuthenticateUserRequest(pcfg.username, pcfg.password))
            pcfg.api_key = {'Authorization': res.jwt}
            pcfg.api_key_prefix = {'Authorization': 'Bearer'}

            log.debug("Authenticating with token: {}".format(res.jwt))
            self.client.jwt = res.jwt
            self.auth_expire = time.time() + 14400

        def try_authenticate_with_limit(retry_limit=3):
            for attempt in range(retry_limit):
                try:
                    authenticate()
                    return True
                except ApiException as e:
                    log.warning(f"Authentication attempt {attempt + 1} failed: {e}")
                    if attempt == retry_limit - 1:
                        log.error("Reached maximum retry limit for authentication")
                        raise
            return False

        if not self.client or not self.auth_expire or time.time() >= self.auth_expire:
            try_authenticate_with_limit()

        try:
            return func(self, *args, **kwargs)
        except ApiException as e:
            if e.status == 401:
                log.warning("Authentication failed, retrying...")
                if try_authenticate_with_limit():
                    return func(self, *args, **kwargs)
                else:
                    raise
            else:
                raise
    return wrapper


class PortainerDockerApi(Service):
    def __init__(self, api_client=None):
        self.auth_expire = None
        self.client = api_client

    @property
    @auth
    def auth_token(self):
        return self.client.jwt

    @property
    def type(self):
        return EPType.PORTAINER

    def _parse_portainer_endpoints(self, res):
        ret = dict()
        for e in res:
            ret[e['Name']] = {
                'name': e['Name'],
                'endpoint_status': e['Status'],
                'endpoint_type': EPType.PORTAINER,
                'backend_type': e['Type'],
                'id': e['Id'],
                'gid': e['GroupId'],
                'public_url': e['PublicURL']
            }
            if e['Type'] != EDGE_AGENT_TYPE:
                ret[e['Name']]['url'] = e['URL']
        return ret

    def _parse_portainer_networks(self, res):
        ret = dict()
        for e in res:
            key = e['Name']
            ret[key] = {
                'id': e['Id'],
                'driver': e['Driver'],
                'subnet': e['IPAM']['Config'],
                '_data': e
            }
            if e["Options"]:
                ret[key].update(e['Options'])
        return ret

    def _parse_portainer_images(self, res):
        ret = list()
        for e in res:
            if not e['RepoDigests'] and not e['RepoTags']:
                continue
            if e['RepoTags']:
                e['name'] = e['RepoTags'][0].split(":")[0]
                ret.extend(e['RepoTags'])
            elif e['RepoDigests']:
                e['name'] = e['RepoDigests'][0].split("@")[0]
                ret.extend(e['RepoDigests'])
            if e['name'] == '<none>':
                continue
        return ret

    def _get_endpoint_info(self, Id, url, nname, nodes, cb=None):
        try:
            nets = self.get_networks(Node(id=Id, name=nname))
            imgs = self.get_images(Node(id=Id, name=nname))
            docker = self._get_docker_info(Id)
        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error("No response from {}: {}".format(url, e))
            return nodes[nname]
        hinfo = {
            "cpu": {
                "count": docker.get("NCPU"),
                "brand_raw": docker.get("Architecture"),
            },
            "mem": {
                "total": docker.get("MemTotal")
            }
        }
        if nodes[nname].get('backend_type') == EDGE_AGENT_TYPE:
            nodes[nname]['url'] = docker['Name']
        nodes[nname]['host'] = hinfo
        nodes[nname]['networks'] = self._parse_portainer_networks(nets)
        nodes[nname]['images'] = self._parse_portainer_images(imgs)
        nodes[nname]['docker'] = docker
        if cb:
            cb(nodes[nname], nname, url)
        return nodes[nname]

    # Endpoints
    @auth
    def get_nodes(self, nname=None, cb=None, refresh=False):
        try:
            eapi = EndpointsApi(self.client)
            res = eapi.endpoint_list()
            # ignore some endpoints based on settings
            for r in res:
                if r['Name'] in IGNORE_EPS:
                    res.remove(r)
            nodes = self._parse_portainer_endpoints(res)
        except Exception as e:
            import traceback
            traceback.print_exc()
            log.error("Backend error: {}".format(e))
            return

        if refresh:
            try:
                futures = list()
                tp = ThreadPoolExecutor(max_workers=8)
                for k, v in nodes.items():
                    if nname and k != nname:
                        continue
                    futures.append(tp.submit(self._get_endpoint_info, v['id'], v['public_url'], k, nodes, cb))
                for future in futures:
                    try:
                        future.result(timeout=5)
                    except Exception as e:
                        log.error(f"Timeout waiting on endpoint query, continuing: {e}")
                        continue
            except Exception as e:
                import traceback
                traceback.print_exc()
                log.error("Backend error: {}".format(e))
                return

        return list(nodes.values())

    @auth
    def create_node(self, ep: AddEndpointRequest, **kwargs):
        eapi = EndpointsApi(self.client)
        eptype = 2 # We use Portainer Agent registration method
        kwargs = {"url": ep.url,
                  "public_url": ep.public_url,
                  "tls": "true",
                  "tls_skip_verify": "true",
                  "tls_skip_client_verify": "true"}
        return eapi.endpoint_create(ep.name, eptype, **kwargs)

    @auth
    def remove_node(self, nid):
        eapi = EndpointsApi(self.client)
        return eapi.endpoint_delete(nid)

    # Info
    def _get_docker_info(self, nid: int, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/info".format(nid),
                         "GET", None, **kwargs)
        string = res.read().decode('utf-8')
        return json.loads(string)

    # Images
    def get_images(self, node: Node, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/images/json".format(node.id),
                         "GET", None, **kwargs)
        string = res.read().decode('utf-8')
        return json.loads(string)

    def pull_image(self, node: Node, img, tag):
        kwargs = dict()
        headers = list()
        kwargs['_return_http_data_only'] = True
        kwargs['query'] = {"fromImage": img,
                           "tag": tag}
        parts = img.split("/")
        if parts[0] in iregs:
            auth = iregs[parts[0]].get("auth", None)
            if not auth:
                raise ApiException("503", f"Authentication not configured for registry {parts[0]}")
            headers.append(f"X-Registry-Auth: {auth}")
        res = self._call("/endpoints/{}/docker/images/create".format(node.id),
                         "POST", None, headers, **kwargs)
        string = res.read().decode('utf-8')
        ret = {"status": res.status}
        for s in string.splitlines():
            ret.update(json.loads(s))
        return ret

    # Containers
    def get_containers(self, node: Node, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/containers/json".format(node.id),
                         "GET", None, **kwargs)
        string = res.read().decode('utf-8')
        return json.loads(string)

    def inspect_container(self, node: Node, cid, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/containers/{}/json".format(node.id, cid),
                         "GET", None, **kwargs)
        string = res.read().decode('utf-8')
        return json.loads(string)

    def create_container(self, node: Node, image, name=None, **kwargs):
        body = {'Image': image}
        params = ['HostName', 'HostConfig', 'NetworkingConfig', 'ExposedPorts',
                  'Env', 'Tty', "MacAddress", 'StopSignal', 'Cmd', 'Entrypoint']
        for k, v in six.iteritems(kwargs):
            if k in params:
                body[k] = v
        kwargs = dict()
        kwargs['_return_http_data_only'] = True
        if name:
            kwargs['query'] = {"name": name}
        res = self._call("/endpoints/{}/docker/containers/create".format(node.id),
                         "POST", body, **kwargs)
        if (res.status == 502):
            return {'status': '{} Bad gateway'.format(res.status)}
        string = res.read().decode('utf-8')
        return json.loads(string)

    def start_container(self, node: Node, cid, service=None, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/containers/{}/start".format(node.id, cid),
                         "POST", None, **kwargs)
        if (res.status == 200 or res.status == 204):
            return {'status': '{} OK'.format(res.status)}
        string = res.read().decode('utf-8')
        return json.loads(string)

    def stop_container(self, node: Node, cid, **kwargs):
        nname = kwargs.get('name')
        kwargs = dict()
        kwargs['_return_http_data_only'] = True
        status = 204
        try:
            res = self._call("/endpoints/{}/docker/containers/{}/stop".format(node.id, cid),
                             "POST", None, **kwargs)
            status = res.status
        except ApiException as e:
            status = e.status
            # not modified, container is already stopped
            if e.status == 304:
                pass
            else:
                raise e
        return {'status': '{}'.format(status),
                'node_id': node.id, 'container_id': cid,
                'node_name': nname}

    def remove_container(self, node: Node, cid, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/containers/{}".format(node.id, cid),
                         "DELETE", None, **kwargs)
        if (res.status == 204):
            return {'status': '{} OK'.format(res.status)}
        string = res.read().decode('utf-8')
        return json.loads(string)

    # Networks
    def get_networks(self, node: Node, nid=None, **kwargs):
        kwargs['_return_http_data_only'] = True
        if nid:
            res = self._call("/endpoints/{}/docker/networks/{}".format(node.id, nid),
                             "GET", None, **kwargs)
        else:
            res = self._call("/endpoints/{}/docker/networks".format(node.id),
                             "GET", None, **kwargs)
        string = res.read().decode('utf-8')
        return json.loads(string)

    def connect_network(self, node: Node, nid, cid, **kwargs):
        body = {'Container': cid}
        params = ['EndpointConfig']
        for k, v in six.iteritems(kwargs):
            if k in params:
                body[k] = v
        kwargs = dict()
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/networks/{}/connect".format(node.id, nid),
                         "POST", body, **kwargs)
        string = res.read().decode('utf-8')
        if (res.status == 200):
            return {'status': '200 OK'}
        return json.loads(string)

    def create_network(self, node: Node, name, **kwargs):
        body = {'Name': name}
        params = ['CheckDuplicate', 'Driver', 'Internal', 'Attachable',
                  'Ingress', 'IPAM', 'EnableIPv6', 'Options', 'Labels']
        for k, v in six.iteritems(kwargs):
            if k in params:
                body[k] = v
        kwargs = dict()
        kwargs['_return_http_data_only'] = True
        self._call("/endpoints/{}/docker/networks/create".format(node.id),
                   "POST", body, **kwargs)
        res = self.get_networks(node, name)
        ninfo = self._parse_portainer_networks([res])[name]
        return ninfo

    def remove_network(self, node: Node, nid, **kwargs):
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/networks/{}".format(node.id, nid),
                         "DELETE", None, **kwargs)
        if (res.status == 204):
            return {'status': '{} OK'.format(res.status)}
        string = res.read().decode('utf-8')
        return json.loads(string)

    # Logs
    def get_logs(self, node: Node, cid, since=0, stderr=1, stdout=1, tail=100, timestamps=0):
        kwargs = dict()
        kwargs['_return_http_data_only'] = True
        kwargs['query'] = {
            'since': since,
            'stderr': stderr,
            'stdout': stdout,
            'tail': tail,
            'timestamps': timestamps
        }
        res = self._call("/endpoints/{}/docker/containers/{}/logs".format(node.id, cid),
                         "GET", None, **kwargs)
        string = res.read().decode('utf-8')
        return {"response": string}

    # Exec
    def exec_create(self, node: Node, cid, **kwargs):
        body = dict()
        params = ['AttachStdin', 'AttachStdout', 'AttachStderr', 'DetachKeys', 'Cmd', 'Env', 'Tty']
        for k, v in six.iteritems(kwargs):
            if k in params:
                body[k] = v
        kwargs = dict()
        kwargs['_return_http_data_only'] = True
        res = self._call("/endpoints/{}/docker/containers/{}/exec".format(node.id, cid),
                         "POST", body, **kwargs)
        string = res.read().decode('utf-8')
        return json.loads(string)

    def exec_start(self, node: Node, ectx, **kwargs):
        eid = ectx.get('Id')
        kwargs['_return_http_data_only'] = True
        body = {"Detach": False,
                "Tty": True}
        res = self._call("/endpoints/{}/docker/exec/{}/start".format(node.id, eid),
                         "POST", body, **kwargs)
        string = res.read().decode('utf-8')
        return {"response": string}

    def exec_stream(self, node, container, exec_id):
        ws_url = f"{cfg.PORTAINER_WS}/exec?token={self.client.jwt}&id={exec_id}&endpointId={node.id}"
        ws = websocket.create_connection(ws_url)

        send_queue = queue.Queue()
        receive_queue = queue.Queue()

        def send_messages(ws, send_queue):
            try:
                while True:
                    message = send_queue.get()
                    if message is None:
                        break
                    ws.send(message)
                    send_queue.task_done()
            except Exception as e:
                log.error(f"Error in sender thread: {e}")

        def receive_messages(ws, receive_queue):
            try:
                while True:
                    try:
                        response = ws.recv()
                        receive_queue.put(response)
                    except websocket.WebSocketConnectionClosedException as e:
                        if e.args and e.args[0] == 1006:
                            log.debug("Client disconnected abnormally (1006)")
                        else:
                            log.debug("WebSocket connection closed normally")
                        break
                    except Exception as e:
                        log.error(f"Unexpected error in receiver: {str(e)}")
                        break
            finally:
                receive_queue.put(None)

        sender_thread = Thread(target=send_messages, args=(ws, send_queue))
        receiver_thread = Thread(target=receive_messages, args=(ws, receive_queue))

        sender_thread.start()
        receiver_thread.start()

        return receive_queue, send_queue, ws, sender_thread, receiver_thread

    def close_stream(self, ws, send_queue, receive_queue, sender_thread, receiver_thread):
        send_queue.put(None)  # Signal sender thread to exit
        sender_thread.join()

        receiver_thread.join()  # Wait for receiver to finish
        ws.close()

    @auth
    def _call(self, url, method, body, headers=[], **kwargs):
        all_params = ['body', 'query']  # noqa: E501
        all_params.append('async_req')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in six.iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " in PortainerDockerApi" % key
                )
            params[key] = val
        del params['kwargs']

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'query' in params:
            query_params = params['query']

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = body
        if 'body' in params:
            body_params = params['body']
        # HTTP header `Accept`
        header_params['Accept'] = self.client.select_header_accept(
            ['application/json'])  # noqa: E501

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.client.select_header_content_type(  # noqa: E501
            ['application/json'])  # noqa: E501

        for hdr in headers:
            parts = hdr.split(":")
            assert (len(parts) == 2)
            header_params[parts[0]] = parts[1]

        # Authentication setting
        auth_settings = ['jwt']  # noqa: E501

        log.debug("Portainer-Docker call: {} {} body={}".format(method, url, body))
        log.debug("Query params: {}".format(query_params))
        log.debug("Header params: {}".format(header_params))

        return self.client.call_api(
            url, method,
            path_params,
            query_params,
            header_params,
            body=body_params,
            post_params=form_params,
            files=local_var_files,
            auth_settings=auth_settings,
            async_req=params.get('async_req'),
            _return_http_data_only=params.get('_return_http_data_only'),
            _preload_content=params.get('_preload_content', False),
            _request_timeout=params.get('_request_timeout'),
            collection_formats=collection_formats)

    # TODO Note node is of type tinydb.table.Document
    def resolve_networks(self, node, prof):
        def _build_kwargs(p):
            docker_kwargs = {
                "Name": p.name,
                "Driver": p.settings.driver,
                "EnableIPv6": p.settings.enable_ipv6
            }
            ipam = p.settings.ipam
            if ipam:
                docker_kwargs["IPAM"] = dict()
                docker_kwargs["IPAM"]["Config"] = list()
                for i in ipam.get('config'):
                    docker_kwargs["IPAM"]["Config"].append({"Subnet": i.get('subnet'),
                                                            "Gateway": i.get('gateway')})
            opts = p.settings.options
            if opts:
                docker_kwargs["Options"] = dict()
                if "mtu" in opts and p.settings.driver == "bridge":
                    docker_kwargs["Options"].update({"com.docker.network.driver.mtu": opts.get('mtu')})
                if "parent" in opts and p.settings.driver in ["macvlan", "ipvlan"]:
                    docker_kwargs["Options"].update({"parent": opts.get('parent')})
                if "macvlan_mode" in opts and p.settings.driver == "macvlan":
                    docker_kwargs["Options"].update({"macvlan_mode": opts.get('macvlan_mode')})
                if "ipvlan_mode" in opts and p.settings.driver == "ipvlan":
                    docker_kwargs["Options"].update({"ipvlan_mode": opts.get('ipvlan_mode')})
            return docker_kwargs

        created = False
        for net in [Network(prof.settings.mgmt_net), Network(prof.settings.data_net)]:
            if not net.name or net.name in [Constants.NET_NONE, Constants.NET_HOST, Constants.NET_BRIDGE]:
                continue
            nname = node.get('name')
            nprof = cfg.pm.get_profile(Constants.NET, net.name)
            if not nprof:
                raise Exception(f"Network profile {net.name} not found")

            kwargs = _build_kwargs(nprof)
            ninfo = None

            try:
                res = self.get_networks(Node(**node), net.name)
                ninfo = self._parse_portainer_networks([res])[net.name]

                if is_subset(kwargs, ninfo.get('_data')):
                    log.info(f"Matching Network {net.name} found on {nname}")
                    node['networks'][net.name] = ninfo
                    continue
            except ApiException as ae:
                if str(ae.status) != "404":
                    raise ae

            if ninfo:
                log.warning(f"Removing non matching network {net.name} on {nname}")
                self.remove_network(Node(**node), net.name)

                if net.name in node['networks']:
                    del node['networks'][net.name]

            ninfo = self.create_network(Node(**node), net.name, **kwargs)
            node['networks'][net.name] = ninfo
            created = True

        return created

    def create_service_record(self, sname, sreq: SessionRequest, addrs_v4, addrs_v6, cports, sports):
        srec = dict()
        node = sreq.node
        prof = sreq.profile
        nname = sreq.node.get('name')
        kwargs = sreq.kwargs
        qos = cfg.get_qos(prof["qos"]) if "qos" in prof else dict()
        dpr = prof.settings.data_port_range
        dnet = Network(prof.settings.data_net, nname)
        mnet = Network(prof.settings.mgmt_net, nname)
        priv = prof.settings.privileged
        sysd = prof.settings.systemd
        pull = prof.settings.pull_image
        args = prof.settings.arguments
        args_override = sreq.arguments
        cmd = None
        entrypoint = sreq.entrypoint
        dns = sreq.dns
        if args_override:
            cmd = shlex.split(args_override)
        elif args:
            cmd = shlex.split(args)

        vfid = None
        vfmac = None
        mgmt_ipv4 = None
        mgmt_ipv6 = None
        data_ipv4 = None
        data_ipv6 = None
        cport = get_next_cport(node, prof, cports)
        sport = get_next_sport(node, prof, sports)
        internal_port = prof.settings.internal_port or cport

        if dpr:
            dports = "{},{}".format(dpr[0],dpr[1])
        else:
            dports = ""

        mnet_kwargs = {}
        docker_kwargs = {
            "HostName": nname[0:63], # truncate to 63 characters
            "HostConfig": {
                "PortBindings": dict(),
                "NetworkMode": mnet.name,
                "Mounts": list(),
                "Devices": list(),
                "CapAdd": list(),
                "Ulimits": list(),
                "Privileged": priv,
                "Dns": dns
            },
            "ExposedPorts": dict(),
            "Env": [
                "HOSTNAME={}".format(node['public_url']),
                "CTRL_PORT={}".format(cport),
                "SERV_PORT={}".format(sport),
                "DATA_PORTS={}".format(dports),
                "USER_NAME={}".format(kwargs.get("USER_NAME", "")),
                "PUBLIC_KEY={}".format(kwargs.get("PUBLIC_KEY", "")),
                "DEPLOYMENT_KEY={}".format(kwargs.get("DEPLOYMENT_KEY", ""))
            ],
            "Tty": True,
            "StopSignal": "SIGRTMIN+3" if sysd else "SIGTERM",
            "Cmd": cmd,
            "Entrypoint": entrypoint
        }

        if sreq.remove_container:
            auto_remove = True
            docker_kwargs["HostConfig"].update({"Autoremove": auto_remove})

        if cport:
            docker_kwargs["HostConfig"]["PortBindings"].update({
                "{}/tcp".format(internal_port): [
                    {"HostPort": "{}".format(cport)}]
            })
            docker_kwargs["ExposedPorts"].update({
                "{}/tcp".format(internal_port): {}
            })

        if sport:
            docker_kwargs["HostConfig"]["PortBindings"].update({
                "{}/tcp".format(sport): [
                    {"HostPort": "{}".format(sport)}]
            })
            docker_kwargs["ExposedPorts"].update({
                "{}/tcp".format(sport): {}
            })

        if mnet.name and not mnet.is_host():
            try:
                minfo = node['networks'][mnet.name]
            except:
                raise Exception("Network not found: {}".format(mnet.name))
            mnet_type = minfo['driver']
            # Remove port mappings if control network requested is not bridge
            if mnet_type != Constants.NET_BRIDGE:
                del docker_kwargs["HostConfig"]["PortBindings"]
                del docker_kwargs["ExposedPorts"]

            if not mnet.is_host() and mnet_type != Constants.NET_BRIDGE:
                # Set mgmt net layer 3
                mgmt_ipv4 = get_next_ipv4(mnet, addrs_v4)
                mgmt_ipv6 = get_next_ipv6(mnet, addrs_v6)
                mnet_kwargs.update({"EndpointConfig": {
                    "IPAMConfig": {
                        "IPv4Address": mgmt_ipv4,
                        "IPv6Address": mgmt_ipv6
                    }
                }
                })

        # Constrain container memory if requested
        mem = get_mem(node, prof)
        if mem:
            docker_kwargs["HostConfig"].update({"Memory": mem})

        for e in prof.settings.environment:
            # XXX: do some sanity checking here
            docker_kwargs['Env'].append(e)

        for v in prof.settings.volumes:
            vol = cfg.pm.get_profile(Constants.VOL, v)
            if vol:
                readonly = True if "ReadOnly" in vol and vol['ReadOnly'] else False
                mnt = {'Type': vol.settings.type,
                       'Source': vol.settings.source,
                       'Target': vol.settings.target,
                       'ReadOnly': readonly
                }
                docker_kwargs['HostConfig']['Mounts'].append(mnt)
                if "driver" in vol:
                    docker_kwargs['HostConfig']['VolumeDriver'] = vol['driver']

        if dnet.name and not mnet.is_host():
            try:
                dinfo = node['networks'][dnet.name]
            except:
                raise Exception("Network not found: {}".format(dnet.name))
            # Pin CPUs based on data net
            cpus = get_cpuset(node, dnet.name, prof)
            if cpus:
                docker_kwargs["HostConfig"].update({"CpusetCpus": cpus})

            # Set data net layer 3
            data_ipv4 = get_next_ipv4(dnet, addrs_v4)
            data_ipv6 = get_next_ipv6(dnet, addrs_v6)
            docker_kwargs["HostConfig"].update({"NetworkMode": dnet.name})
            docker_kwargs.update({"NetworkingConfig": {
                "EndpointsConfig": {
                    dnet.name: {
                        "IPAMConfig": {
                            "IPv4Address": data_ipv4,
                            "IPv6Address": data_ipv6
                        }
                    }
                }
            }
            })
            docker_kwargs["Env"].append("DATA_IFACE={}".format(data_ipv4))

            # Need to specify and track sriov vfs explicitly
            ndrv = dinfo.get("driver", None)
            if ndrv == "sriov":
                (vfid, vfmac) = get_next_vf(node, dnet.name)
                #docker_kwargs['NetworkingConfig']['EndpointsConfig'][dnet.name]['IPAMConfig']['MacAddress'] = vfmac
        else:
            docker_kwargs["Env"].append("DATA_IFACE={}".format(node['public_url']))
            if not mnet.is_host() and dpr:
                for p in range(dpr[0], dpr[1]+1):
                    docker_kwargs["HostConfig"]["PortBindings"].update(
                        {"{}/tcp".format(p):
                         [{"HostPort": "{}".format(p)}]}
                    )
                    docker_kwargs["ExposedPorts"].update({"{}/tcp".format(p): {}})

        # handle features enabled for this service
        for f in prof.settings.features:
            feat = cfg.get_feature(f)
            if feat:
                caps = feat.get('caps', list())
                docker_kwargs['HostConfig']['CapAdd'].extend(caps)
                limits = feat.get('limits', list())
                docker_kwargs['HostConfig']['Ulimits'].extend(limits)

                devices = feat.get('devices', list())
                for d in devices:
                    if dnet.name:
                        if "rdma_cm" in d['names']:
                            dev = {'PathOnHost': os.path.join(d['devprefix'], "rdma_cm"),
                                   'PathInContainer': os.path.join(d['devprefix'], "rdma_cm"),
                                   'CGroupPermissions': "rwm"}
                            docker_kwargs['HostConfig']['Devices'].append(dev)
                        if "uverbs" in d['names']:
                            dev = node["networks"][dnet.name]["netdevice"]
                            vfs = node["host"]["sriov"][dev]["vfs"]
                            for iface in vfs:
                                n = iface["ib_verbs_devs"][0]
                                dev = {'PathOnHost': os.path.join(d['devprefix'], n),
                                       'PathInContainer': os.path.join(d['devprefix'], n),
                                       'CGroupPermissions': "rwm"}
                                docker_kwargs['HostConfig']['Devices'].append(dev)
                    else:
                        dev = {'PathOnHost': d['devprefix'],
                               'PathInContainer': d['devprefix'],
                               'CGroupPermissions': "rwm"}
                        docker_kwargs['HostConfig']['Devices'].append(dev)

        srec['mgmt_net'] = node['networks'].get(mnet.name, None)
        srec['mgmt_ipv4'] = mgmt_ipv4
        srec['mgmt_ipv6'] = mgmt_ipv6
        srec['data_net'] = node['networks'].get(dnet.name, None)
        srec['data_net_name'] = dnet.name
        srec['data_ipv4'] = data_ipv4
        srec['data_ipv6'] = data_ipv6
        srec['data_vfmac'] = vfmac
        srec['data_vfid'] = vfid
        srec['container_user'] = kwargs.get("USER_NAME", None)

        srec['sname'] = sname
        srec['node'] = node
        srec['node_id'] = node['id']
        srec['serv_port'] = sport
        srec['ctrl_port'] = cport
        srec['ctrl_host'] = node['public_url']
        srec['kwargs'] = docker_kwargs
        srec['net_kwargs'] = mnet_kwargs
        srec['image'] = sreq.image
        srec['profile'] = prof.name
        srec['pull_image'] = pull
        srec['qos'] = qos
        srec['errors'] = list()
        return srec
