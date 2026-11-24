import numpy as np
import pandas as pd
import pytest

from analysis import (event_window, first_date_below, last_observation_date,
                      rebase_to_100, rolling_mean, rolling_volatility)
from visualize import EVENTS


def walk(n=300, sigma=0.006, seed=0):
    rng = np.random.default_rng(seed)
    return pd.Series(np.exp(np.cumsum(rng.normal(0, sigma, n))),
                     index=pd.bdate_range("2020-01-01", periods=n))


def test_rolling_mean_counts_observations():
    s = pd.Series(np.arange(1.0, 41.0), index=pd.bdate_range("2020-01-01", periods=40))
    rm = rolling_mean(s)
    assert rm.iloc[:29].isna().all() and rm.iloc[29] == pytest.approx(15.5)


def test_volatility_positive_and_annualised():
    vol = rolling_volatility(walk()).dropna()
    assert (vol > 0).all()
    assert 5 < vol.mean() < 15  # 0.6% per observation is roughly 9.5% a year


def test_volatility_invariant_to_rescaling():
    s = walk()
    pd.testing.assert_series_equal(rolling_volatility(s), rolling_volatility(s * 123.4))


def test_volatility_invariant_to_inversion():
    s = walk()
    diff = (rolling_volatility(s) - rolling_volatility(1 / s)).abs().max()
    assert diff < 1e-9


def test_rebasing_scale_invariant():
    s = walk()
    a = rebase_to_100(pd.DataFrame({"x": s, "y": s * 0.7}))
    b = rebase_to_100(pd.DataFrame({"x": s * 150, "y": s * 0.7 * 0.8}))
    pd.testing.assert_frame_equal(a, b)
    assert (a.iloc[0] == 100).all()


def test_rebasing_uses_common_dates_only():
    idx = pd.bdate_range("2020-01-01", periods=5)
    df = pd.DataFrame({"x": [np.nan, 2, 4, 6, 8], "y": [1, 1, 2, np.nan, 4]}, index=idx)
    out = rebase_to_100(df)
    assert list(out.index) == [idx[1], idx[2], idx[4]]
    assert out.iloc[0].tolist() == [100, 100]


def test_first_date_below():
    s = pd.Series([1.2, 1.0042, 1.0001, 0.9927, 0.99],
                  index=pd.to_datetime(["2022-07-11", "2022-07-12", "2022-08-22",
                                        "2022-08-23", "2022-08-24"]))
    assert first_date_below(s, 1.0) == pd.Timestamp("2022-08-23")
    assert first_date_below(s, 0.5) is None
    assert first_date_below(s, 1.0, start="2022-08-24") == pd.Timestamp("2022-08-24")


def test_event_window_nearest_observation():
    s = walk(100)
    friday = next(d for d in s.index[40:] if d.weekday() == 4)
    saturday = friday + pd.Timedelta(days=1)  # no observation: nearest is the Friday
    w = event_window(s, saturday, half_width=20)
    assert len(w) == 41 and w.loc[0] == pytest.approx(100)
    assert w.index.min() == -20 and w.index.max() == 20
    pos = s.index.get_indexer([saturday], method="nearest")[0]
    assert w.loc[1] == pytest.approx(s.iloc[pos + 1] / s.iloc[pos] * 100)


def test_event_window_truncates_at_edges_and_rejects_outside():
    s = walk(30)
    assert event_window(s, s.index[2], 20).index.min() == -2
    with pytest.raises(ValueError):
        event_window(s, "1990-01-01")


def test_last_observation_date_summary():
    idx = pd.bdate_range("2021-03-01", periods=4)
    df = pd.DataFrame({"USD": [1, 1, 1, np.nan], "GBP": [1, 1, np.nan, np.nan]}, index=idx)
    assert last_observation_date(df) == idx[2]


def test_events_use_audited_dates():
    assert "2022-08-23" in EVENTS and "2022-07-12" not in EVENTS
    assert all("parity" not in v.lower() for v in EVENTS.values())
    assert "2014-06-05" in EVENTS
