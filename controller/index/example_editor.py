"""Editor"""

__priority__ = 1000

import json
from core import form
from core.context import Context


@form.onpage
def manage_player(ctx: Context, _jsoneditor_content: str, opcode: int):
    """
    {
        "title": "Player data",
        "args": {
            "opcode": {
                "desc": "Operation",
                "input": "select",
                "options": {
                     "0": "Query",
                     "100": "Update",
                     "200": "Delete"
                }
            }
        },
        "submit": "opcode"
    }
    """
    data = {}
    data["stringKey"] = "value1"
    data["numberKey"] = 2024
    data["arrayKey"] = [1, 2, 3]
    data["mapKey1"] = {"k1": 1, "k2": 2}
    data["mapKey2"] = {"k1": True, "k2": False}
    json_data = json.dumps(data)

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
