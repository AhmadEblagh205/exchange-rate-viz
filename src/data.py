"""Loader and validation for the ECB wide-format reference-rate CSV.

Quote convention: every currency column holds foreign-currency units per
one EUR. A value of USD = 1.15 means EUR 1 buys USD 1.15, so a rising USD
column means the euro buys more dollars. The ECB publishes these as
information-purpose reference rates, not as executable transaction prices.

The loader is strict about structure and lenient only about the ECB's own
missing-value markers ("-", "N/A" and empty cells).
"""
import csv

import numpy as np
import pandas as pd

MISSING = {"", "-", "N/A"}


class DataError(ValueError):
    """Raised when a rate file does not satisfy the expected structure."""


def load_rates(path) -> pd.DataFrame:
    """Return a Date-indexed (ascending) float frame of units per EUR."""
    with open(path, newline="", encoding="utf-8-sig") as fh:
        rows = [r for r in csv.reader(fh) if any(c.strip() for c in r)]
    if not rows:
        raise DataError("file is empty")

    header = [h.strip() for h in rows[0]]
    if "Date" not in header:
        raise DataError("missing 'Date' column")
    keep = [i for i, h in enumerate(header) if h]  # drops the trailing empty column
    names = [header[i] for i in keep]
    dupes = sorted({n for n in names if names.count(n) > 1})
    if dupes:
        raise DataError(f"duplicate column names: {dupes}")
    currencies = [n for n in names if n != "Date"]
    if not currencies:
        raise DataError("no currency columns")

    dates, values = [], []
    for line_no, row in enumerate(rows[1:], start=2):
        cells = {names[k]: (row[i].strip() if i < len(row) else "")
                 for k, i in enumerate(keep)}
        try:
            dates.append(pd.to_datetime(cells["Date"], format="%Y-%m-%d"))
        except (ValueError, TypeError) as exc:
            raise DataError(f"line {line_no}: unparseable date "
                            f"{cells['Date']!r}") from exc
        out = []
        for cur in currencies:
            raw = cells[cur]
            if raw in MISSING:
                out.append(np.nan)
                continue
            try:
                val = float(raw)
            except ValueError as exc:
                raise DataError(f"line {line_no}: non-numeric rate "
                                f"{raw!r} in {cur}") from exc
            if not np.isfinite(val) or val <= 0:
                raise DataError(f"line {line_no}: rate {raw!r} in {cur} "
                                "is not a positive finite number")
            out.append(val)
        values.append(out)

    index = pd.DatetimeIndex(dates, name="Date")
    if index.has_duplicates:
        raise DataError(f"duplicate dates: {sorted(set(index[index.duplicated()]))[:3]}")
    return pd.DataFrame(values, index=index, columns=currencies).sort_index()


load = load_rates
