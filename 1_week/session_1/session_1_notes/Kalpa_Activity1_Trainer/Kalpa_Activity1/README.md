# Kalpa Retail: Activity 1 — Outcome

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
