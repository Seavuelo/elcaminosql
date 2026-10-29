import pygame
from game.rendering import draw, make_font
from game.constants import *
from game.appearance import *

class Player:
    def __init__(self, x, y, custom_data=None):
        self.x = float(x)
        self.y = float(y)
        self.width = 16
        self.height = 20
        self.speed = 2.2
        self.direction = "down"
        self.moving = False
        self.anim_timer = 0
        self.anim_frame = 0
        self.custom_data = custom_data or {}
        self.sprites = self._generate_sprites()

    def update_customization(self, custom_data):
        self.custom_data = custom_data
        self.sprites = self._generate_sprites()

    def _generate_sprites(self):
        sprites = {}

        def color(key, palette):
            return palette[self.custom_data.get(key, 0) % len(palette)][1]

        c_skin = color("skin_tone", SKIN_TONES)
        c_skin_shadow = tuple(int(c * 0.8) for c in c_skin)
        c_hair = color("hair_color", HAIR_COLORS)
        c_shirt = color("shirt_color", SHIRT_COLORS)
        c_pants = color("pants_color", PANTS_COLORS)
        c_shoes = color("shoe_color", SHOE_COLORS)
        c_backpack = color("backpack_color", BACKPACK_COLORS)
        c_eyes = color("eye_color", EYE_COLORS)
        style = self.custom_data.get("hair_style", 0)
        outfit = self.custom_data.get("clothing_style", 0)
        dark_shirt = tuple(int(c * 0.6) for c in c_shirt)

        for direction in ("down", "up", "left", "right"):
            sprites[direction] = []
            for frame in range(4):
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                draw.ellipse(surf, (15, 20, 30, 100), (2, 17, 12, 3))
                left_step = 1 if frame == 1 else 0
                right_step = 1 if frame == 3 else 0
                if direction in ('left','right'):
                    sign=1 if direction=='right' else -1
                    stride=sign*(right_step-left_step)*2
                    for ankle,color in ((7+stride,tuple(int(c*.65) for c in c_pants)),(8-stride,c_pants)):
                        draw.line(surf,color,(8,14),(ankle,17),3)
                        draw.rect(surf,c_shoes,(ankle-1 if sign>0 else ankle-3,17,5,2))
                        if self.custom_data.get('shoe_style',0)==1:draw.rect(surf,c_shoes,(ankle-1,16,3,2))
                else:
                    draw.rect(surf, c_pants, (4, 14, 3, 4 + left_step))
                    draw.rect(surf, c_pants, (9, 14, 3, 4 + right_step))
                    draw.rect(surf, c_shoes, (3, 17 + left_step, 4, 2))
                    draw.rect(surf, c_shoes, (9, 17 + right_step, 4, 2))
                if self.custom_data.get("shoe_style", 0) == 1 and direction in ('up','down'):
                    draw.rect(surf, c_shoes, (4, 16, 3, 2))
                    draw.rect(surf, c_shoes, (9, 16, 3, 2))
                draw.rect(surf, c_shirt, (4, 9, 8, 6))
                if direction in ("up", "down"):
                    for x, step in ((2, right_step), (12, left_step)):
                        draw.rect(surf, c_shirt, (x, 9 + step, 2, 4))
                        draw.rect(surf, c_skin, (x, 13 + step, 2, 2))
                    draw.rect(surf, c_skin, (4, 3, 8, 6))
                    if direction == "down":
                        draw.rect(surf, c_backpack, (4, 9, 1, 5))
                        draw.rect(surf, c_backpack, (11, 9, 1, 5))
                        draw.rect(surf, c_eyes, (5, 6, 2, 2))
                        draw.rect(surf, c_eyes, (9, 6, 2, 2))
                        draw.line(surf, c_skin_shadow, (7, 8), (8, 8))
                    else:
                        draw.rect(surf, c_backpack, (4, 10, 8, 5))
                        draw.rect(surf, tuple(int(c * 0.7) for c in c_backpack), (5, 12, 6, 2))
                else:
                    facing_right = direction == "right"
                    draw.rect(surf, c_skin, (7 if facing_right else 3, 3, 6, 6))
                    draw.rect(surf, c_eyes, (10 if facing_right else 4, 6, 2, 2))
                    draw.rect(surf, c_backpack, (3 if facing_right else 11, 9, 2, 6))
                    arm_x = 9 if facing_right else 5
                    swing = right_step - left_step
                    draw.rect(surf, dark_shirt, (arm_x - 1, 9, 3, 4))
                    draw.rect(surf, c_shirt, (arm_x, 9 + swing, 2, 4))
                    draw.rect(surf, c_skin, (arm_x, 13 + swing, 3, 2))
                if outfit==6:
                    arms=((2,right_step),(12,left_step)) if direction in ('up','down') else ((arm_x,swing),)
                    for x,step in arms:
                        draw.rect(surf,c_shirt,(x,12+step,2,3))
                        draw.rect(surf,c_skin,(x,15+step,2,1))
                if direction != "up":
                    if outfit == 1:
                        draw.rect(surf, dark_shirt, (6, 9, 4, 2))
                        draw.line(surf, (230, 225, 210), (7, 11), (7, 12))
                    elif outfit == 2:
                        draw.rect(surf, (225, 225, 215), (7, 10, 2, 5))
                        draw.rect(surf, dark_shirt, (5, 9, 2, 6))
                    elif outfit == 3:
                        for sy in (10, 12, 14):
                            draw.line(surf, dark_shirt, (5, sy), (10, sy))
                    elif outfit==4:
                        draw.line(surf,(230,225,210),(8,10),(8,14))
                        for sy in (11,13):surf.set_at((9,sy),dark_shirt)
                        draw.polygon(surf,(230,225,210),[(5,9),(8,11),(10,9)])
                    elif outfit==5:
                        draw.polygon(surf,(225,219,197),[(6,9),(9,9),(8,13)])
                        draw.line(surf,dark_shirt,(8,12),(8,14))
                    elif outfit==6:
                        draw.line(surf,dark_shirt,(5,14),(10,14))
                    elif outfit==7:
                        draw.rect(surf,(222,219,205),(7,10,2,5))
                        draw.line(surf,dark_shirt,(6,9),(6,14))
                        draw.line(surf,dark_shirt,(10,9),(10,14))
                self._draw_hair(surf, direction, style, c_hair)
                # Reflejos mínimos que conservan la silueta y los colores elegidos
                for hx,hy in ((5,2),(6,2),(10,3)):
                    if surf.get_at((hx,hy))[:3]==c_hair:
                        surf.set_at((hx,hy),tuple(min(255,int(v*1.15)+8) for v in c_hair))
                for sx in (5,6):
                    if surf.get_at((sx,10))[:3]==c_shirt:
                        surf.set_at((sx,10),tuple(min(255,int(v*1.12)+5) for v in c_shirt))
                draw.rect(surf,tuple(int(v*.65) for v in c_pants),(4,15,1,2))
                sprites[direction].append(surf)
        return sprites

    @staticmethod
    def _draw_hair(surface, direction, style, color):
        if direction == "up":
            height = 12 if style == 1 else (4 if style == 3 else 7)
            draw.rect(surface, color, (3, 1, 10, height))
        elif direction == "down":
            draw.rect(surface, color, (3, 1 if style != 3 else 2, 10, 3 if style != 3 else 2))
            if style != 3:
                draw.rect(surface, color, (3, 3, 2, 3))
                draw.rect(surface, color, (11, 3, 2, 3))
            if style == 1:
                draw.rect(surface, color, (2, 3, 2, 10))
                draw.rect(surface, color, (12, 3, 2, 10))
        else:
            right = direction == "right"
            back_x = 3 if right else 9
            draw.rect(surface, color, (3, 1 if style != 3 else 2, 10, 4 if style != 3 else 2))
            draw.rect(surface, color, (back_x, 3, 4, 11 if style == 1 else 6))
            if style != 3:
                draw.rect(surface, color, (7 if right else 6, 3, 3, 3))
                draw.rect(surface,color,(7 if right else 7,6,2,2))
        if style == 2:
            draw.polygon(surface, color, [(3, 3), (4, 0), (6, 2), (8, 0), (10, 2), (12, 1), (12, 4)])
        elif style == 4:
            for hx in (4, 7, 10):
                draw.circle(surface, color, (hx, 2), 2)
            if direction in ("left", "right"):
                draw.circle(surface, color, (4 if direction == "right" else 11, 6), 2)

    def update(self, keys, colliders):
        dx, dy = 0, 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= self.speed
            self.direction = "left"
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += self.speed
            self.direction = "right"
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy -= self.speed
            self.direction = "up"
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy += self.speed
            self.direction = "down"

        if dx != 0 and dy != 0:
            dx *= 0.7071
            dy *= 0.7071

        self.moving = (dx != 0 or dy != 0)

        new_rect_x = pygame.Rect(int(self.x + dx), int(self.y), self.width, self.height)
        collision_x = False
        for c in colliders:
            if new_rect_x.colliderect(c):
                collision_x = True
                break
        if not collision_x:
            self.x += dx

        new_rect_y = pygame.Rect(int(self.x), int(self.y + dy), self.width, self.height)
        collision_y = False
        for c in colliders:
            if new_rect_y.colliderect(c):
                collision_y = True
                break
        if not collision_y:
            self.y += dy

        if self.moving:
            self.anim_timer += 1
            if self.anim_timer >= 8:
                self.anim_timer = 0
                self.anim_frame = (self.anim_frame + 1) % 4
        else:
            self.anim_frame = 0

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        current_sprite = self.sprites[self.direction][self.anim_frame]
        surface.blit(current_sprite, (int(self.x), int(self.y)))
