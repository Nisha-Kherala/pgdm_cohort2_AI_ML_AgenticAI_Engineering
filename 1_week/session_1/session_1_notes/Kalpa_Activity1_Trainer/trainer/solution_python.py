from pathlib import Path
import csv, sqlite3, json

# Locate the dataset whether the kernel starts in this folder or its parent.
ROOT = next((p for p in [Path.cwd(), *Path.cwd().parents] if (p / "data" / "orders.csv").exists()), None)
if ROOT is None:
    raise FileNotFoundError("Start the kernel inside the extracted Kalpa_Activity1 folder or its notebooks folder.")

def read_table(name, integer_columns=()):
    with (ROOT / "data" / (name + ".csv")).open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        for field in integer_columns:
            row[field] = int(row[field])
    return rows

orders = read_table("orders", ["gross_amount", "discount_amount", "refund_amount"])
order_costs = read_table("order_costs", ["product_cost", "fulfilment_cost", "payment_cost"])
marketing_spend = read_table("marketing_spend", ["amount"])
periods = read_table("periods")
customers = read_table("customers")
channels = read_table("channels")
db = sqlite3.connect("file:" + str(ROOT / "kalpa.sqlite") + "?mode=ro", uri=True)
db.row_factory = sqlite3.Row

def run_sql(query):
    return [dict(row) for row in db.execute(query)]

print("Data loaded. Monetary values are integer INR. Database connection is read-only.")
print(orders[0])

# Independent calculation from raw CSV records; no target values embedded.
from collections import defaultdict
cost_by_order = {row["order_id"]: row for row in order_costs}
python_results = {}
for period in periods:
    pid = period["period_id"]
    year_orders = [row for row in orders if row["period_id"] == pid]
    completed = [row for row in year_orders if row["status"] == "COMPLETED"]
    buyers = {row["customer_id"] for row in completed}
    revenue = sum(row["gross_amount"] - row["discount_amount"] - row["refund_amount"] for row in completed)
    n_orders = len(completed)
    expenses = {name: sum(cost_by_order[row["order_id"]][name] for row in year_orders)
                for name in ["product_cost", "fulfilment_cost", "payment_cost"]}
    marketing = sum(row["amount"] for row in marketing_spend if row["period_id"] == pid)
    total_cost = sum(expenses.values()) + marketing
    contribution = revenue - total_cost
    margin = contribution / revenue
    python_results[pid] = dict(revenue=revenue, completed_orders=n_orders,
        purchasing_customers=len(buyers), orders_per_customer=n_orders/len(buyers),
        revenue_per_order=revenue/n_orders, **expenses, marketing_cost=marketing,
        total_cost=total_cost, contribution=contribution,
        contribution_margin_pct=margin*100, guardrail="MET" if margin >= .20 else "BREACHED")
print(json.dumps(python_results, indent=2))

previous = python_results["FY2024_25"]
current = python_results["FY2025_26"]
changes = {name: 100 * (current[name]/previous[name] - 1) for name in
           ["revenue", "completed_orders", "purchasing_customers", "orders_per_customer", "revenue_per_order", "total_cost", "contribution"]}
changes["margin_change_percentage_points"] = current["contribution_margin_pct"] - previous["contribution_margin_pct"]
print(json.dumps(changes, indent=2))
