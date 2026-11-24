-- Q5. Monthly revenue trend across the whole store.
SELECT
    STRFTIME('%Y-%m', i.InvoiceDate) AS month,
    ROUND(SUM(i.Total), 2)           AS revenue,
    COUNT(*)                         AS orders
FROM Invoice i
GROUP BY month
ORDER BY month;
