"""Modifier"""

__priority__ = 1

from core import form
from core.context import Context


@form.onpage
def manage_whilelist(ctx: Context, whitelist_type: int, content: str, opcode: int):
    """
    {
        "title": "Whitelist",
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
                     "100": "Update",
                     "200": "Delete"
                }
            }
        },
        "submit": "opcode"
    }
    """
    return -1, "not implemented"
