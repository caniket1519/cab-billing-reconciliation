-- Q2. Cab-number mismatches between the KM log and the client MIS.
-- A different cab number on the same route usually means a replacement cab
-- or a typing error; both must be fixed before the client invoice goes out.

WITH log_cabs AS (
    SELECT DISTINCT route_id, cab_no FROM trip_log
)
SELECT
    r.city,
    r.route_id,
    r.area,
    l.cab_no  AS cab_in_km_log,
    c.cab_no  AS cab_in_client_mis
FROM log_cabs l
FULL OUTER JOIN client_mis c ON c.route_id = l.route_id
JOIN routes r ON r.route_id = COALESCE(l.route_id, c.route_id)
WHERE l.cab_no IS NULL
   OR c.cab_no IS NULL
   OR l.cab_no <> c.cab_no
ORDER BY r.city, r.route_id;
