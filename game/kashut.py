from game.visuals import panel, button, centered, backdrop, GOLD, mix
"""Kashut local, respuestas persistidas y premios por mejora sin cultivar XP"""
import pygame
from game.kashut_questions import QUESTIONS
from game.rendering import draw,make_font
from game.ui_helpers import draw_fitted_text,render_wrapped_text
from game.intro_peers import INTRO_NAMES


def podium_rank(score):
    return 1 if score==10 else 2 if score>=8 else 3 if score>=7 else None


def reward_for(score):
    return 40+20*score+{1:100,2:60,3:30,None:0}[podium_rank(score)]


def reading_seconds(day,index):
    question,options,_,_=QUESTIONS[day][min(index,9)]
    words=len((' '.join((question,)+tuple(options))).split())
    return min(45.,25.+max(0,words-25)*.5)


class Kashut:
    def __init__(self,save,audio,on_exit):
        self.save,self.audio,self.on_exit=save,audio,on_exit
        self.font,self.title,self.small=make_font(14),make_font(24),make_font(11)
        self.buttons=[]
        self.tick=0

    def open(self,day):
        self.day=day
        records=self.save.data['foundation'].setdefault('kashut',{})
        self.state=records.setdefault(str(day),dict(answers=[],remaining=reading_seconds(day,0),reviewed=False,best=0,xp_granted=0))
        self.state.setdefault('xp_granted',0)
        self.remaining=float(self.state.get('remaining',reading_seconds(day,len(self.state['answers']))))
        self.paused=False
        self.cooldown=0
        self.review_index=0
        self.phase='question' if len(self.state['answers'])<10 else 'podium'
        if self.phase=='podium': self.finish_score()

    @property
    def score(self):
        return sum(answer==QUESTIONS[self.day][i][2] for i,answer in enumerate(self.state['answers']))

    @property
    def wrong(self):
        return [i for i,answer in enumerate(self.state['answers']) if answer!=QUESTIONS[self.day][i][2]]

    def persist(self):
        self.state['remaining']=self.remaining
        self.save.save()

    def answer(self,index):
        if self.phase!='question' or self.paused or self.cooldown>0: return
        self.state['answers'].append(index)
        self.remaining=reading_seconds(self.day,len(self.state['answers']))
        self.cooldown=.3
        self.audio.play_key()
        if len(self.state['answers'])==10:
            self.phase='podium'
            self.finish_score()
        self.persist()

    def finish_score(self):
        self.state['best']=max(self.state.get('best',0),self.score)
        total=reward_for(self.state['best'])
        delta=max(0,total-self.state['xp_granted'])
        if delta:
            self.save.award_league_xp(delta,f'kashut_{self.day}_best_{self.state["best"]}')
            self.state['xp_granted']=total
        self.state['complete']=True
        self.save.save()
        if podium_rank(self.score): self.audio.play_success()

    def restart(self):
        self.state.update(answers=[],remaining=reading_seconds(self.day,0),reviewed=False,complete=False)
        self.open(self.day)
        self.persist()

    def leave(self):
        self.persist()
        self.on_exit()

    def next_review(self):
        if self.phase=='podium' and self.wrong:
            self.phase='review'; self.review_index=0
        elif self.phase=='review' and self.review_index+1<len(self.wrong):
            self.review_index+=1
        else:
            self.state['reviewed']=True
            self.leave()

    def update(self,dt,enabled=True):
        self.tick+=1
        self.cooldown=max(0,self.cooldown-dt)
        if enabled and not self.paused and self.phase=='question':
            self.remaining=max(0,self.remaining-dt)
            if not self.remaining:
                self.answer(None)

    def handle_event(self,event):
        if event.type==pygame.WINDOWFOCUSLOST:
            self.paused=True; self.persist(); return True
        if event.type==pygame.KEYDOWN:
            if self.paused:
                if event.key==pygame.K_RETURN: self.paused=False
                elif event.key==pygame.K_ESCAPE: self.leave()
                return True
            if event.key==pygame.K_ESCAPE:
                self.paused=True; self.persist(); return True
            if self.phase=='question' and pygame.K_1<=event.key<=pygame.K_4:
                self.answer(event.key-pygame.K_1)
            elif self.phase!='question' and event.key in (pygame.K_RETURN,pygame.K_SPACE):
                self.next_review()
            elif self.phase=='podium' and event.key==pygame.K_r:
                self.restart()
            return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for rect,callback in self.buttons:
                if rect.collidepoint(event.pos): callback(); break
            return True
        return False

    def button(self,surface,label,rect,callback,color=(40,70,110)):
        rect=pygame.Rect(rect)
        button(surface,label,rect,self.font,accent=mix(color,(255,255,255),.45),fill=mix(color,(17,26,40),.25))
        self.buttons.append((rect,callback))

    def draw(self,surface):
        self.buttons=[]
        backdrop(surface,(32,27,57))
        panel(surface,pygame.Rect(12,6,456,46),(38,35,63),GOLD,shadow=False)
        draw_fitted_text(surface,'KASHUT | Profesor Marco',pygame.Rect(16,9,448,27),self.title,(255,220,110),padding=0)
        draw_fitted_text(surface,'Participantes: '+', '.join((self.save.data.get('player_name','Estudiante'),)+INTRO_NAMES),pygame.Rect(16,36,448,15),self.small,(190,180,215),padding=0)
        if self.phase=='question':
            index=len(self.state['answers'])
            question,options,correct,why=QUESTIONS[self.day][index]
            draw_fitted_text(surface,f'Pregunta {index+1}/10 | {max(0,int(self.remaining+1))} s',pygame.Rect(24,57,432,18),self.small,(200,205,230),padding=0)
            draw_fitted_text(surface,question,pygame.Rect(24,82,432,53),self.title,(245,242,255),padding=0)
            draw.rect(surface,(60,40,85),(24,140,432,4))
            draw.rect(surface,(95,220,205),(24,140,int(432*min(1,self.remaining/reading_seconds(self.day,index))),4))
            colors=[(150,44,68),(37,80,160),(135,95,16),(30,110,83)]
            for i,option in enumerate(options):
                self.button(surface,f'{i+1}. '+option,(24+(i%2)*221,156+(i//2)*58,211,49),lambda j=i:self.answer(j),colors[i])
            draw_fitted_text(surface,'La rapidez no cambia el podio, cuenta cuántas entiendes',pygame.Rect(24,279,432,13),self.small,(205,195,220),padding=0)
        elif self.phase=='podium':
            rank=podium_rank(self.score)
            pname=self.save.data.get('player_name','Estudiante')
            text='¡PRIMER LUGAR!' if rank==1 else '¡Estás en el podio!' if rank else 'Terminaste, ahora repasemos'
            draw_fitted_text(surface,text,pygame.Rect(24,61,432,25),self.title,(255,220,100),padding=0)
            draw_fitted_text(surface,f'{self.score}/10 aciertos | Mejor resultado: {self.state["best"]}/10 | XP total del día: {self.state["xp_granted"]}',pygame.Rect(24,91,432,20),self.small,(225,220,245),padding=0)
            names={1:'Moshi',2:'Sofía',3:'Matías'}
            if rank:
                if rank==1:names.update({2:'Moshi',3:'Sofía'})
                names[rank]=pname
            else: draw_fitted_text(surface,pname+' | Sigue practicando, puedes repetir',pygame.Rect(24,107,432,18),self.font,(220,210,235),padding=0)
            for place,x,height in [(2,56,52),(1,184,75),(3,312,38)]:
                color=(225,175,55) if place==1 else (125,145,175) if place==2 else (160,105,65)
                panel(surface,pygame.Rect(x,229-height,112,height),mix(color,(23,31,45),.18),color,radius=3)
                draw.line(surface,mix(color,(255,255,255),.35),(x+4,230-height),(x+107,230-height))
                draw_fitted_text(surface,names[place],pygame.Rect(x-4,207-height,120,20),self.font,(255,250,235),padding=0)
                centered(surface,str(place),pygame.Rect(x,232-height,112,30),self.title,(31,40,50),padding=0)
            if rank:
                for i in range(42 if rank==1 else 20):
                    x=(i*67+self.tick*2)%480; y=(i*29+self.tick*(2 if rank==1 else 1))%225
                    draw.rect(surface,[(255,205,65),(90,230,195),(190,120,245)][i%3],(x,y,2,3))
            self.button(surface,'Salir del Kashut' if not self.wrong else 'Revisar respuestas',(24,249,282,29),self.next_review)
            self.button(surface,'Repetir',(316,249,140,29),self.restart)
            draw_fitted_text(surface,'Repetir no duplica XP, mejorar tu mejor marca premia solo la diferencia',pygame.Rect(24,281,432,13),self.small,(192,193,216),padding=0)
        else:
            index=self.wrong[self.review_index]
            question,options,correct,why=QUESTIONS[self.day][index]
            answer=self.state['answers'][index]
            from game.learning_diagrams import illustration
            from game.kashut_questions import DIAGRAMS
            panel(surface,pygame.Rect(18,58,444,56),(41,43,73),(156,143,208),shadow=False)
            draw_fitted_text(surface,f'REPASO | Pregunta {index+1}',pygame.Rect(26,63,428,13),self.small,(213,191,255),padding=0)
            draw_fitted_text(surface,question,pygame.Rect(26,80,428,28),self.font,(242,240,250),padding=0)
            for x,label,text,color in [(18,'TU RESPUESTA','Sin respuesta' if answer is None else options[answer],(244,159,146)),(246,'RESPUESTA CORRECTA',options[correct],(133,230,189))]:
                panel(surface,pygame.Rect(x,120,216,49),(28,38,58),color,shadow=False)
                draw_fitted_text(surface,label,pygame.Rect(x+8,124,200,11),self.small,color,padding=0)
                draw_fitted_text(surface,text,pygame.Rect(x+8,139,200,25),self.font,(240,239,246),padding=0)
            panel(surface,pygame.Rect(18,177,444,67),(20,49,49),(103,167,157),shadow=False)
            illustration(surface,DIAGRAMS[self.day][index],pygame.Rect(25,185,165,50),variant=index)
            draw_fitted_text(surface,why,pygame.Rect(201,184,252,53),self.font,(224,242,229),padding=0)
            self.button(surface,f'Repaso {self.review_index+1}/{len(self.wrong)} | Seguir',(24,252,432,30),self.next_review)
        if self.paused:
            panel(surface,pygame.Rect(65,83,350,142),(21,33,48),GOLD)
            draw_fitted_text(surface,'Pausa, el tiempo está detenido',pygame.Rect(78,99,324,24),self.title,(255,220,110),padding=0)
            self.button(surface,'Continuar',(83,142,314,26),lambda:setattr(self,'paused',False))
            self.button(surface,'Guardar y volver a la sala',(83,178,314,26),self.leave)
