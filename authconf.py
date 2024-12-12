from core.rbac.role import *
from core.rbac.user import *

APIS = {
    # APPID -> APPKEY
    # APPKEY generated by: echo "$(date) + $appid" | md5sum
    "prod": "9cdaccb0f61a66ac70cfd5256cd8960b"
}

USERS = Users()
USERS.add("test", "testpw", [GUEST])
USERS.add("admin", "adminpw", [ADMIN])