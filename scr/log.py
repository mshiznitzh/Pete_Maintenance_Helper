import logging
import os
#from rich.logging import RichHandler
import sys

class CustomFormatter2(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
   """
    Black = '\x1b[0;30m'
    BlinkBlack = '\x1b[5;30m'
    BlinkBlue = '\x1b[5;34m'
    BlinkCyan = '\x1b[5;36m'
    BlinkGreen = '\x1b[5;32m'
    BlinkLightGray = '\x1b[5;37m'
    BlinkPurple = '\x1b[5;35m'
    BlinkRed = '\x1b[5;31m'
    BlinkYellow = '\x1b[5;33m'
    Blue = '\x1b[0;34m'
    Brown = '\x1b[0;33m'
    Cyan = '\x1b[0;36m'
    DarkGray = '\x1b[1;30m'
    Green = '\x1b[0;32m'
    LightBlue = '\x1b[1;34m'
    LightCyan = '\x1b[1;36m'
    LightGray = '\x1b[0;37m'
    LightGreen = '\x1b[1;32m'
    LightPurple = '\x1b[1;35m'
    LightRed = '\x1b[1;31m'
    NoColor = ''
    Normal = '\x1b[0m'
    Purple = '\x1b[0;35m'
    Red = '\x1b[0;31m'
    White = '\x1b[1;37m'
    Yellow = '\x1b[1;33m'
    reset = "\x1b[0m"

    def format(self, record):
        FORMATS = {
            logging.DEBUG: self.LightGray + self._fmt + self.reset,
            logging.INFO: self.Normal + self._fmt + self.reset,
            logging.WARNING: self.Yellow + self._fmt + self.reset,
            logging.ERROR: self.LightRed + self._fmt + self.reset,
            logging.CRITICAL: self.Cyan + self._fmt + self.reset
        }


        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        log_fmt = FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)
        #return formatter.format(record)
        #return super(CustomFormatter2, self).format(record)

class CustomFormatter(logging.Formatter):
    """ Custom Formatter does these 2 things:
    1. Overrides 'funcName' with the value of 'func_name_override', if it exists.
    2. Overrides 'filename' with the value of 'file_name_override', if it exists.
    """


    def format(self, record):
        if hasattr(record, 'func_name_override'):
            record.funcName = record.func_name_override
        if hasattr(record, 'file_name_override'):
            record.filename = record.file_name_override
        return super(CustomFormatter, self).format(record)


def get_logger(log_file_name, log_sub_dir=""):
    """ Creates a Log File and returns Logger object """
    windows_log_dir = 'c:\\logs_dir\\'
    linux_log_dir = './logs_dir/'

    # Build Log file directory, based on the OS and supplied input
    log_dir = windows_log_dir if os.name == 'nt' else linux_log_dir
    log_dir = os.path.join(log_dir, log_sub_dir)

    # Create Log file directory if not exists
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Build Log File Full Path
    logPath = log_file_name if os.path.exists(log_file_name) else os.path.join(log_dir, (str(log_file_name) + '.log'))

    # Create logger object and set the format for logging and other attributes
    logger = logging.Logger(log_file_name)
    logger.setLevel(logging.DEBUG)
#    handler = RichHandler(rich_tracebacks=True) #logging.FileHandler(logPath, 'w+')
    handler = logging.StreamHandler(sys.__stdout__)
    """ Set the formatter of 'CustomFormatter' type as we need to log base function name and base file name """
    handler.setFormatter(CustomFormatter2('%(asctime)5s - %(levelname)-5s - %(filename)s - %(funcName)s - %(message)s (%(filename)s:%(lineno)d)'))
    logger.addHandler(handler)

    # Return logger object
    return logger
