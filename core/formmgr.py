import os
from pathlib import Path
from . import util
from .logger import log


class Package(object):
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
    modifier_module_names = [
        os.path.splitext(file_name)[0]
        for file_name in os.listdir(pkg_path)
        if file_name.endswith(("_modifier.py", "_editor.py"))
    ]
    pkg_name = pkg_path.replace("/", ".")
    package = Package(pkg_name)
    for module_name in modifier_module_names:
        log.debug("add modifier module: " + module_name)
        mod = __import__(pkg_name, fromlist=[module_name])
        imported_module = getattr(mod, module_name)
        module_name = imported_module.__name__
        funcs = util.get_func_by_module(imported_module)
        package.modules.append(imported_module)
        package.indexes[module_name] = (imported_module, funcs)
    # sort by priority
    package.modules = sorted(
        package.modules, key=lambda module: module.__priority__, reverse=True
    )
    # insert to all
    global ALL_PACKAGES
    ALL_PACKAGES[pkg_name] = package
    log.debug(f"parsed package: {package}")


def parse_controller_forms():
    base_dir = "controller"
    # Iterate over all entries in the base directory
    for entry in os.listdir(base_dir):
        full_path = os.path.join(base_dir, entry)
        if os.path.isdir(full_path) and entry != "__pycache__":
            parse_package_forms(full_path)

    global ALL_PACKAGES
    global PACKAGE_NAMES
    for fullname in ALL_PACKAGES.keys():
        name = fullname.rsplit(".", 1)[1]
        PACKAGE_NAMES.append(name)
    PACKAGE_NAMES.sort()
