"""
A pluggable N-level authentication module.
"""

import base64
import collections
import hashlib
from http import HTTPStatus
import tornado
import config
import authconf
from .logger import log
from .rbac.user import User


def auth_anonym(handler):
    return True, "Anonym"


# returns True is basic auth provided, otherwise it sends back a 401
# status code and requests user input their credentials.
#
# todo: write logic or pass in a function so that it can determine
# whether the authentication is accepted (e.g. you find the credentials
# within an external database).
def auth_basic(handler):
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
        return _unauthorized(), None

    # The information that the browser sends us is
    # base64-encoded, and in the format "username:password".
    # Keep in mind that either username or password could
    # still be unset, and that you should check to make sure
    # they reflect valid credentials!
    auth_decoded = base64.decodebytes(bytes(auth_header[6:], "utf-8"))
    username, password = auth_decoded.decode("utf-8").split(":", 2)

    if authconf.USERS.authenticate(username, password):
        return True, username
    else:
        return _unauthorized(), username


def auth_api(handler):
    appid = handler.get_argument("_appid", "")
    if not appid:
        return False, ""

    sign = handler.get_argument("_sign", "")
    ts = int(handler.get_argument("_ts", 0))
    log.debug(f"appid: {appid}, sign: {sign}, ts: {ts}")
    if authconf.USERS.authenticate_api(appid, sign, ts):
        return True, appid
    else:
        return False, appid


_AUTHS = collections.OrderedDict(
    [
        ("api", {"handler": auth_api, "level": 3}),
        ("basic", {"handler": auth_basic, "level": 2}),
        ("anonym", {"handler": auth_anonym, "level": 1}),
    ]
)


class BaseHandler(tornado.web.RequestHandler):

    def _authenticate(self) -> bool:
        # for name, value in self.request.headers.get_all():
        #     log.debug("headers: " + name + ":" + value)

        # prepare common data members
        self.auth_type = config.DEPLOYED_VENV["auth"]
        self.username = None  # To be filled by authentication

        # treat VENV as env for checking permissions
        self.env: str = config.VENV_NAME

        real_auth_type = self.auth_type
        ok, username = False, None
        # NOTE: auths是OrderedDict
        # 描述: 按照level从高到低一个个尝试鉴权，如果成功就break，直到level等于设置的最低鉴权类型对应level
        # 目的: 保证高level权限的用户可以pass低level的鉴权类型
        for _auth_type, _auth_item in _AUTHS.items():
            if _auth_item["level"] >= _AUTHS[self.auth_type]["level"]:
                ok, username = _auth_item["handler"](self)
                if ok:
                    real_auth_type = _auth_type
                    break

        # remember for later use
        self.username = username
        self.auth_type = real_auth_type

        access_detail = f"username: {username}, specified auth: {self.auth_type}, real auth: {real_auth_type}, arguments: {self.request.arguments}"
        if ok:
            log.debug(f"authenticate succeeded, " + access_detail)
            return True
        else:
            log.error(f"authenticate failed, " + access_detail)
            # NOTE: HTTP header is set by each auth type handler
            self.write("<h3>Permission denied!</h3>")
            self.write("Please contact the server team for permissions.")
            self.write("<br>Auth level: <strong>" + self.auth_type + "</strong>")
            self.finish()
            return False


# Refer: https://github.com/tornadoweb/tornado/issues/3287
#
# You should not be overriding `_execute`` here and should do your auth checks
# in `prepare()` instead. We previously kinda-supported overriding `_execute`
# because prepare couldn't be asynchronous, but now that we support coroutines
# in `prepare`` there's no reason to override `_execute` any more and you
# should stay away from it.
class BaseListHandler(BaseHandler):
    def prepare(self):
        self._authenticate()


class BaseExecHandler(BaseHandler):
    def prepare(self):

        if not self._authenticate():
            return

        # prepare common data members
        self.zone: int = int(self.get_argument("_zone"))
        self.env: str = config.ZONES[self.zone]["env"]["name"]
        self.module: str = self.get_argument("_module")
        self.func: str = self.get_argument("_func")
        self.opcode: int = int(self.get_argument("_opcode"))

        self._authorize()

    def _authorize(self) -> bool:
        # NOTE: depending "self.username" filled by authentication
        access_detail = f"username: {self.username}, env: {self.env}, module: {self.module}, func: {self.func}, opcode: {self.opcode}"

        ok = authconf.USERS.authorize(
            self.username, self.env, self.module, self.func, self.opcode
        )
        if ok:
            log.debug("authorize succeeded, " + access_detail)
            return True
        else:
            log.error("authorize failed, " + access_detail)
            self.set_status(HTTPStatus.FORBIDDEN)
            self.write("<h3>Forbidden</h3>")
            self.write(
                f"You are not allowed to access env: {self.env}, module: {self.module}, func: {self.func}, opcode: {self.opcode}"
            )
            self.finish()
            return False


def gen_auth_forms(user: User, env_name: str, module_name: str, forms: dict) -> dict:
    """generate auth forms for disabling unauthorized opcodes"""

    def authorize_opcode(opcodes: dict[int, str], opcode: int):
        # comment out for test
        # opcodes[opcode] = ""
        if user.authorize(env_name, module_name, func_name, opcode):
            opcodes[opcode] = ""
        else:
            opcodes[opcode] = "disabled"

    auth_forms = {}
    for func_name, form in forms.items():
        opcodes = {}
        if "submit" in form:
            if type(form["submit"]) == int:
                opcode = form["submit"]
                authorize_opcode(opcodes, opcode)
            else:
                for opcode in form["submit"]["opcodes"].keys():
                    authorize_opcode(opcodes, int(opcode))
        else:
            opcode = 0  # default opcode is 0
            authorize_opcode(opcodes, opcode)
        auth_forms[func_name] = {"opcodes": opcodes}

    return auth_forms


if __name__ == "__main__":
    pass
