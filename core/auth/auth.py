"""
Common authentication functions.
"""

import base64
from http import HTTPStatus
import tornado
import userconf
from ..rbac.user import User
from core.rbac.role import GUEST
from ..logger import log

__ANONY = User("anonym", "", [GUEST])


def anonym(handler: tornado.web.RequestHandler) -> tuple[bool, str, User]:
    return True, __ANONY.username(), __ANONY


# returns True is basic auth provided, otherwise it sends back a 401
# status code and requests user input their credentials.
#
# todo: write logic or pass in a function so that it can determine
# whether the authentication is accepted (e.g. you find the credentials
# within an external database).
def basic(handler: tornado.web.RequestHandler) -> tuple[bool, str, User]:
    def _unauthorized():
        handler.set_status(HTTPStatus.UNAUTHORIZED)
        handler.set_header("WWW-Authenticate", "Basic realm=Restricted")  # noqa
        return False

    auth_header = handler.request.headers.get("Authorization")
    if auth_header is None or not auth_header.startswith("Basic "):
        # If the browser didn't send us authorization headers,
        # send back a response letting it know that we'd like
        # a username and password (the "Basic" authentication
        # method).  Without this, even if your visitor puts a
        # username and password in the URL, the browser won't
        # send it.  The "realm" option in the header is the
        # name that appears in the dialog that pops up in your
        # browser.
        return _unauthorized(), "", None

    # The information that the browser sends us is
    # base64-encoded, and in the format "username:password".
    # Keep in mind that either username or password could
    # still be unset, and that you should check to make sure
    # they reflect valid credentials!
    auth_decoded = base64.decodebytes(bytes(auth_header[6:], "utf-8"))
    username, password = auth_decoded.decode("utf-8").split(":", 2)
    log.debug(f"username: {username}, password: {password}")
    ok, user = userconf.USERS.authenticate(username, password)
    if ok:
        return True, username, user
    else:
        return _unauthorized(), username, None


def api(handler: tornado.web.RequestHandler) -> tuple[bool, str, User]:
    appid = handler.get_argument("_appid", "")
    if not appid:
        return False, "", None

    sign = handler.get_argument("_sign", "")
    ts = int(handler.get_argument("_ts", 0))
    log.debug(f"appid: {appid}, sign: {sign}, ts: {ts}")
    ok, user = userconf.USERS.authenticate_api(appid, sign, ts)
    if ok:
        return True, appid, user
    else:
        return False, appid, None
