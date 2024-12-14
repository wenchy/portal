"""Editor"""

__priority__ = 1000

import json
from core import form
from core.context import Context


@form.onpage
def manage_player(ctx: Context, editor: form.Editor, opcode: int):
    """
    {
        "title": "Player data",
        "args": {
            "editor": {
                "input": "editor"
            },
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
        return form.Editor(json_data)
    elif opcode == 100:
        # TODO: update
        return editor
    elif opcode == 200:
        # TODO: delete
        return form.Editor()

    return -1, "not implemented"
