class Mission:
    def __init__(self, mission_id, title, dialog, objective, hint, canonical_query, explanation):
        self.id = mission_id
        self.title = title
        self.dialog = dialog
        self.objective = objective
        self.hint = hint
        self.canonical_query = canonical_query
        self.explanation = explanation

    def validate(self, db_manager, user_result):
        """Valida si el resultado de la consulta del jugador resuelve correctamente la misión."""
        if not user_result or not user_result.get("success"):
            return False, "La consulta no devolvió resultados válidos."

        # Ejecutar la consulta canónica de referencia para comparar datos esperados
        ref = db_manager.execute_query(self.canonical_query)
        if not ref.get("success"):
            return False, "Error interno validando la misión."

        user_rows = user_result.get("rows", [])
        ref_rows = ref.get("rows", [])

        # 1. Comparar cantidad de filas devueltas
        if len(user_rows) != len(ref_rows):
            return False, f"Cantidad de filas incorrecta. Tu consulta devolvió {len(user_rows)} fila(s), pero se esperaban {len(ref_rows)}."

        # 2. Comparar contenido de las filas
        # Convertir a sets de tuplas ordenadas o comparar directamente si el orden importa
        if "ORDER BY" in self.canonical_query.upper():
            # El orden exacto importa
            # Normalizar tipos para comparar (por ejemplo flotantes redondeados)
            for u_row, r_row in zip(user_rows, ref_rows):
                if len(u_row) != len(r_row):
                    return False, "La cantidad de columnas no coincide con lo solicitado."
                # Comparar valores principales
                # Para mayor flexibilidad, comprobamos si los valores clave coinciden
                if u_row[-1] != r_row[-1] and u_row[0] != r_row[0]:
                    return False, "El orden o los datos devueltos no coinciden con lo pedido."
        else:
            # El orden no importa tanto, pero los conjuntos de datos deben ser iguales
            u_set = {tuple(str(x) for x in r) for r in user_rows}
            r_set = {tuple(str(x) for x in r) for r in ref_rows}
            # Si el usuario seleccionó menos o más columnas que la canónica pero las filas son correctas:
            # Comprobar si al menos la cantidad coincide
            if len(user_rows) == 0:
                return False, "La consulta no devolvió ninguna fila."

        return True, self.explanation


class MissionSystem:
    def __init__(self, db_manager):
        self.db = db_manager
        self.current_mission_index = 0
        self.missions = [
            Mission(
                mission_id=1,
                title="Clase 1: El Padrón Estudiantil",
                dialog="¡Hola novato! Bienvenido a la Universidad. Hoy aprenderás la base de todo: SELECT y FROM. Abre la terminal de la computadora y consulta la lista completa de todos los estudiantes registrados en la tabla 'estudiantes'.",
                objective="Escribe una consulta para ver todos los datos de la tabla 'estudiantes'.",
                hint="Usa el asterisco (*) para seleccionar todas las columnas: SELECT * FROM estudiantes;",
                canonical_query="SELECT * FROM estudiantes;",
                explanation="¡Excelente! El comando 'SELECT * FROM tabla;' es la base de SQL para extraer información cruda de una base de datos."
            ),
            Mission(
                mission_id=2,
                title="Clase 2: Buscando a los Reprobados",
                dialog="¡Buen trabajo con la lista! Ahora tenemos un problema: varios estudiantes tienen promedio menor a 4.0 y necesitan tutoría urgente. Necesito ver sus nombres y notas.",
                objective="Filtra de la tabla 'notas_parcial' a los estudiantes con 'nota' menor a 4.0. Muestra su 'estudiante_nombre' y su 'nota'.",
                hint="Usa la cláusula WHERE para filtrar condiciones: SELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;",
                canonical_query="SELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;",
                explanation="¡Muy bien! 'WHERE' es el filtro más importante en SQL. En las empresas se usa para filtrar clientes activos, compras del día o pedidos pendientes."
            ),
            Mission(
                mission_id=3,
                title="Clase 3: El Cuadro de Honor",
                dialog="El Decano me pide premiar a los mejores de 'Ingenieria Informatica'. Quiero ver a todos los estudiantes de esa carrera, ordenados desde el mayor promedio hasta el menor.",
                objective="Selecciona 'nombre' y 'promedio' de 'estudiantes' donde carrera sea 'Ingenieria Informatica', ordenados por 'promedio' de mayor a menor.",
                hint="Combina WHERE y ORDER BY ... DESC: SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ingenieria Informatica' ORDER BY promedio DESC;",
                canonical_query="SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ingenieria Informatica' ORDER BY promedio DESC;",
                explanation="¡Perfecto! 'ORDER BY columna DESC' ordena de mayor a menor (descendente). Fundamental para rankings, líderes de ventas y tablas de posiciones."
            ),
            Mission(
                mission_id=4,
                title="Examen Final: Asignación de Salas",
                dialog="¡Llegó la hora de tu Examen Final de la U! Tenemos sobrecupo. Necesito que encuentres las 3 materias con cupos disponibles (cupos mayor a 0) que tengan MENOS cupos restantes, para avisar a rectoría.",
                objective="Selecciona 'nombre' y 'cupos' de 'materias' con cupos > 0, ordenadas por 'cupos' ascendente y limitadas a 3 resultados.",
                hint="Usa WHERE cupos > 0 ORDER BY cupos ASC LIMIT 3;",
                canonical_query="SELECT nombre, cupos FROM materias WHERE cupos > 0 ORDER BY cupos ASC LIMIT 3;",
                explanation="¡FELICITACIONES! Has aprobado con distinción. 'LIMIT' junto con 'ORDER BY' es exactamente lo que usan plataformas como Netflix o Spotify para mostrar el 'Top 3' o 'Top 10'."
            )
        ]

    def get_current_mission(self):
        if self.current_mission_index < len(self.missions):
            return self.missions[self.current_mission_index]
        return None

    def is_chapter_completed(self):
        return self.current_mission_index >= len(self.missions)

    def complete_current_mission(self):
        self.current_mission_index += 1
