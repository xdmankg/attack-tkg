import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, hashlib, zipfile
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT = Path(sys.argv[1]).resolve()
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
SEED, B = (2026081505, 10000)
p = np.load(ROOT / 'source/stage15_inputs.npz')
raw, coverage = (p['raw'], p['coverage'])
median = np.median(raw, axis=0)
scale = 1.4826 * np.median(np.abs(raw - median), axis=0)
scale[scale <= 1e-12] = 1.0
y = (raw - median) / scale
xr = np.column_stack([np.ones(21), coverage])
xf = np.column_stack([np.ones(21), np.linspace(-1, 1, 21), coverage])
fitted = xr @ np.linalg.lstsq(xr, y, rcond=None)[0]
residual = y - fitted
rss_reduced = np.square(residual).sum()
observed = float(rss_reduced - np.square(y - xf @ np.linalg.lstsq(xf, y, rcond=None)[0]).sum())
residual -= residual.mean(axis=0)
pinv_r, pinv_f = (np.linalg.pinv(xr), np.linalg.pinv(xf))
signs = np.random.default_rng(SEED).choice(np.asarray([-1.0, 1.0]), size=(B, 21))
stats = np.empty(B)
for i, sign in enumerate(signs):
    ys = fitted + sign[:, None] * residual
    stats[i] = np.square(ys - xr @ (pinv_r @ ys)).sum() - np.square(ys - xf @ (pinv_f @ ys)).sum()
exceed = int(np.sum(stats >= observed))
pvalue = (1 + exceed) / (1 + B)
assert abs(observed - 15.5479266334405) < 1e-10
assert exceed == 1398
assert abs(pvalue - 0.13988601139886012) < 1e-15
q95 = float(np.quantile(stats, 0.95))
np.savez_compressed(ROOT / 'source/initial_bootstrap_replay.npz', delta_rss_star=stats, observed=observed, seed=SEED, B=B)
reloaded = np.load(ROOT / 'source/initial_bootstrap_replay.npz')['delta_rss_star']
assert np.array_equal(stats, reloaded)
stats = reloaded
np.savetxt(ROOT / 'source/bootstrap_statistics.csv', stats, delimiter=',', header='delta_rss_star', comments='', fmt='%.17g')
validation = dict(contrast='Time | Analytical Coverage', data_source='Frozen V07 baseline_datasets.npz: STAGE15_S0_raw and STAGE15_S0_coverage', distribution_source='Deterministic replay with frozen V03-02 generic_wild_bootstrap algorithm and initial seed; not the later V07 Rademacher reevaluation.', seed=SEED, B=B, n_transitions=21, n_descriptors=9, observed_delta_RSS=observed, upper_tail_count=exceed, empirical_tail_fraction=exceed / B, plus_one_raw_p=pvalue, empirical_95th_percentile=q95, reduced_RSS=float(rss_reduced), partial_R2=float(observed / rss_reduced), numpy_version=np.__version__, validation='PASS: original observed statistic within 1e-10; original exceedance count and plus-one p reproduced.', plotted_array='source/initial_bootstrap_replay.npz::delta_rss_star', array_sha256_float64=hashlib.sha256(stats.astype('<f8').tobytes()).hexdigest(), quantile_method='numpy.quantile(method=linear)', source_sha256=hashlib.sha256((ROOT / 'source/stage15_inputs.npz').read_bytes()).hexdigest())
(ROOT / 'validation.json').write_text(json.dumps(validation, indent=2) + '\n')
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'axes.labelsize': 8.4, 'xtick.labelsize': 7.8, 'ytick.labelsize': 7.8, 'axes.linewidth': 0.65, 'pdf.fonttype': 42, 'ps.fonttype': 42, 'svg.fonttype': 'none', 'mathtext.default': 'regular'})
fig, ax = plt.subplots(figsize=(7.2, 3.6))
fig.subplots_adjust(left=0.082, right=0.985, bottom=0.2, top=0.88)
navy, orange, gray = ('#153F68', '#DB7D24', '#697782')
bins = np.sort(np.unique(np.r_[np.arange(0, 28.01, 0.75), observed]))
counts, edges = np.histogram(stats, bins=bins)
dens = counts / (B * np.diff(edges))
assert counts.sum() == B
assert counts[edges[:-1] >= observed].sum() == exceed
np.savetxt(ROOT / 'source/histogram_bins.csv', np.column_stack([edges[:-1], edges[1:], counts, dens]), delimiter=',', header='bin_left,bin_right,count,density', comments='', fmt='%.17g')
for left, width, height in zip(edges[:-1], np.diff(edges), dens):
    ax.bar(left, height, width=width, align='edge', color=orange if left >= observed else navy, edgecolor='white', linewidth=0.35, zorder=3)
ax.axvline(observed, color=orange, lw=1.65, zorder=5)
ax.axvline(q95, color=gray, lw=0.9, ls=(0, (3, 2)), zorder=4)
ax.set(xlim=(0, 28), ylim=(0, 0.115), ylabel='Density')
ax.set_xticks(np.arange(0, 29, 4))
ax.set_yticks([0, 0.025, 0.05, 0.075, 0.1], labels=['0', '0.025', '0.050', '0.075', '0.100'])
ax.set_xlabel('$\\Delta$RSS* under the wild bootstrap' + '\n(reduced model: Analytical Coverage only)', labelpad=6)
ax.spines[['top', 'right']].set_visible(False)
ax.grid(axis='y', color='#E9EEF1', linewidth=0.5, zorder=0)
ax.tick_params(length=3, width=0.6)
fig.text(0.082, 0.945, 'Initial independent Rademacher test', ha='left', va='center', fontsize=8.7)
fig.text(0.985, 0.945, 'B = 10,000 · 21 transitions', ha='right', va='center', fontsize=8)
ax.text(observed - 0.35, 0.109, 'Observed\n' + '$\\Delta$RSS = 15.548', ha='right', va='top', fontsize=8.1, color=navy)
ax.text(q95 + 0.4, 0.105, '95th percentile\n' + f'{q95:.3f}', ha='left', va='top', fontsize=7.7, color=gray)
ax.text(0.975, 0.61, 'Raw p-value\np = 0.1399 (upper tail)', transform=ax.transAxes, ha='right', va='top', fontsize=8.5, color=orange, linespacing=1.5)
ax.text(0.975, 0.405, 'Criterion not met\n' + '$\\alpha$ = 0.05', transform=ax.transAxes, ha='right', va='top', fontsize=8, color='#333333', linespacing=1.5)
ax.annotate('', xy=(20, 0.019), xytext=(23, 0.04), arrowprops=dict(arrowstyle='->', color=orange, lw=0.8))
stamp = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d-%H%M')
base = 'figure_07'
for ext in ['png', 'svg', 'pdf']:
    fig.savefig(OUT / f'{base}.{ext}', dpi=600, facecolor='white')
plt.close(fig)
