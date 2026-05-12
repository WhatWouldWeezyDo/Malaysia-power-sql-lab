# Data load

There are no hand-written `INSERT` statements in this project. The database is built
deterministically from the committed source slice:

```
python scripts/build_db.py
```

That script reads `data/sources/ember_malaysia_monthly.csv` (a Malaysia-only slice of
Ember's *Monthly Electricity Data*, 2018-01 … 2025-12 — see `data/sources/SOURCES.md`),
creates the schema (mirrors `sql/ddl/schema.dbcode`) and the views (`sql/views/views.dbcode`),
loads the data, and runs reconciliation checks against Ember's own reported totals.
