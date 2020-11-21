# @brief    a logger factory to produce colored or normal logger.
# @version  1.0
# @depend   
# @author   wenchyzhu(wenchyzhu@gmail.com)
# @created  2018-05-18

import time
import copy
import logging, logging.handlers
import os, sys

LOG_FORMAT = "%(threadName)s|%(asctime)s|%(filename)s:%(lineno)d|%(levelname)s|%(funcName)s|%(message)s"
class LoggerFactory:
    def __init__(self, name = "app", path = "logs"):
        self.__name = name
        self.__path = path

    def get_normal_logger(self):
        logger = logging.getLogger(self.__name)
        logger.setLevel(logging.DEBUG)
        # console_handler = logging.StreamHandler(sys.stdout)
        # normal_formatter = logging.Formatter(LOG_FORMAT)
        # console_handler.setFormatter(normal_formatter)
        # logger.addHandler(console_handler)
        self.__rotate_logfile(logger)
        return logger

    def get_colored_logger(self):
        logging.setLoggerClass(self.ColoredLogger)
        logger = logging.getLogger(self.__name)
        self.__rotate_logfile(logger)
        return logger

    def __rotate_logfile(self, logger):
        path = self.__path
        if path:
            if not os.path.exists(path):
                os.makedirs(path)
            logfile = path + "/" + self.__name
            # generate one logfile per day, each logfile exists for 10 days.
            logfile_handler = logging.handlers.TimedRotatingFileHandler(logfile, when = 'D', interval = 1, backupCount = 10)
            # NOTES: "%Y%m%d%H%M%S.log"
            logfile_handler.suffix = "%Y%m%d.log"
            logfile_formatter = logging.Formatter(LOG_FORMAT)
            logfile_handler.setFormatter(logfile_formatter)
            logger.addHandler(logfile_handler)

    class ColoredLogger(logging.Logger):
        def __init__(self, name):
            logging.Logger.__init__(self, name, logging.DEBUG)
            # For CGI output, need logging.StreamHandler(sys.stdout)
            console_handler = logging.StreamHandler(sys.stdout)
            color_formatter = self.ColoredFormatter(LOG_FORMAT)
            console_handler.setFormatter(color_formatter)
            self.addHandler(console_handler)

        class ColoredFormatter(logging.Formatter):
            BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)
            # The background is set with 40 plus the number of the color, and the foreground with 30
            # These are the sequences need to get colored ouput
            COLOR_SEQ = "\033[1;%dm"
            RESET_SEQ = "\033[0m"

            def __init__(self, msg):
                logging.Formatter.__init__(self, msg)
                self.COLORS = {
                    'DEBUG': self.BLUE,
                    'INFO': self.WHITE,
                    'WARNING': self.YELLOW,
                    'ERROR': self.RED,
                    'CRITICAL': self.MAGENTA
                }

            def format(self, record):
                # Avoid modifying the original record object, or it would be passed further to other handlers or propagated to other loggers.
                color_record = copy.deepcopy(record)
                if record.levelname in self.COLORS:
                   color_record.levelname = self.COLOR_SEQ % (30 + self.COLORS[record.levelname]) +record.levelname + self.RESET_SEQ
                   # color_record.msg = COLOR_SEQ % (30 + COLORS[record.levelname]) + record.msg + RESET_SEQ
                return logging.Formatter.format(self, color_record)

logger = LoggerFactory(name = "app", path = "logs").get_normal_logger()