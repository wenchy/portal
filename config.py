import collections

ENVS = collections.OrderedDict(
    [
        (
            "dev",
            {
                "desc": "dev",
                "redirection": "dev",
                "gate": {"ip": "127.0.0.1", "port": 8080},
                "redis": {
                    "host": "127.0.0.1",
                    "port": 16379,
                    "passwd": "redispw",
                },
            },
        ),
        (
            "test",
            {
                "desc": "test",
                "redirection": "test",
                "gate": {"ip": "127.0.0.1", "port": 8080},
                "redis": {
                    "host": "127.0.0.1",
                    "port": 16379,
                    "passwd": "redispw",
                },
            },
        ),
        (
            "pre",
            {
                "desc": "pre",
                "redirection": "pre",
                "gate": {"ip": "127.0.0.1", "port": 8080},
                "redis": {
                    "host": "127.0.0.1",
                    "port": 16379,
                    "passwd": "redispw",
                },
            },
        ),
        (
            "prod",
            {
                "desc": "prod",
                "redirection": "prod",
                "gate": {"ip": "127.0.0.1", "port": 8080},
                "redis": {
                    "host": "127.0.0.1",
                    "port": 16379,
                    "passwd": "redispw",
                },
            },
        ),
    ]
)

# auto insert name
for name, value in ENVS.items():
    value["name"] = name

# 部署环境配置: Virtual ENVironmentS
# 此命名原因: 一个venv映射多个env, 以利于弹性部署
# 部署目录: user00用户home目录下的`~/tornado`
VENVS = collections.OrderedDict(
    [
        (
            "内网环境",
            collections.OrderedDict(
                [
                    (
                        "dev",
                        {
                            "desc": "开发环境",
                            "path": "dev",
                            "envs": ["dev"],
                            "port": 8001,
                            "auth": "basic",
                            "alert": False,
                            "domain": "https://xxx.com",
                        },
                    ),
                    (
                        "test",
                        {
                            "desc": "测试环境",
                            "path": "test",
                            "envs": ["test", "pre"],
                            "port": 8002,
                            "auth": "basic",
                            "alert": False,
                            "domain": "https://xxx.com",
                        },
                    ),
                ]
            ),
        ),
        (
            "外网环境",
            collections.OrderedDict(
                [
                    (
                        "prod",
                        {
                            "desc": "正式环境",
                            "path": "prod",
                            "envs": ["prod"],
                            "port": 9001,
                            "auth": "basic",
                            "alert": True,
                            "domain": "http://xxx.com",
                        },
                    ),
                ]
            ),
        ),
    ]
)


def zoneid(world, zone):
    return (world << 13) + zone


def get_world(zoneid: int):
    return zoneid >> 13


def get_zone(zoneid: int):
    return zoneid & 0x1FFF


ZONES = collections.OrderedDict(
    [
        (zoneid(7, 1), {"desc": "dev", "env": ENVS["dev"]}),
        (zoneid(7, 2), {"desc": "test", "env": ENVS["test"]}),
        (zoneid(7, 3), {"desc": "pre", "env": ENVS["pre"]}),
        (zoneid(7, 11), {"desc": "prod", "env": ENVS["prod"]}),
    ]
)


def get_venv(venv_name):
    for venvs in VENVS.values():
        for name, venv in venvs.items():
            if name == venv_name:
                return venv


def filter_zones(venv):
    zones = collections.OrderedDict()
    for zone_id, item in ZONES.items():
        if item["env"]["name"] in venv["envs"]:
            zones[zone_id] = item
    return zones


VENV_NAME = "dev"  # will be replaced to real env by deploy.sh
DANGER_VENV_NAMES = []  # prompt when submit form
DEPLOYED_VENV = get_venv(VENV_NAME)
DEPLOYED_ZONES = filter_zones(DEPLOYED_VENV)


def get_avatar_url(username: str) -> str:
    # TODO: implement custom avatar URL
    return "/" + VENV_NAME + "/static/img/avatar.svg"
