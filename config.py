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
                "redirection": "idcnet",
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

WORLDS = {
    "WX": 1,
    "QQ": 2,
    "dev": 7,
}


def zoneid(world, zone):
    # world:3.zone:13.function:6.instance:10
    # world: max 7 (2 ** 3 - 1)
    #   1: 微信
    #   2: QQ
    #   7: 测试(包括开发环境和测试环境)
    # zone: max 8191 (2 ** 13 - 1)
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

AUTHS = {
    "apis": {
        # APPID -> APPKEY
        # APPKEY generated by: echo "$(date) + $appid"  | md5sum
        "prod": "9cdaccb0f61a66ac70cfd5256cd8960b"
    },
    "basics": [
        # 测试组
        "john",
    ],
    "admins": [
        # 运营组
        # 后台组
        "john",
        # 前台组
    ],
}

VENV_NAME = "dev"  # will be replaced to real env by deploy.sh

DANGER_VENVS = []  # prompt when submit form

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
                            "auth": {"controller": "basic", "admin": "admin"},
                            "alert": True,
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
                            "auth": {"controller": "basic", "admin": "admin"},
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
                            "desc": "prod环境",
                            "path": "prod",
                            "envs": ["prod"],
                            "port": 9001,
                            "auth": {"controller": "basic", "admin": "admin"},
                            "alert": True,
                            "domain": "http://xxx.com",
                        },
                    ),
                ]
            ),
        ),
    ]
)


def help():
    for key, venvs in VENVS.items():
        print(key + ": ")
        for name, venv in venvs.items():
            print(name + ": " + venv["desc"])


def get_venv(venv_name):
    for _, venvs in VENVS.items():
        for name, venv in venvs.items():
            if name == venv_name:
                return venv


def filter_zones(deployed_env):
    if deployed_env:
        zones = collections.OrderedDict()
        for zone_id, item in ZONES.items():
            if item["env"]["name"] in deployed_env["envs"]:
                zones[zone_id] = item
        return zones


DEPLOYED_ENV = get_venv(VENV_NAME)
DEPLOYED_ZONES = filter_zones(DEPLOYED_ENV)


def is_devnet() -> bool:
    if VENV_NAME in ["lab", "dev"]:
        return True
    return False


def get_avatar_url(username: str) -> str:
    # TODO: implement custom avatar URL
    return "/" + VENV_NAME + "/static/img/avatar.svg"
