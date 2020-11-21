'''编辑器'''
__priority__ = 0

from core import form

@form.onpage
def manage_role_data(__uid__, __env__, __jsoneditor_content__, operation_type):
    '''
    {
        "title": "玩家数据",
        "args": {
            "operation_type": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                     "1": "查 询",
                     "2": "修 改",
                     "3": "删 除"
                }
            }
        },
        "submit": "operation_type"
    }
    '''
    return -1, "not implemented"