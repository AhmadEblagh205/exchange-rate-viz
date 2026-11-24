# ECB Exchange-Rate Storytelling & Scale-Aware Comparison

[![CI](https://github.com/AhmadEblagh205/exchange-rate-viz/actions/workflows/ci.yml/badge.svg)](https://github.com/AhmadEblagh205/exchange-rate-viz/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

I turned the European Central Bank's euro reference-rate history into five charts: an annotated EUR/USD story, its volatility companion, raw small multiples, a common-date rebased panel and descriptive event windows. Version 0.3 is my audit of the earlier version: I checked what each chart label actually claims against what the code and the data support, and fixed what did not match.

## Provenance

- This began as a guided Dataquest project. The code in this repository is my independent Python rebuild and audit of it.
- The data are the ECB's public euro foreign-exchange reference rates. The ECB publishes them for information purposes; they are reference rates, not executable transaction prices.
- Quote convention: every currency column is foreign-currency units per one EUR. A rising USD column means one euro buys more dollars.
- A local ECB file is a snapshot. It is only current if I have run `--refresh`, and the refresh records when and with what hash (see below).

## What changed in the audit (v0.3)

- **30-observation correction.** pandas `rolling(30)` counts rows, and the ECB publishes on working days, so my windows are 30 observations (roughly six calendar weeks), not 30 days. Every label now says so. I kept the conventional `sqrt(252)` annualisation and documented it as a convention rather than an exact count of ECB observations per year.
- **Parity annotation correction.** My old chart labelled 12 July 2022 "EUR-USD reaches parity". The ECB reference rate plotted by the project was 1.0042 USD per EUR that day. It was 1.0001 on 22 August 2022 and 0.9927 on 23 August 2022. The chart now marks 23 August as the date the plotted ECB reference series moved below USD 1 again, and it only draws that marker when the plotted data are actually below 1 on that date.
- **Context, not cause.** My earlier wording said the annotations were "the events behind the shape". A marker next to a movement does not identify a cause, so the markers are now described as context markers (Lehman, the ECB's negative deposit-rate announcement of 5 June 2014, the WHO pandemic characterisation of 11 March 2020, and the 2022 parity crossing).
- **Descriptive event windows.** I added +/-20-observation windows rebased to 100 at the nearest observation, explicitly not event studies.
- **Scale-aware rebasing.** Raw small multiples stay (they answer what one euro buys), and I added a common-date rebased-to-100 panel so relative movement is not confused with arbitrary quote units.
- **Loader validation.** `src/data.py` rejects duplicate columns, a missing Date column, unparseable or duplicate dates, non-numeric rates, zero or negative rates and files with no currency columns. ECB dashes and empty cells are treated as missing, and a trailing empty column is ignored.
- **Refresh and manifest.** Cached data are reused explicitly (and the script says so). `--refresh` replaces the local file and writes a manifest with the source URL, UTC retrieval time and SHA-256.
- **Honest titles.** Chart titles use the actual last observation date, never the word "today".

## Known-truth unit-scale audit

`src/audit.py` builds 500 synthetic working-day observations. Four quote series share exactly one multiplicative path and start at 0.80, 1.20, 100 and 150, so any properly scale-free diagnostic must agree across them. This is a controlled mathematical check, not an empirical FX result. My run (`reports/audit_summary.json`) produced:

| Check | Result |
|---|---|
| Raw level SD ratio, largest / smallest | 187.5x |
| Max spread of paths rebased to 100 | 2.84e-14 index points |
| Mean annualised 30-observation log volatility, every series | 9.6145% (all four agree to about 1e-13) |
| Max volatility spread across series (per date) | 4.26e-13 percentage points |
| Max direct-versus-reciprocal volatility difference | 2.10e-13 percentage points |

Raw level dispersion differs 187.5-fold purely because of units, while rebasing and log-return volatility are invariant to positive scale and to quote inversion, as the identity delta log(1/q) = -delta log(q) implies. The residuals are floating-point noise.

## Usage

```bash
pip install -r requirements.txt
python src/download_data.py             # reuses the local snapshot if present, and says so
python src/download_data.py --refresh   # replaces it and writes data/raw/eurofxref-hist.manifest.json
python src/visualize.py                 # five charts to reports/figures/
python src/audit.py                     # unit-scale audit and the synthetic sample CSV
```

To run fully offline, use the bundled synthetic sample:

```bash
python src/visualize.py --csv data/sample/synthetic_eurofxref_sample.csv
```

The figures committed in `reports/figures/` come from that synthetic sample (see `reports/figures/README.md`); real-data figures regenerate after `download_data.py --refresh`. Outputs: `eur_usd_story.png`, `eur_usd_volatility.png`, `small_multiples.png`, `rebased_panel.png`, `event_windows.png`. Method details are in [docs/METHODOLOGY.md](docs/METHODOLOGY.md).

## Tests

`pytest` runs 26 offline tests (no network): loader validation, rolling statistics, invariance to rescaling and inversion, rebasing, event windows, the corrected event dates, the audit's 187.5x ratio, cache reuse and refresh/manifest with an injected fake fetch, and generation of all five figures from the synthetic sample. CI runs them on every push.

## Licence

MIT, see [LICENSE](LICENSE). Data: European Central Bank reference rates.
