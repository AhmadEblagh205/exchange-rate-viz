"""Scale-aware time-series helpers for the exchange-rate charts.

All windows count OBSERVATIONS (rows), not calendar days: the ECB publishes
on working days, so 30 observations span roughly six calendar weeks.
"""
import numpy as np
import pandas as pd

TRADING_DAYS = 252  # annualisation convention, not an exact ECB count per year


def rolling_mean(series: pd.Series, window: int = 30) -> pd.Series:
    """30-observation rolling mean (window counts rows)."""
    return series.rolling(window).mean()


def rolling_volatility(series: pd.Series, window: int = 30) -> pd.Series:
    """Annualised rolling volatility of log changes, in percent.

    Uses a 30-observation window and the conventional sqrt(252) factor.
    Since delta log(1/q) = -delta log(q) and delta log(c*q) = delta log(q),
    the result is invariant to inversion and positive rescaling of quotes.
    """
    logret = np.log(series).diff()
    return logret.rolling(window).std() * np.sqrt(TRADING_DAYS) * 100


def rebase_to_100(frame: pd.DataFrame) -> pd.DataFrame:
    """Restrict to dates where every column is observed, then set the first
    common date to 100."""
    common = frame.dropna(how="any")
    if common.empty:
        raise ValueError("no common observation dates")
    return common / common.iloc[0] * 100


def event_window(series: pd.Series, date, half_width: int = 20) -> pd.Series:
    """Descriptive +/- half_width observation window around the observation
    nearest to `date`, rebased to 100 at that observation. The index is the
    observation offset (0 = nearest observation). Not a causal event study."""
    s = series.dropna()
    ts = pd.Timestamp(date)
    if not (s.index.min() <= ts <= s.index.max()):
        raise ValueError("date lies outside the observed range")
    pos = int(s.index.get_indexer([ts], method="nearest")[0])
    lo, hi = max(0, pos - half_width), min(len(s), pos + half_width + 1)
    out = s.iloc[lo:hi] / s.iloc[pos] * 100
    out.index = pd.Index(range(lo - pos, hi - pos), name="offset")
    return out


def first_date_below(series: pd.Series, level: float, start=None):
    """First observation date (on/after `start`) whose value is below
    `level`; None if there is none."""
    s = series.dropna()
    if start is not None:
        s = s[s.index >= pd.Timestamp(start)]
    hit = s[s < level]
    return None if hit.empty else hit.index[0]


def last_observation_date(frame: pd.DataFrame) -> pd.Timestamp:
    """Latest date with at least one observed rate."""
    return frame.dropna(how="all").index.max()
