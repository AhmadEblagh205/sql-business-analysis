-- Q4. What share of purchases are whole albums vs individual tracks?
-- An invoice counts as an album purchase when every track on it comes from
-- one album AND the invoice contains that album's full track list.
WITH invoice_tracks AS (
    SELECT il.InvoiceId, t.TrackId, t.AlbumId
    FROM InvoiceLine il
    JOIN Track t ON t.TrackId = il.TrackId
),
per_invoice AS (
    SELECT
        InvoiceId,
        COUNT(DISTINCT AlbumId) AS n_albums,
        COUNT(DISTINCT TrackId) AS n_tracks,
        MIN(AlbumId)            AS the_album
    FROM invoice_tracks
    GROUP BY InvoiceId
),
album_sizes AS (
    SELECT AlbumId, COUNT(*) AS album_tracks
    FROM Track
    GROUP BY AlbumId
)
SELECT
    CASE WHEN p.n_albums = 1 AND p.n_tracks = a.album_tracks
         THEN 'full album' ELSE 'individual tracks' END   AS purchase_type,
    COUNT(*)                                              AS invoices,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM Invoice), 2) AS pct
FROM per_invoice p
JOIN album_sizes a ON a.AlbumId = p.the_album
GROUP BY purchase_type;
