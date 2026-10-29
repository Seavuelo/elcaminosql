"""Liga de Dioses: preparación, relato de partida y oportunidades de precisión"""
import math
import random
from copy import deepcopy

MATCH_DURATION=42.0
RANKS=[('Madera 3',0),('Madera 2',40),('Madera 1',80),('Fierro 3',130),('Fierro 2',190),('Fierro 1',260),
       ('Platilla 3',340),('Platilla 2',430),('Platilla 1',530),('Dorado 3',640),('Dorado 2',760),('Dorado 1',890),
       ('Platino 3',1030),('Platino 2',1180),('Platino 1',1340),('Rubí 3',1510),('Rubí 2',1690),('Rubí 1',1880),
       ('Prime 3',2080),('Prime 2',2290),('Prime 1',2510),('GOD',2750)]

GODS={
 'astra':('Astra','Maga astral','team',(151,147,244)),
 'bront':('Bront','Guardián','safe',(104,199,152)),
 'nix':('Nix','Asesina lunar','flank',(226,129,188)),
 'kael':('Kael','Duelista ígneo','pressure',(243,145,87)),
 'selka':('Selka','Oráculo de mareas','team',(105,210,218)),
 'orion':('Orión','Arquero solar','siege',(234,196,106)),
 'varda':('Varda','Druida del bosque','safe',(156,197,103)),
 'rok':('Rok','Coloso de piedra','pressure',(186,156,131)),
 'zenit':('Zénit','Cronomante','scaling',(170,162,230)),
}
PROFILES={
 'astra':dict(skill='Constelación',detail='Agrupa rivales y conecta daño en área',focus='mastery',relic='hourglass',stats=(8,3,8),weights=(1,.9,.9,1.1,1.4)),
 'bront':dict(skill='Baluarte',detail='Absorbe la entrada y protege a su equipo',focus='positioning',relic='aegis',stats=(4,10,7),weights=(1.2,.6,1.4,1,1)),
 'nix':dict(skill='Paso lunar',detail='Entra por un flanco y remata objetivos aislados',focus='mechanics',relic='fang',stats=(10,3,4),weights=(1.1,1.4,.9,.7,1.2)),
 'kael':dict(skill='Filo de brasa',detail='Gana intercambios cortos con combos precisos',focus='mechanics',relic='ember',stats=(9,5,3),weights=(.8,1.5,1,.9,1.1)),
 'selka':dict(skill='Marea viva',detail='Mantiene al grupo unido y habilita asistencias',focus='vision',relic='banner',stats=(4,5,10),weights=(1.4,.6,1.1,1.3,1)),
 'orion':dict(skill='Flecha del alba',detail='Castiga desde lejos y convierte presión en torres',focus='macro',relic='banner',stats=(9,3,6),weights=(1,1.2,1.2,1.3,.8)),
 'varda':dict(skill='Raíces vigías',detail='Detecta emboscadas y controla rutas del bosque',focus='vision',relic='lens',stats=(5,7,9),weights=(1.5,.6,1.3,1,1)),
 'rok':dict(skill='Impacto tectónico',detail='Rompe la primera línea y abre espacio al grupo',focus='positioning',relic='aegis',stats=(7,10,4),weights=(.7,1.1,1.4,1.1,.8)),
 'zenit':dict(skill='Último segundo',detail='Escala con maestría y castiga el final de la pelea',focus='mastery',relic='hourglass',stats=(9,4,7),weights=(1,1.1,1,1.1,1.5)),
}
STRATEGIES={'safe':'Seguro','pressure':'Presión','team':'En equipo','flank':'Flancos','siege':'Asedio','scaling':'Escalar'}
STRATEGY_INFO={
 'safe':('Espera el error rival y protege la retirada',(1.1,.7,1.4,.8,.9)),
 'pressure':('Disputa el carril y busca intercambios cortos',(.9,1.4,.8,1,1.1)),
 'team':('Reúne al equipo y pelea por los objetivos',(1.3,.8,1,1.4,.9)),
 'flank':('Usa visión y maestría para entrar por detrás',(1.4,1.1,.7,.8,1.3)),
 'siege':('Desgasta antes de derribar las estructuras',(1,.9,1.2,1.5,.9)),
 'scaling':('Cede presión inicial y aprovecha el juego tardío',(.9,1.1,1.2,1,1.5)),
}
RELICS={
 'lens':('Luciérnaga','Visión +2, posición +1, mecánicas -1',(2,-1,1,0,0),'eye'),
 'fang':('Colmillo','Mecánicas +2, maestría +1, posición -1',(0,2,-1,0,1),'blade'),
 'aegis':('Bastión','Posición +2, visión +1, objetivos -1',(1,0,2,-1,0),'shield'),
 'banner':('Estandarte','Objetivos +2, visión +1, mecánicas -1',(1,-1,0,2,0),'flag'),
 'hourglass':('Reloj del eco','Maestría +2, posición +1, visión -1',(-1,0,1,0,2),'clock'),
 'ember':('Ascuas','Objetivos +2, mecánicas +1, posición -1',(0,1,-1,2,0),'flame'),
}
UPGRADES={
 'vision':('Visión','Aprendiste a poner visión en la jungla'),
 'mechanics':('Mecánicas','Mejoras el farmeo y aciertas más habilidades'),
 'positioning':('Posicionamiento','Evitas entrar a peleas que ya estaban perdidas'),
 'macro':('Objetivos','Conviertes una ventaja en torres y objetivos'),
 'mastery':('Maestría del dios','Dominas las habilidades del dios elegido'),
}
SCOUTS=[
 dict(name='Cazadores de niebla',style='Emboscadas en el bosque',weak='vision',counters=['safe','team'],hint='La visión descubre sus entradas, evita caminar solo'),
 dict(name='Muralla de bronce',style='Defensa y estructuras',weak='macro',counters=['siege','scaling'],hint='Conviérteles el mapa en un problema, no fuerces la torre'),
 dict(name='Furia del carril',style='Daño temprano y duelos',weak='positioning',counters=['safe','scaling'],hint='Conserva distancia y no respondas cada provocación'),
 dict(name='Círculo del alba',style='Cinco rivales muy juntos',weak='mastery',counters=['flank','pressure'],hint='Una entrada lateral obliga a dividir su atención'),
]
CUE_TEXT={
 'vision':('Emboscada detectada','Marca al rival antes de que cruce el río'),
 'mechanics':('Ventana de remate','Conecta cuando el anillo entre en la banda'),
 'positioning':('Retirada arriesgada','Esquiva la entrada y sal de la zona de daño'),
 'macro':('Objetivo disputado','Asegura al Guardián antes que el equipo rival'),
 'mastery':('Tu definitiva está lista','Encadena la habilidad con la entrada del equipo'),
}


def new_state():
    return dict(xp=0,rewards=[],rating=0,matches=0,wins=0,god='astra',strategy='safe',relic='lens',
                upgrades={key:0 for key in UPGRADES if key!='mastery'},mastery={key:0 for key in GODS},battle=None,last_match=None)


def award_xp(save,amount,source):
    state=save.data.setdefault('league',new_state())
    if amount<=0 or source in state['rewards']:return 0
    state['xp']+=amount;state['rewards'].append(source)
    return amount


class LeagueGame:
    def __init__(self,save):
        self.save=save
        state=self.state
        state.setdefault('relic','lens')
        for god in GODS:state['mastery'].setdefault(god,0)
        if state['god'] not in GODS:state['god']='astra'
        if state['strategy'] not in STRATEGIES:state['strategy']='safe'
        if state['relic'] not in RELICS:state['relic']='lens'

    @property
    def state(self):return self.save.data.setdefault('league',new_state())

    @property
    def rank(self):
        if self.state['matches']<3:return 'Unranked'
        return next(name for name,threshold in reversed(RANKS) if self.state['rating']>=threshold)

    def level(self,key):
        return self.state['mastery'].get(self.state['god'],0) if key=='mastery' else self.state['upgrades'][key]

    def cost(self,key):return 100+self.level(key)*60+(self.state['rating']//250)*15

    def buy(self,key):
        if key not in UPGRADES:return False,'Ese aumento no existe'
        if self.state['battle']:return False,'Espera a que termine la partida para comprar aumentos'
        level,cost=self.level(key),self.cost(key)
        if level>=10:return False,'Este aumento ya llegó a nivel 10'
        if self.state['xp']<cost:return False,f'Necesitas {cost} XP para este aumento'
        self.state['xp']-=cost
        target=self.state['mastery'] if key=='mastery' else self.state['upgrades']
        target[self.state['god'] if key=='mastery' else key]=level+1
        self.save.save()
        return True,f'{UPGRADES[key][1]}, nivel {level+1}/10'

    def choose_god(self,god):return self._choose('god',god,GODS)
    def choose_strategy(self,strategy):return self._choose('strategy',strategy,STRATEGIES)
    def choose_relic(self,relic):return self._choose('relic',relic,RELICS)

    def _choose(self,key,value,options):
        if value not in options or self.state['battle']:return False
        self.state[key]=value;self.save.save();return True

    def scout(self):return deepcopy(SCOUTS[self.state['matches']%len(SCOUTS)])

    def preparation(self):
        god,strategy,relic=self.state['god'],self.state['strategy'],self.state['relic']
        foe=self.scout();profile=PROFILES[god]
        levels=[self.level(key) for key in UPGRADES]
        effective=[max(0,min(12,a+b)) for a,b in zip(levels,RELICS[relic][2])]
        strength=sum(level*w*p for level,w,p in zip(effective,STRATEGY_INFO[strategy][1],profile['weights']))
        synergy=GODS[god][2]==strategy;relic_match=profile['relic']==relic;counter=strategy in foe['counters']
        focus=effective[list(UPGRADES).index(foe['weak'])]
        chance=max(.12,min(.85,.20+strength*.010+(.05 if synergy else 0)+(.025 if relic_match else 0)+(.055 if counter else -.015)+focus*.004-self.state['rating']/10000))
        return dict(chance=round(chance,4),synergy=synergy,relic_match=relic_match,counter=counter,enemy=foe,effective=effective)

    @staticmethod
    def _rating(result):
        k,d,a=(result[key] for key in ('kills','deaths','assists'))
        mvp=result['win'] and ((k>=10 and d<=5) or (k+a>=18 and d<=4) or (k>=6 and d==0))
        delta=max(13,min(42,round(22+k*1.5+a*.7-d)))+3*int(mvp) if result['win'] else min(-8,max(-26,round(-18-max(-10,min(10,-(k*.8+a*.4-d*.8))))))
        result.update(rating_delta=int(delta),mvp=bool(mvp))

    @staticmethod
    def _chronicle(events):
        events.sort(key=lambda e:e['time'])
        for event in events:event['text']=event['text'].removeprefix('¡Primera sangre! ')
        first=next((e for e in events if e.get('k',0)+e.get('d',0)+e.get('a',0)>0),None)
        if first and first['type']=='kill' and first['k']==1:first['text']='¡Primera sangre! '+first['text']

    def simulate(self,seed,duration=MATCH_DURATION):
        rng=random.Random(seed);prep=self.preparation()
        v,m,p,o,z=(self.level(key) for key in UPGRADES)
        god=self.state['god'];roll=rng.random();win=roll<prep['chance'];support=god in ('selka','varda','bront')
        damage,toughness,utility=PROFILES[god]['stats']
        k=max(1,round(2+m*.55+z*.5+rng.uniform(-1,3)+(2 if win else 0)-support+(damage-7)*.2))
        d=max(0,round(10-p*.55-v*.35+rng.uniform(-2,2)-(2 if win else 0)-(toughness-5)*.2))
        a=max(1,round(2+o*.5+v*.35+rng.uniform(0,3)+(3 if self.state['strategy']=='team' else 0)+support*2+(utility-6)*.2))
        result=dict(win=win,kills=k,deaths=d,assists=a,god=god,strategy=self.state['strategy'],relic=self.state['relic'],
                    win_chance=prep['chance'],outcome_roll=roll,bonus=0.,enemy=prep['enemy'],events=[],precision=[])
        self._rating(result)
        actions=[];burst=min(4,k) if k>=2 and rng.random()<min(.72,.08+(m+z)*.03) else 0;remaining=k-burst
        for _ in range(remaining):actions.append(dict(type='kill',k=1,d=0,a=0))
        for _ in range(d):actions.append(dict(type='death',k=0,d=1,a=0))
        while a>0:
            count=min(a,2);actions.append(dict(type='assist',k=0,d=0,a=count));a-=count
        rng.shuffle(actions)
        locations=[(.34,.35),(.53,.53),(.70,.72),(.28,.70),(.74,.27)]
        for i,event in enumerate(actions):
            event.update(time=round(duration*(.07+.61*(i+.5)/max(1,len(actions))),4),pos=locations[i%len(locations)],lane=['superior','central','inferior'][i%3])
            if event['type']=='death':
                reasons=([f'Cruzas sin visión y te cazan en el carril {event["lane"]}','Un rival esperaba en la maleza, faltó un centinela','Pierdes de vista al jungla y llega por tu espalda'] if v<3 else
                         ['Entras antes que el equipo y concentran el daño','Gastaste tu salida muy pronto y el rival te alcanza','Te alejas de la línea aliada y cierran la retirada'] if p<3 else
                         ['Tres rivales conectan sus habilidades y caes','El rival te enfoca en el intercambio del río','Tu equipo se retira, pero no alcanzas la salida'])
                event['text']=rng.choice(reasons)
            elif event['type']=='kill':event['text']=rng.choice([f'Aíslas a un rival en el carril {event["lane"]}',f'{PROFILES[god]["skill"]} conecta y aseguras una baja',f'Castigas la retirada del rival en el carril {event["lane"]}'])
            else:
                lead=rng.choice(['Tu control abre la entrada del equipo','El grupo aprovecha tu cobertura','Cierras la ruta de escape del rival','Conectas la habilidad y el equipo remata','Tu presión facilita el intercambio'])
                event['text']=lead+f', +{event["a"]} '+('asistencias' if event['a']>1 else 'asistencia')
            result['events'].append(event)
        if burst:
            result['events'].append(dict(time=duration*.735,type='kill',k=burst,d=0,a=0,pos=(.66,.48),lane='central',combo=burst,
                                         text={2:'¡Doble! Dos rivales caen en la pelea del río',3:'¡Triple! Tres rivales caen en la pelea del río',4:'¡Cuadra! Cuatro rivales caen en la pelea del río'}[burst]))
        for i in range(1+o//4):
            objective='torre' if i%2==0 else 'Guardián'
            result['events'].append(dict(time=duration*(.35+i*.24),type='objective',k=0,d=0,a=0,pos=(.69,.54),objective=objective,
                                         text='La presión abre espacio, tu equipo asegura '+('una torre' if objective=='torre' else 'al Guardián')))
        result['events'].append(dict(time=.1,type='info',k=0,d=0,a=0,pos=(.12,.84),text='Se abren los carriles, tu equipo sale de la base'))
        self._chronicle(result['events'])
        return result

    def start_battle(self,seed=None,duration=MATCH_DURATION):
        if self.state['battle']:return False
        if not math.isfinite(duration) or duration<12:raise ValueError('La partida necesita al menos doce segundos')
        seed=random.randrange(2**31) if seed is None else seed
        rng=random.Random(seed+8041);result=self.simulate(seed,duration)
        kinds=rng.sample(['vision','positioning','macro','mastery'],1+seed%2)+['mechanics']
        fractions=[.30,.76] if len(kinds)==2 else [.23,.48,.76]
        windows=[]
        for i,(kind,fraction) in enumerate(zip(kinds,fractions)):
            level=self.level(kind)
            jitter=rng.uniform(-.012,.012) if kind=='mechanics' else rng.uniform(-.025,.025)
            pos=(.66,.48) if kind=='mechanics' else (round(rng.uniform(.22,.76),3),round(rng.uniform(.27,.72),3))
            windows.append(dict(id=i,kind=kind,at=duration*(fraction+jitter),windup=.85,window=round(.30+level*.10,2),radius=9+level*1.4,pos=pos,status='pending'))
        self.state['battle']=dict(version=2,seed=seed,elapsed=0.,duration=float(duration),result=result,windows=windows)
        self.save.save();return True

    def current_cue(self):
        battle=self.state['battle']
        if not battle:return None
        return next((w for w in battle.get('windows',[]) if w['status']=='pending' and w['at']<=battle['elapsed']<=w['at']+w['windup']+w['window']),None)

    def live_score(self):
        battle=self.state['battle']
        if not battle:return (0,0,0)
        events=[e for e in battle['result'].get('events',[]) if e['time']<=battle['elapsed']]
        return tuple(sum(e.get(key,1 if e['type']==kind else 0) for e in events) for key,kind in [('k','kill'),('d','death'),('a','assist')])

    def attempt_timing(self,point=None):
        battle=self.state['battle'];cue=self.current_cue()
        if not battle or not cue:return None
        progress=(battle['elapsed']-cue['at']-cue['windup'])/cue['window']
        inside=point is None or math.hypot((point[0]-cue['pos'][0])*304,(point[1]-cue['pos'][1])*154)<=cue['radius']
        success=inside and .15<=progress<=.92;perfect=success and .38<=progress<=.69
        cue['status']='perfect' if perfect else 'hit' if success else 'miss'
        result=battle['result'];kind=cue['kind']
        if not success:text='La ventana se cerró antes de conectar' if progress>.92 else 'Te anticipaste al anillo' if progress<.15 else 'El golpe quedó fuera del círculo'
        elif kind in ('mechanics','mastery'):
            result['kills']+=1
            previous=next((e.get('combo',0) for e in reversed(result['events']) if e.get('combo',0)>1 and 0<=battle['elapsed']-e['time']<=4.),0) if kind=='mechanics' else 0
            combo=previous+1 if previous else 1
            text={3:'¡Triple! Alcanzas a otro rival con el último combo',4:'¡Cuadra! Conectas el remate antes de la retirada',5:'¡Penta! Alcanzas al quinto rival con el último combo'}.get(combo,'¡Remate preciso! Conectas la habilidad y sumas una baja')
            result['events'].append(dict(time=battle['elapsed'],type='kill',k=1,d=0,a=0,pos=cue['pos'],text=text,combo=combo))
        elif kind=='positioning':
            future=next((e for e in result['events'] if e['type']=='death' and e['time']>battle['elapsed']),None)
            if future:
                future.update(type='dodge',d=0,text='La ruta de retirada te salva de la siguiente emboscada');result['deaths']-=1
                text='¡Esquiva precisa! Preparaste una retirada segura'
            else:
                result['assists']+=1
                result['events'].append(dict(time=battle['elapsed'],type='assist',k=0,d=0,a=1,pos=cue['pos'],text='Reposicionas al equipo y habilitas una baja'))
                text='¡Buena posición! Tu equipo aprovecha el espacio'
        else:
            result['assists']+=int(kind=='vision')
            text='¡Lo viste venir! Marcas al rival y tu equipo lo intercepta' if kind=='vision' else '¡Objetivo asegurado! El Guardián cae de tu lado'
            result['events'].append(dict(time=battle['elapsed'],type='assist' if kind=='vision' else 'objective',k=0,d=0,a=int(kind=='vision'),pos=cue['pos'],text=text,objective='Guardián' if kind=='macro' else None))
        if success:result['bonus']+=.065 if perfect else .04
        result['precision'].append(dict(kind=kind,status=cue['status'],text=text,time=battle['elapsed']))
        self._chronicle(result['events']);self.save.save()
        return dict(success=success,perfect=perfect,text=text)

    def update(self,dt,interactive=False):
        battle=self.state['battle']
        if not battle:return False
        if not math.isfinite(dt) or dt<0:return False
        battle['elapsed']=min(battle['duration'],battle['elapsed']+dt)
        for cue in battle.get('windows',[]):
            if cue['status']=='pending' and battle['elapsed']>cue['at']+cue['windup']+cue['window']:
                cue['status']='miss' if interactive else 'skipped'
                battle['result']['precision'].append(dict(kind=cue['kind'],status=cue['status'],text='Oportunidad no aprovechada' if interactive else 'La simulación siguió en segundo plano',time=cue['at']+cue['windup']+cue['window']))
        if battle['elapsed']<battle['duration']:return False
        result=battle['result']
        if battle.get('version')==2:
            result['win_chance']=min(.95,result['win_chance']+result['bonus'])
            result['win']=result['outcome_roll']<result['win_chance'];self._rating(result)
        before=self.rank
        self.state['matches']+=1;self.state['wins']+=int(result['win'])
        self.state['rating']=max(0,self.state['rating']+result.get('rating_delta',25 if result['win'] else -12))
        self.state['last_match']={**result,'rank_before':before,'rank_after':self.rank}
        self.state['battle']=None;self.save.save();return True
