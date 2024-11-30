"""
A pluggable N-level authentication module.
"""

import base64
import collections
import hashlib
from http import HTTPStatus
from core.logger import log
import config
from core import util


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
        # handler._transforms = []
        # handler.finish()
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

    # TODO: actually verify provided credentials :-)
    user_list = config.AUTHS["basics"] + config.AUTHS["admins"]
    if username in user_list and username == password:
        return True, username
    else:
        return _unauthorized(), username


def auth_api(handler):
    appid = str(handler.get_argument("appid", None))
    log.debug("appid: " + appid)
    if appid and appid in config.AUTHS["apis"]:
        appkey = config.AUTHS["apis"][appid]
        signature = str(handler.get_argument("signature", ""))
        timestamp = str(handler.get_argument("timestamp", 0))
        encoded = hashlib.md5((appkey + timestamp).encode("utf-8")).hexdigest()
        log.debug("encoded = {} | signature = {}".format(encoded, signature))
        if encoded == signature:
            return True, appid
    return False, appid


def auth_admin(handler):
    ok, username = auth_basic(handler)
    if ok and username in config.AUTHS["admins"]:
        return True, username
    else:
        return False, username


def auth(auth_type="basic"):
    """
    Explanation:
        tornado.web.RequestHandler calls an internal `_execute` method before
        calling any other method such as `get` or `post` etc.
        we wrap the internal `_execute` method so that it either returns False if
        no basic authentication provided or it will return the result of calling
        the actual `_execute` method.
    Tutorial:
        http://kevinsayscode.tumblr.com/post/7362319243/easy-basic-http-authentication-with-tornado
    """
    auths = collections.OrderedDict(
        [
            ("admin", {"handler": auth_admin, "level": 6}),
            ("api", {"handler": auth_api, "level": 3}),
            ("basic", {"handler": auth_basic, "level": 2}),
            ("anonym", {"handler": auth_anonym, "level": 1}),
        ]
    )

    def decorator(handler_class):
        def wrap_execute(handler_execute):
            # Since we're going to attach this to a RequestHandler class,
            # the first argument will wind up being a reference to an
            # instance of that class.
            @util.exception_catcher
            def _execute(self, transforms, *args, **kwargs):
                for name, value in self.request.headers.get_all():
                    log.debug("headers: " + name + ":" + value)

                real_auth_type = auth_type
                ok, username = False, None
                # NOTE: auths是OrderedDict
                # 描述: 按照level从高到低一个个尝试鉴权，如果成功就break，直到level等于设置的最低鉴权类型对应level
                # 目的: 保证高level权限的用户可以pass低level的鉴权类型
                for _auth_type, _auth_item in auths.items():
                    if _auth_item["level"] >= auths[auth_type]["level"]:
                        ok, username = _auth_item["handler"](self)
                        if ok:
                            real_auth_type = _auth_type
                            break

                if ok:
                    log.info(
                        "success|username: %s|specified auth: %s|real auth: %s|class: %s|arguments: %s"
                        % (
                            username,
                            auth_type,
                            real_auth_type,
                            handler_class.__name__,
                            str(self.request.arguments),
                        )
                    )
                    kwargs["username"] = username
                    kwargs["auth_type"] = real_auth_type
                    return handler_execute(self, transforms, *args, **kwargs)
                else:
                    log.info(
                        "username: %s|auth failed: %s|class: %s|arguments: %s"
                        % (
                            username,
                            auth_type,
                            handler_class.__name__,
                            str(self.request.arguments),
                        )
                    )
                    self.write("<h3>Permission denied!</h3>")
                    self.write(
                        "Please contact the backend dev-group if you do need permission."
                    )
                    self.write("<br>Auth level: <strong>" + auth_type + "</strong>")
                    self._transforms = []
                    self.finish()

                    return False

            # return our new function, which either returns False if basic auth
            # wasn't provided, otherwise it returns the result of calling the
            # original _execute function.
            return _execute

        # wrap tornado's internal `_execute` method, which is called first before
        # any other method in the RequestHandler class
        handler_class._execute = wrap_execute(handler_class._execute)

        # return the modified class
        return handler_class

    return decorator


def main():
    pass


if __name__ == "__main__":
    main()
