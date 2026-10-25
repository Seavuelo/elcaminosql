"""Ayuda gradual compartida por los ejercicios originales y adicionales"""
from game.sql_syntax import tokenize

CONCEPTS = [
    ("CREATE INDEX", "Un índice organiza referencias para ciertas búsquedas, identifica la tabla y la columna que pide el enunciado"),
    ("CREATE VIEW", "Una vista pone nombre a una consulta, primero piensa qué debe devolver ese SELECT"),
    ("CREATE TABLE", "Necesitas definir una estructura, revisa el nombre, cada columna, su tipo y las restricciones solicitadas"),
    ("INSERT", "Vas a añadir una fila, relaciona cada columna con el valor situado en la misma posición"),
    ("UPDATE", "Debes cambiar filas existentes, separa qué cambia de qué condición identifica las filas"),
    ("DELETE", "Se eliminan filas de una tabla, identifica el filtro y comprueba a quién afecta antes de borrar"),
    ("EXPLAIN", "Necesitas inspeccionar el plan de una consulta, no sus filas de resultado"),
    ("LEFT JOIN", "Conserva todas las filas de la izquierda, distingue una relación ausente de un dato pendiente"),
    ("JOIN", "La información está repartida, relaciona los identificadores y decide qué representa cada fila del cruce"),
    ("HAVING", "Necesitas decidir qué grupos conservar después de calcular sus resúmenes"),
    ("GROUP BY", "Separa los registros por la categoría solicitada y calcula un resumen por grupo"),
    (" IN ", "Una consulta puede obtener los identificadores que la consulta exterior necesita buscar"),
    ("COUNT", "Piensa si cuentas filas o valores conocidos de una columna, NULL puede hacer que difieran"),
    ("AVG", "Una función agregada resume varios valores en una cifra, revisa qué columna debes resumir"),
    ("LIMIT", "Obtén primero el orden solicitado y después limita el tamaño de la página"),
    ("ORDER BY", "Las filas deben tener un orden explícito, revisa dirección y posibles desempates"),
    ("WHERE", "Necesitas conservar solo las filas que cumplen una condición, distingue columna, operador y valor"),
    ("DISTINCT", "Elimina repeticiones del resultado, sin borrar los registros almacenados"),
]


def task_hint(task, level):
    upper = task.canonical_query.upper()
    concept = next((text for marker,text in CONCEPTS if marker in upper), "Identifica las columnas que necesitas mostrar y la tabla donde están guardadas")
    if level <= 1:
        return concept + "\nRevisa el cuaderno con F1 si necesitas un ejemplo de la clase"
    if level == 2:
        identifiers = {}
        parts = []
        for kind,value in tokenize(task.canonical_query):
            if kind == "identifier":
                value = identifiers.setdefault(value, f"dato_{len(identifiers)+1}")
            elif kind == "number":
                value = "numero"
            elif kind == "string":
                value = "'texto'"
            parts.append(value)
        return concept + "\n\nEstructura orientativa\n" + ''.join(parts) + "\n\nReemplaza cada dato por los nombres del catálogo y los valores del enunciado"
    fragments = []
    for marker, description in [("SELECT", "SELECT elige las columnas o cálculos del resultado"), ("FROM", "FROM indica la tabla de origen"), ("WHERE", "WHERE limita las filas usando la condición escrita"), ("GROUP BY", "GROUP BY separa las categorías antes de resumir"), ("HAVING", "HAVING conserva los grupos que cumplen su condición"), ("ORDER BY", "ORDER BY fija el orden y los desempates indicados"), ("LIMIT", "LIMIT fija el máximo de filas y OFFSET salta las anteriores"), ("SET", "SET asigna los nuevos valores solo a las filas seleccionadas"), ("VALUES", "VALUES asigna cada valor a su columna según la posición")]:
        if marker in upper:
            fragments.append(description)
    return ("SOLUCIÓN COMPLETA, esta es una posibilidad, no se ejecuta ni completa el ejercicio\n\n" + task.canonical_query + "\n\nPor qué funciona\n" + concept + "\n" + "\n".join(fragments) + "\n\nResultado solicitado\n" + task.objective + "\n\n" + task.explanation)
