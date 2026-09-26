import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib, zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
ROOT = Path(sys.argv[1]).resolve()
S = ROOT / 'source'
O = ROOT / 'output'
O.mkdir(exist_ok=True)
d = pd.read_csv(S / 'Figure09_IC_and_DeltaIC.csv')
old = json.loads((S / 'previous_memberships.json').read_text())
for panel in ['left', 'right']:
    sub = d[d.panel == panel]
    ic = sub[['R0_IC', 'R1_IC', 'R2_IC']].to_numpy()
    delta = ic - ic.min(axis=1, keepdims=True)
    assert np.allclose(delta, sub[['R0_delta', 'R1_delta', 'R2_delta']].to_numpy(), atol=1e-12, rtol=0)
    assert (delta <= 2).astype(int).tolist() == old[panel + '_sets']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8.5, 'axes.titlesize': 9.5, 'axes.labelsize': 9, 'xtick.labelsize': 8.2, 'ytick.labelsize': 8.4, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none'})
fig = plt.figure(figsize=(11, 5.1))
axs = [fig.add_axes([0.15, 0.2, 0.3, 0.64]), fig.add_axes([0.645, 0.2, 0.27, 0.64])]
colors = ['#697782', '#153F68', '#138D91']
markers = ['o', 'o', 'D']
offsets = [-0.21, 0, 0.21]
statuses = []
for ax, panel, title in zip(axs, ['left', 'right'], ['TRR inclusion · collection · B2 density level', 'B2 analysis period (start year)']):
    sub = d[d.panel == panel].reset_index(drop=True)
    n = len(sub)
    ax.set_xscale('symlog', linthresh=2, linscale=1.25, base=10)
    ax.set_xlim(-0.15, 45)
    ax.set_ylim(n - 0.5, -0.6)
    ax.axvspan(0, 2, color='#C3DFE2', alpha=0.65, zorder=0)
    ax.axvline(2, color=colors[2], lw=0.85, ls=(0, (3, 2)), zorder=1)
    ax.set_yticks(range(n), sub.condition)
    ax.set_xticks([0, 1, 2, 5, 10, 20, 40], ['0', '1', '2', '5', '10', '20', '40'])
    ax.grid(axis='x', color='#DCE4E8', lw=0.45, zorder=0)
    ax.tick_params(axis='y', length=0, pad=7)
    ax.tick_params(axis='x', length=3, width=0.6)
    ax.spines[['top', 'right', 'left']].set_visible(False)
    ax.spines['bottom'].set_linewidth(0.6)
    for h in [2.5, 4.5, 6.5, 8.5] if panel == 'left' else [1.5, 3.5]:
        ax.axhline(h, color='#CCD5DB', lw=0.65, zorder=0)
    for j, row in sub.iterrows():
        for k in range(3):
            x = row[f'R{k}_delta']
            y = j + offsets[k]
            ax.scatter(x, y, s=26, marker=markers[k], facecolors='white' if k == 0 else colors[k], edgecolors=colors[k], linewidths=0.95, zorder=4)
            if x <= 2:
                xytext = (-5, 0) if x > 1.5 else (5, 0)
                ax.annotate(f'{x:.3f}', (x, y), xytext=xytext, textcoords='offset points', ha='right' if x > 1.5 else 'left', va='center', fontsize=7.3, color=colors[k])
    ax.set_title(title, pad=10)
    ax.set_xlabel('ΔIC = IC − min(IC)', labelpad=6)
    pairs = [(0, 2), (5, 6), (7, 8), (9, 10)] if panel == 'left' else [(0, 1), (2, 3), (4, 5)]
    for i, j in pairs:
        a = {f'R{k}' for k in range(3) if sub.iloc[i][f'R{k}_delta'] <= 2}
        b = {f'R{k}' for k in range(3) if sub.iloc[j][f'R{k}_delta'] <= 2}
        status = 'overlap' if a & b else 'disjoint'
        statuses.append({'S0': sub.iloc[i].condition, 'S2': sub.iloc[j].condition, 'status': status})
        trans = ax.get_yaxis_transform()
        ax.plot([1.012, 1.03, 1.03, 1.012], [i, i, j, j], transform=trans, color='#89959D', lw=0.7, clip_on=False)
        ax.text(1.052, (i + j) / 2, status, transform=trans, ha='left', va='center', fontsize=8.0, color=colors[2] if status == 'overlap' else '#59656D', fontweight='bold' if status == 'overlap' else 'normal', clip_on=False)
handles = [Line2D([], [], marker=markers[k], color='none', markerfacecolor='white' if k == 0 else colors[k], markeredgecolor=colors[k], markersize=5, label=f'R{k}') for k in range(3)]
handles.append(Patch(facecolor='#C3DFE2', edgecolor='none', label='IC-based candidate band: ΔIC ≤ 2'))
fig.legend(handles=handles, loc='upper center', bbox_to_anchor=(0.52, 0.982), ncol=4, frameon=False, columnspacing=2.0, handletextpad=0.6, fontsize=8.8)
fig.text(0.53, 0.101, 'Shared x-scale: linear from 0 to 2; logarithmic above 2. Values label candidate models only.', ha='center', fontsize=8.1)
fig.text(0.53, 0.041, 'Initial condition-specific runs; follow-up sampling intensities are shown in Figure 10.', ha='center', fontsize=8.6, color=colors[1])
stamp = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d-%H%M')
base = 'figure_09'
for ext in ['png', 'svg', 'pdf']:
    fig.savefig(O / f'{base}.{ext}', dpi=600, facecolor='white')
plt.close(fig)
validation = {'conditions': 17, 'IC_values': 51, 'candidate_sets_matching_tables20_21': 17, 'missing_IC_values': 0, 'candidate_rule': 'IC − min(IC) ≤ 2.0', 'pair_comparisons': statuses, 'key_deltas': d[d.condition.isin(['TRR S0', '2005–2023 S0'])].to_dict('records'), 'sources_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(S.glob('*'))}}
(ROOT / 'validation.json').write_text(json.dumps(validation, ensure_ascii=False, indent=2) + '\n')
