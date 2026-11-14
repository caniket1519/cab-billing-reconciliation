-- Q7. Month-end billing summary by city: client billing, vendor cost,
-- gross margin, and how much the reconciliation checks protect.

WITH route_km AS (
    SELECT route_id, COUNT(*) AS days_run, SUM(km) AS total_km
    FROM trip_log GROUP BY route_id
),
client AS (
    SELECT r.route_id,
           r.client_rate
             + MAX(k.total_km - k.days_run * r.approved_km_per_day, 0) * r.extra_km_rate AS client_amount
    FROM routes r JOIN route_km k ON k.route_id = r.route_id
),
overbilled AS (
    SELECT v.route_id,
           MAX(v.days_billed - k.days_run, 0) * r.vendor_rate / r.contract_days AS overbilled_amount
    FROM vendor_bill v
    JOIN route_km k ON k.route_id = v.route_id
    JOIN routes  r ON r.route_id = v.route_id
)
SELECT
    r.city,
    ROUND(SUM(c.client_amount), 0)                               AS client_billing,
    ROUND(SUM(v.amount), 0)                                      AS vendor_billed,
    ROUND(SUM(o.overbilled_amount), 0)                           AS vendor_overbilling_found,
    ROUND(SUM(v.amount) - SUM(o.overbilled_amount), 0)           AS vendor_payable_after_checks,
    ROUND(100.0 * (SUM(c.client_amount) - (SUM(v.amount) - SUM(o.overbilled_amount)))
          / SUM(c.client_amount), 1)                             AS gross_margin_pct
FROM routes r
JOIN client      c ON c.route_id = r.route_id
JOIN vendor_bill v ON v.route_id = r.route_id
JOIN overbilled  o ON o.route_id = r.route_id
GROUP BY r.city
ORDER BY r.city;
