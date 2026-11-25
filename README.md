# ECB Exchange-Rate Storytelling & Scale-Aware Comparison

[![CI](https://github.com/AhmadEblagh205/exchange-rate-viz/actions/workflows/ci.yml/badge.svg)](https://github.com/AhmadEblagh205/exchange-rate-viz/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

This began as a guided Dataquest project. The code here is my independent Python rebuild and audit of it. I turn the European Central Bank's euro reference-rate history into five charts. Version 0.3 is my audit of the earlier version, where I checked each chart label against what the code and data support and fixed the ones that did not match.

## What it does

- Draws an annotated EUR/USD chart and a rolling volatility chart.
- Draws raw small multiples for several currencies, and a common-date panel rebased to 100.
- Draws descriptive event windows of 20 observations either side of a date, rebased to 100.
- Downloads the ECB file, or refreshes it and writes a manifest with the source URL, retrieval time and SHA-256.
- Runs a unit-scale check on synthetic data.

## Results

The data are the ECB's public euro reference rates. They are published for information, so they are reference rates and not prices anyone could trade at. Every currency column is foreign-currency units per one euro.

The unit-scale check uses 500 synthetic working-day observations, not ECB data. Four series share one multiplicative path and start at 0.80, 1.20, 100 and 150. Their raw level standard deviations differ by a factor of 187.5, purely because of units. After rebasing to 100 the paths agree to 2.84e-14 index points, and the mean annualised 30-observation volatility is 9.6145% for every series. The differences are floating-point noise. The output is in `reports/audit_summary.json`.

## How to run

```bash
pip install -r requirements.txt
python src/download_data.py             # reuses the local snapshot if present, and says so
python src/download_data.py --refresh   # replaces it and writes data/raw/eurofxref-hist.manifest.json
python src/visualize.py                 # five charts to reports/figures/
python src/audit.py                     # unit-scale audit and the synthetic sample CSV
pytest
```

To run offline, use the bundled synthetic sample:

```bash
python src/visualize.py --csv data/sample/synthetic_eurofxref_sample.csv
```

The figures committed in `reports/figures/` come from that synthetic sample (see `reports/figures/README.md`). Real-data figures regenerate after `download_data.py --refresh`. The tests are 26 offline tests with no network, and CI runs them on every push.

## Notes

Windows count observations, not calendar days, so 30 observations is roughly six calendar weeks. The markers on the charts are context and do not identify causes. A local ECB file is a snapshot and is only current if I have run `--refresh`. The audit changes, the formulas and the audit table are in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Licence

MIT, see [LICENSE](LICENSE). Data: European Central Bank reference rates.
