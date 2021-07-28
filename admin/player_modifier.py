# coding=utf-8

'''玩家'''
__priority__ = 999

import config
from core import form

@form.onpage
def manage_whilelist(__uid__, __env__, whitelist_type, content, operate_type):
    '''
    {
        "title": "白名单管理",
        "args": {
            "whitelist_type": {
                "desc": "白名单类型",
                "input": "select",
                "options": {
                     "normal": "限号白名单",
                     "inernal": "内部白名单",
                     "advanced": "高级白名单"
                }
            },
            "content": {
                "tip": "每行一个openid",
                "desc": "openids",
                "input": "textarea"
            },
            "operate_type": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                    "0": "查 询",
                    "1": "新 增",
                    "2": "删 除"
                }
            }
        },
        "submit": "operate_type"
    }
    '''
    return -1, "not implemented"