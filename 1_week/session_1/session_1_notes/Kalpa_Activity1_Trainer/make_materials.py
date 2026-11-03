from pathlib import Path
import json, csv, shutil, io, contextlib, traceback

ROOT=Path(__file__).resolve().parent; PACK=ROOT/'Kalpa_Activity1'; TRAINER=ROOT/'trainer'
report=json.loads((TRAINER/'verification_report.json').read_text())
def write(path,text):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(text.strip()+'\n',encoding='utf-8')

write(PACK/'README.md', '''# Kalpa Retail: Activity 1 — Outcome

A synthetic Indian retail dataset for the revenue and contribution exercises. All records are fictional. Values are calibrated to a teaching case, not estimates from a real retailer.

## Start here
1. Extract the ZIP into a folder. Keep the folder structure intact.
2. Read `EXERCISES.md` and `DATA_DICTIONARY.md`.
3. Open `notebooks/Activity1_STUDENT.ipynb` in Jupyter or VS Code and run the setup cells. Python uses only the standard library; no pip install is needed.
4. Alternatively open `kalpa.sqlite` in a SQLite-capable client. It already contains every CSV row, enforced primary/foreign keys, indexes and the `eligible_orders` view.
5. `sql/Activity1_STUDENT.sql` is a question scaffold; write your queries in it. SQL in the notebook is executed through Python's built-in sqlite3.

## Files
| File | Grain | Rows |
|---|---|---:|
| data/periods.csv | One complete financial year | 2 |
| data/channels.csv | One sales channel | 3 |
| data/customers.csv | One registered customer | 18,000 |
| data/orders.csv | One order, including pre-dispatch cancellations | 106,400 |
| data/order_costs.csv | One cost record per order | 106,400 |
| data/marketing_spend.csv | One period-month-channel-purpose expense | 144 |

Both financial years contain 365 days: FY 2024-25 (1 April 2024–31 March 2025) and FY 2025-26 (1 April 2025–31 March 2026). The reporting snapshot is closed at 31 March 2026. All monetary fields are integer INR, not paise, lakh or crore. Divide rupees by 10,000,000 to display crore.

## Scope
Today: define the outcome; calculate the revenue tree; assess historical contribution against a margin floor; state limitations. Next session: customer/order distributions, grouped summaries, typical values, spread and hypotheses. Customer, segment, channel and date fields remain available for that session.

This is one shared dataset for both exercises. Exercise 2 adds historical costs to the same orders. Marketing expense records represent past expenditure, not the proposed future ₹12 crore acquisition request.

## Rebuild the database, if needed
From this folder run `python tools/load_database.py`. This recreates `kalpa.sqlite` from the CSVs and schema. You need write permission to this local folder. The loader is included, so learners do not need a database server.
''')

fields=[
('periods','period_id','TEXT','PK','FY2024_25','Financial-year key.','FY2024_25 or FY2025_26'),
('periods','period_label','TEXT','','FY 2024-25','Human-readable financial year.','Two labels'),
('periods','start_date','DATE','','2024-04-01','Inclusive reporting start.','ISO YYYY-MM-DD'),
('periods','end_date','DATE','','2025-03-31','Inclusive reporting end.','ISO YYYY-MM-DD'),
('periods','role','TEXT','','previous','Chronological role in comparison.','previous or current'),
('channels','channel_id','TEXT','PK','APP','Stable channel key.','APP, WEB, STORE'),
('channels','channel_name','TEXT','','Mobile app','Channel display name.','Three channel names'),
('customers','customer_id','TEXT','PK','C000001','Synthetic customer key; not a person identifier.','C followed by six digits'),
('customers','segment','TEXT','','Retail-Core','Stable customer segment for both years.','Business, Retail-Core, Retail-Plus, Student'),
('customers','city','TEXT','','Gurugram','Synthetic home city.','Ten Indian cities'),
('customers','region','TEXT','','North','Region associated with city.','North, South, East, West'),
('customers','signup_date','DATE','','2023-05-18','Registration date; precedes every order.','ISO YYYY-MM-DD'),
('orders','order_id','TEXT','PK','O0000001','Synthetic order key.','O followed by seven digits'),
('orders','customer_id','TEXT','FK customers.customer_id','C000001','Customer placing the order.','Must exist in customers'),
('orders','period_id','TEXT','FK periods.period_id','FY2024_25','Financial year containing order_date.','Must exist in periods'),
('orders','order_date','DATE','','2024-06-15','Order booking date; recognition assigned to this financial year.','ISO date inside its period'),
('orders','channel_id','TEXT','FK channels.channel_id','APP','Channel in which this order was placed.','Must exist in channels'),
('orders','status','TEXT','','COMPLETED','Final order state at the closed snapshot.','COMPLETED or CANCELLED'),
('orders','gross_amount','INTEGER INR','','28500','Value before discounts and refunds; excludes indirect tax.','Nonnegative whole rupees'),
('orders','discount_amount','INTEGER INR','','1500','Discount already granted on the order.','Nonnegative; gross >= discount + refund'),
('orders','refund_amount','INTEGER INR','','1000','Settled partial refund assigned to this order and period.','Nonnegative; gross >= discount + refund'),
('order_costs','order_id','TEXT','PK; FK orders.order_id','O0000001','The order to which the cost record belongs.','Exactly one row for every order'),
('order_costs','product_cost','INTEGER INR','','16000','Recognised product cost after applicable recoveries.','Nonnegative whole rupees'),
('order_costs','fulfilment_cost','INTEGER INR','','750','Recognised packing, shipping and handling cost.','Nonnegative whole rupees'),
('order_costs','payment_cost','INTEGER INR','','240','Recognised payment processing cost.','Nonnegative whole rupees'),
('marketing_spend','spend_id','TEXT','PK','M00001','Historical expense-record key.','M followed by five digits'),
('marketing_spend','period_id','TEXT','FK periods.period_id','FY2024_25','Period in which expense was incurred.','Must exist in periods'),
('marketing_spend','month_start','DATE','','2024-04-01','Accounting month, represented by its first day.','Inside associated period'),
('marketing_spend','channel_id','TEXT','FK channels.channel_id','WEB','Channel receiving this marketing expenditure.','Must exist in channels'),
('marketing_spend','purpose','TEXT','','Acquisition','Historical expenditure purpose.','Acquisition or Retention'),
('marketing_spend','amount','INTEGER INR','','620000','Cost incurred in this month/channel/purpose.','Nonnegative whole rupees'),
]
relationships=[
('customers.customer_id','orders.customer_id','1 to many','Join once to attach a stable customer segment. Registered customers are not the purchasing denominator.'),
('periods.period_id','orders.period_id','1 to many','Attach period dates and labels.'),
('channels.channel_id','orders.channel_id','1 to many','Attach sales-channel name.'),
('orders.order_id','order_costs.order_id','1 to exactly 1','Safe direct order join; every order has one cost row.'),
('periods.period_id','marketing_spend.period_id','1 to many','Aggregate marketing by period before comparing with annual revenue.'),
('channels.channel_id','marketing_spend.channel_id','1 to many','Marketing-channel dimension; not an order-to-spend allocation.'),
]
dictionary='''# Data dictionary and relationship guide

## Business definitions
- **Eligible order:** status = COMPLETED. Cancelled orders are excluded from recognised revenue, completed-order count and purchasing-customer count.
- **Net revenue:** gross_amount − discount_amount − refund_amount, on eligible orders only. Do not subtract discounts again in costs.
- **Purchasing customers:** distinct customer_id among eligible orders in the chosen period. The registry includes people with no eligible purchase.
- **Frequency:** completed orders / purchasing customers, over the same period and population.
- **Revenue per order:** net revenue / completed orders. This is a mean, not the median order value.
- **Specified costs:** all recorded product + fulfilment + payment costs, plus historical marketing spend in the same period. All pre-dispatch cancellations have zero tracked order costs in this dataset.
- **Contribution:** net revenue − specified costs. This is a teaching contribution measure, not net profit. Payroll, rent, depreciation, financing and income tax are outside the dataset.
- **Contribution margin:** contribution / net revenue. Aggregate components first; do not average row-level margin percentages.
- **Growth:** current / previous − 1. Multiply by 100 for percent display. A 20% to 15% margin change is −5 percentage points, not −5%.
- **Future agreement:** 15% revenue growth over the next annual reporting period and a 20% contribution-margin floor. The floor is the previous year's reference level; current margin is to be discovered. A successful analysis does not demonstrate that a future intervention has worked.

## Data scope and precision
Every file is UTF-8 CSV with a header. No required fields are missing. IDs are text. Money is nonnegative integer INR; CSV readers initially return strings, so convert monetary columns to integers. The snapshot is closed at 31 March 2026; historical partial refunds are settled and assigned to the same financial year as their order for this lab. There are no line-item, inventory, tax or refund-event tables. This simplification is deliberate.

Segments are stable customer attributes, not time-varying histories. Channels are order attributes; one customer can use several channels. Consequently, unique customers can be added across disjoint segments within a year, but cannot generally be added across channels or years. Signup is registration, not first completed purchase.

## Entity relationships
```mermaid
erDiagram
    CUSTOMERS ||--o{ ORDERS : places
    PERIODS ||--o{ ORDERS : contains
    CHANNELS ||--o{ ORDERS : receives
    ORDERS ||--|| ORDER_COSTS : has
    PERIODS ||--o{ MARKETING_SPEND : incurs
    CHANNELS ||--o{ MARKETING_SPEND : receives
```

| Parent | Child | Cardinality | Join guidance |
|---|---|---|---|
'''
dictionary+='\n'.join('| '+' | '.join(r)+' |' for r in relationships)
dictionary+='''

**Marketing join warning:** a period has many orders and many marketing-spend rows. Joining the detail tables using period_id repeats both measures. Aggregate revenue, order costs and marketing independently to one row per period; then join those summaries. Marketing costs are not allocated to individual customers in this dataset.

## Field dictionary
All fields are required; none are nullable in the supplied SQLite schema.

| Table | Field | Type / unit | Key | Example | Meaning | Rule |
|---|---|---|---|---|---|---|
'''
dictionary+='\n'.join('| '+' | '.join(r)+' |' for r in fields)
dictionary+='''

## Prepared SQL view
`eligible_orders` is a view, not an extra source file. It exposes order_id, customer_id, period_id, order_date, channel_id and computed net_revenue for completed orders. Inspect its definition in `sql/schema.sql`. Using the view is the scaffolded route; calculating eligibility and net revenue from `orders` is the independent route.

## Practical joins for today
Exercise 1 can use orders and periods only. Exercise 2 adds order_costs (join on order_id) and marketing_spend (aggregate separately by period). Customers and channels are available for the next session's grouping and distributions. No product table is required because this activity analyses orders rather than line items.
'''
write(PACK/'DATA_DICTIONARY.md',dictionary)
with (PACK/'data_dictionary.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.writer(f);w.writerow(['table','field','type_or_unit','key','example','meaning','rule']);w.writerows(fields)
write(ROOT/'dictionary_for_workbook.json',json.dumps(dict(fields=fields,relationships=relationships),indent=2))

write(PACK/'EXERCISES.md', '''# Activity 1 — Outcome: revenue and the guardrail

## Your role
Kalpa Retail sells consumer goods through its app, website and stores. Last year, it made ₹100 crore in revenue. This year, it made ₹104 crore, against a plan of ₹115 crore.

Marketing says, “We need more customers. Give us ₹12 crore for acquisition.”

You are Kalpa Retail's new data team. Meera asks: “Revenue grew less than planned. Marketing wants ₹12 crore for acquisition. Before I commit, show me what changed and whether our recent growth protected profitability.”

The original plan was 15% growth. For the next annual reporting period, success means at least 15% growth in eligible net revenue while contribution margin reaches at least the agreed 20% floor. Today's task establishes historical evidence; no proposed future acquisition programme has been executed in these files.

Use the full dataset. Complete both exercises on the SAME financial years. All monetary amounts are whole INR. Read the dictionary before calculating.

## Before coding — 3 minutes
Write one sentence stating the problem, the primary business metric, the time window and the guardrail. Identify the decision Meera is considering. Do not adopt “insufficient acquisition” as a proven cause.

## Exercise 1: Check Marketing's explanation — 30 minutes
Meera: “Is customer acquisition the branch that is short, or is something else changing?”

### A. Python calculation
1. Decide which order statuses belong in revenue and purchase counts. State your rule.
2. Calculate eligible revenue from the raw monetary fields. Show the relationship between gross amount, discounts, refunds and recognised revenue.
3. For each financial year, calculate completed orders, distinct purchasing customers and revenue.
4. Calculate orders per purchasing customer and revenue per order. Keep the numerators and denominators alongside the ratios.
5. Calculate the percentage change in all five measures. Distinguish a difference in counts from a percentage change.
6. Check that customers × orders per customer × revenue per order returns each year's revenue. Check that the product of the three current-year / previous-year branch ratios returns the annual revenue ratio. Use full precision until display.

### B. SQL confirmation
Reproduce the base totals and ratios from the SAME data in `kalpa.sqlite`. Use `eligible_orders` if you want the eligibility/amount scaffold; inspect how it is defined. Sort results by period. Compare the Python and SQL totals before interpreting them.

### C. Response to Meera — maximum 100 words
State what changed, which branch deserves investigation and what these results do not establish. Address Marketing's explanation directly. Does a lower overall frequency mean every existing customer bought less often? Explain why you cannot assume that.

Deliver: one two-period results table, a Python/SQL reconciliation and the short response.

## Exercise 2: Was the growth profitable? — 20 minutes
Meera: “Before we celebrate revenue growth, did we protect the contribution-margin floor?”

1. Inspect the grain and join keys of order_costs and marketing_spend. Write how you will combine them without repeating money.
2. Sum product, fulfilment and payment costs for each financial year using the historical order-cost records.
3. Sum historical marketing expenditure by financial year. These are costs already incurred; they are NOT the proposed ₹12 crore budget.
4. Combine the annual cost components, then calculate contribution and contribution margin using the revenue from Exercise 1.
5. Calculate cost growth and contribution growth. State margin movement in percentage points.
6. Compare both years against the 20% floor. Was positive revenue growth sufficient to meet our desired business outcome?
7. Confirm your result with SQL. Aggregate each grain separately before joining the annual summaries; a query scaffold is provided.
8. Update your response to Meera in at most 100 words: what is now different about your assessment, what should be investigated, and what is still unknown?

Deliver: a cost bridge, contribution/margin table, guardrail verdict and updated response.

## Closing challenge — 5 minutes
Marketing suggests measuring acquisition success by account registrations. Give one way registrations could increase without helping our agreed outcome, and identify another measurement you would request.

## Hand-off to Deconstruction
Do not conclude that “unchanged average order value” means an unchanged customer experience. For the next session, bring two questions about what the averages could hide. We will examine customer-level frequency, order-level value, segments, channels, median, quartiles, spread and distributions.

## Ungraded review criteria
Your work is complete when your eligibility/metric definitions are explicit; counts are distinct where needed; both languages agree; totals reconcile; costs are not duplicated; the margin verdict follows the agreed floor; and observed changes are distinguished from causes or campaign effects. No model training, causal claim or future campaign forecast is required today.
''')

write(PACK/'sql'/'Activity1_STUDENT.sql', '''-- Student scaffold: write the missing queries; no answer values are supplied.
-- Open kalpa.sqlite in a SQLite client, or run SQL via the notebook.

-- Orientation (runnable):
SELECT * FROM periods ORDER BY period_id;
SELECT * FROM eligible_orders ORDER BY order_date, order_id LIMIT 5;

-- Exercise 1:
-- FROM eligible_orders, one row per period_id.
-- Return completed orders, DISTINCT purchasing customers and SUM(net_revenue).
-- Calculate both ratios using 1.0 * numerator / denominator to avoid integer division.
-- Then calculate percentage changes between periods.

-- Exercise 2:
-- Step 1: recognised revenue grouped by period.
-- Step 2: orders JOIN order_costs ON order_id; sum each cost category by period.
-- Step 3: marketing_spend grouped by period.
-- Step 4: combine the three period summaries; calculate total cost,
-- contribution, contribution margin and whether the 20% floor was met.
-- Do NOT join individual orders directly to marketing spend using period_id.
''')

loader='''from pathlib import Path
import csv, sqlite3
ROOT=Path(__file__).resolve().parents[1]
dbpath=ROOT/'kalpa.sqlite'
dbpath.unlink(missing_ok=True)
db=sqlite3.connect(dbpath)
db.executescript((ROOT/'sql'/'schema.sql').read_text())
for table in ['periods','channels','customers','orders','order_costs','marketing_spend']:
    with (ROOT/'data'/f'{table}.csv').open(newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        names=reader.fieldnames
        query=f"INSERT INTO {table} ({','.join(names)}) VALUES ({','.join('?' for _ in names)})"
        db.executemany(query,([row[name] for name in names] for row in reader))
db.commit()
assert db.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
assert not db.execute('PRAGMA foreign_key_check').fetchall()
db.close()
print('Rebuilt kalpa.sqlite from all six CSV files.')
'''
write(PACK/'tools'/'load_database.py',loader)

setup='''from pathlib import Path
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
'''
def md(text): return dict(cell_type='markdown',metadata={},source=text.strip().splitlines(True))
def code(text):return dict(cell_type='code',metadata={},execution_count=None,outputs=[],source=text.strip().splitlines(True))
def notebook(cells):return dict(nbformat=4,nbformat_minor=5,metadata=dict(kernelspec=dict(display_name='Python 3',language='python',name='python3'),language_info=dict(name='python',version='3.11')),cells=[dict(id=f'cell-{i:03d}',**c) for i,c in enumerate(cells)])
studentcells=[md('''# Kalpa Retail — Activity 1: Outcome
Read ../EXERCISES.md and ../DATA_DICTIONARY.md. Use the same data for both exercises. This is synthetic historical data, not campaign forecasts.

Write your problem statement, success metric, reporting window and guardrail below.'''),md('**Your outcome statement:**'),code(setup),md('''## Exercise 1 — Revenue tree
Calculate completed orders, distinct purchasing customers and recognised revenue for each period. Then frequency, revenue per order and percentage changes. Verify both revenue-tree identities.'''),code('# Your Python calculation here'),md('''### SQL confirmation
Write a query grouped by period. The eligible_orders view is available as a scaffold. Compare the resulting totals with Python.'''),code('# query = """Your SELECT here"""\n# print(run_sql(query))'),md('**Your response to Meera (maximum 100 words):**'),md('''## Exercise 2 — Historical profitability
Inspect the grain of order_costs and marketing_spend. Calculate annual cost components independently, combine with revenue, then contribution and contribution margin. Apply the 20% floor. Do not subtract discounts twice.'''),code('# Your Python calculation here'),md('''### SQL confirmation
Aggregate revenue, order costs and marketing separately by period before joining. Calculate growth and margin movement.'''),code('# Your SQL calculation here'),md('**Updated response to Meera (maximum 100 words):**'),md('''## Closing challenge
Can account registrations increase without helping the agreed business outcome? What else would you measure?

## Next session
Write two questions about what averages could hide. We will inspect distributions and groups before explaining causes.''')]
write(PACK/'notebooks'/'Activity1_STUDENT.ipynb',json.dumps(notebook(studentcells),indent=2))

solution_python='''# Independent calculation from raw CSV records; no target values embedded.
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
'''
def read_solution(name):
    path=PACK/'sql'/name
    return (path if path.exists() else TRAINER/name).read_text()
sql1=read_solution('exercise_1_solution.sql');sql2=read_solution('exercise_2_solution.sql')
solutions=[md('# Trainer solutions — do not distribute\nExecuted cell-by-cell against the shipped historical CSV files and SQLite database.'),code(setup),md('## Python: both exercises'),code(solution_python),md('## SQL: Exercise 1'),code('query = '+repr(sql1)+'\nprint(json.dumps(run_sql(query), indent=2))'),md('## SQL: Exercise 2'),code('query = '+repr(sql2)+'\nprint(json.dumps(run_sql(query), indent=2))'),md('''## Interpretation
Revenue +4%, buyers +30%, frequency −20%, average order value unchanged. The average does not describe every buyer, and changing customer mix can affect it. Margin falls 20% to 15%; contribution falls 22%. Costs grew 10.5%. The 20% floor is breached in the current year. These observations justify investigation, not a causal explanation or a claim that future acquisition cannot work.''')]
nb=notebook(solutions)
env={}; old=Path.cwd()
import os
os.chdir(PACK)
try:
    count=0
    for cell in nb['cells']:
        if cell['cell_type']=='code':
            count+=1;out=io.StringIO()
            with contextlib.redirect_stdout(out):exec(compile(''.join(cell['source']),'<trainer notebook>','exec'),env)
            cell['execution_count']=count
            cell['outputs']=[dict(output_type='stream',name='stdout',text=out.getvalue().splitlines(True))]
finally:os.chdir(old)
write(TRAINER/'Activity1_SOLUTIONS_EXECUTED.ipynb',json.dumps(nb,indent=2))
write(TRAINER/'solution_python.py',setup+'\n'+solution_python)
write(TRAINER/'exercise_1_solution.sql',sql1);write(TRAINER/'exercise_2_solution.sql',sql2)
# Remove answer SQL from the student tree after the validator has used it.
# Validator runs against the trainer path from this point onward.
for filename in ['exercise_1_solution.sql','exercise_2_solution.sql']:
    (PACK/'sql'/filename).unlink(missing_ok=True)

metrics=report['python_results']; stats=report['descriptive_statistics']
key='''# Trainer guide — Activity 1

## Timing and sequence
Introduction 25 min; Exercise 1 30 min; Exercise 2 20 min; closing challenge 5 min. Reveal costs after the revenue discussion. Use the prepared environment so installation does not consume teaching time.

## Opening conversation — 25 minutes
1. Read the story aloud and ask everyone to write their first proposed solution (3 min). Expect advertising, dashboards or prediction models.
2. Ask: “What is the problem, and what decision does Meera need to make?” Collect answers. Separate the observed growth shortfall from the assumed acquisition explanation (5 min).
3. Ask: “If registrations doubled but revenue did not move, would we have succeeded?” Agree that registrations are an intermediate measure; the business outcome is eligible net revenue (4 min).
4. Put the next annual agreement on the board: grow net revenue at least 15% from the ₹104 crore baseline, with contribution margin at least 20%. Ask: “Could a discount help the first number and hurt the second?” Define contribution using the costs supplied in this case (5 min).
5. Build the tree together: revenue = purchasing customers × orders per purchasing customer × revenue per order. Ask learners to name each numerator, denominator and time window. The branches explain where to look; they do not identify a cause (5 min).
6. Introduce the two tasks: first check the revenue explanation, then check the historical margin. Ask learners to write their outcome sentence before coding (3 min).

## Story consistency
The financial years in the data reproduce ₹100 crore → ₹104 crore. The missed current-year plan was ₹115 crore. A new 15% target on the ₹104 crore baseline is ₹119.6 crore. The 20% margin floor is the PREVIOUS year's reference level. Do not tell students the current margin is 20%; it is 15%, discovered in Exercise 2. To meet the future agreement Kalpa must restore that floor. The proposed ₹12 crore acquisition request is not an expense row. Actual historical marketing costs are ₹7 crore and ₹9.52 crore.

## Exact answer key
| Metric | FY 2024-25 | FY 2025-26 | Change |
|---|---:|---:|---:|
| Recognised revenue | ₹100 crore | ₹104 crore | +4% |
| Completed orders | 50,000 | 52,000 | +4% |
| Purchasing customers | 10,000 | 13,000 | +30% |
| Orders per purchasing customer | 5 | 4 | −20% |
| Revenue per order | ₹20,000 | ₹20,000 | 0% |
| Product cost | ₹68 crore | ₹71.6 crore | |
| Fulfilment cost | ₹4 crore | ₹5.72 crore | |
| Payment cost | ₹1 crore | ₹1.56 crore | |
| Marketing cost | ₹7 crore | ₹9.52 crore | |
| Total specified cost | ₹80 crore | ₹88.4 crore | +10.5% |
| Contribution | ₹20 crore | ₹15.6 crore | −22% |
| Contribution margin | 20% | 15% | −5 percentage points |
| 20% margin floor | MET | BREACHED | |

## Suggested responses
Exercise 1: Buyers grew 30%, but overall orders per buyer fell 20%; average revenue per order was flat. Frequency deserves investigation before adopting acquisition as the main explanation. This does not show every returning customer reduced their purchases or that acquisition is unprofitable.

Exercise 2: Costs grew faster than revenue, contribution declined and the margin floor was breached. Investigate cost categories and order economics alongside frequency. Contribution is not net profit and no future campaign has been tested.

## Misconceptions to surface
- All registered customers are not this year's purchasing customers.
- COUNT(*) counts orders even if the column is named customers.
- Cancelled pre-dispatch orders do not recognise sales.
- Discount and refund amounts are already deducted in net revenue.
- Marketing expenses are incurred at month/channel/purpose grain; do not attach their full amount to every order.
- A mean order value of ₹20,000 does not imply most orders are near ₹20,000.
- A −5 percentage-point margin move is different from a −25% relative margin move.
- Customer changes and average changes are descriptions, not causes.

## Next session: Deconstruction and descriptive statistics
Use orders as the unit for order-value distribution; use customer-period as the unit for purchase-frequency distribution. Attach customer segment and order channel only when needed. Customers can buy in several channels, so unique customers do not generally add across channels.
'''
key+='\n| Distribution | Previous | Current |\n|---|---:|---:|\n'
for k,label in [('order_value_mean','Mean order value (INR)'),('order_value_median','Median order value (INR)'),('order_value_iqr','IQR, inclusive linear quartiles (INR)'),('order_value_std_population','Population standard deviation (INR)'),('orders_per_customer_median','Median orders per purchasing customer')]:
    key+=f"| {label} | {stats['FY2024_25'][k]:,.2f} | {stats['FY2025_26'][k]:,.2f} |\n"
key+='''
The aggregate mean order value is unchanged while median and spread differ. Retail-Plus is the segment with a substantial frequency and revenue deterioration. Keep these facts in the trainer pack; learners discover them next session. Small synthetic populations are not evidence of market-wide effects.

## Data design
There are 7,000 buyers in both annual periods, 3,000 previous-only and 6,000 current-only. Two thousand registered customers never make a completed purchase. These support later cohort work but are not the previously discussed 10,000/12,000 quarterly churn illustration. That quarterly story must be recalibrated before reuse: this dataset compares complete financial years, and current buyers total 13,000. There is no pre-April-2024 purchase history, so “current-only” does not prove lifetime first purchase. Do not use signup as a substitute for first purchase. Churn and lifetime first-to-second-purchase activities need their own defined windows/history extension.

The record variability is intentional, while headline totals are constrained. There are no duplicate primary keys, orphan references, missing costs or malformed amounts. Do not tell learners the generator's targets or planted distribution patterns before they compute.

## Reproducibility
`build_pack.py` generates the six related raw files and database using seed 20261005 (requires NumPy). Student calculations, loader and solutions use only Python's standard library. `validate_pack.py` independently reads the CSVs and runs both SQL solutions. The trainer notebook contains captured outputs from executing its Python cells against the delivered dataset. SQL was executed in SQLite; no claim of a PostgreSQL runtime test is made.
'''
write(TRAINER/'TRAINER_GUIDE.md',key)

verification='''# Verification report

Status: **PASS**. Both Python and SQLite calculations agree with the teaching targets.

'''+f"{report['checks_passed']} checks passed.\n\n"
verification+='''Checks cover every primary key, required field, foreign key and compound spend grain; exact CSV/database row equality; date boundaries and signup timing; monetary identities; one-to-one cost coverage; cancelled-order scope; exact target totals; revenue-tree identities; segment reconciliation; independent Python/SQL results; database integrity; and deliberate wrong-query probes.

| Measure | Previous | Current |
|---|---:|---:|
| Completed orders | 50,000 | 52,000 |
| Purchasing customers | 10,000 | 13,000 |
| Revenue (INR) | 1,000,000,000 | 1,040,000,000 |
| Total specified cost (INR) | 800,000,000 | 884,000,000 |
| Contribution (INR) | 200,000,000 | 156,000,000 |
| Contribution margin | 20% | 15% |

Amounts are whole rupees and reconcile exactly. Ratios are compared at full precision; rounding is for display. Monetary values, cost coverage and entity IDs are compared exactly. Detailed results and SHA-256 CSV hashes are in verification_report.json.

Limitations: synthetic case calibration, stable customer segments, simplified within-period recognition/refunds, no line items or inventory, no pre-period purchase history, contribution rather than net profit, and no causal intervention results. The data includes 106,400 order records, of which 102,000 are completed and 4,400 are cancelled before dispatch.
'''
write(TRAINER/'VERIFICATION_REPORT.md',verification)
print('Created student instructions, dictionary, SQL scaffold, starter notebook, executed trainer notebook and trainer guide.')
