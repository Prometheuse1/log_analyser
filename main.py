import os

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
from storage.store import save_events


def tally(events, key):
    d = {}
    for e in events:
        k = key(e)
        d[k] = d.get(k, 0) + e['count']
    return d


if __name__ == '__main__':
    print('Lecture des logs...')
    events = [e for e in map(extract_from_row, raw.toRows('./data')) if e]
    failed = [e for e in events if e['status'] == 'failed']
    success = [e for e in events if e['status'] == 'success']

    ip_counts = tally(failed, lambda e: e['ip'])
    success_users = tally(success, lambda e: e['user'])
    invalid_users = tally([e for e in failed if e['invalid']], lambda e: e['user'])
    print(f'{sum(ip_counts.values())} tentatives échouées ({len(ip_counts)} IP), '
          f'{sum(success_users.values())} connexion(s) réussie(s), '
          f'{sum(invalid_users.values())} avec invalid user')

    print('Géolocalisation...')
    geo = locate(ip_counts)
    save_events(events, geo)
    by_country = {}
    for ip, n in ip_counts.items():
        c = geo.get(ip, 'unknown')
        by_country[c] = by_country.get(c, 0) + n

    show_dashboard(by_country, success_users, invalid_users)