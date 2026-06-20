import logging
import sys
from datetime import datetime


def _emit(level, message):
    line = f"[{level}] {datetime.utcnow()} {message}"
    print(line, flush=True)
    sys.stdout.flush()


def log_info(message):
    _emit("INFO", message)


def log_warning(message):
    _emit("WARNING", message)


def log_error(message):
    _emit("ERROR", message)
