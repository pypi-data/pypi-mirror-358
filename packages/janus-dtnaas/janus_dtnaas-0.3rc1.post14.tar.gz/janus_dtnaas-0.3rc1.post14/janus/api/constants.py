from enum import IntEnum


class Constants:
    NET = "network"
    HOST = "host"
    QOS = "qos"
    VOL = "volume"
    NET_BRIDGE = "bridge"
    NET_NONE = "none"
    NET_HOST = "host"
    PROFILE_RESOURCES = [NET, HOST, QOS, VOL]
    NET_RESOURCES = [NET, NET_BRIDGE, NET_NONE, NET_HOST]
    AUTH_RESOURCES = ["nodes", "images", "profiles", "active"]


class State(IntEnum):
    UNKNOWN = 0
    INITIALIZED = 1
    STARTED = 2
    STOPPED = 3
    MIXED = 4
    STALE = 5


class EPType(IntEnum):
    UNKNOWN = 0
    PORTAINER = 1
    KUBERNETES = 2
    DOCKER = 3
    SLURM = 4
    EDGE = 100


class WSEPType(IntEnum):
    PORTAINER = 1001
    KUBERNETES = 1002
    DOCKER = 1003
    SLURM = 1004


class WSType(IntEnum):
    EXEC_STREAM = 0
    EP_STATUS = 1
    CONTAINER_STATUS = 2
    EVENTS = 3
    AGENT_COMM = 4
    AGENT_REGISTER = EPType.EDGE


WS_MIN = WSEPType.PORTAINER
WS_MAX = WSEPType.SLURM
