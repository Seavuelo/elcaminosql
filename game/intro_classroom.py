from game.visuals import intro_room, desk, monitor_details, panel, button, backdrop, centered, GOLD, MINT, marco_sprite
"""Aula optativa con Marco, Moshi, pizarra y Kashut desde el PC"""
from copy import deepcopy
import math
import pygame
from game.data_model import DEFAULT_FOUNDATION
from game.logical_model import LogicalDesign
from game.design_studio import DesignStudio
from game.foundations_content import DAYS
from game.kashut import Kashut
from game.player import Player
from game.world import Classmate
from game.moshi import create_moshi
from game.dialog import DialogBox
from game.lecture import LectureScene
from game.rendering import draw,make_font
from game.ui_helpers import draw_fitted_text,paginate_text
from game.intro_boards import board_for
from game.intro_peers import create_intro_peers,speech_for,DESKS
from game.intro_voice_scripts import attach_voice_scripts

MOSHI_BEFORE={
1:'Vine a la clase opcional porque prefiero preguntar qué es una tabla aquí y no el primer día con cuarenta personas mirando, igual si preguntan digo que vine a acompañarte',
2:'Al teléfono le pondría texto, tiene números pero no voy a sumar mi número con el tuyo, eso ya sería una forma muy rara de pedir el contacto',
3:'Dos personas pueden llamarse Moshi, pero con el mismo ID no pasan, por fin una sala donde ser única viene con explicación',
4:'Un estudiante puede tener varias tutorías, eso es uno a muchos, yo con las dudas ya voy en muchos a demasiados',
5:'Hoy toca comprobar que el modelo también rechace cosas, me encanta cuando un error es exactamente lo que el profe quería ver',
}
MOSHI_AFTER={
1:'SQL es lo que pides y SQLite el que hace la pega, ya entendí, yo también necesito a alguien que haga la pega mientras digo lo que quiero',
2:'VARCHAR para texto, NUMERIC para números y DATE para fechas, me falta un tipo para guardar el hambre, porque eso ya ocupa demasiado espacio',
3:'UID identifica y obligatorio exige un valor, mi desayuno debería ser obligatorio, pero todos los días aparece NULL',
4:'La identificadora pasa la clave a la clave del hijo, no todos los datos, menos mal, imagina heredar también las deudas',
5:'Quedó bonito el modelo, si algo falla después digo que lo hicimos entre dos, si funciona digo que te enseñé yo, mentira, vamos por un completo',
}


class FoundationsScene:
    def __init__(self,save,audio):
        self.save,self.audio=save,audio
        self.active=False
        self.font,self.small,self.title=make_font(13),make_font(11),make_font(16)
        self.on_notes=lambda:None
        self.on_settings=lambda:None
        self.buttons=[]

    def open(self,on_finish,on_exit,review=False):
        self.state=self.save.data.setdefault('foundation',deepcopy(DEFAULT_FOUNDATION))
        for key,value in DEFAULT_FOUNDATION.items(): self.state.setdefault(key,deepcopy(value))
        self.state.setdefault('lectures',{})
        self.state.setdefault('lecture_pages',{})
        self.review=review
        self.on_finish,self.on_exit=on_finish,on_exit
        self.day=1 if review else max(1,min(5,self.state['day']))
        self.mode='studio' if review else 'room'
        self.active=True
        self.tick=0
        self.day_intro_remaining=0 if review else 2.0
        self.design=LogicalDesign(self.state.get('logical_model'),self.state.get('tables'))
        self.modeler=DesignStudio(self.design,self.save_design,lambda:self.on_notes(),self.task if not review else None,self.save_test)
        self.player=Player(210,228,self.save.data)
        self.moshi=create_moshi(Classmate)
        self.moshi.desk_x,self.moshi.desk_y=280,197
        self.moshi.px,self.moshi.py=301,208
        self.moshi.reset_day()
        self.peers=create_intro_peers(Classmate)
        self.dialog=DialogBox(self.audio)
        self.lecture=LectureScene(self.audio,self.save)
        self.kashut=Kashut(self.save,self.audio,lambda:setattr(self,'mode','room'))
        self.desks=[(130,197,self.save.data.get('player_name','Estudiante'),None),(280,197,'Moshi',self.moshi)]+[(x,y,p.name,p) for (x,y),p in zip(DESKS,self.peers)]
        self.colliders=[pygame.Rect(78,30,324,25),pygame.Rect(78,30,8,228),pygame.Rect(394,30,8,228),pygame.Rect(78,250,324,8),pygame.Rect(215,96,58,20)]+[pygame.Rect(x,y,65,27) for x,y,_,_ in self.desks]

    def save_design(self,data):
        self.state['logical_model']=deepcopy(data)
        self.save.save()

    def save_test(self,passed):
        self.state['tested_sql']=self.design.statements() if passed else []
        self.save.save()

    def persist(self):
        if self.mode=='kashut': self.kashut.persist()
        if self.mode=='lecture': self.state['lecture_pages'][str(self.day)]=self.lecture.slide_index
        self.state['logical_model']=deepcopy(self.design.data)
        self.save.save()

    def task(self):
        return {1:'Hoy solo conceptos y Kashut, no hay tarea de modelamiento',
          2:'Crea ESTUDIANTE con ID numérico, NOMBRE VARCHAR y PROMEDIO numérico, hoy no necesitas una relación',
          3:'Marca ESTUDIANTE.ID como UID primario y NOMBRE como obligatorio',
          4:'Crea TUTORIA con su UID ID y atributo TEMA, une ESTUDIANTE con TUTORIA mediante 1:N, activa pasar UID para crear la FK',
          5:'Convierte a relacional y pulsa Probar en el aula para comprobar datos válidos, PK duplicada, nombre ausente y una FK inexistente'}[self.day]

    def model_goal(self):
        if self.day==1:return True,'Sin tarea de modelamiento hoy'
        student=self.design.entity('ESTUDIANTE')
        attrs={a['name']:a for a in student['attributes']} if student else {}
        if any(key not in attrs for key in ('ID','NOMBRE','PROMEDIO')) or attrs.get('NOMBRE',{}).get('type')!='VARCHAR' or any(attrs.get(k,{}).get('type') not in ('NUMERIC','INTEGER','REAL') for k in ('ID','PROMEDIO')):
            return False,self.task()
        if self.day>=3 and (not attrs['ID'].get('uid') or not attrs['NOMBRE'].get('mandatory')):
            return False,'En ESTUDIANTE marca ID como UID primario y NOMBRE como obligatorio'
        if self.day>=4:
            target=self.design.entity('TUTORIA')
            other={a['name']:a for a in target['attributes']} if target else {}
            if not other.get('ID',{}).get('uid') or other.get('TEMA',{}).get('type')!='VARCHAR' or not any(r['source']=='ESTUDIANTE' and r['target']=='TUTORIA' and r['kind']=='1:N' and r.get('transfer_key') for r in self.design.relations):
                return False,self.task()
        if self.day==5 and self.state['tested_sql']!=self.design.statements():
            return False,'Pulsa Probar modelo desde tu computador, comprueba el diseño actual con datos reales'
        return True,'Taller listo'

    def test_workshop(self):
        from contextlib import closing
        import sqlite3
        try:
            if not self.design.entity('ESTUDIANTE') or not self.design.entity('TUTORIA'):
                raise ValueError('Primero construye las entidades ESTUDIANTE y TUTORIA del taller')
            with closing(self.design.connection()) as conn:
                conn.execute('INSERT INTO ESTUDIANTE(ID,NOMBRE,PROMEDIO) VALUES(1,\'Moshi\',6.8)')
                conn.execute('INSERT INTO TUTORIA(ID,ESTUDIANTE_ID,TEMA) VALUES(1,1,\'Modelo relacional\')')
                conn.execute('INSERT INTO TUTORIA(ID,ESTUDIANTE_ID,TEMA) VALUES(2,1,\'Claves\')')
                checks=[]
                for label,sql in [('PK repetida',"INSERT INTO ESTUDIANTE(ID,NOMBRE,PROMEDIO) VALUES(1,'Otro',5)"),('Nombre obligatorio',"INSERT INTO ESTUDIANTE(ID,NOMBRE,PROMEDIO) VALUES(2,NULL,5)"),('FK inexistente',"INSERT INTO TUTORIA(ID,ESTUDIANTE_ID,TEMA) VALUES(3,999,'Sin dueño')")]:
                    try: conn.execute(sql)
                    except sqlite3.IntegrityError: checks.append(label+': rechazado correctamente')
                    else: raise ValueError(label+' no fue rechazado, revisa las restricciones')
                rows=conn.execute('SELECT ID,ESTUDIANTE_ID,TEMA FROM TUTORIA').fetchall()
            self.save_test(True)
            self.modeler.show('Prueba de datos del taller','Una estudiante y dos tutorías insertadas correctamente\n\n'+str(rows)+'\n\n'+'\n\n'.join(checks))
        except (ValueError,sqlite3.Error) as exc:
            self.modeler.show('Revisa el modelo',str(exc)+'\n\nSi añadiste otros campos obligatorios, también necesitan valores de prueba')
        self.mode='studio'

    def start_lecture(self):
        self.audio.stop_narration()
        self.day_intro_remaining=0
        self.lecture.year=0; self.lecture.day=self.day
        self.lecture.slides=[]
        welcome=[]
        if self.day==1:
            welcome=[dict(title='Bienvenidos al taller',body='Soy el profesor Marco, estas clases son opcionales y sirven para entender bien los fundamentos antes de empezar la carrera\n\nHoy nos acompañan Moshi, Carlos, Sofía y Matías, primero conversaremos sobre las ideas, no tienes que crear tablas el primer día',sql='',columns=[],rows=[])]
        for page in welcome+DAYS[self.day]['pages']:
            speeches=[speech for paragraph in page['body'].split('\n\n') for speech in paginate_text(paragraph,self.lecture.font_body,394,52,2)]
            for index,speech in enumerate(speeches):
                kind,caption=board_for(self.day,page['title'],index)
                slide=dict(title=page['title'],chalk_title=page['title'],chalk_body=caption,turing=speech,code_example=page['sql'])
                if page['sql']:slide['code_focus']=min(index,len(page['sql'].splitlines())-1)
                elif page['columns'] and self.day!=1:slide.update(table_columns=page['columns'],table_rows=page['rows'])
                elif kind:slide.update(illustration=kind,illustration_variant=index)
                self.lecture.slides.append(slide)
        for speech in paginate_text('Ya, vamos a hacer un Kashut, únanse desde su computador a ver si quedan en el podio, lean con calma antes de responder, después repasamos juntos las preguntas que hayan costado',self.lecture.font_body,394,52,2):
            self.lecture.slides.append(dict(title='Vamos a hacer un Kashut',chalk_title='KASHUT | Entra desde tu computador',chalk_body='Entra desde tu PC | Lee la pregunta y elige tu respuesta',turing=speech,code_example='',illustration='welcome'))
        attach_voice_scripts(self.day,self.lecture.slides)
        self.lecture.slide_index=min(self.state['lecture_pages'].get(str(self.day),0),len(self.lecture.slides)-1)
        self.lecture.chalk_char_index=0;self.lecture.chalk_is_done=False
        self.lecture.on_finish_callback=self.after_lecture
        self.lecture.active=True
        self.mode='lecture'

    def after_lecture(self):
        self.audio.stop_narration()
        self.state['lectures'][str(self.day)]=True
        self.state['lecture_pages'].pop(str(self.day),None)
        self.save.save()
        self.mode='room'
        self.dialog.show('Kashut listo','Ya pueden entrar desde sus computadores, cuando terminemos revisamos las preguntas que hayan costado',speaker='Profesor Marco')

    def restart_lecture(self):
        self.state['lecture_pages'].pop(str(self.day),None)
        self.start_lecture()

    def start_kashut(self):
        self.kashut.open(self.day)
        self.mode='kashut'

    def interact_teacher(self):
        if not self.state['lectures'].get(str(self.day)):
            self.start_lecture();return
        record=self.state.get('kashut',{}).get(str(self.day),{})
        if not record.get('complete') or not record.get('reviewed'):
            self.dialog.show('Ahora el Kashut','Entra desde tu computador para responder o revisar la retroalimentación, no necesitas quedar en el podio para seguir aprendiendo',speaker='Profesor Marco');return
        try: valid,message=self.model_goal()
        except ValueError as exc: valid,message=False,str(exc)
        if not valid:
            self.dialog.show('Vamos con el taller',message,speaker='Profesor Marco');return
        self.dialog.show('Jornada terminada','Buen trabajo, hoy ya vimos las ideas y las comprobamos, mañana seguimos desde aquí' if self.day<5 else 'Terminamos los fundamentos, ya puedes empezar el primer año, guarda tus apuntes y tu modelo, los podrás consultar después',speaker='Profesor Marco',callback=self.advance_day)

    def advance_day(self):
        record=self.state.get('kashut',{}).get(str(self.day),{})
        if not self.state['lectures'].get(str(self.day)) or not record.get('complete') or not record.get('reviewed'):
            return
        valid,_=self.model_goal()
        if not valid:return
        if self.day==5:
            if not self.review:self.state['completed']=True
            self.save.save();self.active=False;self.on_finish()
        else:
            self.day+=1
            if not self.review:self.state['day']=self.day
            self.player.x,self.player.y=210,228
            self.moshi.reset_day()
            for peer in self.peers:peer.reset_day()
            self.day_intro_remaining=2.0
            self.save.save();self.mode='room'

    def skip(self):
        if not self.review:self.state['completed']=True
        self.save.save();self.active=False;self.on_finish()

    def leave(self):
        self.persist();self.active=False;self.on_exit()

    def update(self,dt,enabled=True):
        self.tick+=1
        if self.day_intro_remaining>0:
            if enabled:self.day_intro_remaining=max(0,self.day_intro_remaining-dt)
            return
        if self.mode=='kashut':self.kashut.update(dt,enabled)
        if enabled and self.mode=='room' and not self.dialog.active:
            self.player.update(pygame.key.get_pressed(),self.colliders)
            self.moshi.update(dt)
            for peer in self.peers:peer.update(dt)

    def handle_event(self,event):
        if not self.active:return False
        if self.day_intro_remaining>0:return True
        if self.mode in ('room','lecture') and not self.dialog.active and event.type==pygame.KEYDOWN and event.key==pygame.K_o:
            self.on_settings();return True
        if self.mode=='kashut':return self.kashut.handle_event(event)
        if self.mode=='studio':
            if not self.modeler.handle_event(event) and event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:self.mode='room'
            return True
        if self.mode=='lecture':
            if event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE:
                self.persist();self.audio.stop_narration();self.lecture.active=False;self.mode='room'
            else:self.lecture.handle_event(event)
            return True
        if self.dialog.active:return self.dialog.handle_event(event)
        if event.type==pygame.KEYDOWN:
            if event.key==pygame.K_ESCAPE:self.mode='room' if self.mode in ('pc','pause') else 'pause';return True
            if self.mode=='pause':return True
            if event.key in (pygame.K_n,pygame.K_F1):self.on_notes();return True
            if event.key==pygame.K_m and (self.day>1 or self.review):self.mode='studio';return True
            if event.key in (pygame.K_RETURN,pygame.K_e,pygame.K_SPACE):
                rect=self.player.get_rect().inflate(30,30)
                if rect.colliderect(pygame.Rect(210,104,65,30)):self.interact_teacher()
                elif self.moshi.state!='gone' and rect.colliderect(pygame.Rect(275,221,70,30) if self.moshi.state in ('studying','packing','shutdown') else pygame.Rect(self.moshi.x,self.moshi.y,20,25)):self.speak_moshi()
                elif rect.colliderect(pygame.Rect(125,224,75,30)):self.open_pc()
                else:
                    for peer in self.peers:
                        if peer.state!='gone' and rect.colliderect(pygame.Rect(peer.x-4,peer.y-4,28,30)):self.speak_peer(peer);break
                return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for rect,callback in self.buttons:
                if rect.collidepoint(event.pos):callback();return True
        return False

    def speak_moshi(self):
        completed=self.state.get('kashut',{}).get(str(self.day),{}).get('complete')
        speech=self.moshi.departure_speech or (MOSHI_AFTER if completed else MOSHI_BEFORE)[self.day]
        def leave():
            if completed and self.moshi.state=='studying':
                self.moshi.start_departure(speech)
                self.moshi.route=[(305,239),(95,239),(88,232)]
        self.dialog.show('Moshi',speech,speaker='Moshi',portrait=self.moshi.sprites['down'][0],callback=leave)

    def speak_peer(self,peer):
        completed=bool(self.state.get('kashut',{}).get(str(self.day),{}).get('complete'))
        speech=peer.departure_speech or speech_for(peer.name,self.day,completed)
        def leave():
            if completed and peer.state=='studying':
                peer.start_departure(speech)
                peer.route=[(peer.x,175),(92,175),(92,232),(88,232)]
        self.dialog.show(peer.name,speech,speaker=peer.name,portrait=peer.sprites['down'][0],callback=leave)

    def open_pc(self):
        if not self.state['lectures'].get(str(self.day)):
            self.dialog.show('Primero la explicación','Marco nos va a explicar las ideas en la pizarra, después abrimos Kashut desde aquí',speaker='Tu computador')
        else:self.mode='pc'

    def button(self,surface,label,rect,callback):
        rect=pygame.Rect(rect)
        button(surface,label,rect,self.font,accent=MINT)
        self.buttons.append((rect,callback))

    def draw(self,surface):
        self.buttons=[]
        if self.mode=='studio':self.modeler.draw(surface);return
        if self.mode=='lecture':self.lecture.draw(surface);return
        if self.mode=='kashut':self.kashut.draw(surface);return
        surface.blit(intro_room(),(0,0))
        centered(surface,'Fundamentos | Marco',(171,37,138,18),self.small,(225,240,215),padding=0)
        x,y=236,77
        marco_sprite(surface,x,y)
        draw.circle(surface,(255,205,95),(244,70),5)
        draw_fitted_text(surface,'!',pygame.Rect(240,65,8,9),self.small,(30,35,40),padding=0)
        for dx,dy,label,peer in self.desks:
            desk(surface,(dx,dy,65,27))
            draw.rect(surface,(232,224,193),(dx+3,dy+6,10,12))
            draw.line(surface,(155,165,144),(dx+5,dy+8),(dx+10,dy+8))
            draw.rect(surface,(70,123,115),(dx+52,dy+14,5,7))
            draw.rect(surface,(38,48,63),(dx+20,dy+27,24,10))
            draw.rect(surface,(145,155,165),(dx+18,dy+3,29,21))
            draw.rect(surface,(12,36,50),(dx+20,dy+5,25,16))
            if peer is None or peer.pc_on:
                draw.line(surface,(65,225,195),(dx+23,dy+9),(dx+41,dy+9))
                draw.line(surface,(80,160,235),(dx+23,dy+14),(dx+36,dy+14))
            draw.rect(surface,(165,170,175),(dx+20,dy+25,25,3))
            monitor_details(surface,(dx+18,dy+3,29,21))
            draw_fitted_text(surface,label,pygame.Rect(dx,dy+48,65,12),self.small,(235,235,225),padding=0)
            if peer is not None:
                if peer.state in ('studying','packing','shutdown'):
                    pose='up' if peer.state=='studying' else 'right'
                    px,py=peer.px+4,peer.py+9
                    surface.blit(peer.sprites[pose][0],(px,py))
                    if peer.state=='packing':
                        reach=int(math.sin(peer.elapsed*10)*3)
                        draw.line(surface,peer.shirt_color,(px+7,py+14),(px+13,py+12+reach),2)
                        draw.rect(surface,peer.skin_color,(px+11,py+10+reach,3,2))
                else:peer.draw_walking(surface)
        self.player.draw(surface)
        for rect,callback in [(pygame.Rect(210,70,65,65),self.interact_teacher),(pygame.Rect(125,197,75,47),self.open_pc)]:self.buttons.append((rect,callback))
        if self.moshi.state!='gone':
            zone=pygame.Rect(275,210,75,40) if self.moshi.state in ('studying','packing','shutdown') else pygame.Rect(self.moshi.x-5,self.moshi.y-5,30,35)
            self.buttons.append((zone,self.speak_moshi))
        for peer in self.peers:
            if peer.state!='gone':
                self.buttons.append((pygame.Rect(peer.x-6,peer.y-15,36,40),lambda p=peer:self.speak_peer(p)))
        panel(surface,pygame.Rect(14,7,270,20),(22,39,50),MINT,shadow=False)
        draw_fitted_text(surface,f'Taller opcional | Día {self.day}/5',pygame.Rect(22,8,254,18),self.title,GOLD,padding=0)
        if self.mode in ('pause','pc'):
            panel(surface,pygame.Rect(85,66,310,185),(18,33,46),GOLD)
            self.buttons=[]
            if self.mode=='pc':
                self.button(surface,'Unirse a Kashut',(105,82,270,28),self.start_kashut)
                if self.day>1 or self.review:self.button(surface,'Abrir modelador',(105,118,270,28),lambda:setattr(self,'mode','studio'))
                if self.day>=4:self.button(surface,'Probar modelo del taller',(105,154,270,28),self.test_workshop)
                self.button(surface,'Cuaderno',(105,190,130,24),self.on_notes)
                self.button(surface,'Volver a sala',(245,190,130,24),lambda:setattr(self,'mode','room'))
            else:
                self.button(surface,'Continuar en la sala',(105,82,270,28),lambda:setattr(self,'mode','room'))
                self.button(surface,'Guardar y volver al menú' if not self.review else 'Volver a la carrera',(105,121,270,28),self.leave)
                self.button(surface,'Omitir taller opcional, ir a la carrera',(105,160,270,28),self.skip)
                self.button(surface,'Repasar la clase de hoy',(105,199,270,28),self.restart_lecture)
        if self.dialog.active:self.dialog.draw(surface)
        if self.day_intro_remaining>0:
            backdrop(surface)
            panel(surface,pygame.Rect(48,86,384,112),(23,41,52),GOLD)
            centered(surface,'Semana Introductoria',pygame.Rect(40,99,400,35),make_font(28),GOLD,padding=0)
            centered(surface,f'Día {self.day}',pygame.Rect(40,151,400,32),make_font(25),MINT,padding=0)
            for i in range(5):draw.circle(surface,GOLD if i+1==self.day else (60,86,91),(212+i*14,191),2)


