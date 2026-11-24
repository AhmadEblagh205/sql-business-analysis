-- Q6 (my own extension beyond the guided brief).
-- Which countries punch above their weight on customer value?
-- I compare each country's share of revenue with its share of customers
-- (value index > 1 means customers there spend more than average), and add
-- a concentration check: how much of the country's revenue its single
-- biggest customer represents.
WITH per_customer AS (
    SELECT c.CustomerId, c.Country AS country, SUM(i.Total) AS spend
    FROM Customer c
    JOIN Invoice i ON i.CustomerId = c.CustomerId
    GROUP BY c.CustomerId
),
totals AS (
    SELECT SUM(spend) AS all_revenue, COUNT(*) AS all_customers
    FROM per_customer
)
SELECT
    p.country,
    COUNT(*)                                                    AS customers,
    ROUND(SUM(p.spend), 2)                                      AS revenue,
    ROUND(100.0 * SUM(p.spend) / t.all_revenue, 1)              AS revenue_share_pct,
    ROUND(100.0 * COUNT(*) / t.all_customers, 1)                AS customer_share_pct,
    ROUND((SUM(p.spend) / t.all_revenue)
        / (1.0 * COUNT(*) / t.all_customers), 2)                AS value_index,
    ROUND(100.0 * MAX(p.spend) / SUM(p.spend), 1)               AS top_customer_pct
FROM per_customer p
CROSS JOIN totals t
GROUP BY p.country
HAVING COUNT(*) >= 2
ORDER BY value_index DESC;
