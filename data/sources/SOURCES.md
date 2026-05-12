# Data Sources

Every monthly figure in this project comes from one dataset: **Ember's *Monthly Electricity
Data*** (Malaysia). The database is built deterministically from a committed slice of it by
`scripts/build_db.py`; nothing is interpolated or hand-entered. A few annual reference numbers
in the README (regional Grid Emission Factors) and two carbon-price reference points are cited
in prose only — listed below.

| What | Source | URL | Accessed | Notes |
|---|---|---|---|---|
| Monthly electricity generation by fuel (Coal, Gas, Hydro, Solar, Bioenergy, Other Fossil; TWh and %), total generation, electricity demand, net imports, power-sector CO₂ by fuel + total, CO₂ intensity — Malaysia, monthly, Jan 2018 – Dec 2025 | Ember, *Monthly Electricity Data* (long-format release) | data page: https://ember-energy.org/data/monthly-electricity-data/ — bulk CSV: https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/monthly_full_release_long_format.csv | 2026-05-12 | Licence: Creative Commons Attribution 4.0 (CC-BY-4.0); cite Ember. The committed file `data/sources/ember_malaysia_monthly.csv` is the rows of that release with `Area == "Malaysia"` and `Date` in 2018-01 … 2025-12 — regenerate it by filtering the bulk CSV the same way. Ember compiles its monthly series from national and multilateral sources (EIA, Eurostat, the Energy Institute) under a published methodology (https://storage.googleapis.com/emb-prod-bkt-publicdata/public-downloads/ember_electricity_data_methodology.pdf); for countries without direct monthly fuel-level reporting the monthly split is estimated, so treat Malaysia's monthly figures as a credible reconstruction, not raw Energy Commission reporting. |
| Regional Grid Emission Factors (Peninsular Malaysia ≈ 740, Sarawak ≈ 199, Sabah ≈ 539 g CO₂/kWh, 2024) — used only in a one-line prose comparison in the README | Energy Commission of Malaysia (Suruhanjaya Tenaga) — Grid Emission Factor reporting; Sarawak cross-checked against Sarawak Energy Berhad | https://myenergystats.st.gov.my ; https://www.st.gov.my | 2026-05-12 | Published annually, by region/utility. There is no public monthly, by-fuel, by-region series — which is why this project is national and monthly rather than regional and monthly. |
| Carbon tax — projected starting rate (~RM 20/tonne CO₂e, from 2026, iron & steel + energy industries) | Government of Malaysia, Budget 2025/2026 announcements; MIDA and tax-advisory commentary | https://www.mida.gov.my/mida-news/budget-2025-govt-to-introduce-carbon-tax-on-iron-steel-and-energy-industries-by-2026/ | 2026-05-12 | **Not a gazetted rate.** The carbon tax is announced for 2026 but the per-tonne rate/scope had not been finalised as of the access date; RM 20/t is the low end of published projections (the range cited runs roughly RM 20–150/t). Used here only as an illustrative price point. |
| Carbon credit floor — RM 50/tonne CO₂e | Bursa Carbon Exchange (BCX), first Malaysian nature-based carbon credit auction (Kuamut Rainforest Conservation Project), 25 July 2024 | https://bcx.bursamalaysia.com/ ; https://theedgemalaysia.com/node/720033 | 2026-05-12 | Floor price set by the project sponsor for that auction (~US$10.70/t at the time). A voluntary-market reference point, not a market-clearing price. |

## Reproducibility status

The database is derived from a committed source file by a committed script, and `scripts/build_db.py`
runs reconciliation checks (per-fuel sums match Ember's reported totals; implied intensity matches
Ember's reported intensity) before writing the DB. The honest residual: Ember itself is downstream
of national and multilateral reporting — it is a well-documented secondary source, not the primary
Energy Commission record, and (per the note above) its monthly fuel-level split is partly estimated
for countries like Malaysia that don't publish it directly.
