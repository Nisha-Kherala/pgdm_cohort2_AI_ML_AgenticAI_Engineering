PRAGMA foreign_keys = ON;
CREATE TABLE periods(period_id TEXT PRIMARY KEY, period_label TEXT NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('previous','current')));
CREATE TABLE channels(channel_id TEXT PRIMARY KEY, channel_name TEXT NOT NULL);
CREATE TABLE customers(customer_id TEXT PRIMARY KEY, segment TEXT NOT NULL CHECK(segment IN ('Business','Retail-Core','Retail-Plus','Student')), city TEXT NOT NULL, region TEXT NOT NULL, signup_date TEXT NOT NULL);
CREATE TABLE orders(order_id TEXT PRIMARY KEY, customer_id TEXT NOT NULL REFERENCES customers(customer_id), period_id TEXT NOT NULL REFERENCES periods(period_id), order_date TEXT NOT NULL, channel_id TEXT NOT NULL REFERENCES channels(channel_id), status TEXT NOT NULL CHECK(status IN ('COMPLETED','CANCELLED')), gross_amount INTEGER NOT NULL CHECK(gross_amount>=0), discount_amount INTEGER NOT NULL CHECK(discount_amount>=0), refund_amount INTEGER NOT NULL CHECK(refund_amount>=0), CHECK(gross_amount>=discount_amount+refund_amount));
CREATE TABLE order_costs(order_id TEXT PRIMARY KEY REFERENCES orders(order_id),product_cost INTEGER NOT NULL CHECK(product_cost>=0),fulfilment_cost INTEGER NOT NULL CHECK(fulfilment_cost>=0),payment_cost INTEGER NOT NULL CHECK(payment_cost>=0));
CREATE TABLE marketing_spend(spend_id TEXT PRIMARY KEY,period_id TEXT NOT NULL REFERENCES periods(period_id),month_start TEXT NOT NULL,channel_id TEXT NOT NULL REFERENCES channels(channel_id),purpose TEXT NOT NULL CHECK(purpose IN ('Acquisition','Retention')),amount INTEGER NOT NULL CHECK(amount>=0),UNIQUE(period_id,month_start,channel_id,purpose));
CREATE INDEX idx_orders_period_status ON orders(period_id,status);
CREATE INDEX idx_orders_customer ON orders(customer_id);
CREATE VIEW eligible_orders AS
SELECT order_id,customer_id,period_id,order_date,channel_id,
       gross_amount-discount_amount-refund_amount AS net_revenue
FROM orders WHERE status='COMPLETED';
