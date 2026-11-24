-- Q3. Sales by country, grouping single-customer countries into 'Other'.
WITH country_stats AS (
    SELECT
        c.Country                       AS country,
        COUNT(DISTINCT c.CustomerId)    AS customers,
        SUM(i.Total)                    AS total_sales,
        COUNT(DISTINCT i.InvoiceId)     AS orders
    FROM Customer c
    JOIN Invoice i ON i.CustomerId = c.CustomerId
    GROUP BY c.Country
),
labelled AS (
    SELECT
        CASE WHEN customers = 1 THEN 'Other' ELSE country END AS country,
        customers, total_sales, orders,
        CASE WHEN customers = 1 THEN 1 ELSE 0 END             AS is_other
    FROM country_stats
)
SELECT
    country,
    SUM(customers)                                   AS customers,
    ROUND(SUM(total_sales), 2)                       AS total_sales,
    ROUND(SUM(total_sales) / SUM(customers), 2)      AS sales_per_customer,
    ROUND(SUM(total_sales) / SUM(orders), 2)         AS avg_order_value
FROM labelled
GROUP BY country
ORDER BY MAX(is_other) ASC, total_sales DESC;
