"""Generate a reproducible synthetic relational teaching dataset (whole INR)."""
from pathlib import Path
from datetime import date, timedelta
import csv, json, sqlite3, random, math, shutil, zipfile, hashlib
import numpy as np

ROOT = Path(__file__).resolve().parent
PACK = ROOT / 'Kalpa_Activity1'
DATA = PACK / 'data'
TRAINER = ROOT / 'trainer'
for p in (DATA, PACK / 'sql', PACK / 'notebooks', PACK / 'tools', TRAINER):
    p.mkdir(parents=True, exist_ok=True)
SEED = 20261005
rng = np.random.default_rng(SEED)
random.seed(SEED)
TABLES = {}

def allocate(total, weights, minimum=0):
    """Largest-remainder allocation, preserving an exact integer total."""
    weights = np.asarray(weights, dtype=float)
    remaining = int(total) - minimum * len(weights)
    assert remaining >= 0
    values = weights / weights.sum() * remaining
    result = np.floor(values).astype(np.int64) + minimum
    residual = int(total) - int(result.sum())
    if residual:
        ix = np.argsort(-(values - np.floor(values)), kind='stable')[:residual]
        result[ix] += 1
    assert int(result.sum()) == total
    return result

def write_csv(name, rows):
    TABLES[name] = rows
    with (DATA / (name + '.csv')).open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)

periods = [
    dict(period_id='FY2024_25', period_label='FY 2024-25', start_date='2024-04-01', end_date='2025-03-31', role='previous'),
    dict(period_id='FY2025_26', period_label='FY 2025-26', start_date='2025-04-01', end_date='2026-03-31', role='current'),
]
write_csv('periods', periods)
write_csv('channels', [dict(channel_id='APP', channel_name='Mobile app'), dict(channel_id='WEB', channel_name='Website'), dict(channel_id='STORE', channel_name='Physical store')])

segments = ['Business', 'Retail-Core', 'Retail-Plus', 'Student']
previous_n = [500, 5500, 3000, 1000]
retained_n = [450, 4200, 1600, 750]
new_n = [300, 3300, 1500, 900]
previous = {}; current = {}; customer_segment = {}
next_id = 1
for seg, n, retained in zip(segments, previous_n, retained_n):
    ids = [f'C{i:06d}' for i in range(next_id, next_id+n)]
    next_id += n; previous[seg] = ids
    current[seg] = list(rng.choice(ids, retained, replace=False))
    customer_segment.update({x: seg for x in ids})
for seg, n in zip(segments, new_n):
    ids = [f'C{i:06d}' for i in range(next_id, next_id+n)]
    next_id += n; current[seg] += ids
    customer_segment.update({x: seg for x in ids})
for i in range(next_id, 18001):
    customer_segment[f'C{i:06d}'] = random.choices(segments, [5,55,30,10])[0]
locations = [('Delhi','North'),('Gurugram','North'),('Mumbai','West'),('Pune','West'),('Bengaluru','South'),('Chennai','South'),('Hyderabad','South'),('Kolkata','East'),('Ahmedabad','West'),('Lucknow','North')]
customers = []
for cid, seg in sorted(customer_segment.items()):
    city, region = random.choice(locations)
    registered = date(2022,1,1) + timedelta(days=random.randrange(810))
    customers.append(dict(customer_id=cid, segment=seg, city=city, region=region, signup_date=registered.isoformat()))
write_csv('customers', customers)

order_targets = [[5000,27500,15000,2500], [6000,31500,10500,4000]]
revenue_targets = [[500_000_000,300_000_000,180_000_000,20_000_000], [580_000_000,325_000_000,110_000_000,25_000_000]]
orders = []; net_by_id = {}
for pi, period in enumerate(periods):
    buyers = previous if pi == 0 else current
    start = date.fromisoformat(period['start_date'])
    for si, seg in enumerate(segments):
        ids = buyers[seg]
        # Different customers have genuinely different purchase frequencies.
        weights = rng.lognormal(0, 0.85 if seg != 'Business' else 0.6, len(ids))
        counts = 1 + rng.multinomial(order_targets[pi][si]-len(ids), weights/weights.sum())
        cid_list = [cid for cid, n in zip(ids, counts) for _ in range(int(n))]
        rng.shuffle(cid_list)
        amount_weights = rng.lognormal(0, 0.95 if seg != 'Business' else 0.65, len(cid_list))
        nets = allocate(revenue_targets[pi][si], amount_weights, minimum=100)
        month_weights = np.array([0.075,0.075,0.075,0.075,0.075,0.085,0.115,0.105,0.095,0.075,0.075,0.07])
        # Retail-Plus is weaker late in the current year; not a causal claim.
        if pi == 1 and seg == 'Retail-Plus':
            month_weights *= np.array([1.25,1.2,1.2,1.15,1.1,1.0,.85,.8,.75,.7,.7,.65])
        month_weights /= month_weights.sum()
        for cid, net in zip(cid_list, nets):
            fiscal_month = int(rng.choice(12, p=month_weights))
            calendar_month = (fiscal_month+3)%12+1
            year = start.year if calendar_month >= 4 else start.year+1
            day = random.randrange(1,29)
            order_date = date(year,calendar_month,day)
            channel_weights = [0.1,0.35,0.55] if seg == 'Business' else ([0.60,0.25,0.15] if pi else [0.45,0.30,0.25])
            channel = random.choices(['APP','WEB','STORE'],channel_weights)[0]
            discount = round(int(net)*float(rng.uniform(.01,.12 if pi == 0 else .18)))
            refund = round(int(net)*float(rng.uniform(.05,.30))) if rng.random()<.025 else 0
            oid = f'O{len(orders)+1:07d}'
            orders.append(dict(order_id=oid, customer_id=cid, period_id=period['period_id'], order_date=order_date.isoformat(), channel_id=channel, status='COMPLETED', gross_amount=int(net)+discount+refund, discount_amount=discount, refund_amount=refund))
            net_by_id[oid] = int(net)
    # Cancelled before dispatch: zero recognised revenue and no tracked costs.
    for _ in range([2000,2400][pi]):
        cid = random.choice(customers)['customer_id']
        d = start + timedelta(days=random.randrange(365))
        oid = f'O{len(orders)+1:07d}'
        gross = int(rng.integers(300,60000)); discount = round(gross*random.uniform(0,.15))
        orders.append(dict(order_id=oid, customer_id=cid, period_id=period['period_id'], order_date=d.isoformat(), channel_id=random.choice(['APP','WEB','STORE']), status='CANCELLED', gross_amount=gross, discount_amount=discount, refund_amount=0))
        net_by_id[oid] = 0
orders.sort(key=lambda x:(x['order_date'], x['order_id']))
write_csv('orders', orders)

cost_targets = [[680_000_000,40_000_000,10_000_000], [716_000_000,57_200_000,15_600_000]]
costs = {}
for pi, period in enumerate(periods):
    eligible = [o for o in orders if o['period_id']==period['period_id'] and o['status']=='COMPLETED']
    nets = np.array([net_by_id[o['order_id']] for o in eligible])
    product = allocate(cost_targets[pi][0], nets*rng.uniform(.6,1.1,len(nets)), minimum=1)
    fulfil = allocate(cost_targets[pi][1], np.sqrt(nets)*rng.uniform(.6,1.6,len(nets)), minimum=1)
    payment = allocate(cost_targets[pi][2], nets*rng.uniform(.8,1.2,len(nets)), minimum=1)
    for o, a,b,c in zip(eligible,product,fulfil,payment):
        costs[o['order_id']] = dict(order_id=o['order_id'],product_cost=int(a),fulfilment_cost=int(b),payment_cost=int(c))
for o in orders:
    costs.setdefault(o['order_id'],dict(order_id=o['order_id'],product_cost=0,fulfilment_cost=0,payment_cost=0))
write_csv('order_costs', [costs[o['order_id']] for o in orders])

spend = []
for pi, period in enumerate(periods):
    raw = []
    for month in range(12):
        calmonth=(month+3)%12+1; year=2024+pi+(calmonth<4)
        for channel in ['APP','WEB','STORE']:
            for purpose in ['Acquisition','Retention']:
                raw.append(dict(spend_id=f'M{len(spend)+len(raw)+1:05d}',period_id=period['period_id'],month_start=f'{year}-{calmonth:02d}-01',channel_id=channel,purpose=purpose,amount=0))
    weights = rng.uniform(.6,1.6,len(raw)) * np.array([1.5 if x['purpose']=='Acquisition' else 1 for x in raw])
    amounts = allocate([70_000_000,95_200_000][pi],weights)
    for row, amount in zip(raw,amounts): row['amount']=int(amount)
    spend.extend(raw)
write_csv('marketing_spend', spend)

# Database loader and SQL are portable; SQLite is shipped to remove installation work.
SCHEMA = '''PRAGMA foreign_keys = ON;
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
'''
(PACK/'sql'/'schema.sql').write_text(SCHEMA)
dbpath = PACK/'kalpa.sqlite'
dbpath.unlink(missing_ok=True)
db = sqlite3.connect(dbpath); db.executescript(SCHEMA)
for name, rows in TABLES.items():
    db.executemany(f"INSERT INTO {name} VALUES ({','.join('?' for _ in rows[0])})", [tuple(x.values()) for x in rows])
db.commit(); db.close()

metadata = dict(seed=SEED, row_counts={k:len(v) for k,v in TABLES.items()},currency='INR',monetary_precision='whole rupees', synthetic=True)
(TRAINER/'generation_metadata.json').write_text(json.dumps(metadata,indent=2))
print(json.dumps(metadata,indent=2))
