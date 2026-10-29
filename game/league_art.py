"""Arte nativo de Liga: retratos, reliquias, arena y señales de precisión"""
from functools import lru_cache
import math
import pygame
from game.rendering import draw,make_font,Canvas,scale_point
from game.visuals import mix,centered
from game.league import GODS

CREAM=(241,225,189)
GOLD=(232,186,101)
MUTE=(178,159,150)
INK=(35,24,36)
PINK=(218,135,170)
ARENA=pygame.Rect(18,71,304,154)


def ring(surface,color,center,radius,progress=1,width=1):
    points=[]
    for i in range(max(2,int(72*progress)+1)):
        angle=-math.pi/2+i/72*math.tau
        points.append((center[0]+math.cos(angle)*radius,center[1]+math.sin(angle)*radius))
    for a,b in zip(points,points[1:]):
        if isinstance(surface,Canvas):pygame.draw.aaline(surface,color,scale_point(a),scale_point(b)) if width<1 else draw.line(surface,color,a,b,width)
        else:draw.line(surface,color,a,b,max(1,width))


def crest(surface,center,size=10,color=GOLD):
    x,y=center
    draw.polygon(surface,mix(color,(20,10,26),.6),[(x-size,y-size*.65),(x,y-size),(x+size,y-size*.65),(x+size*.7,y+size*.5),(x,y+size),(x-size*.7,y+size*.5)])
    draw.polygon(surface,color,[(x-size,y-size*.65),(x,y-size),(x+size,y-size*.65),(x+size*.7,y+size*.5),(x,y+size),(x-size*.7,y+size*.5)],1)
    draw.line(surface,color,(x-size*.4,y+size*.35),(x+size*.4,y-size*.45),2)
    draw.line(surface,color,(x-size*.4,y-size*.45),(x+size*.4,y+size*.35),2)
    draw.polygon(surface,CREAM,[(x,y-size*.6),(x+2,y),(x,y+2),(x-2,y)])


def gem(surface,center,color=GOLD,size=5):
    x,y=center
    draw.polygon(surface,mix(color,(10,10,24),.4),[(x,y-size),(x+size,y),(x,y+size),(x-size,y)])
    draw.polygon(surface,color,[(x,y-size),(x+size,y),(x,y+size),(x-size,y)],1)
    draw.line(surface,CREAM,(x,y-size+1),(x-size+2,y))


def relic_icon(surface,key,center,color=GOLD,size=10):
    x,y=center;s=size/10
    def line(a,b,w=1):draw.line(surface,color,(x+a[0]*s,y+a[1]*s),(x+b[0]*s,y+b[1]*s),w)
    if key in ('lens','vision','eye'):
        draw.ellipse(surface,color,(x-8*s,y-4*s,16*s,8*s),1);draw.circle(surface,color,(round(x),round(y)),max(2,round(3*s)))
        line((-6,-6),(-4,-4));line((6,-6),(4,-4))
    elif key in ('fang','mechanics','blade'):
        draw.polygon(surface,color,[(x-5*s,y+8*s),(x+6*s,y-8*s),(x+6*s,y-1*s),(x-1*s,y+6*s)])
        line((-7,3),(1,8),2)
    elif key in ('aegis','positioning','shield'):
        draw.polygon(surface,color,[(x-7*s,y-7*s),(x+7*s,y-7*s),(x+6*s,y+3*s),(x,y+9*s),(x-6*s,y+3*s)],1)
        line((0,-5),(0,5));line((-4,-1),(4,-1))
    elif key in ('banner','macro','flag'):
        line((-5,-8),(-5,9),2)
        draw.polygon(surface,color,[(x-4*s,y-7*s),(x+8*s,y-6*s),(x+4*s,y-1*s),(x-4*s,y-1*s)])
    elif key in ('hourglass','mastery','clock'):
        line((-6,-8),(6,-8),2);line((-6,8),(6,8),2)
        for a,b in [((-5,-6),(5,6)),((5,-6),(-5,6))]:line(a,b)
        draw.polygon(surface,color,[(x-4*s,y+6*s),(x,y+2*s),(x+4*s,y+6*s)])
    else:
        draw.polygon(surface,color,[(x-7*s,y+4*s),(x-4*s,y-4*s),(x,y-9*s),(x+2*s,y-1*s),(x+6*s,y-5*s),(x+7*s,y+5*s),(x,y+9*s)])
        draw.polygon(surface,CREAM,[(x-3*s,y+6*s),(x,y),(x+3*s,y+6*s)])


@lru_cache(maxsize=18)
def portrait(god,size=64):
    # Cada retrato tiene su silueta, armadura y arma, conservadas al reducirlo
    art=pygame.Surface((64,70),pygame.SRCALPHA)
    c=GODS[god][3];dark=mix(c,(20,14,33),.65);skin=(226,180,142)
    pygame.draw.circle(art,mix(c,(34,22,40),.78),(32,31),28)
    pygame.draw.circle(art,mix(c,(35,24,36),.48),(32,31),27,1)
    for i in range(8):
        angle=i*math.pi/4;pygame.draw.circle(art,mix(c,CREAM,.35),(round(32+math.cos(angle)*25),round(31+math.sin(angle)*25)),1)
    pygame.draw.polygon(art,dark,[(8,66),(12,48),(24,39),(41,39),(54,49),(59,66)])
    pygame.draw.polygon(art,c,[(16,64),(18,47),(28,42),(38,42),(48,49),(50,65)])
    pygame.draw.rect(art,(54,34,42),(25,12,16,29),border_radius=6)
    pygame.draw.rect(art,skin,(25,20,16,20),border_radius=4)
    pygame.draw.rect(art,mix(skin,(80,40,40),.22),(25,33,16,6),border_radius=3)
    pygame.draw.rect(art,c,(25,13,16,11),border_radius=4)
    pygame.draw.line(art,(54,34,42),(29,29),(30,29),2);pygame.draw.line(art,(54,34,42),(36,29),(37,29),2)
    pygame.draw.line(art,CREAM,(27,26),(30,26));pygame.draw.line(art,CREAM,(36,26),(39,26))
    pygame.draw.rect(art,dark,(29,43,8,17));pygame.draw.line(art,GOLD,(31,44),(34,54))
    if god=='astra':
        pygame.draw.polygon(art,dark,[(16,24),(33,0),(49,24)])
        pygame.draw.line(art,c,(16,24),(49,24),3)
        pygame.draw.circle(art,CREAM,(33,15),2)
        pygame.draw.line(art,GOLD,(49,63),(51,23),2)
        gem(art,(51,17),c,7)
        pygame.draw.line(art,c,(20,49),(12,62),4)
    elif god=='bront':
        pygame.draw.rect(art,(141,177,150),(22,17,21,12),border_radius=3)
        pygame.draw.rect(art,(30,49,43),(25,25,16,4));pygame.draw.line(art,GOLD,(33,19),(33,31))
        pygame.draw.polygon(art,(54,92,76),[(7,40),(26,37),(27,57),(16,68),(6,57)])
        pygame.draw.polygon(art,GOLD,[(7,40),(26,37),(27,57),(16,68),(6,57)],1)
        gem(art,(17,49),c,5)
    elif god=='nix':
        pygame.draw.polygon(art,dark,[(19,35),(20,12),(34,5),(47,17),(45,38),(38,19),(27,20)])
        pygame.draw.rect(art,dark,(25,31,16,7));pygame.draw.line(art,c,(27,29),(30,29));pygame.draw.line(art,c,(36,29),(39,29))
        for x in (9,52):
            pygame.draw.polygon(art,(223,210,222),[(x,63),(x+5,39),(x+7,47),(x+3,64)])
    elif god=='kael':
        pygame.draw.polygon(art,(159,62,44),[(20,21),(24,8),(29,12),(33,3),(38,12),(45,10),(43,24),(37,19)])
        pygame.draw.line(art,(247,200,122),(50,64),(54,28),4)
        pygame.draw.line(art,(237,116,65),(48,53),(58,34),2)
        pygame.draw.polygon(art,dark,[(14,44),(22,39),(27,47),(16,54)])
    elif god=='selka':
        pygame.draw.rect(art,(50,104,124),(20,16,5,32),border_radius=2)
        pygame.draw.rect(art,(50,104,124),(41,15,6,35),border_radius=2)
        for x in (23,33,43):pygame.draw.polygon(art,GOLD,[(x-3,19),(x,10),(x+3,19)])
        pygame.draw.line(art,c,(51,64),(51,27),2)
        pygame.draw.arc(art,CREAM,(45,18,14,17),0,math.pi*1.7,2)
    elif god=='orion':
        pygame.draw.polygon(art,dark,[(18,39),(22,12),(33,5),(46,15),(47,40),(38,20),(26,21)])
        pygame.draw.arc(art,GOLD,(41,27,21,41),-math.pi/2,math.pi/2,3)
        pygame.draw.line(art,CREAM,(51,28),(51,66))
        pygame.draw.line(art,c,(39,46),(60,43),2)
    elif god=='varda':
        for center in [(22,16),(30,12),(40,14),(44,21)]:pygame.draw.circle(art,(71,113,68),center,7)
        for x in (20,43):pygame.draw.line(art,(161,125,77),(x,21),(x-3,7),2)
        pygame.draw.line(art,(170,132,81),(51,65),(52,24),3)
        pygame.draw.circle(art,c,(52,23),6);pygame.draw.circle(art,CREAM,(52,23),2)
    elif god=='rok':
        pygame.draw.polygon(art,(119,112,109),[(21,14),(40,10),(47,22),(43,37),(25,37),(19,28)])
        pygame.draw.rect(art,GOLD,(27,25,4,2));pygame.draw.rect(art,GOLD,(37,24,4,2))
        for x in (12,44):pygame.draw.polygon(art,c,[(x-4,44),(x+8,39),(x+13,51),(x,56)])
        pygame.draw.line(art,(114,94,80),(51,65),(53,32),4)
        pygame.draw.rect(art,(169,160,143),(44,28,19,11),border_radius=2)
    else:
        pygame.draw.rect(art,(226,218,198),(21,13,23,11),border_radius=4)
        pygame.draw.line(art,GOLD,(45,58),(53,27),2)
        pygame.draw.circle(art,c,(52,20),10,2)
        pygame.draw.line(art,CREAM,(52,20),(52,14));pygame.draw.line(art,CREAM,(52,20),(57,22))
        pygame.draw.polygon(art,dark,[(15,44),(24,40),(31,63),(19,61)])
    pygame.draw.line(art,mix(c,CREAM,.6),(16,65),(50,65))
    return pygame.transform.scale(art,(size,round(size*70/64)))


@lru_cache(maxsize=1)
def background():
    art=pygame.Surface((480,300))
    for y in range(300):pygame.draw.line(art,mix((58,35,53),(27,23,36),y/300),(0,y),(479,y))
    for i in range(45):
        x=(i*73+11)%480;y=(i*41+17)%300
        pygame.draw.circle(art,(91,63,71),(x,y),1)
    for side in (10,470):
        pygame.draw.line(art,(123,88,68),(side,7),(side,282))
        for yy in (9,39,279):gem(art,(side,yy),GOLD,3)
    for y in (8,280):pygame.draw.line(art,(123,88,68),(10,y),(470,y))
    return art


def league_button(surface,label,rect,font,selected=False,accent=GOLD,enabled=True):
    r=pygame.Rect(rect);c=accent if enabled else (104,94,104)
    fill=(75,51,60) if selected else (47,35,49)
    display=pygame.display.get_surface()
    if display and pygame.mouse.get_focused() and enabled:
        mx,my=pygame.mouse.get_pos();ww,hh=display.get_size()
        if r.collidepoint(mx*480/max(1,ww),my*300/max(1,hh)):fill=mix(fill,c,.17)
    points=[(r.x+4,r.y),(r.right-4,r.y),(r.right,r.y+4),(r.right,r.bottom-4),(r.right-4,r.bottom),(r.x+4,r.bottom),(r.x,r.bottom-4),(r.x,r.y+4)]
    draw.polygon(surface,(19,16,27),[(x,y+2) for x,y in points])
    draw.polygon(surface,fill,points)
    draw.polygon(surface,mix(c,fill,.30 if selected else .67),points,1)
    draw.line(surface,mix(fill,c,.30),(r.x+6,r.y+2),(r.right-6,r.y+2))
    if selected:gem(surface,(r.x+6,r.centery),c,2)
    centered(surface,label,r.inflate(-6,0),font,CREAM if enabled else MUTE,padding=2)


def phone_launcher(surface,rect,font,busy=False):
    league_button(surface,'',rect,font,accent=PINK)
    r=pygame.Rect(rect);x=r.x+5;y=r.y+2
    centered(surface,'Teléfono',pygame.Rect(r.x+16,r.y,r.width-20,r.height),font,CREAM,padding=0)
    draw.rect(surface,(209,180,129),(x,y,9,13),border_radius=2)
    draw.rect(surface,(53,34,54),(x+1,y+2,7,8))
    gem(surface,(x+4,y+6),PINK,2)
    draw.line(surface,CREAM,(x+3,y+11),(x+5,y+11))
    if busy:draw.circle(surface,(136,222,175),(r.right-4,r.y+3),2)


def _route(points,t):
    lengths=[math.dist(a,b) for a,b in zip(points,points[1:])];total=sum(lengths);travel=max(0,min(1,t))*total
    for a,b,length in zip(points,points[1:],lengths):
        if travel<=length:
            q=travel/max(1,length);return (a[0]+(b[0]-a[0])*q,a[1]+(b[1]-a[1])*q)
        travel-=length
    return points[-1]


@lru_cache(maxsize=1)
def terrain():
    art=pygame.Surface(ARENA.size);w,h=ARENA.size
    for y in range(h):pygame.draw.line(art,mix((47,80,57),(27,58,50),y/h),(0,y),(w,y))
    for i in range(430):
        xx=(i*47)%w;yy=(i*31)%h
        pygame.draw.rect(art,[(55,88,60),(39,71,52),(70,99,66)][i%3],(xx,yy,1,1))
    routes=[[(23,132),(23,24),(275,24),(280,22)],[(23,132),(280,22)],[(23,132),(276,132),(280,22)]]
    for path in routes:
        for a,b in zip(path,path[1:]):
            pygame.draw.line(art,(53,61,49),a,b,13);pygame.draw.line(art,(126,124,91),a,b,9)
        for i in range(35):
            xx,yy=_route(path,i/35);pygame.draw.rect(art,(145,140,105),(round(xx)-1,round(yy),3,1))
    pygame.draw.line(art,(25,71,76),(113,0),(192,h),19)
    pygame.draw.line(art,(46,110,110),(113,0),(192,h),12)
    for xx,yy in [(83,46),(110,108),(204,41),(219,100),(63,81),(241,70)]:
        pygame.draw.ellipse(art,(24,46,41),(xx-15,yy+3,32,9))
        for dx,dy,rr in [(-8,0,7),(1,-4,10),(10,0,7)]:
            pygame.draw.circle(art,(29,64,45),(xx+dx,yy+dy),rr)
            pygame.draw.circle(art,(51,94,57),(xx+dx-2,yy+dy-2),rr-2)
            pygame.draw.line(art,(89,122,68),(xx+dx-3,yy+dy-rr+2),(xx+dx+1,yy+dy-rr+2))
    for xx,yy in [(121,64),(167,83)]:
        pygame.draw.rect(art,(129,117,84),(xx,yy,22,7))
        for i in range(4):pygame.draw.line(art,(82,78,64),(xx+i*6,yy),(xx+i*6,yy+7))
    pygame.draw.ellipse(art,(32,50,53),(187,73,26,16),2)
    pygame.draw.ellipse(art,(93,110,83),(190,76,20,10),1)
    return art


def unit(surface,pos,god,team=0,player=False,health=1):
    x,y=pos;c=GODS[god][3] if not team else (224,120,115)
    draw.ellipse(surface,(21,40,38),(x-5,y+5,11,4))
    if player:ring(surface,GOLD,(x,y+2),9,.999,1)
    draw.rect(surface,mix(c,(15,24,30),.55),(x-4,y-3,8,9),border_radius=2)
    draw.rect(surface,c,(x-3,y-3,6,7))
    draw.rect(surface,(221,184,140),(x-2,y-8,5,5))
    draw.rect(surface,c,(x-3,y-9,6,3))
    if god in ('rok','bront'):draw.rect(surface,(174,168,140),(x-4,y-8,8,5))
    if god=='nix':draw.line(surface,CREAM,(x+4,y-4),(x+7,y+3))
    elif god=='orion':draw.ellipse(surface,GOLD,(x+3,y-5,5,10),1)
    elif god in ('astra','selka','zenit','varda'):
        draw.line(surface,(157,137,99),(x+5,y-7),(x+5,y+5));gem(surface,(x+5,y-8),c,2)
    else:draw.line(surface,GOLD,(x+4,y+3),(x+7,y-6),2)
    draw.rect(surface,(22,27,33),(x-6,y-14,13,3))
    draw.rect(surface,(131,215,158) if not team else (230,126,123),(x-5,y-13,max(0,round(11*health)),1))


def arena(surface,battle):
    surface.blit(terrain(),ARENA)
    x,y,w,h=ARENA;elapsed=battle['elapsed'];progress=elapsed/battle['duration'];result=battle['result']
    events=result.get('events',[]);seen=[e for e in events if e['time']<=elapsed]
    last=seen[-1] if seen else {'time':0,'pos':(.12,.84)}
    upcoming=next((e for e in events if e['time']>elapsed),None)
    # Interpolación entre jugadas del relato, no trayectorias circulares arbitrarias
    start=last.get('pos',(.45,.5));end=upcoming.get('pos',(.88,.12)) if upcoming else (.88,.12)
    q=min(1,(elapsed-last['time'])/max(.1,(upcoming['time'] if upcoming else battle['duration'])-last['time']))
    q=q*q*(3-2*q)
    target=(x+(start[0]+(end[0]-start[0])*q)*w,y+(start[1]+(end[1]-start[1])*q)*h)
    for i in range(10):
        yy=y+(i*17+elapsed*11)%h;xx=x+113+(yy-y)/h*79
        draw.line(surface,(71,138,133),(xx-3,yy),(xx+2,yy))
    routes=[[(x+23,y+132),(x+23,y+24),(x+275,y+24)],[(x+23,y+132),(x+280,y+22)],[(x+23,y+132),(x+276,y+132),(x+280,y+22)]]
    towers=sum(e.get('objective')=='torre' for e in seen)
    for team in (0,1):
        color=(125,197,190) if team==0 else (212,124,123)
        base=(x+22,y+132) if team==0 else (x+280,y+22)
        draw.ellipse(surface,(76,85,73),(base[0]-13,base[1]-7,26,14))
        gem(surface,base,color,9)
        for lane,path in enumerate(routes):
            pos=_route(path,.23 if team==0 else .77)
            if team and lane<towers:
                draw.ellipse(surface,(83,76,63),(pos[0]-5,pos[1],12,4));continue
            draw.rect(surface,(101,107,93),(pos[0]-4,pos[1]-10,8,15))
            draw.rect(surface,color,(pos[0]-5,pos[1]-12,10,4))
            gem(surface,(pos[0],pos[1]-15),color,3)
            for j in range(3):
                phase=((elapsed*.032+j*.022+lane*.1)%1)
                mpos=_route(path,phase if team==0 else 1-phase)
                draw.rect(surface,mix(color,(30,47,44),.3),(mpos[0]-2,mpos[1]-2,4,5))
    last_death=next((e for e in reversed(seen) if e['type']=='death'),None)
    dead=last_death is not None and elapsed-last_death['time']<.75
    down=set()
    for event in seen:
        if event['type']=='kill' and elapsed-event['time']<(4 if event.get('combo',0)>1 else 1.3):
            if event.get('combo',0)>1 and event.get('k')==1:down.add(event['combo']-1)
            else:down.update(range(min(4,event.get('k',1))))
    gods=list(GODS);chosen=result['god'];allies=[chosen]+[g for g in gods if g!=chosen][:4]
    for team in (1,0):
        for i in range(5):
            if team and i in down:continue
            hero=allies[i] if team==0 else gods[(i+battle['seed'])%len(gods)]
            px=target[0]+(i-2)*9+(14 if team else -14)
            py=target[1]+(i%3-1)*13+(8 if team else -8)
            px=max(x+12,min(x+w-12,px));py=max(y+20,min(y+h-10,py))
            if i==0 and team==0 and dead:
                ring(surface,(207,130,123),(px,py),8);continue
            hurt=upcoming and upcoming['type'] in ('kill','death') and upcoming['time']-elapsed<1.2
            health=.9 if not hurt else max(.12,(upcoming['time']-elapsed)/1.2)
            unit(surface,(px,py),hero,team,player=i==0 and team==0,health=health if hurt and team==int(upcoming['type']=='kill') and i==0 else .85)
    if upcoming and upcoming['type'] in ('kill','death','assist') and 0<upcoming['time']-elapsed<1.2:
        phase=(elapsed%.6)/.6
        source=(target[0]-21,target[1]-8);end=(target[0]+23,target[1]+8)
        if upcoming['type']=='death':source,end=end,source
        draw.circle(surface,(242,205,125),(round(source[0]+(end[0]-source[0])*phase),round(source[1]+(end[1]-source[1])*phase)),2)
    if last.get('type') in ('kill','death','assist','objective'):
        age=elapsed-last['time']
        if 0<=age<.8:
            pos=last.get('pos',(.5,.5));cx=x+pos[0]*w;cy=y+pos[1]*h
            color=(243,192,103) if last['type']=='kill' else (223,127,119) if last['type']=='death' else (133,216,203)
            ring(surface,color,(cx,cy),3+age*18,.999,1)
            for i in range(7):
                angle=i*math.tau/7;rr=age*28
                draw.rect(surface,color,(cx+math.cos(angle)*rr,cy+math.sin(angle)*rr,2,2))
            if last['type'] in ('kill','assist'):
                draw.line(surface,CREAM,(cx-25+age*28,cy+9-age*11),(cx-18+age*28,cy+6-age*11),2)
    draw.rect(surface,(137,144,103),ARENA,1,border_radius=2)


def precision_circle(surface,cue,elapsed):
    x=ARENA.x+cue['pos'][0]*ARENA.width;y=ARENA.y+cue['pos'][1]*ARENA.height
    age=elapsed-cue['at'];radius=cue['radius'];ready=age>=cue['windup']
    progress=max(0,min(1,(age-cue['windup'])/cue['window']))
    ring(surface,(39,29,43),(x,y),radius+3,.999,3)
    ring(surface,GOLD if ready else (189,170,149),(x,y),radius,.999,1)
    if ready:
        sweet=.15<=progress<=.92
        color=(150,235,187) if sweet else (240,188,112)
        ring(surface,color,(x,y),radius+9*(1-progress),.999,2)
        ring(surface,color,(x,y),radius+4,1-progress,2)
        draw.circle(surface,color,(round(x),round(y)),2)
        if .38<=progress<=.69:gem(surface,(x,y),CREAM,4)
    else:
        ring(surface,(204,169,105),(x,y),radius+16*(1-age/cue['windup']),.999,1)
        relic_icon(surface,cue['kind'],(x,y),GOLD,7)
    return pygame.Rect(x-radius,y-radius,radius*2,radius*2)
