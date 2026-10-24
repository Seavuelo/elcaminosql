import pygame
import math
from game.constants import *
from game.ui_helpers import render_wrapped_text, draw_panel

class IntroPrologue:
    """Prólogo cinemático con ilustraciones dinámicas en pixel art e introducción a Ingeniería Informática."""
    def __init__(self, audio_manager, on_finish_callback):
        self.audio = audio_manager
        self.on_finish = on_finish_callback
        self.active = False
        self.slide_idx = 0

        self.font_title = pygame.font.Font(None, 20)
        self.font_text = pygame.font.Font(None, 16)
        self.font_hint = pygame.font.Font(None, 13)
        self.font_pixel = pygame.font.Font(None, 14)

        # Pre-renderizar el degradado de fondo
        self.bg_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        for y in range(VIRTUAL_HEIGHT):
            ratio = y / VIRTUAL_HEIGHT
            r = int(10 * (1 - ratio) + 24 * ratio)
            g = int(14 * (1 - ratio) + 32 * ratio)
            b = int(26 * (1 - ratio) + 52 * ratio)
            pygame.draw.line(self.bg_surface, (r, g, b), (0, y), (VIRTUAL_WIDTH, y))

        self.slides = [
            {
                "title": "CAPÍTULO 0: LA CARTA DE ADMISIÓN",
                "text": "Año 2026. Tras meses de arduo estudio y preparación, recibes la esperada carta con sello dorado del Instituto Tecnológico Universitario:\n\n'Nos complace informarle que ha sido admitido formalmente en la Carrera de Ingeniería Informática'."
            },
            {
                "title": "EL SUEÑO DEL DESARROLLADOR",
                "text": "Tu vocación es clara: completar los 4 años de carrera universitaria, dominar el arte de las bases de datos relacionales y el lenguaje SQL desde cero, para algún día liderar proyectos de software en las mayores empresas tecnológicas del mundo."
            },
            {
                "title": "LA EXIGENCIA ACADÉMICA",
                "text": "Pero en esta facultad el rigor es absoluto. Para avanzar de año, deberás asistir a las clases en pizarra del Dr. Alan Turing, resolver los laboratorios diarios y aprobar los rigurosos Exámenes de los Viernes con nota mínima de 4.0.\n\nSi repruebas un año, deberás repetirlo hasta dominarlo por completo."
            },
            {
                "title": "PRIMER DÍA DE CLASES",
                "text": "Las puertas de la Facultad de Ingeniería Informática se abren ante ti.\n\nEs momento de completar tu ficha de matrícula y personalizar tu carnet de estudiante antes de tomar asiento en el laboratorio..."
            }
        ]

    def start(self):
        self.active = True
        self.slide_idx = 0
        self.audio.play_key()

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT]:
                self.slide_idx += 1
                self.audio.play_chalk()
                if self.slide_idx >= len(self.slides):
                    self.active = False
                    self.on_finish()
                return True
            elif event.key == pygame.K_ESCAPE:
                self.active = False
                self.on_finish()
                return True
        return False

    def draw(self, surface, tick):
        if not self.active:
            return

        # 1. Fondo base degradado pre-renderizado
        surface.blit(self.bg_surface, (0, 0))

        # 2. Escena visual ilustrada en la mitad superior (y=0 a 175) según la diapositiva
        if self.slide_idx == 0:
            self._draw_scene_admission_letter(surface, tick)
        elif self.slide_idx == 1:
            self._draw_scene_developer_desk(surface, tick)
        elif self.slide_idx == 2:
            self._draw_scene_turing_blackboard(surface, tick)
        else:
            self._draw_scene_campus_gate(surface, tick)

        # 3. Piso y línea de división
        pygame.draw.rect(surface, (12, 16, 24), (0, 175, VIRTUAL_WIDTH, 125))
        pygame.draw.line(surface, (0, 229, 255), (0, 175), (VIRTUAL_WIDTH, 175), 1)

        # 4. Cuadro de Narración Central
        box_w = 430
        box_h = 106
        box_x = (VIRTUAL_WIDTH - box_w) // 2
        box_y = 180

        cur_slide = self.slides[self.slide_idx]
        card_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        draw_panel(surface, card_rect, bg_color=(12, 18, 28, 240), border_color=COLOR_CYAN, border_width=1,
                   title=cur_slide["title"], font=self.font_title, title_color=COLOR_AMBER)

        # Texto de la diapositiva con Word-Wrap riguroso
        text_rect = pygame.Rect(box_x + 12, box_y + 26, box_w - 24, box_h - 40)
        render_wrapped_text(surface, cur_slide["text"], text_rect, self.font_text, color=COLOR_WHITE, line_spacing=3, padding=0)

        # Indicador de avance
        prog_txt = f"[{self.slide_idx + 1}/{len(self.slides)}] Pulsa [ESPACIO] o [ENTER] para continuar ▶"
        p_surf = self.font_hint.render(prog_txt, True, (0, 229, 255))
        surface.blit(p_surf, (box_x + box_w - p_surf.get_width() - 10, box_y + box_h - 14))

    # --- ILUSTRACIONES PIXEL ART PARA CADA ESCENA ---

    def _draw_scene_admission_letter(self, surface, tick):
        """Escena 1: La carta de admisión formal con membrete y sello de lacre dorado."""
        # Estrellas de fondo
        for sx, sy in [(60, 25), (140, 15), (340, 20), (420, 35), (240, 10)]:
            tw = int(180 + 70 * math.sin(tick * 0.1 + sx))
            pygame.draw.rect(surface, (tw, tw, 255), (sx, sy, 2, 2))

        # Mesa de madera noble
        pygame.draw.rect(surface, (45, 30, 20), (80, 140, 320, 35))
        pygame.draw.line(surface, (70, 50, 35), (80, 140), (400, 140), 2)

        # Sobre de pergamino
        lx, ly, lw, lh = 175, 40, 130, 95
        pygame.draw.rect(surface, (235, 220, 185), (lx, ly, lw, lh))
        pygame.draw.rect(surface, (180, 160, 125), (lx, ly, lw, lh), 2)
        
        # Pliegues del sobre
        pygame.draw.polygon(surface, (215, 200, 165), [(lx, ly), (lx + lw // 2, ly + 50), (lx + lw, ly)])
        pygame.draw.polygon(surface, (195, 180, 145), [(lx, ly), (lx + lw // 2, ly + 50), (lx + lw, ly)], 1)

        # Sello de lacre dorado brillante
        seal_pulse = int(180 + 40 * math.sin(tick * 0.15))
        seal_x, seal_y = lx + lw // 2, ly + 50
        pygame.draw.circle(surface, (210, 150, 20), (seal_x, seal_y), 16)
        pygame.draw.circle(surface, (255, seal_pulse, 50), (seal_x, seal_y), 13)
        seal_txt = self.font_pixel.render("IT", True, (80, 50, 10))
        surface.blit(seal_txt, (seal_x - 5, seal_y - 5))

        # Cinta carmesí colgante
        pygame.draw.polygon(surface, (160, 30, 30), [(seal_x - 6, seal_y + 10), (seal_x - 12, seal_y + 32), (seal_x, seal_y + 24)])
        pygame.draw.polygon(surface, (190, 40, 40), [(seal_x + 6, seal_y + 10), (seal_x + 12, seal_y + 32), (seal_x, seal_y + 24)])

        # Tintero y pluma de caligrafía
        pygame.draw.rect(surface, (30, 35, 45), (130, 120, 22, 20))
        pygame.draw.rect(surface, (50, 60, 80), (133, 115, 16, 5))
        # Pluma blanca inclinada
        pygame.draw.line(surface, (240, 240, 245), (142, 115), (120, 60), 3)
        pygame.draw.line(surface, (200, 200, 210), (120, 60), (115, 50), 2)

        # Etiqueta institucional
        cert_txt = self.font_pixel.render("ADMISIÓN FORMAL 2026", True, (0, 229, 255))
        surface.blit(cert_txt, (180, 20))

    def _draw_scene_developer_desk(self, surface, tick):
        """Escena 2: El escritorio nocturno de un futuro programador con monitor retro CRT."""
        # Monitor CRT de tubo
        mx, my, mw, mh = 170, 30, 140, 100
        pygame.draw.rect(surface, (50, 55, 65), (mx, my, mw, mh))
        pygame.draw.rect(surface, (35, 40, 50), (mx + 2, my + 2, mw - 4, mh - 4), 2)
        # Pantalla fósforo verde
        scr_x, scr_y, scr_w, scr_h = mx + 10, my + 10, mw - 20, mh - 26
        pygame.draw.rect(surface, (10, 32, 16), (scr_x, scr_y, scr_w, scr_h))
        pygame.draw.rect(surface, (20, 70, 35), (scr_x, scr_y, scr_w, scr_h), 1)

        # Líneas de código SQL simuladas en pantalla
        code_lines = [
            ("sql> SELECT * FROM futuro;", (0, 255, 136)),
            ("[OK] 1 fila encontrada.", (160, 240, 180)),
            ("carrera: Informatica", (240, 240, 240)),
            ("nivel: Senior Dev", (255, 215, 0))
        ]
        for idx, (c_txt, col) in enumerate(code_lines):
            t_surf = self.font_hint.render(c_txt, True, col)
            surface.blit(t_surf, (scr_x + 6, scr_y + 6 + (idx * 14)))

        # Cursor parpadeante
        if (tick // 25) % 2 == 0:
            pygame.draw.rect(surface, (0, 255, 136), (scr_x + 6, scr_y + 64, 6, 8))

        # Base del monitor
        pygame.draw.rect(surface, (45, 50, 60), (mx + 55, my + mh, 30, 12))
        pygame.draw.rect(surface, (40, 45, 55), (mx + 45, my + mh + 10, 50, 5))

        # Teclado en la mesa
        pygame.draw.rect(surface, (45, 50, 60), (160, 150, 120, 18))
        for kx in range(165, 275, 8):
            pygame.draw.rect(surface, (70, 75, 85), (kx, 153, 6, 10))

        # Taza de café con vapor animado
        cx, cy = 320, 142
        pygame.draw.rect(surface, (200, 70, 60), (cx, cy, 18, 18))
        pygame.draw.rect(surface, (200, 70, 60), (cx + 18, cy + 4, 5, 10), 2)
        # Humo ondulante
        s_y = int(math.sin(tick * 0.15) * 3)
        pygame.draw.line(surface, (180, 180, 190), (cx + 6, cy - 3 + s_y), (cx + 9, cy - 12 + s_y), 1)
        pygame.draw.line(surface, (180, 180, 190), (cx + 12, cy - 3 - s_y), (cx + 15, cy - 12 - s_y), 1)

        # Libros apilados
        pygame.draw.rect(surface, (30, 80, 160), (100, 144, 45, 8))
        pygame.draw.rect(surface, (180, 140, 30), (102, 136, 42, 8))
        pygame.draw.rect(surface, (160, 40, 40), (105, 128, 38, 8))
        book_txt = self.font_pixel.render("SQL ANSI", True, COLOR_WHITE)
        surface.blit(book_txt, (103, 114))

    def _draw_scene_turing_blackboard(self, surface, tick):
        """Escena 3: Aula magistral con el Profesor Turing explicando Álgebra Relacional."""
        # Pizarra verde central
        bx, by, bw, bh = 100, 18, 280, 125
        pygame.draw.rect(surface, COLOR_BOARD_FRAME, (bx, by, bw, bh))
        pygame.draw.rect(surface, COLOR_BOARD, (bx + 3, by + 3, bw - 6, bh - 6))

        # Diagrama de Venn de INNER JOIN en tiza blanca y amarilla
        cx1, cy1 = 200, 65
        cx2, cy2 = 235, 65
        pygame.draw.circle(surface, (220, 220, 220), (cx1, cy1), 22, 1)
        pygame.draw.circle(surface, (220, 220, 220), (cx2, cy2), 22, 1)
        # Intersección iluminada
        pygame.draw.ellipse(surface, COLOR_AMBER, (212, 52, 12, 26))

        # Fórmulas y textos en tiza
        t1 = self.font_hint.render("A ⋈ B (INNER JOIN)", True, COLOR_CHALK_TEXT)
        t2 = self.font_hint.render("Aprobación: Nota >= 4.0", True, (160, 240, 180))
        t3 = self.font_hint.render("Reprobación: Nota < 4.0 (Repite año)", True, (255, 140, 140))
        surface.blit(t1, (160, 95))
        surface.blit(t2, (255, 35))
        surface.blit(t3, (255, 50))

        # Profesor Alan Turing dibujado de cuerpo presente en pixel art
        px, py = 50, 60
        # Pelo canoso
        pygame.draw.rect(surface, (220, 220, 225), (px + 6, py - 4, 18, 10))
        # Cabeza y rostro
        pygame.draw.rect(surface, (255, 205, 148), (px + 8, py + 4, 14, 12))
        # Ojos y gafas
        pygame.draw.rect(surface, (20, 20, 20), (px + 10, py + 8, 3, 3))
        pygame.draw.rect(surface, (20, 20, 20), (px + 16, py + 8, 3, 3))
        pygame.draw.line(surface, COLOR_AMBER, (px + 9, py + 9), (px + 19, py + 9), 1) # Montura de gafas
        # Chaqueta de tweed verde
        pygame.draw.rect(surface, (65, 85, 60), (px + 4, py + 16, 22, 28))
        pygame.draw.rect(surface, (240, 240, 245), (px + 12, py + 16, 6, 12)) # Camisa y corbata
        pygame.draw.rect(surface, (160, 40, 40), (px + 14, py + 18, 2, 8))
        # Pantalón café
        pygame.draw.rect(surface, (80, 60, 45), (px + 7, py + 44, 7, 26))
        pygame.draw.rect(surface, (80, 60, 45), (px + 16, py + 44, 7, 26))
        # Brazo señalando a la pizarra con tiza blanca
        pygame.draw.line(surface, (65, 85, 60), (px + 24, py + 22), (px + 52, py + 10), 3)
        pygame.draw.circle(surface, (255, 255, 255), (px + 53, py + 9), 2)

    def _draw_scene_campus_gate(self, surface, tick):
        """Escena 4: El pórtico monumental de entrada a la Facultad de Ingeniería Informática."""
        # Cielo crepuscular con luna
        pygame.draw.circle(surface, (255, 245, 200), (410, 30), 16)
        pygame.draw.circle(surface, (18, 25, 45), (416, 28), 14)

        # Edificio de la Facultad
        pygame.draw.rect(surface, (28, 38, 56), (100, 30, 280, 145))
        # Columnas monumentales
        for col_x in [120, 170, 300, 350]:
            pygame.draw.rect(surface, (45, 58, 82), (col_x, 40, 16, 135))
            pygame.draw.rect(surface, (60, 78, 108), (col_x - 3, 38, 22, 5)) # Capitel
            pygame.draw.rect(surface, (60, 78, 108), (col_x - 3, 170, 22, 5)) # Base

        # Puerta principal de doble hoja con luz interior cálida
        pygame.draw.rect(surface, (255, 210, 100), (210, 95, 60, 80))
        pygame.draw.rect(surface, (70, 50, 35), (210, 95, 60, 80), 2)
        pygame.draw.line(surface, (70, 50, 35), (240, 95), (240, 175), 2)

        # Gran letrero institucional sobre las columnas
        pygame.draw.rect(surface, (18, 24, 38), (100, 24, 280, 18))
        pygame.draw.rect(surface, COLOR_AMBER, (100, 24, 280, 18), 1)
        banner_txt = self.font_pixel.render("FACULTAD DE INGENIERÍA INFORMÁTICA", True, COLOR_AMBER)
        surface.blit(banner_txt, (125, 27))

        # Farolas con luz cálida titilante
        for lx in [60, 420]:
            pygame.draw.rect(surface, (50, 55, 65), (lx, 80, 4, 95))
            pulse = int(180 + 35 * math.sin(tick * 0.12 + lx))
            pygame.draw.circle(surface, (255, pulse, 80), (lx + 2, 76), 8)
            pygame.draw.rect(surface, (20, 20, 25), (lx - 2, 70, 8, 4))

        # Silueta del estudiante caminando hacia la entrada
        st_x, st_y = 230, 140
        pygame.draw.rect(surface, (15, 20, 30), (st_x + 5, st_y, 8, 8)) # Cabeza
        pygame.draw.rect(surface, (25, 35, 50), (st_x + 3, st_y + 8, 12, 14)) # Chaqueta/Mochila
        pygame.draw.rect(surface, (15, 20, 30), (st_x + 4, st_y + 22, 4, 12)) # Piernas
        pygame.draw.rect(surface, (15, 20, 30), (st_x + 10, st_y + 22, 4, 12))
