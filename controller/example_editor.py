"""ExampleEditor"""

__priority__ = 1000

import json
from core import form


@form.onpage
def manage_player(_ctx, _jsoneditor_content, opcode):
    """
    {
        "title": "Player Manager",
        "args": {
            "opcode": {
                "desc": "Operation",
                "input": "select",
                "options": {
                     "0": "Query",
                     "1": "Update",
                     "2": "Delete"
                }
            }
        },
        "submit": "opcode"
    }
    """
    data = {}
    data["key1"] = "value1"
    data["key2"] = {"k1": 1, "k2": 2}
    data["key3"] = [1, 2, 3]
    data["key4"] = {"k1": True, "k2": False}
    json_data = json.dumps(data)

    opcode = int(opcode)
    if opcode == 0:
        # TODO: query
        return json_data
    elif opcode == 1:
        # TODO: update
        return json_data
    elif opcode == 2:
        # TODO: delete
        return

    return -1, "not implemented"
