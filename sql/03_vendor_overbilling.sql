-- Q3. Vendor bills that charge for more days than the cab actually ran.
-- Overbilled amount = extra days x daily vendor rate (monthly rate / contract days).

WITH days_run AS (
    SELECT route_id, COUNT(*) AS days_logged
    FROM trip_log
    GROUP BY route_id
)
SELECT
    r.city,
    r.route_id,
    r.vendor,
    d.days_logged,
    v.days_billed,
    v.days_billed - d.days_logged                              AS extra_days_billed,
    ROUND((v.days_billed - d.days_logged) * r.vendor_rate / r.contract_days, 0) AS overbilled_amount
FROM vendor_bill v
JOIN days_run d ON d.route_id = v.route_id
JOIN routes  r ON r.route_id = v.route_id
WHERE v.days_billed > d.days_logged
ORDER BY overbilled_amount DESC;
