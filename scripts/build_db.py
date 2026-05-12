#!/usr/bin/env python3
"""Build malaysia_power.db deterministically from the committed Ember source slice.

Source of truth: data/sources/ember_malaysia_monthly.csv -- a Malaysia-only slice
(2018-01 .. 2025-12) of Ember's "Monthly Electricity Data" long-format release.
See data/sources/SOURCES.md for provenance and licence.

Run from the repo root:  python scripts/build_db.py
"""
from __future__ import annotations

import csv
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "data" / "sources" / "ember_malaysia_monthly.csv"
DB = ROOT / "malaysia_power.db"

# Ember's six "Fuel" buckets, in display order, with fixed ids.
FUELS = [(1, "Coal"), (2, "Gas"), (3, "Hydro"), (4, "Solar"), (5, "Bioenergy"), (6, "Other Fossil")]
FUEL_ID = {name: fid for fid, name in FUELS}

DDL = """
DROP TABLE IF EXISTS fact_summary_monthly;
DROP TABLE IF EXISTS fact_demand_monthly;
DROP TABLE IF EXISTS fact_emissions_monthly;
DROP TABLE IF EXISTS fact_generation_monthly;
DROP TABLE IF EXISTS dim_fuel;
DROP TABLE IF EXISTS dim_month;

CREATE TABLE dim_month (
    month_id    INTEGER PRIMARY KEY,           -- YYYYMM
    year        INTEGER NOT NULL,
    month       INTEGER NOT NULL CHECK (month BETWEEN 1 AND 12),
    month_start TEXT    NOT NULL                -- 'YYYY-MM-01'
);

CREATE TABLE dim_fuel (
    fuel_id   INTEGER PRIMARY KEY,
    fuel_name TEXT NOT NULL UNIQUE
);

CREATE TABLE fact_generation_monthly (
    month_id  INTEGER NOT NULL,
    fuel_id   INTEGER NOT NULL,
    twh       REAL    NOT NULL CHECK (twh >= 0),
    share_pct REAL    NOT NULL CHECK (share_pct >= 0),
    PRIMARY KEY (month_id, fuel_id),
    FOREIGN KEY (month_id) REFERENCES dim_month(month_id),
    FOREIGN KEY (fuel_id)  REFERENCES dim_fuel(fuel_id)
);

CREATE TABLE fact_emissions_monthly (
    month_id INTEGER NOT NULL,
    fuel_id  INTEGER NOT NULL,
    mtco2    REAL    NOT NULL CHECK (mtco2 >= 0),
    PRIMARY KEY (month_id, fuel_id),
    FOREIGN KEY (month_id) REFERENCES dim_month(month_id),
    FOREIGN KEY (fuel_id)  REFERENCES dim_fuel(fuel_id)
);

CREATE TABLE fact_demand_monthly (
    month_id        INTEGER PRIMARY KEY,
    demand_twh      REAL NOT NULL CHECK (demand_twh >= 0),
    net_imports_twh REAL NOT NULL,
    FOREIGN KEY (month_id) REFERENCES dim_month(month_id)
);

-- Ember's own reported totals/intensity, kept verbatim as a cross-check.
CREATE TABLE fact_summary_monthly (
    month_id                INTEGER PRIMARY KEY,
    total_gen_twh           REAL NOT NULL CHECK (total_gen_twh >= 0),
    total_emissions_mtco2   REAL NOT NULL CHECK (total_emissions_mtco2 >= 0),
    co2_intensity_g_per_kwh REAL NOT NULL CHECK (co2_intensity_g_per_kwh >= 0),
    FOREIGN KEY (month_id) REFERENCES dim_month(month_id)
);

CREATE INDEX idx_gen_month  ON fact_generation_monthly(month_id);
CREATE INDEX idx_gen_fuel   ON fact_generation_monthly(fuel_id);
CREATE INDEX idx_emis_month ON fact_emissions_monthly(month_id);
CREATE INDEX idx_emis_fuel  ON fact_emissions_monthly(fuel_id);

-- analytical views
CREATE VIEW v_generation_enriched AS
SELECT m.year, m.month, m.month_start, f.fuel_name,
       g.twh, g.share_pct, e.mtco2
FROM fact_generation_monthly g
JOIN dim_month m USING(month_id)
JOIN dim_fuel  f USING(fuel_id)
JOIN fact_emissions_monthly e USING(month_id, fuel_id);

CREATE VIEW v_fuel_mix AS
SELECT year, month, month_start, fuel_name, twh,
       ROUND(100.0 * twh / SUM(twh) OVER (PARTITION BY year, month), 2) AS pct_mix
FROM v_generation_enriched;

CREATE VIEW v_monthly_emissions AS
SELECT m.year, m.month, m.month_start,
       s.total_gen_twh, s.total_emissions_mtco2, s.co2_intensity_g_per_kwh
FROM fact_summary_monthly s JOIN dim_month m USING(month_id);

CREATE VIEW v_annual AS
SELECT m.year,
       SUM(s.total_gen_twh)         AS gen_twh,
       SUM(s.total_emissions_mtco2) AS emissions_mtco2,
       1000.0 * SUM(s.total_emissions_mtco2) / SUM(s.total_gen_twh) AS co2_intensity_g_per_kwh
FROM fact_summary_monthly s JOIN dim_month m USING(month_id)
GROUP BY m.year;

CREATE VIEW v_implied_emission_factor AS
SELECT f.fuel_name,
       ROUND(SUM(e.mtco2) / NULLIF(SUM(g.twh), 0), 4) AS tco2_per_mwh
FROM fact_emissions_monthly e
JOIN fact_generation_monthly g USING(month_id, fuel_id)
JOIN dim_fuel f USING(fuel_id)
GROUP BY f.fuel_name;
"""


def _key(row: dict) -> tuple[str, str, str, str]:
    return (row["Category"], row["Subcategory"], row["Variable"], row["Unit"])


def load_source() -> list[dict]:
    if not SRC.exists():
        sys.exit(f"missing source slice: {SRC}\n(regenerate it from Ember's monthly release -- see SOURCES.md)")
    with SRC.open() as fh:
        rows = list(csv.DictReader(fh))
    assert rows, "source slice is empty"
    assert all(r["Area"] == "Malaysia" for r in rows), "source slice contains non-Malaysia rows"
    return rows


def build() -> None:
    rows = load_source()

    months = sorted({r["Date"] for r in rows})
    assert len(months) == 96, f"expected 96 months, got {len(months)}"
    assert months[0] == "2018-01-01" and months[-1] == "2025-12-01", (months[0], months[-1])
    month_id = {d: int(d[:4]) * 100 + int(d[5:7]) for d in months}

    # index by (key, date) -> float value
    val: dict[tuple, dict[str, float]] = {}
    for r in rows:
        v = r["Value"].strip()
        if v in ("", "nan", "NaN"):
            continue
        val.setdefault(_key(r), {})[r["Date"]] = float(v)

    def series(cat, sub, var, unit) -> dict[str, float]:
        s = val.get((cat, sub, var, unit))
        assert s is not None, f"missing series: {cat} / {sub} / {var} / {unit}"
        missing = [d for d in months if d not in s]
        assert not missing, f"series {var} ({unit}) missing months: {missing[:3]}..."
        return s

    gen = {name: series("Electricity generation", "Fuel", name, "TWh") for _, name in FUELS}
    gen_pct = {name: series("Electricity generation", "Fuel", name, "%") for _, name in FUELS}
    emis = {name: series("Power sector emissions", "Fuel", name, "mtCO2") for _, name in FUELS}
    demand = series("Electricity demand", "Demand", "Demand", "TWh")
    net_imp = series("Electricity imports", "Electricity imports", "Net Imports", "TWh")
    tot_gen = series("Electricity generation", "Total", "Total Generation", "TWh")
    tot_emis = series("Power sector emissions", "Total", "Total emissions", "mtCO2")
    intensity = series("Power sector emissions", "CO2 intensity", "CO2 intensity", "gCO2/kWh")

    # --- reconciliation checks against Ember's own reported totals ---
    for d in months:
        sg = sum(gen[name][d] for _, name in FUELS)
        se = sum(emis[name][d] for _, name in FUELS)
        assert abs(sg - tot_gen[d]) <= 0.02 * max(tot_gen[d], 1), f"{d}: gen sum {sg:.3f} vs reported {tot_gen[d]:.3f}"
        assert abs(se - tot_emis[d]) <= 0.02 * max(tot_emis[d], 1), f"{d}: emis sum {se:.3f} vs reported {tot_emis[d]:.3f}"
        implied_i = (tot_emis[d] / tot_gen[d]) * 1000.0  # mtCO2/TWh -> gCO2/kWh
        assert abs(implied_i - intensity[d]) <= 2.0, f"{d}: implied intensity {implied_i:.1f} vs reported {intensity[d]:.1f}"
        sp = sum(gen_pct[name][d] for _, name in FUELS)
        assert abs(sp - 100.0) <= 0.5, f"{d}: fuel shares sum to {sp:.2f}%"

    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(DDL)
    con.executemany("INSERT INTO dim_fuel(fuel_id, fuel_name) VALUES (?, ?)", FUELS)
    con.executemany(
        "INSERT INTO dim_month(month_id, year, month, month_start) VALUES (?, ?, ?, ?)",
        [(month_id[d], int(d[:4]), int(d[5:7]), d) for d in months],
    )
    con.executemany(
        "INSERT INTO fact_generation_monthly(month_id, fuel_id, twh, share_pct) VALUES (?, ?, ?, ?)",
        [(month_id[d], FUEL_ID[name], gen[name][d], gen_pct[name][d]) for d in months for _, name in FUELS],
    )
    con.executemany(
        "INSERT INTO fact_emissions_monthly(month_id, fuel_id, mtco2) VALUES (?, ?, ?)",
        [(month_id[d], FUEL_ID[name], emis[name][d]) for d in months for _, name in FUELS],
    )
    con.executemany(
        "INSERT INTO fact_demand_monthly(month_id, demand_twh, net_imports_twh) VALUES (?, ?, ?)",
        [(month_id[d], demand[d], net_imp[d]) for d in months],
    )
    con.executemany(
        "INSERT INTO fact_summary_monthly(month_id, total_gen_twh, total_emissions_mtco2, co2_intensity_g_per_kwh) VALUES (?, ?, ?, ?)",
        [(month_id[d], tot_gen[d], tot_emis[d], intensity[d]) for d in months],
    )
    con.commit()

    n_gen = con.execute("SELECT COUNT(*) FROM fact_generation_monthly").fetchone()[0]
    yrs = con.execute("SELECT MIN(year), MAX(year) FROM dim_month").fetchone()
    con.close()
    assert n_gen == 96 * 6, n_gen
    print(f"built {DB.name}: 96 months ({yrs[0]}-{yrs[1]}), 6 fuels, {n_gen} generation rows; reconciliation checks passed.")


if __name__ == "__main__":
    build()
