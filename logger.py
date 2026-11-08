import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

LOG_FILE = Path('logs') / 'errors.log'


def setup():
    """Send warnings/errors (with tracebacks) to logs/errors.log, incl. uncaught crashes."""
    LOG_FILE.parent.mkdir(exist_ok=True)
    root = logging.getLogger()
    if root.handlers:
        return
    root.setLevel(logging.WARNING)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1_000_000, backupCount=3,
                                  encoding='utf-8', delay=True)
    handler.setFormatter(logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s:%(lineno)d | %(message)s'))
    root.addHandler(handler)

    def _hook(exc_type, exc, tb):
        if not issubclass(exc_type, KeyboardInterrupt):
            logging.getLogger('uncaught').critical(
                'Uncaught exception', exc_info=(exc_type, exc, tb))
        sys.__excepthook__(exc_type, exc, tb)    # still print the traceback

    sys.excepthook = _hook
