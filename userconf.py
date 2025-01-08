from core.rbac.role import *
from core.rbac.user import *


class ExternalUsers(BaseExternalUsers):
    """
    TODO: get user from remote **authx** (WIP) server.
    """

    def get(self, username: str) -> User:
        # return None
        return User(username, "", [ADMIN])


USERS = Users(ExternalUsers())
# API: sign = md5(f"_appid={appid}&_appkey={appkey}&_ts={ts}")
USERS.add("appid", "appkey", [STAFF])
# users
USERS.add("guest", "guestpw", [GUEST])
USERS.add("staff", "staffpw", [STAFF])
USERS.add("dev", "devpw", [GUEST, STAFF])
USERS.add("admin", "adminpw", [ADMIN])
