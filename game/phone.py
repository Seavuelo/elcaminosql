from game.visuals import panel, button, GOLD, MUTED
"""Teléfono opcional con Liga de Dioses y partidas automáticas locales"""
import math
import pygame
from game.constants import COLOR_WHITE, COLOR_CYAN, COLOR_AMBER
from game.rendering import draw, make_font
from game.ui_helpers import draw_panel, draw_fitted_text, render_wrapped_text
from game.league import LeagueGame, GODS, STRATEGIES, UPGRADES


class StudentPhone:
    def __init__(self, save, audio):
        self.game = LeagueGame(save)
        self.audio = audio
        self.active = False
        self.opening = 0.0
        self.tab = "match"
        self.selected_upgrade = 0
        self.message = "Aprueba ejercicios SQL para ganar XP y comprar aumentos"
        self.font_title = make_font(19)
        self.font = make_font(14)
        self.small = make_font(12)
        self.buttons = []

    def open(self):
        self.active = True
        self.opening = 0.0
        self.audio.play_key()

    def close(self):
        self.active = False

    def update(self, dt):
        if self.active:
            self.opening = min(1, self.opening + dt / 0.25)
        if self.game.update(dt):
            result = self.game.state["last_match"]
            self.message = ("Victoria" if result["win"] else "Derrota") + ", prueba otra combinación o compra aumentos con tus XP"

    def _activate(self, action):
        kind, value = action
        if kind == "tab":
            self.tab = value
        elif kind == "god":
            if self.game.choose_god(value):
                self.message = f"{GODS[value][0]} combina mejor con la estrategia {STRATEGIES[GODS[value][2]]}"
        elif kind == "strategy":
            if self.game.choose_strategy(value):
                self.message = {"safe": "Seguro aprovecha visión y posicionamiento para reducir riesgos",
                                "pressure": "Presión aprovecha mecánicas y maestría para buscar peleas",
                                "team": "En equipo aprovecha visión y objetivos para convertir ventajas"}[value]
        elif kind == "buy":
            self.selected_upgrade = list(UPGRADES).index(value)
            success, self.message = self.game.buy(value)
            if success:
                self.audio.play_success()
                return
        elif kind == "battle":
            if self.game.start_battle():
                self.tab = "match"
                self.message = "La partida se juega sola, puedes cerrar el teléfono y seguir estudiando"
        self.audio.play_key()

    def handle_event(self, event):
        if not self.active:
            return False
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_F4):
                self.close()
            elif event.key in (pygame.K_TAB, pygame.K_1, pygame.K_2):
                self.tab = ("upgrades" if self.tab == "match" else "match") if event.key == pygame.K_TAB else ("match" if event.key == pygame.K_1 else "upgrades")
            elif self.tab == "upgrades":
                if event.key in (pygame.K_UP, pygame.K_DOWN):
                    self.selected_upgrade = (self.selected_upgrade + (1 if event.key == pygame.K_DOWN else -1)) % len(UPGRADES)
                elif event.key == pygame.K_RETURN:
                    self._activate(("buy", list(UPGRADES)[self.selected_upgrade]))
            elif not self.game.state["battle"]:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                    gods = list(GODS)
                    index = gods.index(self.game.state["god"])
                    self._activate(("god", gods[(index + (1 if event.key == pygame.K_RIGHT else -1)) % len(gods)]))
                elif event.key == pygame.K_s:
                    options = list(STRATEGIES)
                    index = options.index(self.game.state["strategy"])
                    self._activate(("strategy", options[(index + 1) % len(options)]))
                elif event.key == pygame.K_RETURN:
                    self._activate(("battle", None))
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for rect, action in self.buttons:
                if rect.collidepoint(event.pos):
                    self._activate(action)
                    break
        return True

    def _button(self, surface, rect, label, action, selected=False, enabled=True):
        button(surface,label,rect,self.font,selected=selected and enabled,accent=GOLD if enabled else MUTED,fill=None if enabled else (28,35,45))
        if enabled:
            self.buttons.append((rect, action))

    def draw(self, surface, tick=0):
        if not self.active:
            return
        self.buttons = []
        dim = pygame.Surface((480, 300), pygame.SRCALPHA)
        dim.fill((0, 0, 0, 170))
        surface.blit(dim, (0, 0))
        if self.opening < 1:
            height = max(16, round(284 * self.opening))
            width = max(48, round(388 * self.opening))
            draw.rect(surface, (14, 19, 30), (240 - width // 2, 296 - height, width, height), border_radius=8)
            draw.rect(surface, COLOR_CYAN, (240 - width // 2, 296 - height, width, height), 1, border_radius=8)
            return
        draw_panel(surface, pygame.Rect(44, 6, 392, 288), bg_color=(12, 18, 29), border_color=(95, 115, 150), border_width=2)
        draw.rect(surface, (3, 6, 12), (215, 7, 50, 5), border_radius=2)
        surface.blit(self.font_title.render("Liga de Dioses", True, COLOR_AMBER), (58, 18))
        xp = f"{self.game.state['xp']} XP"
        xp_surface = self.font.render(xp, True, COLOR_CYAN)
        surface.blit(xp_surface, (421 - xp_surface.get_width(), 20))
        rank = f"{self.game.rank} | {self.game.state['rating']} PL | {self.game.state['wins']} victorias / {self.game.state['matches']} partidas"
        draw_fitted_text(surface, rank, pygame.Rect(58, 37, 364, 18), self.small, COLOR_WHITE, padding=1)
        self._button(surface, pygame.Rect(58, 58, 176, 21), "Partida", ("tab", "match"), self.tab == "match")
        self._button(surface, pygame.Rect(242, 58, 180, 21), "Aumentos", ("tab", "upgrades"), self.tab == "upgrades")
        if self.tab == "upgrades":
            self._draw_upgrades(surface)
        elif self.game.state["battle"]:
            self._draw_battle(surface)
        else:
            self._draw_match(surface)
        draw.rect(surface,(100,119,129),(211,285,58,2),border_radius=1)

    def _draw_match(self, surface):
        for index, (key, (name, role, _, color)) in enumerate(GODS.items()):
            rect = pygame.Rect(58 + index * 123, 87, 118, 38)
            self._button(surface, rect, f"{name} · {role}", ("god", key), self.game.state["god"] == key)
            draw.circle(surface, color, (rect.right - 8, rect.top + 7), 3)
        for index, (key, label) in enumerate(STRATEGIES.items()):
            self._button(surface, pygame.Rect(58 + index * 123, 131, 118, 23), label,
                         ("strategy", key), self.game.state["strategy"] == key)
        last = self.game.state["last_match"]
        if last:
            status = "VICTORIA" if last["win"] else "DERROTA"
            color = (110, 220, 155) if last["win"] else (235, 135, 130)
            draw_fitted_text(surface, f"{status} · {last['kills']}/{last['deaths']}/{last['assists']}",
                             pygame.Rect(58, 163, 364, 27), self.font_title, color)
            detail = f"{GODS[last['god']][0]} · {STRATEGIES[last['strategy']]} · {last['rank_after']}"
        else:
            detail = "Tres partidas de colocación para salir de Unranked"
        draw_fitted_text(surface, detail, pygame.Rect(58, 194, 364, 21), self.small, COLOR_WHITE)
        render_wrapped_text(surface, self.message, pygame.Rect(58, 217, 364, 31), self.small,
                            color=(170, 195, 215), line_spacing=1, padding=1)
        self._button(surface, pygame.Rect(58, 250, 364, 22), "Buscar partida · gratis", ("battle", None), selected=True)

    def _draw_upgrades(self, surface):
        for index, (key, (name, description)) in enumerate(UPGRADES.items()):
            level = self.game.level(key)
            cost = self.game.cost(key)
            label = f"{name}  {level}/10 · " + ("MÁXIMO" if level == 10 else f"{cost} XP")
            self._button(surface, pygame.Rect(58, 86 + index * 25, 364, 23), label,
                         ("buy", key), self.selected_upgrade == index,
                         enabled=not self.game.state["battle"])
        key = list(UPGRADES)[self.selected_upgrade]
        detail = UPGRADES[key][1]
        if key == "mastery":
            detail += f" · {GODS[self.game.state['god']][0]}"
        render_wrapped_text(surface, detail, pygame.Rect(58, 214, 364, 25), self.small, line_spacing=1, padding=1)
        render_wrapped_text(surface, self.message, pygame.Rect(58, 245, 364, 27), self.small,
                            color=COLOR_CYAN, line_spacing=1, padding=1)

    def _draw_battle(self, surface):
        battle = self.game.state["battle"]
        progress = battle["elapsed"] / battle["duration"]
        arena = pygame.Rect(58, 88, 364, 132)
        panel(surface,arena,(24,52,46),(77,125,101))
        for i in range(60):
            xx=62+(i*47)%354;yy=93+(i*31)%119
            draw.rect(surface,(34,68,52),(xx,yy,2,1))
        draw.line(surface, (100, 95, 67), (80, 201), (398, 106), 12)
        draw.line(surface, (41, 93, 98), (180, 92), (300, 216), 8)
        for x, y in ((105, 122), (350, 183), (145, 179), (314, 115)):
            draw.circle(surface, (30, 80, 57), (x, y), 10)
        draw.rect(surface, (85, 145, 225), (67, 187, 19, 23))
        draw.rect(surface, (200, 90, 105), (394, 96, 19, 23))
        elapsed = battle["elapsed"]
        for team in (0, 1):
            color = GODS[battle['result']['god']][3] if team == 0 else (225, 115, 110)
            for index in range(3):
                phase = elapsed * 1.7 + index * 2 + team
                x = 225 + math.sin(phase) * (47 + index * 7) + (team * 2 - 1) * 20
                y = 153 + math.cos(phase * 0.8) * (18 + index * 5)
                draw.circle(surface, color, (round(x), round(y)), 5)
                draw.rect(surface, (12, 20, 25), (round(x) - 6, round(y) - 10, 12, 3))
                draw.rect(surface, (120, 225, 125), (round(x) - 6, round(y) - 10, max(2, round(12 - (phase % 5) * 2)), 2))
                shot = (elapsed * 2 + index * 0.31) % 1
                target_x = 250 if team == 0 else 225
                draw.circle(surface, (240, 220, 135), (round(x + (target_x - x) * shot), round(y)), 2)
        result = battle["result"]
        kda = '/'.join(str(round(result[key] * progress)) for key in ('kills', 'deaths', 'assists'))
        draw_fitted_text(surface, f"{GODS[result['god']][0]} · {kda} · partida automática", pygame.Rect(58, 223, 364, 19), self.font, COLOR_AMBER)
        draw.rect(surface, (35, 45, 65), (62, 246, 356, 6))
        draw.rect(surface, COLOR_CYAN, (62, 246, round(356 * progress), 6))
        draw_fitted_text(surface, "Puedes cerrar el teléfono y continuar con SQL", pygame.Rect(58, 257, 364, 16), self.small, COLOR_WHITE, padding=1)
