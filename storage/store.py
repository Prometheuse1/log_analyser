def _q(s):
    """JSON string literal (escapes quotes, backslashes and control characters)."""
    out = ['"']
    for ch in str(s):
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        elif ord(ch) < 0x20:
            out.append('\\u%04x' % ord(ch))
        else:
            out.append(ch)
    out.append('"')
    return ''.join(out)


def _record(e, geo):
    return ('{"month": %s, "day": %d, "hour": %d, "status": %s, "invalid": %s, '
            '"user": %s, "ip": %s, "country": %s, "count": %d}') % (
        _q(e['month']), e['day'], e['hour'], _q(e['status']),
        'true' if e['invalid'] else 'false', _q(e['user']), _q(e['ip']),
        _q(geo.get(e['ip'], 'unknown')), e['count'])


def save_events(events, geo, path='storage/events.json'):
    """One JSON record per parsed login line: date, status, user, IP, country, count."""
    body = ',\n'.join('  ' + _record(e, geo) for e in events)
    with open(path, 'w', encoding='utf-8') as f:
        f.write('[\n' + body + '\n]\n' if events else '[]\n')
