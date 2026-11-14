-- Q5. Margin per route on the fixed monthly rate (client rate vs vendor cost),
-- with each route ranked within its city. Low-margin routes are candidates
-- for vendor renegotiation.

SELECT
    city,
    route_id,
    area,
    client_rate,
    vendor_rate,
    client_rate - vendor_rate                                   AS margin,
    ROUND(100.0 * (client_rate - vendor_rate) / client_rate, 1) AS margin_pct,
    RANK() OVER (PARTITION BY city
                 ORDER BY (client_rate - vendor_rate) ASC)      AS lowest_margin_rank_in_city
FROM routes
ORDER BY margin_pct ASC
LIMIT 15;
