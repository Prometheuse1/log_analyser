import json
import os
import requests
from dotenv import load_dotenv

CACHE = 'storage/geo_cache.json'

load_dotenv()

def _load():
    try:
        with open(CACHE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def _save(cache):
    with open(CACHE, 'w') as f:
        json.dump(cache, f, indent=2)


def locate(ips):
    cache = _load()
    todo = [ip for ip in ips if ip not in cache]
    print(f'{len(cache)} cached, {len(todo)} to look up')
    try:
        for i, ip in enumerate(todo, 1):
            r = requests.get(f'https://ipinfo.io/{ip}/json',
                             params={'token': os.getenv('IPINFO_TOKEN')}, timeout=5)
            if r.status_code == 429:
                print('Rate limited, rerun later.')
                break
            cache[ip] = r.json().get('country', '??') if r.status_code == 200 else '??'
            print(f'[{i}/{len(todo)}] {ip} -> {cache[ip]}', flush=True)
            if i % 50 == 0:
                _save(cache)
    except (requests.RequestException, KeyboardInterrupt) as e:
        print('Stopped:', repr(e))
    _save(cache)
    return cache