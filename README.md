# 🇲🇾 Malaysia Power SQL Lab ⚡

A hands-on SQL data warehousing project built to model Malaysia’s electricity system.
This repo simulates a full analytics workflow: designing a warehouse schema, creating dimension + fact tables, seeding them with realistic generation and fuel-price data, and building enriched SQL views for CO₂, fuel mix, and regional insights.

The goal is to mirror what real energy analysts, data engineers, and SQL developers do — but in a lightweight, fully local environment using SQLite + DBCODE notebooks.
Everything is structured so you can open the project, run it instantly, and explore Malaysia’s power grid through clean, well-organised SQL.

---

## 📦 What This Repo Contains

**1. `schema.dbcode`**
Full DDL: table creation for all dimensions + fact tables.

**2. `seed.dbcode`**
Fake-but-realistic seed data for Jan–Jun 2024 (generation, fuel prices, emission factors).

**3. `views.dbcode`**
Enriched fact views joining all dimensions, plus analytic-ready wide tables.

**4. `analysis.dbcode`**
SQL analysis examples: emissions by region, fuel mix, CO₂, generation insights, etc.

**5. `malaysia_power.db`** *(optional)*
The compiled SQLite database (useful for recruiters who want to inspect tables manually).

---

## 🧱 Tech Stack

* **SQLite** (lightweight DB engine)
* **VS Code** + **DBCODE Notebooks**
* **SQL** (CTEs, joins, views, warehouse structure)


---

## 🚀 How to Use

### 1. Clone the repo

```bash
git clone https://github.com/WhatWouldWeezyDo/Malaysia-power-sql-lab.git
```

### 2. Open in VS Code

Install the **DBCODE** extension (free).
Open the folder.

### 3. Run notebooks

Open `malaysia_power.db` and run **any `.dbcode` notebook**.
Everything works out of the box — schema → seed → views → analytics.

---

## 📊 Future Improvements

These are optional extensions for later:

* Replace fake data with **real MEIH datasets**
* Add a **renewables breakdown**
* Add **demand** tables + peak/off-peak modelling
* Build a simple **ETL script** (Python)
* Add a **Grafana or PowerBI dashboard**

---

## 👤 Author

Built by **Prabaveer Singh**
Mechanical engineer exploring energy systems, data modelling, and SQL development.

---


