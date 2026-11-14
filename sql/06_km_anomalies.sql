-- Q6. KM entries far above a route's normal daily distance.
-- A day is flagged when its km is more than 1.5x the route's median-like
-- typical km (the most common value for that route).

WITH typical AS (
    SELECT route_id, km AS typical_km
    FROM (
        SELECT route_id, km, COUNT(*) AS n,
               ROW_NUMBER() OVER (PARTITION BY route_id ORDER BY COUNT(*) DESC) AS rn
        FROM trip_log
        GROUP BY route_id, km
    )
    WHERE rn = 1
)
SELECT
    r.city,
    t.route_id,
    t.trip_date,
    t.cab_no,
    t.km,
    ty.typical_km,
    ROUND(1.0 * t.km / ty.typical_km, 1) AS times_typical
FROM trip_log t
JOIN typical ty ON ty.route_id = t.route_id
JOIN routes  r  ON r.route_id  = t.route_id
WHERE t.km > 1.5 * ty.typical_km
ORDER BY times_typical DESC, t.trip_date;
