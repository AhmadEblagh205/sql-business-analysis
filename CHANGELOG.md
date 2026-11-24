# Changelog

## 0.3.0 — defensibility and cohort-semantics audit

- Removed the unsupported claim that sales-agent results were normalised by hire date.
- Added sales per assigned customer and revenue share alongside raw agent totals.
- Rebuilt cohort analysis with a recursive month spine so zero-activity months are explicit.
- Reframed the cohort metric as exact-month repeat-purchase activity rather than survival-style retention.
- Added a pooled cohort-activity query that handles right-censoring of newer cohorts.
- Replaced the sparse first-five-cohort line chart with a dense cohort heatmap and pooled activity curve.
- Added pinned Chinook v1.4.5 download validation and database integrity/schema checks.
- Added methodology documentation covering query grain, cohort semantics and limitations.
- Expanded tests from 3 to a richer in-memory SQL regression suite covering all eight queries.
- Clarified that Chinook sales are auto-generated sample data, not real commercial history.

## 0.2.0 — update round 2

Added Q7, window-function cohort analysis, with a cohort figure.

## 0.1.0

Initial release.
