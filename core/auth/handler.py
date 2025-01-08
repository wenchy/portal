"""
Basic authentication and authorization handlers.
"""

from http import HTTPStatus
import tornado
import config
import userconf
import authconf
from ..logger import log
from ..rbac.user import User


class BaseHandler(tornado.web.RequestHandler):
    username: str
    user: User
    auth_type: str

    def _authenticate(self) -> bool:
        # for name, value in self.request.headers.get_all():
        #     log.debug("headers: " + name + ":" + value)

        # prepare common data members
        self.auth_type = config.DEPLOYED_VENV["auth"]
        real_auth_type = self.auth_type

        # treat VENV as env for checking permissions
        self.env: str = config.VENV_NAME

        # Authenticate from high to low priority until it passes.
        ok = False
        need_check = False
        for auth in reversed(authconf.AUTHS):
            auth_type = auth.name
            if auth_type == self.auth_type:
                need_check = True
            if need_check:
                ok, username, user = auth.authenticate(self)
                if ok:
                    real_auth_type = auth_type
                    # remember for later use
                    self.username = username
                    self.user = user
                    self.auth_type = auth_type
                    break

        access_detail = f"username: {self.username}, specified auth: {self.auth_type}, real auth: {real_auth_type}, arguments: {self.request.arguments}"
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

    def gen_auth_forms(self, module_name: str, forms: dict) -> dict:
        """generate auth forms for disabling unauthorized opcodes"""

        def authorize_opcode(opcodes: dict[int, str], opcode: int):
            # comment out for test
            # opcodes[opcode] = ""
            if self.user.authorize(self.env, module_name, func_name, opcode):
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

        ok = userconf.USERS.authorize(
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
