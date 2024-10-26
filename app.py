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

import collections
import json
import traceback
import tornado.websocket
import tornado.gen
import tornado.options
import tornado.ioloop
import tornado.httpserver
import tornado.web
import os
import sys

from core.logger import log
from core import context
from core import auth
from core import util
from core.timespan import Timespan
import config

sys.path.append("common")
sys.path.append("common/protocol")

all_modules = {}

ordered_modifier_modules = []
ordered_editor_modules = []

admin_ordered_modifier_modules = []
admin_ordered_editor_modules = []


def LoadAllModifiers():
    modifier_module_names = [
        os.path.splitext(file_name)[0]
        for file_name in os.listdir("controller")
        if file_name.endswith("_modifier.py")
    ]
    global all_modules
    global ordered_modifier_modules
    modifier_modules = []
    for module_name in modifier_module_names:
        log.debug("add modifier module: " + module_name)
        package = __import__("controller", fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        modifier_modules.append(imported_module)
    ordered_modifier_modules = sorted(
        modifier_modules, key=lambda module: module.__priority__, reverse=True
    )
    log.debug("ordered_modifier_modules: " + str(ordered_modifier_modules))


def LoadAllEditors():
    editor_module_names = [
        os.path.splitext(file_name)[0]
        for file_name in os.listdir("controller")
        if file_name.endswith("_editor.py")
    ]
    global all_modules
    global ordered_editor_modules
    editor_modules = []
    for module_name in editor_module_names:
        log.debug("add editor module: " + module_name)
        package = __import__("controller", fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        editor_modules.append(imported_module)
    ordered_editor_modules = sorted(
        editor_modules, key=lambda module: module.__priority__, reverse=True
    )
    log.debug("ordered_editor_modules: " + str(ordered_editor_modules))


def AdminLoadAllModifiers():
    modifier_module_names = [
        os.path.splitext(file_name)[0]
        for file_name in os.listdir("admin")
        if file_name.endswith("modifier.py")
    ]
    global all_modules
    global admin_ordered_modifier_modules
    modifier_modules = []
    for module_name in modifier_module_names:
        log.debug("add modifier module: " + module_name)
        package = __import__("admin", fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        modifier_modules.append(imported_module)
    admin_ordered_modifier_modules = sorted(
        modifier_modules, key=lambda module: module.__priority__, reverse=True
    )
    log.debug("admin_ordered_modifier_modules: " + str(admin_ordered_modifier_modules))


def AdminLoadAllEditors():
    editor_module_names = [
        os.path.splitext(file_name)[0]
        for file_name in os.listdir("admin")
        if file_name.endswith("_editor.py")
    ]
    global all_modules
    global admin_ordered_editor_modules
    editor_modules = []
    for module_name in editor_module_names:
        log.debug("add editor module: " + module_name)
        package = __import__("admin", fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        editor_modules.append(imported_module)
    admin_ordered_editor_modules = sorted(
        editor_modules, key=lambda module: module.__priority__, reverse=True
    )
    log.debug("admin_ordered_editor_modules: " + str(admin_ordered_editor_modules))


class FileUploadHandler(tornado.web.RequestHandler):
    def get(self):
        filename = self.get_argument("filename")
        filename = os.path.join("./files/", filename)
        # http头 浏览器自动识别为文件下载
        self.set_header("Content-Type", "application/octet-stream")
        # 下载时显示的文件名称
        self.set_header("Content-Disposition", "attachment; filename=%s" % filename)
        with open(filename, "rb") as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)
        # # 记得有finish哦
        self.finish()

    def post(self):
        ret = {"result": "OK"}
        upload_path = os.path.join(os.path.dirname(__file__), "files")  # 文件的暂存路径
        file_metas = self.request.files.get(
            "file", None
        )  # 提取表单中‘name’为‘file’的文件元数据

        if not file_metas:
            ret["result"] = "Invalid Args"
            return ret

        for meta in file_metas:
            filename = meta["filename"]
            file_path = os.path.join(upload_path, filename)

            with open(file_path, "wb") as up:
                up.write(meta["body"])
                # OR do other thing

        self.write(json.dumps(ret))


@auth.auth(config.DEPLOYED_ENV["auth"]["controller"])
class ControllerList(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        param_type = self.get_argument("type", "")
        param_zone = self.get_argument("zone", "")
        param_uid = self.get_argument("uid", "")

        if param_type and param_zone and param_uid:
            # redirect by zone_id
            zone_id = int(param_zone)
            if zone_id in config.ZONES:
                redirected_venv_name = config.ZONES[zone_id]["env"]["redirection"]
                venv = config.get_venv(redirected_venv_name)
                if venv:
                    if (
                        redirected_venv_name != config.VENV_NAME
                    ):  # 相同env_name无需重定向，否则会导致redirect死循环:
                        redirect_url = (
                            venv["domain"]
                            + "/"
                            + venv["path"]
                            + "/modifier/list?"
                            + "type="
                            + param_type
                            + "&"
                            + "zone="
                            + param_zone
                            + "&"
                            + "uid="
                            + param_uid
                        )
                        self.redirect(redirect_url)
                    else:
                        # 此处说明env_name相同，无需重定向
                        log.debug("no need to redirect")
                else:
                    self.write(
                        "unknown redirected venv name: %s(%d)"
                        % (redirected_venv_name, zone_id)
                    )
                    return
            else:
                self.write("unknown zone id: %d" % zone_id)
                self.finish()
                return

        username = kwargs["username"]
        auth_type = kwargs["auth_type"]

        modules = ordered_modifier_modules + ordered_editor_modules
        modules.sort(key=lambda module: module.__priority__, reverse=True)
        tabs = collections.OrderedDict()
        for module in modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C
            # to comply with HTML name pattern
            tab_name = module.__name__.replace(".", "-")
            tabs[tab_name] = {
                "module_name": module.__name__,
                "desc": module.__doc__,
                "forms": util.get_forms_by_module(module),
            }
        # log.debug(tabs)
        self.render(
            "index.html",
            tabs=tabs,
            venv_name=config.VENV_NAME,
            deployed_venv=config.DEPLOYED_ENV,
            venvs=config.VENVS,
            zones=config.DEPLOYED_ZONES,
            username=username,
            auth_type=auth_type,
            avatar_url=config.get_avatar_url(username),
            form_action="/modifier/exec",
        )

    get = post


def handle_execute_request(handler: tornado.web.RequestHandler, *args, **kwargs):
    try:
        execute_request(handler, *args, **kwargs)
    except Exception as e:
        log.error("Caught exception: %s, %s", str(e), traceback.format_exc())
        handler.write(traceback.format_exc())


def execute_request(handler: tornado.web.RequestHandler, *args, **kwargs):
    module_name = handler.get_argument("_module", "")
    assert module_name, "argument _module not provided"

    func_name = handler.get_argument("_func", "")
    assert func_name, "argument _func not provided"

    func = None
    for key_module_name, val_module_tuple in all_modules.items():
        if module_name == "" or module_name == key_module_name:
            if func_name in val_module_tuple[1]:
                func = val_module_tuple[1][func_name]
                break
    assert func, "func '%s' not existed in module '%s'" % (func_name, module_name)

    username = kwargs["username"]
    extras = {"username": username}
    account_type = int(handler.get_argument("_type", "0"))
    uid = int(handler.get_argument("_uid", 0))
    zone_id = int(handler.get_argument("_zone"))
    trace_id = handler.get_argument("trace_id", 0)
    world = config.get_world(zone_id)

    if world == config.WORLDS["WX"]:
        env = config.ENVS["idc_wx"]

    elif world == config.WORLDS["QQ"]:
        env = config.ENVS["idc_qq"]
    else:
        if not zone_id or zone_id not in config.DEPLOYED_ZONES:
            handler.write("not found zone: " + str(zone_id))
            return
        env = config.DEPLOYED_ZONES[zone_id]["env"]

    ctx = context.Context(
        account_type=account_type,
        uid=uid,
        zone_id=zone_id,
        env=env,
        trace_id=trace_id,
        extras=extras,
    )

    log.debug("ctx: %s", ctx.debug_str())

    func_args = util.get_func_args(func)
    args = []
    for arg_name in func_args[0]:
        log.debugCtx(ctx, "arg_name: " + arg_name)
        if arg_name.endswith("__file"):
            # assume as file if arg_name's suffix is '__file'
            arg = handler.request.files.get(arg_name, None)
        else:
            arg = handler.get_argument(arg_name, None)
        # TODO(wenchy): check if required argument
        if not arg:
            arg = ""  # default empty str
            # assert False, "argument '%s' not provided" % arg_name
        args.append(arg)

    ecode = -1
    need_write_ecode = True

    uidlist = []
    uidlist_str = handler.get_argument("__uidlist__", None)
    if uidlist_str:
        uidlist = map(int, uidlist_str.splitlines())
    else:
        uidlist.append(handler.get_argument("_uid", 0))

    for uid in uidlist:
        ctx.uid = int(uid)
        args[0] = ctx

        fixed_args = []
        for arg in args:
            # TODO(wenchy): do type conversion due to type annotation
            fixed_args.append(arg)
        log.infoCtx(ctx, "fixed args: " + str(fixed_args))
        # result规范：
        # 1. type(result) == tuple
        #   (error_code, content, {content_type: 'Content-Type', filename: 'filename'})
        # 2. 如果是json字符串，输出到前端json_editor
        # 3. 其它，直接输出result，并且附带字符串"\nSUCCESS"
        result = func(*fixed_args)

        if isinstance(result, tuple):
            # 如果返回类型是tuple，则默认第一个元素是error code
            ecode = result[0]
            if len(result) == 1:
                need_write_ecode = True
            else:
                if ecode == 0:
                    if len(result) == 3 and isinstance(result[2], dict):
                        handler.set_header("Content-Type", result[2]["content_type"])
                        handler.set_header(
                            "content-Disposition",
                            "attachement; filename=" + result[2]["filename"],
                        )
                        handler.write(result[1])  # file content
                        need_write_ecode = False
                    else:
                        for item in result[1:]:
                            handler.write(util.to_text(item))
                else:
                    for item in result[1:]:
                        handler.write(util.to_text(item))
        elif util.is_json(result):
            # must only ouptut json data
            handler.write(util.to_text(result))
            need_write_ecode = False
        else:
            handler.write(util.to_text(result))
            ecode = 0

    if need_write_ecode:
        if ecode == 0:
            handler.write("\n" + util.html_font(util.get_ecode_name(ecode), "green"))
        else:
            handler.write("\n" + util.html_font(util.get_ecode_name(ecode), "red"))
    handler.flush()  # Flushes the current output buffer to the network.


@auth.auth(config.DEPLOYED_ENV["auth"]["controller"])
class Execute(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        with Timespan(
            lambda duration: log.debug(
                f"handle request time-consuming: {duration}, args: {args}, kwargs: {kwargs}, request.arguments: {self.request.arguments}"
            )
        ):
            handle_execute_request(self, *args, **kwargs)

    get = post


@auth.auth(config.DEPLOYED_ENV["auth"]["admin"])
class AdminList(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        username = kwargs["username"]
        auth_type = kwargs["auth_type"]

        modules = admin_ordered_modifier_modules + admin_ordered_editor_modules
        modules.sort(key=lambda module: module.__priority__, reverse=True)
        tabs = collections.OrderedDict()
        for module in modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C
            # to comply with HTML name pattern
            tab_name = module.__name__.replace(".", "-")
            tabs[tab_name] = {
                "module_name": module.__name__,
                "desc": module.__doc__,
                "forms": util.get_forms_by_module(module),
            }

        # log.debug(tabs)
        self.render(
            "index.html",
            tabs=tabs,
            venv_name=config.VENV_NAME,
            deployed_venv=config.DEPLOYED_ENV,
            venvs=config.VENVS,
            zones=config.DEPLOYED_ZONES,
            username=username,
            auth_type=auth_type,
            avatar_url=config.get_avatar_url(username),
            form_action="/admin/exec",
        )

    get = post


@auth.auth(config.DEPLOYED_ENV["auth"]["admin"])
class AdminExecute(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        with Timespan(
            lambda duration: log.debug(
                f"handle request time-consuming: {duration}, args: {args}, kwargs: {kwargs}, request.arguments: {self.request.arguments}"
            )
        ):
            handle_execute_request(self, *args, **kwargs)

    get = post


def start_app(mode):
    tornado.options.parse_command_line()

    # load all modifiers and editors
    LoadAllModifiers()
    LoadAllEditors()
    AdminLoadAllModifiers()
    AdminLoadAllEditors()

    # NOTE:
    # Application Class default constructor:
    # Application(handlers=None, default_host=None, transforms=None, **settings)
    #
    # application arg: handlers
    handlers = [
        (r"/(favicon.ico)", tornado.web.StaticFileHandler, {"path": ""}),
        (r"/", ControllerList),
        (r"/modifier/", ControllerList),
        (r"/modifier/list", ControllerList),
        (r"/modifier/exec", Execute),
        (r"/admin/", AdminList),
        (r"/admin/list", AdminList),
        (r"/admin/exec", AdminExecute),
        (r"/file", FileUploadHandler),
    ]
    # application kwargs: settings
    settings = {
        "debug": True,  # if in multiprocess mode, set `debug = False`
        "static_path": "./static",
        "template_path": "./template",
    }

    if mode == "singleprocess":
        settings["debug"] = False
        app = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(app)
        server.listen(config.DEPLOYED_ENV["port"])
    elif mode == "multiprocess":
        settings["debug"] = False
        app = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(app)
        server.bind(config.DEPLOYED_ENV["port"])
        # value 0 means: autodetect cpu cores and fork one process per core
        server.start(0)
        log.set_multi_process(True, tornado.process.task_id())
    else:
        log.error("unknown start mode: " + mode)
        Usage()
        exit(1)

    def periodic_task():
        log.info(
            "periodic_task at "
            + "tornado.process.task_id: "
            + str(tornado.process.task_id())
        )

    log.info("tornado.process.task_id: " + str(tornado.process.task_id()))
    if not tornado.process.task_id():
        tornado.ioloop.PeriodicCallback(periodic_task, 10 * 1000).start()

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
