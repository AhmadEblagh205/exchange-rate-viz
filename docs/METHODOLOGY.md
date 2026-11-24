# Methodology

## Quote semantics

The ECB file is wide: one `Date` column and one column per currency. I treat each currency column as **foreign-currency units per one EUR**. If `USD = 1.15`, one euro buys 1.15 US dollars, and a rising `USD` column means the euro strengthened against the dollar under this convention. The reciprocal (euros per dollar) moves in the opposite direction.

The ECB states that these are reference rates for information purposes, published on working days. I treat them as a measurement series, not as prices at which anyone could trade.

## Formulas

Let `q_t` be a quote series with observations `t = 1..n`. All windows count observations (rows), not calendar days; 30 ECB observations span roughly six calendar weeks.

- **Rolling mean (30 observations):** `m_t = (1/30) * sum_{i=0}^{29} q_{t-i}`.
- **Log return:** `r_t = log(q_t) - log(q_{t-1})`.
- **Rolling volatility (30 observations, annualised, in percent):** `100 * sqrt(252) * sd(r_{t-29..t})`, with the sample standard deviation. The factor 252 is a conventional trading-day count, not an exact number of ECB observations per year.
- **Rebasing to 100:** on the dates where every selected currency is observed, `R_t = 100 * q_t / q_{t0}`, where `t0` is the first common date.
- **Event window:** for a date `d`, take the observation nearest to `d`, call its position `p`, and show `100 * q_{p+k} / q_p` for `k = -20..20` (truncated at the ends of the data).
- **Parity helper:** `first_date_below(series, level)` returns the first observation date with a value below `level`.

### Invariance identity

For a positive constant `c`, `log(c*q_t) - log(c*q_{t-1}) = r_t`, so log returns do not depend on the quote unit. For inversion,

`delta log(1/q_t) = -delta log(q_t)`,

and the standard deviation of a series equals that of its negation. Rolling log-return volatility is therefore invariant to positive rescaling and to quote inversion. `tests/` checks both numerically, and `src/audit.py` checks them on a known-truth design.

## Scale-aware comparison

Raw levels in different currencies are not comparable measures of movement: JPY per EUR naturally sits near 100 and above, GBP per EUR near 1 or below. The standard deviation of raw levels therefore changes with the unit alone. In my audit, four series with an identical multiplicative path but starting levels 0.80, 1.20, 100 and 150 have a raw-level SD ratio of 187.5 (the ratio of the largest to the smallest start). I keep the raw small multiples for the question "what does one euro buy?", and add a common-date rebased panel and log-return volatility for the question "how did the quotes move relatively?". Rebasing removes the original level, so it never replaces the raw view when the level itself matters.

## Event annotations: context, not causes

The dated markers are historical context placed on a chart. FX rates respond to many simultaneous shocks and expectations, and I estimate no counterfactual, so co-location of a marker and a movement does not identify an effect. The +/-20-observation windows are descriptive: they show what the series did around a date, not what would have happened without the event. They are not event studies.

The 2022 parity marker is tied to the plotted measurement series. The ECB reference rate was 1.0042 on 12 July 2022, 1.0001 on 22 August and 0.9927 on 23 August, so I mark 23 August as the date the ECB reference series moved below USD 1 again. A true intraday market headline can still be wrong for the exact series on the chart.

## Snapshot provenance

The ECB file is live and mutable. `download_data.py` reuses a local file by default and says so; `--refresh` replaces it and writes `data/raw/eurofxref-hist.manifest.json` with the source URL, the UTC retrieval timestamp and the SHA-256 of the CSV. Chart titles use the last observation date actually present in the data, so a stale cache cannot be mistaken for current coverage. The committed figures come from a deterministic synthetic sample, not from ECB data.

## References

- European Central Bank, euro foreign exchange reference rates: https://www.ecb.europa.eu/stats/policy_and_exchange_rates/euro_reference_exchange_rates/html/index.en.html
- European Central Bank, monetary policy decisions of 5 June 2014 (negative deposit facility rate, effective 11 June 2014): https://www.ecb.europa.eu/press/pr/date/2014/html/pr140605_2.en.html
- World Health Organization, opening remarks of 11 March 2020 characterising COVID-19 as a pandemic: https://www.who.int/director-general/speeches/detail/who-director-general-s-opening-remarks-at-the-media-briefing-on-covid-19---11-march-2020
