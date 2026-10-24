import pygame
from game.constants import *

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

        # Paletas de colores dinámicas
        skin_tones = [
            (255, 205, 148), # Claro
            (230, 175, 125), # Trigueño
            (185, 125, 80),  # Moreno
            (115, 75, 50)    # Ébano
        ]

        hair_colors = [
            (80, 45, 25),    # Castaño
            (30, 25, 25),    # Negro
            (240, 210, 80),  # Rubio
            (200, 75, 30),   # Pelirojo
            (0, 229, 255)    # Cyan Cyber
        ]

        shirt_colors = [
            (30, 144, 255),  # Azul Hacker
            (220, 50, 50),   # Rojo Carmesí
            (36, 180, 100),  # Verde Terminal
            (35, 40, 50),    # Negro Cyber
            (150, 60, 200)   # Púrpura Mágico
        ]

        skin_idx = self.custom_data.get("skin_tone", 0) % len(skin_tones)
        hair_idx = self.custom_data.get("hair_color", 0) % len(hair_colors)
        shirt_idx = self.custom_data.get("shirt_color", 0) % len(shirt_colors)
        style = self.custom_data.get("hair_style", 0)

        c_skin = skin_tones[skin_idx]
        c_skin_shadow = (int(c_skin[0] * 0.8), int(c_skin[1] * 0.8), int(c_skin[2] * 0.8))
        c_hair = hair_colors[hair_idx]
        c_shirt = shirt_colors[shirt_idx]
        c_pants = (40, 50, 75)
        c_shoes = (30, 25, 20)
        c_backpack = (220, 90, 40)

        for direction in ["down", "up", "left", "right"]:
            sprites[direction] = []
            for frame in [0, 1, 2, 3]:
                surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                
                # Sombra
                pygame.draw.ellipse(surf, (15, 20, 30, 100), (2, 17, 12, 3))

                if direction == "down":
                    # Cabello
                    if style == 0: # Corto
                        pygame.draw.rect(surf, c_hair, (4, 1, 8, 4))
                        pygame.draw.rect(surf, c_hair, (3, 3, 2, 3))
                        pygame.draw.rect(surf, c_hair, (11, 3, 2, 3))
                    elif style == 1: # Largo / Coleta
                        pygame.draw.rect(surf, c_hair, (3, 1, 10, 4))
                        pygame.draw.rect(surf, c_hair, (2, 4, 3, 7))
                        pygame.draw.rect(surf, c_hair, (11, 4, 3, 7))
                    else: # Despeinado
                        pygame.draw.rect(surf, c_hair, (3, 0, 10, 5))
                        pygame.draw.rect(surf, c_hair, (5, 0, 6, 2))
                    
                    # Cara y ojos
                    pygame.draw.rect(surf, c_skin, (4, 4, 8, 5))
                    pygame.draw.rect(surf, (20, 25, 35), (5, 6, 2, 2))
                    pygame.draw.rect(surf, (20, 25, 35), (9, 6, 2, 2))
                    
                    # Camiseta y mochila
                    pygame.draw.rect(surf, c_shirt, (4, 9, 8, 6))
                    pygame.draw.rect(surf, c_backpack, (3, 9, 1, 6))
                    pygame.draw.rect(surf, c_backpack, (12, 9, 1, 6))
                    
                    # Pantalón y zapatos con animación de pasos
                    pygame.draw.rect(surf, c_pants, (4, 15, 3, 3 + (1 if frame == 1 else 0)))
                    pygame.draw.rect(surf, c_pants, (9, 15, 3, 3 + (1 if frame == 3 else 0)))
                    pygame.draw.rect(surf, c_shoes, (4, 17 + (1 if frame == 1 else 0), 3, 2))
                    pygame.draw.rect(surf, c_shoes, (9, 17 + (1 if frame == 3 else 0), 3, 2))

                elif direction == "up":
                    pygame.draw.rect(surf, c_hair, (3, 1, 10, 7))
                    if style == 1:
                        pygame.draw.rect(surf, c_hair, (6, 7, 4, 4)) # Coleta atrás
                    pygame.draw.rect(surf, c_skin_shadow, (6, 8, 4, 1))
                    pygame.draw.rect(surf, c_shirt, (4, 9, 8, 5))
                    pygame.draw.rect(surf, c_backpack, (4, 9, 8, 6))
                    pygame.draw.rect(surf, (180, 70, 30), (5, 11, 6, 3))
                    pygame.draw.rect(surf, c_pants, (4, 15, 3, 3 + (1 if frame == 1 else 0)))
                    pygame.draw.rect(surf, c_pants, (9, 15, 3, 3 + (1 if frame == 3 else 0)))
                    pygame.draw.rect(surf, c_shoes, (4, 17 + (1 if frame == 1 else 0), 3, 2))
                    pygame.draw.rect(surf, c_shoes, (9, 17 + (1 if frame == 3 else 0), 3, 2))

                elif direction == "left":
                    pygame.draw.rect(surf, c_hair, (4, 1, 8, 5))
                    pygame.draw.rect(surf, c_skin, (3, 4, 6, 5))
                    pygame.draw.rect(surf, (20, 25, 35), (4, 6, 2, 2))
                    pygame.draw.rect(surf, c_shirt, (5, 9, 6, 6))
                    pygame.draw.rect(surf, c_backpack, (10, 8, 3, 7))
                    if frame in [1, 2]:
                        pygame.draw.rect(surf, c_pants, (3, 15, 4, 3))
                        pygame.draw.rect(surf, c_pants, (7, 14, 4, 3))
                        pygame.draw.rect(surf, c_shoes, (2, 17, 4, 2))
                        pygame.draw.rect(surf, c_shoes, (8, 16, 4, 2))
                    else:
                        pygame.draw.rect(surf, c_pants, (5, 15, 5, 3))
                        pygame.draw.rect(surf, c_shoes, (4, 17, 5, 2))

                elif direction == "right":
                    pygame.draw.rect(surf, c_hair, (4, 1, 8, 5))
                    pygame.draw.rect(surf, c_skin, (7, 4, 6, 5))
                    pygame.draw.rect(surf, (20, 25, 35), (10, 6, 2, 2))
                    pygame.draw.rect(surf, c_shirt, (5, 9, 6, 6))
                    pygame.draw.rect(surf, c_backpack, (3, 8, 3, 7))
                    if frame in [1, 2]:
                        pygame.draw.rect(surf, c_pants, (9, 15, 4, 3))
                        pygame.draw.rect(surf, c_pants, (5, 14, 4, 3))
                        pygame.draw.rect(surf, c_shoes, (10, 17, 4, 2))
                        pygame.draw.rect(surf, c_shoes, (4, 16, 4, 2))
                    else:
                        pygame.draw.rect(surf, c_pants, (6, 15, 5, 3))
                        pygame.draw.rect(surf, c_shoes, (7, 17, 5, 2))

                sprites[direction].append(surf)
        return sprites

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
