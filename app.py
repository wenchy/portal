#!/usr/bin/env python
# coding=utf-8

'''
SYNOPSIS
    ./app.py [start_mode] [env]

DESCRIPTION
    start_mode  singleprocess|multiprocess, default start mode is singleprocess

    env         environment

DEMOSTRATION
    ./app.py # default start mode is singleprocess
    ./app.py singleprocess dev
    ./app.py multiprocess test
'''

import time
from core.logger_factory import logger
from core import auth
from core import util
import config
import os.path
import re
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
sys.path.append("common")

print("sys.getdefaultencoding(): ", sys.getdefaultencoding())
print("sys.stdin.encoding: ", sys.stdin.encoding)
print("sys.stdout.encoding: ", sys.stdout.encoding)
print("sys.stderr.encoding: ", sys.stderr.encoding)

all_modules = {}

ordered_modifier_modules = []
ordered_editor_modules = []

admin_ordered_modifier_modules = []
admin_ordered_editor_modules = []

def LoadAllModifiers():
    modifier_module_names = [os.path.splitext(file_name)[0] for file_name in os.listdir(
        'controller') if file_name.endswith("_modifier.py")]
    global all_modules
    global ordered_modifier_modules
    modifier_modules = []
    for module_name in modifier_module_names:
        logger.debug("add modifier module: " + module_name)
        package = __import__('controller', fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        modifier_modules.append(imported_module)
    ordered_modifier_modules = sorted(
        modifier_modules, key=lambda module: module.__priority__, reverse=True)
    logger.debug("ordered_modifier_modules: " + str(ordered_modifier_modules))

def LoadAllEditors():
    editor_module_names = [os.path.splitext(file_name)[0] for file_name in os.listdir(
        'controller') if file_name.endswith("_editor.py")]
    global all_modules
    global ordered_editor_modules
    editor_modules = []
    for module_name in editor_module_names:
        logger.debug("add editor module: " + module_name)
        package = __import__('controller', fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        editor_modules.append(imported_module)
    ordered_editor_modules = sorted(
        editor_modules, key=lambda module: module.__priority__, reverse=True)
    logger.debug("ordered_editor_modules: " + str(ordered_editor_modules))


def AdminLoadAllModifiers():
    modifier_module_names = [os.path.splitext(file_name)[0] for file_name in os.listdir(
        'admin') if file_name.endswith("modifier.py")]
    global all_modules
    global admin_ordered_modifier_modules
    modifier_modules = []
    for module_name in modifier_module_names:
        logger.debug("add modifier module: " + module_name)
        package = __import__('admin', fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        modifier_modules.append(imported_module)
    admin_ordered_modifier_modules = sorted(
        modifier_modules, key=lambda module: module.__priority__, reverse=True)
    logger.debug("admin_ordered_modifier_modules: " +
                 str(admin_ordered_modifier_modules))

def AdminLoadAllEditors():
    editor_module_names = [os.path.splitext(file_name)[0] for file_name in os.listdir(
        'admin') if file_name.endswith("_editor.py")]
    global all_modules
    global admin_ordered_editor_modules
    editor_modules = []
    for module_name in editor_module_names:
        logger.debug("add editor module: " + module_name)
        package = __import__('admin', fromlist=[module_name])
        imported_module = getattr(package, module_name)
        funcs = util.get_func_by_module(imported_module)
        all_modules[imported_module.__name__] = (imported_module, funcs)
        editor_modules.append(imported_module)
    admin_ordered_editor_modules = sorted(
        editor_modules, key=lambda module: module.__priority__, reverse=True)
    logger.debug("admin_ordered_editor_modules: " +
                 str(admin_ordered_editor_modules))

class FileUploadHandler(tornado.web.RequestHandler):
    def get(self):
        filename = self.get_argument('filename')
        filename = os.path.join("./files/", filename)
        # http头 浏览器自动识别为文件下载
        self.set_header('Content-Type', 'application/octet-stream')
        # 下载时显示的文件名称
        self.set_header('Content-Disposition',
                        'attachment; filename=%s' % filename)
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                self.write(data)
        # # 记得有finish哦
        self.finish()

    def post(self):
        ret = {'result': 'OK'}
        upload_path = os.path.join(
            os.path.dirname(__file__), 'files')  # 文件的暂存路径
        file_metas = self.request.files.get(
            'file', None)  # 提取表单中‘name’为‘file’的文件元数据

        if not file_metas:
            ret['result'] = 'Invalid Args'
            return ret

        for meta in file_metas:
            filename = meta['filename']
            file_path = os.path.join(upload_path, filename)

            with open(file_path, 'wb') as up:
                up.write(meta['body'])
                # OR do other thing

        self.write(json.dumps(ret))

@auth.auth(config.DEPLOYED_ENV['auth']['controller'])
class ControllerList(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        param_type = self.get_argument("type", "")
        param_env = self.get_argument("env", "")
        param_uid = self.get_argument("uid", "")

        if param_type and param_env and param_uid:
            # redirect by zoneid
            zoneid = int(param_env)
            if zoneid in config.ZONES:
                redirected_venv_name = config.ZONES[zoneid]['env']['redirection']
                venv = config.get_venv(redirected_venv_name)
                if venv:
                    if redirected_venv_name != config.VENV_NAME:  # 相同env_name无需重定向，否则会导致redirect死循环:
                        redirect_url = venv['domain'] + '/' + venv['path'] + '/modifier/list?' + \
                            'type=' + param_type + '&' + \
                            'env=' + param_env + '&' + \
                            'uid=' + param_uid
                        self.redirect(redirect_url)
                    else:
                        # 此处说明env_name相同，无需重定向
                        logger.debug('no need to redirect')
                else:
                    self.write('unknown redirected venv name: %s(%d)' %
                               (redirected_venv_name, zoneid))
                    return
            else:
                self.write('unknown zone id: %d' % zoneid)
                self.finish()
                return

        username = kwargs['username']
        auth_type = kwargs['auth_type']

        tabs = collections.OrderedDict()
        for module in ordered_modifier_modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C to comply with HTML name pattern
            tab_name = module.__name__.replace('.', '-')
            tabs[tab_name] = {'module_name': module.__name__,
                              'desc': module.__doc__, 'forms': util.get_forms_by_module(module)}
        for module in ordered_editor_modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C to comply with HTML name pattern
            tab_name = module.__name__.replace('.', '-')
            tabs[tab_name] = {'module_name': module.__name__,
                              'desc': module.__doc__, 'forms': util.get_forms_by_module(module)}
        # logger.debug(tabs)
        self.render('index.html', tabs = tabs, venv_name = config.VENV_NAME, deployed_venv = config.DEPLOYED_ENV, venvs = config.VENVS, zones = config.DEPLOYED_ZONES, username = username + ' (' + auth_type + ')', form_action = "/modifier/exec")

    get = post

@auth.auth(config.DEPLOYED_ENV['auth']['controller'])
class Execute(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        username = kwargs['username']
        extras = {'username': username}

        module_name = self.get_argument("__module_name__", "")
        # 暂时注释掉，兼容客户端请求的老接口，没有__module_name__参数就从所有模块找到第一个func就返回
        # 后续遇到冲突，让客户端在新接口上新增参数__module_name__，老接口不用改，已经兼容了
        # assert module_name, "module_name should be given"
        func_name = self.get_argument("__func_name__", "")
        assert func_name, "func_name should be given"
        func = None
        for key_module_name, val_module_tuple in all_modules.items():
            if module_name == "" or module_name == key_module_name:
                if func_name in val_module_tuple[1]:
                    func = val_module_tuple[1][func_name]
                    break
        assert func, ("not found func '%s' in module '%s'" %
                      (func_name, module_name))

        zone_id = int(self.get_argument("__env__"))
        platform_type = int(self.get_argument("__account_type__", "0"))

        world = zone_id >> 13
        zoneid = zone_id & 0x1FFF
        if world == config.WORLDS['WX']:
            pcl_conf = config.ENVS['idc_wx']['pcl']
            zone_conf = {'desc': 'WX' +
                         str(zoneid), 'env': config.ENVS['idc_wx']}
            env_addr = (pcl_conf['ip'], pcl_conf['port'],
                        zone_id, zone_conf, extras)
        elif world == config.WORLDS['QQ']:
            pcl_conf = config.ENVS['idc_qq']['pcl']
            zone_conf = {'desc': 'QQ' +
                         str(zoneid), 'env': config.ENVS['idc_qq']}
            env_addr = (pcl_conf['ip'], pcl_conf['port'],
                        zone_id, zone_conf, extras)
        else:
            if not zone_id or zone_id not in config.DEPLOYED_ZONES:
                self.write("not found zone: " + str(zone_id))
                return

            pcl_conf = config.DEPLOYED_ZONES[zone_id]['env']['pcl']
            env_addr = (pcl_conf['ip'], pcl_conf['port'],
                        zone_id, config.DEPLOYED_ZONES[zone_id], extras)

        print("env_addr: ", env_addr)

        func_args = util.get_func_args(func)
        args = []
        for arg_name in func_args[0]:
            logger.debug("arg_name: " + arg_name)
            if arg_name.endswith('__file'):
                # assume as file if arg_name's suffix is '_file'
                arg = self.request.files.get(arg_name, None)
            else:
                arg = self.get_argument(arg_name, None)
            if not arg:
                assert False, "%s should be given" % arg_name
            args.append(arg)

        ecode = -1
        need_write_ecode = True

        uidlist = []
        uidlist_str = self.get_argument("__uidlist__", None)
        if uidlist_str:
            uidlist = map(int, uidlist_str.splitlines())
        else:
            uidlist.append(args[0])

        for input_uid in uidlist:
            # 在这里确保一下是低32位
            # oid = int(input_uid) & 0xFFFFFFFF
            uid = int(input_uid)
            # if oid == uid:
            #     uid = util.gen_uid(zone_id, platform_type, oid)
            args[0] = uid
            args[1] = env_addr
            logger.info("base args: " + str(args))

            try:
                fixed_args = []
                for arg in args:
                    try:
                        fixed_args.append(int(arg))
                    except:
                        fixed_args.append(arg)
                logger.info("fixed args: " + str(fixed_args))
                # result规范：
                # 1. type(result) == tuple
                #   (error_code, content, {content_type: 'Content-Type', filename: 'filename'})
                # 2. 如果是json字符串，输出到前端json_editor
                # 3. 其它，直接输出result，并且附带字符串"\nSUCCESS"
                result = func(*fixed_args)
            except Exception as e:
                logger.warn(traceback.format_exc(), e)
                self.write(str(traceback.format_exc()))
            else:
                if isinstance(result, tuple):
                    # 如果返回类型是tuple，则默认第一个元素是error code
                    ecode = result[0]
                    if len(result) == 1:
                        need_write_ecode = True
                    else:
                        if ecode == 0:
                            if len(result) == 3 and isinstance(result[2], dict):
                                self.set_header(
                                    'Content-Type', result[2]['content_type'])
                                self.set_header(
                                    'content-Disposition', 'attachement; filename=' + result[2]['filename'])
                                self.write(result[1])  # file content
                                need_write_ecode = False
                            else:
                                for item in result[1:]:
                                    self.write(util.to_text(item))
                        else:
                            for item in result[1:]:
                                self.write(util.to_text(item))
                elif util.is_json(result):
                    # must only ouptut json data
                    self.write(util.to_text(result))
                    need_write_ecode = False
                else:
                    self.write(util.to_text(result))
                    ecode = 0

        if need_write_ecode:
            if ecode == 0:
                self.write(
                    '\n' + util.html_font(util.get_ecode_name(ecode), 'green'))
            else:
                self.write(
                    '\n' + util.html_font(util.get_ecode_name(ecode), 'red'))
        self.flush()  # Flushes the current output buffer to the network.

        # json_msg = {}
        # json_msg['ops'] = ChatHandler.get_chat_header(username)
        # json_msg['ops'].append(ChatHandler.get_chat_insert(u'任务: ' + func.__html_form__["title"]))
        # json_msg['ops'].append(ChatHandler.get_chat_insert(u'arguments: ' + str(self.request.arguments)))
        # json_msg['ops'].append(ChatHandler.get_chat_insert(u'result: ' + util.to_text(result)))
        # ChatHandler.broadcast(json.dumps(json_msg))

    get = post

@auth.auth(config.DEPLOYED_ENV['auth']['admin'])
class AdminList(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        username = kwargs['username']
        auth_type = kwargs['auth_type']

        tabs = collections.OrderedDict()
        for module in admin_ordered_modifier_modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C to comply with HTML name pattern
            tab_name = module.__name__.replace('.', '-')
            tabs[tab_name] = {'module_name': module.__name__,
                              'desc': module.__doc__, 'forms': util.get_forms_by_module(module)}
        for module in admin_ordered_editor_modules:
            # name pattern of python module is: A.B.C, convert it to A-B-C to comply with HTML name pattern
            tab_name = module.__name__.replace('.', '-')
            tabs[tab_name] = {'module_name': module.__name__,
                              'desc': module.__doc__, 'forms': util.get_forms_by_module(module)}
        # logger.debug(tabs)
        self.render('index.html', tabs = tabs, venv_name = config.VENV_NAME, deployed_venv = config.DEPLOYED_ENV, venvs = config.VENVS,  zones = config.DEPLOYED_ZONES, username = username + ' (' + auth_type + ')', form_action = "/admin/exec")

    get = post


@auth.auth(config.DEPLOYED_ENV['auth']['admin'])
class AdminExecute(tornado.web.RequestHandler):

    def post(self, *args, **kwargs):
        username = kwargs['username']
        extras = {'username': username}

        module_name = self.get_argument("__module_name__", "")
        # 暂时注释掉，兼容客户端请求的老接口，没有__module_name__参数就从所有模块找到第一个func就返回
        # 后续遇到冲突，让客户端在新接口上新增参数__module_name__，老接口不用改，已经兼容了
        # assert module_name, "module_name should be given"
        func_name = self.get_argument("__func_name__", "")
        assert func_name, "func_name should be given"
        func = None
        for key_module_name, val_module_tuple in all_modules.items():
            if module_name == "" or module_name == key_module_name:
                if func_name in val_module_tuple[1]:
                    func = val_module_tuple[1][func_name]
                    break
        assert func, ("not found func '%s' in module '%s'" %
                      (func_name, module_name))

        zone_id = int(self.get_argument("__env__"))
        platform_type = int(self.get_argument("__account_type__", "0"))

        world = zone_id >> 13
        zoneid = zone_id & 0x1FFF
        if world == config.WORLDS['WX']:
            pcl_conf = config.ENVS['idc_wx']['pcl']
            zone_conf = {'desc': 'WX' +
                         str(zoneid), 'env': config.ENVS['idc_wx']}
            env_addr = (pcl_conf['ip'], pcl_conf['port'],
                        zone_id, zone_conf, extras)
        elif world == config.WORLDS['QQ']:
            pcl_conf = config.ENVS['idc_qq']['pcl']
            zone_conf = {'desc': 'QQ' +
                         str(zoneid), 'env': config.ENVS['idc_qq']}
            env_addr = (pcl_conf['ip'], pcl_conf['port'],
                        zone_id, zone_conf, extras)
        else:
            if not zone_id or zone_id not in config.DEPLOYED_ZONES:
                self.write("not found zone: " + str(zone_id))
                return

            pcl_conf = config.DEPLOYED_ZONES[zone_id]['env']['pcl']
            env_addr = (pcl_conf['ip'], pcl_conf['port'],
                        zone_id, config.DEPLOYED_ZONES[zone_id], extras)

        print("env_addr: ", env_addr)

        func_args = util.get_func_args(func)
        args = []
        for arg_name in func_args[0]:
            logger.debug("arg_name: " + arg_name)
            if arg_name.endswith('__file'):
                # assume as file if arg_name's suffix is '_file'
                arg = self.request.files.get(arg_name, None)
            else:
                arg = self.get_argument(arg_name, None)
            if not arg:
                assert False, "%s should be given" % arg_name
            args.append(arg)

        ecode = -1
        need_write_ecode = True

        uidlist = []
        uidlist_str = self.get_argument("__uidlist__", None)
        if uidlist_str:
            uidlist = map(int, uidlist_str.splitlines())
        else:
            uidlist.append(args[0])

        for input_uid in uidlist:
            # 在这里确保一下是低32位
            oid = int(input_uid) & 0xFFFFFFFF
            uid = int(input_uid)
            if oid == uid:
                uid = util.gen_uid(zone_id, platform_type, oid)
            args[0] = uid
            args[1] = env_addr
            logger.info("base args: " + str(args))

            try:
                fixed_args = []
                for arg in args:
                    try:
                        fixed_args.append(int(arg))
                    except:
                        fixed_args.append(arg)
                logger.info("fixed args: " + str(fixed_args))
                # result规范：
                # 1. type(result) == tuple
                #   (error_code, content, {content_type: 'Content-Type', filename: 'filename'})
                # 2. 如果是json字符串，输出到前端json_editor
                # 3. 其它，直接输出result，并且附带字符串"\nSUCCESS"
                result = func(*fixed_args)
            except Exception as e:
                logger.warn(traceback.format_exc(), e)
                self.write(str(traceback.format_exc()))
            else:
                if isinstance(result, tuple):
                    # 如果返回类型是tuple，则默认第一个元素是error code
                    ecode = result[0]
                    if len(result) == 1:
                        need_write_ecode = True
                    else:
                        if ecode == 0:
                            if len(result) == 3 and isinstance(result[2], dict):
                                self.set_header(
                                    'Content-Type', result[2]['content_type'])
                                self.set_header(
                                    'content-Disposition', 'attachement; filename=' + result[2]['filename'])
                                self.write(result[1])  # file content
                                need_write_ecode = False
                            else:
                                for item in result[1:]:
                                    self.write(util.to_text(item))
                        else:
                            for item in result[1:]:
                                self.write(util.to_text(item))
                elif util.is_json(result):
                    # must only ouptut json data
                    self.write(util.to_text(result))
                    need_write_ecode = False
                else:
                    self.write(util.to_text(result))
                    ecode = 0

        if need_write_ecode:
            if ecode == 0:
                self.write(
                    '\n' + util.html_font(util.get_ecode_name(ecode), 'green'))
            else:
                self.write(
                    '\n' + util.html_font(util.get_ecode_name(ecode), 'red'))
        self.flush()  # Flushes the current output buffer to the network.

    get = post


class ExcelList(tornado.web.RequestHandler):

    def get(self, *args, **kwargs):
        self.post(*args, **kwargs)

    def post(self, *args, **kwargs):
        excel_path = "./static/xls/"
        filenames = [f for f in os.listdir(
            excel_path) if self.is_excel_file(excel_path, f)]
        self.render('xls.html', excels=filenames, venv_name=config.VENV_NAME)

    def is_excel_file(self, path, filename):
        if os.path.isfile(os.path.join(path, filename)):
            if filename.endswith("xls") or filename.endswith("xlsx"):
                return True
            else:
                return False
        else:
            return False


class ChatHandler(tornado.websocket.WebSocketHandler):

    clients = set()  # 用来存放在线用户的容器

    @classmethod
    def broadcast(cls, message):
        logger.info('broadcast: ' + message)
        for client in cls.clients:
            client.write_message(message)

    @classmethod
    def get_chat_header(cls, username):
        stats = '  Total: ' + str(len(cls.clients)) + \
            '  ' + util.time2strf(time.time()) + '\n'
        inserts = [
            {'insert': u'👤' + username, 'attributes': {"bold": True}},
            {'insert': stats, 'attributes': {"color": "#ccc", 'italic': True}}
        ]
        return inserts

    @classmethod
    def get_chat_insert(cls, line):
        return {'insert': line + '\n'}

    def get_welcome_insert(self):
        return {
            'insert': u'— Welcome, ' + self.username + u' joins chat room —\n',
            'attributes': {"color": "#aaa", 'align': 'center'}
        }

    def get_goodbye_insert(self):
        return {
            'insert': u'— Goodbye, ' + self.username + u' leaves chat room —\n',
            'attributes': {"color": "#aaa", 'align': 'center'}
        }

    def open(self):
        self.username = 'anonymous'
        ChatHandler.clients.add(self)  # 建立连接后添加用户到容器中

    def on_message(self, message):
        json_msg = json.loads(message)

        if 'username' in json_msg:
            for client in ChatHandler.clients:
                if self == client:
                    self.username = json_msg['username']
                    json_msg['ops'] = [self.get_welcome_insert()]
                    break
        else:
            json_msg['ops'] = ChatHandler.get_chat_header(
                self.username) + json_msg['ops']

        message = json.dumps(json_msg)
        ChatHandler.broadcast(message)

    def on_close(self):
        # 用户关闭连接后从容器中移除用户(注意，此时client连接已经不可用)
        ChatHandler.clients.remove(self)

        json_msg = {}
        json_msg['ops'] = self.get_goodbye_insert()
        message = json.dumps(json_msg)
        ChatHandler.broadcast(message)

    def check_origin(self, origin):
        return True  # 允许WebSocket的跨域请求

def start_app(start_mode):
    tornado.options.parse_command_line()

    # load all modifiers and editors
    LoadAllModifiers()
    LoadAllEditors()
    AdminLoadAllModifiers()
    AdminLoadAllEditors()

    # NOTES:
    # Application Class dafault constructor:
    # Application(handlers=None, default_host=None, transforms=None, **settings)
    #
    # application arg: handlers
    handlers = [
        (r'/(favicon.ico)', tornado.web.StaticFileHandler, {"path": ""}),
        (r'/', ControllerList),
        (r'/modifier/', ControllerList),
        (r'/modifier/list', ControllerList),
        (r'/modifier/exec', Execute),

        (r'/admin/', AdminList),
        (r'/admin/list', AdminList),
        (r'/admin/exec', AdminExecute),

        (r'/excel/list', ExcelList),
        (r'/chatroom', ChatHandler),

        (r'/file', FileUploadHandler),
    ]
    # application kwargs: settings
    settings = {'debug': True,  # if in multiprocess mode, set `debug = False`
                'static_path': './static',
                'template_path': "./template"
                }

    if start_mode == 'singleprocess':
        settings["debug"] = False
        app = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(app)
        server.listen(config.DEPLOYED_ENV['port'])
    elif start_mode == 'multiprocess':
        settings["debug"] = False
        app = tornado.web.Application(handlers, **settings)
        server = tornado.httpserver.HTTPServer(app)
        server.bind(config.DEPLOYED_ENV['port'])
        # value 0 means: autodetect cpu cores and fork one process per core
        server.start(4)
    else:
        logger.error("unknown start mode: " + start_mode)
        Usage()
        exit(-1)

    def periodic_task():
        logger.info("periodic_task at " + 'tornado.process.task_id: ' +
                    str(tornado.process.task_id()))

    logger.info('tornado.process.task_id: ' + str(tornado.process.task_id()))
    if not tornado.process.task_id():
        tornado.ioloop.PeriodicCallback(periodic_task, 10 * 1000).start()

    try:
        # start web server
        tornado.ioloop.IOLoop.current().start()
    except:
        logger.error("An exception occurred" + traceback.format_exc())

def Usage():
    # help(sys.modules[__name__])
    print(sys.modules[__name__].__doc__)


if __name__ == "__main__":
    if len(sys.argv) == 1:
        start_mode = "singleprocess"
        start_app(start_mode)
    elif len(sys.argv) == 2:
        start_mode = sys.argv[1]
        start_app(start_mode)
    elif len(sys.argv) == 3:
        start_mode = sys.argv[1]
        env = sys.argv[2]
        logger.info("start_mode: %s|env: %s" % (start_mode, env))
        start_app(start_mode)
    else:
        logger.error("error: illegal args")
        Usage()
        exit(-1)
