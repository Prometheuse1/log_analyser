import logging
import re

log = logging.getLogger(__name__)

ROW = re.compile(r'^(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s+\S+\s+\S+?:\s(.*)$')
FAILED = re.compile(r'Failed password for (invalid user )?(\S*) from (\S+) port \d+')
ACCEPTED = re.compile(r'Accepted \S+ for (\S+) from (\S+) port \d+')
REPEAT = re.compile(r'message repeated (\d+) times')


def extract_from_row(row):
    """Dict for a failed ('failed') or successful ('success') SSH login, else None."""
    m = ROW.match(row)
    f = FAILED.search(row)
    a = None if f else ACCEPTED.search(row)
    if not m or not (f or a):
        if 'Failed password' in row or 'Accepted password' in row \
                or 'Accepted publickey' in row:
            log.warning('Unparsed login line: %r', row.strip())
        return None
    r = REPEAT.search(row)
    base = {'month': m.group(1), 'day': int(m.group(2)), 'hour': int(m.group(3)[:2]),
            'count': int(r.group(1)) if r else 1}
    if f:
        return {**base, 'status': 'failed', 'invalid': bool(f.group(1)),
                'user': f.group(2) or '(vide)', 'ip': f.group(3)}
    return {**base, 'status': 'success', 'invalid': False,
            'user': a.group(1), 'ip': a.group(2)}