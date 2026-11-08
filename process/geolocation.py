import logging
import os
import time

import requests

log = logging.getLogger(__name__)

CACHE = 'storage/geo_cache.json'
IPINFO_URL = 'https://ipinfo.io/{ip}/json'
IPAPI_URL = 'http://ip-api.com/batch?fields=query,status,countryCode'


def _load():
    cache = {}
    try:
        with open(CACHE) as f:
            for line in f:
                line = line.strip().rstrip(',')
                if line.count('"') == 4:                  # "ip": "CC"
                    ip, country = line.replace('"', '').split(': ')
                    cache[ip] = country
    except FileNotFoundError:
        pass
    return cache


def _save(cache):
    items = ',\n'.join(f'  "{ip}": "{c}"' for ip, c in sorted(cache.items()))
    with open(CACHE, 'w') as f:
        f.write('{\n' + items + '\n}\n' if items else '{}\n')


def _ipinfo(todo, cache, token):
    """ipinfo.io, one request per IP (needs IPINFO_TOKEN)."""
    for i, ip in enumerate(todo, 1):
        r = requests.get(IPINFO_URL.format(ip=ip), params={'token': token}, timeout=5)
        if r.status_code in (401, 403):
            log.error('ipinfo rejected the token (HTTP %s)', r.status_code)
            print('ipinfo rejected the token, check IPINFO_TOKEN.')
            return
        if r.status_code == 429:
            log.error('ipinfo rate limit reached, lookups stopped')
            print('Rate limited, rerun later.')
            return
        if r.status_code != 200:
            log.warning('ipinfo HTTP %s for %s, skipped', r.status_code, ip)
            continue
        cache[ip] = r.json().get('country', '??')
        print(f'[{i}/{len(todo)}] {ip} -> {cache[ip]}', flush=True)
        if i % 50 == 0:
            _save(cache)


def _ipapi(todo, cache):
    """ip-api.com batch, 100 IPs per request, no token."""
    for i in range(0, len(todo), 100):
        batch = todo[i:i + 100]
        for _ in range(2):
            r = requests.post(IPAPI_URL, json=batch, timeout=15)
            if r.status_code != 429:
                break
            wait = int(r.headers.get('X-Ttl', 60)) + 1
            log.warning('Rate limited by ip-api, waiting %ss', wait)
            print(f'Rate limited, waiting {wait}s...', flush=True)
            time.sleep(wait)
        else:
            log.error('Still rate limited after retry, lookups stopped')
            print('Still rate limited, rerun later.')
            return
        if r.status_code != 200:
            log.error('ip-api returned HTTP %s: %s', r.status_code, r.text[:200])
            print('HTTP', r.status_code, '- stopping')
            return
        for item in r.json():
            ok = item.get('status') == 'success'
            if not ok:
                log.warning('Lookup failed: %s', item)
            cache[item['query']] = item['countryCode'] if ok else '??'
        _save(cache)
        print(f'{min(i + 100, len(todo))}/{len(todo)} looked up', flush=True)
        time.sleep(4.5)


def locate(ips):
    """Map each IP to an ISO country code, cached in storage/geo_cache.json.
    Uses ipinfo.io if IPINFO_TOKEN is set (env or .env), else ip-api.com."""
    token = os.getenv('IPINFO_TOKEN')
    cache = _load()
    todo = [ip for ip in ips if ip not in cache]
    print(f'{len(cache)} cached, {len(todo)} to look up '
          f'({"ipinfo.io" if token else "ip-api.com"})', flush=True)
    try:
        if token:
            _ipinfo(todo, cache, token)
        else:
            _ipapi(todo, cache)
    except requests.RequestException:
        log.exception('Network error during geolocation')
        print('Network error, see logs/errors.log')
    except KeyboardInterrupt:
        log.warning('Geolocation interrupted by user')
        print('Stopped')
    _save(cache)
    return cache


if __name__ == '__main__':
    print(locate(['8.8.8.8']))