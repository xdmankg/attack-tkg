import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import hashlib, json, zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
ROOT = Path(sys.argv[1]).resolve()
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
S = ROOT / 'source'
ic = pd.read_csv(S / 'IC_model_comparison.csv').set_index('method_id')['ic'].reindex(['R0', 'R1', 'R2'])
delta = ic - ic.min()
loto = json.loads((S / 'LOTO_table19.json').read_text())
e02 = pd.read_csv(S / 'E02_T12_null.csv')
e03 = pd.read_csv(S / 'E03_T12_null.csv')
obs = float(e02.T12_observed.iloc[0])
assert np.allclose(e03.T12_obs_replay, obs, atol=1e-12, rtol=0)
arrays = [e02.T12_null.to_numpy(), e03.T12_null_E03.to_numpy()]
summary = []
for label, a, expected_count, expected_median in zip(['E02', 'E03'], arrays, [1, 0], [63.372265424122375, 62.40889567763617]):
    count = int((a <= obs).sum())
    assert len(a) == 200 and np.isfinite(a).all() and (count == expected_count)
    assert abs(np.median(a) - expected_median) < 1e-10
    summary.append(dict(run=label, B=200, min=float(a.min()), median=float(np.median(a)), max=float(a.max()), lower_tail_count=count, pMC=(1 + count) / 201))
assert abs(ic.R1 - ic.R2 - obs) < 1e-10
assert all((lo <= 0 <= hi for lo, hi in zip(loto['ci_low'], loto['ci_high'])))
validation = {'IC': ic.to_dict(), 'delta_IC': delta.to_dict(), 'IC_based_candidate_set': delta[delta <= 2].index.tolist(), 'LOTO': loto, 'observed_T12': obs, 'independent_null_tests': summary, 'pooled': False, 'source_hashes': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(S.glob('*'))}, 'checks': 'PASS: source arrays 200 each; lower-tail counts 1 and 0; medians and observed T12 match frozen summaries; both CIs contain zero.'}
(ROOT / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.labelsize': 9, 'axes.titlesize': 10.5, 'axes.linewidth': 0.7, 'xtick.labelsize': 8.5, 'ytick.labelsize': 9, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'axes.unicode_minus': True})
navy = '#153F68'
teal = '#158D91'
orange = '#DB7D24'
gray = '#667783'
fig = plt.figure(figsize=(11.2, 4.1))
gs = fig.add_gridspec(1, 3, width_ratios=[1, 1.23, 1.95], left=0.048, right=0.992, bottom=0.27, top=0.77, wspace=0.3)
axs = [fig.add_subplot(gs[0, i]) for i in range(3)]
for ax in axs:
    ax.spines[['top', 'right']].set_visible(False)
    ax.tick_params(length=3, width=0.6)
    ax.grid(axis='x', color='#E7EDF0', lw=0.5, zorder=0)
ax = axs[0]
ax.axvspan(0, 2, color=teal, alpha=0.15, zorder=1)
ax.axvline(2, color=teal, lw=0.8, ls=(0, (3, 2)), zorder=2)
ys = np.array([2, 1, 0])
ax.scatter(delta, ys, s=42, color=[gray, navy, navy], zorder=4)
for x, y in zip(delta, ys):
    ax.annotate(f'{x:.3f}', (x, y), xytext=(4, 9), textcoords='offset points', fontsize=8.7, ha='left' if x < 20 else 'right')
ax.set(xlim=(-0.65, 27.2), ylim=(-0.6, 2.65), yticks=ys, yticklabels=['R0', 'R1', 'R2'], xticks=[0, 2, 10, 20], xlabel='ΔIC = IC − min(IC)')
ax.text(0.01, 1.24, 'A  IC-based comparison', transform=ax.transAxes, ha='left', fontweight='bold', fontsize=10.5)
ax.text(0.01, 1.08, 'IC-based candidate band: ΔIC ≤ 2', transform=ax.transAxes, ha='left', color=teal, fontsize=9)
ax.text(0.5, -0.36, 'IC-based candidate set:\n{R1, R2}', transform=ax.transAxes, ha='center', va='top', fontsize=9, linespacing=1.4)
ax = axs[1]
mean = np.array(loto['mean'])
lo = np.array(loto['ci_low'])
hi = np.array(loto['ci_high'])
y = np.array([1, 0])
ax.axvline(0, color=gray, lw=0.9, ls=(0, (3, 2)), zorder=1)
ax.errorbar(mean, y, xerr=[mean - lo, hi - mean], fmt='o', markersize=5.5, color=navy, ecolor=navy, elinewidth=1.35, capsize=4, zorder=4)
for x, y0 in zip(mean, y):
    ax.annotate(f'{x:.3f}'.replace('-', '−'), (x, y0), xytext=(0, 12), textcoords='offset points', ha='center', fontsize=9)
ax.set(xlim=(-0.85, 0.35), ylim=(-0.65, 1.7), yticks=[1, 0], yticklabels=loto['contrasts'], xticks=[-0.8, -0.4, 0, 0.3], xlabel='Mean squared-error difference')
ax.text(0.0, 1.24, 'B  LOTO error differences', transform=ax.transAxes, ha='left', fontweight='bold', fontsize=10.5)
ax.text(0.0, 1.08, 'Initial full-period scaling and\nindividual-error resampling', transform=ax.transAxes, ha='left', fontsize=8.5, linespacing=1.25)
ax.text(0.5, -0.36, 'Both 95% CIs include 0 →\nclear superiority not established', transform=ax.transAxes, ha='center', va='top', fontsize=8.5, linespacing=1.4)
ax = axs[2]
ax.axvspan(-18, obs, color=orange, alpha=0.09, zorder=1)
ax.axvline(obs, color=orange, lw=1.2, zorder=3)
for i, (a, row, color) in enumerate(zip(arrays, [1, 0], [navy, teal])):
    offsets = (np.arange(200) * 0.61803398875 % 1 - 0.5) * 0.3
    ax.scatter(a, row + offsets, s=11, color=color, alpha=0.64, linewidths=0, zorder=3)
    tail = a <= obs
    ax.scatter(a[tail], (row + offsets)[tail], s=26, facecolors='none', edgecolors=orange, lw=1, zorder=5)
    med = float(np.median(a))
    ax.plot([med, med], [row - 0.22, row + 0.22], color='black', lw=1.2, zorder=5)
    ax.text(-12, row + 0.46, f"{['E02', 'E03'][i]} · B = 200", ha='left', fontsize=8.6)
    ax.text(466, row + 0.46, f"pMC = {summary[i]['pMC']:.6f}", ha='right', fontsize=8.7)
    ax.text(-12, row + 0.27, f'Median = {med:.2f}', ha='left', fontsize=8.1, color=color)
    ax.text(466, row + 0.27, f"Lower-tail count: {summary[i]['lower_tail_count']}/200", ha='right', fontsize=8.1, color=color)
ax.set(xlim=(-18, 470), ylim=(-0.45, 1.9), yticks=[], xticks=[0, 100, 200, 300, 400], xlabel='T12* under the pseudo-temporal null')
ax.text(0.0, 1.24, 'C  Pseudo-temporal null tests', transform=ax.transAxes, ha='left', fontweight='bold', fontsize=10.5)
ax.text(0.0, 1.08, 'Observed T12 = −1.809', transform=ax.transAxes, ha='left', fontsize=9, color=orange)
ax.text(0.5, -0.36, 'Lower-tail tests · independent runs · not pooled', transform=ax.transAxes, ha='center', va='top', fontsize=9)
fig.text(0.992, 0.018, 'C: each dot is one saved null statistic; black ticks mark medians.', ha='right', fontsize=7.7, color=gray)
stamp = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d-%H%M')
base = 'figure_08'
for ext in ['png', 'svg', 'pdf']:
    fig.savefig(OUT / f'{base}.{ext}', dpi=600, facecolor='white')
plt.close(fig)
