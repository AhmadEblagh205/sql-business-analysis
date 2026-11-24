-- Q1. Which genres sell best in the USA?
-- (Used in the original brief to decide which new artists to sign.)
SELECT
    g.Name                                        AS genre,
    SUM(il.Quantity)                              AS tracks_sold,
    ROUND(100.0 * SUM(il.Quantity) / (
        SELECT SUM(il2.Quantity)
        FROM InvoiceLine il2
        JOIN Invoice i2 ON i2.InvoiceId = il2.InvoiceId
        WHERE i2.BillingCountry = 'USA'
    ), 2)                                         AS pct_of_us_sales
FROM InvoiceLine il
JOIN Invoice i ON i.InvoiceId = il.InvoiceId
JOIN Track   t ON t.TrackId   = il.TrackId
JOIN Genre   g ON g.GenreId   = t.GenreId
WHERE i.BillingCountry = 'USA'
GROUP BY g.Name
ORDER BY tracks_sold DESC;
