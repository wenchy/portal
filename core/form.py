import json
import collections
from core.logger import log
import config
import traceback
from typing import Any, Type, get_type_hints
import inspect
import functools
from tornado import httputil


def convert_type(value: Any, target_type: Type) -> Any:
    """Convert value to the target_type."""
    log.debug(f"value: {value}, target_type: {target_type}")
    if target_type == int:
        return int(value)
    elif target_type == float:
        return float(value)
    elif target_type == str:
        return str(value)
    elif target_type == bool:
        return bool(value)
    elif target_type == File:
        # see https://www.tornadoweb.org/en/stable/httputil.html#tornado.httputil.HTTPFile
        if not value:
            return None
        file: httputil.HTTPFile = value
        return File(file.filename, file.body, file.content_type)
    elif target_type == Editor:
        if not value:
            return None
        return Editor(value)
    elif hasattr(
        target_type, "__origin__"
    ):  # Handle generic types like List, Dict, etc.
        origin = target_type.__origin__
        if origin is list:
            item_type = target_type.__args__[0]
            return [convert_type(item, item_type) for item in value]
        elif origin is dict:
            key_type, value_type = target_type.__args__
            return {
                convert_type(k, key_type): convert_type(v, value_type)
                for k, v in value.items()
            }
        elif origin is tuple:
            item_types = target_type.__args__
            return tuple(
                convert_type(value[i], item_types[i]) for i in range(len(item_types))
            )
    return value  # Return the original value if no conversion is needed


def type_converter(func):
    """
    Decorator to convert argument types based on type annotations,
    but leaves the types unchanged if no annotations are provided.
    """

    @functools.wraps(func)  # Preserve the original function's metadata
    def wrapper(*args, **kwargs):
        # Get the function's signature and type hints
        sig = inspect.signature(func)
        type_hints = get_type_hints(func)

        # Convert positional arguments
        converted_args = []
        for param, arg in zip(sig.parameters.values(), args):
            if param.name in type_hints:  # Check if there's a type hint
                converted_args.append(convert_type(arg, type_hints[param.name]))
            else:
                converted_args.append(arg)  # Leave unchanged if no annotation

        # Convert keyword arguments
        converted_kwargs = {}
        for k, v in kwargs.items():
            if k in type_hints:  # Check if there's a type hint
                converted_kwargs[k] = convert_type(v, type_hints[k])
            else:
                converted_kwargs[k] = v  # Leave unchanged if no annotation

        return func(*converted_args, **converted_kwargs)

    return wrapper


def onpage(func):
    """
    - Rendering a Python function to an HTML form.
    - Convert argument types based on type annotations.
    """

    # Set the __html_form__ attribute on the wrapper
    func.__html_form__ = parse_html_form(func)

    return type_converter(func)


def parse_html_form(func):
    """A powerful tool for generating HTML forms based on function signatures and documentation"""
    signature = inspect.signature(func)
    args = collections.OrderedDict()

    # Collect argument names and default values
    for param in signature.parameters.values():
        if param.default is param.empty:
            args[param.name] = ""
        else:
            args[param.name] = param.default

    # Initialize the ordered form structure
    # E.g.: {'title': '', 'args': {}}
    ordered_form = {"title": func.__name__, "args": collections.OrderedDict()}

    def parse_form(form, args, ordered_form):
        # Populate ordered_form based on the form input
        form_props = [
            "title",
            "target",
            "method",
            "enctype",
            "tip",
            "popup",
            "submit",
            "layout",
            "theme",
        ]
        for key in form_props:
            if key in form:
                ordered_form[key] = form[key]

        if "args" not in form:
            form["args"] = {}

        # Required: desc, input, and default
        for arg_name, default in args.items():
            if arg_name in form["args"]:
                ordered_form["args"][arg_name] = form["args"][arg_name]
                ordered_form["args"][arg_name].setdefault("desc", arg_name)
                ordered_form["args"][arg_name].setdefault("input", "text")
                ordered_form["args"][arg_name].setdefault("default", default)
                ordered_form["args"][arg_name].setdefault("status", "")
            else:
                ordered_form["args"][arg_name] = {
                    "desc": arg_name,
                    "input": "text",
                    "default": default,
                    "status": "",
                }

            # Evaluate dynamic values, pattern: "$VAR"
            for key, value in ordered_form["args"][arg_name].items():
                log.debug("func:%s|key:%s|value:%s", func.__name__, key, value)
                if isinstance(value, str) and value.startswith("$"):
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
            f"failed to decode docstring as JSON, then just treat it as title: {func.__name__}"
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

    # Set default layout and theme
    ordered_form.setdefault("layout", "1-column")
    ordered_form.setdefault("theme", "primary")

    if config.VENV_NAME in config.DANGER_VENV_NAMES:
        log.debug(f"{config.VENV_NAME}: need confirm when submit the form")
        ordered_form["popup"] = "prompt"
        ordered_form["theme"] = "danger"

    # log.debug(json.dumps(form))
    # log.debug(str(ordered_form))
    return ordered_form


class File(object):
    """Represents a file uploaded via a form.

    * ``filename``
    * ``body``
    * ``content_type``
    """

    filename: str
    body: bytes
    content_type: str

    def __init__(self, filename: str, body: bytes, content_type: str = "text/plain"):
        self.filename = filename
        self.body = body
        self.content_type = content_type

    def __repr__(self):
        return f"File(filename={self.filename}, body_len={len(self.body)}), content_type={self.content_type}"


class Editor(object):
    """Represents an editor uploaded via a form.

    * ``body``
    """

    body: str

    def __init__(self, body: str = "{}"):
        self.body = body

    def __repr__(self):
        return f"Editor(body={self.body})"
