import os
import re
import inspect
import collections
import types
from core.logger import log


def get_forms_by_module(module):
    forms = collections.OrderedDict()
    # funcs = inspect.getmembers(module, inspect.isfunction)
    funcs = get_ordered_funcs_by_module(module)
    for func in funcs:
        if hasattr(func[1], "__html_form__"):
            forms[func[0]] = getattr(func[1], "__html_form__")
    return forms


def get_ordered_funcs_by_module(module):
    func_dict = {}
    for func in inspect.getmembers(module, inspect.isfunction):
        func_dict[func[0]] = func[1]
    ordered_funcs = []
    func_pattern = re.compile(r"def *([\w]+)\(")
    # log.debug("filepath: " + module.__file__)
    with open(os.path.splitext(module.__file__)[0] + ".py", "r") as file:
        func_names = func_pattern.findall(file.read())
        for func_name in func_names:
            # 剔除func_pattern匹配到的被注释掉的函数
            if func_name in func_dict:
                ordered_funcs.append((func_name, func_dict[func_name]))
    # log.debug("ordered_funcs" + str(ordered_funcs))
    return ordered_funcs


def get_func_parameters(func: callable) -> list[inspect.Parameter]:
    sig = inspect.signature(func)
    return sig.parameters.values()


def get_func_form(func: callable) -> collections.OrderedDict[str, any]:
    return getattr(func, "__html_form__")


def is_list_argument(func: callable, arg_name: str) -> bool:
    form = get_func_form(func)
    is_checkbox = form["args"][arg_name]["input"] == "checkbox"
    is_multiple = "multiple" in form["args"][arg_name]
    return is_checkbox or is_multiple


def is_file_argument(func: callable, arg_name: str) -> bool:
    form = get_func_form(func)
    return form["args"][arg_name]["input"] == "file"


def get_funcs_by_module(module: types.ModuleType) -> dict[str, callable]:
    funcs: dict[str, callable] = {}
    for func in dir(module):
        func = getattr(module, func)
        if callable(func) and hasattr(func, "__html_form__"):
            funcs[func.__name__] = func
    return funcs
