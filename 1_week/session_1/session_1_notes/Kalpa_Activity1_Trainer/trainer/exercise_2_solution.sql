-- Aggregate each grain separately BEFORE joining. Spend has multiple rows per period.
WITH revenue AS (
    SELECT period_id, SUM(net_revenue) AS revenue
    FROM eligible_orders GROUP BY period_id
), order_expenses AS (
    SELECT o.period_id, SUM(c.product_cost) AS product_cost,
           SUM(c.fulfilment_cost) AS fulfilment_cost,
           SUM(c.payment_cost) AS payment_cost
    FROM orders o JOIN order_costs c ON c.order_id = o.order_id
    GROUP BY o.period_id
), marketing AS (
    SELECT period_id, SUM(amount) AS marketing_cost
    FROM marketing_spend GROUP BY period_id
)
SELECT p.period_label, r.revenue, c.product_cost, c.fulfilment_cost,
       c.payment_cost, m.marketing_cost,
       c.product_cost+c.fulfilment_cost+c.payment_cost+m.marketing_cost AS total_cost,
       r.revenue-c.product_cost-c.fulfilment_cost-c.payment_cost-m.marketing_cost AS contribution,
       ROUND(100.0*(r.revenue-c.product_cost-c.fulfilment_cost-c.payment_cost-m.marketing_cost)/r.revenue,2) AS contribution_margin_pct,
       CASE WHEN 1.0*(r.revenue-c.product_cost-c.fulfilment_cost-c.payment_cost-m.marketing_cost)/r.revenue >= 0.20 THEN 'MET' ELSE 'BREACHED' END AS margin_floor
FROM revenue r JOIN order_expenses c ON c.period_id=r.period_id
JOIN marketing m ON m.period_id=r.period_id
JOIN periods p ON p.period_id=r.period_id
ORDER BY p.period_id;
