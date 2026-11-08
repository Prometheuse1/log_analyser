import logging
import os
import sys

from logger import setup

setup()

# load .env (KEY=VALUE lines) into the environment; real env variables win
env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
if os.path.exists(env_path):
    with open(env_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ.setdefault(key.strip(), value.strip().strip('"\''))

from ingestion import raw
from process.extract_transforme import extract_from_row
from process.geolocation import locate
from serving.report import show_dashboard
from storage import db

log = logging.getLogger('main')


def tally(events, key):
    d = {}
    for e in events:
        k = key(e)
        d[k] = d.get(k, 0) + e['count']
    return d


if __name__ == '__main__':
    print('Reading logs...')
    events = [e for e in map(extract_from_row, raw.toRows('./data')) if e]
    ip_counts = tally(events, lambda e: e['ip'])
    print(f'{sum(ip_counts.values())} failed attempts from {len(ip_counts)} IPs')

    print('Geolocating...')
    geo = locate(ip_counts)

    print('Saving to PostgreSQL...')
    try:
        with db.connect() as conn:
            db.init(conn)
            db.save_events(conn, events)
            db.save_geo(conn, geo)
            stats = (db.country_counts(conn), db.unique_ips(conn), db.day_counts(conn),
                     db.hour_counts(conn), db.user_counts(conn))
    except db.Error:
        log.exception('Database error')
        print('Database error, see logs/errors.log')
        sys.exit(1)

    show_dashboard(*stats)