from game.visuals import marco_portrait
import pygame
from game.rendering import draw, make_font
from game.constants import *
from game.ui_helpers import render_wrapped_text, draw_panel, paginate_text

class DialogBox:
    def __init__(self, audio_manager=None):
        self.active = False
        self.title = ""
        self.text = ""
        self.speaker = ""
        self.callback = None
        self.audio = audio_manager
        self.font_title = make_font(15)
        self.font_text = make_font(13)
        self.font_hint = make_font(11)

    def show(self, title, text, speaker="Profesor Marco", callback=None, portrait=None):
        self.active = True
        self.title = title
        self.text = text
        self.speaker = speaker
        self.callback = callback
        self.portrait = portrait
        self.pages = paginate_text(text, self.font_text, 382, 56)
        self.page_index = 0
        if self.audio:
            self.audio.play_key()

    def close(self):
        self.active = False
        if self.callback:
            cb = self.callback
            self.callback = None
            cb()

    def advance(self):
        if self.page_index + 1 < len(self.pages):
            self.page_index += 1
        else:
            self.close()

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_RETURN, pygame.K_SPACE, pygame.K_e, pygame.K_ESCAPE]:
                self.advance()
                return True
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.advance()
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
        draw.rect(surface, (25, 35, 50), (avatar_x, avatar_y, 42, 54))
        draw.rect(surface, COLOR_AMBER, (avatar_x, avatar_y, 42, 54), 1)

        if self.portrait is not None:
            surface.blit(pygame.transform.scale(self.portrait, (32, 40)), (avatar_x + 5, avatar_y + 6))
        elif "Marco" in self.speaker:
            marco_portrait(surface,pygame.Rect(avatar_x,avatar_y,42,54))
        else:
            draw.rect(surface, (200, 50, 50), (avatar_x + 8, avatar_y + 8, 26, 38))
            draw.rect(surface, (240, 240, 245), (avatar_x + 12, avatar_y + 12, 18, 28))
            draw.line(surface, COLOR_AMBER, (avatar_x + 15, avatar_y + 18), (avatar_x + 26, avatar_y + 18), 2)
            draw.line(surface, COLOR_AMBER, (avatar_x + 15, avatar_y + 24), (avatar_x + 24, avatar_y + 24), 2)

        # Texto del diálogo formateado con Word-Wrap riguroso
        text_rect = pygame.Rect(box_x + 60, box_y + 24, box_w - 70, 56)
        render_wrapped_text(surface, self.pages[self.page_index], text_rect, self.font_text, color=COLOR_WHITE, line_spacing=2, padding=0)

        # Indicador de continuación
        hint_surf = self.font_hint.render(f"{self.page_index + 1:02} / {len(self.pages):02}", True, COLOR_CYAN)
        surface.blit(hint_surf, (box_x+60, box_y + box_h - 13))
        from game.visuals import advance_indicator
        advance_indicator(surface,(box_x+119,box_y+box_h-9),pygame.time.get_ticks()//16,self.page_index==len(self.pages)-1)
