"""Unidades didácticas, SQL y resultados reales en una conexión aislada"""
import sqlite3
from pathlib import Path
from contextlib import closing
from database.seed_universidad import add_practice_data


def unit(title, speech, sql="", explanation="", inspect="", error="", check=""):
    return dict(title=title, speech=speech, sql=sql, explanation=explanation, inspect=inspect, error=error, check=check)


def lesson_units(year, day):
    from game.lessons import year1, year2, year3, year4
    return (year1,year2,year3,year4)[year-1].LESSONS[day]


def demonstration(year, day):
    """La plantilla se abre en modo lectura y cada clase recibe su propia copia"""
    seed = Path(__file__).resolve().parents[2] / "database" / "universidad.db"
    with closing(sqlite3.connect(seed.as_uri() + "?mode=ro", uri=True)) as source:
        with closing(sqlite3.connect(":memory:")) as conn:
            source.backup(conn)
            add_practice_data(conn)
            if year == 2:
                conn.execute("CREATE TABLE taller_demo (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, costo REAL)")
                conn.executemany("INSERT INTO taller_demo VALUES (?, ?, ?)", [(1,'Robótica',12.5),(2,'Fotografía',None),(3,'Dibujo',8.0)])
                conn.commit()
            conn.commit()
            conn.isolation_level = None
            results = []
            for item in lesson_units(year,day):
                result = dict(item, columns=[], rows=[])
                if item['sql']:
                    cur = conn.execute(item['sql'])
                    if cur.description:
                        result['columns'] = [d[0] for d in cur.description]
                        result['rows'] = cur.fetchall()
                    elif item['inspect']:
                        cur = conn.execute(item['inspect'])
                        result['columns'] = [d[0] for d in cur.description]
                        result['rows'] = cur.fetchall()
                results.append(result)
            return results


def slides_for(year,day):
    pages = []
    for item in demonstration(year,day):
        base = dict(title=item['title'], chalk_title=item['title'], turing=item['speech'])
        pages.append(dict(base, chalk_body=item['explanation'], code_example=item['sql']))
        if item['columns']:
            rows = item['rows']
            from game.ui_helpers import paginate_grid_rows
            from game.rendering import make_font
            chunks = paginate_grid_rows(item["columns"], rows, make_font(12), 424, 124)
            for index,chunk in enumerate(chunks):
                pages.append(dict(base, chalk_body="Resultado de la demostración" + (f" ({index+1}/{len(chunks)})" if len(chunks)>1 else ""), code_example="", table_columns=item['columns'], table_rows=chunk, turing="Compara estas filas con la condición y las columnas de la consulta anterior, este resultado se calculó en SQLite sobre una copia aislada"))
        if item['error'] or item['check']:
            pages.append(dict(base, chalk_body=("Error habitual\n"+item['error'] if item['error'] else "") + ("\n\nPara pensar\n"+item['check'] if item['check'] else ""), code_example="", turing="Antes de seguir, intenta explicar qué cambiaría y por qué, puedes retroceder para comparar el ejemplo con su resultado"))
    pages.append(dict(title="Antes del laboratorio",chalk_title="Ahora te toca aplicar lo aprendido",chalk_body="Lee el objetivo, predice el resultado y prueba tu consulta\n\nEl laboratorio usa otros nombres, valores o condiciones\n\nF1: apuntes, F2: catálogo, F3: pistas graduales",code_example="",turing="No necesitas memorizar la consulta, identifica qué información necesitas, de dónde sale y qué transformación debes hacer"))
    return pages
