import pygame
from game.constants import *
from game.ui_helpers import draw_panel, render_wrapped_text

class CharacterCustomizer:
    def __init__(self, audio_manager, on_finish_callback):
        self.audio = audio_manager
        self.on_finish_callback = on_finish_callback
        self.active = False

        self.font_title = pygame.font.Font(None, 20)
        self.font_field = pygame.font.Font(None, 16)
        self.font_hint = pygame.font.Font(None, 13)
        self.font_preview = pygame.font.Font(None, 12)
        self.font_role = pygame.font.Font(None, 13)

        # Paletas y opciones
        self.skin_tones = [
            ("Claro", (255, 205, 148)),
            ("Trigueño", (230, 175, 125)),
            ("Moreno", (185, 125, 80)),
            ("Ébano", (115, 75, 50))
        ]

        self.hair_colors = [
            ("Castaño", (80, 45, 25)),
            ("Negro", (30, 25, 25)),
            ("Rubio", (240, 210, 80)),
            ("Pelirojo", (200, 75, 30)),
            ("Cyan Cyber", (0, 229, 255))
        ]

        self.hair_styles = [
            "Corto Clásico",
            "Largo con Coleta",
            "Despeinado Moderno"
        ]

        self.shirt_colors = [
            ("Azul Hacker", (30, 144, 255)),
            ("Rojo Carmesí", (220, 50, 50)),
            ("Verde Terminal", (36, 180, 100)),
            ("Negro Cyber", (35, 40, 50)),
            ("Púrpura Mágico", (150, 60, 200))
        ]

        self.genders = [
            ("Masculino", "male", "Bienvenido", "Alumno"),
            ("Femenino", "female", "Bienvenida", "Alumna"),
            ("Neutro", "neutral", "Bienvenide", "Estudiante")
        ]

        # Estado actual de edición
        self.player_name = "Alex"
        self.typing_name = False
        self.gender_idx = 0
        self.skin_idx = 0
        self.hair_col_idx = 0
        self.hair_style_idx = 0
        self.shirt_col_idx = 0

        self.selected_field = 0
        self.fields = ["name", "gender", "skin", "hair_col", "hair_style", "shirt_col", "confirm"]

    def open(self):
        self.active = True
        self.selected_field = 0

    def close(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            field = self.fields[self.selected_field]

            if field == "name" and self.typing_name:
                if event.key == pygame.K_RETURN:
                    self.typing_name = False
                    self.audio.play_key()
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    if len(self.player_name) > 0:
                        self.player_name = self.player_name[:-1]
                        self.audio.play_key()
                    return True
                elif event.unicode and len(self.player_name) < 14 and event.unicode.isalnum() or event.unicode == " ":
                    self.player_name += event.unicode
                    self.audio.play_key()
                    return True

            if event.key == pygame.K_UP:
                self.selected_field = (self.selected_field - 1) % len(self.fields)
                self.typing_name = False
                self.audio.play_key()
                return True

            elif event.key == pygame.K_DOWN:
                self.selected_field = (self.selected_field + 1) % len(self.fields)
                self.typing_name = False
                self.audio.play_key()
                return True

            elif event.key == pygame.K_LEFT:
                self.audio.play_key()
                if field == "gender":
                    self.gender_idx = (self.gender_idx - 1) % len(self.genders)
                elif field == "skin":
                    self.skin_idx = (self.skin_idx - 1) % len(self.skin_tones)
                elif field == "hair_col":
                    self.hair_col_idx = (self.hair_col_idx - 1) % len(self.hair_colors)
                elif field == "hair_style":
                    self.hair_style_idx = (self.hair_style_idx - 1) % len(self.hair_styles)
                elif field == "shirt_col":
                    self.shirt_col_idx = (self.shirt_col_idx - 1) % len(self.shirt_colors)
                return True

            elif event.key == pygame.K_RIGHT:
                self.audio.play_key()
                if field == "gender":
                    self.gender_idx = (self.gender_idx + 1) % len(self.genders)
                elif field == "skin":
                    self.skin_idx = (self.skin_idx + 1) % len(self.skin_tones)
                elif field == "hair_col":
                    self.hair_col_idx = (self.hair_col_idx + 1) % len(self.hair_colors)
                elif field == "hair_style":
                    self.hair_style_idx = (self.hair_style_idx + 1) % len(self.hair_styles)
                elif field == "shirt_col":
                    self.shirt_col_idx = (self.shirt_col_idx + 1) % len(self.shirt_colors)
                return True

            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if field == "name":
                    self.typing_name = not self.typing_name
                    self.audio.play_key()
                    return True
                elif field == "confirm":
                    self.audio.play_success()
                    self.active = False
                    final_name = self.player_name.strip() if self.player_name.strip() else "Novato"
                    g_info = self.genders[self.gender_idx]
                    self.on_finish_callback({
                        "name": final_name,
                        "gender": g_info[1],
                        "pronoun_welcome": g_info[2],
                        "title_role": g_info[3],
                        "skin_tone": self.skin_idx,
                        "hair_color": self.hair_col_idx,
                        "hair_style": self.hair_style_idx,
                        "shirt_color": self.shirt_col_idx
                    })
                    return True

        return False

    def draw(self, surface, tick):
        if not self.active:
            return

        # Fondo cyberpunk de matrícula
        surface.fill((12, 16, 26))

        # Panel Principal
        panel_rect = pygame.Rect(16, 12, 448, 276)
        draw_panel(surface, panel_rect, bg_color=(16, 22, 35, 250), border_color=COLOR_CYAN, border_width=2,
                   title="CREACIÓN DE ESTUDIANTE  |  MATRÍCULA UNIVERSITARIA", font=self.font_title, title_color=COLOR_CYAN)

        # 1. Vista Previa del Personaje a la Izquierda (Pixel Art aumentado)
        prev_box = pygame.Rect(30, 42, 100, 160)
        pygame.draw.rect(surface, (22, 30, 46), prev_box)
        pygame.draw.rect(surface, (45, 65, 95), prev_box, 1)

        p_label = self.font_preview.render("VISTA PREVIA", True, COLOR_AMBER)
        surface.blit(p_label, (42, 46))

        # Renderizar sprite escalado x3
        sprite_surf = pygame.Surface((16, 20), pygame.SRCALPHA)
        self._render_character_preview(sprite_surf)
        big_sprite = pygame.transform.scale(sprite_surf, (48, 60))
        surface.blit(big_sprite, (56, 75))

        # Etiqueta con el nombre y pronombre
        n_surf = self.font_field.render(self.player_name if self.player_name else "...", True, COLOR_WHITE)
        surface.blit(n_surf, (prev_box.centerx - n_surf.get_width() // 2, 150))
        
        role_str = self.genders[self.gender_idx][3]
        r_surf = self.font_role.render(f"[{role_str}]", True, (0, 229, 255))
        surface.blit(r_surf, (prev_box.centerx - r_surf.get_width() // 2, 168))

        # 2. Formulario de Personalización a la Derecha
        form_x = 145
        form_y = 42
        row_h = 28

        labels = [
            ("Nombre:", f"[ {self.player_name} ]" + (" |" if self.typing_name and (tick // 25) % 2 == 0 else "")),
            ("Identidad:", f"< {self.genders[self.gender_idx][0]} >"),
            ("Tono de Piel:", f"< {self.skin_tones[self.skin_idx][0]} >"),
            ("Color de Cabello:", f"< {self.hair_colors[self.hair_col_idx][0]} >"),
            ("Estilo de Cabello:", f"< {self.hair_styles[self.hair_style_idx]} >"),
            ("Color de Ropa:", f"< {self.shirt_colors[self.shirt_col_idx][0]} >"),
            ("Confirmar", "[ ¡CONFIRMAR MATRÍCULA Y EMPEZAR! ]")
        ]

        for i, (name, val) in enumerate(labels):
            y = form_y + (i * row_h)
            is_sel = (i == self.selected_field)

            if is_sel:
                pygame.draw.rect(surface, (25, 45, 75), (form_x - 4, y - 2, 310, 22))
                pygame.draw.rect(surface, COLOR_AMBER, (form_x - 4, y - 2, 310, 22), 1)
                text_col = COLOR_AMBER
                cursor_txt = "> "
            else:
                text_col = COLOR_WHITE
                cursor_txt = "  "

            if i < 6:
                s_name = self.font_field.render(cursor_txt + name, True, text_col)
                surface.blit(s_name, (form_x, y + 2))

                val_col = COLOR_GREEN if (i == 0 and self.typing_name) else (COLOR_CYAN if is_sel else (180, 210, 240))
                s_val = self.font_field.render(val, True, val_col)
                surface.blit(s_val, (form_x + 130, y + 2))
            else:
                # Botón de Confirmación
                btn_surf = self.font_field.render(val, True, COLOR_GREEN if is_sel else COLOR_WHITE)
                surface.blit(btn_surf, (form_x + 20, y + 3))

        # Pista al pie
        hint_txt = "[FLECHAS] Navegar y Cambiar  |  [ENTER] Escribir / Confirmar Matrícula"
        hint_surf = self.font_hint.render(hint_txt, True, COLOR_GRAY)
        surface.blit(hint_surf, (panel_rect.centerx - hint_surf.get_width() // 2, panel_rect.bottom - 16))

    def _render_character_preview(self, surf):
        skin = self.skin_tones[self.skin_idx][1]
        hair = self.hair_colors[self.hair_col_idx][1]
        shirt = self.shirt_colors[self.shirt_col_idx][1]
        style = self.hair_style_idx

        # Sombra
        pygame.draw.ellipse(surf, (15, 20, 30, 100), (2, 17, 12, 3))

        # Rostro
        pygame.draw.rect(surf, skin, (4, 4, 8, 5))
        pygame.draw.rect(surf, (20, 25, 35), (5, 6, 2, 2))
        pygame.draw.rect(surf, (20, 25, 35), (9, 6, 2, 2))

        # Cabello según estilo
        if style == 0: # Corto
            pygame.draw.rect(surf, hair, (4, 1, 8, 4))
            pygame.draw.rect(surf, hair, (3, 3, 2, 3))
            pygame.draw.rect(surf, hair, (11, 3, 2, 3))
        elif style == 1: # Largo / Coleta
            pygame.draw.rect(surf, hair, (3, 1, 10, 4))
            pygame.draw.rect(surf, hair, (2, 4, 3, 8))
            pygame.draw.rect(surf, hair, (11, 4, 3, 8))
        else: # Despeinado
            pygame.draw.rect(surf, hair, (3, 0, 10, 5))
            pygame.draw.rect(surf, hair, (5, 0, 6, 2))
            pygame.draw.rect(surf, hair, (12, 2, 2, 4))

        # Ropa
        pygame.draw.rect(surf, shirt, (4, 9, 8, 6))
        # Mochila naranja
        pygame.draw.rect(surf, (220, 90, 40), (3, 9, 1, 6))
        pygame.draw.rect(surf, (220, 90, 40), (12, 9, 1, 6))

        # Pantalón y Zapatos
        pygame.draw.rect(surf, (40, 50, 75), (4, 15, 3, 3))
        pygame.draw.rect(surf, (40, 50, 75), (9, 15, 3, 3))
        pygame.draw.rect(surf, (30, 25, 20), (4, 17, 3, 2))
        pygame.draw.rect(surf, (30, 25, 20), (9, 17, 3, 2))
