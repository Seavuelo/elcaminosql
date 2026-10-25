"""Modelo del taller introductorio, independiente de la base de la carrera"""
import re
import sqlite3
from contextlib import closing
from copy import deepcopy

TYPES = ("INTEGER", "TEXT", "REAL", "BLOB")
DEFAULT_FOUNDATION = dict(day=1, completed=False, answers={}, tables=[], tested_sql=[])


def identifier(name):
    name = name.strip().lower()
    if not re.fullmatch(r"[a-z][a-z0-9_]{0,31}", name):
        raise ValueError("Usa un nombre de hasta 32 caracteres, con letras sin tildes, números y guion bajo, empezando por una letra")
    return name


def quoted(name):
    return '"' + name.replace('"', '""') + '"'


class DataModel:
    def __init__(self, tables=None):
        self.tables = deepcopy(tables or [])

    def table(self, name):
        return next((t for t in self.tables if t['name'] == name), None)

    def add_table(self, name):
        name = identifier(name)
        if self.table(name):
            raise ValueError("Ya existe una tabla con ese nombre")
        index = len(self.tables)
        table = dict(name=name, columns=[], x=12+(index % 2)*142, y=12+(index//2)*140)
        self.tables.append(table)
        return table

    def rename_table(self, old, new):
        new = identifier(new)
        if new != old and self.table(new):
            raise ValueError("Ya existe una tabla con ese nombre")
        self.table(old)['name'] = new
        for table in self.tables:
            for col in table['columns']:
                if col.get('reference', {}).get('table') == old:
                    col['reference']['table'] = new

    def incoming(self, table_name, column=None):
        return [(t['name'],c['name']) for t in self.tables for c in t['columns']
                if c.get('reference', {}).get('table') == table_name
                and (column is None or c['reference']['column'] == column)]

    def delete_table(self, name):
        if any(t != name for t,c in self.incoming(name)):
            raise ValueError("Otra tabla usa esta clave, quita primero la relación")
        self.tables.remove(self.table(name))

    def delete_column(self, table_name, name):
        if self.incoming(table_name, name):
            raise ValueError("La columna está referenciada, quita primero la relación")
        table = self.table(table_name)
        table['columns'] = [c for c in table['columns'] if c['name'] != name]

    def set_column(self, table_name, column, old_name=None):
        before = deepcopy(self.tables)
        try:
            column = deepcopy(column)
            column['name'] = identifier(column['name'])
            if column['type'] not in TYPES:
                raise ValueError("Elige INTEGER, TEXT, REAL o BLOB")
            table = self.table(table_name)
            if any(c['name'] == column['name'] and c['name'] != old_name for c in table['columns']):
                raise ValueError("La tabla ya tiene una columna con ese nombre")
            if column.get('pk'):
                column['not_null'] = True
                if any(c.get('pk') and c['name'] != old_name for c in table['columns']):
                    raise ValueError("En este taller usamos una sola columna como clave primaria por tabla")
            if not column.get('reference'):
                column.pop('reference', None)
            index = next((i for i,c in enumerate(table['columns']) if c['name'] == old_name), len(table['columns']))
            if index == len(table['columns']):
                table['columns'].append(column)
            else:
                table['columns'][index] = column
            if old_name and old_name != column['name']:
                for source in self.tables:
                    for col in source['columns']:
                        ref = col.get('reference', {})
                        if ref.get('table') == table_name and ref.get('column') == old_name:
                            ref['column'] = column['name']
            self.validate(allow_empty=True)
        except (ValueError, KeyError):
            self.tables = before
            raise

    def validate(self, allow_empty=False):
        if not self.tables and not allow_empty:
            raise ValueError("Crea al menos una tabla")
        for table in self.tables:
            if not table['columns'] and not allow_empty:
                raise ValueError(f"Faltan columnas en {table['name']}")
            for col in table['columns']:
                ref = col.get('reference')
                if ref:
                    target = self.table(ref['table'])
                    key = next((c for c in target['columns'] if c['name'] == ref['column']), None) if target else None
                    if not key or not key.get('pk'):
                        raise ValueError("La clave foránea debe apuntar a una clave primaria existente")
                    if key['type'] != col['type']:
                        raise ValueError("En este taller elegimos el mismo tipo para las dos columnas de la relación")

    def statements(self):
        self.validate()
        statements = []
        for table in self.tables:
            columns = []
            for col in table['columns']:
                part = f"{quoted(col['name'])} {col['type']}"
                if col.get('not_null') or col.get('pk'):
                    part += " NOT NULL"
                if col.get('pk'):
                    part += " PRIMARY KEY"
                if col.get('reference'):
                    ref = col['reference']
                    part += f" REFERENCES {quoted(ref['table'])} ({quoted(ref['column'])})"
                columns.append(part)
            statements.append(f"CREATE TABLE {quoted(table['name'])} (\n  " + ",\n  ".join(columns) + "\n);")
        return statements

    def connection(self):
        conn = sqlite3.connect(':memory:')
        try:
            conn.execute('PRAGMA foreign_keys = ON')
            for sql in self.statements():
                conn.execute(sql)
            return conn
        except Exception:
            conn.close()
            raise

    def day_goal(self, day):
        if day == 1:
            return True, "Ya distingues el modelo, los datos y el lenguaje que los consulta"
        students = self.table('estudiantes')
        cols = {c['name']:c for c in students['columns']} if students else {}
        if any(name not in cols or cols[name]['type'] != kind for name,kind in [('id','INTEGER'),('nombre','TEXT'),('promedio','REAL')]):
            return False, "Crea estudiantes con id INTEGER, nombre TEXT y promedio REAL"
        if day >= 3 and (not cols['id'].get('pk') or not cols['nombre'].get('not_null')):
            return False, "En estudiantes marca id como PK y nombre como obligatorio, NN significa NOT NULL"
        if day >= 4:
            tutoring = self.table('tutorias')
            tc = {c['name']:c for c in tutoring['columns']} if tutoring else {}
            if (not tc.get('id', {}).get('pk') or tc.get('id', {}).get('type') != 'INTEGER'
                    or tc.get('estudiante_id', {}).get('type') != 'INTEGER'
                    or tc.get('tema', {}).get('type') != 'TEXT'
                    or tc.get('estudiante_id', {}).get('reference') != dict(table='estudiantes',column='id')
                    or not tc.get('estudiante_id', {}).get('not_null')):
                return False, "Crea tutorias con id INTEGER PK, estudiante_id INTEGER NN unido a estudiantes.id y tema TEXT"
        try:
            with closing(self.connection()):
                pass
        except (ValueError,sqlite3.Error) as exc:
            return False, str(exc)
        return True, "El diseño cumple el objetivo y SQLite puede construirlo"

    def demonstrate_integrity(self):
        """Inserciones reales y fallos esperados, siempre en memoria"""
        valid, message = self.day_goal(4)
        if not valid:
            raise ValueError(message)
        with closing(self.connection()) as conn:
            # Las columnas extra obligatorias requieren un valor, se pide el modelo del taller.
            try:
                conn.execute("INSERT INTO estudiantes(id,nombre,promedio) VALUES(1,'Moshi',6.8)")
                conn.execute("INSERT INTO tutorias(id,estudiante_id,tema) VALUES(1,1,'Modelo relacional')")
                conn.execute("INSERT INTO tutorias(id,estudiante_id,tema) VALUES(2,1,'Tipos de datos')")
            except sqlite3.IntegrityError as exc:
                raise ValueError("Tu diseño tiene restricciones adicionales, revisa las columnas obligatorias del taller, " + str(exc)) from exc
            checks = []
            for title,sql in [
                ("PK evita dos estudiantes con id 1", "INSERT INTO estudiantes(id,nombre,promedio) VALUES(1,'Carlos',5.0)"),
                ("NOT NULL exige un nombre", "INSERT INTO estudiantes(id,nombre,promedio) VALUES(2,NULL,5.0)"),
                ("FK rechaza una tutoría de un estudiante inexistente", "INSERT INTO tutorias(id,estudiante_id,tema) VALUES(3,999,'Sin dueño')"),
            ]:
                try:
                    conn.execute(sql)
                except sqlite3.IntegrityError:
                    checks.append((title,True))
                else:
                    checks.append((title,False))
            return dict(checks=checks, estudiantes=conn.execute('SELECT id,nombre,promedio FROM estudiantes').fetchall(),
                        tutorias=conn.execute('SELECT id,estudiante_id,tema FROM tutorias').fetchall())
