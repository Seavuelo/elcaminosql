from game.visuals import panel, centered, backdrop, GOLD, MINT, MUTED, EMERALD, button
import pygame
from game.rendering import draw, make_font
from game.constants import *
from game.appearance import *
from game.player import Player
from game.ui_helpers import draw_panel, render_wrapped_text, draw_fitted_text


class CharacterCustomizer:
    """Editor con lista desplazable y el mismo sprite que se utiliza al jugar."""
    OPTIONS = {
        "skin_tone": ("Piel", SKIN_TONES),
        "hair_color": ("Cabello", HAIR_COLORS),
        "hair_style": ("Peinado", HAIR_STYLES),
        "shirt_color": ("Color de ropa", SHIRT_COLORS),
        "eye_color": ("Ojos", EYE_COLORS),
        "pants_color": ("Pantalón", PANTS_COLORS),
        "shoe_color": ("Color zapatos", SHOE_COLORS),
        "clothing_style": ("Vestuario", CLOTHING_STYLES),
        "shoe_style": ("Calzado", SHOE_STYLES),
        "backpack_color": ("Mochila", BACKPACK_COLORS),
    }

    def __init__(self, audio_manager, on_finish_callback):
        self.audio = audio_manager
        self.on_finish_callback = on_finish_callback
        self.active = False
        self.font_title = make_font(18)
        self.font_field = make_font(16)
        self.font_hint = make_font(13)
        self.player_name = "Alex"
        self.typing_name = False
        self.genders = [("Masculino", "male"), ("Femenino", "female"), ("Neutro", "neutral")]
        self.gender_idx = 0
        self.values = {key: 0 for key in CUSTOM_FIELDS}
        self.fields = ["name", "gender", *CUSTOM_FIELDS, "confirm"]
        self.selected_field = 0
        self.preview_direction = "down"
        self.preview = None
        self.repeat_key=None
        self.repeat_elapsed=0
        self.hit_fields=[]

    def _data(self):
        return {"name": self.player_name.strip() or "Novato",
                "gender": self.genders[self.gender_idx][1], **self.values}

    def _refresh_preview(self):
        self.preview = Player(0, 0, self._data())

    def open(self, data=None):
        self.active = True
        self.selected_field = 0
        self.typing_name = False
        self.repeat_key=None
        if data:
            self.player_name = data.get("player_name", "Alex")
            self.gender_idx = next((i for i, entry in enumerate(self.genders)
                                    if entry[1] == data.get("gender")), 0)
            self.values = {key: data.get(key, 0) % len(self.OPTIONS[key][1]) for key in CUSTOM_FIELDS}
        self._refresh_preview()

    def confirm(self):
        self.active=False
        self.repeat_key=None
        self.audio.play_success()
        self.on_finish_callback(self._data())

    def update(self,dt,enabled=True):
        if not enabled or not self.active:
            self.repeat_key=None
            return
        if self.repeat_key is not None:
            self.repeat_elapsed+=dt
            while self.repeat_elapsed>=0:
                self.repeat_elapsed-=.065
                self.handle_event(pygame.event.Event(pygame.KEYDOWN,key=self.repeat_key,unicode=''))

    def handle_event(self, event):
        if not self.active:return False
        if event.type==pygame.WINDOWFOCUSLOST or event.type==pygame.KEYUP and event.key==self.repeat_key:
            self.repeat_key=None
            return False
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if pygame.Rect(150,248,306,28).collidepoint(event.pos):self.confirm();return True
            for rect,index in self.hit_fields:
                if rect.collidepoint(event.pos):
                    self.selected_field=index
                    self.typing_name=self.fields[index]=='name'
                    if not self.typing_name and event.pos[0]>=278:
                        self.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RIGHT,unicode=''))
                        self.repeat_key=None
                    return True
        if event.type!=pygame.KEYDOWN:return False
        if event.key in (pygame.K_UP,pygame.K_DOWN,pygame.K_LEFT,pygame.K_RIGHT) and event.key!=self.repeat_key:
            self.repeat_key=event.key
            self.repeat_elapsed=-.32
        field = self.fields[self.selected_field]
        if field == "name" and self.typing_name:
            if event.key == pygame.K_RETURN:
                self.typing_name = False
            elif event.key == pygame.K_BACKSPACE:
                self.player_name = self.player_name[:-1]
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                self.typing_name = False
            elif len(self.player_name) < 14 and (event.unicode.isalnum() or event.unicode == " "):
                self.player_name += event.unicode
            else:
                return True
            if self.typing_name or event.key == pygame.K_RETURN:
                return True
        if event.key in (pygame.K_UP, pygame.K_DOWN):
            self.selected_field = (self.selected_field + (1 if event.key == pygame.K_DOWN else -1)) % len(self.fields)
        elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
            delta = 1 if event.key == pygame.K_RIGHT else -1
            if field == "gender":
                self.gender_idx = (self.gender_idx + delta) % len(self.genders)
            elif field in self.OPTIONS:
                self.values[field] = (self.values[field] + delta) % len(self.OPTIONS[field][1])
                self._refresh_preview()
        elif event.key == pygame.K_r:
            directions = ["down", "left", "up", "right"]
            self.preview_direction = directions[(directions.index(self.preview_direction) + 1) % 4]
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            if field == "name":
                self.typing_name = not self.typing_name
            elif field == "confirm":
                self.confirm()
        else:
            return False
        self.audio.play_key()
        return True

    def draw(self, surface, tick):
        if not self.active:
            return
        backdrop(surface)
        draw_panel(surface, pygame.Rect(12, 10, 456, 280), title="PERSONALIZA TU ESTUDIANTE", font=self.font_title)
        panel(surface,pygame.Rect(24,40,116,213),(27,45,56),GOLD)
        for yy in range(49,173,12):draw.line(surface,(35,56,64),(29,yy),(134,yy))
        draw.ellipse(surface,(17,31,42),(39,156,86,11))
        sprite = self.preview.sprites[self.preview_direction][(tick // 16) % 4]
        surface.blit(pygame.transform.scale(sprite, (80, 100)), (42, 67))
        centered(surface,self.player_name or '...',pygame.Rect(28,176,108,28),self.font_field,GOLD,padding=0)
        centered(surface,'Vista del juego',pygame.Rect(28,210,108,17),self.font_hint,MUTED,padding=0)
        centered(surface,'R para rotar',pygame.Rect(28,230,108,14),self.font_hint,MINT,padding=0)
        edit_fields=self.fields[:-1]
        start=min(max(0,min(self.selected_field,len(edit_fields)-1)-5),max(0,len(edit_fields)-7))
        self.hit_fields=[]
        for row,field in enumerate(edit_fields[start:start+7]):
            index=start+row
            rect=pygame.Rect(150,40+row*28,306,25)
            selected=index==self.selected_field
            panel(surface,rect,(31,51,64) if selected else (21,35,48),GOLD if selected else MINT,shadow=False,selected=selected)
            draw.rect(surface,(16,29,40),(rect.x+2,rect.y+2,123,rect.height-4),border_radius=2)
            draw.line(surface,(70,97,107),(rect.x+126,rect.y+4),(rect.x+126,rect.bottom-4))
            if field=='name':label,value='Nombre',self.player_name+(' |' if self.typing_name else '')
            elif field=='gender':label,value='Identidad',self.genders[self.gender_idx][0]
            else:
                label,options=self.OPTIONS[field]
                value=options[self.values[field]]
                value=value[0] if isinstance(value,tuple) else value
            draw_fitted_text(surface,label,pygame.Rect(rect.x+8,rect.y+2,111,21),self.font_hint,MUTED,padding=0)
            centered(surface,str(value),pygame.Rect(rect.x+134,rect.y+2,164,21),self.font_field,GOLD if selected else (232,239,237),padding=0)
            self.hit_fields.append((rect,index))
        button(surface,'Confirmar estudiante',pygame.Rect(150,248,306,28),self.font_field,selected=self.fields[self.selected_field]=='confirm',accent=EMERALD,fill=(18,57,39),icon='check')
