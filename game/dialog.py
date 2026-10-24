import pygame
from game.constants import *
from game.ui_helpers import render_wrapped_text, draw_panel

class DialogBox:
    def __init__(self, audio_manager=None):
        self.active = False
        self.title = ""
        self.text = ""
        self.speaker = ""
        self.callback = None
        self.audio = audio_manager
        self.font_title = pygame.font.Font(None, 15)
        self.font_text = pygame.font.Font(None, 13)
        self.font_hint = pygame.font.Font(None, 11)

    def show(self, title, text, speaker="Prof. Turing", callback=None):
        self.active = True
        self.title = title
        self.text = text
        self.speaker = speaker
        self.callback = callback
        if self.audio:
            self.audio.play_key()

    def close(self):
        self.active = False
        if self.callback:
            cb = self.callback
            self.callback = None
            cb()

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_ESCAPE]:
                self.close()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.close()
            return True
        return False

    def draw(self, surface):
        if not self.active:
            return

        box_x = 14
        box_y = 192
        box_w = 452
        box_h = 96

        # Panel con borde cian
        box_rect = pygame.Rect(box_x, box_y, box_w, box_h)
        draw_panel(surface, box_rect, bg_color=(14, 18, 28, 245), border_color=COLOR_CYAN, border_width=1,
                   title=f"[{self.speaker}]  {self.title}", font=self.font_title, title_color=COLOR_AMBER)

        # Avatar
        avatar_x = box_x + 10
        avatar_y = box_y + 24
        pygame.draw.rect(surface, (25, 35, 50), (avatar_x, avatar_y, 42, 54))
        pygame.draw.rect(surface, COLOR_AMBER, (avatar_x, avatar_y, 42, 54), 1)

        if "Turing" in self.speaker:
            pygame.draw.rect(surface, (220, 220, 225), (avatar_x + 8, avatar_y + 4, 26, 12))
            pygame.draw.rect(surface, (255, 205, 148), (avatar_x + 10, avatar_y + 12, 22, 20))
            pygame.draw.circle(surface, (20, 25, 35), (avatar_x + 16, avatar_y + 20), 3, 1)
            pygame.draw.circle(surface, (20, 25, 35), (avatar_x + 26, avatar_y + 20), 3, 1)
            pygame.draw.rect(surface, (65, 85, 60), (avatar_x + 6, avatar_y + 34, 30, 18))
        else:
            pygame.draw.rect(surface, (200, 50, 50), (avatar_x + 8, avatar_y + 8, 26, 38))
            pygame.draw.rect(surface, (240, 240, 245), (avatar_x + 12, avatar_y + 12, 18, 28))
            pygame.draw.line(surface, COLOR_AMBER, (avatar_x + 15, avatar_y + 18), (avatar_x + 26, avatar_y + 18), 2)
            pygame.draw.line(surface, COLOR_AMBER, (avatar_x + 15, avatar_y + 24), (avatar_x + 24, avatar_y + 24), 2)

        # Texto del diálogo formateado con Word-Wrap riguroso
        text_rect = pygame.Rect(box_x + 60, box_y + 24, box_w - 70, 56)
        render_wrapped_text(surface, self.text, text_rect, self.font_text, color=COLOR_WHITE, line_spacing=2, padding=0)

        # Indicador de continuación
        hint_surf = self.font_hint.render("Pulsa [ESPACIO] o [ENTER] para continuar ▼", True, COLOR_CYAN)
        surface.blit(hint_surf, (box_x + box_w - hint_surf.get_width() - 10, box_y + box_h - 13))
