import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def report(ip_counts, geo, out='serving/failed_by_country.png'):
    by_country = {}
    for ip, n in ip_counts.items():
        c = geo.get(ip, 'unknown')
        by_country[c] = by_country.get(c, 0) + n

    ranked = sorted(by_country.items(), key=lambda x: x[1], reverse=True)

    print(f'{"country":<10}{"failed attempts"}')
    for c, n in ranked:
        print(f'{c:<10}{n}')
    print(f'{"TOTAL":<10}{sum(by_country.values())}')

    top = ranked[:15]
    plt.figure(figsize=(10, 5))
    plt.bar([c for c, _ in top], [n for _, n in top])
    plt.title('Failed SSH logins by country')
    plt.ylabel('attempts')
    plt.tight_layout()
    plt.savefig(out)
    return by_country
