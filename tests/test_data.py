import pandas as pd
import pytest

from data import DataError, load_rates


def write(tmp_path, text):
    p = tmp_path / "rates.csv"
    p.write_text(text)
    return p


def test_dashes_and_na_are_missing(tmp_path):
    df = load_rates(write(tmp_path, "Date,USD,GBP\n1999-01-04,1.18,0.70\n"
                                    "1999-01-05,-,0.71\n1999-01-06,1.17,N/A\n"))
    assert pd.isna(df.loc["1999-01-05", "USD"])
    assert pd.isna(df.loc["1999-01-06", "GBP"])


def test_dates_sorted_ascending(tmp_path):
    df = load_rates(write(tmp_path, "Date,USD\n2020-01-03,1.1\n2020-01-02,1.2\n"))
    assert df.index.is_monotonic_increasing


def test_trailing_empty_column_ignored(tmp_path):
    df = load_rates(write(tmp_path, "Date,USD,\n2020-01-02,1.1,\n2020-01-03,1.2,\n"))
    assert list(df.columns) == ["USD"]


def test_duplicate_column_rejected(tmp_path):
    with pytest.raises(DataError, match="duplicate column"):
        load_rates(write(tmp_path, "Date,USD,USD\n2020-01-02,1.1,1.1\n"))


def test_duplicate_date_rejected(tmp_path):
    with pytest.raises(DataError, match="duplicate dates"):
        load_rates(write(tmp_path, "Date,USD\n2020-01-02,1.1\n2020-01-02,1.2\n"))


def test_invalid_date_rejected(tmp_path):
    with pytest.raises(DataError, match="unparseable date"):
        load_rates(write(tmp_path, "Date,USD\nnot-a-date,1.1\n"))


def test_missing_date_column_rejected(tmp_path):
    with pytest.raises(DataError, match="Date"):
        load_rates(write(tmp_path, "Day,USD\n2020-01-02,1.1\n"))


def test_non_numeric_rate_rejected(tmp_path):
    with pytest.raises(DataError, match="non-numeric"):
        load_rates(write(tmp_path, "Date,USD\n2020-01-02,abc\n"))


@pytest.mark.parametrize("bad", ["0", "-1.5"])
def test_zero_or_negative_rate_rejected(tmp_path, bad):
    with pytest.raises(DataError, match="positive"):
        load_rates(write(tmp_path, f"Date,USD\n2020-01-02,{bad}\n"))


def test_no_currency_columns_rejected(tmp_path):
    with pytest.raises(DataError, match="no currency"):
        load_rates(write(tmp_path, "Date,\n2020-01-02,\n"))
