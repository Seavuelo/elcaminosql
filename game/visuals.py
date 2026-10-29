"""Acabados visuales compartidos, sin estado de juego ni zonas interactivas"""
from functools import lru_cache
import pygame
import math
from game.rendering import draw, make_font

INK = (18, 28, 42)
PAPER = (239, 231, 211)
MINT = (126, 218, 191)
GOLD = (239, 193, 112)
TEXT = (231, 237, 238)
MUTED = (142, 166, 181)
CRIMSON = (225, 65, 65)
ROSE = (245, 95, 120)
AZURE = (60, 150, 255)
EMERALD = (50, 205, 125)
INDIGO = (140, 120, 250)
AMBER = (255, 190, 60)

BTN_DANGER = {"accent": CRIMSON, "fill": (52, 24, 28)}
BTN_CREATE = {"accent": AZURE, "fill": (22, 38, 64)}
BTN_SUCCESS = {"accent": EMERALD, "fill": (18, 48, 32)}
BTN_TASK = {"accent": GOLD, "fill": (50, 40, 18)}
BTN_SPECIAL = {"accent": INDIGO, "fill": (36, 28, 62)}
BTN_NEUTRAL = {"accent": (130, 150, 170), "fill": (28, 38, 48)}


def mix(a, b, amount):
    return tuple(round(x+(y-x)*amount) for x,y in zip(a[:3],b[:3]))


@lru_cache(maxsize=128)
def _skin(size, fill, accent, selected, light, radius):
    w,h=size
    art=pygame.Surface(size,pygame.SRCALPHA)
    pygame.draw.rect(art,mix(fill,accent,.34 if selected else .16),(0,0,w,h),border_radius=radius)
    pygame.draw.rect(art,fill,(1,1,w-2,h-2),border_radius=max(0,radius-1))
    for y in range(2,h-2):
        color=mix(fill,(255,255,255),.055*(1-y/max(1,h)))
        inset=2+max(0,radius-2-min(y,h-1-y))
        pygame.draw.line(art,color,(inset,y),(w-inset-1,y))
    pygame.draw.line(art,mix(fill,accent,.48 if selected else .23),(radius,1),(w-radius-1,1))
    pygame.draw.line(art,mix(fill,(0,0,0),.35),(radius,h-2),(w-radius-1,h-2))
    if selected:
        pygame.draw.rect(art,accent,(2,5,2,max(1,h-10)),border_radius=1)
        pygame.draw.rect(art,accent,(w-4,5,1,max(1,h-10)))
    return art


def panel(surface,rect,fill=INK,accent=MINT,shadow=True,radius=4,selected=False,light=False):
    rect=pygame.Rect(rect)
    if rect.width<5 or rect.height<5:return
    if shadow:
        draw.rect(surface,(8,14,24),rect.move(0,3),border_radius=radius+1)
    surface.blit(_skin(rect.size,tuple(fill[:3]),tuple(accent[:3]),selected,light,radius),rect)


def centered(surface,text,rect,font,color=TEXT,padding=4):
    from game.ui_helpers import wrap_text_lines
    rect=pygame.Rect(rect)
    selected=font
    lines=wrap_text_lines(text,selected,max(1,rect.width-padding*2))
    for size in range(getattr(font,'point_size',12),7,-1):
        selected=font if size==getattr(font,'point_size',12) else make_font(size)
        lines=wrap_text_lines(text,selected,max(1,rect.width-padding*2))
        if len(lines)*selected.get_linesize()<=rect.height-padding*2:break
    old=surface.get_clip();surface.set_clip(old.clip(rect))
    y=rect.centery-len(lines)*selected.get_linesize()//2
    for line in lines:
        rendered=selected.render(line,True,color)
        surface.blit(rendered,(rect.centerx-rendered.get_width()//2,y))
        y+=selected.get_linesize()
    surface.set_clip(old)


def draw_pixel_icon(surface, kind, cx, cy, color):
    """Dibuja iconos nítidos en pixel art sin cargar archivos externos."""
    if kind == "+":
        draw.rect(surface, color, (cx - 3, cy, 7, 1))
        draw.rect(surface, color, (cx, cy - 3, 1, 7))
    elif kind in ("x", "close", "delete"):
        for d in range(-2, 3):
            draw.rect(surface, color, (cx + d, cy + d, 1, 1))
            draw.rect(surface, color, (cx + d, cy - d, 1, 1))
    elif kind in ("check", "ok"):
        draw.rect(surface, color, (cx - 3, cy, 1, 2))
        draw.rect(surface, color, (cx - 2, cy + 1, 1, 2))
        draw.rect(surface, color, (cx - 1, cy + 2, 1, 2))
        draw.rect(surface, color, (cx, cy + 1, 1, 2))
        draw.rect(surface, color, (cx + 1, cy, 1, 2))
        draw.rect(surface, color, (cx + 2, cy - 1, 1, 2))
        draw.rect(surface, color, (cx + 3, cy - 2, 1, 2))
    elif kind in ("!", "info", "task"):
        draw.rect(surface, color, (cx, cy - 3, 1, 4))
        draw.rect(surface, color, (cx, cy + 2, 1, 1))
    elif kind=='quiz':
        for i,fill in enumerate((ROSE,AZURE,GOLD,EMERALD)):
            draw.rect(surface,fill,(cx-4+(i%2)*5,cy-4+(i//2)*5,4,4),border_radius=1)
    elif kind=='model':
        draw.rect(surface,color,(cx-5,cy-4,5,4),1)
        draw.rect(surface,color,(cx+1,cy+1,5,4),1)
        draw.line(surface,color,(cx-3,cy),(cx-3,cy+3))
        draw.line(surface,color,(cx-3,cy+3),(cx+1,cy+3))
    elif kind in ('book','class'):
        draw.rect(surface,color,(cx-5,cy-4,11,8),1)
        draw.line(surface,color,(cx,cy-4),(cx,cy+4))
        draw.line(surface,color,(cx-3,cy-1),(cx-1,cy-1))
    elif kind=='door':
        draw.rect(surface,color,(cx-4,cy-5,8,11),1)
        draw.rect(surface,color,(cx+1,cy,1,1))
    elif kind in ("sword", "attack"):
        draw.line(surface, color, (cx - 2, cy + 2), (cx + 2, cy - 2))
        draw.line(surface, color, (cx - 3, cy + 3), (cx - 1, cy + 1))
        draw.rect(surface, color, (cx + 1, cy - 3, 2, 2))
    elif kind in ("shield", "defense"):
        draw.polygon(surface, color, [(cx - 3, cy - 3), (cx + 3, cy - 3), (cx + 3, cy), (cx, cy + 4), (cx - 3, cy)])
    elif kind in ("wand", "star"):
        draw.rect(surface, color, (cx, cy - 3, 1, 7))
        draw.rect(surface, color, (cx - 3, cy, 7, 1))
        for d in (-1, 1):
            draw.rect(surface, color, (cx + d, cy + d, 1, 1))
            draw.rect(surface, color, (cx + d, cy - d, 1, 1))


def draw_mvp_banner(surface, rect, tick=0):
    """Pancarta dorada pixel art para celebrar el rendimiento MVP."""
    rect = pygame.Rect(rect)
    panel(surface, rect, fill=(48, 36, 12), accent=GOLD, shadow=True, radius=3)
    draw.rect(surface, (255, 235, 150), rect.inflate(-2, -2), 1, border_radius=2)
    font_mvp = make_font(16)
    font_sub = make_font(10)
    import math
    shimmer = int((math.sin(tick * 0.12) + 1.0) * 25)
    gold_glow = (min(255, 239 + shimmer), min(255, 193 + shimmer), 112)
    rendered = font_mvp.render("M V P", True, gold_glow)
    surface.blit(rendered, (rect.centerx - rendered.get_width() // 2, rect.y + 3))
    for x in (rect.centerx-rendered.get_width()//2-10,rect.centerx+rendered.get_width()//2+10):
        draw_pixel_icon(surface,'star',x,rect.y+9,gold_glow)
    sub_txt = font_sub.render("¡DESEMPEÑO SOBRESALIENTE! +3 PL", True, (240, 245, 215))
    surface.blit(sub_txt, (rect.centerx - sub_txt.get_width() // 2, rect.y + 20))


def button(surface,label,rect,font,selected=False,accent=MINT,fill=None,light=False,hover=True,pulse=False,icon=None):
    rect=pygame.Rect(rect)
    fill=fill or ((220,228,218) if light else (35,57,67) if selected else (25,40,55))
    if pulse:
        import math
        p = (math.sin(pygame.time.get_ticks() / 140.0) + 1.0) * 0.5
        fill = mix(fill, accent, 0.28 * p)
        accent = mix(accent, (255, 255, 255), 0.45 * p)
    display=pygame.display.get_surface()
    if hover and display and pygame.mouse.get_focused():
        mx,my=pygame.mouse.get_pos();dw,dh=display.get_size()
        if rect.collidepoint(mx*480/max(1,dw),my*300/max(1,dh)):
            fill=mix(fill,accent,.14)
    radius=min(rect.height//2,9) if rect.width<=35 else 3
    panel(surface,rect,fill,accent,shadow=True,radius=radius,selected=selected,light=light)
    if icon:
        draw_pixel_icon(surface, icon, rect.x + 8, rect.centery, accent if selected else TEXT)
        text_rect = pygame.Rect(rect.x + 12, rect.y, rect.width - 12, rect.height)
        centered(surface,label,text_rect,font,(37,62,69) if light else GOLD if selected else TEXT,padding=2)
    else:
        centered(surface,label,rect,font,(37,62,69) if light else GOLD if selected else TEXT,padding=3)


def backdrop(surface,tint=(15,25,39)):
    surface.blit(_backdrop(tuple(tint)),(0,0))


@lru_cache(maxsize=8)
def _backdrop(tint):
    art=pygame.Surface((480,300))
    for y in range(300):
        pygame.draw.line(art,mix(tint,(5,12,24),y/450),(0,y),(479,y))
    for y in range(12,300,16):
        for x in range(12,480,16):
            if (x+y)%48==0:art.set_at((x,y),mix(tint,(130,180,190),.10))
    return art


def board(surface,rect,exam=False):
    rect=pygame.Rect(rect)
    surface.blit(_board(rect.size,exam),rect)


@lru_cache(maxsize=12)
def _board(size,exam):
    w,h=size;art=pygame.Surface(size)
    art.fill((24,29,33))
    pygame.draw.rect(art,(91,68,47),(0,0,w,h),border_radius=2)
    for y in (1,3,h-4):pygame.draw.line(art,(135,105,68),(2,y),(w-3,y))
    for x in range(7,w,19):pygame.draw.line(art,(76,55,39),(x,1),(x+8,2))
    base=(37,40,48) if exam else (24,55,49)
    pygame.draw.rect(art,base,(4,5,w-8,h-11))
    for y in range(6,h-7):
        pygame.draw.line(art,mix(base,(44,81,67),.18*(1-y/h)),(5,y),(w-6,y))
    for i in range(w*h//220):
        x=6+(i*43)%max(1,w-13);y=7+(i*31)%max(1,h-17)
        art.set_at((x,y),mix(base,(130,160,128),.09))
    pygame.draw.line(art,(12,32,30),(4,5),(w-5,5))
    pygame.draw.line(art,(173,135,85),(3,h-5),(w-4,h-5))
    pygame.draw.rect(art,(223,227,205),(w-47,h-7,12,2))
    pygame.draw.rect(art,(216,177,111),(w-29,h-7,7,2))
    pygame.draw.rect(art,(66,79,70),(w-18,h-9,11,4))
    return art


def plant(surface,x,y,scale=1):
    def r(c,rect):draw.rect(surface,c,(x+rect[0]*scale,y+rect[1]*scale,rect[2]*scale,rect[3]*scale))
    r((37,55,48),(6,4,1,17))
    for xx,yy in [(0,5),(7,2),(1,12),(8,9)]:
        r((48,108,77),(xx,yy,6,4));r((91,148,98),(xx+1,yy,4,1))
    r((128,77,53),(2,20,11,2));r((155,99,65),(3,22,9,7));r((187,124,77),(3,22,2,6))


def window(surface,rect):
    x,y,w,h=pygame.Rect(rect)
    draw.rect(surface,(30,42,51),(x+1,y+2,w,h))
    draw.rect(surface,(176,170,144),(x,y,w,h))
    draw.rect(surface,(73,137,154),(x+2,y+2,w-4,h-4))
    draw.rect(surface,(145,185,169),(x+2,y+2,w-4,4))
    for i in range(4):
        xx=x+3+i*(w-6)//4
        draw.rect(surface,(48+i*4,83+i*5,84+i*4),(xx,y+h//2+(i%2)*3,max(3,w//5),h//2-3))
    draw.line(surface,(204,198,167),(x+w//2,y+1),(x+w//2,y+h-2),2)
    draw.line(surface,(195,190,161),(x+1,y+h//2),(x+w-2,y+h//2))
    draw.rect(surface,(210,194,157),(x-2,y+h,w+4,2))
    draw.line(surface,(172,209,203),(x+4,y+4),(x+w//2-3,y+4))


def desk(surface,rect):
    x,y,w,h=pygame.Rect(rect)
    draw.rect(surface,(22,29,35),(x+2,y+4,w,h),border_radius=2)
    draw.rect(surface,(62,48,40),(x,y,w,h),border_radius=2)
    draw.rect(surface,(131,94,62),(x,y,w,h-4),border_radius=2)
    draw.line(surface,(178,133,83),(x+2,y+1),(x+w-3,y+1))
    for i in range(3):
        yy=y+5+i*6
        draw.line(surface,(119,84,57),(x+4+i*3,yy),(x+w-5-i*4,yy))
    draw.line(surface,(81,59,43),(x+1,y+h-4),(x+w-2,y+h-4))
    for xx in (x+3,x+w-6):draw.rect(surface,(49,57,63),(xx,y+h-1,3,5))


def monitor_details(surface,rect):
    x,y,w,h=pygame.Rect(rect)
    draw.line(surface,(213,217,205),(x+1,y),(x+w-2,y))
    draw.line(surface,(83,104,110),(x+w-1,y+1),(x+w-1,y+h-1))
    draw.rect(surface,(123,211,173),(x+w-3,y+h-2,1,1))
    draw.line(surface,(67,82,88),(x+3,y+h+4),(x+w-2,y+h+4))
    for xx in range(x+3,x+w-3,3):draw.rect(surface,(130,144,145),(xx,y+h+3,1,1))


@lru_cache(maxsize=2)
def intro_room():
    art=_backdrop((16,26,39)).copy()
    pygame.draw.rect(art,(8,16,27),(76,35,330,227))
    pygame.draw.rect(art,(70,75,72),(78,30,324,228))
    for y in range(58,258,12):
        for x in range(80,402,24):
            c=(58,68,72) if (x//24+y//12)%2 else (61,71,74)
            pygame.draw.rect(art,c,(x,y,min(23,402-x),min(11,258-y)))
            pygame.draw.line(art,(66,76,78),(x+1,y+1),(min(x+21,401),y+1))
    pygame.draw.rect(art,(88,98,95),(78,30,324,28))
    pygame.draw.rect(art,(46,64,65),(78,54,324,4))
    pygame.draw.line(art,(164,153,119),(78,54),(401,54))
    for xx in (78,396):pygame.draw.rect(art,(74,86,82),(xx,58,6,200))
    window(art,(98,32,45,20));window(art,(337,32,45,20))
    # Las franjas de luz y los objetos quedan dentro del aula existente
    pygame.draw.polygon(art,(66,80,79),[(100,59),(140,59),(172,102),(124,102)])
    pygame.draw.polygon(art,(64,78,77),[(340,59),(380,59),(389,98),(358,98)])
    plant(art,93,73);plant(art,378,73)
    pygame.draw.rect(art,(43,34,27),(78,211,24,44))
    pygame.draw.rect(art,(177,142,92),(81,214,18,38))
    pygame.draw.rect(art,(94,71,50),(83,216,14,34))
    pygame.draw.rect(art,(46,76,83),(85,220,10,12))
    pygame.draw.rect(art,(211,191,133),(95,237,2,3))
    pygame.draw.line(art,(211,194,151),(82,251),(100,251),2)
    pygame.draw.rect(art,(125,104,75),(394,115,6,45))
    for i in range(5):pygame.draw.rect(art,[(162,117,80),(101,145,130),(203,170,100)][i%3],(395,119+i*7,4,5))
    board(art,(163,31,153,32))
    pygame.draw.ellipse(art,(35,45,49),(207,113,75,7))
    desk(art,(215,96,58,20))
    pygame.draw.rect(art,(226,222,197),(221,98,14,8))
    pygame.draw.line(art,(104,127,120),(223,100),(231,100))
    pygame.draw.rect(art,(74,119,103),(257,99,6,7))
    pygame.draw.line(art,(220,221,198),(258,99),(261,99))
    netbook(art,245,95)
    return art


def marco_portrait(surface,rect):
    x,y,w,h=pygame.Rect(rect)
    panel(surface,rect,(37,55,62),GOLD,shadow=False)
    # Silueta, solapas, camisa y lentes con puentes y reflejos
    draw.ellipse(surface,(26,42,49),(x+4,y+31,w-8,h-33))
    draw.polygon(surface,(91,115,90),[(x+5,y+h-3),(x+7,y+35),(x+16,y+30),(x+27,y+30),(x+w-6,y+36),(x+w-4,y+h-3)])
    draw.polygon(surface,(216,217,191),[(x+15,y+32),(x+24,y+32),(x+20,y+47)])
    draw.polygon(surface,(184,139,79),[(x+19,y+35),(x+22,y+35),(x+22,y+43),(x+20,y+46),(x+19,y+43)])
    draw.rect(surface,(205,158,116),(x+17,y+26,7,7))
    draw.rect(surface,(243,198,150),(x+10,y+10,22,19),border_radius=4)
    draw.rect(surface,(221,171,126),(x+10,y+24,22,4),border_radius=2)
    draw.rect(surface,(225,230,218),(x+9,y+5,24,9),border_radius=3)
    draw.rect(surface,(244,244,226),(x+12,y+5,17,3))
    draw.rect(surface,(185,200,192),(x+8,y+12,4,9))
    draw.rect(surface,(185,200,192),(x+30,y+12,3,9))
    for xx in (x+12,x+24):
        draw.rect(surface,(48,58,61),(xx,y+16,8,6),1,border_radius=2)
        draw.rect(surface,(58,67,65),(xx+3,y+18,2,2))
        draw.rect(surface,(201,222,210),(xx+1,y+17,2,1))
    draw.line(surface,(48,58,61),(x+20,y+18),(x+24,y+18))
    draw.line(surface,(168,117,91),(x+19,y+26),(x+25,y+26))
    draw.line(surface,(126,146,108),(x+7,y+37),(x+9,y+h-5))


def marco_sprite(surface,x,y):
    draw.ellipse(surface,(27,39,41),(x,y+21,18,4))
    draw.rect(surface,(73,64,51),(x+4,y+17,4,6))
    draw.rect(surface,(73,64,51),(x+10,y+17,4,6))
    draw.rect(surface,(30,33,34),(x+3,y+22,5,2))
    draw.rect(surface,(30,33,34),(x+10,y+22,6,2))
    draw.rect(surface,(64,84,65),(x+2,y+9,13,11))
    draw.rect(surface,(113,135,100),(x+2,y+9,3,9))
    draw.polygon(surface,(228,226,197),[(x+7,y+9),(x+11,y+9),(x+9,y+15)])
    draw.line(surface,(187,150,83),(x+9,y+11),(x+9,y+15))
    draw.rect(surface,(238,194,148),(x+3,y+2,11,8))
    draw.rect(surface,(218,227,213),(x+2,y,13,4),border_radius=1)
    draw.rect(surface,(179,195,184),(x+2,y+4,2,3))
    draw.rect(surface,(22,39,57),(x+4,y+5,4,3),1)
    draw.rect(surface,(22,39,57),(x+10,y+5,4,3),1)
    draw.line(surface,(37,51,50),(x+7,y+6),(x+10,y+6))
    draw.rect(surface,(233,189,141),(x,y+14,2,4))
    draw.rect(surface,(233,189,141),(x+15,y+14,2,4))


@lru_cache(maxsize=1)
def title_art():
    art=_backdrop((24,45,59)).copy()
    # Campus al anochecer, ventanas iluminadas y caminos de adoquines
    for i in range(35):
        x=(i*79+17)%480;y=(i*31+8)%132
        pygame.draw.rect(art,(106,149,158),(x,y,1,1))
    pygame.draw.circle(art,(217,213,174),(421,41),14)
    pygame.draw.circle(art,(41,62,71),(427,36),13)
    for x,w,h in [(0,88,145),(393,87,158)]:
        pygame.draw.rect(art,(35,54,62),(x,118,w,h))
        pygame.draw.rect(art,(68,84,86),(x-2,116,w+4,4))
        for yy in range(133,250,23):
            for xx in range(x+11,x+w-10,17):
                pygame.draw.rect(art,(16,35,46),(xx,yy,11,15))
                pygame.draw.rect(art,(190,156,96) if (xx+yy)%3 else (77,122,127),(xx+1,yy+1,9,12))
                pygame.draw.line(art,(60,71,71),(xx+5,yy),(xx+5,yy+13))
    pygame.draw.rect(art,(28,45,49),(0,259,480,41))
    for y in range(263,300,8):
        for x in range(-(y%16),480,23):
            pygame.draw.line(art,(44,61,62),(x,y),(x+21,y))
    for xx in (34,438):
        pygame.draw.rect(art,(72,91,90),(xx,166,3,94))
        pygame.draw.rect(art,(217,182,111),(xx-3,161,9,10))
        pygame.draw.line(art,(244,218,161),(xx-4,160),(xx+6,160))
        pygame.draw.ellipse(art,(55,68,61),(xx-18,257,40,5))
    plant(art,67,231,2);plant(art,388,231,2)
    return art


def advance_indicator(surface,center,tick,finished=False):
    x,y=center
    if finished:draw.circle(surface,MINT,(x,y),2)
    else:
        x+=round(math.sin(tick*.15)*2)
        draw.polygon(surface,MINT,[(x-3,y-4),(x+3,y),(x-3,y+4)])


def teacher_notice(surface,center,tick,completed=False):
    color=MINT if completed else GOLD
    if math.sin(tick*.14)<0:color=mix(color,(44,52,44),.38)
    draw.circle(surface,color,center,6)
    if completed:draw_pixel_icon(surface,'check',center[0],center[1],INK)
    else:centered(surface,'!',pygame.Rect(center[0]-5,center[1]-5,10,10),make_font(16),INK,padding=0)


def chair(surface,rect):
    x,y,w,h=pygame.Rect(rect)
    draw.ellipse(surface,(12,23,31),(x-2,y+h-4,w+4,6))
    draw.line(surface,(87,103,105),(x+w//2,y+h-7),(x+w//2,y+h-1),2)
    draw.line(surface,(87,103,105),(x+2,y+h-1),(x+w-2,y+h-1))
    panel(surface,pygame.Rect(x,y,w,h-5),(38,65,76),(89,133,141),shadow=False,radius=3)
    draw.line(surface,(67,104,115),(x+3,y+4),(x+w-4,y+4))


def netbook(surface,x,y):
    panel(surface,pygame.Rect(x,y,24,15),(64,82,92),(153,179,183),shadow=False,radius=2)
    draw.rect(surface,(13,35,44),(x+2,y+2,20,10))
    draw.line(surface,MINT,(x+4,y+5),(x+16,y+5))
    draw.line(surface,AZURE,(x+4,y+8),(x+12,y+8))
    draw.polygon(surface,(143,162,169),[(x,y+15),(x+24,y+15),(x+28,y+20),(x-3,y+20)])
    for dx in range(1,23,4):draw.line(surface,(64,83,97),(x+dx,y+16),(x+dx+1,y+18))
