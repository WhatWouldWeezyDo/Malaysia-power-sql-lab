# Data Sources

Every figure in this project traces to one of: (a) the bundled SQLite database
`malaysia_power.db`, (b) the counterfactual model in `notebooks/04_counterfactual.ipynb`,
(c) the forecast model in `notebooks/05_forecast.ipynb`, or (d) an external source listed below.

The database itself was assembled from official **annual** totals and Grid Emission
Factors; the **monthly** breakdown is interpolated with a seasonal adjustment, and the
fuel-price series is a stylised levelised-cost assumption, not a measured price feed.
That is a known limitation — see the README, Section 9.

| Data | Source | URL | Accessed | Notes |
|---|---|---|---|---|
| Annual net generation by region, 2022–2024 | Energy Commission of Malaysia (Suruhanjaya Tenaga) — Malaysia Energy Statistics / Grid Emission Factor reporting | https://myenergystats.st.gov.my | 2026-05-12 | Portal, not a single PDF; the Grid Emission Factor report is published periodically by the Commission. |
| Grid Emission Factors by region, 2022–2024 | Energy Commission of Malaysia; Sarawak figures cross-checked against Sarawak Energy Berhad disclosures | https://myenergystats.st.gov.my | 2026-05-12 | Peninsular GEF used to calibrate the Peninsular fuel mix; Sabah's official GEF (~539 kg/MWh) is higher than this model computes (~191) because the model maps Sabah's diesel/fuel-oil thermal to "Gas" — documented simplification. |
| Sarawak generation estimates | Sarawak Energy Berhad — Annual Reports | https://www.sarawakenergy.com (Investor Relations / Annual Reports) | 2026-05-12 | Used for the Sarawak hydro/gas split. |
| Carbon tax — projected starting rate (~RM 20/tonne CO2e, from 2026, iron & steel + energy industries) | Government of Malaysia, Budget 2025 / Budget 2026 announcements; reporting via MIDA and tax-advisory commentary | https://www.mida.gov.my/mida-news/budget-2025-govt-to-introduce-carbon-tax-on-iron-steel-and-energy-industries-by-2026/ ; https://www.pwc.com/my/en/perspective/esg/241121-malaysia-carbon-tax.html | 2026-05-12 | **Unverified as a final rate.** The carbon tax has been announced for 2026 but the per-tonne rate, scope and thresholds had not been gazetted as of the access date; RM 20/t is the low end of published projections (the range cited runs RM 20 to RM 150/t). Used in this project only as an illustrative price point. |
| Carbon credit floor — RM 50/tonne CO2e | Bursa Carbon Exchange (BCX), first Malaysian nature-based carbon credit auction, Kuamut Rainforest Conservation Project, 25 July 2024 | https://bcx.bursamalaysia.com/ ; https://theedgemalaysia.com/node/720033 | 2026-05-12 | Floor price set by the project sponsor for that auction (~US$10.70/t at the time). Used as a voluntary-market reference point, not a market-clearing price. |

## Reproducibility status

This is a portfolio analysis, not a production data pipeline. What is *not* yet in place:
automated pulls from the Energy Commission portal, schema validation on ingest, versioned
snapshots of source documents, and a fixed mapping from each cell in `fact_generation_monthly`
back to a specific table in a specific published report. A production version would commit the
raw source PDFs/CSVs here with checksums and download dates and derive the database from them
deterministically. It currently does not — the database is the artifact, and these citations
are the lineage as far as it goes.
