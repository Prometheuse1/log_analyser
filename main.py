from ingestion import raw
from process.extract_transforme import failed_attempt
from process.geolocation import locate
from serving.report import report
from storage.store import save_counts

if __name__ == '__main__':
    print('Reading logs...')
    rows = raw.toRows('./data')
    print(f'{len(rows)} lines read, parsing...')
    ip_counts = {}
    for line in rows:
        a = failed_attempt(line)
        if a:
            ip, n = a
            ip_counts[ip] = ip_counts.get(ip, 0) + n
    print(f'{sum(ip_counts.values())} failed attempts from {len(ip_counts)} IPs')
    save_counts(ip_counts)
    print('Geolocating...')
    geo = locate(ip_counts)
    print('Building report...')
    report(ip_counts, geo)