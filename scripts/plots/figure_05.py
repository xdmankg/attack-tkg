import sys
from pathlib import Path
import hashlib
import json
import math
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
ROOT = Path(sys.argv[1]).resolve()
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
STAMP = 'reproduced'
NAME = 'figure_05'
source = ROOT / 'source' / 'rich_document_ranking.csv'
df = pd.read_csv(source)
assert len(df) == 1474 and df.canonical_document_id.is_unique
assert np.array_equal(df.pair_potential, df.n_techniques * (df.n_techniques - 1) // 2)
p = np.sort(df.pair_potential.to_numpy(dtype=float))[::-1]
assert (p > 0).sum() == 588 and p.sum() == 66325
series = [('All core', p, '#153E68', 'o', '-'), ('Pair-generating', p[p > 0], '#D87916', 's', (0, (4, 1.8)))]
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.labelsize': 8, 'xtick.labelsize': 7, 'ytick.labelsize': 7, 'axes.linewidth': 0.65, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'path.simplify': False, 'savefig.facecolor': 'white'})
fig = plt.figure(figsize=(7.2, 3.6), facecolor='white')
ax = fig.add_axes([0.087, 0.15, 0.891, 0.745])
detail = ax.inset_axes([0.445, 0.17, 0.525, 0.625])
handles, labels, checks, rows = ([], [], [], [])
expected = [[67.68, 92.72, 97.47], [46.87, 80.24, 89.85]]
for j, (label, vals, color, marker, style) in enumerate(series):
    n = len(vals)
    x = np.arange(n + 1) / n * 100
    y = np.r_[0.0, np.cumsum(vals) / vals.sum() * 100]
    a = vals[::-1]
    gini = 2 * np.dot(np.arange(1, n + 1), a) / (n * a.sum()) - (n + 1) / n
    line, = ax.plot(x, y, color=color, lw=1.65, ls=style, zorder=3)
    detail.plot(x, y, color=color, lw=1.55, ls=style, zorder=3)
    handles.append(line)
    labels.append(f'{label} (N = {n:,}; Gini = {gini:.4f})')
    for k, (xx, yy) in enumerate(zip(x, y)):
        rows.append({'series': label, 'rank': k, 'N': n, 'document_percent': xx, 'cumulative_pair_potential_percent': yy})
    for i, frac in enumerate([0.01, 0.05, 0.1]):
        k = math.ceil(n * frac)
        assert round(y[k], 2) == expected[j][i]
        checks.append({'series': label, 'top_percent': frac * 100, 'document_count': k, 'actual_document_percent': x[k], 'cumulative_pair_potential_percent': y[k], 'table14_percent': expected[j][i], 'matches_2dp': True})
        for axes in [ax, detail]:
            axes.plot(x[k], y[k], marker=marker, ms=3.8, color=color, mec='white', mew=0.55, zorder=5)
        if frac == 0.05:
            textxy = (5.85, 103) if j == 0 else (6.25, 65)
            detail.annotate(f'Top 5%: {y[k]:.2f}%', xy=(x[k], y[k]), xytext=textxy, fontsize=7, color=color, ha='center', va='center', weight='bold', arrowprops={'arrowstyle': '-', 'color': color, 'lw': 0.65, 'shrinkA': 3, 'shrinkB': 4}, zorder=6)
ax.plot([0, 100], [0, 100], ls=(0, (3, 3)), color='#9B9B9B', lw=0.8, zorder=1)
ax.text(20, 24, 'Uniform reference', fontsize=7, color='#6B6B6B', rotation=23)
ax.add_patch(Rectangle((0, 0), 10, 100, facecolor='#153E68', alpha=0.04, edgecolor='none', zorder=0))
ax.set(xlim=(0, 100), ylim=(0, 104), xlabel='Top-ranked documents by pair potential (%)', ylabel='Cumulative pair potential (%)')
ax.set_xticks(np.arange(0, 101, 20))
ax.set_yticks(np.arange(0, 101, 20))
ax.spines[['top', 'right']].set_visible(False)
ax.tick_params(length=3, width=0.6)
ax.grid(axis='y', color='#E7EAEE', lw=0.45, zorder=0)
detail.set(xlim=(0, 10.3), ylim=(0, 110))
detail.set_xticks([0, 1, 5, 10])
detail.set_yticks([0, 25, 50, 75, 100])
detail.set_title('Top 10% detail', fontsize=7.5, pad=4, loc='left')
detail.tick_params(labelsize=6.5, length=2.5, width=0.5, pad=2)
detail.grid(axis='y', color='#ECEFF2', lw=0.4, zorder=0)
for spine in detail.spines.values():
    spine.set_color('#BAC3CD')
    spine.set_linewidth(0.65)
fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.54, 0.992), ncol=2, frameon=False, fontsize=7.5, columnspacing=1.8, handlelength=2.7)
for ext in ['png', 'svg', 'pdf']:
    fig.savefig(OUT / f'{NAME}.{ext}', dpi=600)
plt.close(fig)
pd.DataFrame(rows).to_csv(OUT / 'full_rank_curves.csv', index=False)
pd.DataFrame(checks).to_csv(OUT / 'table14_validation.csv', index=False)
