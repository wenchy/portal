from core.rbac.role import *
from core.rbac.user import *

USERS = Users()
# API: sign = md5(f"_appid={appid}&_appkey={appkey}&_ts={ts}")
USERS.add("appid", "appkey", [STAFF])
# users
USERS.add("guest", "guestpw", [GUEST])
USERS.add("staff", "staffpw", [STAFF])
USERS.add("dev", "devpw", [GUEST, STAFF])
USERS.add("admin", "adminpw", [ADMIN])
