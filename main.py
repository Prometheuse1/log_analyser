from ingestion import raw
from process import extract_transforme 
from process.extract_transforme import failed_attempt
from process.geolocation import locate
from serving.report import report
from storage.store import save_counts


if __name__=='__main__':
    ip_counts = {}
    for line in raw.toRows('./data'):
        a = failed_attempt(line)
        if a:
            ip, n = a
            ip_counts[ip] = ip_counts.get(ip, 0) + n
    save_counts(ip_counts)
    report(ip_counts, locate(ip_counts))