-- Q8. Pooled cohort activity curve.
--
-- Aggregate the dense cohort table logic across all cohorts that have had time
-- to reach a given month offset.  The denominator therefore contains only
-- eligible cohorts at each horizon, avoiding right-censoring from newer cohorts.
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
        MAX(activity_month) AS max_month,
        MIN(cohort) AS min_cohort,
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
),
dense AS (
    SELECT
        e.cohort,
        e.month_offset,
        e.cohort_size,
        COALESCE(a.active_customers, 0) AS active_customers
    FROM eligible e
    LEFT JOIN active a
      ON a.cohort = e.cohort
     AND a.month_offset = e.month_offset
)
SELECT
    month_offset,
    COUNT(*) AS eligible_cohorts,
    SUM(cohort_size) AS eligible_customers,
    SUM(active_customers) AS active_customers,
    ROUND(100.0 * SUM(active_customers) / SUM(cohort_size), 1)
        AS pooled_activity_pct
FROM dense
GROUP BY month_offset
ORDER BY month_offset;
