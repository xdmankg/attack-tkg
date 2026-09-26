import sys
from pathlib import Path
import json, hashlib, zipfile
from datetime import datetime
from zoneinfo import ZoneInfo
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.ticker import FixedLocator, FixedFormatter, NullLocator
ROOT = Path(sys.argv[1]).resolve()
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
SRC = ROOT / 'source'
df = pd.read_csv(SRC / 'mc_model_comparison.csv')
df = df[df.scope.eq('B0_REFERENCE') & df.density_multiplier.eq(1)].copy()
df['scenario_short'] = df.scenario.str[:2]
df['level_short'] = df.level.str[:2]
models = ['R0', 'R1', 'R2']
scenarios = ['S0', 'S1', 'S2']
levels = ['L0', 'L1', 'L2']
minimum = df[[m + '_IC' for m in models]].min(axis=1)
for m in models:
    df['DeltaIC_' + m] = df[m + '_IC'] - minimum
sets = {}
counts = {}
for s in scenarios:
    for l in levels:
        part = df[(df.scenario_short == s) & (df.level_short == l)].sort_values('replicate_id')
        assert len(part) == 5 and set(part.replicate_id) == set(range(5))
        counts[s + '_' + l] = {m: int((part['DeltaIC_' + m] <= 2).sum()) for m in models}
        for _, r in part.iterrows():
            candidate = {m for m in models if r['DeltaIC_' + m] <= 2}
            assert '{' + ','.join(sorted(candidate)) + '}' == r.preferred_model_set
            sets[s, l, int(r.replicate_id)] = candidate
expected = {'S0_L0': {'R0': 0, 'R1': 3, 'R2': 2}, 'S0_L1': {'R0': 0, 'R1': 0, 'R2': 5}, 'S0_L2': {'R0': 0, 'R1': 0, 'R2': 5}, **{'S1_' + l: {'R0': 0, 'R1': 5, 'R2': 0} for l in levels}, 'S2_L0': {'R0': 5, 'R1': 0, 'R2': 0}, 'S2_L1': {'R0': 5, 'R1': 0, 'R2': 0}, 'S2_L2': {'R0': 5, 'R1': 0, 'R2': 5}}
assert counts == expected
cor = pd.read_csv(SRC / 'mc_set_comparison_corrected.csv')
cor = cor[(cor.scope == 'B0_REFERENCE') & (cor.comparison_pair == 'S0_FULL--S2_DROP_TOP5')]
overlap = {}
for l in levels:
    overlap[l] = sum((bool(sets['S0', l, r] & sets['S2', l, r]) for r in range(5)))
    for r in range(5):
        row = cor[(cor.level.str[:2] == l) & (cor.replicate_id == r)].iloc[0]
        assert bool(row.sets_overlap) == bool(sets['S0', l, r] & sets['S2', l, r])
assert overlap == {'L0': 0, 'L1': 0, 'L2': 5}
assert all((sets['S0', 'L0', r] != {'R1', 'R2'} for r in range(5)))
s2 = df[(df.scenario_short == 'S2') & (df.level_short == 'L2')]
diff = s2.R2_IC - s2.R0_IC
assert (s2.DeltaIC_R2 == 0).sum() == 2
initial = {'R0': 128.05042576398375, 'R1': 104.22894377333606, 'R2': 106.03840694337877}
initial_delta = {m: v - min(initial.values()) for m, v in initial.items()}
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 9, 'axes.titlesize': 11, 'axes.labelsize': 9, 'xtick.labelsize': 8, 'ytick.labelsize': 9, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'ps.fonttype': 42, 'axes.linewidth': 0.65})
colors = {'R0': '#6A7B87', 'R1': '#163F66', 'R2': '#109399'}
markers = {'R0': 'o', 'R1': 'o', 'R2': 'D'}
fig = plt.figure(figsize=(12.5, 4.8), facecolor='white')
gs = fig.add_gridspec(1, 4, width_ratios=[1, 1, 1, 0.61], left=0.092, right=0.995, bottom=0.245, top=0.835, wspace=0.18)
axes = [fig.add_subplot(gs[0, i]) for i in range(3)]
rep_offsets = np.linspace(-0.2, 0.2, 5)
marker_counts = {}
for ai, (ax, s) in enumerate(zip(axes, scenarios)):
    ax.set_title(s, fontweight='bold', pad=11)
    ax.set_xscale('symlog', linthresh=2, linscale=1.25, base=10)
    ax.set_xlim(-0.13, 44)
    ax.set_ylim(2.55, -0.8)
    ax.axvspan(0, 2, color='#CAE5E6', alpha=0.8, zorder=0)
    ax.axvline(2, color='#659B9E', ls=(0, (3, 3)), lw=0.7, zorder=1)
    for j, l in enumerate(levels):
        if j < 2:
            ax.axhline(j + 0.52, color='#D3DDE3', lw=0.7, zorder=0)
        part = df[(df.scenario_short == s) & (df.level_short == l)].sort_values('replicate_id')
        for mi, m in enumerate(models):
            yy = j + rep_offsets + (mi - 1) * 0.017
            ax.scatter(part['DeltaIC_' + m], yy, s=23, marker=markers[m], facecolors='white' if m == 'R0' else colors[m], edgecolors=colors[m], linewidths=0.9, zorder=4)
        marker_counts[s + '_' + l] = 15
        label = ' · '.join((f"{m} {counts[s + '_' + l][m]}/5" for m in models if counts[s + '_' + l][m]))
        ax.text(0.985, j + 0.37, label, transform=ax.get_yaxis_transform(), ha='right', va='center', fontsize=8, color='#303B43')
    ax.xaxis.set_major_locator(FixedLocator([0, 1, 2, 5, 10, 20, 40]))
    ax.xaxis.set_major_formatter(FixedFormatter(['0', '1', '2', '5', '10', '20', '40']))
    ax.xaxis.set_minor_locator(NullLocator())
    ax.grid(axis='x', color='#DCE4E9', lw=0.45, zorder=0)
    ax.set_yticks([0, 1, 2])
    ax.set_yticklabels(['L0 · 200/yr', 'L1 · 2,400/yr', 'L2 · 9,600/yr'] if ai == 0 else [])
    ax.tick_params(axis='y', length=0, pad=9)
    for sp in ['top', 'right', 'left']:
        ax.spines[sp].set_visible(False)
    ax.set_xlabel('ΔIC = IC − min(IC)', labelpad=7)
a = axes[0]
orange = '#C86B16'
a.text(0.5, -0.67, 'Initial single run: {R1, R2}', transform=a.get_yaxis_transform(), ha='center', va='center', color=orange, fontsize=7.6)
a.scatter([0, initial_delta['R2']], [-0.43, -0.43], marker='*', s=68, color=orange, zorder=6, edgecolors='white', linewidths=0.4)
a.text(0.1, -0.43, '0', color=orange, fontsize=7, va='center')
a.annotate('1.809', (initial_delta['R2'], -0.43), xytext=(6, 0), textcoords='offset points', color=orange, fontsize=7, va='center')
summary = fig.add_subplot(gs[0, 3])
summary.set_ylim(2.55, -0.8)
summary.set_xlim(0, 1)
summary.axis('off')
summary.set_title('S0 vs S2\ncandidate sets', fontweight='bold', fontsize=10, pad=6)
for j, l in enumerate(levels):
    summary.text(0.03, j, f'{l}: ' + ('disjoint 5/5' if j < 2 else 'overlap 5/5'), va='center', fontsize=9.2, color=colors['R2'] if j == 2 else '#465865', fontweight='bold' if j == 2 else 'normal')
    if j == 2:
        summary.text(0.03, j + 0.22, '(share R2)', fontsize=8.7, color=colors['R2'], va='center')
    if j < 2:
        summary.axhline(j + 0.52, color='#D3DDE3', lw=0.7)
handles = [Line2D([], [], marker=markers[m], ls='', markerfacecolor='white' if m == 'R0' else colors[m], markeredgecolor=colors[m], markersize=5, label=m) for m in models] + [Patch(facecolor='#CAE5E6', label='IC-based candidate band: ΔIC ≤ 2')]
fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.52, 0.986), ncol=4, frameon=False, fontsize=9, columnspacing=2, handletextpad=0.65)
fig.text(0.54, 0.12, 'Shared x-scale: linear 0–2, logarithmic above 2. Small vertical offsets identify replicate bundles 0–4 (top to bottom).', ha='center', fontsize=8)
fig.text(0.54, 0.07, 'B0 reference scope · five independent replicate bundles per intensity · prefix samples shared across L0 → L1 → L2.', ha='center', fontsize=8)
fig.text(0.54, 0.024, 'Agreement across replicates within an intensity does not establish convergence.', ha='center', fontsize=8.4, fontweight='bold')
stamp = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d-%H%M')
name = 'figure_10'
for ext in ['png', 'svg', 'pdf']:
    fig.savefig(OUT / (name + '.' + ext), dpi=600, facecolor='white', metadata={'Creator': 'Reproducible matplotlib plot from frozen V07 outputs'} if ext == 'pdf' else None)
plt.close(fig)
df.to_csv(SRC / 'Figure10_B0_IC_and_DeltaIC.csv', index=False)
pd.DataFrame([dict(scenario=k[:2], level=k[3:], **v) for k, v in counts.items()]).to_csv(SRC / 'Figure10_inclusion_counts.csv', index=False)
validation = {'model_rows': len(df), 'plotted_replicate_markers': 135, 'markers_per_scenario_intensity': marker_counts, 'candidate_sets_verified': 45, 'counts': counts, 'overlap_counts': overlap, 'initial_set_reproduced_by_L0': 0, 'initial_IC': initial, 'initial_DeltaIC': initial_delta, 'S2_L2_R2_minus_R0_range': [float(diff.min()), float(diff.max())], 'S2_L2_R2_minimum_replicates': s2.loc[s2.DeltaIC_R2 == 0, 'replicate_id'].tolist(), 'S0_T12_means': {l: float(df[(df.scenario_short == 'S0') & (df.level_short == l)].T12.mean()) for l in levels}, 'source_sha256': {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in SRC.glob('*.csv')}, 'timestamp_KST': datetime.now(ZoneInfo('Asia/Seoul')).isoformat()}
(ROOT / 'validation.json').write_text(json.dumps(validation, indent=2), encoding='utf-8')
