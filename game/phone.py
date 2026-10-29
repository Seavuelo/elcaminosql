"""Liga de Dioses en el teléfono, con preparación y simulación a pantalla amplia"""
import pygame
from game.rendering import draw,make_font
from game.ui_helpers import render_wrapped_text,draw_fitted_text
from game.visuals import centered,mix
from game.league import LeagueGame,GODS,PROFILES,STRATEGIES,STRATEGY_INFO,RELICS,UPGRADES,CUE_TEXT,RANKS
from game.league_art import (background,portrait,crest,gem,relic_icon,league_button,arena,precision_circle,
                             ARENA,CREAM,GOLD,MUTE,PINK,INK)


class StudentPhone:
    def __init__(self,save,audio):
        self.game=LeagueGame(save);self.audio=audio
        self.active=False;self.opening=0.;self.tab='match';self.selected_upgrade=0
        self.message='La XP de tus clases entrena a tus dioses, las partidas son gratis'
        self.font_title=make_font(21);self.font=make_font(13);self.small=make_font(11);self.tiny=make_font(10)
        self.large=make_font(29);self.buttons=[];self.view_result=False;self.last_cue=None

    def open(self):
        self.active=True;self.opening=0.;self.audio.play_key()
        if self.game.state['battle']:self.tab='match';self.view_result=False

    def close(self):self.active=False

    def update(self,dt):
        if self.active:self.opening=min(1,self.opening+dt/.25)
        if self.game.update(dt,interactive=self.active and self.tab=='match'):
            last=self.game.state['last_match'];self.view_result=True
            self.message=('Victoria' if last['win'] else 'Derrota')+f' · {last.get("rating_delta",0):+} PL'
            if self.active:self.audio.play_success() if last['win'] else self.audio.play_key()
        cue=self.game.current_cue()
        cue_id=(self.game.state['battle']['seed'],cue['id']) if cue and self.active and self.tab=='match' else None
        if cue_id and cue_id!=self.last_cue:self.audio.play_key()
        self.last_cue=cue_id

    def _activate(self,action):
        kind,value=action
        if kind=='close':self.close();return
        if kind=='tab':self.tab=value
        elif kind=='god':
            if self.game.choose_god(value):
                self.message=PROFILES[value]['detail'];self.view_result=False
        elif kind=='strategy':
            if self.game.choose_strategy(value):self.message=STRATEGY_INFO[value][0]
        elif kind=='relic':
            if self.game.choose_relic(value):self.message=RELICS[value][1]
        elif kind=='buy':
            self.selected_upgrade=list(UPGRADES).index(value)
            success,self.message=self.game.buy(value)
            if success:self.audio.play_success();return
        elif kind=='prepare':self.view_result=False;self.tab='match'
        elif kind=='result':self.view_result=True;self.tab='match'
        elif kind=='battle':
            if self.game.start_battle():
                self.tab='match';self.view_result=False
                self.message='Lee el mapa y espera una oportunidad, no necesitas pulsar sin parar'
        self.audio.play_key()

    def _attempt(self,point=None):
        result=self.game.attempt_timing(point)
        if result:
            self.message=result['text']
            self.audio.play_success() if result['success'] else self.audio.play_error()

    def handle_event(self,event):
        if not self.active:return False
        if event.type==pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE,pygame.K_p,pygame.K_F4):self.close()
            elif event.key in (pygame.K_1,pygame.K_2,pygame.K_3):
                self.tab={pygame.K_1:'match',pygame.K_2:'upgrades',pygame.K_3:'plan'}[event.key]
            elif event.key==pygame.K_TAB:self.tab=['match','plan','upgrades'][(['match','plan','upgrades'].index(self.tab)+1)%3]
            elif self.game.state['battle']:
                if self.tab=='match' and event.key in (pygame.K_SPACE,pygame.K_RETURN):self._attempt()
            elif self.tab=='upgrades':
                if event.key in (pygame.K_UP,pygame.K_DOWN):self.selected_upgrade=(self.selected_upgrade+(1 if event.key==pygame.K_DOWN else -1))%len(UPGRADES)
                elif event.key==pygame.K_RETURN:self._activate(('buy',list(UPGRADES)[self.selected_upgrade]))
            elif event.key in (pygame.K_LEFT,pygame.K_RIGHT):
                keys=list(GODS);index=keys.index(self.game.state['god'])
                self._activate(('god',keys[(index+(1 if event.key==pygame.K_RIGHT else -1))%len(keys)]))
            elif event.key==pygame.K_s:
                keys=list(STRATEGIES);self._activate(('strategy',keys[(keys.index(self.game.state['strategy'])+1)%len(keys)]))
            elif event.key==pygame.K_r:
                keys=list(RELICS);self._activate(('relic',keys[(keys.index(self.game.state['relic'])+1)%len(keys)]))
            elif event.key==pygame.K_RETURN:self._activate(('prepare' if self.view_result and self.tab=='match' else 'battle',None))
            return True
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for rect,action in self.buttons:
                if rect.collidepoint(event.pos):self._activate(action);return True
            if self.game.state['battle'] and self.tab=='match' and ARENA.collidepoint(event.pos):
                self._attempt(((event.pos[0]-ARENA.x)/ARENA.width,(event.pos[1]-ARENA.y)/ARENA.height))
            return True
        return True

    def _button(self,surface,rect,label,action,selected=False,enabled=True,accent=GOLD):
        rect=pygame.Rect(rect)
        league_button(surface,label,rect,self.font,selected,accent,enabled)
        if enabled:self.buttons.append((rect,action))

    def _panel(self,surface,rect,accent=GOLD):
        rect=pygame.Rect(rect)
        draw.rect(surface,(23,18,30),rect.move(0,2),border_radius=3)
        draw.rect(surface,(46,33,46),rect,border_radius=3)
        draw.rect(surface,mix(accent,INK,.64),rect,1,border_radius=3)
        draw.line(surface,mix(accent,INK,.50),(rect.x+5,rect.y+2),(rect.right-5,rect.y+2))

    def _text(self,surface,text,rect,font=None,color=CREAM):
        render_wrapped_text(surface,text,pygame.Rect(rect),font or self.small,color=color,line_spacing=1,padding=0)

    def draw(self,surface,tick=0):
        if not self.active:return
        self.buttons=[]
        if self.opening<1:
            r=pygame.Rect(240-232*self.opening,292-282*self.opening,464*self.opening,max(16,282*self.opening))
            draw.rect(surface,(47,32,48),r,border_radius=8);draw.rect(surface,GOLD,r,1,border_radius=8)
            return
        surface.blit(background(),(0,0))
        crest(surface,(29,25),12)
        surface.blit(self.font_title.render('LIGA DE DIOSES',True,CREAM),(49,11))
        wins=self.game.state['wins']
        rank=f'{self.game.rank} · {self.game.state["rating"]} PL · {wins} '+('victoria' if wins==1 else 'victorias')
        surface.blit(self.tiny.render(rank,True,MUTE),(49,29))
        self._panel(surface,(349,13,88,23))
        gem(surface,(359,24),GOLD,4)
        centered(surface,f'{self.game.state["xp"]} XP',pygame.Rect(366,14,66,20),self.font,GOLD,padding=0)
        self._button(surface,(444,15,17,18),'X',('close',None),accent=PINK)
        for x,label,key in [(18,'En vivo' if self.game.state['battle'] else 'Dioses','match'),(169,'Plan de partida','plan'),(320,'Aumentos','upgrades')]:
            self._button(surface,(x,47,142,18),label,('tab',key),self.tab==key)
        if self.tab=='upgrades':self._draw_upgrades(surface)
        elif self.tab=='plan':self._draw_plan(surface)
        elif self.game.state['battle']:self._draw_battle(surface)
        elif self.view_result and self.game.state['last_match']:self._draw_result(surface)
        else:self._draw_match(surface)
        draw.line(surface,(114,81,69),(196,280),(284,280))
        gem(surface,(240,280),GOLD,2)

    def _draw_match(self,surface):
        surface.blit(self.tiny.render('ELIGE TU DIOS',True,MUTE),(19,68))
        selected=self.game.state['god']
        for i,(key,(name,role,_,color)) in enumerate(GODS.items()):
            r=pygame.Rect(18+i%3*94,81+i//3*49,89,45)
            league_button(surface,'',r,self.small,selected==key,color)
            surface.blit(portrait(key,33),(r.x+2,r.y+3))
            draw_fitted_text(surface,name,pygame.Rect(r.x+37,r.y+5,48,13),self.font,CREAM,padding=0)
            self._text(surface,role,(r.x+37,r.y+20,48,22),self.tiny,MUTE)
            self.buttons.append((r,('god',key)))
        self._hero_card(surface,selected)
        plan=f'{STRATEGIES[self.game.state["strategy"]]} · {RELICS[self.game.state["relic"]][0]}'
        self._text(surface,plan,(19,234,280,14),self.small,GOLD)
        self._footer(surface)

    def _hero_card(self,surface,god):
        name,role,strategy,color=GODS[god];profile=PROFILES[god]
        self._panel(surface,(307,71,155,157),color)
        surface.blit(self.font_title.render(name,True,color),(318,78))
        surface.blit(portrait(god,62),(313,98))
        self._text(surface,role,(382,102,70,28),self.small)
        self._text(surface,'Afinidad\n'+STRATEGIES[strategy],(382,135,70,24),self.tiny,color)
        surface.blit(self.font.render(profile['skill'],True,GOLD),(318,170))
        self._text(surface,profile['detail'],(318,183,134,21),self.tiny)
        for i,(label,value) in enumerate(zip(('Daño','Aguante','Apoyo'),profile['stats'])):
            yy=205+i*7
            surface.blit(self.tiny.render(label,True,MUTE),(318,yy-1))
            draw.rect(surface,(28,22,36),(365,yy+1,84,2))
            draw.rect(surface,color,(365,yy+1,round(84*value/10),2))

    def _footer(self,surface):
        self._text(surface,self.message,(19,250,296,23),self.tiny,MUTE)
        self._button(surface,(324,249,138,25),'Buscar partida',('battle',None),True)
        if self.game.state['last_match']:
            self._button(surface,(307,232,155,14),'Ver último resultado',('result',None),accent=PINK)

    def _draw_plan(self,surface):
        locked=bool(self.game.state['battle']);prep=self.game.preparation();foe=prep['enemy']
        self._panel(surface,(18,72,444,42),PINK)
        crest(surface,(35,92),10,PINK)
        surface.blit(self.font.render('Rival: '+foe['name'],True,PINK),(51,78))
        self._text(surface,foe['hint'],(51,94,399,15),self.small)
        surface.blit(self.tiny.render('ESTRATEGIA',True,MUTE),(19,118))
        for i,(key,label) in enumerate(STRATEGIES.items()):
            self._button(surface,(18+i%3*150,130+i//3*23,144,20),label,('strategy',key),self.game.state['strategy']==key,not locked)
        surface.blit(self.tiny.render('RELIQUIA · una elección gratis con ventajas y desventajas',True,MUTE),(19,178))
        for i,(key,info) in enumerate(RELICS.items()):
            r=pygame.Rect(18+i%3*150,190+i//3*23,144,20)
            self._button(surface,r,info[0],('relic',key),self.game.state['relic']==key,not locked,accent=PINK)
            relic_icon(surface,key,(r.x+10,r.centery),GOLD,5)
        tags=('Afinidad activa' if prep['synergy'] else 'Sin afinidad')+' · '+('Responde al rival' if prep['counter'] else 'Rival incómodo')+(' · Reliquia afín' if prep['relic_match'] else '')
        self._text(surface,tags,(19,238,293,12),self.tiny,(153,219,173) if prep['counter'] else GOLD)
        if locked:self._text(surface,'Plan cerrado hasta terminar la partida',(19,255,430,18),self.small,MUTE)
        else:
            self._text(surface,RELICS[self.game.state['relic']][1],(19,252,296,23),self.tiny)
            self._button(surface,(324,249,138,25),'Buscar partida',('battle',None),True)

    def _draw_upgrades(self,surface):
        for i,(key,(name,_)) in enumerate(UPGRADES.items()):
            r=pygame.Rect(18,73+i*32,278,29);level=self.game.level(key);selected=i==self.selected_upgrade
            self._button(surface,r,'',('buy',key),selected,not self.game.state['battle'] and level<10)
            relic_icon(surface,key,(r.x+13,r.centery),GOLD,7)
            surface.blit(self.font.render(name,True,CREAM),(r.x+27,r.y+4))
            cost='MÁXIMO' if level>=10 else f'{self.game.cost(key)} XP'
            rendered=self.small.render(cost,True,(156,217,175) if self.game.state['xp']>=self.game.cost(key) else MUTE)
            surface.blit(rendered,(r.right-rendered.get_width()-7,r.y+5))
            for j in range(10):draw.rect(surface,GOLD if j<level else (83,64,72),(r.x+28+j*18,r.y+20,15,3),border_radius=1)
            surface.blit(self.tiny.render(f'{level}/10',True,MUTE),(r.right-32,r.y+18))
        key=list(UPGRADES)[self.selected_upgrade];level=self.game.level(key)
        self._panel(surface,(307,73,155,157),PINK)
        relic_icon(surface,key,(384,95),GOLD,13)
        centered(surface,UPGRADES[key][0],pygame.Rect(314,116,141,20),self.font_title,CREAM,padding=0)
        self._text(surface,UPGRADES[key][1],(318,140,133,31),self.small)
        self._text(surface,f'Ventana de precisión\n{.30+level*.10:.1f} s / máximo 1,3 s',(318,178,134,27),self.small,GOLD)
        detail=GODS[self.game.state['god']][0] if key=='mastery' else 'Compartido por tus dioses'
        self._text(surface,detail,(318,211,134,15),self.tiny,MUTE)
        self._text(surface,self.message,(19,245,443,27),self.small,MUTE)

    def _draw_battle(self,surface):
        battle=self.game.state['battle'];t=battle['elapsed'];duration=battle['duration'];result=battle['result']
        arena(surface,battle)
        self._panel(surface,(330,71,132,154),PINK)
        seen=[e for e in result.get('events',[]) if e['time']<=t]
        surface.blit(self.font.render('Relato de partida',True,GOLD),(338,76))
        for i,event in enumerate(seen[-4:]):
            yy=93+i*32;color=(238,191,110) if event['type']=='kill' else (226,143,144) if event['type']=='death' else (145,212,194)
            draw.rect(surface,color,(337,yy,2,25))
            self._text(surface,event['text'],(343,yy,111,29),self.tiny,color)
        k,d,a=self.game.live_score()
        phase='Carriles' if t/duration<.30 else 'Control del río' if t/duration<.65 else 'Pelea decisiva' if t/duration<.88 else 'Último empuje'
        self._panel(surface,(18,229,304,16))
        self._text(surface,f'{phase}  |  {k} / {d} / {a}  |  {max(0,int(duration-t))} s',(25,232,292,12),self.small)
        draw.rect(surface,(61,42,55),(330,232,132,6),border_radius=2)
        draw.rect(surface,GOLD,(330,232,max(1,round(132*t/duration)),6),border_radius=2)
        cue=self.game.current_cue()
        recent=next((e for e in reversed(result.get('precision',[])) if 0<=t-e['time']<2.8 and e['status']!='skipped'),None)
        if cue:
            precision_circle(surface,cue,t)
            title,detail=CUE_TEXT[cue['kind']]
            if cue['kind']=='mechanics' and any(e.get('combo')==4 and e['time']<=t for e in seen):title='¡Cuadra! El quinto está a tiro'
            ready=t>=cue['at']+cue['windup']
            self._text(surface,title+' · '+('AHORA' if ready else 'Prepárate'),(19,250,443,12),self.font,GOLD)
            self._text(surface,detail+' · Clic o Espacio',(19,264,443,12),self.tiny,CREAM)
        elif recent:
            self._text(surface,('¡PERFECTO! ' if recent['status']=='perfect' else '')+recent['text'],(19,250,443,26),self.font,(226,143,144) if recent['status']=='miss' else (157,229,184))
        else:
            self._text(surface,'Las jugadas de precisión son opcionales, tu plan sigue jugando aunque cierres el teléfono',(19,253,443,23),self.small,MUTE)

    def _draw_result(self,surface):
        last=self.game.state['last_match'];color=(151,220,176) if last['win'] else (224,148,158)
        self._panel(surface,(18,72,444,161),color)
        surface.blit(portrait(last['god'],93),(26,102))
        centered(surface,'VICTORIA' if last['win'] else 'DERROTA',pygame.Rect(134,80,310,30),self.large,color,padding=0)
        delta=last.get('rating_delta',0)
        for i,(label,value) in enumerate(zip(('BAJAS','MUERTES','ASISTENCIAS','PUNTOS'),(last['kills'],last['deaths'],last['assists'],f'{delta:+}'))):
            r=pygame.Rect(141+i*76,118,70,44);self._panel(surface,r,color)
            centered(surface,str(value),pygame.Rect(r.x,r.y+3,r.width,23),self.large,CREAM,padding=0)
            centered(surface,label,pygame.Rect(r.x,r.y+29,r.width,12),self.tiny,MUTE,padding=0)
        precision=last.get('precision',[]);hits=sum(e['status'] in ('hit','perfect') for e in precision)
        self._text(surface,f'{last.get("rank_after",self.game.rank)} · '+('MVP · ' if last.get('mvp') else '')+f'{hits}/{len(precision)} jugadas conectadas',(141,170,305,14),self.small,GOLD)
        rating=self.game.state['rating'];matches=self.game.state['matches']
        if matches<3:progress=matches/3;progress_label=f'Colocación {matches}/3'
        else:
            previous=max(threshold for _,threshold in RANKS if threshold<=rating)
            following=next(((name,threshold) for name,threshold in RANKS if threshold>rating),None)
            progress=min(1,(rating-previous)/max(1,following[1]-previous)) if following else 1
            progress_label=f'{following[1]-rating} PL para {following[0]}' if following else 'Rango GOD alcanzado'
        surface.blit(self.tiny.render(progress_label,True,MUTE),(141,184))
        draw.rect(surface,(79,61,66),(141,194,301,2));draw.rect(surface,GOLD,(141,194,max(1,round(301*progress)),2))
        enemy=last.get('enemy',{}).get('name','Equipo rival')
        self._text(surface,'Rival: '+enemy,(141,199,305,13),self.small)
        weak=min(UPGRADES,key=self.game.level)
        self._text(surface,'Próximo entrenamiento: '+UPGRADES[weak][0],(141,211,305,16),self.small,MUTE)
        self._button(surface,(18,246,216,27),'Preparar otra combinación',('prepare',None),True)
        self._button(surface,(246,246,216,27),'Entrenar con XP',('tab','upgrades'),accent=PINK)
