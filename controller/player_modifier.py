# coding=utf-8

'''玩家数据'''
__priority__ = 9999999

from core import form
import config

@form.onpage
def process_time_offset(__uid__, __env__, dst_svr_id, datetime_str, opcode):
    '''
    {
        "title": "服务器时间",
        "args": {
            "dst_svr_id": {
                "desc": "服务器",
                "tip": "如果不知道改哪个服务器时间，就选择: 所有服务器",
                "input": "select",
                "options": "$kwargs.get_svr_dict1"
            },
            "datetime_str": {
                "desc": "设置时间",
                "input": "datetime"
            },
            "opcode": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                    "0": "查 询",
                    "1": "设 置",
                    "2": "复 位"
                }
            }
        },
        "submit": "opcode"
    }
    '''

    return -1, "not implemented"

@form.onpage
def send_mail(__uid__, __env__, mail_type, title, content, attachment="0"):
    '''
    {
        "title": "发送邮件",
        "args": {
            "mail_type": {
                "desc": "类型",
                "input": "select",
                "options": {
                     "1": "系统邮件",
                     "2": "好友邮件"
                }
            },
            "title": {
                "desc": "标题",
                "placeholder": "邮件标题"
            },
            "content": {
                "desc": "内容",
                "input": "textarea",
                "placeholder": "邮件内容"
            },
            "attachment": {
                "desc": "附件",
                "tip": "id:num|id:num ...（标点全部为英文符号）",
                "placeholder": "id:num|id:num ...",
                "datalist": {
                    "0": "无附件",
                    "10000001:10|10000006:20": "10个金币|20个梦域结晶"
                }
            }
        }
    }
    '''
    print("title type: ", type(title))
    title = title.encode('utf-8')
    content = content.encode('utf-8').decode('string_escape')

    print(attachment)
    if attachment:
        attachment = [map(int, e.split(':')) for e in attachment.split('|')]
        print(attachment)

 
    return -1, "not implemented"

@form.onpage
def modify_item(__uid__, __env__, id, num):
    '''
    {
        "title": "增减道具",
        "args": {
            "id": {
                "datalist": "$kwargs.get_item_dict"
            },
            "num": {
                "tip": "负号(-): 减少",
                "default": "100"
            }
        }
    }
    '''
    return -1, "not implemented"