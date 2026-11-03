-- Trainer solution. All money is whole INR. The view filters completed orders.
SELECT p.period_label,
       COUNT(*) AS completed_orders,
       COUNT(DISTINCT o.customer_id) AS purchasing_customers,
       SUM(o.net_revenue) AS revenue,
       ROUND(1.0 * COUNT(*) / COUNT(DISTINCT o.customer_id), 4) AS orders_per_customer,
       ROUND(1.0 * SUM(o.net_revenue) / COUNT(*), 2) AS revenue_per_order
FROM eligible_orders o
JOIN periods p ON p.period_id = o.period_id
GROUP BY p.period_id, p.period_label
ORDER BY p.period_id;
