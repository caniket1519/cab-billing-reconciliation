"""
Load the CSVs into a SQLite database, run every query in sql/, save each
result to results/, print a short summary and draw two charts.

Usage:
    python generate_data.py     # (re)create the simulated data
    python run_analysis.py      # build cab_billing.db and run the analysis
"""
import csv
import sqlite3
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).parent
DATA, SQL, RESULTS = ROOT / "data", ROOT / "sql", ROOT / "results"
RESULTS.mkdir(exist_ok=True)
DB = ROOT / "cab_billing.db"


def load(conn):
    conn.executescript((SQL / "00_schema.sql").read_text())
    for table in ["routes", "trip_log", "vendor_bill", "client_mis"]:
        with open(DATA / f"{table}.csv", newline="") as f:
            rows = list(csv.DictReader(f))
        cols = list(rows[0].keys())
        conn.executemany(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' * len(cols))})",
            [tuple(r[c] for c in cols) for r in rows],
        )
    conn.commit()


def run(conn, path):
    cur = conn.execute(path.read_text())
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    with open(RESULTS / f"{path.stem}.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    return cols, rows


def main():
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    load(conn)

    out = {}
    for path in sorted(SQL.glob("0[1-9]_*.sql")):
        out[path.stem] = run(conn, path)
        print(f"{path.stem}: {len(out[path.stem][1])} rows -> results/{path.stem}.csv")

    # ---- headline findings -------------------------------------------------
    _, summary = out["01_city_summary"]
    total = summary[-1]
    _, mism = out["02_cab_mismatch"]
    _, over = out["03_vendor_overbilling"]
    _, anomalies = out["06_km_anomalies"]
    _, billing = out["07_billing_summary"]

    print("\nKEY FINDINGS")
    print(f"- {total[1]} routes, {total[3]:,} trips, {total[4]:,} km in the month")
    print(f"- {len(mism)} cab-number mismatches between KM log and client MIS "
          f"({100 * len(mism) / total[1]:.0f}% of routes)")
    print(f"- {len(over)} vendor bills charged for days not run; "
          f"overbilling found: {sum(r[6] for r in over):,.0f}")
    print(f"- {len(anomalies)} KM entries over 1.5x the route's typical distance")
    for row in billing:
        print(f"- {row[0]}: client billing {row[1]:,.0f}, gross margin {row[5]}%")

    # ---- charts ------------------------------------------------------------
    cities = [r[0] for r in summary[:-1]]
    plt.figure(figsize=(7, 4))
    plt.bar(cities, [r[4] for r in summary[:-1]], color="#2F5F9E")
    plt.title("Total km per city - Feb 2025 (simulated)")
    plt.ylabel("km")
    plt.tight_layout()
    plt.savefig(RESULTS / "km_by_city.png", dpi=150)

    plt.figure(figsize=(7, 4))
    plt.bar([r[0] for r in billing], [r[5] for r in billing], color="#4C9A6A")
    plt.title("Gross margin % by city after reconciliation")
    plt.ylabel("%")
    plt.tight_layout()
    plt.savefig(RESULTS / "margin_by_city.png", dpi=150)
    conn.close()


if __name__ == "__main__":
    main()
