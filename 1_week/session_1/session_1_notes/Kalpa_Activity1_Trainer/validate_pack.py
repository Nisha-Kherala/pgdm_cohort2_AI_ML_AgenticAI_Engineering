"""Independent CSV/Python and database/SQL validation; never reads target metadata."""
from pathlib import Path
import csv, json, sqlite3, collections, statistics, hashlib, math

ROOT=Path(__file__).resolve().parent
PACK=ROOT/'Kalpa_Activity1'; TRAINER=ROOT/'trainer'
def read(name):
    with (PACK/'data'/f'{name}.csv').open(newline='',encoding='utf-8') as f:
        return list(csv.DictReader(f))
tables={x:read(x) for x in ['periods','channels','customers','orders','order_costs','marketing_spend']}
checks=[]
def check(name, condition, details=''):
    checks.append(dict(check=name,passed=bool(condition),details=details))
    if not condition: raise AssertionError(name+': '+str(details))
pk={'periods':'period_id','channels':'channel_id','customers':'customer_id','orders':'order_id','order_costs':'order_id','marketing_spend':'spend_id'}
for t,k in pk.items():
    check(f'{t}: primary key nonblank and unique',len({r[k] for r in tables[t]})==len(tables[t]) and all(r[k] for r in tables[t]))
    check(f'{t}: no missing field values',all(all(v!='' for v in r.values()) for r in tables[t]))
periods={r['period_id']:r for r in tables['periods']}
customers={r['customer_id']:r for r in tables['customers']}
channels={r['channel_id']:r for r in tables['channels']}
orders={r['order_id']:r for r in tables['orders']}
costs={r['order_id']:r for r in tables['order_costs']}
check('orders -> customers FK',all(r['customer_id'] in customers for r in orders.values()))
check('orders -> periods FK',all(r['period_id'] in periods for r in orders.values()))
check('orders -> channels FK',all(r['channel_id'] in channels for r in orders.values()))
check('order_costs -> orders exact one-to-one coverage',set(costs)==set(orders))
check('marketing -> periods and channels FKs',all(r['period_id'] in periods and r['channel_id'] in channels for r in tables['marketing_spend']))
check('marketing compound grain unique',len({(r['period_id'],r['month_start'],r['channel_id'],r['purpose']) for r in tables['marketing_spend']})==len(tables['marketing_spend']))
check('orders dated inside their period',all(periods[r['period_id']]['start_date']<=r['order_date']<=periods[r['period_id']]['end_date'] for r in orders.values()))
check('marketing month inside its period and first day',all(periods[r['period_id']]['start_date']<=r['month_start']<=periods[r['period_id']]['end_date'] and r['month_start'].endswith('-01') for r in tables['marketing_spend']))
check('signup precedes every order',all(customers[r['customer_id']]['signup_date']<=r['order_date'] for r in orders.values()))
check('statuses permitted',all(r['status'] in ['COMPLETED','CANCELLED'] for r in orders.values()))
check('monetary fields nonnegative integers',all(int(r[k])>=0 for t,ks in [('orders',['gross_amount','discount_amount','refund_amount']),('order_costs',['product_cost','fulfilment_cost','payment_cost']),('marketing_spend',['amount'])] for r in tables[t] for k in ks))
check('discount plus refund does not exceed gross',all(int(r['discount_amount'])+int(r['refund_amount'])<=int(r['gross_amount']) for r in orders.values()))
check('pre-dispatch cancellations have zero tracked order costs',all(sum(int(costs[r['order_id']][k]) for k in ['product_cost','fulfilment_cost','payment_cost'])==0 for r in orders.values() if r['status']=='CANCELLED'))

py={}; distributions={}; segments=[]
for pid in sorted(periods):
    eligible=[r for r in orders.values() if r['period_id']==pid and r['status']=='COMPLETED']
    amounts=[int(r['gross_amount'])-int(r['discount_amount'])-int(r['refund_amount']) for r in eligible]
    buyers={r['customer_id'] for r in eligible}
    revenue=sum(amounts); count=len(eligible)
    ordercosts={k:sum(int(costs[r['order_id']][k]) for r in orders.values() if r['period_id']==pid) for k in ['product_cost','fulfilment_cost','payment_cost']}
    marketing=sum(int(r['amount']) for r in tables['marketing_spend'] if r['period_id']==pid)
    totalcost=sum(ordercosts.values())+marketing
    py[pid]=dict(period_label=periods[pid]['period_label'],completed_orders=count,purchasing_customers=len(buyers),revenue=revenue,orders_per_customer=count/len(buyers),revenue_per_order=revenue/count,**ordercosts,marketing_cost=marketing,total_cost=totalcost,contribution=revenue-totalcost,contribution_margin_pct=100*(revenue-totalcost)/revenue)
    check(f'{pid}: positive recognised order revenue',all(a>0 for a in amounts))
    check(f'{pid}: revenue tree exact identity',math.isclose(len(buyers)*(count/len(buyers))*(revenue/count),revenue,abs_tol=.01))
    f=collections.Counter(r['customer_id'] for r in eligible)
    q=statistics.quantiles(amounts,n=4,method='inclusive')
    distributions[pid]=dict(order_value_mean=statistics.mean(amounts),order_value_median=statistics.median(amounts),order_value_q1=q[0],order_value_q3=q[2],order_value_iqr=q[2]-q[0],order_value_min=min(amounts),order_value_max=max(amounts),order_value_std_population=statistics.pstdev(amounts),orders_per_customer_median=statistics.median(f.values()),orders_per_customer_min=min(f.values()),orders_per_customer_max=max(f.values()))
    for seg in ['Business','Retail-Core','Retail-Plus','Student']:
        ix=[i for i,r in enumerate(eligible) if customers[r['customer_id']]['segment']==seg]
        b={eligible[i]['customer_id'] for i in ix}
        segments.append(dict(period_id=pid,segment=seg,orders=len(ix),customers=len(b),revenue=sum(amounts[i] for i in ix),orders_per_customer=len(ix)/len(b)))
    check(f'{pid}: segment revenue and orders tie out',sum(r['revenue'] for r in segments if r['period_id']==pid)==revenue and sum(r['orders'] for r in segments if r['period_id']==pid)==count)
    check(f'{pid}: customer registry differs from buyers',len(buyers)<len(customers))

expected={'FY2024_25':dict(completed_orders=50000,purchasing_customers=10000,revenue=1000000000,orders_per_customer=5,revenue_per_order=20000,total_cost=800000000,contribution=200000000,contribution_margin_pct=20),
          'FY2025_26':dict(completed_orders=52000,purchasing_customers=13000,revenue=1040000000,orders_per_customer=4,revenue_per_order=20000,total_cost=884000000,contribution=156000000,contribution_margin_pct=15)}
for pid,target in expected.items():
    for k,v in target.items(): check(f'{pid}: agreed {k}',py[pid][k]==v,f'{py[pid][k]} == {v}')

conn=sqlite3.connect(PACK/'kalpa.sqlite');conn.row_factory=sqlite3.Row
check('SQLite integrity_check',conn.execute('PRAGMA integrity_check').fetchone()[0]=='ok')
check('SQLite foreign_key_check',len(conn.execute('PRAGMA foreign_key_check').fetchall())==0)
for t in tables:
    check(f'{t}: database row count equals CSV',conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0]==len(tables[t]))
    columns=list(tables[t][0]); csvrows={tuple(str(r[c]) for c in columns) for r in tables[t]}
    dbrows={tuple(str(v) for v in r) for r in conn.execute(f'SELECT * FROM {t}')}
    check(f'{t}: every stored row matches CSV',csvrows==dbrows)
sql_results={}
for filename in ['exercise_1_solution.sql','exercise_2_solution.sql']:
    query_path=TRAINER/filename if (TRAINER/filename).exists() else PACK/'sql'/filename
    result=[dict(r) for r in conn.execute(query_path.read_text())]
    sql_results[filename]=result
    for r in result:
        pid=next(k for k,v in periods.items() if v['period_label']==r['period_label'])
        for k,v in r.items():
            if k in py[pid] and isinstance(v,(int,float)):
                check(f'{filename}: {pid} Python/SQL {k}',math.isclose(v,py[pid][k],rel_tol=1e-10,abs_tol=.00001))
        if 'margin_floor' in r:
            check(f'{pid}: SQL guardrail label',r['margin_floor']==('MET' if pid=='FY2024_25' else 'BREACHED'))

# Deliberate error probes: verify that common beginner mistakes visibly fail.
naive=[dict(r) for r in conn.execute('SELECT period_id,COUNT(*) AS n,SUM(gross_amount-discount_amount-refund_amount) AS revenue FROM orders GROUP BY period_id')]
check('status omission changes both order count and revenue',all(r['n']!=py[r['period_id']]['completed_orders'] and r['revenue']!=py[r['period_id']]['revenue'] for r in naive))
check('count(*) is not purchasing customers',all(r['completed_orders']!=r['purchasing_customers'] for r in py.values()))
check('averages hide different order distributions',all(abs(r['order_value_mean']-r['order_value_median'])>500 for r in distributions.values()))
fanout=conn.execute('SELECT COUNT(*) FROM eligible_orders o JOIN marketing_spend m ON m.period_id=o.period_id').fetchone()[0]
check('period-level detail join produces obvious fanout',fanout==102000*72)
conn.close()

report=dict(status='PASS',checks_passed=len(checks),checks=checks,python_results=py,sql_results=sql_results,descriptive_statistics=distributions,segment_results=segments,row_counts={k:len(v) for k,v in tables.items()},checksums={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((PACK/'data').glob('*.csv'))})
(TRAINER/'verification_report.json').write_text(json.dumps(report,indent=2))
(TRAINER/'results_for_workbook.json').write_text(json.dumps(dict(metrics=py,statistics=distributions,segments=segments),indent=2))
print(json.dumps(dict(status='PASS',checks_passed=len(checks),python_results=py,descriptive_statistics=distributions),indent=2))
