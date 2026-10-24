import pygame
from game.constants import *
from game.ui_helpers import draw_panel, render_wrapped_text

class StudentNotebook:
    """Cuaderno de Apuntes del estudiante: Se desbloquean resúmenes y fórmulas a medida que aprueba días."""
    def __init__(self, audio_manager, save_system):
        self.audio = audio_manager
        self.save = save_system
        self.active = False
        self.current_page = 0

        self.font_title = pygame.font.Font(None, 15)
        self.font_subtitle = pygame.font.Font(None, 13)
        self.font_body = pygame.font.Font(None, 12)
        self.font_code = pygame.font.Font(None, 12)
        self.font_hint = pygame.font.Font(None, 11)
        self.font_label = pygame.font.Font(None, 12)

        self.all_notes = self._build_knowledge_base()

    def _build_knowledge_base(self):
        return [
            {
                "id": "y1_d1",
                "year": 1,
                "day": 1,
                "title": "Año 1, Día 1: El Modelo Relacional y SELECT",
                "concept": "Las bases de datos relacionales guardan datos en tablas con filas (registros) y columnas (atributos).",
                "syntax": "SELECT columna1, columna2 FROM tabla;\nSELECT * FROM tabla; -- Trae todas las columnas",
                "example": "SELECT nombre, carrera FROM estudiantes;",
                "tip": "El asterisco (*) es práctico para explorar, pero en producción selecciona solo las columnas que necesitas."
            },
            {
                "id": "y1_d2",
                "year": 1,
                "day": 2,
                "title": "Año 1, Día 2: Filtros con la Cláusula WHERE",
                "concept": "WHERE evalúa una condición booleana para cada fila. Solo devuelve las filas donde la condición es VERDADERA.",
                "syntax": "SELECT columnas FROM tabla WHERE condicion;\nOperadores: =, !=, <, >, <=, >=, AND, OR",
                "example": "SELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;",
                "tip": "El texto siempre debe ir entre comillas simples: carrera = 'Ingenieria'."
            },
            {
                "id": "y1_d3",
                "year": 1,
                "day": 3,
                "title": "Año 1, Día 3: Ordenamiento con ORDER BY",
                "concept": "Por defecto, SQL no garantiza ningún orden. ORDER BY organiza los resultados de forma ascendente (ASC) o descendente (DESC).",
                "syntax": "SELECT columnas FROM tabla ORDER BY columna [ASC | DESC];",
                "example": "SELECT nombre, promedio FROM estudiantes ORDER BY promedio DESC;",
                "tip": "Si no especificas ASC o DESC, SQL ordenará automáticamente de menor a mayor (ASC)."
            },
            {
                "id": "y1_d4",
                "year": 1,
                "day": 4,
                "title": "Año 1, Día 4: Paginación con LIMIT y Estructura",
                "concept": "LIMIT restringe la cantidad máxima de filas devueltas. Se coloca siempre al final de la consulta.",
                "syntax": "SELECT columnas FROM tabla WHERE filtro ORDER BY orden LIMIT cantidad;",
                "example": "SELECT nombre, cupos FROM materias WHERE cupos > 0 ORDER BY cupos ASC LIMIT 3;",
                "tip": "El orden de cláusulas obligatorio es: SELECT -> FROM -> WHERE -> ORDER BY -> LIMIT."
            },
            {
                "id": "y2_d1",
                "year": 2,
                "day": 1,
                "title": "Año 2, Día 1: Creación de Tablas (DDL)",
                "concept": "CREATE TABLE define una nueva estructura con sus tipos de datos (INTEGER, TEXT, REAL, BLOB).",
                "syntax": "CREATE TABLE nombre (\n    id INTEGER PRIMARY KEY AUTOINCREMENT,\n    campo1 TIPO NOT NULL,\n    campo2 TIPO\n);",
                "example": "CREATE TABLE proyectos (id INTEGER PRIMARY KEY, titulo TEXT NOT NULL, nota REAL);",
                "tip": "PRIMARY KEY identifica de forma única e irrepetible a cada fila en la tabla."
            },
            {
                "id": "y2_d2",
                "year": 2,
                "day": 2,
                "title": "Año 2, Día 2: Inserción de Datos (INSERT INTO)",
                "concept": "INSERT INTO agrega nuevas filas a una tabla existente con sus respectivos valores.",
                "syntax": "INSERT INTO tabla (columna1, columna2) VALUES (valor1, valor2);",
                "example": "INSERT INTO proyectos (titulo, nota) VALUES ('Motor 2D SQL', 6.8);",
                "tip": "Si omites las columnas, debes entregar los valores de TODAS las columnas en orden exacto."
            },
            {
                "id": "y2_d3",
                "year": 2,
                "day": 3,
                "title": "Año 2, Día 3: Modificación de Datos (UPDATE)",
                "concept": "UPDATE altera el valor de una o más columnas en registros existentes.",
                "syntax": "UPDATE tabla SET columna = nuevo_valor WHERE condicion;",
                "example": "UPDATE estudiantes SET estado = 'Egresado' WHERE promedio >= 5.5;",
                "tip": "¡CUIDADO SENIOR! Si olvidas el WHERE en un UPDATE, modificarás TODA la tabla de producción."
            },
            {
                "id": "y2_d4",
                "year": 2,
                "day": 4,
                "title": "Año 2, Día 4: Borrado de Datos (DELETE)",
                "concept": "DELETE FROM elimina filas completas que cumplan una condición.",
                "syntax": "DELETE FROM tabla WHERE condicion;",
                "example": "DELETE FROM materias WHERE cupos = 0;",
                "tip": "Al igual que con UPDATE, un DELETE sin WHERE vacía la tabla por completo."
            },
            {
                "id": "y3_d1",
                "year": 3,
                "day": 1,
                "title": "Año 3, Día 1: Funciones de Agregación",
                "concept": "Calculan un único valor resumen a partir de un conjunto de filas: COUNT, SUM, AVG, MIN, MAX.",
                "syntax": "SELECT COUNT(*), AVG(columna), MAX(columna) FROM tabla;",
                "example": "SELECT COUNT(*), AVG(promedio) FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                "tip": "COUNT(*) cuenta todas las filas, mientras que COUNT(columna) ignora los valores NULL."
            },
            {
                "id": "y3_d2",
                "year": 3,
                "day": 2,
                "title": "Año 3, Día 2: Agrupamiento con GROUP BY",
                "concept": "GROUP BY colapsa filas con valores idénticos en filas de resumen, combinándose con funciones agregadas.",
                "syntax": "SELECT categoria, COUNT(*) FROM tabla GROUP BY categoria;",
                "example": "SELECT carrera, COUNT(*), AVG(promedio) FROM estudiantes GROUP BY carrera;",
                "tip": "Cualquier columna que pongas en SELECT que no sea agregada DEBE estar en el GROUP BY."
            },
            {
                "id": "y3_d3",
                "year": 3,
                "day": 3,
                "title": "Año 3, Día 3: Filtro de Grupos con HAVING",
                "concept": "HAVING filtra grupos calculados por GROUP BY. WHERE filtra filas ANTES del agrupamiento.",
                "syntax": "SELECT carrera, AVG(promedio) FROM estudiantes GROUP BY carrera HAVING AVG(promedio) >= 5.0;",
                "example": "SELECT carrera, COUNT(*) FROM estudiantes GROUP BY carrera HAVING COUNT(*) > 3;",
                "tip": "Regla nemotécnica: WHERE filtra filas crudas; HAVING filtra grupos agregados."
            },
            {
                "id": "y3_d4",
                "year": 3,
                "day": 4,
                "title": "Año 3, Día 4: Uniendo Tablas con INNER JOIN",
                "concept": "INNER JOIN combina filas de dos o más tablas en base a una columna relacionada entre ellas.",
                "syntax": "SELECT t1.col, t2.col FROM tabla1 t1 INNER JOIN tabla2 t2 ON t1.id = t2.t1_id;",
                "example": "SELECT e.nombre, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id;",
                "tip": "Usa alias cortos (e, n) para evitar escribir el nombre completo de la tabla una y otra vez."
            },
            {
                "id": "y4_d1",
                "year": 4,
                "day": 1,
                "title": "Año 4, Día 1: Subconsultas en WHERE (IN / NOT IN)",
                "concept": "Una subconsulta es un SELECT anidado dentro de otra consulta para calcular filtros dinámicos.",
                "syntax": "SELECT * FROM tabla WHERE columna IN (SELECT columna FROM otra_tabla WHERE condicion);",
                "example": "SELECT nombre FROM estudiantes WHERE id IN (SELECT estudiante_id FROM notas_parcial WHERE nota = 7.0);",
                "tip": "La subconsulta interna se ejecuta primero y entrega una lista de valores a la consulta principal."
            },
            {
                "id": "y4_d2",
                "year": 4,
                "day": 2,
                "title": "Año 4, Día 2: Registros Huérfanos con LEFT JOIN",
                "concept": "LEFT JOIN devuelve TODAS las filas de la tabla izquierda, y las coincidentes de la derecha. Si no hay coincidencia, rellena con NULL.",
                "syntax": "SELECT t1.col, t2.col FROM tabla1 t1 LEFT JOIN tabla2 t2 ON t1.id = t2.t1_id;",
                "example": "SELECT e.nombre, n.nota FROM estudiantes e LEFT JOIN notas_parcial n ON e.id = n.estudiante_id WHERE n.nota IS NULL;",
                "tip": "LEFT JOIN ... WHERE derecha.id IS NULL es la técnica maestra para encontrar registros sin ventas o sin notas."
            },
            {
                "id": "y4_d3",
                "year": 4,
                "day": 3,
                "title": "Año 4, Día 3: Vistas y Transacciones",
                "concept": "CREATE VIEW guarda una consulta compleja como una tabla virtual. Transacciones (BEGIN / COMMIT / ROLLBACK) garantizan atomicidad.",
                "syntax": "CREATE VIEW vista_alumnos AS SELECT ...;\nBEGIN TRANSACTION;\n-- cambios\nCOMMIT; -- o ROLLBACK si falla",
                "example": "CREATE VIEW ranking_informatica AS SELECT nombre, promedio FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                "tip": "En un banco, si se descuenta saldo de una cuenta y se cae el sistema antes de abonar a la otra, ROLLBACK revierte todo."
            },
            {
                "id": "y4_d4",
                "year": 4,
                "day": 4,
                "title": "Año 4, Día 4: Optimización de Consultas e Índices",
                "concept": "CREATE INDEX acelera búsquedas masivas evitando escaneos completos de tabla (Table Scans).",
                "syntax": "CREATE INDEX idx_carrera ON estudiantes (carrera);\nEXPLAIN QUERY PLAN SELECT ...;",
                "example": "EXPLAIN QUERY PLAN SELECT * FROM estudiantes WHERE carrera = 'Ingenieria Informatica';",
                "tip": "EXPLAIN QUERY PLAN te dice si SQLite usará un índice rápido (SEARCH) o recorrerá toda la tabla (SCAN)."
            }
        ]

    def open(self):
        self.active = True
        self.audio.play_key()

    def close(self):
        self.active = False

    def get_unlocked_notes(self):
        """Filtra las notas que el estudiante ya tiene desbloqueadas según su año y día cursado."""
        cur_year = self.save.data.get("current_year", 1)
        cur_day = self.save.data.get("current_day", 1)

        unlocked = []
        for n in self.all_notes:
            if n["year"] < cur_year:
                unlocked.append(n)
            elif n["year"] == cur_year and n["day"] <= cur_day:
                unlocked.append(n)
        return unlocked

    def handle_event(self, event):
        if not self.active:
            return False

        unlocked = self.get_unlocked_notes()
        total_pages = max(1, len(unlocked))

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_n, pygame.K_F1]:
                self.close()
                return True
            elif event.key in [pygame.K_RIGHT, pygame.K_d, pygame.K_PAGEDOWN]:
                if self.current_page < total_pages - 1:
                    self.current_page += 1
                    self.audio.play_chalk()
                return True
            elif event.key in [pygame.K_LEFT, pygame.K_a, pygame.K_PAGEUP]:
                if self.current_page > 0:
                    self.current_page -= 1
                    self.audio.play_chalk()
                return True

        return False

    def draw(self, surface):
        if not self.active:
            return

        unlocked = self.get_unlocked_notes()
        total_pages = len(unlocked)

        # Fondo oscuro atenuado
        dim = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 190))
        surface.blit(dim, (0, 0))

        # Cuaderno de espiral universitario (Ancho 420 x Alto 260)
        book_x = 30
        book_y = 20
        book_w = 420
        book_h = 260

        # Tapa de cuero azul marino
        pygame.draw.rect(surface, (25, 35, 55), (book_x - 4, book_y - 4, book_w + 8, book_h + 8), border_radius=4)
        # Hoja cuadriculada blanca crema
        pygame.draw.rect(surface, (245, 245, 240), (book_x, book_y, book_w, book_h))
        pygame.draw.rect(surface, (210, 210, 205), (book_x, book_y, book_w, book_h), 1)

        # Espiral a la izquierda
        for sy in range(book_y + 12, book_y + book_h - 10, 16):
            pygame.draw.circle(surface, (60, 70, 85), (book_x + 10, sy), 4)
            pygame.draw.circle(surface, (245, 245, 240), (book_x + 10, sy), 2)
            pygame.draw.line(surface, (140, 150, 165), (book_x + 2, sy), (book_x + 14, sy), 2)

        # Cuadrícula suave de la libreta
        for gy in range(book_y + 10, book_y + book_h, 15):
            pygame.draw.line(surface, (235, 235, 238), (book_x + 20, gy), (book_x + book_w - 6, gy), 1)

        # Margen rojo de libreta
        pygame.draw.line(surface, (230, 150, 150), (book_x + 32, book_y), (book_x + 32, book_y + book_h), 1)

        # Contenido
        content_x = book_x + 40
        content_w = book_w - 55

        if total_pages == 0:
            msg_rect = pygame.Rect(content_x, book_y + 50, content_w, 100)
            render_wrapped_text(surface, "Aún no has registrado apuntes. Asiste a tus clases con el Profesor Turing para desbloquear resúmenes.", msg_rect, self.font_subtitle, color=(80, 80, 90))
            return

        self.current_page = min(self.current_page, total_pages - 1)
        note = unlocked[self.current_page]

        # Encabezado de la página
        title_surf = self.font_title.render(note["title"], True, (30, 40, 60))
        surface.blit(title_surf, (content_x, book_y + 12))

        pname = self.save.data.get("player_name", "Estudiante")
        user_tag = self.font_hint.render(f"Apuntes de: {pname}  |  Año {note['year']}", True, (120, 130, 145))
        surface.blit(user_tag, (content_x, book_y + 28))

        # 1. Concepto
        c_label = self.font_label.render("CONCEPTO CLAVE:", True, (160, 60, 40))
        surface.blit(c_label, (content_x, book_y + 45))
        c_rect = pygame.Rect(content_x, book_y + 58, content_w, 35)
        render_wrapped_text(surface, note["concept"], c_rect, self.font_body, color=(40, 45, 55), line_spacing=2)

        # 2. Sintaxis
        s_label = self.font_label.render("SINTAXIS OFICIAL:", True, (40, 110, 160))
        surface.blit(s_label, (content_x, book_y + 96))
        s_box = pygame.Rect(content_x, book_y + 108, content_w, 38)
        pygame.draw.rect(surface, (230, 238, 245), s_box)
        pygame.draw.rect(surface, (160, 190, 220), s_box, 1)
        render_wrapped_text(surface, note["syntax"], s_box, self.font_code, color=(20, 50, 90), line_spacing=1, padding=4)

        # 3. Ejemplo Práctico
        e_label = self.font_label.render("EJEMPLO DE LABORATORIO:", True, (35, 130, 70))
        surface.blit(e_label, (content_x, book_y + 152))
        e_box = pygame.Rect(content_x, book_y + 164, content_w, 32)
        pygame.draw.rect(surface, (230, 245, 235), e_box)
        pygame.draw.rect(surface, (150, 210, 170), e_box, 1)
        render_wrapped_text(surface, note["example"], e_box, self.font_code, color=(15, 80, 40), line_spacing=1, padding=4)

        # 4. Consejo Senior
        tip_rect = pygame.Rect(content_x, book_y + 204, content_w, 35)
        render_wrapped_text(surface, f"💡 Consejo Senior: {note['tip']}", tip_rect, self.font_body, color=(110, 80, 30), line_spacing=2)

        # Número de Página y Navegación
        page_info = f"Página {self.current_page + 1} de {total_pages}   [◀ / ▶] Cambiar página   [ESC / N] Cerrar"
        p_surf = self.font_hint.render(page_info, True, (100, 110, 125))
        surface.blit(p_surf, (book_x + (book_w - p_surf.get_width()) // 2, book_y + book_h - 14))
