"""Una sola entrada para consultar los atajos de la pantalla actual"""
import pygame
from game.rendering import Canvas,draw,make_font
from game.visuals import panel, button, centered, MINT, GOLD, MUTED

GUIDES={
 'Menú':[('Arriba / Abajo','Elegir opción'),('Enter / Espacio','Confirmar'),('Esc','Cancelar una nueva partida')],
 'Introducción':[('Enter / Espacio / Der.','Continuar'),('Esc','Saltar la introducción')],
 'Personaje':[('Arriba / Abajo','Elegir un detalle'),('Izq / Der','Cambiar su aspecto'),('Enter','Editar nombre o confirmar'),('R','Girar el personaje')],
 'Aula':[('WASD / Flechas','Caminar'),('E / Enter / Espacio','Hablar o usar el computador'),('N','Cuaderno'),('F4 / P','Teléfono'),('M','Taller de modelamiento'),('C','Personalizar personaje'),('O / F2 / Esc','Ajustes'),('Q','Guardar y salir')],
 'Taller introductorio':[('WASD / Flechas','Caminar'),('E / Enter / Espacio / Clic','Hablar o usar el computador'),('N / F1','Cuaderno'),('M','Modelador desde el día 2'),('F4','Teléfono'),('O','Ajustes'),('Esc','Pausa, guardar u omitir taller')],
 'Clase':[('Espacio / Enter / Der. / Clic','Completar pizarra o avanzar'),('Izq.','Volver a la diapositiva anterior'),('F7','Activar o desactivar la voz introductoria'),('F8','Repetir la voz introductoria'),('O','Ajustes en la clase introductoria'),('Esc','Salir de la explicación')],
 'Conversación':[('Espacio / Enter / E / Esc','Continuar la conversación')],
 'SQL':[('Enter / Tab','Nueva línea / sangría'),('Ctrl+Enter / F5','Ejecutar o probar sin nota'),('Ctrl+Shift+Enter','Entregar respuesta del examen'),('F1 / F2 / F3 / F6','Apuntes / tablas / pistas / resultados'),('Flechas / Inicio / Fin','Mover el cursor, mantener para repetir'),('Ctrl+Izq / Der / Shift','Mover por palabras / seleccionar'),('Ctrl+A / C / X / V','Seleccionar / copiar / cortar / pegar'),('PgUp / PgDn','Historial de consultas'),('Esc','Salir del computador')],
 'Catálogo SQL':[('1–9 / Izq / Der','Cambiar de tabla'),('F2 / Enter / Espacio','Volver a la terminal'),('Esc','Salir del computador'),('F6','Resultado completo')],
 'Modelador':[('Rueda','Acercar o alejar'),('Arrastrar fondo','Desplazar el lienzo'),('Arrastrar entidad','Mover una entidad'),('Clic en entidad / relación','Abrir sus propiedades'),('Ctrl+Z','Deshacer'),('Esc','Cerrar propiedades o volver a sala')],
 'Kashut':[('1 / 2 / 3 / 4 / Clic','Responder'),('Enter','Continuar o revisar respuestas'),('R','Repetir desde el podio'),('Esc','Pausar o volver a la sala')],
 'Cuaderno':[('Izq / Der / Clic en < >','Cambiar de página'),('Ctrl+F','Buscar palabras'),('Enter','Escribir en Mis notas'),('Esc','Terminar de escribir o cerrar'),('N / F1','Cerrar el cuaderno')],
 'Teléfono':[('1 / 2 / Tab','Partida o aumentos'),('Arriba / Abajo / Clic','Elegir aumento'),('Izq / Der / S','Cambiar dios / estrategia'),('Enter','Buscar partida o comprar aumento'),('Esc / P / F4','Cerrar el teléfono')],
 'Ajustes':[('Arriba / Abajo','Elegir ajuste'),('Izq / Der','Cambiar su valor'),('Enter / Espacio','Activar opción'),('Esc','Volver al juego')],
}


class ControlsOverlay:
    rect=pygame.Rect(396,283,77,14)

    def __init__(self):
        self.active=False
        self.context='Menú'
        self.background=Canvas((480,300))
        self.font=make_font(13);self.small=make_font(11);self.title=make_font(20)

    def handle_event(self,event,context,surface):
        toggle=event.type==pygame.KEYDOWN and event.key==pygame.K_F10
        click=event.type==pygame.MOUSEBUTTONDOWN and event.button==1 and self.rect.collidepoint(event.pos)
        if toggle or click:
            if not self.active:
                pygame.Surface.blit(self.background,surface,(0,0))
                self.context=context
            self.active=not self.active
            return True
        if self.active:
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:self.active=False
            return True
        return False

    def draw_button(self,surface):
        button(surface,'Controles · F10',self.rect,self.small,selected=self.active,accent=MINT)

    def draw(self,surface):
        pygame.Surface.blit(surface,self.background,(0,0))
        dim=pygame.Surface((480,300),pygame.SRCALPHA);dim.fill((5,12,23,215));surface.blit(dim,(0,0))
        panel(surface,pygame.Rect(40,21,400,254),(18,32,46),MINT)
        centered(surface,'Controles',pygame.Rect(54,32,372,24),self.title,GOLD)
        centered(surface,self.context,pygame.Rect(54,59,372,15),self.font,MUTED)
        for i,(key,description) in enumerate(GUIDES[self.context]):
            y=83+i*18
            if i%2==0:draw.rect(surface,(23,40,53),(52,y-2,376,18),border_radius=2)
            surface.blit(self.small.render(key,True,MINT),(60,y+1))
            surface.blit(self.small.render(description,True,(224,232,229)),(199,y+1))
        centered(surface,'F10 o Esc para volver',pygame.Rect(60,252,360,14),self.small,MUTED)
        self.draw_button(surface)
