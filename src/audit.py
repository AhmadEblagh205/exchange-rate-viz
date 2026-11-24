"""Deterministic known-truth unit-scale audit, plus the synthetic sample CSV.

Four quote series share exactly one multiplicative path and differ only in
starting level. Any scale-free diagnostic must therefore agree across them.
These are controlled mathematical checks, not empirical FX results.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from analysis import rebase_to_100, rolling_volatility

ROOT = Path(__file__).resolve().parents[1]
STARTS = (0.80, 1.20, 100.0, 150.0)
N_OBS = 500


def run_audit(n_obs: int = N_OBS, seed: int = 24) -> dict:
    rng = np.random.default_rng(seed)
    logret = rng.normal(0, 0.006, n_obs)
    logret[0] = 0.0
    path = np.exp(np.cumsum(logret))
    idx = pd.bdate_range("2020-01-01", periods=n_obs)
    frame = pd.DataFrame({f"start_{s:g}": s * path for s in STARTS}, index=idx)

    sds = frame.std()
    rebased = rebase_to_100(frame)
    rebased_spread = (rebased.max(axis=1) - rebased.min(axis=1)).max()
    vols = frame.apply(rolling_volatility).dropna()
    recip = (1 / frame).apply(rolling_volatility).dropna()
    return {
        "n_observations": n_obs,
        "start_levels": list(STARTS),
        "raw_level_sd_ratio_max_over_min": float(sds.max() / sds.min()),
        "rebased_max_spread_index_points": float(rebased_spread),
        "mean_annualised_30_observation_log_vol_pct": {
            c: float(vols[c].mean()) for c in vols},
        "vol_max_spread_across_series_pp": float(
            (vols.max(axis=1) - vols.min(axis=1)).max()),
        "vol_max_direct_vs_reciprocal_diff_pp": float((vols - recip).abs().max().max()),
    }


def write_sample(path: Path, seed: int = 7) -> Path:
    """Write a small SYNTHETIC ECB-format file (newest first, trailing empty
    column, a few '-' gaps). Not real exchange-rate data."""
    rng = np.random.default_rng(seed)
    idx = pd.bdate_range("2019-01-01", "2022-12-30")
    starts = {"USD": 1.14, "GBP": 0.90, "JPY": 125.0, "CHF": 1.13}
    cols = {}
    for c, s in starts.items():  # mean-reverting log path around the start level
        x, vals = 0.0, []
        for e in rng.normal(0, 0.005, len(idx)):
            x += -0.01 * x + e
            vals.append(s * np.exp(x))
        cols[c] = vals
    df = pd.DataFrame(cols, index=idx).round(4)
    lines = ["Date,USD,JPY,GBP,CHF,"]
    for k, (d, row) in enumerate(df.iloc[::-1].iterrows()):
        cells = ["-" if k % 400 == 399 and c == "JPY" else f"{row[c]:g}"
                 for c in ("USD", "JPY", "GBP", "CHF")]
        lines.append(f"{d:%Y-%m-%d}," + ",".join(cells) + ",")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")
    return path


def main():
    summary = run_audit()
    out = ROOT / "reports" / "audit_summary.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2) + "\n")
    sample = write_sample(ROOT / "data" / "sample" / "synthetic_eurofxref_sample.csv")
    print(json.dumps(summary, indent=2))
    print(f"Saved -> {out}\nSaved -> {sample}")


if __name__ == "__main__":
    main()
