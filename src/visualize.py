"""Storytelling charts for ECB euro reference rates (foreign units per EUR).

Principles: one message per chart, muted raw series with a 30-observation
rolling mean, and scale-aware comparison (rebased panel) next to the raw
quote panel. Dated markers are historical CONTEXT, not causal explanations.

Usage:
    python src/download_data.py            # reuse or fetch the snapshot
    python src/visualize.py                # uses data/raw/eurofxref-hist.csv
    python src/visualize.py --csv data/sample/synthetic_eurofxref_sample.csv
"""
import argparse
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from analysis import (event_window, last_observation_date, rebase_to_100,
                      rolling_mean, rolling_volatility)
from data import load_rates

ROOT = Path(__file__).resolve().parents[1]
FIGURES = ROOT / "reports" / "figures"
BLUE, MUTED = "#0b3d91", "lightsteelblue"
CURRENCIES = {"USD": "US dollar", "GBP": "British pound",
              "JPY": "Japanese yen", "CHF": "Swiss franc"}

# Context markers (not causes).
EVENTS = {
    "2008-09-15": "Lehman Brothers\ncollapse",
    "2014-06-05": "ECB announces negative\ndeposit rate (effective\n11 June 2014)",
    "2020-03-11": "WHO characterises COVID-19\nas a pandemic",
    "2022-08-23": "ECB EUR/USD reference\nfalls below $1 again",
}
PARITY_DATE = "2022-08-23"
SHORT = {"2008-09-15": "Lehman", "2014-06-05": "ECB negative rate",
         "2020-03-11": "WHO pandemic", "2022-08-23": "Below $1 again"}


def style(ax):
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    ax.grid(alpha=0.25)


def _inside(s: pd.Series, date: str) -> bool:
    """True if the marker applies: the date lies inside the data and, for
    the parity marker, the plotted series really is below 1 there."""
    ts = pd.Timestamp(date)
    if not s.index.min() < ts < s.index.max():
        return False
    if date == PARITY_DATE:
        return s.reindex([ts], method="nearest").iloc[0] < 1.0
    return True


def _span(s: pd.Series) -> str:
    return f"{s.index.min():%b %Y} to last observation {s.index.max():%d %b %Y}"


def _save(fig, out_dir: Path, name: str) -> Path:
    out = Path(out_dir) / name
    fig.tight_layout()
    fig.savefig(out, dpi=150)
    plt.close(fig)
    return out


def story_chart(df, out_dir):
    usd = df["USD"].dropna()
    fig, ax = plt.subplots(figsize=(11, 5.5))
    ax.plot(usd.index, usd, color=MUTED, lw=0.7, alpha=0.8,
            label="Daily ECB reference rate")
    roll = rolling_mean(usd)
    ax.plot(roll.index, roll, color=BLUE, lw=2, label="30-observation rolling mean")
    ax.axhline(1.0, color="grey", ls=":", lw=1)
    top = usd.max()
    for date, label in EVENTS.items():
        if _inside(usd, date):
            d = pd.Timestamp(date)
            y = usd.reindex([d], method="nearest").iloc[0]
            ax.annotate(label, xy=(d, y), xytext=(d, top * 1.04), ha="center",
                        fontsize=8, arrowprops=dict(arrowstyle="-", lw=0.8, color="grey"))
    ax.set_ylim(top=top * 1.2)
    ax.set_title(f"Euro against the dollar, {_span(usd)}", fontsize=13, loc="left")
    ax.set_ylabel("US dollars per euro (ECB reference rate)")
    ax.legend(frameon=False, loc="lower left")
    ax.set_xlabel("Markers give historical context, not causes.", fontsize=8,
                  color="grey", loc="right")
    style(ax)
    return _save(fig, out_dir, "eur_usd_story.png")


def volatility_chart(df, out_dir):
    usd = df["USD"].dropna()
    vol = rolling_volatility(usd)
    fig, ax = plt.subplots(figsize=(11, 4.2))
    ax.plot(vol.index, vol, lw=1.4, color=BLUE)
    for date in EVENTS:
        if _inside(vol.dropna(), date):
            ax.axvline(pd.Timestamp(date), color="grey", lw=0.7, alpha=0.6)
            ax.text(pd.Timestamp(date), 1.0, SHORT[date], transform=ax.get_xaxis_transform(),
                    rotation=90, va="top", ha="right", fontsize=7, color="grey")
    ax.set_ylabel("% per year")
    ax.set_title("EUR/USD 30-observation rolling volatility (annualised, sqrt(252)), "
                 f"last observation {usd.index.max():%d %b %Y}", fontsize=11, loc="left")
    style(ax)
    return _save(fig, out_dir, "eur_usd_volatility.png")


def _available(df):
    return {c: n for c, n in CURRENCIES.items() if c in df.columns}


def small_multiples(df, out_dir):
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharex=True)
    for ax, (code, name) in zip(axes.ravel(), _available(df).items()):
        s = df[code].dropna()
        ax.plot(s.index, s, lw=1.0, color=BLUE)
        ax.set_title(f"{name} ({code} per EUR)", fontsize=10, loc="left")
        style(ax)
    fig.suptitle("What one euro buys: raw ECB quotes (y-axes differ by unit)",
                 fontsize=12, x=0.02, ha="left")
    return _save(fig, out_dir, "small_multiples.png")


def rebased_panel(df, out_dir):
    cols = list(_available(df))
    reb = rebase_to_100(df[cols])
    fig, ax = plt.subplots(figsize=(11, 5.2))
    for c in cols:
        ax.plot(reb.index, reb[c], lw=1.2, label=c)
        ax.annotate(c, (reb.index[-1], reb[c].iloc[-1]), xytext=(4, 0),
                    textcoords="offset points", fontsize=8, va="center")
    ax.axhline(100, color="grey", ls=":", lw=1)
    ax.legend(frameon=False, ncol=len(cols), loc="upper left")
    ax.set_ylabel("Index, first common date = 100")
    ax.set_title("Relative movement on common dates, rebased to 100 "
                 f"({reb.index.min():%d %b %Y} to {reb.index.max():%d %b %Y})",
                 fontsize=12, loc="left")
    style(ax)
    return _save(fig, out_dir, "rebased_panel.png")


def event_windows(df, out_dir, half_width=20):
    usd = df["USD"].dropna()
    fig, axes = plt.subplots(2, 2, figsize=(11, 6.5), sharey=False)
    for ax, date in zip(axes.ravel(), EVENTS):
        style(ax)
        ax.set_title(f"{SHORT[date]} ({date})", fontsize=9, loc="left")
        if not _inside(usd, date):
            ax.set_xticks([]); ax.set_yticks([])
            ax.text(0.5, 0.5, "not applicable to this data (outside range, or series not below $1)", transform=ax.transAxes,
                    ha="center", color="grey")
            continue
        w = event_window(usd, date, half_width)
        ax.plot(w.index, w, color=BLUE, lw=1.4)
        ax.axvline(0, color="grey", lw=0.8)
        ax.axhline(100, color="grey", ls=":", lw=0.8)
    fig.suptitle(f"Descriptive +/-{half_width}-observation EUR/USD windows, rebased to 100 "
                 "at the nearest observation (not causal event studies)",
                 fontsize=10, x=0.02, ha="left")
    return _save(fig, out_dir, "event_windows.png")


def generate_all(csv_path, out_dir=FIGURES):
    df = load_rates(csv_path)
    if "USD" not in df.columns:
        raise ValueError("the CSV needs a USD column")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = [f(df, out_dir) for f in (story_chart, volatility_chart, small_multiples,
                                      rebased_panel, event_windows)]
    print(f"Last observation: {last_observation_date(df):%Y-%m-%d}")
    return paths


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default=ROOT / "data" / "raw" / "eurofxref-hist.csv")
    ap.add_argument("--out", default=FIGURES)
    args = ap.parse_args()
    for p in generate_all(Path(args.csv), Path(args.out)):
        print(f"Saved -> {p}")


if __name__ == "__main__":
    main()
