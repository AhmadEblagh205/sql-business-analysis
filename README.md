# SQL Business Analysis: Chinook Music Store

[![CI](https://github.com/AhmadEblagh205/sql-business-analysis/actions/workflows/ci.yml/badge.svg)](https://github.com/AhmadEblagh205/sql-business-analysis/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

This is a SQL analysis of the [Chinook 1.4.5](https://github.com/lerocha/chinook-database) sample database. I wrote eight queries using joins, CTEs, window functions and a recursive cohort spine, and a small Python runner that exports the reports and figures. Chinook is a demonstration database. Its upstream documentation describes the customer and employee records as fictitious and the sales history as auto-generated, so the findings show method and not real commercial performance.

## What it does

The eight queries ask the following questions.

1. Which genres account for the most US track sales?
2. How do support agents compare on total revenue and on revenue per assigned customer?
3. How does revenue vary by country when one-customer markets are grouped as `Other`?
4. Do invoices contain complete albums or individual tracks?
5. How does monthly revenue change across the sample period?
6. Which countries earn more per customer than the store average, and how concentrated is that revenue?
7. What does repeat-purchase activity look like by first-purchase cohort?
8. What is the pooled repeat-purchase curve once newer, right-censored cohorts are accounted for?

## Results

These figures come from the sample database.

- Rock accounts for 31.8% of US track units.
- 99.5% of invoices are individual-track purchases, and only 2 are full-album invoices.
- Jane Peacock has the highest total sales ($833.04). Steve Johnson has the highest sales per assigned customer ($40.01, against $39.67 for Jane), so I report both measures.
- The Czech Republic has the highest country value index (1.14) among markets with at least two customers. It has only two customers and its top customer gives 55% of its revenue.
- I treat cohort retention as exact-month repeat-purchase activity. The pooled sample is active in 30.5% of customers in month 1 and 37.3% in month 3. The curve can rise because a customer may skip a month and come back.

![Cohort activity heatmap](reports/figures/cohort_activity_heatmap.png)

![Monthly revenue](reports/figures/monthly_revenue.png)

## How to run

```bash
pip install -r requirements.txt
python src/download_data.py     # pinned Chinook v1.4.5 + schema/integrity checks
python src/run_analysis.py      # runs every query, writes CSVs and figures
pytest -q
```

Each query is in its own file under `sql/`. Raw databases are git-ignored. The tests build a small in-memory Chinook-like database and check that all eight queries run. They also pin portfolio-size normalisation, zero-filled cohort months, right-censoring, album classification and monthly aggregation.

## Repository layout

```text
sql/                    eight standalone analytical queries
src/download_data.py    pinned sample-data acquisition + validation
src/run_analysis.py     query orchestration + figures
reports/                CSV outputs and figures
docs/METHODOLOGY.md     definitions, grain, caveats and test semantics
tests/                  in-memory SQL regression tests
```

## Notes

The first cohort query returned only months with a purchase, so a chart could skip over months with no activity. The current query builds every eligible month offset with a recursive CTE and joins the observed activity onto it. Definitions and query grain are in `docs/METHODOLOGY.md`.

## Licence

Project code is MIT licensed, see [LICENSE](LICENSE). Chinook data stays under the upstream project's licence.
