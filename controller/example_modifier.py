"""ExampleModifier"""

__priority__ = 9999

import time
import collections
from core import form
from core import util
from core.context import Context


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
def process_server_time(ctx, svr_name, datetime_str, opcode):
    """
    {
        "title": "Server Time Manager",
        "args": {
            "svr_name": {
                "desc": "Server",
                "tip": "default: all",
                "input": "select",
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
                    "1": "Set",
                    "2": "Reset"
                }
            }
        },
        "submit": "opcode"
    }
    """
    opcode = int(opcode)

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
def modify_item(ctx, id, num):
    """
    {
        "title": "Modify Item",
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
    return f"id: {id}, num: {num}"


@form.onpage
def manage_whilelist(ctx, whitelist_type, content, opcode):
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


@form.onpage
def send_mail(ctx, title, content, attachments=""):
    """
    {
        "title": "Send Mail",
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

    return title, content, attachments


@form.onpage
def upload(ctx, upload__file):
    """
    {
        "title": "Upload File",
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
def download(ctx):
    """
    {
        "title": "Download File",
        "target": "_blank"
    }
    """
    filename = "test.txt"
    content = "This file content is generated from portal."
    return 0, content, {"content_type": "text/plain", "filename": filename}


@form.onpage
def confirm(ctx):
    """
    {
        "title": "Popup Confirm",
        "popup": "confirm"
    }
    """
    return "confirmed"

@form.onpage
def multi_checkbox(ctx, boxes, boxes2):
    """
    {
        "title": "Multi Checkbox",
        "args": {
            "boxes": {
                "input": "checkbox",
                "desc": "Fruit",
                "options": {
                   "a": "apple",
                   "b": "banana",
                   "c": "original"
                }
            },
            "boxes2": {
                "input": "checkbox",
                "desc": "Animinal",
                "options": {
                   "d": "bee",
                   "e": "dog",
                   "f": "cat"
                }
            }
        }
    }
    """
    # boxes return a,b,c
    # boxes2 return d,e,f
    #return -1, str(a) + "-" + str(b) + "-"+ str(c)
    return 0, str(boxes) + "-" + str(boxes2) 
