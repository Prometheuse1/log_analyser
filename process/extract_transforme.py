import re


ROW = re.compile(r'^(\w{3})\s+(\d{1,2})\s+(\d{2}:\d{2}:\d{2})\s+\S+\s+\S+?:\s(.*)$')
KEEP = re.compile(r'(?=.*invalid user)(?=.*failed password)', re.I)
FAILED = re.compile(r'Failed password for (?:invalid user )?(\S*) from (\S+) port \d+')
REPEAT = re.compile(r'message repeated (\d+) times')
 
 
def extract_from_row(row):
    m = ROW.match(row)
    if not m or not KEEP.search(m.group(4)):
        return None
    return {'month': m.group(1), 'day': int(m.group(2)),
            'time': m.group(3), 'message': m.group(4)}
 
 
def failed_attempt(line):
    m = FAILED.search(line)
    if not m:
        return None
    r = REPEAT.search(line)
    return m.group(2), int(r.group(1)) if r else 1
