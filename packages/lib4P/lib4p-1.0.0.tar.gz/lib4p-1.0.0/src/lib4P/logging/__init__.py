import argparse
import logging
import sys
import time
from io import StringIO
from logging import *
from traceback import TracebackException


class Formatter(logging.Formatter):
    default_msec_format = "%s.%03d"
    converter = time.gmtime

    def __init__(self):
        fmt = '[%(asctime)s][%(levelname)s][%(name)s]%(scope)s%(message)s'
        defaults = {"scope": ""}
        super().__init__(fmt=fmt, defaults=defaults)

    def format(self, record):
        # Add brackets for the optional 'scope' if present
        if "scope" in record.__dict__ and record.__dict__["scope"] != "":
            record.__dict__["scope"] = "["+record.__dict__["scope"]+"]"
        # Add a space to distinguish message starters with brackets
        if record.__dict__["msg"].startswith("["):
            record.__dict__["msg"] = " "+record.__dict__["msg"]
        # Remove unnecessary line breaks
        if record.__dict__["msg"].endswith("\n"):
            record.__dict__["msg"] = record.__dict__["msg"][:-1]
        # Add tabs for multi-line logs
        record.__dict__["msg"] = record.__dict__["msg"].replace("\n", "\n\t")
        return super().format(record)


def getLogger(name_or_argumentparser=None):
    if isinstance(name_or_argumentparser, argparse.ArgumentParser):
        name_or_argumentparser = name_or_argumentparser.prog
    return logging.getLogger(name_or_argumentparser)


class LogCatcher:
    class LogWriter(StringIO):
        def __init__(self, log_func, **kwargs):
            super().__init__()
            self.log_func = log_func
            self.kwargs = kwargs

        def write(self, x):
            if x != "\n" and x != "":
                self.log_func(x, **self.kwargs)

    def __init__(self, name_or_argumentparser=None, **kwargs):
        self.logger = getLogger(name_or_argumentparser)
        self.kwargs = kwargs

    def __enter__(self):
        self._stdout = sys.stdout
        self._stderr = sys.stderr
        sys.stdout = self._stringio_info = LogCatcher.LogWriter(self.logger.info, **self.kwargs)
        sys.stderr = self._stringio_warning = LogCatcher.LogWriter(self.logger.warning, **self.kwargs)
        self._stringio_error = LogCatcher.LogWriter(self.logger.error, **self.kwargs)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val is not None:
            te = TracebackException(exc_type, exc_val, exc_tb, compact=True)
            full_err_msg = "".join([line for line in te.format()])

            sys.stderr = self._stringio_error

            exit(full_err_msg)

        # Free up some memory
        del self._stringio_info
        del self._stringio_warning
        del self._stringio_error
        # Restore original io
        sys.stdout = self._stdout
        sys.stderr = self._stderr

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = Formatter()
handler.setFormatter(formatter)
logger.setLevel(logging.NOTSET)
logger.addHandler(handler)
