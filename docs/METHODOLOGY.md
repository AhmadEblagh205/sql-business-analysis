# Methodology and query semantics

This repository is a SQL-analysis exercise built on the **Chinook 1.4.5 sample database**. It is useful for demonstrating analytical SQL, but it is not a real commercial transaction history. Upstream Chinook documentation states that customer/employee details are fictitious and the sales history is auto-generated sample data over a four-year period. The results therefore illustrate how I would answer commercial questions; they are not real-world market recommendations.

## Data grain matters

Different questions operate at different grains:

- `InvoiceLine`: units/tracks purchased.
- `Invoice`: order-level revenue and order composition.
- `Customer`: assigned support representative and customer geography.
- customer-month: cohort activity.

Several common SQL mistakes come from mixing those grains, especially double-counting customers after joining invoices to invoice lines.

## Query 02: agent performance

The original project description said performance was “normalised by hire date”, but the SQL only ranked total sales. That claim has been removed.

The revised query reports both:

- total sales; and
- sales per assigned customer.

This is a simple portfolio-size normalisation. It is **not** causal evidence that one employee is a better salesperson: customers were not randomly assigned, portfolio mix is uncontrolled, and the sample is synthetic.

## Query 04: album vs track

An invoice is labelled a full-album purchase only when:

1. every purchased track comes from a single album; and
2. the number of distinct tracks on the invoice equals the number of tracks on that album.

Everything else is classified as an individual-track purchase.

## Query 06: country value index

The value index is:

`country revenue share / country customer share`

A value above 1 means the country's customers spend more per customer than the store-wide average. It is paired with a top-customer concentration statistic because tiny markets can look attractive due to one customer.

## Queries 07–08: cohort activity

A customer's cohort is the month of their first purchase, computed with a window function. The revised query then creates a **recursive month-offset spine** so months with no purchases appear explicitly as zero rather than disappearing from the result.

The metric is the fraction of the cohort with at least one purchase in **that exact month offset**. It is therefore period activity / repeat-purchase activity, not survival-style retention. A customer can be inactive at month 2 and active again at month 3, so the curve need not be monotonic.

The pooled summary also handles right-censoring: at each offset it includes only cohorts that have had enough elapsed calendar time to reach that offset.

## Testing strategy

The tests build an in-memory miniature Chinook-like schema. All eight SQL files must execute against it. Targeted tests then pin:

- total-sales vs sales-per-customer semantics;
- explicit zero months in cohort output;
- right-censoring in pooled cohort activity;
- full-album classification; and
- monthly revenue aggregation.

The test database is deliberately small enough that expected answers can be checked by inspection.
