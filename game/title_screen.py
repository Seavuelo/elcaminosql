import pygame
from game.version import DISPLAY_VERSION
from game.rendering import draw, make_font
import math
from game.visuals import title_art, panel, button, centered, GOLD, MINT
from game.constants import *
from game.ui_helpers import draw_panel, render_wrapped_text, draw_fitted_text

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
        self.confirm_new_game = False
        self.confirmation_choice = 0
        self.font_title_big = make_font(28)
        self.font_subtitle = make_font(15)
        self.font_item = make_font(17)
        self.font_info = make_font(13)
        self.font_footer = make_font(12)
        self.font_by = make_font(13)

        self.bg_surface = title_art()

    def _get_menu_options(self):
        has_save = self.save.exists()
        options = []
        if has_save:
            options.append(("continue", "CONTINUAR PARTIDA"))
        options.append(("new_game", "NUEVA PARTIDA"))
        if has_save:
            options.append(("notes", "CUADERNO DE APUNTES"))
        options.append(("settings", "AJUSTES Y PANTALLA"))
        options.append(("exit", "SALIR AL ESCRITORIO"))
        return options

    def handle_event(self, event):
        if not self.active:
            return False

        options = self._get_menu_options()

        if self.confirm_new_game:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._confirm_new(False)
                elif event.key in (pygame.K_LEFT, pygame.K_UP):
                    self.confirmation_choice = 0
                elif event.key in (pygame.K_RIGHT, pygame.K_DOWN):
                    self.confirmation_choice = 1
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self._confirm_new(self.confirmation_choice == 1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(78, 185, 150, 27).collidepoint(event.pos):
                    self._confirm_new(False)
                elif pygame.Rect(242, 185, 160, 27).collidepoint(event.pos):
                    self._confirm_new(True)
            return True

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            menu_y = 120 if self.save.exists() else 105
            for i, (action, _) in enumerate(options):
                if pygame.Rect(110, menu_y + i * 28, 260, 24).collidepoint(event.pos):
                    self.selected_idx = i
                    self._activate(action)
                    return True

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
                self._activate(options[self.selected_idx][0])
                return True

        return False

    def _activate(self, action):
        self.audio.play_success()
        if action == "continue":
            self.active = False
            self.on_continue()
        elif action == "new_game":
            if self.save.exists():
                self.confirm_new_game = True
                self.confirmation_choice = 0
            else:
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

    def _confirm_new(self, accepted):
        self.confirm_new_game = False
        if accepted:
            self.active = False
            self.on_new_game()

    def draw(self, surface, tick):
        if not self.active:
            return

        # Fondo optimizado pre-renderizado
        surface.blit(self.bg_surface, (0, 0))

        # Marca de autoría en la esquina superior derecha
        by_surf = self.font_by.render("by Seavuelo", True, COLOR_CYAN)
        bw = by_surf.get_width() + 10
        draw.rect(surface, (14, 20, 32, 220), (VIRTUAL_WIDTH - bw - 8, 8, bw, 18))
        draw.rect(surface, (40, 70, 110), (VIRTUAL_WIDTH - bw - 8, 8, bw, 18), 1)
        surface.blit(by_surf, (VIRTUAL_WIDTH - bw - 3, 11))

        panel(surface,pygame.Rect(102,30,276,43),(19,36,46),MINT,shadow=True)
        centered(surface,"EL CAMINO SQL",pygame.Rect(107,30,266,28),self.font_title_big,GOLD)
        centered(surface,"Para todo buen final, hay un inicio...",pygame.Rect(102,58,276,14),self.font_subtitle,(192,206,195),padding=0)
        panel(surface,pygame.Rect(101,112 if self.save.exists() else 97,278,151 if self.save.exists() else 122),(16,29,40),MINT)

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
            panel(surface,pygame.Rect(card_x,card_y,card_w,24),(27,44,53),MINT)

            save_str = f"Expediente: {pname} ({prole})  |  Año {pyear} de 4 (Día {pday}/5)"
            if attempts > 1:
                save_str += f" [Repetición #{attempts}]"
            centered(surface,save_str,pygame.Rect(card_x+5,card_y,card_w-10,24),self.font_info,(192,216,211))

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

            button(surface,label,pygame.Rect(btn_x,by,btn_w,btn_h),self.font_item,selected=is_sel,accent=GOLD if is_sel else MINT)

        # 4. Pie de página
        footer = self.font_footer.render(DISPLAY_VERSION, True, COLOR_GRAY)
        surface.blit(footer, (VIRTUAL_WIDTH // 2 - footer.get_width() // 2, VIRTUAL_HEIGHT - 16))

        if self.confirm_new_game:
            panel(surface,pygame.Rect(60,76,360,151),(19,31,44),GOLD,selected=True)
            draw_fitted_text(surface, "Antes de empezar una nueva partida", pygame.Rect(78, 87, 324, 21), self.font_item, COLOR_AMBER, padding=0)
            render_wrapped_text(surface, "¿Estás seguro de empezar una nueva partida?\n\nPerderás todo tu progreso actual, incluidos la carrera, Liga de Dioses, los modelos y tus apuntes", pygame.Rect(78, 114, 324, 65), self.font_info, padding=0, line_spacing=2)
            for i, (label, rect) in enumerate((("Cancelar [Esc]", pygame.Rect(78, 185, 150, 27)), ("Sí, empezar de nuevo", pygame.Rect(242, 185, 160, 27)))):
                button(surface,label,rect,self.font_info,selected=self.confirmation_choice==i,accent=GOLD if i==0 else (221,129,112))
