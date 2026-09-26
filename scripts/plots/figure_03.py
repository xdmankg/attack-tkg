import sys
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
import json, zipfile, hashlib, shutil
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyArrowPatch, Circle
ROOT = Path(sys.argv[1]).resolve()
OUT = ROOT / 'output'
OUT.mkdir(exist_ok=True)
SRC = ROOT / 'source'
X = np.array([[1, 1, 0, 0, 0], [0, 0, 1, 1, 0], [1, 0, 1, 0, 1], [0, 1, 0, 1, 1], [1, 0, 0, 1, 0], [0, 1, 1, 0, 0]])
Y = X.copy()
Y[0, 1] = 0
Y[0, 3] = 1
Y[4, 1] = 1
Y[4, 3] = 0
Z = np.array([[1, 0, 1, 0, 0], [0, 1, 0, 1, 0], [1, 0, 1, 0, 1], [0, 1, 0, 1, 1], [1, 0, 0, 1, 0], [0, 1, 1, 0, 0]])
W = X.T @ X / 6
mu = (X.T @ X + Z.T @ Z) / 12
R = np.maximum(W - mu, 0)
upper = np.triu(np.ones((5, 5), dtype=bool), 1)
assert X.sum(1).tolist() == [2, 2, 3, 3, 2, 2]
assert X.sum(0).tolist() == [3, 3, 3, 3, 2]
assert np.array_equal(X.sum(0), Y.sum(0)) and np.array_equal(X.sum(1), Y.sum(1))
assert np.array_equal(X.sum(0), Z.sum(0)) and np.array_equal(X.sum(1), Z.sum(1))
assert np.argwhere(X != Y).tolist() == [[0, 1], [0, 3], [4, 1], [4, 3]]
assert np.allclose(W[upper], 1 / 6)
assert np.argwhere((R > 0) & upper).tolist() == [[0, 1], [2, 3]]
expected_mu = [1 / 12, 1 / 4, 1 / 6, 1 / 6, 1 / 6, 1 / 4, 1 / 6, 1 / 12, 1 / 6, 1 / 6]
assert np.allclose(mu[upper], expected_mu)
for name, a in [('observed_incidence', X), ('single_swap_incidence', Y), ('illustrative_state_2', Z), ('observed_strength', W), ('illustrative_mu', mu), ('positive_excess', R)]:
    np.savetxt(SRC / (name + '.csv'), a, delimiter=',', fmt='%.12g')
navy = '#153F68'
green = '#23664C'
teal = '#15968B'
orange = '#DB8A27'
gray = '#CFD0D0'
edge = '#AAB6BD'
ink = '#15232B'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 13, 'svg.fonttype': 'none', 'pdf.fonttype': 42, 'ps.fonttype': 42})
fig = plt.figure(figsize=(18, 6.5), facecolor='white')
positions = [(0.009, 0.153, 0.185, 0.832), (0.204, 0.153, 0.239, 0.832), (0.453, 0.153, 0.229, 0.832), (0.692, 0.153, 0.299, 0.832)]
axes = []
headers = ['A. Observed incidence X', 'B. One composition-preserving swap', 'C. Many samples → null expectation μ', 'D. Positive Excess']
for (x, y, w, h), title in zip(positions, headers):
    a = fig.add_axes([x, y, w, h])
    a.set_xlim(0, 1)
    a.set_ylim(0, 1)
    a.axis('off')
    axes.append(a)
    a.add_patch(Rectangle((0.001, 0.001), 0.998, 0.998, facecolor='white', edgecolor='#7E929F', lw=0.8, zorder=-10))
    a.add_patch(Rectangle((0.01, 0.908), 0.98, 0.08, facecolor=gray, edgecolor='none'))
    a.text(0.026, 0.948, title, fontsize=12.3 if title.startswith('C.') else 13.8, fontweight='bold', va='center', ha='left')

def arrow(a, x1, y1, x2, y2, color=ink, lw=1.2):
    a.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle='-|>', mutation_scale=12, color=color, lw=lw))

def grid(a, M, x, y, w, h, color=navy, labels=True, sums=True, fontsize=12, highlights=()):
    nr, nc = M.shape
    cw = w / nc
    ch = h / nr
    for r in range(nr):
        for c in range(nc):
            a.add_patch(Rectangle((x + c * cw, y + (nr - r - 1) * ch), cw, ch, facecolor=color if M[r, c] else '#F2F6F7', edgecolor='#B9C7CF', lw=0.65))
            if (r, c) in highlights:
                a.add_patch(Rectangle((x + c * cw + 0.003, y + (nr - r - 1) * ch + 0.002), cw - 0.006, ch - 0.004, fill=False, edgecolor=orange, lw=2))
    if labels:
        for r in range(nr):
            a.text(x - 0.022, y + (nr - r - 0.5) * ch, f'D{r + 1}', ha='right', va='center', fontsize=fontsize)
        for c in range(nc):
            a.text(x + (c + 0.5) * cw, y + h + 0.028, f'T{c + 1}', ha='center', va='center', fontsize=fontsize)
    if sums:
        for r in range(nr):
            a.text(x + w + 0.028, y + (nr - r - 0.5) * ch, str(M[r].sum()), ha='center', va='center', fontsize=fontsize)
        for c in range(nc):
            a.text(x + (c + 0.5) * cw, y - 0.03, str(M[:, c].sum()), ha='center', va='center', fontsize=fontsize)

def pairmatrix(a, M, x, y, w, h, kind='mu', fontsize=10.8):
    cw = w / 5
    ch = h / 5
    for r in range(5):
        a.text(x - 0.018, y + (4 - r + 0.5) * ch, f'T{r + 1}', ha='right', va='center', fontsize=fontsize)
        a.text(x + (r + 0.5) * cw, y + h + 0.027, f'T{r + 1}', ha='center', va='center', fontsize=fontsize)
        for c in range(r + 1, 5):
            value = M[r, c]
            if kind == 'mu':
                face = plt.cm.YlOrBr(0.12 + 0.53 * value / 0.25)
            else:
                face = '#88CEC0' if value > 0 else '#F0F8F4'
            a.add_patch(Rectangle((x + c * cw, y + (4 - r) * ch), cw, ch, facecolor=face, edgecolor='white', lw=0.8))
            a.text(x + (c + 0.5) * cw, y + (4 - r + 0.5) * ch, f'{value:.2f}', ha='center', va='center', fontsize=fontsize, color='black')
A = axes[0]
A.text(0.5, 0.86, 'Adopted document–Technique links', ha='center', fontsize=11.8)
grid(A, X, 0.17, 0.335, 0.67, 0.44, fontsize=12.5, highlights=[(0, 1), (0, 3), (4, 1), (4, 3)])
A.text(0.51, 0.259, 'Column sums', ha='center', fontsize=11, color='#50616D')
A.text(0.9, 0.807, 'Σ', ha='center', fontsize=12)
A.text(0.5, 0.19, 'Orange: four cells in the swap', ha='center', fontsize=11, color='#8D591D')
A.text(0.5, 0.073, 'Row sums: Techniques per document\nColumn sums: documents per Technique', ha='center', va='center', fontsize=11.4, linespacing=1.6)
B = axes[1]

def block(x, y, M, title):
    cw = 0.079
    ch = 0.071
    B.text(x + cw, y + 0.2, title, ha='center', fontsize=12)
    for j, t in enumerate(['T2', 'T4']):
        B.text(x + (j + 0.5) * cw, y + 0.165, t, ha='center', fontsize=10.8)
    for i, d in enumerate(['D1', 'D5']):
        B.text(x - 0.016, y + (1 - i + 0.5) * ch, d, ha='right', va='center', fontsize=10.8)
        for j in range(2):
            B.add_patch(Rectangle((x + j * cw, y + (1 - i) * ch), cw, ch, facecolor=green if M[i, j] else '#F2F6F7', edgecolor=orange, lw=1.15))
block(0.17, 0.622, np.eye(2, dtype=int), 'Before')
block(0.66, 0.622, 1 - np.eye(2, dtype=int), 'After')
arrow(B, 0.37, 0.691, 0.55, 0.691)
B.text(0.5, 0.565, 'One swap → updated incidence', ha='center', fontsize=11.5)
grid(B, Y, 0.265, 0.224, 0.47, 0.255, color=green, fontsize=10.8, highlights=[(0, 1), (0, 3), (4, 1), (4, 3)])
B.text(0.5, 0.159, 'Same row sums and column sums', ha='center', fontsize=11.2)
B.text(0.5, 0.065, 'Partners change; row and column sums do not.\nSwaps stay within one equal-weight stratum\n(here: all six documents).', ha='center', va='center', fontsize=11.2, linespacing=1.5)
C = axes[2]
for x, y, M in [(0.08, 0.692, X), (0.17, 0.718, Y), (0.26, 0.743, Z)]:
    grid(C, M, x, y, 0.21, 0.095, color='#87B8A5', labels=False, sums=False)
C.text(0.54, 0.777, '…', fontsize=21, ha='center')
C.text(0.68, 0.78, 'B samples', fontsize=12, ha='center')
arrow(C, 0.77, 0.754, 0.77, 0.674)
C.text(0.5, 0.643, 'Mean co-reporting strength per pair', ha='center', fontsize=11.6)
pairmatrix(C, mu, 0.145, 0.245, 0.74, 0.32)
C.text(0.5, 0.185, 'CP-null expectation μ (illustrative)', ha='center', fontsize=11.8)
C.text(0.5, 0.077, 'Expected co-reporting from document\ncomposition alone (illustrative values).', ha='center', va='center', fontsize=11.5, linespacing=1.5)
D = axes[3]
D.text(0.225, 0.862, 'Two traced pairs', ha='center', fontweight='bold', fontsize=12)
D.text(0.763, 0.862, 'Positive Excess', ha='center', fontweight='bold', fontsize=12)

def trace(y, pair, obs, null, res):
    D.text(0.035, y + 0.045, pair, fontweight='bold', fontsize=12)
    maxw = 0.24
    D.text(0.035, y - 0.007, 'W_obs', fontsize=10.5, va='center')
    D.text(0.035, y - 0.064, 'μ', fontsize=11.5, va='center')
    bx = 0.145
    D.add_patch(Rectangle((bx, y - 0.024), maxw * obs / 0.25, 0.033, facecolor=navy, edgecolor='none'))
    D.add_patch(Rectangle((bx, y - 0.081), maxw * null / 0.25, 0.033, facecolor='#E5AA50', edgecolor='none'))
    if res > 0:
        D.add_patch(Rectangle((bx + maxw * null / 0.25, y - 0.024), maxw * res / 0.25, 0.033, facecolor=teal, edgecolor='none'))
    D.text(bx + maxw * obs / 0.25 + 0.009, y - 0.007, f'{obs:.2f}', fontsize=10.8, va='center')
    D.text(bx + maxw * null / 0.25 + 0.009, y - 0.064, f'{null:.2f}', fontsize=10.8, va='center')
    D.text(0.225, y - 0.123, ('Excess retained: ' if res > 0 else 'No excess: ') + f'{res:.2f}', ha='center', fontsize=11, color=green if res > 0 else ink)
trace(0.761, 'T1–T2', 1 / 6, 1 / 12, 1 / 12)
trace(0.497, 'T1–T3', 1 / 6, 1 / 4, 0)
pairmatrix(D, R, 0.555, 0.49, 0.405, 0.285, kind='R', fontsize=10.3)
arrow(D, 0.771, 0.46, 0.771, 0.405)
pts = {'T1': (0.575, 0.341), 'T2': (0.73, 0.341), 'T3': (0.575, 0.231), 'T4': (0.73, 0.231), 'T5': (0.904, 0.285)}
for p, q in [('T1', 'T2'), ('T3', 'T4')]:
    D.plot([pts[p][0], pts[q][0]], [pts[p][1], pts[q][1]], color=teal, lw=2.8, zorder=1)
for name, (x, y) in pts.items():
    D.add_patch(Circle((x, y), 0.033, facecolor='#E6F4F0', edgecolor=green, lw=0.95, zorder=2))
    D.text(x, y, name, ha='center', va='center', fontsize=10.5, zorder=3)
D.text(0.25, 0.265, 'Green segment:\nobserved strength above μ', ha='center', fontsize=11.1, linespacing=1.5)
D.text(0.5, 0.136, 'R(i, j, t) = max(0, W_obs(i, j, t) − μ(i, j, t))', ha='center', fontsize=12.5, fontweight='bold')
D.text(0.5, 0.057, 'Each observed pair occurs in one of six documents (W_obs: 0.17).\nOnly pairs above μ remain.', ha='center', va='center', fontsize=11.2, linespacing=1.5)
fig.text(0.5, 0.096, 'Positive Excess is a comparison against document composition, not evidence of execution order, causality, or pair-level significance.', ha='center', fontsize=12.3)
fig.text(0.5, 0.055, 'The observed graph and the Positive Excess graph are analyzed with the same descriptors (Section 4.1).', ha='center', fontsize=12.3)
fig.text(0.5, 0.02, 'Schematic example · six documents in one equal-weight stratum · displayed values rounded to two decimals', ha='center', fontsize=10.8, color='#51606A')
stamp = datetime.now(ZoneInfo('Asia/Seoul')).strftime('%Y%m%d-%H%M')
name = 'figure_03'
for ext in ['png', 'svg', 'pdf']:
    fig.savefig(OUT / (name + '.' + ext), dpi=400, facecolor='white')
plt.close(fig)
validation = {'observed_row_sums': X.sum(1).tolist(), 'swapped_row_sums': Y.sum(1).tolist(), 'observed_column_sums': X.sum(0).tolist(), 'swapped_column_sums': Y.sum(0).tolist(), 'changed_cells_D_T_1_based': (np.argwhere(X != Y) + 1).tolist(), 'each_observed_pair_strength': 1 / 6, 'mu_upper': mu[upper].tolist(), 'positive_excess_upper': R[upper].tolist(), 'surviving_edges': ['T1–T2', 'T3–T4'], 'single_swap_pair_strength_unchanged': bool(np.array_equal(X.T @ X, Y.T @ Y)), 'is_empirical_null_distribution': False, 'sample_mean_source_states': ['observed_incidence.csv', 'illustrative_state_2.csv'], 'source_sha256': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in SRC.glob('*.csv')}}
(ROOT / 'validation.json').write_text(json.dumps(validation, indent=2, ensure_ascii=False), encoding='utf-8')
