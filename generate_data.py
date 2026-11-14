"""
Generate an anonymised, simulated dataset for a corporate employee-transport
(cab) operation, modelled on the structure of real monthly billing workbooks:

  * a cab-wise KM / trip log            -> data/trip_log.csv
  * a vendor billing working sheet      -> data/vendor_bill.csv
  * a client MIS / billing calculation  -> data/client_mis.csv
  * route master with client and vendor rates -> data/routes.csv

No real cab numbers, people, addresses, clients or vendors are included.
Rates and distances follow realistic ranges. A fixed random seed makes the
output reproducible. Known data issues are planted on purpose so the SQL
analysis has something to find (see PLANTED_ISSUES at the bottom).
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

random.seed(2025)
OUT = Path(__file__).parent / "data"
OUT.mkdir(exist_ok=True)

MONTH_START = date(2025, 2, 1)
CITIES = {
    1: ("Mumbai", ["Kurla", "Andheri", "Dadar", "Borivali", "Kandivali", "Vikhroli", "Thane", "Vasai", "Virar"]),
    2: ("Navi Mumbai", ["Kharghar", "Panvel", "Ulwe", "Seawoods", "Taloja", "Kamothe", "Koparkhairane", "Ghansoli"]),
    3: ("Pune", ["Hinjewadi", "Wakad", "Baner", "Kharadi", "Hadapsar", "Viman Nagar", "Pimple Saudagar", "Aundh"]),
    4: ("Chennai", ["Velachery", "Tambaram", "Porur", "Adyar", "Guindy", "Sholinganallur", "Anna Nagar", "OMR"]),
}
ROUTES_PER_CITY = 35
VENDORS = {1: "Vendor A", 2: "Vendor B", 3: "Vendor C", 4: "Vendor D"}  # one fleet vendor per city
CLIENT_RATE = 56500          # fixed monthly rate per route
APPROVED_KM_PER_DAY = 50
EXTRA_KM_RATE = 16


def working_days(start):
    d, days = start, []
    while d.month == start.month:
        if d.weekday() < 5:          # Mon-Fri
            days.append(d)
        d += timedelta(days=1)
    return days


DAYS = working_days(MONTH_START)   # 20 working days in Feb 2025
WORK_DAYS = len(DAYS)

routes, trips, vendor_bill, client_mis = [], [], [], []
cab_counter = 0
planted = []

for city_id, (city, areas) in CITIES.items():
    for n in range(1, ROUTES_PER_CITY + 1):
        route_id = f"R{city_id}{n:02d}"
        area = random.choice(areas)
        cab_counter += 1
        cab_no = f"CAB-{cab_counter:03d}"
        daily_km = random.choice([35, 44, 46, 48, 51, 52, 60, 64, 72, 82, 86, 125])
        vendor_rate = random.choice([37000, 40500, 42000, 42000, 42000, 45000, 46000, 50000])
        routes.append(dict(route_id=route_id, city_id=city_id, city=city, area=area,
                           vendor=VENDORS[city_id], client_rate=CLIENT_RATE,
                           vendor_rate=vendor_rate, contract_days=WORK_DAYS, approved_km_per_day=APPROVED_KM_PER_DAY,
                           extra_km_rate=EXTRA_KM_RATE))

        days_run = DAYS[:]
        # Issue 1: some routes miss 1-2 days in the trip log (no-shows / breakdowns)
        if random.random() < 0.10:
            for d in random.sample(days_run, random.choice([1, 2])):
                days_run.remove(d)
            planted.append(("missing_trip_days", route_id, WORK_DAYS - len(days_run)))

        for d in days_run:
            km = daily_km
            # Issue 2: occasional inflated KM entries (data-entry errors / over-claims)
            if random.random() < 0.006:
                km = daily_km * random.choice([2, 3])
                planted.append(("km_outlier", route_id, d.isoformat()))
            extra_hours = random.choice([0, 0, 0, 0.5, 1, 1.5, 2])
            trips.append(dict(trip_date=d.isoformat(), route_id=route_id, cab_no=cab_no,
                              km=km, extra_hours=extra_hours))

        # Vendor bill: vendor normally bills days actually run ...
        billed_days = len(days_run)
        # Issue 3: ... but sometimes bills the full month even when trips were missed
        if billed_days < WORK_DAYS and random.random() < 0.6:
            billed_days = WORK_DAYS
            planted.append(("vendor_overbilled_days", route_id, WORK_DAYS - len(days_run)))
        vendor_bill.append(dict(route_id=route_id, cab_no=cab_no, days_billed=billed_days,
                                amount=round(vendor_rate * billed_days / WORK_DAYS, 2)))

        # Client MIS: usually the same cab number ...
        mis_cab = cab_no
        # Issue 4: replacement / mistyped cab numbers in the client MIS (~17% of routes)
        if random.random() < 0.17:
            mis_cab = f"CAB-{random.randint(500, 999)}"
            planted.append(("cab_mismatch", route_id, f"{cab_no}->{mis_cab}"))
        client_mis.append(dict(route_id=route_id, cab_no=mis_cab, days_billed=WORK_DAYS,
                               km_billed=sum(t["km"] for t in trips if t["route_id"] == route_id)))


def write(name, rows):
    with open(OUT / name, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)


write("routes.csv", routes)
write("trip_log.csv", trips)
write("vendor_bill.csv", vendor_bill)
write("client_mis.csv", client_mis)

# Keep a record of what was planted so the SQL results can be checked against it
PLANTED_ISSUES = planted
with open(OUT / "planted_issues.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["issue", "route_id", "detail"])
    w.writerows(planted)

print(f"routes={len(routes)} trips={len(trips)} vendor_bill={len(vendor_bill)} client_mis={len(client_mis)}")
print("planted issues:", {k: sum(1 for p in planted if p[0] == k) for k in sorted({p[0] for p in planted})})
