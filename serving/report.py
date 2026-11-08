import matplotlib.pyplot as plt

MONTHS = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
          'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


def _ranked(d):
    return sorted(d.items(), key=lambda x: x[1], reverse=True)


def _country_donut(ax, by_country, top=8):
    total = sum(by_country.values())
    ranked = _ranked(by_country)
    slices = ranked[:top]
    rest = ranked[top:]
    if rest:
        slices.append((f'other ({len(rest)})', sum(n for _, n in rest)))
    wedges, _ = ax.pie([n for _, n in slices], startangle=90, counterclock=False,
                       wedgeprops={'width': 0.45, 'edgecolor': 'white'})
    ax.legend(wedges, [f'{c}  {n} ({n / total * 100:.1f}%)' for c, n in slices],
              loc='center left', bbox_to_anchor=(0.95, 0.5), fontsize=8, frameon=False)
    ax.text(0, 0, f'{total}\nattempts', ha='center', va='center', fontsize=11)
    ax.set_title('By country')


def _day_line(ax, day_counts):
    keys = sorted(day_counts, key=lambda k: (MONTHS.index(k[0]), k[1]))
    values = [day_counts[k] for k in keys]
    x = range(len(keys))
    ax.plot(x, values, marker='o', linewidth=1.5)
    ax.fill_between(x, values, alpha=0.15)
    step = max(1, len(keys) // 10)
    ax.set_xticks(range(0, len(keys), step))
    ax.set_xticklabels([f'{m} {d:02d}' for m, d in keys][::step],
                       rotation=45, ha='right', fontsize=8)
    ax.set_ylabel('attempts')
    ax.set_title('Per day')
    ax.grid(alpha=0.3)


def _hour_bars(ax, hour_counts):
    hours = list(range(24))
    ax.bar(hours, [hour_counts.get(h, 0) for h in hours])
    ax.set_xticks(hours)
    ax.set_xticklabels([f'{h:02d}' for h in hours], fontsize=8)
    ax.set_xlabel('hour of day')
    ax.set_ylabel('attempts')
    ax.set_title('By hour of day')


def _user_barh(ax, user_counts, top=10):
    ranked = _ranked(user_counts)[:top][::-1]
    bars = ax.barh([u for u, _ in ranked], [n for _, n in ranked])
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.margins(x=0.12)
    ax.set_xlabel('attempts')
    ax.set_title('Most targeted usernames')


def show_dashboard(by_country, n_ips, day_counts, hour_counts, user_counts,
                   out='serving/report.png'):
    """4 charts in one window; also saved as a single PNG."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 9))
    fig.suptitle(f'Failed SSH logins: {sum(by_country.values())} attempts '
                 f'from {n_ips} IPs', fontsize=14)
    _country_donut(axes[0][0], by_country)
    _day_line(axes[0][1], day_counts)
    _hour_bars(axes[1][0], hour_counts)
    _user_barh(axes[1][1], user_counts)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=120, bbox_inches='tight')
    plt.show()