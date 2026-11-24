-- Q2. How do sales support agents compare after accounting for portfolio size?
-- Raw revenue can favour an agent simply because they manage more customers, so
-- report both total sales and sales per assigned customer.
WITH agent_sales AS (
    SELECT
        e.EmployeeId,
        e.FirstName || ' ' || e.LastName AS agent,
        e.HireDate AS hire_date,
        COUNT(DISTINCT c.CustomerId) AS customers,
        SUM(i.Total) AS total_sales
    FROM Employee e
    JOIN Customer c ON c.SupportRepId = e.EmployeeId
    JOIN Invoice i ON i.CustomerId = c.CustomerId
    GROUP BY e.EmployeeId, e.FirstName, e.LastName, e.HireDate
),
totals AS (
    SELECT SUM(total_sales) AS all_sales
    FROM agent_sales
)
SELECT
    a.agent,
    a.hire_date,
    a.customers,
    ROUND(a.total_sales, 2) AS total_sales,
    ROUND(a.total_sales / a.customers, 2) AS sales_per_customer,
    ROUND(100.0 * a.total_sales / t.all_sales, 2) AS revenue_share_pct
FROM agent_sales a
CROSS JOIN totals t
ORDER BY total_sales DESC;
