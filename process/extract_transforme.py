import logging
import re

log = logging.getLogger(__name__)

ROW = re.compile(r'^(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s+\S+\s+\S+?:\s(.*)$')
FAILED = re.compile(r'Failed password for (?:invalid user )?(\S*) from (\S+) port \d+')
REPEAT = re.compile(r'message repeated (\d+) times')


def extract_from_row(row):
    """Dict with month, day, hour, user, ip, count for any failed password line."""
    m = ROW.match(row)
    f = FAILED.search(row)
    if not m or not f:
        if 'Failed password' in row:
            log.warning('Unparsed failed-login line: %r', row.strip())
        return None
    r = REPEAT.search(row)
    return {'month': m.group(1), 'day': int(m.group(2)),
            'hour': int(m.group(3)[:2]), 'user': f.group(1) or '(empty)',
            'ip': f.group(2), 'count': int(r.group(1)) if r else 1}