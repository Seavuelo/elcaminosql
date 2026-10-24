import pygame
import math
from game.constants import *
from game.ui_helpers import draw_panel

class TitleScreen:
    def __init__(self, audio_manager, save_system, on_continue, on_new_game, on_open_notes, on_open_settings):
        self.audio = audio_manager
        self.save = save_system
        self.on_continue = on_continue
        self.on_new_game = on_new_game
        self.on_open_notes = on_open_notes
        self.on_open_settings = on_open_settings
        self.active = True

        self.selected_idx = 0
        self.font_title_big = pygame.font.Font(None, 28)
        self.font_subtitle = pygame.font.Font(None, 15)
        self.font_item = pygame.font.Font(None, 17)
        self.font_info = pygame.font.Font(None, 13)
        self.font_footer = pygame.font.Font(None, 12)
        self.font_by = pygame.font.Font(None, 13)

        # Pre-renderizar el degradado de fondo y la cuadrícula en perspectiva
        self.bg_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        for y in range(VIRTUAL_HEIGHT):
            ratio = y / VIRTUAL_HEIGHT
            c = (int(10 * (1 - ratio) + 20 * ratio),
                 int(14 * (1 - ratio) + 28 * ratio),
                 int(24 * (1 - ratio) + 48 * ratio))
            pygame.draw.line(self.bg_surface, c, (0, y), (VIRTUAL_WIDTH, y))

        for x in range(0, VIRTUAL_WIDTH, 40):
            pygame.draw.line(self.bg_surface, (25, 35, 60), (x, 180), (x, VIRTUAL_HEIGHT), 1)
        for y in range(180, VIRTUAL_HEIGHT, 20):
            pygame.draw.line(self.bg_surface, (25, 35, 60), (0, y), (VIRTUAL_WIDTH, y), 1)

    def _get_menu_options(self):
        has_save = self.save.exists()
        options = []
        if has_save:
            options.append(("continue", "CONTINUAR PARTIDA"))
        options.append(("new_game", "NUEVA PARTIDA"))
        if has_save:
            options.append(("notes", "CUADERNO DE APUNTES [N]"))
        options.append(("settings", "AJUSTES Y PANTALLA [O]"))
        options.append(("exit", "SALIR AL ESCRITORIO"))
        return options

    def handle_event(self, event):
        if not self.active:
            return False

        options = self._get_menu_options()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_idx = (self.selected_idx - 1) % len(options)
                self.audio.play_key()
                return True
            elif event.key == pygame.K_DOWN:
                self.selected_idx = (self.selected_idx + 1) % len(options)
                self.audio.play_key()
                return True
            elif event.key in [pygame.K_RETURN, pygame.K_SPACE]:
                action = options[self.selected_idx][0]
                self.audio.play_success()
                if action == "continue":
                    self.active = False
                    self.on_continue()
                elif action == "new_game":
                    self.active = False
                    self.on_new_game()
                elif action == "notes":
                    self.on_open_notes()
                elif action == "settings":
                    self.on_open_settings()
                elif action == "exit":
                    pygame.quit()
                    import sys
                    sys.exit(0)
                return True

        return False

    def draw(self, surface, tick):
        if not self.active:
            return

        # Fondo optimizado pre-renderizado
        surface.blit(self.bg_surface, (0, 0))

        # Marca de autoría en la esquina superior derecha
        by_surf = self.font_by.render("by Seavuelo", True, COLOR_CYAN)
        bw = by_surf.get_width() + 10
        pygame.draw.rect(surface, (14, 20, 32, 220), (VIRTUAL_WIDTH - bw - 8, 8, bw, 18))
        pygame.draw.rect(surface, (40, 70, 110), (VIRTUAL_WIDTH - bw - 8, 8, bw, 18), 1)
        surface.blit(by_surf, (VIRTUAL_WIDTH - bw - 3, 11))

        # 1. Logotipo / Título Principal
        t_glow = int(220 + 35 * math.sin(tick * 0.08))
        glow_color = (0, t_glow, 255)

        title_surf = self.font_title_big.render("EL CAMINO SQL", True, glow_color)
        tx = (VIRTUAL_WIDTH - title_surf.get_width()) // 2
        surface.blit(title_surf, (tx, 35))

        sub_surf = self.font_subtitle.render("Para todo buen final, hay un inicio...", True, COLOR_AMBER)
        sx = (VIRTUAL_WIDTH - sub_surf.get_width()) // 2
        surface.blit(sub_surf, (sx, 58))

        # 2. Información de la Partida Guardada (si existe)
        has_save = self.save.exists()
        if has_save:
            pname = self.save.data.get("player_name", "Estudiante")
            prole = self.save.data.get("title_role", "Alumno")
            pyear = self.save.data.get("current_year", 1)
            pday = self.save.data.get("current_day", 1)
            attempts = self.save.data.get("year_attempts", {}).get(str(pyear), 1)

            card_w = 320
            card_x = (VIRTUAL_WIDTH - card_w) // 2
            card_y = 82
            pygame.draw.rect(surface, (18, 26, 42), (card_x, card_y, card_w, 24))
            pygame.draw.rect(surface, (45, 65, 95), (card_x, card_y, card_w, 24), 1)

            save_str = f"Expediente: {pname} ({prole})  |  Año {pyear} de 4 (Día {pday}/5)"
            if attempts > 1:
                save_str += f" [Repetición #{attempts}]"
            i_surf = self.font_info.render(save_str, True, (180, 220, 255))
            surface.blit(i_surf, (card_x + (card_w - i_surf.get_width()) // 2, card_y + 6))

        # 3. Menú de Opciones
        options = self._get_menu_options()
        menu_y = 120 if has_save else 105
        btn_w = 260
        btn_h = 24
        btn_x = (VIRTUAL_WIDTH - btn_w) // 2

        self.selected_idx = min(self.selected_idx, len(options) - 1)

        for i, (key, label) in enumerate(options):
            by = menu_y + (i * 28)
            is_sel = (i == self.selected_idx)

            btn_bg = (25, 45, 75) if is_sel else (14, 20, 32)
            border_col = COLOR_AMBER if is_sel else (40, 55, 80)

            pygame.draw.rect(surface, btn_bg, (btn_x, by, btn_w, btn_h))
            pygame.draw.rect(surface, border_col, (btn_x, by, btn_w, btn_h), 1)

            cursor_str = "> " if is_sel else "  "
            item_col = COLOR_AMBER if is_sel else COLOR_WHITE
            item_surf = self.font_item.render(cursor_str + label, True, item_col)
            surface.blit(item_surf, (btn_x + 14, by + 4))

        # 4. Pie de página
        footer = self.font_footer.render("v2.0 • antiX Linux Edition • Motor SQLite3 Nativo", True, COLOR_GRAY)
        surface.blit(footer, (VIRTUAL_WIDTH // 2 - footer.get_width() // 2, VIRTUAL_HEIGHT - 16))
