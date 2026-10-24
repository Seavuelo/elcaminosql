import pygame

class DailyTask:
    def __init__(self, year, day, task_idx, title, objective, hint, canonical_query, explanation, note_id=None, is_write=False):
        self.year = year
        self.day = day
        self.task_idx = task_idx
        self.title = title
        self.objective = objective
        self.hint = hint
        self.canonical_query = canonical_query
        self.explanation = explanation
        self.note_id = note_id or f"y{year}_d{day}"
        self.is_write = is_write

    def validate(self, db_manager, user_result, user_query=""):
        if not user_result or not user_result.get("success"):
            return False, "La consulta falló o tiene un error de sintaxis."

        u_upper = user_query.upper().strip()

        # Operaciones DDL / DML
        if self.is_write:
            if "CREATE TABLE" in self.canonical_query.upper():
                if "CREATE TABLE" not in u_upper:
                    return False, "Debes usar la instrucción CREATE TABLE para definir la estructura solicitada."
            elif "INSERT INTO" in self.canonical_query.upper():
                if "INSERT INTO" not in u_upper:
                    return False, "Debes insertar los datos solicitados usando la instrucción INSERT INTO."
            elif "UPDATE" in self.canonical_query.upper():
                if "UPDATE" not in u_upper or "WHERE" not in u_upper:
                    return False, "Cuidado: Recuerda siempre incluir la cláusula WHERE al usar UPDATE para no modificar filas indebidas."
            elif "DELETE" in self.canonical_query.upper():
                if "DELETE" not in u_upper or "WHERE" not in u_upper:
                    return False, "Cuidado: Recuerda usar DELETE FROM con la cláusula WHERE para borrar solo las filas indicadas."
            elif "CREATE VIEW" in self.canonical_query.upper():
                if "CREATE VIEW" not in u_upper:
                    return False, "Debes crear la vista usando CREATE VIEW ..."
            elif "CREATE INDEX" in self.canonical_query.upper():
                if "CREATE INDEX" not in u_upper:
                    return False, "Debes crear el índice usando CREATE INDEX ..."
            elif "EXPLAIN" in self.canonical_query.upper():
                if "EXPLAIN" not in u_upper:
                    return False, "Debes inspeccionar el plan de ejecución usando EXPLAIN QUERY PLAN ..."

            return True, self.explanation

        # Consultas de lectura (SELECT)
        ref = db_manager.execute_query(self.canonical_query)
        if not ref.get("success"):
            return False, "Error interno validando la consulta de referencia."

        u_cols = [c.lower() for c in user_result.get("columns", [])]
        r_cols = [c.lower() for c in ref.get("columns", [])]

        # 1. Validación estricta de columnas solicitadas
        if len(u_cols) < len(r_cols):
            missing = [c for c in r_cols if c not in u_cols]
            col_list = ", ".join(r_cols)
            return False, f"Faltan columnas en tu resultado. Se esperaban {len(r_cols)} columnas ({col_list}), pero solo entregaste {len(u_cols)} ({', '.join(u_cols)}). ¡Revisa el enunciado!"

        if len(u_cols) > len(r_cols):
            extra = [c for c in u_cols if c not in r_cols]
            col_list = ", ".join(r_cols)
            return False, f"Devolviste más columnas de las pedidas ({len(u_cols)} en vez de {len(r_cols)}). Se solicitó únicamente ({col_list})."

        if set(u_cols) != set(r_cols):
            return False, f"Los nombres de las columnas no coinciden con lo pedido. Se esperaba ({', '.join(r_cols)}), pero entregaste ({', '.join(u_cols)})."

        # 2. Validación de filas devueltas
        u_rows = user_result.get("rows", [])
        r_rows = ref.get("rows", [])

        if len(u_rows) == 0 and len(r_rows) > 0:
            return False, "La consulta no devolvió ninguna fila. Revisa los filtros en tu cláusula WHERE."

        if len(u_rows) > len(r_rows):
            return False, f"La consulta devolvió demasiadas filas ({len(u_rows)} en vez de {len(r_rows)}). ¿Olvidaste o afinaste mal la cláusula WHERE?"

        if len(u_rows) < len(r_rows):
            return False, f"Faltan filas en el resultado ({len(u_rows)} devueltas de {len(r_rows)} esperadas). Revisa si tu condición en el WHERE es demasiado restrictiva."

        # Mapear columnas según el orden solicitado en la referencia
        col_indices = [u_cols.index(c) for c in r_cols]

        if "ORDER BY" in self.canonical_query.upper():
            for u_r, r_r in zip(u_rows, r_rows):
                for target_idx, u_idx in enumerate(col_indices):
                    u_val = u_r[u_idx]
                    r_val = r_r[target_idx]
                    if isinstance(u_val, float) and isinstance(r_val, float):
                        if abs(u_val - r_val) > 0.01:
                            return False, "El orden o los valores numéricos no coinciden con lo pedido."
                    elif str(u_val) != str(r_val):
                        return False, "El orden de los resultados no coincide con lo pedido. Revisa ORDER BY."
        else:
            def norm_row(r, indices):
                return tuple(round(r[i], 2) if isinstance(r[i], float) else str(r[i]) for i in indices)

            u_set = sorted([norm_row(r, col_indices) for r in u_rows])
            r_set = sorted([norm_row(r, range(len(r_cols))) for r in r_rows])

            if u_set != r_set:
                return False, "Los datos devueltos no coinciden con la información esperada. Revisa los filtros aplicados."

        return True, self.explanation


class ExamQuestion:
    def __init__(self, q_num, title, objective, canonical_query):
        self.q_num = q_num
        self.title = title
        self.objective = objective
        self.canonical_query = canonical_query

    def validate(self, db_manager, user_result):
        if not user_result or not user_result.get("success"):
            return False, "Error al ejecutar la consulta."

        ref = db_manager.execute_query(self.canonical_query)
        if not ref.get("success"):
            return False, "Error interno en consulta de referencia."

        u_cols = [c.lower() for c in user_result.get("columns", [])]
        r_cols = [c.lower() for c in ref.get("columns", [])]

        if len(u_cols) != len(r_cols):
            return False, f"Cantidad de columnas incorrecta ({len(u_cols)} entregadas, se esperaban {len(r_cols)}: {', '.join(r_cols)})."

        if set(u_cols) != set(r_cols):
            return False, f"Las columnas no coinciden. Se esperaba ({', '.join(r_cols)})."

        u_rows = user_result.get("rows", [])
        r_rows = ref.get("rows", [])

        if len(u_rows) != len(r_rows):
            return False, f"Cantidad de filas incorrecta ({len(u_rows)} devueltas, se esperaban {len(r_rows)})."

        col_indices = [u_cols.index(c) for c in r_cols]

        if "ORDER BY" in self.canonical_query.upper():
            for u_r, r_r in zip(u_rows, r_rows):
                for target_idx, u_idx in enumerate(col_indices):
                    u_val = u_r[u_idx]
                    r_val = r_r[target_idx]
                    if isinstance(u_val, float) and isinstance(r_val, float):
                        if abs(u_val - r_val) > 0.01:
                            return False, "El orden o valor de los resultados no coincide."
                    elif str(u_val) != str(r_val):
                        return False, "El orden de los resultados no coincide con lo pedido."
        else:
            def norm_row(r, indices):
                return tuple(round(r[i], 2) if isinstance(r[i], float) else str(r[i]) for i in indices)

            u_set = sorted([norm_row(r, col_indices) for r in u_rows])
            r_set = sorted([norm_row(r, range(len(r_cols))) for r in r_rows])
            if u_set != r_set:
                return False, "Los datos devueltos no coinciden con los registros esperados."

        return True, "¡Excelente respuesta!"


class UniversityCurriculum:
    """Gestiona los 4 Años de Carrera de Ingeniería Informática con múltiples ejercicios diarios."""
    def __init__(self, db_manager, save_system, audio_manager):
        self.db = db_manager
        self.save = save_system
        self.audio = audio_manager

        self.current_year = self.save.data.get("current_year", 1)
        self.current_day = self.save.data.get("current_day", 1)
        
        self.current_task_idx = 0
        self.day_task_completed = False
        self.lecture_done_for_day = False

        # Examen del Viernes
        self.exam_active = False
        self.exam_q_index = 0
        self.exam_score = 0
        self.exam_finished = False
        self.exam_final_grade = 1.0

        self._build_curriculum()

    def _build_curriculum(self):
        # Mapeo de Tareas Diarias por (Año, Día): Cada día tiene mínimo 2 ejercicios
        self.tasks = {
            # === AÑO 1: Fundamentos y Álgebra Relacional ===
            (1, 1): [
                DailyTask(1, 1, 0, "Día 1 - Ejercicio 1/2: Consulta General",
                          "Escribe una consulta para ver todos los datos y columnas de la tabla 'estudiantes'.",
                          "Usa SELECT * FROM estudiantes;",
                          "SELECT * FROM estudiantes;",
                          "¡Excelente! El comodín asterisco (*) selecciona todas las columnas de la tabla."),
                DailyTask(1, 1, 1, "Día 1 - Ejercicio 2/2: Proyección de Columnas",
                          "Muestra únicamente las columnas 'nombre' y 'carrera' de todos los estudiantes (separadas por coma).",
                          "Usa SELECT nombre, carrera FROM estudiantes;",
                          "SELECT nombre, carrera FROM estudiantes;",
                          "¡Brillante! Has aprendido a solicitar columnas específicas separadas por comas.")
            ],
            (1, 2): [
                DailyTask(1, 2, 0, "Día 2 - Ejercicio 1/2: Filtro Numérico",
                          "De la tabla 'notas_parcial', filtra a los alumnos con 'nota' menor a 4.0. Muestra las columnas 'estudiante_nombre' y 'nota'.",
                          "Usa SELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;",
                          "SELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;",
                          "¡Muy bien! El filtro WHERE nota < 4.0 aísla con exactitud los datos de riesgo."),
                DailyTask(1, 2, 1, "Día 2 - Ejercicio 2/2: Filtro de Texto",
                          "De la tabla 'estudiantes', selecciona a los alumnos cuya 'carrera' sea 'Ingenieria Informatica'. Muestra 'nombre' y 'promedio'.",
                          "Usa SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                          "SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                          "¡Perfecto! Recuerda que en SQL los valores de texto siempre van entre comillas simples 'así'.")
            ],
            (1, 3): [
                DailyTask(1, 3, 0, "Día 3 - Ejercicio 1/2: Ranking de Rendimiento",
                          "Selecciona 'nombre' y 'promedio' de la tabla 'estudiantes', ordenados por 'promedio' de mayor a menor (DESC).",
                          "Usa ORDER BY promedio DESC;",
                          "SELECT nombre, promedio FROM estudiantes ORDER BY promedio DESC;",
                          "¡Excelente! ORDER BY DESC es el fundamento de los cuadros de honor y rankings."),
                DailyTask(1, 3, 1, "Día 3 - Ejercicio 2/2: Carga Académica Ordenada",
                          "Selecciona 'nombre' y 'creditos' de 'materias' con creditos > 4, ordenadas por 'nombre' alfabéticamente (ASC).",
                          "Usa WHERE creditos > 4 ORDER BY nombre ASC;",
                          "SELECT nombre, creditos FROM materias WHERE creditos > 4 ORDER BY nombre ASC;",
                          "¡Genial! Has combinado el filtro condicional WHERE con el ordenamiento alfabético.")
            ],
            (1, 4): [
                DailyTask(1, 4, 0, "Día 4 - Ejercicio 1/2: Podio de Excelencia",
                          "Muestra 'nombre' y 'promedio' de los 3 mejores estudiantes de toda la universidad usando LIMIT.",
                          "Usa ORDER BY promedio DESC LIMIT 3;",
                          "SELECT nombre, promedio FROM estudiantes ORDER BY promedio DESC LIMIT 3;",
                          "¡Extraordinario! LIMIT restringe la cantidad exacta de registros transmitidos."),
                DailyTask(1, 4, 1, "Día 4 - Ejercicio 2/2: Cupos Críticos",
                          "Muestra 'nombre' y 'cupos' de las 2 materias con menos cupos disponibles (cupos > 0) ordenadas de menor a mayor.",
                          "Usa WHERE cupos > 0 ORDER BY cupos ASC LIMIT 2;",
                          "SELECT nombre, cupos FROM materias WHERE cupos > 0 ORDER BY cupos ASC LIMIT 2;",
                          "¡Nivel 1 Superado! Dominas la secuencia completa: SELECT -> FROM -> WHERE -> ORDER BY -> LIMIT.")
            ],

            # === AÑO 2: DDL y DML (Creación, Inserción y Modificación) ===
            (2, 1): [
                DailyTask(2, 1, 0, "Día 1 - Ejercicio 1/2: Tabla de Proyectos",
                          "Crea una tabla llamada 'proyectos' con columnas: 'id' (INTEGER PRIMARY KEY), 'titulo' (TEXT), 'nota' (REAL).",
                          "Usa CREATE TABLE proyectos (id INTEGER PRIMARY KEY, titulo TEXT, nota REAL);",
                          "CREATE TABLE IF NOT EXISTS proyectos (id INTEGER PRIMARY KEY, titulo TEXT, nota REAL);",
                          "¡Genial! Has definido tu primera estructura relacional profesional con DDL.", is_write=True),
                DailyTask(2, 1, 1, "Día 1 - Ejercicio 2/2: Tabla de Laboratorios",
                          "Crea una segunda tabla llamada 'laboratorios' con columnas: 'id' (INTEGER PRIMARY KEY), 'nombre' (TEXT), 'capacidad' (INTEGER).",
                          "Usa CREATE TABLE laboratorios (id INTEGER PRIMARY KEY, nombre TEXT, capacidad INTEGER);",
                          "CREATE TABLE IF NOT EXISTS laboratorios (id INTEGER PRIMARY KEY, nombre TEXT, capacidad INTEGER);",
                          "¡Excelente! Ahora cuentas con dos estructuras modulares en tu esquema relacional.", is_write=True)
            ],
            (2, 2): [
                DailyTask(2, 2, 0, "Día 2 - Ejercicio 1/2: Inserción de Proyecto",
                          "Inserta en 'proyectos' el registro con id=1, titulo='Motor SQL 2D', nota=6.8.",
                          "Usa INSERT INTO proyectos (id, titulo, nota) VALUES (1, 'Motor SQL 2D', 6.8);",
                          "INSERT INTO proyectos (id, titulo, nota) VALUES (1, 'Motor SQL 2D', 6.8);",
                          "¡Gran trabajo! Tu tabla 'proyectos' ya almacena información tangible.", is_write=True),
                DailyTask(2, 2, 1, "Día 2 - Ejercicio 2/2: Segundo Proyecto",
                          "Inserta en 'proyectos' un segundo registro con id=2, titulo='Compilador C', nota=5.9.",
                          "Usa INSERT INTO proyectos (id, titulo, nota) VALUES (2, 'Compilador C', 5.9);",
                          "INSERT INTO proyectos (id, titulo, nota) VALUES (2, 'Compilador C', 5.9);",
                          "¡Perfecto! Los datos persistidos quedan listos para su posterior manipulación.", is_write=True)
            ],
            (2, 3): [
                DailyTask(2, 3, 0, "Día 3 - Ejercicio 1/2: Actualización de Alumnos",
                          "Actualiza la tabla 'estudiantes' para cambiar el 'estado' a 'Graduado' donde el 'promedio' sea >= 6.8.",
                          "Usa UPDATE estudiantes SET estado = 'Graduado' WHERE promedio >= 6.8;",
                          "UPDATE estudiantes SET estado = 'Graduado' WHERE promedio >= 6.8;",
                          "¡Impecable! La cláusula WHERE protegió al resto del padrón de modificaciones masivas.", is_write=True),
                DailyTask(2, 3, 1, "Día 3 - Ejercicio 2/2: Calificación de Proyecto",
                          "Actualiza en la tabla 'proyectos' la 'nota' a 7.0 para el proyecto con id = 1.",
                          "Usa UPDATE proyectos SET nota = 7.0 WHERE id = 1;",
                          "UPDATE proyectos SET nota = 7.0 WHERE id = 1;",
                          "¡Muy bien! Modificar valores específicos por clave primaria es la mejor práctica de la industria.", is_write=True)
            ],
            (2, 4): [
                DailyTask(2, 4, 0, "Día 4 - Ejercicio 1/2: Depuración de Cupos",
                          "Elimina de 'materias' aquellas que no tengan cupos disponibles (cupos = 0).",
                          "Usa DELETE FROM materias WHERE cupos = 0;",
                          "DELETE FROM materias WHERE cupos = 0;",
                          "¡Correcto! Has removido registros que ya no prestan utilidad.", is_write=True),
                DailyTask(2, 4, 1, "Día 4 - Ejercicio 2/2: Depuración de Proyectos Reprobados",
                          "Elimina de la tabla 'proyectos' aquellos con 'nota' menor a 4.0 si existieran.",
                          "Usa DELETE FROM proyectos WHERE nota < 4.0;",
                          "DELETE FROM proyectos WHERE nota < 4.0;",
                          "¡Completado! Año 2 superado con pleno dominio de DDL y DML.", is_write=True)
            ],

            # === AÑO 3: Agregaciones y Relaciones Multitabla ===
            (3, 1): [
                DailyTask(3, 1, 0, "Día 1 - Ejercicio 1/2: Censo Estudiantil",
                          "Calcula la cantidad total de estudiantes registrados en la tabla 'estudiantes' usando COUNT(*).",
                          "Usa SELECT COUNT(*) FROM estudiantes;",
                          "SELECT COUNT(*) FROM estudiantes;",
                          "¡Excelente! COUNT(*) procesa volúmenes masivos de registros en una sola cifra."),
                DailyTask(3, 1, 1, "Día 1 - Ejercicio 2/2: Promedio General y Máximo",
                          "Calcula el promedio general de notas usando AVG(promedio) y la nota máxima con MAX(promedio) de 'estudiantes'.",
                          "Usa SELECT AVG(promedio), MAX(promedio) FROM estudiantes;",
                          "SELECT AVG(promedio), MAX(promedio) FROM estudiantes;",
                          "¡Muy bien! Las funciones agregadas son el núcleo del Business Intelligence.")
            ],
            (3, 2): [
                DailyTask(3, 2, 0, "Día 2 - Ejercicio 1/2: Alumnos por Carrera",
                          "Muestra 'carrera' y la cantidad de alumnos por carrera usando GROUP BY.",
                          "Usa SELECT carrera, COUNT(*) FROM estudiantes GROUP BY carrera;",
                          "SELECT carrera, COUNT(*) FROM estudiantes GROUP BY carrera;",
                          "¡Gran trabajo! GROUP BY organiza tus datos en conjuntos analíticos categorizados."),
                DailyTask(3, 2, 1, "Día 2 - Ejercicio 2/2: Rendimiento por Semestre",
                          "Muestra 'semestre' y el promedio de notas por semestre usando GROUP BY semestre.",
                          "Usa SELECT semestre, AVG(promedio) FROM estudiantes GROUP BY semestre;",
                          "SELECT semestre, AVG(promedio) FROM estudiantes GROUP BY semestre;",
                          "¡Perfecto! Agrupar por dimensiones temporales permite ver la evolución académica.")
            ],
            (3, 3): [
                DailyTask(3, 3, 0, "Día 3 - Ejercicio 1/2: Carreras Destacadas",
                          "Muestra 'carrera' y el promedio de notas por carrera solo para aquellas con promedio >= 5.0 usando HAVING.",
                          "Usa GROUP BY carrera HAVING AVG(promedio) >= 5.0;",
                          "SELECT carrera, AVG(promedio) FROM estudiantes GROUP BY carrera HAVING AVG(promedio) >= 5.0;",
                          "¡Dominado! HAVING filtra grupos calculados, a diferencia de WHERE que filtra filas individuales."),
                DailyTask(3, 3, 1, "Día 3 - Ejercicio 2/2: Cuerpos Docentes Robustos",
                          "Muestra 'departamento' y la cantidad de profesores solo para departamentos con más de 1 profesor.",
                          "Usa SELECT departamento, COUNT(*) FROM profesores GROUP BY departamento HAVING COUNT(*) > 1;",
                          "SELECT departamento, COUNT(*) FROM profesores GROUP BY departamento HAVING COUNT(*) > 1;",
                          "¡Exacto! Filtrar agregaciones con HAVING es una habilidad clave en entrevistas técnicas.")
            ],
            (3, 4): [
                DailyTask(3, 4, 0, "Día 4 - Ejercicio 1/2: Cruce con INNER JOIN",
                          "Une 'estudiantes' con 'notas_parcial' para mostrar el 'nombre' del alumno y su 'nota' en el examen parcial.",
                          "Usa SELECT e.nombre, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id;",
                          "SELECT e.nombre, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id;",
                          "¡IMPRESIONANTE! Has construido tu primer cruce de tablas profesional con INNER JOIN."),
                DailyTask(3, 4, 1, "Día 4 - Ejercicio 2/2: Cruce Multitabla con Filtro",
                          "Une 'estudiantes' con 'notas_parcial' para mostrar 'e.nombre', 'n.materia_codigo' y 'n.nota' donde n.nota >= 6.0.",
                          "Usa SELECT e.nombre, n.materia_codigo, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id WHERE n.nota >= 6.0;",
                          "SELECT e.nombre, n.materia_codigo, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id WHERE n.nota >= 6.0;",
                          "¡Sublime! Combinar JOIN con WHERE es el pan de cada día en sistemas en producción.")
            ],

            # === AÑO 4: Subconsultas, Vistas y Proyecto de Título ===
            (4, 1): [
                DailyTask(4, 1, 0, "Día 1 - Ejercicio 1/2: Subconsultas con IN",
                          "Muestra el 'nombre' de los estudiantes cuyo 'id' aparezca en 'notas_parcial' con nota igual a 7.0.",
                          "Usa WHERE id IN (SELECT estudiante_id FROM notas_parcial WHERE nota = 7.0);",
                          "SELECT nombre FROM estudiantes WHERE id IN (SELECT estudiante_id FROM notas_parcial WHERE nota = 7.0);",
                          "¡Excelente! Las subconsultas anidan consultas dentro de otras para resolver lógicas complejas."),
                DailyTask(4, 1, 1, "Día 1 - Ejercicio 2/2: Subconsulta Comparativa",
                          "Muestra 'nombre' y 'promedio' de estudiantes cuyo promedio sea mayor al promedio general de todos los estudiantes.",
                          "Usa SELECT nombre, promedio FROM estudiantes WHERE promedio > (SELECT AVG(promedio) FROM estudiantes);",
                          "SELECT nombre, promedio FROM estudiantes WHERE promedio > (SELECT AVG(promedio) FROM estudiantes);",
                          "¡Nivel Avanzado! Comparar un campo escalar contra una subconsulta agregada es un patrón senior.")
            ],
            (4, 2): [
                DailyTask(4, 2, 0, "Día 2 - Ejercicio 1/2: Auditoría con LEFT JOIN",
                          "Une 'estudiantes' con 'notas_parcial' usando LEFT JOIN para mostrar 'e.nombre' y 'n.nota'.",
                          "Usa SELECT e.nombre, n.nota FROM estudiantes e LEFT JOIN notas_parcial n ON e.id = n.estudiante_id;",
                          "SELECT e.nombre, n.nota FROM estudiantes e LEFT JOIN notas_parcial n ON e.id = n.estudiante_id;",
                          "¡Perfecto! LEFT JOIN preserva la tabla izquierda incluso si no existen coincidencias en la derecha."),
                DailyTask(4, 2, 1, "Día 2 - Ejercicio 2/2: Detección de Registros Huérfanos",
                          "Muestra 'e.nombre' de los estudiantes que no tengan ninguna nota registrada en 'notas_parcial' (WHERE n.id IS NULL).",
                          "Usa SELECT e.nombre FROM estudiantes e LEFT JOIN notas_parcial n ON e.id = n.estudiante_id WHERE n.id IS NULL;",
                          "SELECT e.nombre FROM estudiantes e LEFT JOIN notas_parcial n ON e.id = n.estudiante_id WHERE n.id IS NULL;",
                          "¡Magistral! La técnica LEFT JOIN + WHERE IS NULL es la forma estándar de auditar inconsistencias.")
            ],
            (4, 3): [
                DailyTask(4, 3, 0, "Día 3 - Ejercicio 1/2: Creación de Vista",
                          "Crea una vista llamada 'vista_honor' con el 'nombre' y 'promedio' de estudiantes con promedio >= 6.0.",
                          "Usa CREATE VIEW vista_honor AS SELECT nombre, promedio FROM estudiantes WHERE promedio >= 6.0;",
                          "CREATE VIEW IF NOT EXISTS vista_honor AS SELECT nombre, promedio FROM estudiantes WHERE promedio >= 6.0;",
                          "¡Genial! Una vista encapsula consultas complejas bajo un alias reutilizable.", is_write=True),
                DailyTask(4, 3, 1, "Día 3 - Ejercicio 2/2: Consulta de Vista Virtual",
                          "Ejecuta una consulta para seleccionar todas las columnas de la vista 'vista_honor' recién creada.",
                          "Usa SELECT * FROM vista_honor;",
                          "SELECT * FROM vista_honor;",
                          "¡Excelente! La vista se consulta como si fuese una tabla física pero sin redundancia de almacenamiento.")
            ],
            (4, 4): [
                DailyTask(4, 4, 0, "Día 4 - Ejercicio 1/2: Optimización con Índices",
                          "Crea un índice llamado 'idx_carrera' sobre la columna 'carrera' de la tabla 'estudiantes'.",
                          "Usa CREATE INDEX idx_carrera ON estudiantes (carrera);",
                          "CREATE INDEX IF NOT EXISTS idx_carrera ON estudiantes (carrera);",
                          "¡Nivel Senior! Los índices en árbol B aceleran las búsquedas de O(N) a O(log N).", is_write=True),
                DailyTask(4, 4, 1, "Día 4 - Ejercicio 2/2: Plan de Ejecución",
                          "Usa EXPLAIN QUERY PLAN para verificar cómo SQLite optimiza la búsqueda por carrera en 'estudiantes'.",
                          "Usa EXPLAIN QUERY PLAN SELECT * FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                          "EXPLAIN QUERY PLAN SELECT * FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                          "¡Felicidades! Entender el plan de ejecución separa a un programador junior de un verdadero Senior.", is_write=True)
            ]
        }

        # Exámenes Parciales de Viernes por Año
        self.exams = {
            1: [
                ExamQuestion(1, "Año 1 - Q1: Profesores de Informática",
                             "Muestra 'nombre' y 'oficina' de profesores del departamento 'Ciencias de la Computacion'.",
                             "SELECT nombre, oficina FROM profesores WHERE departamento = 'Ciencias de la Computacion';"),
                ExamQuestion(2, "Año 1 - Q2: Materias por Carga",
                             "Muestra todas las columnas de 'materias' ordenadas por 'creditos' de mayor a menor (DESC).",
                             "SELECT * FROM materias ORDER BY creditos DESC;"),
                ExamQuestion(3, "Año 1 - Q3: El Mejor de Ciencia de Datos",
                             "Muestra 'nombre' y 'promedio' del alumno de 'Ciencia de Datos' con mejor promedio (1 fila).",
                             "SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ciencia de Datos' ORDER BY promedio DESC LIMIT 1;")
            ],
            2: [
                ExamQuestion(1, "Año 2 - Q1: Consulta de Proyectos Creados",
                             "Muestra todas las columnas de la tabla 'proyectos'.",
                             "SELECT * FROM proyectos;"),
                ExamQuestion(2, "Año 2 - Q2: Estudiantes Activos",
                             "Muestra 'nombre' y 'carrera' de estudiantes cuyo 'estado' sea 'Activo'.",
                             "SELECT nombre, carrera FROM estudiantes WHERE estado = 'Activo';"),
                ExamQuestion(3, "Año 2 - Q3: Materias Disponibles",
                             "Muestra 'nombre' y 'cupos' de materias con más de 5 cupos ordenadas por 'cupos' ASC.",
                             "SELECT nombre, cupos FROM materias WHERE cupos > 5 ORDER BY cupos ASC;")
            ],
            3: [
                ExamQuestion(1, "Año 3 - Q1: Conteo Total de Evaluaciones",
                             "Calcula cuántas notas están registradas en la tabla 'notas_parcial'.",
                             "SELECT COUNT(*) FROM notas_parcial;"),
                ExamQuestion(2, "Año 3 - Q2: Promedio por Materia",
                             "Muestra 'materia_codigo' y el promedio de notas agrupado por 'materia_codigo'.",
                             "SELECT materia_codigo, AVG(nota) FROM notas_parcial GROUP BY materia_codigo;"),
                ExamQuestion(3, "Año 3 - Q3: Cruce Estudiante-Nota",
                             "Muestra 'e.nombre' y 'n.nota' uniendo 'estudiantes' con 'notas_parcial' donde nota >= 6.0.",
                             "SELECT e.nombre, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id WHERE n.nota >= 6.0;")
            ],
            4: [
                # ¡EXAMEN DE GRADO OFICIAL!
                ExamQuestion(1, "Grado - Q1: Subconsulta de Excelencia",
                             "Selecciona 'nombre' y 'promedio' de estudiantes cuyo promedio sea mayor al promedio general de todos los estudiantes.",
                             "SELECT nombre, promedio FROM estudiantes WHERE promedio > (SELECT AVG(promedio) FROM estudiantes);"),
                ExamQuestion(2, "Grado - Q2: Ranking General Multitabla",
                             "Une 'estudiantes' con 'notas_parcial' para mostrar 'e.carrera' y la nota máxima MAX(n.nota) agrupada por carrera.",
                             "SELECT e.carrera, MAX(n.nota) FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id GROUP BY e.carrera;"),
                ExamQuestion(3, "Grado - Q3: Los Mejores de Informática",
                             "Muestra 'nombre' y 'promedio' de los 2 mejores estudiantes de 'Ingenieria Informatica'.",
                             "SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ingenieria Informatica' ORDER BY promedio DESC LIMIT 2;")
            ]
        }

    def get_current_task(self):
        tasks_today = self.tasks.get((self.current_year, self.current_day), [])
        if not tasks_today:
            return None
        if self.current_task_idx < len(tasks_today):
            return tasks_today[self.current_task_idx]
        return tasks_today[-1]

    def get_total_tasks_today(self):
        tasks_today = self.tasks.get((self.current_year, self.current_day), [])
        return len(tasks_today)

    def advance_daily_task(self):
        """Avanza al siguiente ejercicio del día si existe, o marca el día como completado."""
        tasks_today = self.tasks.get((self.current_year, self.current_day), [])
        if self.current_task_idx + 1 < len(tasks_today):
            self.current_task_idx += 1
            return False, self.get_current_task() # Quedan más ejercicios hoy
        else:
            self.day_task_completed = True
            return True, None # ¡Día completo!

    def get_current_exam_questions(self):
        return self.exams.get(self.current_year, [])

    def get_current_exam_question(self):
        qs = self.get_current_exam_questions()
        if self.current_day == 5 and self.exam_q_index < len(qs):
            return qs[self.exam_q_index]
        return None

    def advance_exam_question(self, was_correct):
        if was_correct:
            self.exam_score += 1
        self.exam_q_index += 1
        qs = self.get_current_exam_questions()

        if self.exam_q_index >= len(qs):
            self.exam_finished = True
            grades = {0: 1.0, 1: 3.0, 2: 5.0, 3: 7.0}
            self.exam_final_grade = grades.get(self.exam_score, 1.0)
            self.save.data["last_grade"] = self.exam_final_grade
            self.save.save()
            return True, self.exam_final_grade >= 4.0
        return False, False

    def finish_day(self):
        """Avanza al siguiente día académico y desbloquea el apunte en el cuaderno."""
        task = self.get_current_task()
        if task and task.note_id:
            self.save.unlock_note(task.note_id)

        if self.current_day < 5:
            self.current_day += 1
            self.current_task_idx = 0
            self.day_task_completed = False
            self.lecture_done_for_day = False
            self.save.data["current_day"] = self.current_day
            self.save.save()
            self.audio.play_bell()

    def advance_to_next_year(self):
        """Avanza al siguiente año académico tras aprobar el examen del viernes."""
        if self.current_year < 4:
            self.current_year += 1
            self.current_day = 1
            self.current_task_idx = 0
            self.day_task_completed = False
            self.lecture_done_for_day = False
            self.exam_active = False
            self.exam_q_index = 0
            self.exam_score = 0
            self.exam_finished = False

            self.save.data["current_year"] = self.current_year
            self.save.data["current_day"] = 1
            self.save.save()
            self.audio.play_success()
            return True # Avanzó de año
        else:
            # ¡Graduado de 4to Año!
            self.save.data["is_graduated"] = True
            self.save.save()
            self.audio.play_success()
            return False # Titulado

    def repeat_current_year(self):
        """Repite el año actual si reprueba el examen (< 4.0). NUNCA retrocede a años anteriores."""
        self.current_day = 1
        self.current_task_idx = 0
        self.day_task_completed = False
        self.lecture_done_for_day = False
        self.exam_active = False
        self.exam_q_index = 0
        self.exam_score = 0
        self.exam_finished = False

        attempts_dict = self.save.data.setdefault("year_attempts", {})
        cur_att = attempts_dict.get(str(self.current_year), 1) + 1
        attempts_dict[str(self.current_year)] = cur_att
        self.save.data["current_day"] = 1
        self.save.save()
        self.audio.play_bell()

    def get_year_attempts(self):
        return self.save.data.get("year_attempts", {}).get(str(self.current_year), 1)
