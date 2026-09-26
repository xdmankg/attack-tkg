# Verbatim function excerpts from frozen V03-02 run_v03_02.py
import numpy as np
import time
EPS=1e-12

def fit_model(y: np.ndarray, x: np.ndarray, model: str, names: list[str]) -> dict:
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    fitted = x @ beta
    residual = y - fitted
    return {
        "model": model, "terms": names, "beta": beta, "fitted": fitted, "residual": residual,
        "rss": float(np.square(residual).sum()), "rank": int(np.linalg.matrix_rank(x)),
        "n_transitions": y.shape[0], "response_dimensions": y.shape[1],
        "solver": "numpy.linalg.lstsq(rcond=None)", "rss_aggregation": "sum over all 21x9 residual cells",
    }

def generic_wild_bootstrap(y: np.ndarray, xr: np.ndarray, xf: np.ndarray, seed: int, b: int) -> dict:
    reduced = fit_model(y, xr, "REDUCED", [f"x{i}" for i in range(xr.shape[1])])
    full = fit_model(y, xf, "FULL", [f"x{i}" for i in range(xf.shape[1])])
    observed = reduced["rss"] - full["rss"]
    residual = reduced["residual"] - reduced["residual"].mean(axis=0)
    pinv_r, pinv_f = np.linalg.pinv(xr), np.linalg.pinv(xf)
    rng = np.random.default_rng(seed)
    signs = rng.choice(np.asarray([-1.0, 1.0]), size=(b, y.shape[0]))
    stats = np.empty(b, dtype=float)
    t0 = time.perf_counter()
    for i, sign in enumerate(signs):
        ys = reduced["fitted"] + sign[:, None] * residual
        fit_r = xr @ (pinv_r @ ys)
        fit_f = xf @ (pinv_f @ ys)
        stats[i] = float(np.square(ys - fit_r).sum() - np.square(ys - fit_f).sum())
    seconds = time.perf_counter() - t0
    exceed = int(np.sum(stats >= observed))
    return {
        "observed": observed, "partial_r2": observed / reduced["rss"], "statistics": stats,
        "exceedance_count": exceed, "p": (1 + exceed) / (1 + b), "seed": seed, "B": b,
        "seconds": seconds, "throughput_per_second": b / max(seconds, EPS),
        "residual_column_mean_max_abs": float(np.max(np.abs(residual.mean(axis=0)))),
        "sign_values": sorted(np.unique(signs).tolist()), "shared_sign_across_9_dimensions": True,
        "rng": "numpy.random.default_rng / PCG64", "worker_count": 1,
    }
