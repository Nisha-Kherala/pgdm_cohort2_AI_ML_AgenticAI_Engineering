from pathlib import Path
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
