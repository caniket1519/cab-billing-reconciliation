-- Schema for the cab billing reconciliation database (SQLite)

DROP TABLE IF EXISTS routes;
DROP TABLE IF EXISTS trip_log;
DROP TABLE IF EXISTS vendor_bill;
DROP TABLE IF EXISTS client_mis;

-- One row per employee-transport route (one dedicated cab per route)
CREATE TABLE routes (
    route_id            TEXT PRIMARY KEY,
    city_id             INTEGER NOT NULL,
    city                TEXT NOT NULL,
    area                TEXT NOT NULL,
    vendor              TEXT NOT NULL,
    client_rate         REAL NOT NULL,   -- fixed monthly rate charged to the client
    vendor_rate         REAL NOT NULL,   -- fixed monthly cost paid to the vendor
    contract_days       INTEGER NOT NULL, -- working days the monthly rates cover
    approved_km_per_day INTEGER NOT NULL,
    extra_km_rate       REAL NOT NULL    -- charged per km above the approved km
);

-- Daily KM log: one row per route per working day the cab ran
CREATE TABLE trip_log (
    trip_date   TEXT NOT NULL,
    route_id    TEXT NOT NULL REFERENCES routes(route_id),
    cab_no      TEXT NOT NULL,
    km          INTEGER NOT NULL,
    extra_hours REAL NOT NULL
);

-- What each vendor billed for the month
CREATE TABLE vendor_bill (
    route_id    TEXT PRIMARY KEY REFERENCES routes(route_id),
    cab_no      TEXT NOT NULL,
    days_billed INTEGER NOT NULL,
    amount      REAL NOT NULL
);

-- What the client MIS records for the month (basis of the client invoice)
CREATE TABLE client_mis (
    route_id    TEXT PRIMARY KEY REFERENCES routes(route_id),
    cab_no      TEXT NOT NULL,
    days_billed INTEGER NOT NULL,
    km_billed   INTEGER NOT NULL
);

CREATE INDEX idx_trip_route ON trip_log(route_id);
