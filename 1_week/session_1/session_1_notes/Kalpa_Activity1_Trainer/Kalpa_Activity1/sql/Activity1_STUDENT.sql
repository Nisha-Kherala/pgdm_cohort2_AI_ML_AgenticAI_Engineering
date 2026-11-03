-- Student scaffold: write the missing queries; no answer values are supplied.
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
