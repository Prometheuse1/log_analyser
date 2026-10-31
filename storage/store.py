import csv


def save_counts(ip_counts, path='storage/failed_by_ip.csv'):
    with open(path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['ip', 'count'])
        w.writerows(sorted(ip_counts.items(), key=lambda x: x[1], reverse=True))
