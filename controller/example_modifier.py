"""ExampleModifier"""

__priority__ = 9999

import time
import collections
from core import form
from core import util
from core.context import Context
from typing import *


# NOTE: function which returns dict can be injected into form "options"
# or "datalist", and it will be dynamically evaluated.
# Injection pattern: "$FUNC_NAME"
def gen_server_dict():
    servers = collections.OrderedDict()
    servers["all"] = "All Servers"
    servers["gamesvr"] = "Game Server"
    servers["activitysvr"] = "Activity Server"
    return servers


@form.onpage
def process_server_time(ctx: Context, svr_name: str, datetime_str: str, opcode: int):
    """
    {
        "title": "Server time",
        "args": {
            "svr_name": {
                "desc": "Server",
                "tip": "default: all",
                "input": "selectpicker",
                "options": "$gen_server_dict"
            },
            "datetime_str": {
                "desc": "Datetime",
                "input": "datetime"
            },
            "opcode": {
                "desc": "Operation",
                "input": "select",
                "options": {
                    "0": "Query",
                    "100": "Set",
                    "101": "Reset"
                }
            }
        },
        "submit": "opcode"
    }
    """
    offset = util.strf2time(datetime_str) - int(time.time())

    return f"server {svr_name} time offset: {offset}"


# NOTE: variable which is dict can be injected into form "options"
# or "datalist", and it will be dynamically evaluated.
# Injection pattern: "$VAR_NAME"
_ITEM_DICT = collections.OrderedDict()
_ITEM_DICT["100001"] = "Coin"
_ITEM_DICT["100002"] = "Diamond"
_ITEM_DICT["100003"] = "Sword"


@form.onpage
def modify_item(ctx: Context, id: int, num: int):
    """
    {
        "title": "Modify item",
        "args": {
            "id": {
                "datalist": "$_ITEM_DICT"
            },
            "num": {
                "tip": "negative number (-): decrease",
                "default": "1"
            }
        }
    }
    """
    type1 = type(id).__name__
    output = f"id: {id}, type is '{type1}'\n"
    type2 = type(num).__name__
    output += f"num: {num}, type is '{type2}'"
    return output


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


@form.onpage
def send_mail(ctx: Context, title: str, content: str, attachments: str = ""):
    """
    {
        "title": "Send mail",
        "args": {
            "title": {
                "desc": "Title",
                "placeholder": "mail title",
                "datalist": {
                    "Reward": "Reward",
                    "Announcement": "Announcement"
                }
            },
            "content": {
                "desc": "Content",
                "input": "textarea",
                "placeholder": "mail content"
            },
            "attachments": {
                "desc": "Attachments",
                "tip": "id:num,id:num ...",
                "placeholder": "id:num,id:num ...",
                "datalist": {
                    "100000:100,200000:200": "100 coins|200 diamonds",
                    "100000:500,200000:900": "500 coins|900 diamonds",
                    "100000:100": "100 coins"
                }
            }
        }
    }
    """

    title = title.encode("utf-8")
    content = content.encode("utf-8")

    if attachments:
        attachments = [map(int, e.split(":")) for e in attachments.split(",")]

    return [title, content, attachments]


@form.onpage
def upload(ctx: Context, upload__file):
    """
    {
        "title": "Upload file",
        "enctype": "multipart/form-data",
        "args": {
            "upload__file": {
                "tip": "test.txt",
                "desc": "File Path",
                "input": "file"
            }
        }
    }
    """
    content = upload__file[0]["body"]
    return 0, content


@form.onpage
def download(ctx: Context):
    """
    {
        "title": "Download file",
        "target": "_blank"
    }
    """
    filename = "test.txt"
    content = "This file content is generated from portal."
    return 0, content, {"content_type": "text/plain", "filename": filename}


@form.onpage
def confirm(ctx: Context):
    """
    {
        "title": "Popup confirm",
        "popup": "confirm"
    }
    """
    return "confirmed"


@form.onpage
def multi_checkbox(ctx: Context, boxes, boxes2: List[int]):
    """
    {
        "title": "Multi checkbox",
        "args": {
            "boxes": {
                "input": "checkbox",
                "options": {
                   "1": "apple",
                   "2": "banana",
                   "3": "original"
                }
            },
            "boxes2": {
                "input": "checkbox",
                "options": {
                   "10": "bee",
                   "20": "dog",
                   "30": "cat"
                }
            }
        }
    }
    """
    type1 = type(boxes).__name__
    output = f"boxes: {boxes}, type is '{type1}'\n"
    type2 = type(boxes2).__name__
    output += f"boxes2: {boxes2}, type is '{type2}'"
    return output


@form.onpage
def selectpicker(ctx: Context, box: int, boxes2: List[int]):
    """
    {
        "title": "Select picker",
        "args": {
            "box": {
                "input": "selectpicker",
                "options": {
                   "1": "apple",
                   "2": "banana",
                   "3": "original"
                }
            },
            "boxes2": {
                "input": "selectpicker",
                "multiple": true,
                "options": {
                   "10": "bee",
                   "20": "dog",
                   "30": "cat"
                }
            }
        }
    }
    """
    type1 = type(box).__name__
    output = f"box: {box}, type is '{type1}'\n"
    type2 = type(boxes2).__name__
    output += f"boxes2: {boxes2}, type is '{type2}'"
    return output


@form.onpage
def multi_form_target(ctx: Context, zone: int, opcode: int, upload__file):
    """
    {
        "title": "Multi form target",
        "enctype": "multipart/form-data",
        "args": {
            "zone": {
              "desc": "Zone",
              "default": "1"
            },
            "opcode": {
                "desc": "操作类型",
                "input": "select",
                "options": {
                    "0": "Download",
                    "1": "Upload",
                    "2": "Run"
                },
                "targets": {
                    "0": "_blank",
                    "1": "_self",
                    "2": "_blank"
                }
            },
            "upload__file": {
                "tip": "test.txt",
                "desc": "File Path",
                "input": "file"
            }
        },
        "submit": "opcode"
    }
    """

    if opcode == 0:
        # download
        filename = "test.txt"
        content = "This file content is generated from portal."
        return 0, content, {"content_type": "text/plain", "filename": filename}
    elif opcode == 1:
        # upload
        content = upload__file[0]["body"]
        return 0, content
    elif opcode == 2:
        filename = "result.txt"
        content = f"Run zone: {zone}"
        return 0, content, {"content_type": "text/plain", "filename": filename}

    return -1, "not implemented"
