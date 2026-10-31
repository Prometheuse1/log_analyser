from ingestion import raw
from process.extract_transforme import extract_from_row
from process.geolocation import locate
from serving.report import show_dashboard
from storage.store import save_counts


def tally(events, key):
    d = {}
    for e in events:
        k = key(e)
        d[k] = d.get(k, 0) + e['count']
    return d


if __name__ == '__main__':
    print('Reading logs...')
    rows = raw.toRows('./data')
    events = [e for e in map(extract_from_row, rows) if e]

    ip_counts = tally(events, lambda e: e['ip'])
    day_counts = tally(events, lambda e: (e['month'], e['day']))
    hour_counts = tally(events, lambda e: e['hour'])
    user_counts = tally(events, lambda e: e['user'])
    print(f'{sum(ip_counts.values())} failed attempts from {len(ip_counts)} IPs')

    save_counts(ip_counts)
    print('Geolocating...')
    geo = locate(ip_counts)
    show_dashboard(ip_counts, geo, day_counts, hour_counts, user_counts)