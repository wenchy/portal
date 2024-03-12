import json
import inspect
import collections
from core.logger import log
from core import kwargs
import config
import traceback


def onpage(func):
    """
    onpage renders the Python function to HTML form.
    """
    html_form(func)
    return func


def html_form(func):
    argspec = inspect.getargspec(func)
    defaults_len = 0
    if argspec[3]:
        defaults_len = len(argspec[3])
    default_start = len(argspec[0]) - defaults_len
    index = 0
    args = collections.OrderedDict()
    for arg in argspec[0]:
        if index >= default_start:
            args[arg] = argspec[3][index - default_start]
        else:
            args[arg] = ""
        index += 1
    # Tip of initial form struct: {'title': '','tip': '',  'args': {}}
    ordered_form = collections.OrderedDict()
    ordered_form = {"title": func.__name__, "args": collections.OrderedDict()}

    def parse_form(form, args, ordered_form):
        if "title" in form:
            ordered_form["title"] = form["title"]
        if "target" in form:
            ordered_form["target"] = form["target"]
        if "method" in form:
            ordered_form["method"] = form["method"]
        if "enctype" in form:
            ordered_form["enctype"] = form["enctype"]
        if "tip" in form:
            ordered_form["tip"] = form["tip"]
        if "popup" in form:
            ordered_form["popup"] = form["popup"]
        if "submit" in form:
            ordered_form["submit"] = form["submit"]
        if "layout" in form:
            ordered_form["layout"] = form["layout"]
        if "theme" in form:
            ordered_form["theme"] = form["theme"]
        if not "args" in form:
            form["args"] = {}
        # Required: desc, input, and default
        for arg_name, default in args.items():
            if arg_name in form["args"]:
                ordered_form["args"][arg_name] = form["args"][arg_name]
                if not "desc" in form["args"][arg_name]:
                    ordered_form["args"][arg_name]["desc"] = arg_name
                if not "input" in form["args"][arg_name]:
                    ordered_form["args"][arg_name]["input"] = "text"
                if not "default" in form["args"][arg_name]:
                    ordered_form["args"][arg_name]["default"] = default
                if not "status" in form["args"][arg_name]:
                    ordered_form["args"][arg_name]["status"] = ""
            else:
                ordered_form["args"][arg_name] = {
                    "desc": arg_name,
                    "input": "text",
                    "default": default,
                    "status": "",
                }

            # evaluate dynamic values, pattern: "$VAR"
            for key, value in ordered_form["args"][arg_name].items():
                log.debug("func:%s|key:%s|value:%s", func.__name__, key, value)
                if isinstance(value, str) and value and value[0] == "$":
                    retval = eval(value[1:], None, func.__globals__)
                    if callable(retval):
                        retval = retval()
                    ordered_form["args"][arg_name][key] = retval

        log.debug(json.dumps(ordered_form))

    log.debug("%s, %s\n%s", func.__name__, str(type(func.__doc__)), func.__doc__)

    try:
        form = json.loads(func.__doc__, object_pairs_hook=collections.OrderedDict)
        parse_form(form, args, ordered_form)
    except Exception as e:
        log.warning("exception: %s\n%s", str(e), traceback.format_exc())
        log.debug(
            str(e)
            + ", Unable to decode docstring as JSON, then just treat it as title: "
            + func.__name__
        )

        if func.__doc__:
            ordered_form["title"] = func.__doc__

        # Required: desc, input, and default
        for arg_name, default in args.items():
            # convert arg name 'A_B_C' to 'A B C' as arg desc, for HTML words to auto break line
            ordered_form["args"][arg_name] = {
                "desc": arg_name.replace("_", " "),
                "input": "text",
                "default": "",
                "status": "",
            }
            ordered_form["args"][arg_name]["default"] = default

    if "layout" not in ordered_form:
        ordered_form["layout"] = "1-column"
    if "theme" not in ordered_form:
        ordered_form["theme"] = "primary"

    if config.VENV_NAME == "mini":
        log.debug("mini venv: need confirm when submit the form")
        ordered_form["popup"] = "prompt"
        ordered_form["theme"] = "danger"

    # log.debug(json.dumps(form))
    func.__html_form__ = ordered_form
    # log.debug(str(ordered_form))
    return func


def exist_json_func(pattern):
    """pattern: ${module_name}.{func_name}"""
    if (
        (type(pattern) == str)
        and pattern.startswith("$")
        and len(pattern.split(".")) == 2
    ):
        return True
    return False


def call_json_func(pattern):
    """pattern: ${module_name}.{func_name}"""
    module_name, func_name = tuple(pattern.split("."))
    module_dict = {"$kwargs": kwargs}
    return getattr(module_dict[module_name], func_name)()
