# coding=utf-8
'''Redis'''
__priority__ = 200

from core import form
#import redis

@form.onpage
def redis_batch_manage(__uid__, __env__, key_prefix, operation_type):
    '''
    {
        "title": "Redis数据批量管理",
        "args": {
            "key_prefix": {
                "desc": "Key前缀",
                "default": "*",
                "datalist": {
                    "WEEKLY_FUBEN_ROOM_KEY_": "周常本:房间数据",
                    "WEEKLY_FUBEN_AVG_PASS_TIME_": "周常本:平均通关时间"
                }
            },
            "operation_type": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                    "0": "查询",
                    "1": "删除"
                }
            }
        },
        "submit": "operation_type"
    }
    '''
    # redis_conf = __env__[3]['env']['redis']
    # redis_client = redis.Redis(redis_conf['ip'], port = redis_conf['port'], db = 0, password = redis_conf['passwd'])

    # key_wildcard = key_prefix + "*"
    # if operation_type == 0:
    #     keys = redis_client.keys(key_wildcard)
    #     log_str ="count: " + str(len(keys)) + "\n" + "\n".join(keys)
    #     return log_str
    # elif operation_type == 1:
    #     keys = redis_client.keys(key_wildcard)
    #     log_str ="count: " + str(len(keys)) + "\n" + "\n".join(keys)
    #     redis_result = redis_client.delete(*keys)
    #     return 0, log_str + "\n" + str(redis_result)
    # else:
    #     return 'unknown operation_type'

    return -1, "not implemented"

@form.onpage
def redis_flushall(__uid__, __env__):
    '''
    {
        "title": "清空Redis",
        "popup": "confirm"
    }
    '''
    # redis_conf = __env__[3]['env']['redis']
    # redis_client = redis.Redis(redis_conf['ip'], port = redis_conf['port'], db = 0, password = redis_conf['passwd'])

    # redis_client.flushall()
    return -1, "not implemented"

@form.onpage
def redis_exec(__uid__, __env__, cmd_content):
    '''
    {
        "title": "Redis Command",
        "popup": "confirm",
        "args": {
            "cmd_content": {
                "desc": "指令",
                "input": "textarea",
                "default": "keys *"
            }
        }
    }
    '''
    # redis_conf = __env__[3]['env']['redis']
    # redis_client = redis.Redis(redis_conf['ip'], port = redis_conf['port'], db = 0, password = redis_conf['passwd'])
    
    # return redis_client.execute_command(cmd_content)
    return -1, "not implemented"