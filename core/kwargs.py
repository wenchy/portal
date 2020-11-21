# coding=utf-8
import collections
import sys
sys.path.append("common")

MAX_ITEM_NUM = 200

print("sys.getdefaultencoding(): ", sys.getdefaultencoding())
print("sys.stdin.encoding: ", sys.stdin.encoding)
print("sys.stdout.encoding: ", sys.stdout.encoding)
print("sys.stderr.encoding: ", sys.stderr.encoding)

def get_item_dict():
    gen_dict = collections.OrderedDict()
    gen_dict['10000001'] = "金币"
    gen_dict['10000014'] = "荣耀之力"
    gen_dict['10000002'] = "钻石"
    gen_dict['10000006'] = "梦域结晶"
    gen_dict['11000003'] = "复活币"
    gen_dict['79980001'] = "角色体验药"
    return gen_dict

def get_svr_dict():
    gen_dict = collections.OrderedDict()
    gen_dict['1.0.3.1'] = "区服(zone)"
    gen_dict['1.0.4.1'] = "邮件(mail)"
    return gen_dict

def get_svr_dict1():
    d1 = collections.OrderedDict([('0.0.0.0', '所有服务器')])
    d2 = get_svr_dict()
    return collections.OrderedDict(list(d1.items()) + list(d2.items()))