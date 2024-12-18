import os
import pkgutil
import importlib
import types
from . import formutil
from .logger import log

DEFAULT_PACKAGE_NAME = "index"
DEFAULT_PACKAGE_DIR = "controller"
_MODULE_NAME_SUFFIXES = ("_modifier", "_editor")


def fullname(name: str) -> str:
    return f"{DEFAULT_PACKAGE_DIR}.{name}"


DEFAULT_PACKAGE_FULLNAME = fullname(DEFAULT_PACKAGE_NAME)


class Package(object):
    modules: list[types.ModuleType]
    indexes: dict[str, tuple[types.ModuleType, dict[str, callable]]]

    def __init__(self, name: str):
        self.name = name
        self.modules = []  # sorted modules
        self.indexes = {}  # module_name -> (module, funcs)

    def __repr__(self):
        out = f"name: {self.name}\n"
        for i, module in enumerate(self.modules):
            out += f"module[{i}]: {module.__name__}\n"
        return out


# package_name -> package
ALL_PACKAGES: dict[str, Package] = {}
PACKAGE_NAMES: list[str] = []


def parse_package_forms(pkg_path: str):
    # Packages are a way of structuring Python's module namespace by
    # using "dotted module names".
    #
    # Convert path to name: A/B/C -> A.B.C
    pkg_fullname = pkg_path.replace("/", ".")
    package = Package(pkg_fullname)
    for info in pkgutil.iter_modules([pkg_path], pkg_fullname + "."):
        if info.name.endswith(_MODULE_NAME_SUFFIXES):
            log.debug(f"add module: {info}")
            module = importlib.import_module(info.name)
            funcs = formutil.get_funcs_by_module(module)
            package.modules.append(module)
            package.indexes[info.name] = (module, funcs)

    # sort by priority
    package.modules = sorted(
        package.modules, key=lambda module: module.__priority__, reverse=True
    )
    # insert to all
    global ALL_PACKAGES
    ALL_PACKAGES[pkg_fullname] = package
    log.debug(f"parsed package: {package}")


def parse_controller_forms():
    # Iterate over all entries in the base directory
    for entry in os.listdir(DEFAULT_PACKAGE_DIR):
        full_path = os.path.join(DEFAULT_PACKAGE_DIR, entry)
        if os.path.isdir(full_path) and entry != "__pycache__":
            parse_package_forms(full_path)

    global ALL_PACKAGES
    global PACKAGE_NAMES
    for fullname in ALL_PACKAGES.keys():
        name = fullname.rsplit(".", 1)[1]
        PACKAGE_NAMES.append(name)
    PACKAGE_NAMES.sort()
