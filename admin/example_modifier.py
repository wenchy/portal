"""Example"""

__priority__ = 1

from core import form


@form.onpage
def manage_whilelist(_ctx, whitelist_type, content, opcode):
    """
    {
        "title": "Whitelist Manager",
        "args": {
            "whitelist_type": {
                "desc": "Type",
                "input": "select",
                "options": {
                    "1": "Primary",
                    "2": "Advanced"
                }
            },
            "content": {
                "tip": "one OpenID per line",
                "desc": "OpenID",
                "input": "textarea"
            },
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
    return -1, "not implemented"
