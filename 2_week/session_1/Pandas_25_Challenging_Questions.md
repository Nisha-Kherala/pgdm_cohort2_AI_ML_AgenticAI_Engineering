# Pandas: 25 Challenging Questions

Five independently generated DataFrames, with five questions per DataFrame. Each dataset has **500 rows** and a fixed random seed. All records are synthetic.

## Before you begin

Run this import cell once, then the setup cell for the relevant DataFrame:

```python
import re
import numpy as np
import pandas as pd
```

- **Start each question from a fresh DataFrame**, by rerunning that dataset's setup cell. Questions are independent; do not carry earlier updates forward.
- Preserve the named, non-default index. The `row_id` values are labels, not row positions.
- Solve the specified task on **all 500 rows**. Every sample below is a preview of an actual result from the complete generated dataset, not an invented illustration. The stated row count is a useful checkpoint.
- Use `loc` for the requested selections and updates. For updates, put the boolean mask on the left-hand side. Avoid chained assignment.
- When a question asks for a slice, create an explicit independent copy, modify it, then explicitly write the specified columns back to the original. Do not assume editing a slice changes its parent.
- For the `apply` questions, define a **named function** and pass it to the Series or DataFrame as specified. Do not use lambda functions or loops over DataFrame rows. Loops over tokens inside a text-cleaning function are allowed.
- Return the columns in the stated order. Unless specified otherwise, sort results by index ascending and show the first five rows.
- Sample tables display money/floats to two decimal places and missing values as `<missing>`. Integer and float display differences do not change the expected values. Text spacing is significant; surrounding spaces in raw source cells may be visually trimmed by Markdown.
- Use the fixed dates in the questions, not your computer's current date. Round only where requested.

The setup code only generates the data. Implement the requested operations yourself; solution code is intentionally omitted.

---

## DataFrame 1: `orders`

500 rows × 15 columns. Each row is one order. Money is in rupees; `discount_pct` is a percentage from 0 to 100. Missing refunds mean no refund recorded. `delivery_days` is missing for cancelled/in-transit orders.

Run this setup cell:

```python
def make_orders():
    rng = np.random.default_rng(101)
    n = 500
    df = pd.DataFrame({
        "order_id": [f"ORD{i:04d}" for i in range(1, n + 1)],
        "customer_id": rng.integers(100, 230, n),
        "city": rng.choice(["Delhi", "Mumbai", "Pune", "Jaipur", "Bengaluru"], n),
        "channel": rng.choice(["App", "Website", "Store"], n),
        "category": rng.choice(["Electronics", "Furniture", "Clothing", "Grocery"], n),
        "order_date": pd.Timestamp("2026-06-01") + pd.to_timedelta(rng.integers(0, 122, n), unit="D"),
        "quantity": rng.integers(1, 7, n),
        "unit_price": rng.integers(250, 22001, n).astype(float),
        "discount_pct": rng.choice([0.0, 5.0, 10.0, 15.0, 20.0], n),
        "shipping_fee": rng.choice([0.0, 49.0, 99.0, 149.0], n),
        "payment": rng.choice(["Prepaid", "COD"], n, p=[0.7, 0.3]),
        "status": rng.choice(["Delivered", "Returned", "Cancelled", "In transit"], n, p=[0.6, 0.15, 0.1, 0.15]),
        "delivery_days": rng.integers(1, 12, n).astype(float),
        "refund_amount": rng.choice([0.0, 0.0, 0.0, 250.0, 700.0, np.nan], n),
        "coupon_code": rng.choice([" vip05 ", "NEW20", "save10", "", None, "A1B20", "NEW00", "VIP75", "new20"], n),
    }, index=pd.Index(1000 + np.arange(n) * 3, name="row_id"))
    df.loc[df["status"].isin(["Cancelled", "In transit"]), "delivery_days"] = np.nan
    return df

orders = make_orders()
```

**Preview — first five rows, selected columns:**

| row_id | order_id | city | category | quantity | unit_price | status |
| --- | --- | --- | --- | --- | --- | --- |
| 1000 | ORD0001 | Bengaluru | Electronics | 5 | 14802.00 | Delivered |
| 1003 | ORD0002 | Delhi | Electronics | 1 | 17871.00 | Delivered |
| 1006 | ORD0003 | Delhi | Clothing | 5 | 3985.00 | Cancelled |
| 1009 | ORD0004 | Delhi | Furniture | 6 | 14406.00 | Delivered |
| 1012 | ORD0005 | Jaipur | Electronics | 6 | 20013.00 | Delivered |

---

### Question 1

Using `loc`, select delivered, prepaid orders from Delhi, Mumbai or Pune placed from **1 July through 30 September 2026, inclusive**, with no recorded refund. Keep orders that are either Electronics with quantity at least 2, or Furniture with unit price at least ₹15,000.

Treat a missing refund as zero. Return `order_id`, `order_date`, `city`, `category`, `quantity`, `unit_price` and `refund_amount`, sorted by index ascending.

**Sample output** — 17 rows in the full result; first five shown.

| row_id | order_id | order_date | city | category | quantity | unit_price | refund_amount |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1066 | ORD0023 | 2026-07-24 | Delhi | Electronics | 5 | 5255.00 | &lt;missing&gt; |
| 1099 | ORD0034 | 2026-09-30 | Pune | Furniture | 2 | 20701.00 | 0.00 |
| 1234 | ORD0079 | 2026-08-31 | Delhi | Furniture | 4 | 15605.00 | 0.00 |
| 1402 | ORD0135 | 2026-07-23 | Mumbai | Electronics | 4 | 10509.00 | &lt;missing&gt; |
| 1408 | ORD0137 | 2026-09-14 | Pune | Electronics | 6 | 20201.00 | 0.00 |

---

### Question 2

Update `orders` itself using boolean masks on the left side of `loc` assignments:

- For every Cancelled order, set `shipping_fee` and `discount_pct` to zero.
- For a Delivered order with `delivery_days > 6`, zero/missing refund and positive shipping fee, refund the **original shipping fee** and then set the shipping fee to zero.

Do not change other rows or columns. Build an audit table for every row matched by either rule, with `order_id`, `status`, `delivery_days`, then old/new pairs for `shipping_fee`, `discount_pct`, `refund_amount`. Sort by index ascending. Evaluate eligibility from the original data; preserve the original values for the audit.

**Sample output** — 128 rows in the full result; first five shown.

| row_id | order_id | status | delivery_days | old_shipping_fee | new_shipping_fee | old_discount_pct | new_discount_pct | old_refund_amount | new_refund_amount |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1006 | ORD0003 | Cancelled | &lt;missing&gt; | 49.00 | 0.00 | 10.00 | 0.00 | 0.00 | 0.00 |
| 1012 | ORD0005 | Delivered | 11.00 | 49.00 | 0.00 | 0.00 | 0.00 | 0.00 | 49.00 |
| 1021 | ORD0008 | Delivered | 7.00 | 49.00 | 0.00 | 10.00 | 10.00 | 0.00 | 49.00 |
| 1045 | ORD0016 | Cancelled | &lt;missing&gt; | 149.00 | 0.00 | 20.00 | 0.00 | &lt;missing&gt; | &lt;missing&gt; |
| 1048 | ORD0017 | Delivered | 8.00 | 49.00 | 0.00 | 0.00 | 0.00 | 0.00 | 49.00 |

---

### Question 3

Create an explicit independent slice named `patch` containing Electronics orders with quantity at least 2 and status Delivered or Returned. Include `order_id`, `status`, `quantity`, `unit_price`, `discount_pct`.

Inside `patch`, add 5 percentage points to Delivered-order discounts, capped at 20%; set Returned-order discounts to 0%. Add `rebate_amount = quantity × unit_price × updated discount_pct / 100`, rounded to two decimals. Sort `patch` by index **descending**.

Write only `discount_pct` back to `orders` by matching index labels, using a DataFrame on the right-hand side. Keep `rebate_amount` only in `patch`, and preserve all non-selected rows. Return an audit table sorted by index ascending: `order_id`, `status`, `old_discount_pct`, `new_discount_pct`, `rebate_amount`.

**Sample output** — 90 rows in the full result; first five shown.

| row_id | order_id | status | old_discount_pct | new_discount_pct | rebate_amount |
| --- | --- | --- | --- | --- | --- |
| 1000 | ORD0001 | Delivered | 20.00 | 20.00 | 14802.00 |
| 1012 | ORD0005 | Delivered | 0.00 | 5.00 | 6003.90 |
| 1036 | ORD0013 | Delivered | 0.00 | 5.00 | 4076.20 |
| 1039 | ORD0014 | Delivered | 20.00 | 20.00 | 14565.00 |
| 1048 | ORD0017 | Delivered | 0.00 | 5.00 | 809.00 |

---

### Question 4

Write a named function and apply it to the `coupon_code` **Series** to create `coupon_clean`.

Missing or whitespace-only values become `NO_COUPON`. Otherwise strip surrounding spaces and uppercase the code. A valid code must have exactly three ASCII letters followed by exactly two digits, and the numeric suffix must be from 01 through 50 inclusive. Return the normalized code if valid; otherwise return `INVALID`.

Return `order_id`, `coupon_code`, `coupon_clean`, sorted by index ascending. Leave the raw column unchanged.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | order_id | coupon_code | coupon_clean |
| --- | --- | --- | --- |
| 1000 | ORD0001 | save10 | INVALID |
| 1003 | ORD0002 | &lt;missing&gt; | NO_COUPON |
| 1006 | ORD0003 | NEW00 | INVALID |
| 1009 | ORD0004 | A1B20 | INVALID |
| 1012 | ORD0005 | VIP75 | INVALID |

---

### Question 5

Use a named function with `orders.apply(..., axis=1)` to produce two columns in one call: `taxable_amount` and `invoice_total`.

For Cancelled orders both are 0. For all other statuses, taxable amount is `quantity × unit_price × (1 − discount_pct / 100)`, rounded to two decimals. Invoice total is that rounded taxable amount plus shipping fee minus refund, floored at zero and rounded to two decimals. Treat a missing refund as zero. The function must return a Series with the two named fields; add the result to `orders` by index alignment.

Return `order_id`, `status`, `quantity`, `unit_price`, `discount_pct`, `shipping_fee`, `refund_amount`, `taxable_amount`, `invoice_total`, sorted by index ascending.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | order_id | status | quantity | unit_price | discount_pct | shipping_fee | refund_amount | taxable_amount | invoice_total |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1000 | ORD0001 | Delivered | 5 | 14802.00 | 20.00 | 49.00 | 700.00 | 59208.00 | 58557.00 |
| 1003 | ORD0002 | Delivered | 1 | 17871.00 | 20.00 | 0.00 | &lt;missing&gt; | 14296.80 | 14296.80 |
| 1006 | ORD0003 | Cancelled | 5 | 3985.00 | 10.00 | 49.00 | 0.00 | 0.00 | 0.00 |
| 1009 | ORD0004 | Delivered | 6 | 14406.00 | 15.00 | 0.00 | 700.00 | 73470.60 | 72770.60 |
| 1012 | ORD0005 | Delivered | 6 | 20013.00 | 0.00 | 49.00 | 0.00 | 120078.00 | 120127.00 |

---

## DataFrame 2: `employees`

500 rows × 17 columns. Each row is one employee. Salary is monthly rupees; performance ratings run from 1 to 5. Missing values represent unavailable records. Skill tokens may use commas or pipes.

Run this setup cell:

```python
def make_employees():
    rng = np.random.default_rng(202)
    n = 500
    return pd.DataFrame({
        "employee_id": [f"EMP{i:04d}" for i in range(1, n + 1)],
        "department": rng.choice(["Data", "Engineering", "Sales", "Support", "HR"], n),
        "city": rng.choice(["Gurgaon", "Pune", "Hyderabad", "Chennai"], n),
        "grade": rng.choice(["Junior", "Mid", "Senior", "Intern"], n),
        "tenure_months": rng.integers(3, 73, n),
        "monthly_salary": rng.integers(25000, 160001, n).astype(float),
        "performance_rating": rng.choice([2.4, 2.9, 3.3, 3.8, 4.2, 4.5, 4.8, np.nan], n),
        "attendance_pct": rng.choice([85.0, 89.0, 92.0, 95.0, 97.0, 99.0, np.nan], n),
        "overtime_hours": rng.integers(0, 46, n),
        "leave_taken": rng.integers(0, 26, n),
        "leave_allowed": rng.choice([18, 21, 24], n),
        "training_hours": rng.integers(0, 41, n),
        "work_mode": rng.choice(["Office", "Hybrid", "Remote"], n),
        "manager_id": rng.choice(["M01", "M02", "M03", "M04", None], n),
        "skills_text": rng.choice([" Python | SQL | python ", "PY, Excel, SQL", " pandas | py | SQL ", "Excel,excel,Power BI", " postgres | SQL | Python ", " , | ", None, "Git | Docker, git"], n),
        "employment_status": rng.choice(["Active", "Notice", "Inactive"], n, p=[0.8, 0.12, 0.08]),
        "variable_pay": np.zeros(n),
    }, index=pd.Index(2000 + np.arange(n) * 5, name="row_id"))

employees = make_employees()
```

**Preview — first five rows, selected columns:**

| row_id | employee_id | department | grade | monthly_salary | performance_rating | attendance_pct |
| --- | --- | --- | --- | --- | --- | --- |
| 2000 | EMP0001 | Data | Senior | 140062.00 | 4.80 | 95.00 |
| 2005 | EMP0002 | Engineering | Senior | 49868.00 | 2.90 | 92.00 |
| 2010 | EMP0003 | Sales | Senior | 89938.00 | 3.80 | 95.00 |
| 2015 | EMP0004 | Sales | Senior | 78558.00 | 2.40 | 89.00 |
| 2020 | EMP0005 | Engineering | Junior | 70724.00 | &lt;missing&gt; | 95.00 |

---

### Question 6

Use an inclusive **index-label slice** from 2050 through 2400 with `loc`, then select Active employees in Data, Engineering or Support who are not Interns, have performance rating at least 3.3, and have either attendance below 92% or overtime above 24 hours.

Missing rating/attendance does not independently satisfy a comparison; the overtime branch may still qualify a row with missing attendance. Return `employee_id`, `department`, `grade`, `performance_rating`, `attendance_pct`, `overtime_hours`, sorted by index ascending. Do not treat the index labels as row positions.

**Sample output** — 9 rows in the full result; first five shown.

| row_id | employee_id | department | grade | performance_rating | attendance_pct | overtime_hours |
| --- | --- | --- | --- | --- | --- | --- |
| 2085 | EMP0018 | Engineering | Senior | 4.80 | 97.00 | 42 |
| 2105 | EMP0022 | Engineering | Junior | 3.30 | 99.00 | 37 |
| 2110 | EMP0023 | Engineering | Junior | 4.80 | 89.00 | 43 |
| 2115 | EMP0024 | Support | Senior | 3.80 | 85.00 | 5 |
| 2120 | EMP0025 | Support | Mid | 4.50 | 85.00 | 33 |

---

### Question 7

Update the original `employees` DataFrame through boolean `loc` assignments. Eligibility requires Active status, grade Junior/Mid/Senior, rating at least 4.2, attendance at least 95%, leave taken no greater than leave allowed, and overtime no greater than 30 hours. Missing required values make an employee ineligible.

Eligible Data/Engineering employees receive a 7% salary rise; other eligible departments receive 4%. Eligible Junior employees receive variable pay equal to 5% of **original annual salary**; eligible Mid/Senior employees receive 8%. Round money to two decimals. Ineligible rows must remain unchanged.

Return eligible rows only: `employee_id`, `department`, `grade`, `old_monthly_salary`, `new_monthly_salary`, `variable_pay`, sorted by index ascending. Calculate variable pay from the pre-increase salary.

**Sample output** — 23 rows in the full result; first five shown.

| row_id | employee_id | department | grade | old_monthly_salary | new_monthly_salary | variable_pay |
| --- | --- | --- | --- | --- | --- | --- |
| 2000 | EMP0001 | Data | Senior | 140062.00 | 149866.34 | 134459.52 |
| 2390 | EMP0079 | Sales | Senior | 78743.00 | 81892.72 | 75593.28 |
| 2420 | EMP0085 | Data | Senior | 93034.00 | 99546.38 | 89312.64 |
| 2445 | EMP0090 | Data | Senior | 151489.00 | 162093.23 | 145429.44 |
| 2610 | EMP0123 | Engineering | Senior | 67941.00 | 72696.87 | 65223.36 |

---

### Question 8

Create an independent copy of the Active-employee slice with overtime at least 25 hours. In that copy, reduce overtime by 5 hours, with a floor of zero. Increase training hours by 4 when performance rating is below 3.5 or missing; otherwise increase training hours by 2.

Sort the copy by index descending. Write both changed columns back to `employees` by index and column labels in **one** `loc` assignment. The left-hand column list must be `['overtime_hours', 'training_hours']`; the right-hand DataFrame must deliberately present `['training_hours', 'overtime_hours']`. Do not use `.values`, `.to_numpy()` or reset the index.

Return `employee_id` followed by old/new pairs for `overtime_hours` and `training_hours`, for the selected rows in ascending index order. Preserve all other data.

**Sample output** — 188 rows in the full result; first five shown.

| row_id | employee_id | old_overtime_hours | new_overtime_hours | old_training_hours | new_training_hours |
| --- | --- | --- | --- | --- | --- |
| 2010 | EMP0003 | 33 | 28 | 21 | 23 |
| 2020 | EMP0005 | 38 | 33 | 30 | 34 |
| 2050 | EMP0011 | 34 | 29 | 36 | 40 |
| 2055 | EMP0012 | 32 | 27 | 29 | 33 |
| 2060 | EMP0013 | 36 | 31 | 26 | 30 |

---

### Question 9

Write a named function and apply it to the `skills_text` Series to create `skills_clean`. Split tokens on commas or pipes, strip spaces, lowercase them, remove empty tokens, replace `py` with `python` and `postgres` with `sql`, then remove duplicates **after** these replacements. Sort tokens alphabetically and join with ` | `.

Missing input or no remaining tokens must produce `UNKNOWN`. Return `employee_id`, `skills_text`, `skills_clean`, sorted by index ascending. Preserve the raw text.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | employee_id | skills_text | skills_clean |
| --- | --- | --- | --- |
| 2000 | EMP0001 | PY, Excel, SQL | excel \| python \| sql |
| 2005 | EMP0002 | Excel,excel,Power BI | excel \| power bi |
| 2010 | EMP0003 | PY, Excel, SQL | excel \| python \| sql |
| 2015 | EMP0004 | Excel,excel,Power BI | excel \| power bi |
| 2020 | EMP0005 |  pandas \| py \| SQL  | pandas \| python \| sql |

---

### Question 10

Use a named row function with `apply(axis=1)` that returns a Series containing `decision` and `reason`. Apply the following rules in order; stop at the first match:

1. Status other than Active → `NOT_ELIGIBLE`, `STATUS`.
2. Missing manager → `MANUAL_REVIEW`, `NO_MANAGER`.
3. Missing rating or attendance → `INSUFFICIENT_DATA`, `MISSING_METRIC`.
4. Senior grade → `NO_OPEN_GRADE`, `SENIOR`.
5. Rating below 3 or attendance below 90% → `PERFORMANCE_PLAN`, `LOW_METRIC`.
6. Junior/Mid grade, tenure at least 24 months, rating at least 4.4, attendance at least 96%, training at least 20 hours and leave within allowance → `PROMOTE`, `ALL_CRITERIA`.
7. Otherwise → `DEVELOP`, `CRITERIA_NOT_MET`.

Add both outputs to `employees`. Return `employee_id`, `employment_status`, `manager_id`, `grade`, `performance_rating`, `attendance_pct`, `decision`, `reason`, sorted by index ascending.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | employee_id | employment_status | manager_id | grade | performance_rating | attendance_pct | decision | reason |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2000 | EMP0001 | Active | M02 | Senior | 4.80 | 95.00 | NO_OPEN_GRADE | SENIOR |
| 2005 | EMP0002 | Active | M03 | Senior | 2.90 | 92.00 | NO_OPEN_GRADE | SENIOR |
| 2010 | EMP0003 | Active | M03 | Senior | 3.80 | 95.00 | NO_OPEN_GRADE | SENIOR |
| 2015 | EMP0004 | Active | M03 | Senior | 2.40 | 89.00 | NO_OPEN_GRADE | SENIOR |
| 2020 | EMP0005 | Active | M04 | Junior | &lt;missing&gt; | 95.00 | INSUFFICIENT_DATA | MISSING_METRIC |

---

## DataFrame 3: `inventory`

500 rows × 17 columns. Each row is one SKU/warehouse record. Stock fields are units; demand is units/day; money is rupees. Some random records intentionally have reservations or damage exceeding stock. Keep negative availability unless a question explicitly floors it.

Run this setup cell:

```python
def make_inventory():
    rng = np.random.default_rng(303)
    n = 500
    cost = rng.integers(80, 2001, n).astype(float)
    return pd.DataFrame({
        "sku": [f"SKU{i:04d}" for i in range(1, n + 1)],
        "warehouse": rng.choice(["North", "South", "East", "West"], n),
        "category": rng.choice(["Food", "Electronics", "Cleaning", "Office"], n),
        "unit_cost": cost,
        "unit_price": np.round(cost * rng.uniform(1.05, 1.8, n), 2),
        "on_hand": rng.integers(0, 301, n),
        "reserved": rng.integers(0, 101, n),
        "inbound": rng.integers(0, 151, n),
        "avg_daily_demand": rng.choice([0.0, 2.0, 5.0, 8.0, 12.0, 20.0, np.nan], n),
        "lead_days": rng.integers(2, 22, n),
        "reorder_point": rng.integers(25, 151, n),
        "safety_stock": rng.integers(10, 61, n),
        "damaged_units": rng.integers(0, 21, n),
        "supplier_rating": rng.choice([2.5, 3.0, 3.8, 4.3, 4.8, np.nan], n),
        "hazardous": rng.choice([True, False], n, p=[0.15, 0.85]),
        "status": rng.choice(["Active", "Blocked", "Discontinued"], n, p=[0.8, 0.1, 0.1]),
        "supplier_code": rng.choice([" sup-041 ", "SUP-7", "SUP-000", "Vendor12", "sup-125", "SUP-1000", None, ""], n),
    }, index=pd.Index(3000 + np.arange(n) * 7, name="row_id"))

inventory = make_inventory()
```

**Preview — first five rows, selected columns:**

| row_id | sku | warehouse | category | on_hand | reserved | damaged_units | avg_daily_demand |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 3000 | SKU0001 | South | Electronics | 153 | 14 | 13 | 0.00 |
| 3007 | SKU0002 | South | Office | 198 | 67 | 9 | 0.00 |
| 3014 | SKU0003 | North | Electronics | 57 | 78 | 3 | 5.00 |
| 3021 | SKU0004 | South | Cleaning | 96 | 31 | 19 | 2.00 |
| 3028 | SKU0005 | North | Electronics | 102 | 16 | 10 | &lt;missing&gt; |

---

### Question 11

Using `loc`, select Active, non-hazardous records in North or West with known positive demand and either available units below the reorder point or fewer than 7 days of cover.

Available units are `on_hand − reserved − damaged_units`; do not floor negative values. Days of cover are available units divided by daily demand. Exclude zero/missing demand before deciding eligibility.

Return `sku`, `warehouse`, `on_hand`, `reserved`, `damaged_units`, `avg_daily_demand`, `reorder_point`, `available_units`, `days_cover`, sorted by index ascending. Round cover only for display; apply the threshold to the unrounded value.

**Sample output** — 61 rows in the full result; first five shown.

| row_id | sku | warehouse | on_hand | reserved | damaged_units | avg_daily_demand | reorder_point | available_units | days_cover |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3014 | SKU0003 | North | 57 | 78 | 3 | 5.00 | 25 | -24 | -4.80 |
| 3133 | SKU0020 | West | 150 | 52 | 7 | 12.00 | 110 | 91 | 7.58 |
| 3140 | SKU0021 | North | 46 | 39 | 13 | 20.00 | 126 | -6 | -0.30 |
| 3147 | SKU0022 | North | 142 | 81 | 18 | 2.00 | 66 | 43 | 21.50 |
| 3168 | SKU0025 | North | 40 | 47 | 8 | 2.00 | 47 | -15 | -7.50 |

---

### Question 12

Update `inventory` itself using boolean masks on the left-hand side:

- For Active records whose reservations exceed usable capacity, set `reserved` to `max(0, on_hand − damaged_units)`.
- For Active records with known positive demand and supplier rating at least 3.8, set `reorder_point` to the greater of its original value and `ceil(avg_daily_demand × lead_days + safety_stock)`. Never reduce it.

Evaluate both masks from the original data. Preserve other columns and records outside both masks. Return all records eligible for either rule, even if the reorder point does not change: `sku`, `status`, then old/new pairs for `reserved` and `reorder_point`, sorted by index ascending.

**Sample output** — 180 rows in the full result; first five shown.

| row_id | sku | status | old_reserved | new_reserved | old_reorder_point | new_reorder_point |
| --- | --- | --- | --- | --- | --- | --- |
| 3014 | SKU0003 | Active | 78 | 54 | 25 | 110 |
| 3035 | SKU0006 | Active | 30 | 30 | 80 | 126 |
| 3049 | SKU0008 | Active | 3 | 3 | 150 | 150 |
| 3063 | SKU0010 | Active | 82 | 8 | 90 | 91 |
| 3140 | SKU0021 | Active | 39 | 33 | 126 | 126 |

---

### Question 13

Create an independent slice of Active Food/Cleaning records with `on_hand > 200`, known daily demand from 0 through 5 inclusive, and unit price at least 115% of unit cost.

Inside the slice, reduce unit price by 8%, but never below 115% of unit cost; round the final price to two decimals. Add `margin_pct = (updated unit_price − unit_cost) / updated unit_price × 100`, rounded to two decimals. Sort the slice by its updated price descending.

Write only `unit_price` back to the original DataFrame through `loc`, using the slice's index labels and a labeled DataFrame on the right. The original must not receive `margin_pct`. Return selected rows in ascending index order: `sku`, `unit_cost`, `old_unit_price`, `new_unit_price`, `margin_pct`.

**Sample output** — 17 rows in the full result; first five shown.

| row_id | sku | unit_cost | old_unit_price | new_unit_price | margin_pct |
| --- | --- | --- | --- | --- | --- |
| 3084 | SKU0013 | 1324.00 | 2218.67 | 2041.18 | 35.14 |
| 3497 | SKU0072 | 1618.00 | 2010.21 | 1860.70 | 13.04 |
| 3623 | SKU0090 | 1558.00 | 2222.52 | 2044.72 | 23.80 |
| 3742 | SKU0107 | 344.00 | 547.96 | 504.12 | 31.76 |
| 4365 | SKU0196 | 987.00 | 1627.40 | 1497.21 | 34.08 |

---

### Question 14

Apply a named function to the `supplier_code` Series. Produce `supplier_clean` according to these rules:

Missing/blank input → `UNKNOWN`. Otherwise strip spaces and uppercase. Accept only `SUP-` followed by one to three ASCII digits representing a number from 1 through 999. Normalize accepted codes to three digits, for example `sup-7` → `SUP-007`. Reject zero, four-digit suffixes, wrong prefixes and extra characters as `INVALID`.

Return `sku`, `supplier_code`, `supplier_clean`, sorted by index ascending. Preserve the raw column.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | sku | supplier_code | supplier_clean |
| --- | --- | --- | --- |
| 3000 | SKU0001 | sup-125 | SUP-125 |
| 3007 | SKU0002 | Vendor12 | INVALID |
| 3014 | SKU0003 |  sup-041  | SUP-041 |
| 3021 | SKU0004 | SUP-7 | SUP-007 |
| 3028 | SKU0005 | SUP-000 | INVALID |

---

### Question 15

Write a named row function and use `inventory.apply(..., axis=1)` to return a Series containing integer `recommended_qty` and string `action`. Apply these rules in order:

1. Non-Active status → quantity 0, `BLOCKED`.
2. Missing demand → quantity 0, `CHECK_DEMAND`.
3. Zero demand → quantity 0, `NO_DEMAND`.
4. Otherwise calculate projected stock as `max(0, on_hand − reserved − damaged_units) + inbound`, target stock as `ceil(demand × lead_days + safety_stock)`, and gap as `max(0, target − projected stock)`. Zero gap → quantity 0, `HOLD`.
5. With a positive gap, missing supplier rating, rating below 3, or hazardous stock → quantity 0, `MANUAL_REVIEW`.
6. Otherwise → `ORDER`, with quantity equal to the gap rounded **up** to a multiple of 12 for Food or 10 for every other category.

Add both columns to `inventory`. Return `sku`, `category`, `status`, `avg_daily_demand`, `supplier_rating`, `hazardous`, `recommended_qty`, `action`, sorted by index ascending.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | sku | category | status | avg_daily_demand | supplier_rating | hazardous | recommended_qty | action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3000 | SKU0001 | Electronics | Active | 0.00 | &lt;missing&gt; | False | 0 | NO_DEMAND |
| 3007 | SKU0002 | Office | Active | 0.00 | &lt;missing&gt; | False | 0 | NO_DEMAND |
| 3014 | SKU0003 | Electronics | Active | 5.00 | 4.30 | False | 90 | ORDER |
| 3021 | SKU0004 | Cleaning | Blocked | 2.00 | 4.30 | False | 0 | BLOCKED |
| 3028 | SKU0005 | Electronics | Active | &lt;missing&gt; | 3.00 | True | 0 | CHECK_DEMAND |

---

## DataFrame 4: `tickets`

500 rows × 16 columns. Each row is one support ticket. All durations are hours; monetary amounts are rupees. A missing first-response value means no response recorded. CSAT runs from 1 to 5.

Run this setup cell:

```python
def make_tickets():
    rng = np.random.default_rng(404)
    n = 500
    return pd.DataFrame({
        "ticket_id": [f"TKT{i:04d}" for i in range(1, n + 1)],
        "customer_tier": rng.choice(["Gold", "Silver", "Standard"], n),
        "channel": rng.choice(["Email", "Chat", "Phone"], n),
        "issue_type": rng.choice(["Payment", "Delivery", "Login", "Refund", "Product"], n),
        "status": rng.choice(["Open", "Pending", "Resolved", "Closed"], n, p=[0.35, 0.25, 0.25, 0.15]),
        "priority": rng.choice(["Low", "Medium", "High", "Critical"], n),
        "age_hours": rng.integers(1, 121, n).astype(float),
        "first_response_hours": rng.choice([0.5, 2.0, 4.0, 8.0, 16.0, np.nan], n),
        "sla_hours": rng.choice([4.0, 8.0, 24.0, 48.0], n),
        "reopen_count": rng.integers(0, 5, n),
        "refund_requested": rng.choice([0.0, 300.0, 1500.0, 6000.0, np.nan], n),
        "order_value": rng.integers(200, 10001, n).astype(float),
        "agent_team": rng.choice(["General", "Payments", "Logistics", "Technical"], n),
        "csat": rng.choice([1.0, 2.0, 3.0, 4.0, 5.0, np.nan], n),
        "tags_text": rng.choice([" urgent ; REFUND ; urgent ", "vip, payment", " Login ; PASSWORD ", "spam;vip", "urgent,,delivery", " ; , ", None, "refund; VIP,refund"], n),
        "compensation": np.zeros(n),
    }, index=pd.Index(4000 + np.arange(n) * 11, name="row_id"))

tickets = make_tickets()
```

**Preview — first five rows, selected columns:**

| row_id | ticket_id | customer_tier | issue_type | status | priority | age_hours | sla_hours |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4000 | TKT0001 | Standard | Product | Resolved | High | 24.00 | 24.00 |
| 4011 | TKT0002 | Gold | Payment | Open | Medium | 26.00 | 48.00 |
| 4022 | TKT0003 | Silver | Login | Closed | Critical | 22.00 | 8.00 |
| 4033 | TKT0004 | Silver | Refund | Open | High | 23.00 | 48.00 |
| 4044 | TKT0005 | Standard | Refund | Resolved | Critical | 20.00 | 24.00 |

---

### Question 16

Using `loc`, extract Open/Pending tickets that meet all of the following:

- Gold customer **or** Critical priority.
- At least one breach: age exceeds SLA, no first response is recorded, or first-response time exceeds one quarter of the SLA.
- Issue type is not Login.
- At least two reopens **or** known CSAT at most 2.

Missing CSAT does not satisfy the CSAT condition. Return `ticket_id`, `customer_tier`, `priority`, `age_hours`, `sla_hours`, `first_response_hours`, `reopen_count`, `csat`, sorted by index ascending.

**Sample output** — 86 rows in the full result; first five shown.

| row_id | ticket_id | customer_tier | priority | age_hours | sla_hours | first_response_hours | reopen_count | csat |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4055 | TKT0006 | Gold | High | 42.00 | 4.00 | 8.00 | 3 | 4.00 |
| 4330 | TKT0031 | Silver | Critical | 5.00 | 8.00 | &lt;missing&gt; | 4 | &lt;missing&gt; |
| 4352 | TKT0033 | Gold | Medium | 106.00 | 24.00 | 0.50 | 2 | &lt;missing&gt; |
| 4385 | TKT0036 | Gold | Medium | 48.00 | 8.00 | 2.00 | 3 | 3.00 |
| 4517 | TKT0048 | Gold | High | 98.00 | 24.00 | 8.00 | 3 | 1.00 |

---

### Question 17

Update `tickets` using boolean `loc` assignments. Determine all eligibility from original values:

1. For Open/Pending tickets, set priority to Critical when either a Gold customer's age exceeds SLA, or the reopen count is at least 3.
2. Among other Open/Pending tickets, promote Low/Medium priority to High when first response is missing and age exceeds half the SLA. Preserve existing High/Critical priorities.
3. For Resolved Delivery/Refund tickets with known CSAT at most 2, set compensation to 10% of order value, capped at ₹500 and rounded to two decimals.

Rule 1 takes precedence over rule 2. Preserve every other value. Return every row matched by any rule: `ticket_id`, `status`, `old_priority`, `new_priority`, `old_compensation`, `new_compensation`, sorted by index ascending.

**Sample output** — 180 rows in the full result; first five shown.

| row_id | ticket_id | status | old_priority | new_priority | old_compensation | new_compensation |
| --- | --- | --- | --- | --- | --- | --- |
| 4011 | TKT0002 | Open | Medium | High | 0.00 | 0.00 |
| 4044 | TKT0005 | Resolved | Critical | Critical | 0.00 | 500.00 |
| 4055 | TKT0006 | Open | High | Critical | 0.00 | 0.00 |
| 4066 | TKT0007 | Open | Medium | Critical | 0.00 | 0.00 |
| 4088 | TKT0009 | Open | Low | Critical | 0.00 | 0.00 |

---

### Question 18

Make an independent slice of Open/Pending Payment/Refund tickets with a known positive refund request. Inside the slice, cap the request at order value, round it to two decimals, and set `agent_team` to Payments. Set priority to Critical when the **capped** request exceeds ₹4,000 or age exceeds SLA; otherwise preserve the original priority.

Add `excess_removed = original refund request − capped refund request`. Shuffle the slice with `sample(frac=1, random_state=41)`. Write back only `refund_requested`, `agent_team`, `priority`, in one labeled `loc` assignment. The right-hand DataFrame must have a different column order: `priority`, `refund_requested`, `agent_team`.

Keep `excess_removed` out of the original. Return selected rows sorted by index ascending: `ticket_id`, `order_value`, `old_refund_requested`, `new_refund_requested`, `agent_team`, `priority`, `excess_removed`.

**Sample output** — 63 rows in the full result; first five shown.

| row_id | ticket_id | order_value | old_refund_requested | new_refund_requested | agent_team | priority | excess_removed |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4011 | TKT0002 | 5028.00 | 1500.00 | 1500.00 | Payments | Medium | 0.00 |
| 4033 | TKT0004 | 8953.00 | 6000.00 | 6000.00 | Payments | Critical | 0.00 |
| 4154 | TKT0015 | 4927.00 | 1500.00 | 1500.00 | Payments | Critical | 0.00 |
| 4209 | TKT0020 | 6773.00 | 6000.00 | 6000.00 | Payments | Critical | 0.00 |
| 4242 | TKT0023 | 8373.00 | 300.00 | 300.00 | Payments | Critical | 0.00 |

---

### Question 19

Apply a named function to the `tags_text` Series to create `tags_clean`. Split on semicolons or commas, trim and lowercase tokens, remove empty tokens and duplicates. If `spam` appears, return `SPAM` immediately, regardless of other tags.

Otherwise keep only `vip`, `urgent`, `refund`, `payment`, `login`, `password`, `delivery`. Put `vip` first when present and `urgent` second when present; sort all remaining allowed tags alphabetically. Join using ` | `. Missing input or no retained tokens becomes `UNTAGGED`.

Return `ticket_id`, `tags_text`, `tags_clean`, sorted by index ascending. Do not change the raw column.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | ticket_id | tags_text | tags_clean |
| --- | --- | --- | --- |
| 4000 | TKT0001 | &lt;missing&gt; | UNTAGGED |
| 4011 | TKT0002 |  Login ; PASSWORD  | login \| password |
| 4022 | TKT0003 |  urgent ; REFUND ; urgent  | urgent \| refund |
| 4033 | TKT0004 |  ; ,  | UNTAGGED |
| 4044 | TKT0005 |  Login ; PASSWORD  | login \| password |

---

### Question 20

Use a named row function with `tickets.apply(..., axis=1)` to create `next_queue`. The first matching rule wins:

1. Resolved/Closed → `ARCHIVE`.
2. Critical priority or at least 3 reopens → `ESCALATION`.
3. Payment/Refund issue: missing request → `VERIFY_REFUND`; request above order value → `FRAUD_REVIEW`; otherwise → `PAYMENTS`.
4. Delivery issue → `LOGISTICS`.
5. Login issue → `TECHNICAL`.
6. Gold customer with no first response or first-response time above one quarter of SLA → `VIP_DESK`.
7. Otherwise → `GENERAL`.

Return `ticket_id`, `status`, `priority`, `issue_type`, `reopen_count`, `refund_requested`, `order_value`, `next_queue`, sorted by index ascending. Use original priorities, not Question 17's updated ones.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | ticket_id | status | priority | issue_type | reopen_count | refund_requested | order_value | next_queue |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4000 | TKT0001 | Resolved | High | Product | 1 | 6000.00 | 9445.00 | ARCHIVE |
| 4011 | TKT0002 | Open | Medium | Payment | 0 | 1500.00 | 5028.00 | PAYMENTS |
| 4022 | TKT0003 | Closed | Critical | Login | 3 | 0.00 | 5127.00 | ARCHIVE |
| 4033 | TKT0004 | Open | High | Refund | 0 | 6000.00 | 8953.00 | PAYMENTS |
| 4044 | TKT0005 | Resolved | Critical | Refund | 3 | 300.00 | 8609.00 | ARCHIVE |

---

## DataFrame 5: `memberships`

500 rows × 17 columns. Each row is one member. Money is rupees; `offer_pct` is a percentage from 0 to 100. All date comparisons use the fixed reference date `AS_OF = 2026-10-01`. Consent controls whether outreach is permitted in this fictional exercise.

Run this setup cell:

```python
def make_memberships():
    rng = np.random.default_rng(505)
    n = 500
    return pd.DataFrame({
        "member_id": [f"MEM{i:04d}" for i in range(1, n + 1)],
        "plan": rng.choice(["Basic", "Plus", "Premium"], n),
        "city": rng.choice(["Delhi", "Mumbai", "Pune", "Ahmedabad"], n),
        "signup_date": pd.Timestamp("2025-01-01") + pd.to_timedelta(rng.integers(0, 600, n), unit="D"),
        "renewal_date": pd.Timestamp("2026-09-01") + pd.to_timedelta(rng.integers(0, 70, n), unit="D"),
        "monthly_fee": rng.choice([499.0, 999.0, 1999.0], n),
        "visits_last_30d": rng.integers(0, 21, n),
        "visits_prev_30d": rng.integers(0, 21, n),
        "days_since_last_visit": rng.integers(0, 91, n),
        "payment_failures": rng.integers(0, 4, n),
        "auto_renew": rng.choice([True, False], n),
        "acquisition_channel": rng.choice(["Referral", "Ads", "Organic", "Partner"], n),
        "status": rng.choice(["Active", "Paused", "Cancelled"], n, p=[0.75, 0.15, 0.1]),
        "consent": rng.choice([True, False], n, p=[0.8, 0.2]),
        "satisfaction": rng.choice([1.0, 2.0, 3.0, 4.0, 5.0, np.nan], n),
        "offer_pct": np.zeros(n),
        "contact_preference": rng.choice([" sms ; EMAIL ", "WhatsApp,email,whatsapp", "push | SMS", "none;email", " ; | , ", None, "email;push;EMAIL"], n),
    }, index=pd.Index(5000 + np.arange(n) * 13, name="row_id"))

memberships = make_memberships()
AS_OF = pd.Timestamp("2026-10-01")
```

**Preview — first five rows, selected columns:**

| row_id | member_id | plan | status | renewal_date | visits_last_30d | visits_prev_30d | payment_failures |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5000 | MEM0001 | Premium | Active | 2026-10-06 | 0 | 10 | 3 |
| 5013 | MEM0002 | Premium | Paused | 2026-09-20 | 13 | 8 | 2 |
| 5026 | MEM0003 | Basic | Active | 2026-10-07 | 9 | 13 | 0 |
| 5039 | MEM0004 | Premium | Active | 2026-09-30 | 15 | 13 | 0 |
| 5052 | MEM0005 | Premium | Active | 2026-11-09 | 11 | 18 | 0 |

---

### Question 21

Using `loc`, select Active, consenting Plus/Premium members whose renewal date is from **1 October through 14 October 2026, inclusive**, and who either:

- made at least 4 visits in the previous 30 days and now have at most half as many visits, or
- have at least 2 payment failures.

Return `member_id`, `plan`, `renewal_date`, `visits_prev_30d`, `visits_last_30d`, `payment_failures`, sorted by index ascending. A previous count of zero must not qualify through the decline branch.

**Sample output** — 30 rows in the full result; first five shown.

| row_id | member_id | plan | renewal_date | visits_prev_30d | visits_last_30d | payment_failures |
| --- | --- | --- | --- | --- | --- | --- |
| 5000 | MEM0001 | Premium | 2026-10-06 | 10 | 0 | 3 |
| 5130 | MEM0011 | Plus | 2026-10-01 | 14 | 6 | 0 |
| 5468 | MEM0037 | Plus | 2026-10-05 | 0 | 14 | 2 |
| 5663 | MEM0052 | Premium | 2026-10-11 | 19 | 19 | 2 |
| 5741 | MEM0058 | Premium | 2026-10-11 | 13 | 3 | 2 |

---

### Question 22

Set `offer_pct` directly on `memberships` through boolean `loc` assignments. Eligibility requires Active status, consent, zero payment failures, and renewal from **24 September through 15 October 2026, inclusive**.

Among eligible members, a high-risk member either has at least 4 previous visits and now at most half as many visits, or has not visited for more than 21 days. Assign 15% to high-risk Plus/Premium members and 10% to high-risk Basic members.

For eligible members who are **not** high-risk, assign 5% only if days since last visit exceed 14 and current visits are below previous visits. These are moderate-risk members. Preserve offers for everyone else. Determine the masks from original values.

Return members assigned an offer: `member_id`, `plan`, `renewal_date`, `visits_prev_30d`, `visits_last_30d`, `days_since_last_visit`, `offer_pct`, plus a reporting-only `offer_band` of `HIGH` or `MODERATE`, sorted by index ascending.

**Sample output** — 19 rows in the full result; first five shown.

| row_id | member_id | plan | renewal_date | visits_prev_30d | visits_last_30d | days_since_last_visit | offer_pct | offer_band |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5026 | MEM0003 | Basic | 2026-10-07 | 13 | 9 | 52 | 10.00 | HIGH |
| 5130 | MEM0011 | Plus | 2026-10-01 | 14 | 6 | 77 | 15.00 | HIGH |
| 6053 | MEM0082 | Basic | 2026-10-03 | 5 | 20 | 55 | 10.00 | HIGH |
| 6079 | MEM0084 | Basic | 2026-10-08 | 16 | 13 | 85 | 10.00 | HIGH |
| 7080 | MEM0161 | Plus | 2026-10-11 | 10 | 11 | 75 | 15.00 | HIGH |

---

### Question 23

Take an independent copy of Active/Paused members whose renewal date is **before** `AS_OF` and who have at least one payment failure. In the copy, set status to Paused, auto-renew to False and offer percentage to zero.

Add a proposed `recovery_fee`: 95% of monthly fee for exactly one failure, otherwise 90%, rounded to two decimals. This proposed fee must remain only in the copy; do not change `monthly_fee` in the original.

Sort the copy by index descending, then write back only `status`, `auto_renew`, `offer_pct` using index-aligned `loc` assignment. Return selected rows in ascending index order: `member_id`, `old_status`, `new_status`, `old_auto_renew`, `new_auto_renew`, `offer_pct`, `recovery_fee`.

**Sample output** — 124 rows in the full result; first five shown.

| row_id | member_id | old_status | new_status | old_auto_renew | new_auto_renew | offer_pct | recovery_fee |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5013 | MEM0002 | Paused | Paused | True | False | 0.00 | 1799.10 |
| 5156 | MEM0013 | Paused | Paused | False | False | 0.00 | 449.10 |
| 5182 | MEM0015 | Active | Paused | False | False | 0.00 | 449.10 |
| 5195 | MEM0016 | Active | Paused | True | False | 0.00 | 899.10 |
| 5221 | MEM0018 | Active | Paused | True | False | 0.00 | 899.10 |

---

### Question 24

Apply a named function to the `contact_preference` Series to create `contact_clean`. Accept semicolons, commas and pipes as separators; strip and lowercase tokens; remove blanks and duplicates.

If the token `none` is present, return `NO_CONTACT` regardless of other tokens. Otherwise retain only `whatsapp`, `email`, `sms`, `push`, ordered by that exact preference sequence, and join them using ` > `. Missing input or no valid retained channels becomes `UNKNOWN`.

Return `member_id`, `contact_preference`, `contact_clean`, sorted by index ascending. This question cleans preference text only; do not use the separate consent flag to alter the cleaned output.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | member_id | contact_preference | contact_clean |
| --- | --- | --- | --- |
| 5000 | MEM0001 | push \| SMS | sms &gt; push |
| 5013 | MEM0002 | email;push;EMAIL | email &gt; push |
| 5026 | MEM0003 |  sms ; EMAIL  | email &gt; sms |
| 5039 | MEM0004 | none;email | NO_CONTACT |
| 5052 | MEM0005 | none;email | NO_CONTACT |

---

### Question 25

Use a named function with `memberships.apply(..., axis=1)` to return a Series containing `risk_score`, `risk_band`, `next_action`. Use the untouched original dataset.

For non-Active members, return missing score, `NOT_ACTIVE`, `NONE`. For Active members calculate:

- Decline fraction = `max(0, (previous visits − current visits) / previous visits)`; use 0 when previous visits are 0.
- Start with `ceil(40 × decline fraction)`.
- Add 30 if current visits are 0 **or** days since last visit are at least 30; otherwise add 15 if days since last visit are at least 14. Do not add both inactivity penalties.
- Add 20 if there is any payment failure.
- Add 10 if satisfaction is known and at most 2; missing satisfaction adds 0.
- Cap the score at 100. Scores at least 60 → `HIGH`; otherwise at least 30 → `MEDIUM`; otherwise → `LOW`.

Choose the next action by the first matching rule: no consent → `NO_CONTACT`; any payment failure → `UPDATE_PAYMENT`; HIGH risk with renewal on/before **15 October 2026** → `HUMAN_CALL` (overdue dates also qualify); any remaining HIGH/MEDIUM risk → `ENGAGEMENT_NUDGE`; otherwise → `MONITOR`.

Add all three columns to `memberships`. Return `member_id`, `status`, `visits_prev_30d`, `visits_last_30d`, `days_since_last_visit`, `payment_failures`, `satisfaction`, `consent`, `risk_score`, `risk_band`, `next_action`, sorted by index ascending.

**Sample output** — 500 rows in the full result; first five shown.

| row_id | member_id | status | visits_prev_30d | visits_last_30d | days_since_last_visit | payment_failures | satisfaction | consent | risk_score | risk_band | next_action |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5000 | MEM0001 | Active | 10 | 0 | 71 | 3 | 3.00 | True | 90.00 | HIGH | UPDATE_PAYMENT |
| 5013 | MEM0002 | Paused | 8 | 13 | 53 | 2 | 2.00 | True | &lt;missing&gt; | NOT_ACTIVE | NONE |
| 5026 | MEM0003 | Active | 13 | 9 | 52 | 0 | 4.00 | True | 43.00 | MEDIUM | ENGAGEMENT_NUDGE |
| 5039 | MEM0004 | Active | 13 | 15 | 19 | 0 | 5.00 | True | 15.00 | LOW | MONITOR |
| 5052 | MEM0005 | Active | 18 | 11 | 46 | 0 | 2.00 | True | 56.00 | MEDIUM | ENGAGEMENT_NUDGE |
