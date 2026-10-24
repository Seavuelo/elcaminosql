import pygame
from game.constants import *
from game.ui_helpers import render_wrapped_text, draw_panel

class LectureScene:
    """Escena interactiva de clase en la pizarra del Profesor Turing adaptada a los 4 años de carrera."""
    def __init__(self, audio_manager, save_system):
        self.audio = audio_manager
        self.save = save_system
        self.active = False
        self.year = 1
        self.day = 1
        self.slide_index = 0
        self.slides = []
        self.on_finish_callback = None

        self.font_title = pygame.font.Font(None, 15)
        self.font_body = pygame.font.Font(None, 13)
        self.font_code = pygame.font.Font(None, 13)
        self.font_chalk = pygame.font.Font(None, 12)
        self.font_code_label = pygame.font.Font(None, 10)
        self.font_page = pygame.font.Font(None, 11)

        # Animación de escritura progresiva en la pizarra y parpadeo de cátedra
        self.chalk_char_index = 0
        self.chalk_is_done = False
        self.tick_count = 0

    def start_lecture(self, year, day, attempts, on_finish):
        self.year = year
        self.day = day
        self.active = True
        self.slide_index = 0
        self.on_finish_callback = on_finish
        self.slides = self._build_slides(year, day, attempts)
        self.chalk_char_index = 0
        self.chalk_is_done = False
        self.tick_count = 0
        self.audio.play_chalk()

    def _build_slides(self, year, day, attempts):
        name = self.save.data.get("player_name", "Novato")
        role = self.save.data.get("title_role", "Alumno")
        pronoun = self.save.data.get("pronoun_welcome", "Bienvenido")

        intro_prefix = f"¡{pronoun} a clases, {name}!"
        if attempts > 1 and day == 1:
            intro_prefix = f"¡Vaya, {name}! Un gusto verte de nuevo por aquí... parece que le tomaste cariño al Año {year}. La constancia hace al verdadero ingeniero, ¡esta vez lo aprobamos sí o sí!"

        # === AÑO 1: Fundamentos y Lectura Básica ===
        if year == 1:
            if day == 1:
                return [
                    {
                        "title": f"Año 1, Día 1: Introducción a SQL y Proyecciones",
                        "turing": f"{intro_prefix} Hoy iniciamos tu carrera en Ingeniería Informática con el cimiento de todo: El Modelo Relacional y la sentencia SELECT.",
                        "chalk_title": "1. TABLAS, REGISTROS Y CAMPOS",
                        "chalk_body": "En SQL los datos se organizan en TABLAS bidimensionales:\n• FILAS (Tuplas): Cada registro único almacenado.\n• COLUMNAS (Atributos): Tipo de dato (nombre, carrera, promedio).\n• Termina siempre cada sentencia SQL con punto y coma (;).",
                        "code_example": "SELECT * FROM estudiantes;"
                    },
                    {
                        "title": "Año 1, Día 1: Seleccionando Múltiples Columnas",
                        "turing": "Para pedir varias columnas específicas a la vez, separamos sus nombres con una coma: 'columna1, columna2'. ¡Ojo! Antes de la palabra FROM nunca debe haber una coma.",
                        "chalk_title": "2. SELECCIÓN DE COLUMNAS CON COMAS",
                        "chalk_body": "• Todas las columnas: Usa el asterisco '*'\n  SELECT * FROM estudiantes;\n• Columnas específicas: Sepáralas con comas\n  SELECT nombre, carrera FROM estudiantes;\n• El orden en que las pides es el orden en que aparecerán.",
                        "code_example": "SELECT nombre, carrera FROM estudiantes;"
                    }
                ]
            elif day == 2:
                return [
                    {
                        "title": "Año 1, Día 2: Filtrando con la Cláusula WHERE",
                        "turing": f"¡Hola {name}! En sistemas reales no queremos ver millones de filas a la vez. Hoy aprenderemos a filtrar con la cláusula condicional WHERE.",
                        "chalk_title": "1. LA CLÁUSULA WHERE",
                        "chalk_body": "WHERE actúa como un colador condicional:\nSolo deja pasar las filas donde la condición sea VERDADERA.\nOperadores: =, !=, <, >, <=, >=, AND, OR\n• Números: WHERE nota < 4.0\n• Texto (entre comillas simples): WHERE carrera = 'Ingenieria Informatica'",
                        "code_example": "SELECT * FROM notas_parcial WHERE nota < 4.0;"
                    },
                    {
                        "title": "Año 1, Día 2: Columnas Específicas + Filtro WHERE",
                        "turing": "Recuerda: si el laboratorio te pide mostrar 'estudiante_nombre' y 'nota', debes solicitar ambas columnas separadas por comas en tu SELECT. Si omites una, tu entrega estará incompleta.",
                        "chalk_title": "2. COMBINANDO COLUMNAS Y WHERE",
                        "chalk_body": "Sintaxis estándar:\nSELECT columna1, columna2 FROM tabla WHERE condicion;\n\nEjemplo de alumnos en riesgo:\nSELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;",
                        "code_example": "SELECT estudiante_nombre, nota FROM notas_parcial WHERE nota < 4.0;"
                    }
                ]
            elif day == 3:
                return [
                    {
                        "title": "Año 1, Día 3: Ordenando con ORDER BY",
                        "turing": "Las bases de datos no garantizan ningún orden por defecto. Hoy aprenderemos a ordenar con ORDER BY.",
                        "chalk_title": "1. ORDEN ASCENDENTE Y DESCENDENTE",
                        "chalk_body": "• ASC: Menor a mayor / A a la Z (por defecto).\n• DESC: Mayor a menor / Z a la A (ideal para rankings de notas y mejores ventas).",
                        "code_example": "SELECT nombre, promedio FROM estudiantes ORDER BY promedio DESC;"
                    }
                ]
            elif day == 4:
                return [
                    {
                        "title": "Año 1, Día 4: Paginación con LIMIT",
                        "turing": f"Atención {name}. LIMIT restringe el número exacto de resultados. Es como se construyen los 'Top 3' o las páginas de Google.",
                        "chalk_title": "1. ORDEN SINTÁCTICO DE SQL",
                        "chalk_body": "1. SELECT  (qué)\n2. FROM    (de dónde)\n3. WHERE   (filtro)\n4. ORDER BY(orden)\n5. LIMIT   (cantidad)",
                        "code_example": "SELECT nombre, cupos FROM materias WHERE cupos > 0 ORDER BY cupos ASC LIMIT 3;"
                    }
                ]
            elif day == 5:
                return [
                    {
                        "title": "Año 1, Día 5: ¡VIERNES DE EXAMEN PARCIAL!",
                        "turing": f"¡Llegó el viernes decisivo, {name}! Tu primer Examen Parcial de 1er Año. Consta de 3 preguntas sin pistas. La nota mínima de aprobación es 4.0.",
                        "chalk_title": "EVALUACIÓN DE 1ER AÑO",
                        "chalk_body": "• Si apruebas (>= 4.0): Pasas oficialmente a 2do Año (Creación de Tablas).\n• Si repruebas (< 4.0): Repetirás 1er Año hasta dominarlo.\n¡Mucho éxito en tu computador!",
                        "code_example": "-- Examen Oficial de Álgebra Relacional I --"
                    }
                ]

        # === AÑO 2: DDL y DML (Creación, Inserción y Modificación) ===
        elif year == 2:
            if day == 1:
                return [
                    {
                        "title": f"Año 2, Día 1: Creación de Tablas (DDL)",
                        "turing": f"{intro_prefix} ¡Felicidades por llegar a 2do Año! Ya sabes leer datos; ahora aprenderás a CREAR estructuras con CREATE TABLE.",
                        "chalk_title": "1. DATA DEFINITION LANGUAGE (DDL)",
                        "chalk_body": "CREATE TABLE define el molde relacional.\nTipos en SQLite: INTEGER, TEXT, REAL (decimal), BLOB.\nPRIMARY KEY asegura que cada fila tenga un identificador único.",
                        "code_example": "CREATE TABLE proyectos (id INTEGER PRIMARY KEY, titulo TEXT, nota REAL);"
                    }
                ]
            elif day == 2:
                return [
                    {
                        "title": "Año 2, Día 2: Inserción de Datos (INSERT INTO)",
                        "turing": "Una tabla vacía no sirve de nada. Hoy aprenderemos a meterle información con INSERT INTO.",
                        "chalk_title": "1. SINTAXIS DE INSERCIÓN",
                        "chalk_body": "INSERT INTO nombre_tabla (col1, col2) VALUES (val1, val2);\nLos valores deben respetar el tipo de dato de cada columna.",
                        "code_example": "INSERT INTO proyectos (id, titulo, nota) VALUES (1, 'Motor SQL 2D', 6.8);"
                    }
                ]
            elif day == 3:
                return [
                    {
                        "title": "Año 2, Día 3: Modificación con UPDATE",
                        "turing": f"Cuidado aquí, {name}: En una empresa real, jamás ejecutes un UPDATE sin WHERE o alterarás toda la base de datos.",
                        "chalk_title": "1. LA SENTENCIA UPDATE",
                        "chalk_body": "UPDATE tabla SET columna = nuevo_valor WHERE condicion;\nModifica exclusivamente las filas que cumplan la condición.",
                        "code_example": "UPDATE estudiantes SET estado = 'Graduado' WHERE promedio >= 6.8;"
                    }
                ]
            elif day == 4:
                return [
                    {
                        "title": "Año 2, Día 4: Depuración con DELETE",
                        "turing": "Hoy aprenderemos a eliminar registros obsoletos con DELETE FROM. Al igual que con UPDATE, el WHERE es tu seguro de vida.",
                        "chalk_title": "1. ELIMINACIÓN DE REGISTROS",
                        "chalk_body": "DELETE FROM tabla WHERE condicion;\nBorra físicamente las filas que cumplan el criterio.",
                        "code_example": "DELETE FROM materias WHERE cupos = 0;"
                    }
                ]
            elif day == 5:
                return [
                    {
                        "title": "Año 2, Día 5: Examen de 2do Año",
                        "turing": f"¡Viernes de Examen de 2do Año, {name}! Evaluaremos CREATE TABLE, INSERT y UPDATE. Nota mínima: 4.0 para avanzar a 3er Año.",
                        "chalk_title": "EXAMEN DE DDL & DML",
                        "chalk_body": "Demuestra que puedes modelar y manipular datos de forma segura.\n¡A tu estación de trabajo!",
                        "code_example": "-- Examen de Estructuras y Manipulación II --"
                    }
                ]

        # === AÑO 3: Agregaciones y Relaciones Multitabla ===
        elif year == 3:
            if day == 1:
                return [
                    {
                        "title": f"Año 3, Día 1: Funciones de Agregación",
                        "turing": f"{intro_prefix} ¡Bienvenido a 3er Año! Hoy comenzamos con la analítica: resumir miles de filas en números clave con COUNT, AVG, SUM, MAX, MIN.",
                        "chalk_title": "1. FUNCIONES AGREGADAS",
                        "chalk_body": "• COUNT(*): Cuenta cantidad de filas.\n• AVG(columna): Promedio aritmético.\n• SUM(columna): Suma acumulada.\n• MAX/MIN: Valores extremos.",
                        "code_example": "SELECT COUNT(*), AVG(promedio) FROM estudiantes;"
                    }
                ]
            elif day == 2:
                return [
                    {
                        "title": "Año 3, Día 2: Agrupando con GROUP BY",
                        "turing": "GROUP BY permite separar datos en categorías (por ejemplo, ver estadísticas separadas por cada carrera).",
                        "chalk_title": "1. LA CLÁUSULA GROUP BY",
                        "chalk_body": "Colapsa filas idénticas y aplica las agregaciones a cada grupo.\nSELECT carrera, COUNT(*) FROM estudiantes GROUP BY carrera;",
                        "code_example": "SELECT carrera, COUNT(*), AVG(promedio) FROM estudiantes GROUP BY carrera;"
                    }
                ]
            elif day == 3:
                return [
                    {
                        "title": "Año 3, Día 3: Filtrando Grupos con HAVING",
                        "turing": f"Muchos juniors se confunden entre WHERE y HAVING. Grábate esto, {name}: WHERE filtra filas antes de agrupar; HAVING filtra grupos ya calculados.",
                        "chalk_title": "1. WHERE VS HAVING",
                        "chalk_body": "• WHERE nota >= 4.0 (Filtra alumnos individuales)\n• HAVING AVG(promedio) >= 5.0 (Filtra carreras completas)",
                        "code_example": "SELECT carrera, AVG(promedio) FROM estudiantes GROUP BY carrera HAVING AVG(promedio) >= 5.0;"
                    }
                ]
            elif day == 4:
                return [
                    {
                        "title": "Año 3, Día 4: El Sagrado INNER JOIN",
                        "turing": "La razón de ser de las bases de datos relacionales: Cruzar dos tablas distintas mediante una llave foránea compartida.",
                        "chalk_title": "1. UNIÓN DE TABLAS (INNER JOIN)",
                        "chalk_body": "Combina filas cuando la llave coincide en ambas tablas:\nFROM estudiantes e\nINNER JOIN notas_parcial n ON e.id = n.estudiante_id",
                        "code_example": "SELECT e.nombre, n.nota FROM estudiantes e INNER JOIN notas_parcial n ON e.id = n.estudiante_id;"
                    }
                ]
            elif day == 5:
                return [
                    {
                        "title": "Año 3, Día 5: Examen de 3er Año",
                        "turing": f"¡Examen de 3er Año, {name}! Hoy pondrás a prueba agregaciones, GROUP BY e INNER JOIN. Si apruebas, entrarás a tu último año de carrera.",
                        "chalk_title": "EXAMEN DE ANALÍTICA & JOINS",
                        "chalk_body": "Pasa con nota >= 4.0 para habilitar tu Proyecto de Título en 4to Año.\n¡Mucho éxito!",
                        "code_example": "-- Examen Avanzado de Relaciones III --"
                    }
                ]

        # === AÑO 4: Subconsultas, Optimización y Proyecto de Título ===
        elif year == 4:
            if day == 1:
                return [
                    {
                        "title": f"Año 4, Día 1: Subconsultas con IN",
                        "turing": f"{intro_prefix} ¡Tu último año académico! Hoy entramos a arquitectura avanzada: Subconsultas anidadas.",
                        "chalk_title": "1. SUBCONSULTAS (SUBQUERIES)",
                        "chalk_body": "Un SELECT dentro de otro SELECT:\nWHERE id IN (SELECT estudiante_id FROM notas_parcial WHERE nota = 7.0)\nLa consulta interna calcula el conjunto dinámicamente.",
                        "code_example": "SELECT nombre FROM estudiantes WHERE id IN (SELECT estudiante_id FROM notas_parcial WHERE nota = 7.0);"
                    }
                ]
            elif day == 2:
                return [
                    {
                        "title": "Año 4, Día 2: Auditoría con LEFT JOIN",
                        "turing": "INNER JOIN solo muestra coincidencias. Pero para auditorías (por ejemplo, buscar alumnos sin ninguna nota registrada) usamos LEFT JOIN.",
                        "chalk_title": "1. LEFT OUTER JOIN",
                        "chalk_body": "Trae TODOS los registros de la tabla izquierda.\nSi en la derecha no hay datos, los rellena con NULL.",
                        "code_example": "SELECT e.nombre, n.nota FROM estudiantes e LEFT JOIN notas_parcial n ON e.id = n.estudiante_id;"
                    }
                ]
            elif day == 3:
                return [
                    {
                        "title": "Año 4, Día 3: Vistas y Transacciones",
                        "turing": "Una VISTA (CREATE VIEW) es una consulta guardada como tabla virtual. Y las transacciones aseguran que el dinero o datos no se pierdan a mitad de camino.",
                        "chalk_title": "1. VISTAS Y TRANSACCIONES",
                        "chalk_body": "• Vistas: CREATE VIEW nombre_vista AS SELECT ...\n• Transacciones: BEGIN TRANSACTION -> Modificaciones -> COMMIT o ROLLBACK si algo falla.",
                        "code_example": "CREATE VIEW IF NOT EXISTS vista_honor AS SELECT nombre, promedio FROM estudiantes WHERE promedio >= 6.0;"
                    }
                ]
            elif day == 4:
                return [
                    {
                        "title": "Año 4, Día 4: Optimización e Índices",
                        "turing": f"El toque Senior, {name}: En bases con millones de filas, un SELECT sin índice puede tardar minutos. Con CREATE INDEX se resuelve en milisegundos.",
                        "chalk_title": "1. ÍNDICES Y EXPLAIN",
                        "chalk_body": "• CREATE INDEX idx_nombre ON tabla (columna);\n• EXPLAIN QUERY PLAN te muestra si el motor de base de datos hace una búsqueda rápida o recorre todo el disco.",
                        "code_example": "CREATE INDEX IF NOT EXISTS idx_carrera ON estudiantes (carrera);"
                    }
                ]
            elif day == 5:
                return [
                    {
                        "title": "Año 4, Día 5: ¡EL EXAMEN DE GRADO OFICIAL!",
                        "turing": f"¡El día más importante de tu vida universitaria, {name}! Hoy defiendes tu Examen de Grado. 3 desafíos complejos que integran toda tu carrera. Si apruebas con 4.0 o más, ¡te otorgaré tu TÍTULO OFICIAL DE INGENIERO DE SOFTWARE!",
                        "chalk_title": "DEFENSA DE TÍTULO DE GRADO",
                        "chalk_body": "• Pregunta 1: Subconsultas dinámicas.\n• Pregunta 2: Agrupación analítica multitabla con JOIN.\n• Pregunta 3: Optimización y ranking de excelencia.\n¡A defender tu título profesional!",
                        "code_example": "-- EXAMEN FINAL DE GRADO DE INGENIERÍA --"
                    }
                ]

        return []

    def handle_event(self, event):
        if not self.active:
            return False

        cur_slide = self.slides[self.slide_index] if self.slides else None
        total_chalk = len(cur_slide["chalk_body"]) + len(cur_slide.get("code_example", "")) if cur_slide else 0

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT]:
                if not self.chalk_is_done:
                    # Primer toque: Completa la pizarra de inmediato
                    self.chalk_char_index = total_chalk
                    self.chalk_is_done = True
                    return True
                else:
                    # Segundo toque: Avanza a la siguiente diapositiva
                    self.slide_index += 1
                    self.chalk_char_index = 0
                    self.chalk_is_done = False
                    self.audio.play_chalk()
                    if self.slide_index >= len(self.slides):
                        self.active = False
                        if self.on_finish_callback:
                            self.on_finish_callback()
                    return True
            elif event.key == pygame.K_LEFT and self.slide_index > 0:
                self.slide_index -= 1
                self.chalk_char_index = 0
                self.chalk_is_done = False
                self.audio.play_chalk()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                if self.on_finish_callback:
                    self.on_finish_callback()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.chalk_is_done:
                self.chalk_char_index = total_chalk
                self.chalk_is_done = True
                return True
            else:
                self.slide_index += 1
                self.chalk_char_index = 0
                self.chalk_is_done = False
                self.audio.play_chalk()
                if self.slide_index >= len(self.slides):
                    self.active = False
                    if self.on_finish_callback:
                        self.on_finish_callback()
                return True
        return False

    def draw(self, surface):
        if not self.active or not self.slides:
            return

        self.tick_count += 1
        cur_slide = self.slides[self.slide_index]
        surface.fill((16, 22, 32))

        # 1. Pizarra de Clase
        board_rect = pygame.Rect(12, 8, 456, 192)
        pygame.draw.rect(surface, (100, 70, 50), board_rect)
        
        board_bg = (45, 20, 25) if self.day == 5 else (20, 50, 36)
        pygame.draw.rect(surface, board_bg, (16, 12, 448, 184))

        # Título de tiza
        c_title_surf = self.font_title.render(cur_slide["chalk_title"], True, COLOR_AMBER)
        surface.blit(c_title_surf, (28, 20))

        # Escritura progresiva en la pizarra (efecto tiza en vivo)
        chalk_body = cur_slide["chalk_body"]
        code_text = cur_slide.get("code_example", "")
        total_chalk = len(chalk_body) + len(code_text)

        if not self.chalk_is_done:
            self.chalk_char_index += 2
            if self.chalk_char_index >= total_chalk:
                self.chalk_char_index = total_chalk
                self.chalk_is_done = True
            elif self.chalk_char_index % 24 in [0, 1]:
                self.audio.play_chalk()

        body_chars = min(self.chalk_char_index, len(chalk_body))
        shown_body = chalk_body[:body_chars]
        if not self.chalk_is_done and body_chars < len(chalk_body) and (self.tick_count // 12) % 2 == 0:
            shown_body += " ▌"

        body_rect = pygame.Rect(28, 42, 424, 102)
        render_wrapped_text(surface, shown_body, body_rect, self.font_chalk, color=(220, 245, 225), line_spacing=3, padding=0)

        # Caja de Código en Pizarra
        code_box = pygame.Rect(28, 148, 424, 34)
        pygame.draw.rect(surface, (12, 35, 24), code_box)
        pygame.draw.rect(surface, (60, 160, 100), code_box, 1)
        code_label = self.font_code_label.render("SINTAXIS SQL RECOMENDADA:", True, (100, 200, 140))
        surface.blit(code_label, (34, 150))

        if self.chalk_char_index > len(chalk_body):
            code_chars = self.chalk_char_index - len(chalk_body)
            shown_code = code_text[:code_chars]
            if not self.chalk_is_done and (self.tick_count // 12) % 2 == 0:
                shown_code += "▌"
            code_surf = self.font_code.render(shown_code[:62], True, (255, 240, 150))
            surface.blit(code_surf, (34, 162))

        # 2. Caja de Diálogo del Profesor Turing abajo (Texto listo altiro con parpadeo)
        diag_rect = pygame.Rect(12, 204, 456, 88)
        
        # Parpadeo sutil en el estado de Turing
        is_blink = (self.tick_count // 18) % 2 == 0
        state_tag = " [● Explicando]" if (not self.chalk_is_done and is_blink) else " [✓ Cátedra]"
        turing_title = f"PROFESOR TURING{state_tag}  |  {cur_slide['title']}"

        draw_panel(surface, diag_rect, bg_color=(14, 18, 28, 248), border_color=(0, 229, 255), border_width=1,
                   title=turing_title, font=self.font_title, title_color=COLOR_AMBER)

        # Avatar de Turing
        avatar_x = 18
        avatar_y = 228
        pygame.draw.rect(surface, (25, 35, 50), (avatar_x, avatar_y, 40, 52))
        pygame.draw.rect(surface, COLOR_AMBER, (avatar_x, avatar_y, 40, 52), 1)
        pygame.draw.rect(surface, (220, 220, 225), (avatar_x + 8, avatar_y + 4, 24, 12))
        pygame.draw.rect(surface, (255, 205, 148), (avatar_x + 10, avatar_y + 12, 20, 18))
        pygame.draw.circle(surface, (20, 25, 35), (avatar_x + 15, avatar_y + 18), 3, 1)
        pygame.draw.circle(surface, (20, 25, 35), (avatar_x + 27, avatar_y + 18), 3, 1)
        pygame.draw.rect(surface, (65, 85, 60), (avatar_x + 5, avatar_y + 32, 30, 18))

        # Texto del profesor (visible inmediatamente, con tamaño compacto legible)
        t_box = pygame.Rect(66, 228, 394, 52)
        render_wrapped_text(surface, cur_slide["turing"], t_box, self.font_body, color=COLOR_WHITE, line_spacing=2, padding=0)

        # Indicador de navegación
        if not self.chalk_is_done:
            page_txt = f"[{self.slide_index + 1}/{len(self.slides)}] Tiza escribiendo... Pulsa [ESPACIO] para completar pizarra ▼"
            page_surf = self.font_page.render(page_txt, True, (255, 200, 100))
        else:
            page_txt = f"[{self.slide_index + 1}/{len(self.slides)}] Pulsa [ESPACIO] o [ENTER] para avanzar ▶"
            page_surf = self.font_page.render(page_txt, True, COLOR_CYAN)
        surface.blit(page_surf, (diag_rect.x + diag_rect.width - page_surf.get_width() - 8, diag_rect.y + diag_rect.height - 13))
