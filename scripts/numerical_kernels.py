"""Numerical functions extracted from the archived Stage15 and V07-01 implementations.
See docs/code_provenance.csv for the original source hashes and function locations.
"""
from __future__ import annotations
import itertools
import math
import numpy as np
EPS = 1e-12
MODELS = ['R0', 'R1', 'R2']
DESCRIPTORS = ['component_share_birth', 'component_share_death', 'component_share_increase', 'support_share_low', 'support_share_medium', 'rms_low', 'rms_medium', 'rms_high', 'persistent_relation_rms']

def build_year(membership, joined, technique_index, year):
    mem = membership[membership.year == year].sort_values("canonical_document_id"); weights_by_doc = dict(zip(mem.canonical_document_id, mem.primary_membership_mass))
    grouped = joined[joined.year == year].groupby("canonical_document_id").canonical_attack_id.apply(lambda values: {technique_index[value] for value in values.drop_duplicates()})
    docs = sorted(mem.canonical_document_id); rows = [set(grouped.get(doc, set())) for doc in docs]; weights = np.asarray([weights_by_doc[doc] for doc in docs], float); strata = {}
    for idx, weight in enumerate(weights): strata.setdefault(float(weight), []).append(idx)
    return {"docs": docs, "rows": rows, "weights": weights, "strata": strata, "effective_mass": float(weights.sum())}

def project(rows, weights, pair_matrix):
    indices, values, binary = [], [], []
    for techniques, weight in zip(rows, weights):
        if len(techniques) < 2: continue
        array = np.fromiter(sorted(techniques), dtype=np.int32); ii, jj = np.triu_indices(len(array), 1); pairs = pair_matrix[array[ii], array[jj]]; pairs = pairs[pairs >= 0]
        if len(pairs): indices.append(pairs); values.append(np.full(len(pairs), weight, float)); binary.append(pairs)
    if not indices: return np.zeros(28195), np.zeros(28195, np.int32)
    return np.bincount(np.concatenate(indices), weights=np.concatenate(values), minlength=28195), np.bincount(np.concatenate(binary), minlength=28195).astype(np.int32)

def curveball_trade(rows, indices, rng):
    a, b = rng.choice(indices, size=2, replace=False); left, right = rows[a], rows[b]; ul, ur = list(left - right), list(right - left)
    if not ul or not ur: return
    pool = np.asarray(ul + ur, np.int32); rng.shuffle(pool); shared = left & right; rows[a] = shared | set(pool[:len(ul)].tolist()); rows[b] = shared | set(pool[len(ul):].tolist())

def apply_trades(rows, eligible, rng, burnin=False):
    for indices in eligible:
        count = max(100, 10 * len(indices)) if burnin else max(10, 2 * len(indices))
        for _ in range(count): curveball_trade(rows, indices, rng)

def descriptor(pre, post, support):
    delta = (post - pre) / (post + pre + EPS); active = np.abs(delta) > 1e-15
    if not active.any(): return {name: 0.0 for name in DESCRIPTORS}
    d, a, b, s = delta[active], pre[active], post[active], support[active]; birth = (a == 0) & (b > 0); death = (a > 0) & (b == 0); increase = (a > 0) & (b > a); low = (s >= 1) & (s <= 2); medium = (s >= 3) & (s <= 5); high = s > 5; persistent = (a > 0) & (b > 0)
    def rms(mask): return 0.0 if not mask.any() else float(np.sqrt(np.mean(d[mask] ** 2)))
    n = len(d); return {"component_share_birth": birth.sum() / n, "component_share_death": death.sum() / n, "component_share_increase": increase.sum() / n, "support_share_low": low.sum() / n, "support_share_medium": medium.sum() / n, "rms_low": rms(low), "rms_medium": rms(medium), "rms_high": rms(high), "persistent_relation_rms": rms(persistent)}

def ic_value(rss, nobs, parameters, boundaries=0, time_points=21): return float(nobs * np.log((rss + EPS) / nobs) + parameters * np.log(nobs) + 2 * boundaries * np.log(time_points))

def fit_r0_exact(values, observed=None):
    n, d = values.shape; observed = np.ones(n, bool) if observed is None else observed; mean = values[observed].mean(axis=0); trajectory = np.tile(mean, (n, 1)); rss = float(((values[observed] - mean) ** 2).sum()); return {"method_id": "R0", "rss": rss, "ic": ic_value(rss, int(observed.sum()) * d, d), "parameter_count": d, "trajectory": trajectory, "boundaries": []}

def fit_r1_exact(values, observed=None):
    n, d = values.shape; observed = np.ones(n, bool) if observed is None else observed; tau = np.linspace(-1, 1, n); design = np.column_stack([np.ones(n), tau]); beta = np.linalg.lstsq(design[observed], values[observed], rcond=None)[0]; trajectory = design @ beta; residuals = values - trajectory; rss = float((residuals[observed] ** 2).sum()); return {"method_id": "R1", "rss": rss, "ic": ic_value(rss, int(observed.sum()) * d, 2 * d), "parameter_count": 2 * d, "trajectory": trajectory, "residuals": residuals, "coefficients": beta, "tau": tau, "boundaries": [], "slope_norm": float(np.linalg.norm(beta[1]))}

def fit_r2_exact(values, observed=None):
    n, d = values.shape; observed = np.ones(n, bool) if observed is None else observed; candidates = []
    for k in (2, 3):
        best = None
        for cuts in itertools.combinations(range(5, n - 4), k - 1):
            bounds = (0, *cuts, n)
            if any(bounds[i + 1] - bounds[i] < 5 for i in range(k)): continue
            rss, means, valid = 0.0, [], True
            for a, b in zip(bounds[:-1], bounds[1:]):
                idx = np.arange(a, b)[observed[a:b]]
                if len(idx) == 0: valid = False; break
                mean = values[idx].mean(axis=0); means.append(mean); rss += float(((values[idx] - mean) ** 2).sum())
            if valid and (best is None or (rss, cuts) < (best[0], best[1])): best = (rss, cuts, means)
        rss, cuts, means = best; bounds = (0, *cuts, n); trajectory = np.zeros_like(values)
        for (a, b), mean in zip(zip(bounds[:-1], bounds[1:]), means): trajectory[a:b] = mean
        candidates.append({"method_id": "R2", "k": k, "rss": rss, "ic": ic_value(rss, int(observed.sum()) * d, d * k, k - 1, n), "parameter_count": d * k, "trajectory": trajectory, "boundaries": list(cuts)})
    return min(candidates, key=lambda row: (row["ic"], row["k"], row["boundaries"]))

def all_models(values):
    fits = [fit_r0_exact(values), fit_r1_exact(values), fit_r2_exact(values)]; best = min(fits, key=lambda row: (row["ic"], ("R0", "R1", "R2").index(row["method_id"]))); return fits, best

def robust_params(raw: np.ndarray, mask: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    use = np.ones(len(raw), bool) if mask is None else mask
    med = np.median(raw[use], axis=0)
    mad = np.median(np.abs(raw[use] - med), axis=0)
    scale = 1.4826 * mad
    fallback = scale <= EPS
    scale[fallback] = 1.0
    return med, scale, fallback

def preferred_set(fits: list[dict]) -> str:
    by = {row["method_id"]: row for row in fits}; minimum = min(row["ic"] for row in fits)
    return "{" + ",".join(model for model in MODELS if by[model]["ic"] - minimum <= 2.0 + 1e-12) + "}"

def stage_global_analysis(stage, raw: np.ndarray) -> dict:
    med, scale, _ = robust_params(raw); values = (raw - med) / scale
    fits, best = stage.all_models(values); by = {row["method_id"]: row for row in fits}
    errors = {model: [] for model in MODELS}
    for holdout in range(len(values)):
        mask = np.ones(len(values), bool); mask[holdout] = False
        fold_fits = [stage.fit_r0_exact(values, mask), stage.fit_r1_exact(values, mask), stage.fit_r2_exact(values, mask)]
        for fit in fold_fits: errors[fit["method_id"]].append(float(np.mean((values[holdout] - fit["trajectory"][holdout]) ** 2)))
    return {"values": values, "median": med, "scale": scale, "fits": fits, "best": best["method_id"],
            "candidate_set": preferred_set(fits), "T12": float(by["R1"]["ic"] - by["R2"]["ic"]),
            **{f"{model}_RSS": float(by[model]["rss"]) for model in MODELS}, **{f"{model}_IC": float(by[model]["ic"]) for model in MODELS},
            **{f"{model}_LOTO": float(np.sqrt(np.mean(errors[model]))) for model in MODELS}}

def fit_fold_prediction(stage, raw: np.ndarray, holdout: int, gap: int):
    n = len(raw); train = np.ones(n, bool)
    train[max(0, holdout - gap):min(n, holdout + gap + 1)] = False
    med, scale, fallback = robust_params(raw, train); scaled = (raw - med) / scale
    fits = [stage.fit_r0_exact(scaled, train), stage.fit_r1_exact(scaled, train), stage.fit_r2_exact(scaled, train)]
    return ({fit["method_id"]: fit["trajectory"][holdout] * scale + med for fit in fits},
            {"median": med, "scale": scale, "fallback": fallback, "train": train}, scaled, fits)

def qr_rss_batch(y: np.ndarray, design: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(design, mode="reduced")
    total = np.sum(y * y, axis=1)
    projected = np.einsum("nk,bnd->bkd", q, y, optimize=True)
    return total - np.sum(projected * projected, axis=1)

def holm_adjust(pvalues: np.ndarray) -> np.ndarray:
    p = np.asarray(pvalues, float); order = np.argsort(p); adjusted = np.empty_like(p); running = 0.0; m = len(p)
    for rank, idx in enumerate(order):
        running = max(running, (m - rank) * p[idx]); adjusted[idx] = min(1.0, running)
    return adjusted

def multiplier_matrix(rng: np.random.Generator, scheme: str, b: int, n: int, ell: int | None = None) -> np.ndarray:
    if scheme == "LEGACY_RADEMACHER": return rng.choice(np.asarray([-1.0, 1.0]), size=(b, n))
    if scheme == "GAUSSIAN_L1": return rng.normal(size=(b, n))
    if ell is None: raise ValueError("DWB requires ell")
    eta = rng.normal(size=(b, n + ell - 1))
    return np.stack([eta[:, i:i + ell].sum(axis=1) / math.sqrt(ell) for i in range(n)], axis=1)

def conditional_bootstrap(values: np.ndarray, coverage: np.ndarray, direction: str, scheme: str, seed: int, b: int = 10000):
    n, d = values.shape; tau = np.linspace(-1, 1, n)
    if direction == "TIME_GIVEN_COVERAGE": reduced = np.column_stack([np.ones(n), coverage]); full = np.column_stack([np.ones(n), coverage, tau])
    else: reduced = np.column_stack([np.ones(n), tau]); full = np.column_stack([np.ones(n), tau, coverage])
    beta = np.linalg.lstsq(reduced, values, rcond=None)[0]; fitted = reduced @ beta; residual = values - fitted; residual -= residual.mean(axis=0, keepdims=True)
    rss_reduced_by_dim = np.sum((values - reduced @ np.linalg.lstsq(reduced, values, rcond=None)[0]) ** 2, axis=0)
    observed_by_dim = rss_reduced_by_dim - np.sum((values - full @ np.linalg.lstsq(full, values, rcond=None)[0]) ** 2, axis=0)
    observed = float(observed_by_dim.sum())
    ell = int(scheme.rsplit("L", 1)[1]) if scheme.startswith("DWB_L") else None
    xi = multiplier_matrix(np.random.default_rng(seed), scheme, b, n, ell)
    ystar = fitted[None, :, :] + xi[:, :, None] * residual[None, :, :]
    component = qr_rss_batch(ystar, reduced) - qr_rss_batch(ystar, full)
    aggregate = component.sum(axis=1)
    count = int((aggregate >= observed - 1e-12).sum()); p = (1 + count) / (b + 1)
    component_counts = (component >= observed_by_dim[None, :] - 1e-12).sum(axis=0).astype(int)
    component_p = (1 + component_counts) / (b + 1); adjusted = holm_adjust(component_p)
    return observed, float(rss_reduced_by_dim.sum()), aggregate, count, p, observed_by_dim, component_counts, component_p, adjusted

def moving_block_indices(rng: np.random.Generator, b: int, n: int, length: int) -> np.ndarray:
    blocks = math.ceil(n / length); starts = rng.integers(0, n - length + 1, size=(b, blocks))
    offsets = np.arange(length); return (starts[:, :, None] + offsets).reshape(b, -1)[:, :n]
