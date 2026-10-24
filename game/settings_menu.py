import pygame
from game.constants import *
from game.ui_helpers import draw_panel

class SettingsMenu:
    def __init__(self, config_manager, audio_manager, on_apply_video_mode, on_quit_game=None):
        self.config = config_manager
        self.audio = audio_manager
        self.on_apply_video_mode = on_apply_video_mode
        self.on_quit_game = on_quit_game
        self.active = False

        self.font_title = pygame.font.Font(None, 18)
        self.font_item = pygame.font.Font(None, 16)
        self.font_hint = pygame.font.Font(None, 13)

        # Opciones disponibles
        self.screen_modes = ["windowed", "fullscreen", "borderless"]
        self.mode_labels = {
            "windowed": "Ventana",
            "fullscreen": "Pantalla Completa",
            "borderless": "Ventana sin Bordes"
        }

        self.resolutions = [[960, 600], [1280, 720], [1366, 768]]
        self.res_labels = {
            "960x600": "960 x 600 (Recomendada)",
            "1280x720": "1280 x 720 (HD)",
            "1366x768": "1366 x 768 (Nativa Laptop)"
        }

        # Estado editable temporal
        self.selected_idx = 0
        self.items = ["screen_mode", "resolution", "music_volume", "sfx_volume", "apply", "close", "quit"]

        self.temp_screen_mode = self.config.get("screen_mode", "windowed")
        res = self.config.get("resolution", [960, 600])
        self.temp_res_idx = 0
        for i, r in enumerate(self.resolutions):
            if r == res:
                self.temp_res_idx = i
                break
        self.temp_music_vol = int(self.config.get("music_volume", 0.25) * 100)
        self.temp_sfx_vol = int(self.config.get("sfx_volume", 0.70) * 100)

    def open(self):
        self.active = True
        self.temp_screen_mode = self.config.get("screen_mode", "windowed")
        res = self.config.get("resolution", [960, 600])
        self.temp_res_idx = 0
        for i, r in enumerate(self.resolutions):
            if r == res:
                self.temp_res_idx = i
                break
        self.temp_music_vol = int(self.config.get("music_volume", 0.25) * 100)
        self.temp_sfx_vol = int(self.config.get("sfx_volume", 0.70) * 100)

    def close(self):
        self.active = False

    def handle_event(self, event):
        if not self.active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.close()
                return True

            elif event.key == pygame.K_UP:
                self.selected_idx = (self.selected_idx - 1) % len(self.items)
                self.audio.play_key()
                return True

            elif event.key == pygame.K_DOWN:
                self.selected_idx = (self.selected_idx + 1) % len(self.items)
                self.audio.play_key()
                return True

            item = self.items[self.selected_idx]

            if event.key == pygame.K_LEFT:
                self.audio.play_key()
                if item == "screen_mode":
                    cur_idx = self.screen_modes.index(self.temp_screen_mode)
                    self.temp_screen_mode = self.screen_modes[(cur_idx - 1) % len(self.screen_modes)]
                elif item == "resolution":
                    self.temp_res_idx = (self.temp_res_idx - 1) % len(self.resolutions)
                elif item == "music_volume":
                    self.temp_music_vol = max(0, self.temp_music_vol - 10)
                    self.config.set("music_volume", self.temp_music_vol / 100.0)
                    self.audio.update_volumes()
                elif item == "sfx_volume":
                    self.temp_sfx_vol = max(0, self.temp_sfx_vol - 10)
                    self.config.set("sfx_volume", self.temp_sfx_vol / 100.0)
                    self.audio.update_volumes()
                return True

            elif event.key == pygame.K_RIGHT:
                self.audio.play_key()
                if item == "screen_mode":
                    cur_idx = self.screen_modes.index(self.temp_screen_mode)
                    self.temp_screen_mode = self.screen_modes[(cur_idx + 1) % len(self.screen_modes)]
                elif item == "resolution":
                    self.temp_res_idx = (self.temp_res_idx + 1) % len(self.resolutions)
                elif item == "music_volume":
                    self.temp_music_vol = min(100, self.temp_music_vol + 10)
                    self.config.set("music_volume", self.temp_music_vol / 100.0)
                    self.audio.update_volumes()
                elif item == "sfx_volume":
                    self.temp_sfx_vol = min(100, self.temp_sfx_vol + 10)
                    self.config.set("sfx_volume", self.temp_sfx_vol / 100.0)
                    self.audio.update_volumes()
                return True

            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                if item == "apply":
                    self.apply_changes()
                    self.audio.play_success()
                    return True
                elif item == "close":
                    self.close()
                    return True
                elif item == "quit":
                    if self.on_quit_game:
                        self.on_quit_game()
                    else:
                        pygame.quit()
                        import sys
                        sys.exit(0)
                    return True
                elif item == "screen_mode":
                    cur_idx = self.screen_modes.index(self.temp_screen_mode)
                    self.temp_screen_mode = self.screen_modes[(cur_idx + 1) % len(self.screen_modes)]
                    self.audio.play_key()
                    return True
                elif item == "resolution":
                    self.temp_res_idx = (self.temp_res_idx + 1) % len(self.resolutions)
                    self.audio.play_key()
                    return True

        return False

    def apply_changes(self):
        new_res = self.resolutions[self.temp_res_idx]
        self.config.set("screen_mode", self.temp_screen_mode)
        self.config.set("resolution", new_res)
        self.config.set("music_volume", self.temp_music_vol / 100.0)
        self.config.set("sfx_volume", self.temp_sfx_vol / 100.0)
        self.audio.update_volumes()
        self.on_apply_video_mode(self.temp_screen_mode, new_res)

    def draw(self, surface):
        if not self.active:
            return

        panel_w = 350
        panel_h = 250
        panel_x = (VIRTUAL_WIDTH - panel_w) // 2
        panel_y = (VIRTUAL_HEIGHT - panel_h) // 2

        # Fondo atenuado oscuro detrás
        dim = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 180))
        surface.blit(dim, (0, 0))

        # Panel de ajustes
        rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        draw_panel(surface, rect, bg_color=(16, 22, 36, 250), border_color=COLOR_CYAN, border_width=2,
                   title="AJUSTES Y CONFIGURACIÓN", font=self.font_title, title_color=COLOR_CYAN)

        start_y = panel_y + 32
        row_h = 25

        labels = [
            ("Modo de Pantalla:", f"< {self.mode_labels.get(self.temp_screen_mode)} >"),
            ("Resolución:", f"< {self.resolutions[self.temp_res_idx][0]}x{self.resolutions[self.temp_res_idx][1]} >"),
            ("Volumen Música:", f"< {self.temp_music_vol}% >"),
            ("Volumen Efectos:", f"< {self.temp_sfx_vol}% >"),
            ("Aplicar Cambios", "[ GUARDAR Y APLICAR ]"),
            ("Cerrar", "[ VOLVER AL JUEGO ]"),
            ("Salir del Juego", "[ GUARDAR Y SALIR AL ESCRITORIO ]")
        ]

        for i, (name, val) in enumerate(labels):
            y = start_y + (i * row_h)
            is_sel = (i == self.selected_idx)
            
            # Barra resaltada de selección
            if is_sel:
                pygame.draw.rect(surface, (25, 45, 75), (panel_x + 10, y - 2, panel_w - 20, 22))
                pygame.draw.rect(surface, COLOR_AMBER, (panel_x + 10, y - 2, panel_w - 20, 22), 1)
                cursor_txt = "> "
                text_color = COLOR_AMBER
            else:
                cursor_txt = "  "
                text_color = COLOR_WHITE

            if i < 4:
                # Opciones normales
                s_name = self.font_item.render(cursor_txt + name, True, text_color)
                surface.blit(s_name, (panel_x + 16, y + 2))

                s_val = self.font_item.render(val, True, COLOR_CYAN if is_sel else (180, 210, 240))
                val_w = s_val.get_width()
                surface.blit(s_val, (panel_x + panel_w - val_w - 20, y + 2))
            else:
                # Botones de acción centrados
                if i == 6 and is_sel:
                    b_color = (255, 120, 120)
                elif i == 4 and is_sel:
                    b_color = COLOR_GREEN
                elif is_sel:
                    b_color = COLOR_AMBER
                else:
                    b_color = COLOR_WHITE
                btn_surf = self.font_item.render(val, True, b_color)
                bx = panel_x + (panel_w - btn_surf.get_width()) // 2
                surface.blit(btn_surf, (bx, y + 3))

        # Pistas de navegación al pie
        hint_txt = "[FLECHAS] Cambiar valores  |  [ENTER] Seleccionar  |  [ESC] Salir"
        hint_surf = self.font_hint.render(hint_txt, True, COLOR_GRAY)
        hx = panel_x + (panel_w - hint_surf.get_width()) // 2
        surface.blit(hint_surf, (hx, panel_y + panel_h - 16))
