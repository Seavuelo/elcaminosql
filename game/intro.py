import pygame
from game.rendering import draw, make_font
import math
from game.constants import *
from game.ui_helpers import render_wrapped_text, draw_panel, draw_fitted_text
from game.visuals import centered, advance_indicator, marco_sprite

class IntroPrologue:
    """Prólogo cinemático con ilustraciones dinámicas en pixel art e introducción a Ingeniería Informática."""
    def __init__(self, audio_manager, on_finish_callback):
        self.audio = audio_manager
        self.on_finish = on_finish_callback
        self.active = False
        self.slide_idx = 0

        self.font_title = make_font(20)
        self.font_text = make_font(16)
        self.font_hint = make_font(13)
        self.font_pixel = make_font(14)

        # Pre-renderizar el degradado de fondo
        self.bg_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        for y in range(VIRTUAL_HEIGHT):
            ratio = y / VIRTUAL_HEIGHT
            r = int(10 * (1 - ratio) + 24 * ratio)
            g = int(14 * (1 - ratio) + 32 * ratio)
            b = int(26 * (1 - ratio) + 52 * ratio)
            draw.line(self.bg_surface, (r, g, b), (0, y), (VIRTUAL_WIDTH, y))

        self.slides = [
            {
                "title": "CAPÍTULO 0: LA CARTA DE ADMISIÓN",
                "text": "Tras meses de arduo estudio y preparación, recibes la esperada carta con sello dorado de la universidad de tus sueños:\n\n\"Nos complace informarle que ha sido admitido formalmente en la carrera\""
            },
            {
                "title": "EL SUEÑO DEL DESARROLLADOR",
                "text": "Tu vocación es clara, completar los cuatro años de carrera y aprender a trabajar con bases de datos relacionales y SQL desde cero\n\nCada clase será un paso para resolver problemas con datos y acercarte al mundo laboral"
            },
            {
                "title": "LA EXIGENCIA ACADÉMICA",
                "text": "En esta facultad el rigor es absoluto, para poder avanzar de año deberás asistir a las clases del profesor Marco, resolver los laboratorios y aprobar los exámenes de los viernes con nota mínima de 4.0.\n\nSi repruebas, repetirás ese año para reforzar lo aprendido."
            },
            {
                "title": "PRIMER DÍA DE CLASES",
                "text": "Las puertas de la Facultad de Ingeniería Informática se abren ante ti\n\nEs momento de completar tu ficha de matrícula y personalizar tu carnet de estudiante antes de tomar asiento en el laboratorio..."
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
        draw.rect(surface, (12, 16, 24), (0, 175, VIRTUAL_WIDTH, 125))
        draw.line(surface, (0, 229, 255), (0, 175), (VIRTUAL_WIDTH, 175), 1)

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
        draw_fitted_text(surface,cur_slide["text"],text_rect,self.font_text,COLOR_WHITE,padding=0)

        # Indicador de avance
        prog_txt = f"{self.slide_idx+1:02} / {len(self.slides):02}"
        p_surf = self.font_hint.render(prog_txt, True, (0, 229, 255))
        surface.blit(p_surf,(box_x+box_w-p_surf.get_width()-28,box_y+box_h-14))
        advance_indicator(surface,(box_x+box_w-14,box_y+box_h-9),tick,self.slide_idx==len(self.slides)-1)

    # --- ILUSTRACIONES PIXEL ART PARA CADA ESCENA ---

    def _draw_scene_admission_letter(self, surface, tick):
        """Escena 1: La carta de admisión formal con membrete y sello de lacre dorado."""
        # Estrellas de fondo
        for sx, sy in [(60, 25), (140, 15), (340, 20), (420, 35), (240, 10)]:
            tw = int(180 + 70 * math.sin(tick * 0.1 + sx))
            draw.rect(surface, (tw, tw, 255), (sx, sy, 2, 2))

        # Mesa de madera noble
        draw.rect(surface, (45, 30, 20), (80, 140, 320, 35))
        draw.line(surface, (70, 50, 35), (80, 140), (400, 140), 2)

        # Sobre de pergamino
        lx, ly, lw, lh = 175, 40, 130, 95
        draw.rect(surface, (235, 220, 185), (lx, ly, lw, lh))
        draw.rect(surface, (180, 160, 125), (lx, ly, lw, lh), 2)
        
        # Pliegues del sobre
        draw.polygon(surface, (215, 200, 165), [(lx, ly), (lx + lw // 2, ly + 50), (lx + lw, ly)])
        draw.polygon(surface, (195, 180, 145), [(lx, ly), (lx + lw // 2, ly + 50), (lx + lw, ly)], 1)

        # Sello de lacre dorado brillante
        seal_pulse = int(180 + 40 * math.sin(tick * 0.15))
        seal_x, seal_y = lx + lw // 2, ly + 50
        draw.circle(surface, (210, 150, 20), (seal_x, seal_y), 16)
        draw.circle(surface, (255, seal_pulse, 50), (seal_x, seal_y), 13)
        seal_txt = self.font_pixel.render("IT", True, (80, 50, 10))
        surface.blit(seal_txt, (seal_x - 5, seal_y - 5))

        # Cinta carmesí colgante
        draw.polygon(surface, (160, 30, 30), [(seal_x - 6, seal_y + 10), (seal_x - 12, seal_y + 32), (seal_x, seal_y + 24)])
        draw.polygon(surface, (190, 40, 40), [(seal_x + 6, seal_y + 10), (seal_x + 12, seal_y + 32), (seal_x, seal_y + 24)])

        # Tintero y pluma de caligrafía
        draw.rect(surface, (30, 35, 45), (130, 120, 22, 20))
        draw.rect(surface, (50, 60, 80), (133, 115, 16, 5))
        # Pluma blanca inclinada
        draw.line(surface, (240, 240, 245), (142, 115), (120, 60), 3)
        draw.line(surface, (200, 200, 210), (120, 60), (115, 50), 2)

        # Etiqueta institucional
        cert_txt = self.font_pixel.render("ADMISIÓN FORMAL 2026", True, (0, 229, 255))
        surface.blit(cert_txt, (180, 20))

    def _draw_scene_developer_desk(self, surface, tick):
        """Escena 2: El escritorio nocturno de un futuro programador con monitor retro CRT."""
        # Monitor CRT de tubo
        mx, my, mw, mh = 170, 30, 140, 100
        draw.rect(surface, (50, 55, 65), (mx, my, mw, mh))
        draw.rect(surface, (35, 40, 50), (mx + 2, my + 2, mw - 4, mh - 4), 2)
        # Pantalla fósforo verde
        scr_x, scr_y, scr_w, scr_h = mx + 10, my + 10, mw - 20, mh - 26
        draw.rect(surface, (10, 32, 16), (scr_x, scr_y, scr_w, scr_h))
        draw.rect(surface, (20, 70, 35), (scr_x, scr_y, scr_w, scr_h), 1)

        # Líneas de código SQL simuladas en pantalla
        code_lines = [
            ("sql> SELECT * FROM futuro;", (0, 255, 136)),
            ("[OK] 1 fila encontrada.", (160, 240, 180)),
            ("carrera: Informatica", (240, 240, 240)),
            ("nivel: Senior Dev", (255, 215, 0))
        ]
        for idx, (c_txt, col) in enumerate(code_lines):
            draw_fitted_text(surface,c_txt,pygame.Rect(scr_x+5,scr_y+5+idx*14,scr_w-10,12),make_font(11),col,padding=0)

        # Cursor parpadeante
        if (tick // 25) % 2 == 0:
            draw.rect(surface, (0, 255, 136), (scr_x + 6, scr_y + 64, 6, 8))

        # Base del monitor
        draw.rect(surface, (45, 50, 60), (mx + 55, my + mh, 30, 12))
        draw.rect(surface, (40, 45, 55), (mx + 45, my + mh + 10, 50, 5))

        # Teclado en la mesa
        draw.rect(surface, (45, 50, 60), (160, 150, 120, 18))
        for kx in range(165, 275, 8):
            draw.rect(surface, (70, 75, 85), (kx, 153, 6, 10))

        # Taza de café con vapor animado
        cx, cy = 320, 142
        draw.rect(surface, (200, 70, 60), (cx, cy, 18, 18))
        draw.rect(surface, (200, 70, 60), (cx + 18, cy + 4, 5, 10), 2)
        # Humo ondulante
        s_y = int(math.sin(tick * 0.15) * 3)
        draw.line(surface, (180, 180, 190), (cx + 6, cy - 3 + s_y), (cx + 9, cy - 12 + s_y), 1)
        draw.line(surface, (180, 180, 190), (cx + 12, cy - 3 - s_y), (cx + 15, cy - 12 - s_y), 1)

        # Torre con ventilación, unidades y encendido
        draw.rect(surface,(53,68,80),(104,62,43,95),border_radius=3)
        draw.rect(surface,(20,33,46),(108,67,35,85),border_radius=2)
        for yy in (75,88):
            draw.rect(surface,(77,94,104),(112,yy,27,8),border_radius=1)
            draw.line(surface,(131,152,157),(114,yy+3),(132,yy+3))
        draw.circle(surface,(90,225,184),(125,111),4)
        for yy in range(127,146,4):draw.line(surface,(65,92,106),(114,yy),(137,yy))
        draw.line(surface,(48,66,77),(147,148),(161,148),2)
        draw.ellipse(surface,(110,135,147),(292,150,14,18))
        draw.line(surface,(36,59,73),(299,151),(299,160))
        draw.line(surface,(105,139,153),(299,150),(295,141))

    def _draw_scene_turing_blackboard(self, surface, tick):
        """Escena 3: Aula magistral con el Profesor Marco explicando Álgebra Relacional."""
        from game.visuals import board, panel, MINT, GOLD
        board(surface,pygame.Rect(106,18,326,140))
        centered(surface,'Aprender, practicar y comprobar',pygame.Rect(117,27,303,20),self.font_pixel,GOLD,padding=0)
        for cx,label in [(143,'A'),(178,'B')]:
            draw.circle(surface,(185,210,192),(cx,83),20,1)
            centered(surface,label,pygame.Rect(cx-8,73,16,17),self.font_pixel,MINT,padding=0)
        # Operador de cruce dibujado, sin depender de un glifo ausente
        draw.polygon(surface,GOLD,[(148,118),(160,110),(160,126)],1)
        draw.polygon(surface,GOLD,[(172,118),(160,110),(160,126)],1)
        for label,detail,yy,color in [('Aprobación','Nota >= 4.0',57,MINT),('Volver a practicar','Nota < 4.0, repites el año',100,(241,152,138))]:
            panel(surface,pygame.Rect(215,yy,202,35),(23,49,45),color,shadow=False)
            draw_fitted_text(surface,label,pygame.Rect(221,yy+3,190,14),self.font_pixel,color,padding=0)
            draw_fitted_text(surface,detail,pygame.Rect(221,yy+18,190,13),self.font_hint,(225,233,217),padding=0)
        sprite=pygame.Surface((20,26),pygame.SRCALPHA)
        marco_sprite(sprite,1,0)
        sprite.fill((0,0,0,0),pygame.Rect(16,10,4,10))
        surface.blit(pygame.transform.scale(sprite,(60,78)),(37,70))
        draw.line(surface,(105,133,95),(83,103),(111,89),5)
        draw.circle(surface,(239,197,151),(112,88),3)
        draw.line(surface,(240,244,229),(114,87),(119,83),2)

    def _draw_scene_campus_gate(self, surface, tick):
        """Escena 4: El pórtico monumental de entrada a la Facultad de Ingeniería Informática."""
        # Cielo crepuscular con luna
        draw.circle(surface, (255, 245, 200), (410, 30), 16)
        draw.circle(surface, (18, 25, 45), (416, 28), 14)

        # Edificio de la Facultad
        draw.rect(surface, (28, 38, 56), (100, 30, 280, 145))
        # Columnas monumentales
        for col_x in [120, 170, 300, 350]:
            draw.rect(surface, (45, 58, 82), (col_x, 40, 16, 135))
            draw.rect(surface, (60, 78, 108), (col_x - 3, 38, 22, 5)) # Capitel
            draw.rect(surface, (60, 78, 108), (col_x - 3, 170, 22, 5)) # Base

        # Puerta principal de doble hoja con luz interior cálida
        draw.rect(surface, (255, 210, 100), (210, 95, 60, 80))
        draw.rect(surface, (70, 50, 35), (210, 95, 60, 80), 2)
        draw.line(surface, (70, 50, 35), (240, 95), (240, 175), 2)

        # Gran letrero institucional sobre las columnas
        draw.rect(surface, (18, 24, 38), (100, 24, 280, 18))
        draw.rect(surface, COLOR_AMBER, (100, 24, 280, 18), 1)
        centered(surface,"FACULTAD DE INGENIERÍA INFORMÁTICA",pygame.Rect(104,25,272,16),self.font_pixel,COLOR_AMBER,padding=0)

        # Farolas con luz cálida titilante
        for lx in [60, 420]:
            draw.rect(surface, (50, 55, 65), (lx, 80, 4, 95))
            pulse = int(180 + 35 * math.sin(tick * 0.12 + lx))
            draw.circle(surface, (255, pulse, 80), (lx + 2, 76), 8)
            draw.rect(surface, (20, 20, 25), (lx - 2, 70, 8, 4))

        # Silueta del estudiante caminando hacia la entrada
        st_x, st_y = 230, 140
        draw.rect(surface, (15, 20, 30), (st_x + 5, st_y, 8, 8)) # Cabeza
        draw.rect(surface, (25, 35, 50), (st_x + 3, st_y + 8, 12, 14)) # Chaqueta/Mochila
        draw.rect(surface, (15, 20, 30), (st_x + 4, st_y + 22, 4, 12)) # Piernas
        draw.rect(surface, (15, 20, 30), (st_x + 10, st_y + 22, 4, 12))
