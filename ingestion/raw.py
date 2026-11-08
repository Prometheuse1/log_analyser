import gzip
import logging
import os

log = logging.getLogger(__name__)


def toRows(path):
    """Read every log file in `path` (plain or .gz) as a list of lines."""
    rows = []
    for file in sorted(os.listdir(path)):
        file_path = os.path.join(path, file)
        opener = gzip.open if file.endswith('.gz') else open
        try:
            with opener(file_path, 'rt', encoding='utf-8', errors='replace') as f:
                rows.extend(f.readlines())
        except (OSError, EOFError):
            log.exception('Cannot read %s', file_path)
    return rows


if __name__ == '__main__':
    print(toRows('./data')[:10])