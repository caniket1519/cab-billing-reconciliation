-- Q1. Monthly operating summary by city: routes, trips, km and extra hours.
-- Each working day a cab does a pickup and a drop, so trips = 2 x cab-days.

SELECT
    r.city,
    COUNT(DISTINCT r.route_id)          AS routes,
    COUNT(*)                            AS cab_days,
    COUNT(*) * 2                        AS trips,
    SUM(t.km)                           AS total_km,
    ROUND(AVG(t.km), 1)                 AS avg_km_per_day,
    SUM(t.extra_hours)                  AS extra_hours
FROM trip_log t
JOIN routes r ON r.route_id = t.route_id
GROUP BY r.city
UNION ALL
SELECT
    'ALL CITIES',
    COUNT(DISTINCT t.route_id),
    COUNT(*),
    COUNT(*) * 2,
    SUM(t.km),
    ROUND(AVG(t.km), 1),
    SUM(t.extra_hours)
FROM trip_log t;
