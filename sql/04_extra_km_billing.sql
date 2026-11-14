-- Q4. Client billing per route: fixed monthly rate plus extra-km charges.
-- Extra km = km driven above (days run x approved km per day).

WITH route_km AS (
    SELECT route_id, COUNT(*) AS days_run, SUM(km) AS total_km
    FROM trip_log
    GROUP BY route_id
)
SELECT
    r.city,
    r.route_id,
    r.area,
    k.days_run,
    k.total_km,
    k.days_run * r.approved_km_per_day                               AS approved_km,
    MAX(k.total_km - k.days_run * r.approved_km_per_day, 0)          AS extra_km,
    MAX(k.total_km - k.days_run * r.approved_km_per_day, 0) * r.extra_km_rate AS extra_km_charge,
    r.client_rate
      + MAX(k.total_km - k.days_run * r.approved_km_per_day, 0) * r.extra_km_rate AS client_amount
FROM route_km k
JOIN routes r ON r.route_id = k.route_id
ORDER BY r.city, extra_km DESC;
