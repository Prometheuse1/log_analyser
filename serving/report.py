import matplotlib.pyplot as plt


def _ranked(d):
    return sorted(d.items(), key=lambda x: x[1], reverse=True)


def _country_donut(ax, by_country, top=8):
    total = sum(by_country.values())
    ranked = _ranked(by_country)
    slices = ranked[:top]
    rest = ranked[top:]
    if rest:
        slices.append((f'autres ({len(rest)})', sum(n for _, n in rest)))
    wedges, _ = ax.pie([n for _, n in slices], startangle=90, counterclock=False,
                       wedgeprops={'width': 0.45, 'edgecolor': 'white'})
    ax.legend(wedges, [f'{c}  {n} ({n / total * 100:.1f}%)' for c, n in slices],
              loc='upper center', bbox_to_anchor=(0.5, 0.02), fontsize=8,
              frameon=False, ncol=2)
    ax.text(0, 0, f'{total}\ntentatives', ha='center', va='center', fontsize=11)
    ax.set_title('Tentatives échouées par pays')


def _success_bars(ax, success_users, top=10):
    ax.set_title('Connexions réussies par utilisateur')
    if not success_users:
        ax.text(0.5, 0.5, 'Aucune connexion réussie', ha='center', va='center',
                transform=ax.transAxes)
        ax.set_axis_off()
        return
    ranked = _ranked(success_users)[:top]
    bars = ax.bar([u for u, _ in ranked], [n for _, n in ranked],
                  color='tab:green', width=0.4)
    ax.bar_label(bars, padding=3)
    ax.margins(x=1.0 if len(ranked) == 1 else 0.05, y=0.12)
    if ranked[0][1] <= 10:                       # whole-number ticks for small counts
        ax.set_yticks(range(ranked[0][1] + 1))
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylabel('connexions réussies')


def _invalid_bars(ax, invalid_users, top=10):
    ranked = _ranked(invalid_users)[:top]
    bars = ax.bar([u for u, _ in ranked], [n for _, n in ranked], color='tab:red')
    ax.bar_label(bars, padding=3, fontsize=8)
    ax.margins(y=0.12)
    ax.tick_params(axis='x', rotation=45)
    ax.set_ylabel('tentatives')
    ax.set_title(f'Tentatives échouées avec invalid user '
                 f'(total {sum(invalid_users.values())})')


def show_dashboard(by_country, success_users, invalid_users,
                   out='serving/report.png'):
    """3 charts in one window; also saved as a single PNG."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 6.5))
    fig.suptitle('Analyse des connexions SSH', fontsize=14)
    _country_donut(axes[0], by_country)
    _invalid_bars(axes[1], invalid_users)
    _success_bars(axes[2], success_users)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(out, dpi=120, bbox_inches='tight')
    plt.show()