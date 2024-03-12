"""
A multi-process safe logger.
"""

import logging
import logging.handlers
import os
import sys

LOG_FORMAT = "%(asctime)s.%(msecs)03d|%(levelname)s|%(filename)s:%(lineno)d|%(funcName)s|%(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class MultiProcessFileRotateLogger(logging.Logger):
    def __init__(self, dir="logs", name="portal.log"):
        self.__name = name
        self.__dir = dir
        if not os.path.exists(self.__dir):
            os.makedirs(self.__dir)
        self.__pid = os.getpid()  # process id

        s = super(MultiProcessFileRotateLogger, self)
        s.__init__(name)
        handler = MultiProcessFileRotateLogger.get_handler(
            self.__dir, self.__name, self.__pid
        )
        if hasattr(self, "__handler") and self.__handler:
            s.removeHandler(self.__handler)
        s.addHandler(handler)
        self.__handler = handler

    @staticmethod
    def get_handler(dir, name, pid):
        filename = os.path.join(dir, name + "." + str(pid))
        formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=DATE_FORMAT)
        # handler = logging.StreamHandler()
        # generate one logfile per day, each logfile exists for 10 days.
        # print log lines to separated files for each process
        handler = logging.handlers.TimedRotatingFileHandler(filename, "D", 1, 10)
        handler.setFormatter(formatter)
        return handler

    def handle(self, record):
        if self.__pid != os.getpid():
            self.__init__(self.__dir, self.__name)
        super(MultiProcessFileRotateLogger, self).handle(record)

    @staticmethod
    def wrap_msg(ctx, msg):
        return "{}|{}".format(ctx, msg)

    @staticmethod
    def _gen_findCaller(depth):
        def findCaller(stack_info=False, stacklevel=1):
            f = sys._getframe(depth)
            # On some versions of IronPython, currentframe() returns None if
            # IronPython isn't run with -X:Frames.
            if f is not None:
                f = f.f_back
            rv = "(unknown file)", 0, "(unknown function)", None
            while hasattr(f, "f_code"):
                co = f.f_code
                filename = os.path.normcase(co.co_filename)
                if filename == logging._srcfile:
                    f = f.f_back
                    continue
                rv = (co.co_filename, f.f_lineno, co.co_name)
                break
            return rv

        return findCaller

    def _wrap_log(self, fn):
        save_find_caller = self.findCaller
        self.findCaller = self._gen_findCaller(5)
        try:
            fn()
        except:
            raise
        finally:
            self.findCaller = save_find_caller

    def debugCtx(self, ctx, msg, *args, **kwargs):
        self.debug(self.wrap_msg(ctx, msg), *args, stacklevel=2, **kwargs)

    def infoCtx(self, ctx, msg, *args, **kwargs):
        self.info(self.wrap_msg(ctx, msg), *args, stacklevel=2, **kwargs)

    def warnCtx(self, ctx, msg, *args, **kwargs):
        self._wrap_log(lambda: self.warn(self.wrap_msg(ctx, msg), *args, **kwargs))

    def errorCtx(self, ctx, msg, *args, **kwargs):
        self._wrap_log(lambda: self.error(self.wrap_msg(ctx, msg), *args, **kwargs))

    def criticalCtx(self, ctx, msg, *args, **kwargs):
        self._wrap_log(lambda: self.critical(self.wrap_msg(ctx, msg), *args, **kwargs))


log = MultiProcessFileRotateLogger(dir="logs", name="app.log")
log.propagate = False
log.setLevel(logging.DEBUG)
