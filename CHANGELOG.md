# Changelog

## 0.3.0 — defensibility audit
- Corrected every "30-day" label to "30-observation": `rolling(30)` counts rows, and ECB observations are working days. Documented `sqrt(252)` as a convention.
- Corrected the 2022 parity annotation: the ECB reference was 1.0042 on 12 July 2022, 1.0001 on 22 August and 0.9927 on 23 August, so the chart now marks 23 August.
- Reworded event annotations as context markers, not explanations; added descriptive +/-20-observation event windows rebased to 100.
- Added a common-date rebased-to-100 panel next to the raw small multiples (five chart types, up from three).
- Added `src/data.py` with strict loader validation and `src/analysis.py` with the rolling and rebasing helpers.
- Downloader: cache reuse is explicit, `--refresh` replaces the snapshot and writes a UTC timestamp and SHA-256 manifest.
- Chart titles use the actual last observation date, never "today".
- Added `src/audit.py`: a deterministic known-truth unit-scale audit (187.5x raw SD ratio, scale-free after rebasing and log returns) and a synthetic sample CSV for offline runs.
- Added `docs/METHODOLOGY.md`; expanded the tests from 3 to 26, all offline.

## 0.2.0, update round 4
Added a rolling 30 day annualised volatility companion chart with the same event markers as the story chart, so 2008 and 2020 read as volatility events first.

## 0.1.0
Initial release.
