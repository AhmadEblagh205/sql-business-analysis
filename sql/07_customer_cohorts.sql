-- Q7. Cohort repeat-purchase activity by exact month offset.
--
-- A customer belongs to the month of their first purchase.  For each eligible
-- month offset, report the share of that cohort with at least one invoice in
-- exactly that month.  This is PERIOD ACTIVITY, not survival-style retention:
-- a customer can be inactive at month 2 and active again at month 3.
--
-- The recursive offset spine deliberately materialises zero-activity months so
-- charts do not connect across missing periods and make activity look continuous.
WITH RECURSIVE
monthly_activity AS (
    SELECT DISTINCT
        CustomerId,
        strftime('%Y-%m', InvoiceDate) AS activity_month
    FROM Invoice
),
tagged AS (
    SELECT
        CustomerId,
        activity_month,
        MIN(activity_month) OVER (PARTITION BY CustomerId) AS cohort
    FROM monthly_activity
),
activity AS (
    SELECT
        CustomerId,
        cohort,
        activity_month,
        (CAST(substr(activity_month, 1, 4) AS INTEGER)
         - CAST(substr(cohort, 1, 4) AS INTEGER)) * 12
        + (CAST(substr(activity_month, 6, 2) AS INTEGER)
         - CAST(substr(cohort, 6, 2) AS INTEGER)) AS month_offset
    FROM tagged
),
cohort_sizes AS (
    SELECT cohort, COUNT(DISTINCT CustomerId) AS cohort_size
    FROM activity
    WHERE month_offset = 0
    GROUP BY cohort
),
bounds AS (
    SELECT
        MIN(cohort) AS min_cohort,
        MAX(activity_month) AS max_month,
        (CAST(substr(MAX(activity_month), 1, 4) AS INTEGER)
         - CAST(substr(MIN(cohort), 1, 4) AS INTEGER)) * 12
        + (CAST(substr(MAX(activity_month), 6, 2) AS INTEGER)
         - CAST(substr(MIN(cohort), 6, 2) AS INTEGER)) AS max_offset
    FROM activity
),
offsets(month_offset) AS (
    SELECT 0
    UNION ALL
    SELECT month_offset + 1
    FROM offsets, bounds
    WHERE month_offset < bounds.max_offset
),
eligible AS (
    SELECT
        c.cohort,
        c.cohort_size,
        o.month_offset
    FROM cohort_sizes c
    CROSS JOIN offsets o
    CROSS JOIN bounds b
    WHERE date(c.cohort || '-01', '+' || o.month_offset || ' months')
          <= date(b.max_month || '-01')
),
active AS (
    SELECT
        cohort,
        month_offset,
        COUNT(DISTINCT CustomerId) AS active_customers
    FROM activity
    GROUP BY cohort, month_offset
)
SELECT
    e.cohort,
    e.month_offset,
    e.cohort_size,
    COALESCE(a.active_customers, 0) AS active_customers,
    ROUND(100.0 * COALESCE(a.active_customers, 0) / e.cohort_size, 1)
        AS activity_pct
FROM eligible e
LEFT JOIN active a
  ON a.cohort = e.cohort
 AND a.month_offset = e.month_offset
ORDER BY e.cohort, e.month_offset;
