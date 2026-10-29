"""Verifica las consultas de este proyecto con SQLite de Python, sin paquetes externos."""
import json
import sqlite3
from pathlib import Path

root = Path(__file__).resolve().parent
cases = json.loads((root / 'pruebas.json').read_text(encoding='utf-8'))
solutions = json.loads((root / 'soluciones.json').read_text(encoding='utf-8'))

def snapshot(db):
    result = []
    for kind, name in db.execute("SELECT type,name FROM sqlite_master WHERE name NOT LIKE 'sqlite_%' ORDER BY type,name"):
        quoted = '"' + name.replace('"', '""') + '"'
        rows = sorted(map(repr, db.execute('SELECT * FROM ' + quoted)))
        columns = list(db.execute('PRAGMA table_info(' + quoted + ')'))
        result.append((kind, name, columns, rows))
    return result

passed = total = 0
for case in cases:
    for index, seed in enumerate(case['fixtures']):
        total += 1
        with sqlite3.connect(':memory:') as actual, sqlite3.connect(':memory:') as expected:
            for db in (actual, expected):
                db.executescript(seed)
                db.execute('PRAGMA foreign_keys=ON')
                for previous in cases:
                    if previous['stage'] < case['stage'] and previous['is_write']:
                        db.execute(solutions[previous['id']])
            try:
                cursor = actual.execute(solutions[case['id']])
                reference = expected.execute(case['sql'])
                if case['is_write']:
                    valid = snapshot(actual) == snapshot(expected)
                else:
                    columns = [c[0].lower() for c in cursor.description]
                    expected_columns = [c[0].lower() for c in reference.description]
                    mapping = [columns.index(c) if c in columns else i for i,c in enumerate(expected_columns)]
                    rows = [tuple(row[i] for i in mapping) for row in cursor.fetchall()] if len(columns) == len(expected_columns) else []
                    reference_rows = reference.fetchall()
                    valid = rows == reference_rows if 'ORDER BY' in case['sql'].upper() else sorted(map(repr, rows)) == sorted(map(repr, reference_rows))
                    valid = valid and len(columns) == len(expected_columns)
            except (sqlite3.Error, IndexError):
                valid = False
            passed += int(valid)
            print(('OK' if valid else 'REVISAR'), case['id'], 'caso', index + 1)
print(str(passed) + '/' + str(total) + ' comprobaciones correctas')
raise SystemExit(0 if passed == total else 1)
