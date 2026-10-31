import re


ROW = re.compile(r'^(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s+\S+\s+\S+?:\s(.*)$')
FAILED = re.compile(r'Failed password for (?:invalid user )?(\S*) from (\S+) port \d+')
REPEAT = re.compile(r'message repeated (\d+) times')

def extract_from_row(line):
    row = ROW.match(line)
    f = FAILED.search(line)
    if not row or not f:
        return None
    r = REPEAT.search(line)
    return {'month': row.group(1), 'day': int(row.group(2)),
            'hour': int(row.group(3)[:2]), 'user': f.group(1) or '(empty)',
            'ip': f.group(2), 'count': int(r.group(1)) if r else 1}