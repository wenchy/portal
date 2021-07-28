# coding:utf-8

import os
import json
import inspect
import collections
import re
import datetime, time
import functools
import tornado
from google.protobuf.message import Message as ProtoBufMessage
from core.logger_factory import logger
from google.protobuf import text_format
import config
import socket
import traceback

def get_forms_by_module(module):
    forms = collections.OrderedDict()
    #funcs = inspect.getmembers(module, inspect.isfunction)
    funcs = get_ordered_funcs_by_module(module)
    for func in funcs:
        if hasattr(func[1], "__html_form__"):
            forms[func[0]] = getattr(func[1], "__html_form__")
    return forms

def get_ordered_funcs_by_module(module):
    func_dict = {}
    for func in inspect.getmembers(module, inspect.isfunction):
        func_dict[func[0]] = func[1]
    ordered_funcs = []
    func_pattern = re.compile(r'def *([\w]+)\(')
    logger.debug("filepath: " + module.__file__)
    with open(os.path.splitext(module.__file__)[0] + '.py', 'r') as file:
        func_names = func_pattern.findall(file.read())
        for func_name in func_names:
            # 剔除func_pattern匹配到的被注释掉的函数
            if func_name in func_dict:
                ordered_funcs.append((func_name, func_dict[func_name]))
    logger.debug("ordered_funcs" + str(ordered_funcs))
    return ordered_funcs

def excelviewer(table_name, sheet_name):
    def decorator(func):
        func.__excelviewer__ = (table_name, sheet_name)
        return func
    return decorator

def get_func_args(func):
    return inspect.getargspec(func)

def get_module_by_name(module_name):
    imported_module = __import__(name=module_name)
    return imported_module

def get_func_by_module(module):
    methods = {}
    for method in dir(module):
        method = getattr(module, method)
        if callable(method) and hasattr(method, "__html_form__"):
            methods[method.__name__] = method
    return methods

def get_func_by_module_name(module_name):
    imported_module = get_module_by_name(module_name)
    methods = get_func_by_module(imported_module)
    return methods

def is_json(test_str):
    try:
        json.loads(test_str)
    except BaseException:
        return False
    return True

def get_ecode_name(ecode):
    try:
        if ecode == 0:
            return "OK"
        else:
            return "Error: " + str(ecode)
    except KeyError:
        return "Error: ERR_UNKNOWN(%d)" % ecode

def strf2time(timestr, format = '%Y-%m-%d %H:%M:%S'):
    return int(datetime.datetime.strptime(timestr, format).strftime("%s"))

def time2strf(timestamp, format = '%Y-%m-%d %H:%M:%S'):
        return datetime.datetime.fromtimestamp(timestamp).strftime(format)

def gen_uid(zone_id, plat_id, uin):
    # uid = 16位区号 + 16位平台类型 + 32位uin
    return (zone_id * (1 << 48)) | (plat_id << 32) | uin

def get_world(uid):
    # uid = 16位区号(3位world + 13位zone) + 16位平台类型 + 32位uin
    return get_zoneid(uid) >> 13

def get_zone(uid):
    # uid = 16位区号(3位world + 13位zone) + 16位平台类型 + 32位uin
    return get_zoneid(uid) & 0x1FFF 

def get_zoneid(uid):
    # uid = 16位区号(3位world + 13位zone) + 16位平台类型 + 32位uin
    return uid >> 48

def get_platid(uid):
    # uid = 16位区号(3位world + 13位zone) + 16位平台类型 + 32位uin
    return uid >> 32 & 0x0000FFFF

def get_uin(uid):
    # uid = 16位区号(3位world + 13位zone) + 16位平台类型 + 32位uin
    return uid & 0x00000000FFFFFFFF

def to_text(item):
    # tornado write() only accepts bytes, str, and dict objects
    if item == None:
        return str(item)
    elif isinstance(item, ProtoBufMessage):
        return text_format.MessageToString(item, as_utf8 = True)
    elif isinstance(item, (str, bytes)):
        # Converts an itme to a  tring.
        # If the argument is already a string or None, it is returned unchanged.
        # Otherwise it must be a byte string and is decoded as utf8.
        return tornado.escape.to_unicode(item)
    else:
        return tornado.escape.to_unicode(str(item))

def zoneid(world, zone):
    # world:3.zone:13.function:6.instance:10
    # world: max 7 (2 ** 3 - 1)
    #   1: 微信
    #   2: QQ
    #   7: 测试(包括开发环境和测试环境)
    # zone: max 8191 (2 ** 13 - 1)
    return (world << 13) + zone

def busid2str(bus_id):
    # world:3.zone:13.function:6.instance:10
    busid = socket.ntohl(bus_id)
    world = str(busid >> 29)
    zone = str((busid >> 16) & 0x1FFF)
    function = str((busid & 0xFFFF) >> 10)
    instance = str((busid & 0xFFFF) & 0x3ff)
    return world + '.' + zone + '.' + function + '.' + instance

def html_font(input, color = 'black'):
    return '<font color="' + color + '"><b>' + input + '</b></font>'

def clean_html(raw_html):
    # re.compile('<.*?>')
    cleanre = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    cleantext = re.sub(cleanre, '', raw_html)
    return cleantext

def main():
    pass

if __name__ == "__main__":
    main()
