"""Carta de bienvenida que se muestra una sola vez por perfil"""
import pygame
from game.rendering import draw,make_font
from game.ui_helpers import paginate_text,render_wrapped_text,draw_fitted_text
from game.visuals import panel,button,PAPER,INK,GOLD

TEXT = ('¡Hola! Soy Sebastián Flores y soy el creador de este juego, gracias por darte el tiempo de probarlo, espero que te ayude a reforzar ideas que sabías o a aprender algo nuevo\n\n'
'Hice este juego con bastante cariño, esmerándome en que sirva para aprender, con un enfoque a futuro en el mundo laboral, con trabajos reales y cómo se trabaja con datos, tendré que hacer una extensa búsqueda, ya que yo también voy entrando al mundo laboral\n\n'
'Cualquier comentario sobre el juego, estoy más que abierto a recibirlo\n\n'
'El modo del teléfono, "Liga de Dioses", es un pequeño minijuego para hacer algo con la experiencia que vas ganando en clases, es 0% obligatorio y puedes enfocarte solo en aprender y practicar\n\n'
'Quise hacer un guiño a esas clases que, aunque te encanten y la materia esté muy buena, ya no te da para concentrarte un segundo más y necesitas hacer algo en segundo plano, simplemente es un detallito\n\n'
'Espero que les guste, gracias por jugar')


class CreatorNote:
    def __init__(self,config):
        self.config=config
        self.active=not config.get('creator_note_seen',False)
        self.font=make_font(15)
        self.title=make_font(22)
        self.pages=paginate_text(TEXT,self.font,352,166,3)
        self.index=0
        self.close_rect=pygame.Rect(41,24,20,20)

    def close(self):
        self.active=False
        self.config.set('creator_note_seen',True)

    def next(self):
        if self.index+1<len(self.pages):self.index+=1
        else:self.close()

    def handle_event(self,event):
        if not self.active:return False
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:self.close()
            elif event.key in (pygame.K_RETURN,pygame.K_SPACE,pygame.K_RIGHT):self.next()
            elif event.key==pygame.K_LEFT:self.index=max(0,self.index-1)
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.close_rect.collidepoint(event.pos):self.close()
            elif pygame.Rect(291,250,127,26).collidepoint(event.pos):self.next()
            elif pygame.Rect(63,250,105,26).collidepoint(event.pos):self.index=max(0,self.index-1)
        return True

    def draw(self,surface):
        veil=pygame.Surface((480,300),pygame.SRCALPHA);veil.fill((6,13,23,215));surface.blit(veil,(0,0))
        panel(surface,pygame.Rect(32,18,416,269),(95,77,54),GOLD)
        draw.rect(surface,PAPER,(38,24,404,256),border_radius=3)
        for y in range(82,244,18):draw.line(surface,(221,212,190),(62,y),(423,y))
        draw.line(surface,(212,156,143),(57,51),(57,241))
        for y in range(61,240,24):draw.circle(surface,(111,98,78),(39,y),2)
        draw_fitted_text(surface,'Una nota del creador',pygame.Rect(76,33,342,26),self.title,(78,64,45),padding=0)
        button(surface,'X',self.close_rect,make_font(15),accent=(161,84,71),light=True)
        render_wrapped_text(surface,self.pages[self.index],pygame.Rect(63,70,352,166),self.font,(43,58,63),padding=0,line_spacing=3)
        if self.index:button(surface,'Anterior',pygame.Rect(63,250,105,26),make_font(13),accent=(91,114,101),light=True)
        draw_fitted_text(surface,f'{self.index+1}/{len(self.pages)}',pygame.Rect(191,252,76,21),make_font(13),(103,105,82),padding=0)
        button(surface,'Siguiente' if self.index+1<len(self.pages) else 'A jugar',pygame.Rect(291,250,127,26),make_font(14),accent=(84,123,107),light=True)
