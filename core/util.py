import os
import json
import inspect
import collections
import re
import datetime
import socket
import sys
import subprocess
import time
import hashlib
import fnmatch
import fcntl
import struct
import traceback

import tornado
from google.protobuf.message import Message as ProtoBufMessage
from google.protobuf import text_format
from core.logger import log


def exception_catcher(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            log.error("Caught exception: %s, %s", str(e), traceback.format_exc())

    return wrapper


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
    log.debug("filepath: " + module.__file__)
    with open(os.path.splitext(module.__file__)[0] + ".py", "r") as file:
        func_names = func_pattern.findall(file.read())
        for func_name in func_names:
            # 剔除func_pattern匹配到的被注释掉的函数
            if func_name in func_dict:
                ordered_funcs.append((func_name, func_dict[func_name]))
    log.debug("ordered_funcs" + str(ordered_funcs))
    return ordered_funcs


def excelviewer(table_name, sheet_name):
    def decorator(func):
        func.__excelviewer__ = (table_name, sheet_name)
        return func

    return decorator


def get_func_args(func):
    return inspect.getargspec(func)


def get_module_by_name(module_name):
    imported_module = __import__(name=module_name)
    return imported_module


def get_func_by_module(module):
    methods = {}
    for method in dir(module):
        method = getattr(module, method)
        if callable(method) and hasattr(method, "__html_form__"):
            methods[method.__name__] = method
    return methods


def get_func_by_module_name(module_name):
    imported_module = get_module_by_name(module_name)
    methods = get_func_by_module(imported_module)
    return methods


def is_json(test_str):
    try:
        json.loads(test_str)
    except BaseException:
        return False
    return True


def get_ecode_name(ecode):
    try:
        if ecode == 0:
            return "OK"
        else:
            return "Error: " + str(ecode)
    except KeyError:
        return "Error: ERR_UNKNOWN(%d)" % ecode


def strf2time(timestr, format="%Y-%m-%d %H:%M:%S"):
    return int(datetime.datetime.strptime(timestr, format).strftime("%s"))


def time2strf(timestamp, format="%Y-%m-%d %H:%M:%S"):
    return datetime.datetime.fromtimestamp(timestamp).strftime(format)


# def gen_uid(zone_id, plat_id, luid):
#     return (zone_id * (1 << 48)) | (plat_id << 32) | uin


def get_world(uid):
    huid = get_huid(uid)
    return huid >> 28


def get_zone(uid):
    huid = get_huid(uid)
    return (huid >> 16) & 0xFFF


def get_platid(uid):
    huid = get_huid(uid)
    return (huid >> 10) & 0x3F


def get_luid(uid):
    return uid & 0x00000000FFFFFFFF


def get_huid(uid):
    return uid >> 32


def to_text(item):
    # tornado write() only accepts bytes, str, and dict objects
    if item == None:
        return str(item)
    elif isinstance(item, ProtoBufMessage):
        return text_format.MessageToString(item, as_utf8=True)
    elif isinstance(item, (str, bytes)):
        # Converts an itme to a  tring.
        # If the argument is already a string or None, it is returned unchanged.
        # Otherwise it must be a byte string and is decoded as utf8.
        return tornado.escape.to_unicode(item)
    else:
        return tornado.escape.to_unicode(str(item))


def zoneid(world, zone):
    # world:3.zone:13.function:6.instance:10
    # world: max 7 (2 ** 3 - 1)
    #   1: 微信
    #   2: QQ
    #   7: 测试(包括开发环境和测试环境)
    # zone: max 8191 (2 ** 13 - 1)
    return (world << 13) + zone


def busid2str(bus_id):
    # world:3.zone:13.function:6.instance:10
    busid = socket.ntohl(bus_id)
    world = str(busid >> 29)
    zone = str((busid >> 16) & 0x1FFF)
    function = str((busid & 0xFFFF) >> 10)
    instance = str((busid & 0xFFFF) & 0x3FF)
    return world + "." + zone + "." + function + "." + instance


def html_font(input, color="black"):
    return '<font color="' + color + '"><b>' + input + "</b></font>"


def clean_html(raw_html):
    # re.compile('<.*?>')
    cleanre = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    cleantext = re.sub(cleanre, "", raw_html)
    return cleantext


class ArgComplete:
    def autocomplete(self, parser):
        log.warning("argcomplete not installed")


argcomplete = ArgComplete()


def exec_cmd(cmd, shell=True, need_log=True, with_exception=True, **kwargs):
    """run command, return (status, stdout, stderr)"""
    process = subprocess.Popen(
        cmd,
        shell=shell,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        **kwargs
    )
    stdout, stderr = process.communicate()
    status = process.poll()
    if need_log:
        if not isinstance(cmd, str):
            cmd_str = subprocess.list2cmdline(cmd)
        else:
            cmd_str = cmd
        log_str = "status: %d" % status
        if stdout:
            log_str += "\nstdout:\n%s" % stdout
        if stderr:
            log_str += "\nstderr:\n%s" % stderr
        if status == 0:
            log.info("exec cmd success: %s\n%s" % (cmd_str, log_str))
        else:
            if with_exception:
                raise Exception("exec cmd error: %s|%s" % (cmd_str, log_str))
            else:
                log.error("exec cmd error: %s\n%s" % (cmd_str, log_str))
    return status, stdout, stderr


def system(cmd, desc="", need_log=True, with_exception=True):
    """run shell command, and return status"""
    logstr = cmd
    if desc:
        logstr += "|" + desc
    status = os.system(cmd)
    if status != 0:
        sys.stdout.flush()
        logstr = "error: %s, status: %d" % (logstr, status)
        if with_exception:
            if need_log:
                log.error(logstr)
            raise Exception(logstr)
        else:
            log.warn(logstr)
    else:
        if need_log:
            log.info("success: " + logstr)
    return status


def camel_to_snake(name):
    name = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", name).lower()


def get_root_path():
    _, stdout, _ = exec_cmd("git rev-parse --show-toplevel", need_log=False)
    return stdout.strip()


def git_get_head_commit_id(short=True):
    cmd = "git rev-parse HEAD"
    if short:
        cmd = "git rev-parse --short HEAD"
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    return stdout.strip()


def git_get_head_commit_time():
    cmd = 'git log --oneline --pretty=format:"%cd" --date=iso-local -1'
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    match = pattern.search(stdout.strip())
    if match:
        return match.group()
    return stdout.strip()


def git_get_latest_commits(dirs=["./"], exclusive_dirs=[]):
    root_path = get_root_path()
    dirs_str = " ".join([os.path.join(root_path, dir) for dir in dirs])
    exclusive_dirs_str = " ".join(
        ["':(exclude)%s'" % os.path.join(root_path, dir) for dir in exclusive_dirs]
    )
    cmd = "git log --pretty=oneline --abbrev-commit -10 -- %s %s" % (
        dirs_str,
        exclusive_dirs_str,
    )
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    return stdout.strip()


def git_get_branch_name():
    cmd = "git symbolic-ref --short -q HEAD"
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    return stdout.strip()


def git_clean(dir):
    system("git clean -dfx %s" % dir)


def svn_get_relative_url(path):
    cmd = (
        "svn info "
        + path
        + " | grep -E 'URL:' | awk -F'wedo_client_proj/' '{print $2}'"
    )
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    return stdout.strip()


def svn_get_last_revison(path):
    cmd = (
        "svn info "
        + path
        + " | grep -E '最后修改的版本|Last Changed Rev' | cut -d ':' -f 2 |  tr -d [:space:]"
    )
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    return stdout.strip()


def svn_get_last_time(path):
    cmd = "svn info " + path + " | grep -E '最后修改的时间|Last Changed Date'"
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    pattern = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}")
    match = pattern.search(stdout.strip())
    if match:
        return match.group()
    return stdout.strip()


def get_local_ip():
    cmd = "ifconfig eth0 | grep -w inet | awk '{ print $2}'"
    _, stdout, _ = exec_cmd(cmd, need_log=False)
    if "error" in stdout:
        cmd = "ifconfig eth1 | grep -w inet | awk '{ print $2}'"
        _, stdout, _ = exec_cmd(cmd, need_log=False)
    return stdout.strip()


def get_host_ip(ifname):
    """
    get network card IP address.

    examples:
        get_host_ip("lo") >> "127.0.0.1"
        get_host_ip("eth0") >> "192.168.1.1"
        get_host_ip("eth100") >> ""
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    packed_ip = fcntl.ioctl(
        s.fileno(), 0x8915, struct.pack("256s", ifname[:15])  # SIOCGIFADDR
    )
    try:
        ip = socket.inet_ntoa(packed_ip[20:24])
    except:
        ip = ""
    return ip


def pidof(name):
    cmd = "pidof %s" % name
    _, stdout, _ = exec_cmd(cmd)
    return stdout.strip()


def check_process_running(name):
    try:
        pid = int(subprocess.check_output(["pgrep", "-u", "user00", name]))
    except:
        return False
    else:
        return os.path.exists("/proc/%s" % pid)


def ln(src, dst):
    system("ln -s %s %s" % (src, dst), need_log=False)


def cp(src, dst, overwrite=True):
    if overwrite:
        system("cp -rf %s %s" % (src, dst), need_log=False)
    else:
        system("cp -rn %s %s" % (src, dst), need_log=False)


def mv(src, dst):
    system("mv %s %s" % (src, dst))


def rm(path, force=False):
    flags = "-r"
    if force:
        flags = "-rf"
    system("rm %s %s" % (flags, path))


def rsync(src, dst, compress=False, create_parent_dir=False, ignore_times=False):
    flags = "-avL"
    if compress:
        flags = flags + "z"
    if create_parent_dir:
        flags = flags + "R"
    if ignore_times:
        flags = flags + "I"
    system("rsync %s %s %s" % (flags, src, dst))


def md5str(content=""):
    m = hashlib.md5()
    m.update(content)
    return m.hexdigest()


def md5sum(fpath, need_log=True):
    cmd = "md5sum %s" % fpath
    _, stdout, _ = exec_cmd(cmd, need_log=need_log)
    return stdout.strip().split()[0]


def rm_free_shm():
    system(
        r"""ipcs|awk '{if($6==0) printf "ipcrm shm %d\n",$2}'|sh""",
        desc="rm free shm",
        with_exception=False,
    )
    # system('ipcs')


def mkdir(dir, exist_ok=True):
    if not os.path.exists(dir):
        os.makedirs(dir)
    else:
        if not exist_ok:
            raise ValueError("dir already exists: %s", dir)


def batch(iterable, n=1):
    l = len(iterable)
    for i in range(0, l, n):
        yield iterable[i : min(i + n, l)]


def match_filepath(dirpath, patterns=["*"], relative=False, excluded_paths=[]):
    normal_excluded_paths = map(
        lambda x: os.path.normpath(os.path.join(dirpath, x)), excluded_paths
    )

    def is_excluded(filename):
        for excluded_path in normal_excluded_paths:
            if filename.startswith(excluded_path):
                return True

    filepaths = list()
    for root, _, files in os.walk(dirpath):
        for filename in files:
            filepath = os.path.join(root, filename)
            if is_excluded(os.path.normpath(filepath)):
                continue
            for pattern in patterns:
                pattern = os.path.normpath(pattern)
                if pattern in filepath or fnmatch.fnmatch(filepath, pattern):
                    if relative:
                        filepath = filepath.replace(dirpath, ".")
                    filepaths.append(filepath)
                    break
    return filepaths


def ask_yes_no(question, default="yes"):
    """refer: https://stackoverflow.com/questions/3041986/apt-command-line-interface-like-yes-no-input

    Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")


def main():
    pass


if __name__ == "__main__":
    main()
