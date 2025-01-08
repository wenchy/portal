"""
SYNOPSIS
    ./app.py [mode] [env]

DESCRIPTION

    mode        singleprocess or multiprocess, default is singleprocess

    env         environment name

DEMONSTRATION

    python3 app.py
    python3 app.py singleprocess dev
    python3 app.py multiprocess test
"""

import sys
import collections
import traceback
from http import HTTPStatus

import tornado.websocket
import tornado.gen
import tornado.options
import tornado.ioloop
import tornado.httpserver
import tornado.web

from core.logger import log
from core import context
from core.auth import handler
from core import util
from core import formmgr
from core import form
from core import formutil
from core.timespan import Timespan
import config

sys.path.append("common")
sys.path.append("common/protocol")


class ControllerList(handler.BaseListHandler):

    def post(self, *args, **kwargs):
        param_type = self.get_argument("type", "")
        param_zone = self.get_argument("zone", "")
        param_uid = self.get_argument("uid", "")
        self.request.query

        # process redirect logic
        if param_type and param_zone and param_uid:
            # redirect by zone_id
            zone_id = int(param_zone)
            if zone_id not in config.ZONES:
                self.set_status(HTTPStatus.NOT_FOUND)
                self.write(f"unknown zone id: {zone_id}")
                return
            redirect_venv_name = config.ZONES[zone_id]["env"]["redirect"]
            venv = config.get_venv(redirect_venv_name)
            if not venv:
                self.set_status(HTTPStatus.NOT_FOUND)
                self.write(f"unknown redirect venv: {redirect_venv_name}({zone_id})")
                return
            if redirect_venv_name != config.VENV_NAME:
                base_url = f"{venv["domain"]}/{venv["path"]}/"
                redirect_url = f"{base_url}?{self.request.query}"
                self.redirect(redirect_url)
            else:
                # same venv name, no need to redirect
                log.debug("no need to redirect")

        pkg_fullname = formmgr.DEFAULT_PACKAGE_FULLNAME
        if len(args) == 1 and args[0]:
            # package specified
            pkg_fullname = formmgr.fullname(args[0])
        if pkg_fullname not in formmgr.ALL_PACKAGES:
            self.set_status(HTTPStatus.NOT_FOUND)
            return
        modules = formmgr.ALL_PACKAGES[pkg_fullname].modules
        tabs = collections.OrderedDict()
        for module in modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C
            # to comply with HTML name pattern
            tab_name = module.__name__.replace(".", "-")
            forms = formutil.get_forms_by_module(module)
            # generate auth forms
            auth_forms = self.gen_auth_forms(module.__name__, forms)
            tabs[tab_name] = {
                "module_name": module.__name__,
                "desc": module.__doc__,
                "forms": forms,
                "auth_forms": auth_forms,
            }
        # log.debug(tabs)
        self.render(
            "./templates/index.html",
            package_names=formmgr.PACKAGE_NAMES,
            tabs=tabs,
            venv_name=config.VENV_NAME,
            deployed_venv=config.DEPLOYED_VENV,
            venvs=config.VENVS,
            zones=config.DEPLOYED_ZONES,
            username=self.username,
            auth_type=self.auth_type,
            avatar_url=config.get_avatar_url(self.username),
            form_action="/controller/exec",
        )

    get = post


class ControllerExec(handler.BaseExecHandler):
    def post(self, *args, **kwargs):
        with Timespan(
            lambda duration: log.debug(
                f"handle request time-consuming: {duration}, args: {args}, kwargs: {kwargs}, request.arguments: {self.request.arguments}"
            )
        ):
            try:
                exec(self, *args, **kwargs)
            except Exception as e:
                log.error("Caught exception: %s, %s", str(e), traceback.format_exc())
                self.write(traceback.format_exc())

    get = post


def exec(handler: handler.BaseExecHandler, *args, **kwargs):
    # Find the corresponding Python function object.
    #
    # Split a module name at the last occurrence of a dot (.) into two parts,
    # the first part is package name:
    # e.g.: "controller.index.example_modifier" -> "controller.index"
    pkg_fullname = handler.module.rsplit(".", 1)[0]
    func = formmgr.ALL_PACKAGES[pkg_fullname].indexes[handler.module][1][handler.func]

    extras = {"username": handler.username}
    account_type = int(handler.get_argument("_type", "0"))
    uid = int(handler.get_argument("_uid", 0))
    opcode = int(handler.get_argument("_opcode", 0))
    zone_id = int(handler.get_argument("_zone"))
    trace_id = int(handler.get_argument("_trace_id", 0))

    if not zone_id or zone_id not in config.DEPLOYED_ZONES:
        handler.write(f"not found zone: {zone_id}")
        return
    env = config.DEPLOYED_ZONES[zone_id]["env"]

    ctx = context.Context(
        uid=uid,
        opcode=opcode,
        account_type=account_type,
        zone_id=zone_id,
        env=env,
        trace_id=trace_id,
        extras=extras,
    )

    log.debug(f"ctx dump: {ctx.dump()}")

    func_args = []
    for param in formutil.get_func_parameters(func):
        # NOTE: The first param must be ctx.
        # log.debugCtx(ctx, f"param: {param}")
        arg = None
        if formutil.is_file_argument(func, param.name):
            # assume as file if param name's suffix is '__file'
            files = handler.request.files.get(param.name, None)
            if files:
                arg = files[0]
        else:
            # searches both the query and body arguments
            arg_list = handler.get_arguments(param.name)
            if formutil.is_list_argument(func, param.name):
                arg = arg_list
            else:
                if len(arg_list) == 0:
                    arg = None
                elif len(arg_list) == 1:
                    arg = arg_list[0]
                else:
                    handler.set_status(HTTPStatus.BAD_REQUEST)
                    handler.write(
                        f"scalar param {param.name} has too many arguments: {arg_list}"
                    )
                    handler.finish()
                    return

        func_args.append(arg)

    uids: list[int] = []
    batch_uids = handler.get_argument("_uids", None)
    if batch_uids:
        uids = map(int, batch_uids.splitlines())
    else:
        uids.append(uid)

    for uid in uids:
        if batch_uids:
            # Separate each uid execution
            handler.write(f"\n--- uid: {uid} ---\n")

        ecode = None
        ctx.uid = uid
        func_args[0] = ctx
        log.infoCtx(ctx, f"func '{handler.func}' args: {func_args}")
        # result formats:
        #   1. tuple: (ecode, [object...])
        #   2. form.File
        #   3. form.Editor
        #   4. other: just textualize it
        result = func(*func_args)
        if isinstance(result, tuple):
            ecode = result[0]
            for item in result[1:]:
                handler.write(util.textualize(item))
        elif isinstance(result, form.File):
            file: form.File = result
            handler.set_header("Content-Type", file.content_type)
            handler.set_header(
                "content-Disposition", "attachement; filename=" + file.filename
            )
            handler.write(file.body)
        elif isinstance(result, form.Editor):
            editor: form.Editor = result
            handler.write(editor.body)
        else:
            handler.write(util.textualize(result))
            ecode = 0

        if ecode != None:
            handler.write("\n\n")
            if ecode == 0:
                handler.write("🆗")
            else:
                text = "❌ " + util.get_ecode_details(ecode)
                handler.write(util.html_font(text, color="red"))
    # Flushes the current output buffer to the network.
    handler.flush()


def start_app(mode):
    tornado.options.parse_command_line()

    # parse all controller forms
    formmgr.parse_controller_forms()

    # NOTE: configure prefix path redirection for VENV_NAME, so we can
    # start standalone web app without nginx reverse proxy.
    handlers = [
        # static file handlers
        (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": "./static/"}),
        (
            rf"/{config.VENV_NAME}/static/(.*)",
            tornado.web.StaticFileHandler,
            {"path": "./static/"},
        ),
        # dynamic handlers
        (rf"/", ControllerList),
        (rf"/{config.VENV_NAME}/?", ControllerList),
        (rf"/{config.VENV_NAME}/controller/list/(.*)", ControllerList),
        (rf"/{config.VENV_NAME}/controller/exec", ControllerExec),
    ]
    # application kwargs: settings
    settings = {
        "debug": True,  # if in multiprocess mode, set `debug = False`
    }

    # TODO: parse address and port from command arguments if provided
    address = "0.0.0.0"
    port = config.DEPLOYED_VENV["port"]
    if mode == "singleprocess":
        settings["debug"] = False
        app = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(app)
        server.listen(port, address=address)
    elif mode == "multiprocess":
        settings["debug"] = False
        app = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(app)
        server.bind(port, address=address)
        # value 0 means: autodetect cpu cores and fork one process per core
        server.start(0)
        log.set_multi_process(True, tornado.process.task_id())
    else:
        log.error("unknown start mode: " + mode)
        Usage()
        exit(1)

    for hanlder in handlers:
        print(f"""Route "{hanlder[0]}" -> {hanlder[1].__name__}""")
    print(f"\nServer is running on http://{address}:{port}\n")

    try:
        # start web server
        tornado.ioloop.IOLoop.current().start()
    except:
        log.error("Caught exception: " + traceback.format_exc())


def Usage():
    # help(sys.modules[__name__])
    print(sys.modules[__name__].__doc__)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        mode = "singleprocess"
        start_app(mode)
    elif len(sys.argv) == 2:
        mode = sys.argv[1]
        start_app(mode)
    elif len(sys.argv) == 3:
        mode = sys.argv[1]
        env = sys.argv[2]
        log.info(f"mode: {mode}, env: {env}")
        start_app(mode)
    else:
        log.error("error: illegal args")
        Usage()
        exit(1)
