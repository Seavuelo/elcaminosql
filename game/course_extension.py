"""Material adicional por jornada: concepto, explicación, ejemplo y dos prácticas."""
LESSONS = {
    (1, 1): ("Proyección y DISTINCT", "SELECT elige columnas; FROM identifica la tabla. DISTINCT elimina filas repetidas del resultado, no borra registros. Prueba primero la consulta sin DISTINCT y compara.", "SELECT DISTINCT carrera FROM estudiantes;", [
        ("Carreras sin repetir", "Muestra solo 'carrera', sin carreras repetidas.", "SELECT DISTINCT carrera FROM estudiantes;"),
        ("Mapa de semestres", "Muestra solo 'semestre', sin semestres repetidos.", "SELECT DISTINCT semestre FROM estudiantes;")]),
    (1, 2): ("Combinar condiciones", "AND exige que ambas condiciones se cumplan. OR acepta cualquiera. Usa paréntesis al mezclarlos. Los límites inclusivos usan >= o <=; un límite estricto usa > o <.", "SELECT nombre FROM estudiantes WHERE semestre = 2 AND promedio >= 6.0;", [
        ("Tutoría focalizada", "Muestra 'nombre' y 'promedio' de estudiantes Activos con promedio menor a 5.0.", "SELECT nombre, promedio FROM estudiantes WHERE estado = 'Activo' AND promedio < 5.0;"),
        ("Dos semestres", "Muestra 'nombre' y 'semestre' de estudiantes de semestre 1 o 3.", "SELECT nombre, semestre FROM estudiantes WHERE semestre = 1 OR semestre = 3;")]),
    (1, 3): ("Orden y desempates", "ORDER BY puede tener varios criterios. El segundo resuelve empates del primero. Las columnas elegidas y su orden son decisiones distintas. Sin ORDER BY, el orden de las filas no está garantizado.", "SELECT nombre, semestre FROM estudiantes ORDER BY semestre ASC, nombre ASC;", [
        ("Listado por semestre", "Muestra 'nombre' y 'semestre', ordenados por semestre ASC y, en empates, nombre ASC.", "SELECT nombre, semestre FROM estudiantes ORDER BY semestre ASC, nombre ASC;"),
        ("Materias por carga", "Muestra 'nombre' y 'creditos' de materias, por creditos DESC y nombre ASC en empates.", "SELECT nombre, creditos FROM materias ORDER BY creditos DESC, nombre ASC;")]),
    (1, 4): ("Páginas con OFFSET", "LIMIT toma una cantidad de filas y OFFSET salta filas del resultado ordenado. La segunda página de dos filas usa LIMIT 2 OFFSET 2. Ordena siempre antes de paginar para obtener páginas estables.", "SELECT nombre FROM estudiantes ORDER BY nombre ASC LIMIT 2 OFFSET 2;", [
        ("Segunda página", "Muestra 'nombre' y 'promedio' de estudiantes por nombre ASC: salta los dos primeros y entrega los dos siguientes.", "SELECT nombre, promedio FROM estudiantes ORDER BY nombre ASC LIMIT 2 OFFSET 2;"),
        ("Filtro y podio", "Muestra 'nombre' y 'promedio' de los dos Activos con mayor promedio; desempata por nombre ASC.", "SELECT nombre, promedio FROM estudiantes WHERE estado = 'Activo' ORDER BY promedio DESC, nombre ASC LIMIT 2;")]),
    (2, 1): ("Diseñar restricciones", "PRIMARY KEY identifica cada fila. NOT NULL impide omitir un valor. TEXT guarda texto y REAL números decimales. SQLite permite conversiones de tipos; no valida por sí solo todas las reglas de un negocio.", "CREATE TABLE entregas (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL);", [
        ("Entregas identificadas", "Crea 'entregas': id INTEGER PRIMARY KEY y titulo TEXT NOT NULL.", "CREATE TABLE IF NOT EXISTS entregas (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL);"),
        ("Inventario del curso", "Crea 'equipos': id INTEGER PRIMARY KEY, nombre TEXT NOT NULL y unidades INTEGER.", "CREATE TABLE IF NOT EXISTS equipos (id INTEGER PRIMARY KEY, nombre TEXT NOT NULL, unidades INTEGER);")]),
    (2, 2): ("NULL y listas de columnas", "Indica las columnas al insertar: así no dependes de su posición física. NULL representa un dato desconocido o pendiente; no es cero ni el texto 'NULL'. Un identificador PRIMARY KEY repetido produce un error.", "INSERT INTO proyectos (id, titulo, nota) VALUES (3, 'Tutor virtual', NULL);", [
        ("Nota pendiente", "Inserta en proyectos: id 3, titulo 'Tutor virtual' y nota NULL.", "INSERT INTO proyectos (id, titulo, nota) VALUES (3, 'Tutor virtual', NULL);"),
        ("Laboratorio disponible", "Inserta en laboratorios: id 1, nombre 'Redes' y capacidad 20.", "INSERT INTO laboratorios (id, nombre, capacidad) VALUES (1, 'Redes', 20);")]),
    (2, 3): ("Actualizar con precisión", "Antes de UPDATE, consulta con SELECT el mismo WHERE. SET cambia los valores; WHERE decide las filas. Actualizar cero filas puede ser correcto si ninguna cumple el criterio. Revisa también las filas que deben permanecer iguales.", "UPDATE laboratorios SET capacidad = 30 WHERE id = 1;", [
        ("Evaluación pendiente resuelta", "Cambia a 4.5 la nota del proyecto con id 3, sin modificar otros proyectos.", "UPDATE proyectos SET nota = 4.5 WHERE id = 3;"),
        ("Ampliación de sala", "Cambia a 30 la capacidad del laboratorio con id 1.", "UPDATE laboratorios SET capacidad = 30 WHERE id = 1;")]),
    (2, 4): ("Eliminar sin perder la estructura", "DELETE borra filas; la tabla sigue existiendo. DROP TABLE elimina la estructura completa. Verifica un DELETE con un SELECT del mismo filtro. En estos ejercicios una respuesta incorrecta se revierte antes de guardarse.", "SELECT * FROM laboratorios WHERE capacidad < 35;", [
        ("Salas pequeñas", "Elimina de laboratorios las filas con capacidad menor a 35.", "DELETE FROM laboratorios WHERE capacidad < 35;"),
        ("Archivo de proyectos", "Elimina de proyectos las filas con nota menor a 6.0, conservando las demás.", "DELETE FROM proyectos WHERE nota < 6.0;")]),
    (3, 1): ("Contar datos ausentes", "COUNT(*) cuenta filas. COUNT(columna) cuenta valores no NULL. AVG, MIN y MAX omiten NULL. La tabla tutorias incluye una asistencia pendiente: compara ambas formas de COUNT para descubrirla.", "SELECT COUNT(*), COUNT(asistencia) FROM tutorias;", [
        ("Asistencias conocidas", "Muestra COUNT(*) y COUNT(asistencia) de tutorias.", "SELECT COUNT(*), COUNT(asistencia) FROM tutorias;"),
        ("Extremos y carga", "Muestra MIN(promedio), MAX(promedio) y SUM(semestre) de estudiantes.", "SELECT MIN(promedio), MAX(promedio), SUM(semestre) FROM estudiantes;")]),
    (3, 2): ("Una fila por grupo", "GROUP BY devuelve un resumen por categoría. Si agregas una columna sin agruparla ni resumirla, SQLite puede elegir un valor arbitrario. Agrupa por estudiante_id para ver cuántas tutorías tiene cada estudiante.", "SELECT estudiante_id, COUNT(*) FROM tutorias GROUP BY estudiante_id;", [
        ("Carga de tutoría", "Muestra 'estudiante_id' y COUNT(*) de tutorias, agrupando por estudiante_id.", "SELECT estudiante_id, COUNT(*) FROM tutorias GROUP BY estudiante_id;"),
        ("Promedio por estado", "Muestra 'estado' y AVG(promedio) de estudiantes, agrupando por estado.", "SELECT estado, AVG(promedio) FROM estudiantes GROUP BY estado;")]),
    (3, 3): ("Dos filtros, dos momentos", "WHERE filtra las filas de entrada. HAVING filtra el resumen de cada grupo. Puedes usarlos juntos: primero elige estudiantes Activos; después conserva las carreras cuyo promedio supere el mínimo.", "SELECT carrera, AVG(promedio) FROM estudiantes WHERE estado = 'Activo' GROUP BY carrera HAVING AVG(promedio) > 5.0;", [
        ("Tutorías repetidas", "Muestra 'estudiante_id' y COUNT(*) de tutorias solo para estudiantes con más de una tutoría.", "SELECT estudiante_id, COUNT(*) FROM tutorias GROUP BY estudiante_id HAVING COUNT(*) > 1;"),
        ("Carreras con masa crítica", "Muestra 'carrera' y COUNT(*) de estudiantes solo para carreras con al menos 3 estudiantes.", "SELECT carrera, COUNT(*) FROM estudiantes GROUP BY carrera HAVING COUNT(*) >= 3;")]),
    (3, 4): ("Relaciones uno a muchos", "Un estudiante puede tener varias tutorías: JOIN produce una fila por coincidencia. Eso no es un error ni siempre se arregla con DISTINCT. Primero identifica si necesitas contar estudiantes o contar sus tutorías.", "SELECT e.nombre, t.tema FROM estudiantes e JOIN tutorias t ON e.id = t.estudiante_id;", [
        ("Agenda cruzada", "Muestra 'e.nombre' y 't.tema' uniendo estudiantes e con tutorias t por id y estudiante_id.", "SELECT e.nombre, t.tema FROM estudiantes e JOIN tutorias t ON e.id = t.estudiante_id;"),
        ("Pendientes con nombre", "Del mismo cruce, muestra 'e.nombre' y 't.tema' solo cuando t.asistencia IS NULL.", "SELECT e.nombre, t.tema FROM estudiantes e JOIN tutorias t ON e.id = t.estudiante_id WHERE t.asistencia IS NULL;")]),
    (4, 1): ("Subconsultas y ausencia", "IN busca pertenencia a un conjunto. IS NULL detecta un dato desconocido: '= NULL' no funciona como una comparación habitual. Prueba la subconsulta sola y luego intégrala en el filtro exterior.", "SELECT nombre FROM estudiantes WHERE id IN (SELECT estudiante_id FROM tutorias WHERE asistencia IS NULL);", [
        ("Seguimiento pendiente", "Muestra 'nombre' de estudiantes con alguna tutoría cuya asistencia sea NULL; usa una subconsulta.", "SELECT nombre FROM estudiantes WHERE id IN (SELECT estudiante_id FROM tutorias WHERE asistencia IS NULL);"),
        ("Sin agenda", "Muestra 'nombre' de estudiantes cuyo id no aparezca en tutorias; estudiante_id nunca es NULL en esta tabla.", "SELECT nombre FROM estudiantes WHERE id NOT IN (SELECT estudiante_id FROM tutorias);")]),
    (4, 2): ("NULL después de LEFT JOIN", "LEFT JOIN conserva estudiantes sin tutorías. WHERE t.id IS NULL encuentra esas ausencias. En cambio, WHERE t.asistencia IS NULL también incluye tutorías existentes con asistencia pendiente: no son la misma pregunta.", "SELECT e.nombre FROM estudiantes e LEFT JOIN tutorias t ON e.id = t.estudiante_id WHERE t.id IS NULL;", [
        ("Agenda completa", "Muestra 'e.nombre' y 't.tema' de todos los estudiantes, incluso sin tutorías, usando LEFT JOIN.", "SELECT e.nombre, t.tema FROM estudiantes e LEFT JOIN tutorias t ON e.id = t.estudiante_id;"),
        ("Ausencia o pendiente", "Del mismo LEFT JOIN, muestra 'e.nombre' y 't.tema' donde t.asistencia IS NULL.", "SELECT e.nombre, t.tema FROM estudiantes e LEFT JOIN tutorias t ON e.id = t.estudiante_id WHERE t.asistencia IS NULL;")]),
    (4, 3): ("Consultar una vista", "La vista guarda una consulta, no una copia independiente de los datos. Puedes aplicarle WHERE, ORDER BY y agregaciones. Cambiar las tablas de origen puede cambiar lo que devuelve la vista la próxima vez que la consultes.", "SELECT nombre, promedio FROM vista_honor ORDER BY promedio DESC, nombre ASC;", [
        ("Honor ordenado", "Muestra 'nombre' y 'promedio' de vista_honor por promedio DESC y nombre ASC en empates.", "SELECT nombre, promedio FROM vista_honor ORDER BY promedio DESC, nombre ASC;"),
        ("Resumen del honor", "Muestra COUNT(*) y AVG(promedio) de vista_honor.", "SELECT COUNT(*), AVG(promedio) FROM vista_honor;")]),
    (4, 4): ("Interpretar el plan", "SCAN recorre una tabla o un índice. SEARCH busca con un criterio aprovechable. Un índice no siempre acelera una consulta: depende de los datos y del filtro. EXPLAIN QUERY PLAN muestra la estrategia, sin ejecutar la consulta completa.", "EXPLAIN QUERY PLAN SELECT nombre FROM estudiantes WHERE carrera = 'Ciencia de Datos';", [
        ("Inspección de búsqueda", "Inspecciona con EXPLAIN QUERY PLAN un SELECT nombre de estudiantes donde carrera sea 'Ciencia de Datos'.", "EXPLAIN QUERY PLAN SELECT nombre FROM estudiantes WHERE carrera = 'Ciencia de Datos';"),
        ("Consulta integrada", "Muestra 'nombre' y 'promedio' de Ciencia de Datos con promedio >= 5.0; ordena por promedio DESC y nombre ASC.", "SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ciencia de Datos' AND promedio >= 5.0 ORDER BY promedio DESC, nombre ASC;")]),
}

EXTRA_EXAMS = {
    1: [
        ("Filtro compuesto", "Muestra 'nombre' y 'promedio' de estudiantes Activos con promedio >= 5.5, por promedio DESC y nombre ASC en empates.", "SELECT nombre, promedio FROM estudiantes WHERE estado = 'Activo' AND promedio >= 5.5 ORDER BY promedio DESC, nombre ASC;"),
        ("Página de semestres", "Muestra 'nombre' y 'semestre' por semestre ASC y nombre ASC en empates; salta las dos primeras filas y devuelve las tres siguientes.", "SELECT nombre, semestre FROM estudiantes ORDER BY semestre ASC, nombre ASC LIMIT 3 OFFSET 2;")],
    2: [
        ("Acta de revisión", "Crea la tabla revision con id INTEGER PRIMARY KEY y aprobado INTEGER.", "CREATE TABLE IF NOT EXISTS revision (id INTEGER PRIMARY KEY, aprobado INTEGER);"),
        ("Reevaluación final", "Actualiza solo el proyecto de id 1: su nota debe quedar en 6.9.", "UPDATE proyectos SET nota = 6.9 WHERE id = 1;")],
    3: [
        ("Varias tutorías", "Muestra 'estudiante_id' y COUNT(*) de tutorias solo para estudiantes con al menos dos tutorías.", "SELECT estudiante_id, COUNT(*) FROM tutorias GROUP BY estudiante_id HAVING COUNT(*) >= 2;"),
        ("Asistencia por estudiante", "Muestra 'e.nombre' y 't.asistencia' uniendo estudiantes con tutorias, solo con asistencia conocida (IS NOT NULL).", "SELECT e.nombre, t.asistencia FROM estudiantes e JOIN tutorias t ON e.id = t.estudiante_id WHERE t.asistencia IS NOT NULL;")],
    4: [
        ("Auditoría sin tutorías", "Muestra 'e.nombre' de estudiantes sin tutorías, usando LEFT JOIN y t.id IS NULL.", "SELECT e.nombre FROM estudiantes e LEFT JOIN tutorias t ON e.id = t.estudiante_id WHERE t.id IS NULL;"),
        ("Honor sobre la media", "Muestra 'nombre' y 'promedio' de vista_honor con promedio mayor a la media de estudiantes; ordena por promedio DESC y nombre ASC.", "SELECT nombre, promedio FROM vista_honor WHERE promedio > (SELECT AVG(promedio) FROM estudiantes) ORDER BY promedio DESC, nombre ASC;")],
}


def extend_curriculum(course):
    from game.curriculum import DailyTask, ExamQuestion
    for (year, day), (_, _, _, practices) in LESSONS.items():
        tasks = course.tasks[(year, day)]
        for title, objective, query in practices:
            tasks.append(DailyTask(year, day, len(tasks), title, objective, query, query,
                                   "Compara el resultado con el objetivo y revisa qué filas se incluyeron.",
                                   is_write=year == 2))
        for index, task in enumerate(tasks):
            topic = task.title.split(": ")[-1]
            task.title = f"Ejercicio {index + 1}/{len(tasks)}: {topic}"
    for year, questions in EXTRA_EXAMS.items():
        for title, objective, query in questions:
            course.exams[year].append(ExamQuestion(len(course.exams[year]) + 1, title, objective, query,
                                                  is_write=query.startswith(("CREATE", "UPDATE"))))
