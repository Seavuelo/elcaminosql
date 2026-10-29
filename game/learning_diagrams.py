from game.visuals import panel, centered, mix
"""Ilustraciones de pizarra reutilizadas en las notas"""
import pygame
from game.rendering import draw,make_font
from game.ui_helpers import draw_fitted_text


def illustration(surface,kind,rect,light=False,variant=None):
    x,y,w,h=pygame.Rect(rect)
    ink=(35,65,85) if light else (220,240,230)
    accent=(30,105,150) if light else (100,200,255)
    gold=(155,90,20) if light else (255,210,110)
    font=make_font(12)
    def box(label,r,color=ink):
        r=pygame.Rect(r)
        fill=(230,232,216) if light else (27,61,54)
        panel(surface,r,fill,color,shadow=True,radius=3)
        parts=label.split('\n')
        if len(parts)>1:
            header=max(13,min(22,r.height//len(parts)))
            draw.rect(surface,mix(fill,color,.12),(r.x+2,r.y+2,r.width-4,header),border_radius=2)
            centered(surface,parts[0],pygame.Rect(r.x+3,r.y+1,r.width-6,header),font,color,padding=1)
            centered(surface,'\n'.join(parts[1:]),pygame.Rect(r.x+3,r.y+header+1,r.width-6,r.height-header-3),font,ink,padding=1)
        else:centered(surface,label,r,font,color,padding=2)
    def arrow(a,b):
        draw.line(surface,accent,a,b,2)
        draw.polygon(surface,accent,[b,(b[0]-6,b[1]-4),(b[0]-6,b[1]+4)])
    flows={
        'filter':('NOTA 3\n3 < 4: sí','NOTA 4\n4 < 4: no','NOTA 4\n4 <= 4: sí'),
        'sort':('SIN ORDEN\n5 | 3 | 7','ASC\n3 | 5 | 7','DESC\n7 | 5 | 3'),
        'paging':('ORDENAR\n1 | 2 | 3 | 4','PÁGINA 1\nLIMIT 2\nOFFSET 0: 1, 2','PÁGINA 2\nLIMIT 2\nOFFSET 2: 3, 4'),
        'update':('SELECT\nElegir y revisar','UPDATE\nSET costo = 14\nWHERE id = 1','COMPROBAR\nSolo cambió ID 1'),
        'delete':('SELECT\nRevisar ID 3','DELETE\nWHERE id = 3','TABLA\nConserva otras filas'),
        'aggregate':('DATOS\n1 | 0 | 1 | NULL','CONTEOS\nFilas: 4\nConocidos: 3','RESUMEN\nSUM: 2\nAVG: 2 / 3'),
        'grouping':('MATERIAS\n4, 4, 6 créditos','GROUP BY\nGrupo 4: dos\nGrupo 6: una','COUNT(*)\n4 -> 2\n6 -> 1'),
        'having':('WHERE\nElegir materias\ncupos > 0','GROUP BY\nAgrupar por créditos\nContar por grupo','HAVING\nElegir grupos\nCOUNT(*) >= 2'),
        'join':('ESTUDIANTE\n11 | Moshi','TUTORÍAS\n20 -> 11\n21 -> 11','COINCIDENCIAS\nMoshi | 20\nMoshi | 21'),
        'subquery':('INTERIOR\nIDs que asistieron','IN\n¿El ID pertenece\na ese conjunto?','EXTERIOR\nNombres de esos\nestudiantes'),
        'leftjoin':('IZQUIERDA\n11 | Moshi\n12 | Carlos','TUTORÍAS\n20 -> 11','LEFT JOIN\nMoshi | 20\nCarlos | NULL'),
        'view':('CREATE VIEW\nGuardar una consulta','CAMBIA EL ORIGEN\nUna materia ya\nno cumple el filtro','CONSULTAR VISTA\nSu resultado\nrefleja el cambio'),
        'index':('SIN AYUDA\nRevisar candidatos','ÍNDICE\nEstructura organizada\npara buscar','COMPARAR\nPlan de ejecución\ny mediciones'),
    }
    if kind=='type_mapping':
        for i,(left,right) in enumerate([('VARCHAR','TEXT'),('NUMERIC','INTEGER / REAL / NUMERIC'),('DATE','TEXT con validación')]):
            yy=y+i*h*.33
            box(left,(x,yy,w*.34,h*.28),gold)
            arrow((x+w*.36,yy+h*.14),(x+w*.44,yy+h*.14))
            box(right,(x+w*.46,yy,w*.54,h*.28),accent)
    elif kind=='capacity':
        for i in range(10):
            cell=pygame.Rect(x+i*w*.101,y+h*.18,w*.088,h*.35)
            box('12'[i] if i<2 else ' ',cell,gold if i<2 else ink)
        draw_fitted_text(surface,'12 usa 2 de hasta 10 posiciones',pygame.Rect(x,y+h*.62,w,h*.3),font,accent,padding=0)
    elif kind=='precision':
        box('12.50\n4 dígitos, 2 decimales\nCabe en NUMERIC(4,2)',(x,y,w*.46,h*.94),accent)
        box('125.50\n5 dígitos, 2 decimales\nNo cabe en NUMERIC(4,2)',(x+w*.53,y,w*.47,h*.94),(230,145,127))
    elif kind=='names':
        box('ENTIDAD\nESTUDIANTE',(x,y,w*.43,h*.94),gold)
        box('ATRIBUTO\nfecha_nacimiento\nanio_ingreso',(x+w*.53,y,w*.47,h*.94),accent)
    elif kind=='affinity':
        box('Columna REAL\nTexto 6.5: número 6.5',(x,y,w*.46,h*.94),gold)
        box('Sin más reglas\npendiente puede seguir\nsiendo texto',(x+w*.53,y,w*.47,h*.94),accent)
    elif kind=='binary':
        box('DATE\n2026-04-18\nUna fecha',(x,y,w*.46,h*.94),gold)
        box('BLOB\n01001001 10100110\nBytes de un archivo',(x+w*.53,y,w*.47,h*.94),accent)
    elif kind in flows:
        for i,label in enumerate(flows[kind]):
            px=x+i*w*.35
            box(label,(px,y+h*.02,w*.30,h*.92),gold if i==(variant or 0)%3 else ink)
            if i<2:arrow((px+w*.305,y+h*.48),(x+(i+1)*w*.35-3,y+h*.48))
    elif kind=='welcome':
        box('Marco | profesor',(x+w*.25,y,w*.50,h*.30),gold)
        draw.line(surface,accent,(x+w*.5,y+h*.32),(x+w*.5,y+h*.47))
        draw.line(surface,accent,(x+w*.09,y+h*.47),(x+w*.91,y+h*.47))
        for i,label in enumerate(['Tú','Moshi','Carlos','Sofía','Matías']):
            px=x+i*w*.205;py=y+h*.58;pw=w*.18;ph=h*.38
            draw.line(surface,accent,(px+pw*.5,y+h*.47),(px+pw*.5,py))
            panel(surface,pygame.Rect(px,py,pw,ph),(230,232,216) if light else (27,61,54),accent if i==variant else ink)
            cx=round(px+pw*.5)
            draw.rect(surface,[(65,138,166),(152,113,79),(65,118,166),(126,101,157),(80,142,108)][i],(cx-7,py+14,14,7),border_radius=2)
            draw.rect(surface,(224,184,139),(cx-4,py+6,8,9),border_radius=2)
            draw.rect(surface,[(83,54,33),(177,130,76),(72,47,29),(80,53,35),(60,44,32)][i],(cx-5,py+3,10,5),border_radius=1)
            centered(surface,label,pygame.Rect(px+2,py+ph-14,pw-4,13),font,ink,padding=0)
    elif kind=='table':
        labels=[['ID','NOMBRE','PROMEDIO'],['1','Moshi','6.8'],['2','Carlos','5.0']]
        widths=[w*.16,w*.48,w*.36]
        for row,values in enumerate(labels):
            px=x
            for col,value in enumerate(values):
                r=(px,y+row*h*.24,widths[col],h*.24)
                active=variant is not None and ((variant%2==0 and row==1) or (variant%2==1 and col==1))
                if active:draw.rect(surface,(45,85,76) if not light else (210,230,225),r)
                box(value,r,accent if active else gold if row==0 else ink)
                px+=widths[col]
        draw_fitted_text(surface,'Columna: característica | Fila: una persona',pygame.Rect(x,y+h*.78,w,h*.2),font,accent,padding=0)
    elif kind=='pipeline':
        width=w*.25
        for i,label in enumerate(['SQL\npetición','SQLite\nmotor','Datos\nresultado']):
            px=x+i*w*.37;py=y+h*.06;cx=px+width*.5
            panel(surface,pygame.Rect(px,py,width,h*.79),(230,232,216) if light else (27,61,54),gold if i==(1 if variant is None else variant%2) else accent)
            if i==0:
                draw.line(surface,accent,(cx-15,py+12),(cx-22,py+19),2)
                draw.line(surface,accent,(cx-22,py+19),(cx-15,py+26),2)
                draw.line(surface,accent,(cx+15,py+12),(cx+22,py+19),2)
                draw.line(surface,accent,(cx+22,py+19),(cx+15,py+26),2)
                draw.line(surface,gold,(cx+3,py+11),(cx-3,py+27),2)
            elif i==1:
                draw.rect(surface,(201,215,195) if light else (45,89,76),(cx-19,py+12,38,20))
                for yy in (py+12,py+21,py+30):draw.ellipse(surface,accent,(cx-19,yy-4,38,8),1)
                draw.line(surface,accent,(cx-19,py+12),(cx-19,py+30))
                draw.line(surface,accent,(cx+18,py+12),(cx+18,py+30))
            else:
                draw.rect(surface,accent,(cx-21,py+8,42,25),1,border_radius=2)
                draw.rect(surface,gold,(cx-19,py+10,38,5))
                for yy in (py+20,py+26):draw.line(surface,accent,(cx-19,yy),(cx+18,yy))
                draw.line(surface,accent,(cx-7,py+16),(cx-7,py+31))
                draw.line(surface,accent,(cx+7,py+16),(cx+7,py+31))
            centered(surface,label,pygame.Rect(px+3,py+38,width-6,h*.79-40),font,gold if i==1 else ink,padding=0)
            if i<2:arrow((px+width+3,y+h*.43),(x+(i+1)*w*.37-4,y+h*.43))
    elif kind=='types' and h<80:
        for i,(label,value) in enumerate([('VARCHAR','Moshi'),('NUMERIC','6.8'),('DATE','2026-04-18')]):
            box(label+'\n'+value,(x+i*w*.34,y,w*.31,h*.94),gold if i==(variant or 0)%3 else ink)
    elif kind=='types':
        for i,(label,value) in enumerate([('VARCHAR','Moshi'),('NUMERIC','6.8'),('DATE','2026-10-24')]):
            px=x+i*w*.34;py=y+h*.05;pw=w*.31;ph=h*.80
            color=gold if variant is not None and i==variant%3 else [ink,accent,gold][i]
            panel(surface,pygame.Rect(px,py,pw,ph),(230,232,216) if light else (27,61,54),color)
            centered(surface,label,pygame.Rect(px+3,py+3,pw-6,16),font,color,padding=0)
            if i<2:centered(surface,'Aa' if i==0 else '1.0',pygame.Rect(px+3,py+21,pw-6,27),make_font(24),accent,padding=0)
            else:
                cx=px+pw*.5
                draw.rect(surface,accent,(cx-14,py+24,28,22),1,border_radius=2)
                draw.line(surface,gold,(cx-12,py+30),(cx+12,py+30),2)
                for xx in (-7,0,7):
                    for yy in (35,41):draw.rect(surface,accent,(cx+xx-1,py+yy,2,2))
            centered(surface,value,pygame.Rect(px+3,py+ph-22,pw-6,18),font,ink,padding=0)
    elif kind=='junction':
        for i,label in enumerate(['ESTUDIANTE\n* ID','INSCRIPCION\nESTUDIANTE_ID\nMATERIA_ID','MATERIA\n* ID']):
            box(label,(x+i*w*.355,y+h*.16,w*.29,h*.59),gold if i==1 else ink)
        arrow((x+w*.30,y+h*.43),(x+w*.35,y+h*.43))
        draw.line(surface,accent,(x+w*.65,y+h*.43),(x+w*.71,y+h*.43),2)
        draw_fitted_text(surface,'N:M se convierte en dos relaciones 1:N',pygame.Rect(x,y+h*.80,w,h*.19),font,accent,padding=0)
    elif kind=='scattered':
        for i,label in enumerate(['Lista de curso\nMoshi','Agenda de tutorías\nMoshi','Cambio de nombre\n¿Dónde corregimos?']):box(label,(x+i*w*.34,y+(i%2)*h*.15,w*.31,h*.60),gold if i==variant else ink)
        draw_fitted_text(surface,'La misma persona aparece en documentos diferentes',pygame.Rect(x,y+h*.80,w,h*.19),font,accent,padding=0)
    elif kind=='attributes':
        center=(x+w*.36,y+h*.33,w*.28,h*.37)
        box('ESTUDIANTE',center,gold)
        for i,(label,r) in enumerate([('NOMBRE',(x,y,w*.28,h*.3)),('PROMEDIO',(x+w*.72,y,w*.28,h*.3)),('ID',(x+w*.36,y+h*.77,w*.28,h*.22))]):
            draw.line(surface,accent,(x+w*.5,y+h*.5),(r[0]+r[2]/2,r[1]+r[3]/2))
            box(label,r,accent if i==(variant or 0) else ink)
    elif kind=='entities':
        box('ESTUDIANTE\nID | NOMBRE | PROMEDIO',(x,y,w*.43,h*.65),gold if variant==0 else ink)
        box('TUTORIA\nID | TEMA',(x+w*.59,y,w*.41,h*.65),accent if variant else ink)
        if variant:
            arrow((x+w*.44,y+h*.3),(x+w*.58,y+h*.3))
        draw_fitted_text(surface,'Entidad: qué representamos | Atributos: sus características',pygame.Rect(x,y+h*.79,w,h*.20),font,accent,padding=0)
    elif kind=='null':
        for i,label in enumerate(['NULL\ndato pendiente','0\nvalor numérico',"''\ntexto vacío"]):box(label,(x+i*w*.34,y+h*.12,w*.31,h*.65),gold if i==(variant or 0)%3 else ink)
    elif kind=='codes':
        box("TEXT\n'0012'\nConserva los ceros",(x,y,w*.43,h*.80),gold)
        box('INTEGER\n12\nEs una cantidad',(x+w*.57,y,w*.43,h*.80),accent)
    elif kind=='range':
        box('8.0\nEs un número',(x,y,w*.42,h*.70),ink)
        box('Nota entre 1 y 7\n8.0 no cumple',(x+w*.56,y,w*.44,h*.70),gold)
    elif kind=='identifying':
        box('PEDIDO\n* ID',(x,y,w*.35,h*.65),gold)
        box('LINEA_PEDIDO\n* PEDIDO_ID\n* NUMERO_LINEA',(x+w*.58,y,w*.42,h*.65),accent)
        arrow((x+w*.36,y+h*.3),(x+w*.57,y+h*.3))
        draw_fitted_text(surface,'Solo la clave participa en el UID del hijo',pygame.Rect(x,y+h*.80,w,h*.19),font,ink,padding=0)
    elif kind=='reparent':
        box('PADRE 1',(x,y,w*.30,h*.3),ink)
        box('PADRE 2',(x,y+h*.65,w*.30,h*.3),gold)
        box('HIJO\nFK al padre',(x+w*.60,y+h*.3,w*.40,h*.4),accent)
        arrow((x+w*.31,y+h*.8 if variant else y+h*.15),(x+w*.59,y+h*.5))
    elif kind=='conversion':
        box('LÓGICO\nEntidad + atributos',(x,y,w*.39,h*.7),gold if not variant else ink)
        box('RELACIONAL\nTabla + columnas',(x+w*.60,y,w*.40,h*.7),accent if variant else ink)
        arrow((x+w*.40,y+h*.35),(x+w*.59,y+h*.35))
    elif kind=='checks':
        for i,label in enumerate(['PK repetida\nRechazar','Nombre NULL\nRechazar','FK inexistente\nRechazar']):box(label,(x+i*w*.34,y,w*.31,h*.70),gold if i==(variant or 0)%3 else ink)
    elif kind=='key':
        box('ESTUDIANTE\n* ID = 1\nNOMBRE = Moshi',(x,y,w*.44,h*.7),gold)
        duplicate=variant is not None and variant%2==1
        box('ESTUDIANTE\n* ID = '+('1' if duplicate else '2')+'\nNOMBRE = Moshi',(x+w*.55,y,w*.44,h*.7),(240,115,110) if duplicate else ink)
        draw_fitted_text(surface,'ID repetido: se rechaza' if duplicate else 'El nombre puede repetirse, el UID completo no',pygame.Rect(x,y+h*.77,w,h*.2),font,accent,padding=0)
    else:
        box('ESTUDIANTE\n* ID',(x,y,w*.35,h*.65),gold if not variant else ink)
        box('TUTORIA\n* ID\nESTUDIANTE_ID',(x+w*.64,y,w*.36,h*.65),accent if variant else ink)
        a=(x+w*.35,y+h*.3);b=(x+w*.64,y+h*.3)
        draw.line(surface,accent,a,b,2)
        for delta in (-7,0,7): draw.line(surface,accent,(b[0]-12,b[1]),(b[0],b[1]+delta))
        draw.line(surface,accent,(a[0]+5,a[1]-6),(a[0]+5,a[1]+6))
        draw_fitted_text(surface,'1',pygame.Rect(a[0]+2,y-15,20,14),font,accent,padding=0)
        draw_fitted_text(surface,'N',pygame.Rect(b[0]-19,y-15,20,14),font,accent,padding=0)
        draw_fitted_text(surface,'Una persona puede tener varias tutorías',pygame.Rect(x,y+h*.77,w,h*.2),font,accent,padding=0)
