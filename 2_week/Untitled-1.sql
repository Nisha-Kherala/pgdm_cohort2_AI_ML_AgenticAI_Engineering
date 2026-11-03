-- ALTER TABLE orders
-- ADD COLUMN order_date DATE;

-- UPDATE orders
-- SET order_date = CASE order_id
--     WHEN 'O01' THEN '2026-09-01'
--     WHEN 'O02' THEN '2026-09-03'
--     WHEN 'O03' THEN '2026-09-01'
--     WHEN 'O04' THEN '2026-09-02'
--     WHEN 'O05' THEN '2026-09-01'
-- END;

-- INSERT INTO orders (order_id, member_id, amount, order_date)
-- VALUES
--     ('O06', 'M01', 700, '2026-09-05'),
--     ('O07', 'M02', 400, '2026-09-03'),
--     ('O08', 'M03', 600, '2026-09-04'),
--     ('O09', 'M05', 300, '2026-09-02'),
--     ('O10', 'M01', 200, '2026-09-07'),
--     ('O11', 'M02', 900, '2026-09-06'),
--     ('O12', 'M03', 500, '2026-09-08'),
--     ('O13', 'M05', 800, '2026-09-05');

-- SELECT *
-- FROM orders
-- ORDER BY member_id, order_date;

