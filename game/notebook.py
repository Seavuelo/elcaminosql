from game.visuals import panel, button, GOLD, PAPER
"""Cuaderno por secciones, búsqueda, ilustraciones y apuntes personales"""
import unicodedata
import pygame
from game.rendering import draw,make_font,draw_caret
from game.ui_helpers import paginate_text,draw_fitted_text,render_wrapped_text
from game.sql_syntax import draw_sql
from game.sql_editor import SQLBuffer
from game.learning_diagrams import illustration

SECTIONS=('Todo','Bases','Modelo','Año 1','Año 2','Año 3','Año 4','Mis notas')
FOUNDATION_NOTES=[
 (1,'SQL y SQLite','SQL es el lenguaje para pedir información o definir estructuras, SQLite es el motor que interpreta esas instrucciones','pipeline','lenguaje motor consulta SELECT FROM'),
 (1,'Filas, columnas y valores','Una fila reúne datos de una persona, NOMBRE es una columna y Moshi es un valor de esa característica','table','tabla fila columna atributo entidad registro'),
 (2,'Tipos de origen','VARCHAR representa texto, NUMERIC números y DATE fechas, el taller adapta esos tipos al motor SQLite','types','tipo VARCHAR TEXT NUMERIC NUMBER INTEGER REAL DATE BLOB'),
 (2,'Precisión y escala','NUMERIC(10,2) permite hasta diez dígitos en total y hasta dos decimales, capacidad máxima no significa longitud exacta, NUMERIC(10,0) permite guardar 12 porque usa solo dos de hasta diez posiciones','types','precision escala decimal numero'),
 (2,'NULL no es cero','NULL representa un dato que todavía no conocemos, un atributo opcional lo permite y uno obligatorio no','table','NULL obligatorio opcional ausencia'),
 (3,'UID primario y clave primaria','El UID distingue cada instancia, en el relacional se convierte en PK, si tiene varias partes la combinación completa debe ser única','key','UID PK primaria identificador clave compuesta'),
 (2,'Convención de nombres','Usamos entidades en singular y MAYÚSCULAS, como ESTUDIANTE, y atributos en minúsculas, como fecha_nacimiento, usa _ entre palabras y anio en lugar de año, es un estilo consistente y SQL admite otros','key','nombre singular mayusculas convencion atributos'),
 (4,'Relaciones 1:N','Una persona puede tener varias tutorías, la clave del lado uno pasa al lado muchos como FK, una tercera tabla normalmente no es necesaria','relation','relacion uno muchos foranea FK padre hijo'),
 (4,'Relaciones 1:1 y N:M','Una FK única representa 1:1, N:M necesita una tabla intermedia con las claves de ambos lados, cada fila representa una asociación','junction','cardinalidad muchos muchos uno uno intermedia UNIQUE'),
 (4,'Relación identificadora','La clave del padre forma parte de la clave primaria del hijo, no se copian todos sus atributos, ejemplo PEDIDO_ID y NUMERO_LINEA','relation','identificacion identificadora dependencia UID PK'),
 (4,'Opcionalidad y transferibilidad','Origen opcional permite FK NULL, destino opcional permite padres sin hijos, transferible permite cambiar el padre de una instancia','relation','transferible opcional punteada circulo pata gallo cardinalidad'),
 (5,'Del lógico al relacional','Las entidades se transforman en tablas y los atributos en columnas, las relaciones generan FK, UID y restricciones según sus propiedades','relation','logico relacional generar convertir DDL CREATE TABLE'),
]


def searchable(value):
    return ''.join(c for c in unicodedata.normalize('NFD',value.lower()) if unicodedata.category(c)!='Mn')


class StudentNotebook:
    def __init__(self,audio_manager,save_system):
        self.audio,self.save=audio_manager,save_system
        self.active=False
        self.current_page=0
        self.section='Todo'
        self.query=''
        self.search_focus=False
        self.editing=False
        self.dirty=False
        self.cursor=0
        self.scroll=0
        self.buffer=SQLBuffer()
        self.buttons=[]
        self.font_title=make_font(15)
        self.font_body=make_font(12)
        self.font_code=make_font(12)
        self.small=make_font(10)
        self.all_notes=[]
        for day,title,body,picture,keywords in FOUNDATION_NOTES:
            self.all_notes.append(dict(id='foundation_'+title,year=0,day=day,title=title,body=body,section='Modelo' if day>=3 else 'Bases',illustration=picture,keywords=keywords,is_sql=False))
        from game.foundations_content import DAYS
        from game.intro_voice_scripts import display_text
        for day,lesson in DAYS.items():
            for index,page in enumerate(lesson['pages']):
                body=display_text(page['body'])
                if page['columns']:
                    body+='\n\n'+' | '.join(page['columns'])+'\n'+'\n'.join(' | '.join(str(value) for value in row) for row in page['rows'])
                for part,text in enumerate(paginate_text(body,self.font_body,416,142,2)):
                    self.all_notes.append(dict(id=f'intro_d{day}_p{index}_{part}',year=0,day=day,title=page['title'],body=text,section='Modelo' if day>=3 else 'Bases',is_sql=False))
                if page['sql']:
                    self.all_notes.append(dict(id=f'intro_d{day}_sql{index}',year=0,day=day,title=page['title']+' | SQL',body=page['sql'],section='Modelo' if day>=3 else 'Bases',is_sql=True))
        from game.lessons import demonstration
        for year in range(1,5):
            for day in range(1,5):
                for index,item in enumerate(demonstration(year,day)):
                    result=' | '.join(item['columns'])
                    if item['columns']:
                        result+='\n'+'\n'.join(' | '.join('NULL' if v is None else str(v) for v in row) for row in item['rows'][:3])
                        if len(item['rows'])>3:result+=f"\nMuestra de 3 filas de {len(item['rows'])}"
                    for label,body,is_sql in [('Explicación de Marco',item['speech'],False),('Concepto',item['explanation'],False),('Ejemplo SQL',item['sql'],True),('Resultado y consejo',result+'\n\n'+item['error']+'\n\n'+item['check'],False)]:
                        if not body.strip():continue
                        for text in paginate_text(body,self.font_body,416,142,2):
                            self.all_notes.append(dict(id=f'y{year}d{day}_{index}',year=year,day=day,title=item['title']+' | '+label,body=text,section=f'Año {year}',is_sql=is_sql))

    def open(self):
        self.active=True
        self.audio.play_key()
        self.personal=self.save.data.get('personal_notes','')
        self.cursor=min(self.cursor,len(self.personal))

    def persist(self):
        if self.dirty:
            self.save.data['personal_notes']=self.personal
            self.save.save()
            self.dirty=False

    def close(self):
        self.persist()
        self.active=False
        self.search_focus=False
        self.editing=False

    def get_unlocked_notes(self):
        year,day=self.save.data.get('current_year',1),self.save.data.get('current_day',1)
        foundation=self.save.data.get('foundation',{'completed':True,'day':5})
        unlocked=[]
        for note in self.all_notes:
            if note['year']==0:
                allowed=foundation.get('completed') or note['day']<=foundation.get('day',1)
            else:
                allowed=foundation.get('completed',False) and (note['year']<year or note['year']==year and note['day']<=day)
            haystack=searchable(note['title']+' '+note['body']+' '+note.get('keywords',''))
            if allowed and (self.section=='Todo' or note['section']==self.section) and all(term in haystack for term in searchable(self.query).split()):
                unlocked.append(note)
        personal=self.save.data.get('personal_notes','')
        if self.section=='Todo' and self.query and personal and all(term in searchable(personal) for term in searchable(self.query).split()):
            for text in paginate_text(personal,self.font_body,416,142,2):
                unlocked.append(dict(title='Mis notas',body=text,section='Mis notas',is_sql=False))
        return unlocked

    def set_section(self,value):
        self.persist()
        self.section=value
        self.current_page=0
        self.editing=value=='Mis notas'
        self.search_focus=False
        self.cursor=len(self.personal)

    def handle_event(self,event):
        if not self.active:return False
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            for rect,callback in self.buttons:
                if rect.collidepoint(event.pos):callback();return True
        if event.type!=pygame.KEYDOWN:return False
        mod=getattr(event,'mod',0)
        if event.key==pygame.K_f and mod&pygame.KMOD_CTRL or event.key==pygame.K_SLASH and not self.editing:
            self.search_focus=True;self.editing=False;return True
        if self.search_focus:
            if event.key in (pygame.K_RETURN,pygame.K_ESCAPE):self.search_focus=False
            elif event.key==pygame.K_BACKSPACE:self.query=self.query[:-1]
            elif event.unicode and event.unicode.isprintable():self.query=(self.query+event.unicode)[:80]
            self.current_page=0
            return True
        if self.editing:
            if event.key==pygame.K_ESCAPE:
                self.persist();self.editing=False;return True
            movements={pygame.K_LEFT:'left',pygame.K_RIGHT:'right',pygame.K_UP:'up',pygame.K_DOWN:'down',pygame.K_HOME:'home',pygame.K_END:'end'}
            if event.key in movements:
                self.cursor=self.buffer.move(self.personal,self.cursor,movements[event.key],bool(mod&pygame.KMOD_SHIFT),bool(mod&pygame.KMOD_CTRL));return True
            if mod&pygame.KMOD_CTRL and event.key==pygame.K_a:self.buffer.anchor=0;self.cursor=len(self.personal);return True
            if event.key in (pygame.K_BACKSPACE,pygame.K_DELETE):
                a,b=self.buffer.selection(self.cursor)
                if a==b:self.buffer.anchor=max(0,self.cursor-1) if event.key==pygame.K_BACKSPACE else min(len(self.personal),self.cursor+1)
                value=''
            elif event.key==pygame.K_RETURN:value='\n'
            elif event.unicode and event.unicode.isprintable() and not mod&pygame.KMOD_CTRL:value=event.unicode
            else:return True
            self.personal,self.cursor=self.buffer.replace(self.personal,self.cursor,value)
            self.dirty=True
            return True
        if event.key in (pygame.K_ESCAPE,pygame.K_n,pygame.K_F1):self.close()
        elif event.key in (pygame.K_RIGHT,pygame.K_d,pygame.K_PAGEDOWN):self.current_page=min(max(0,len(self.get_unlocked_notes())-1),self.current_page+1)
        elif event.key in (pygame.K_LEFT,pygame.K_a,pygame.K_PAGEUP):self.current_page=max(0,self.current_page-1)
        elif self.section=='Mis notas' and event.key==pygame.K_RETURN:self.editing=True
        return True

    def button(self,surface,label,rect,callback,selected=False):
        rect=pygame.Rect(rect)
        button(surface,label,rect,self.small,selected=selected,accent=(63,122,113),light=True)
        self.buttons.append((rect,callback))

    def draw(self,surface):
        if not self.active:return
        self.buttons=[]
        panel(surface,pygame.Rect(12,10,456,280),(81,69,56),GOLD)
        draw.rect(surface,PAPER,(17,15,446,270),border_radius=3)
        draw.line(surface,(208,193,166),(21,72),(459,72))
        draw.line(surface,(218,172,149),(23,76),(23,256))
        for yy in range(96,254,14):draw.line(surface,(224,217,198),(25,yy),(457,yy))
        for yy in range(30,280,20):
            draw.circle(surface,(87,77,62),(16,yy),2)
            draw.line(surface,(188,178,151),(11,yy),(18,yy),2)

        self.button(surface,'Buscar: '+self.query,(25,23,388,20),lambda:setattr(self,'search_focus',True),self.search_focus)
        self.button(surface,'Limpiar',(417,23,37,20),lambda:setattr(self,'query',''))
        for i,section in enumerate(SECTIONS):self.button(surface,section,(25+i*54,49,51,19),lambda s=section:self.set_section(s),self.section==section)
        if self.section=='Mis notas':
            draw_fitted_text(surface,'Mis apuntes | '+('Escribiendo, Esc guarda' if self.editing else 'Enter para escribir'),pygame.Rect(29,77,420,20),self.font_title,(35,55,75),padding=0)
            rect=pygame.Rect(29,104,420,148)
            lines=self.personal.split('\n')
            row=self.personal[:self.cursor].count('\n')
            column=self.cursor-(self.personal.rfind('\n',0,self.cursor)+1)
            line_h=self.font_body.get_linesize()+2
            self.scroll=max(0,min(self.scroll,row))
            self.scroll=max(self.scroll,row-max(1,rect.height//line_h)+1)
            clip=surface.get_clip();surface.set_clip(clip.clip(rect))
            xscroll=max(0,self.font_body.size(lines[row][:column])[0]-rect.width+4)
            for i,line in enumerate(lines[self.scroll:self.scroll+rect.height//line_h],self.scroll):surface.blit(self.font_body.render(line,True,(35,50,65)),(rect.x-xscroll,rect.y+(i-self.scroll)*line_h))
            if self.editing:
                draw_caret(surface,rect.x+self.font_body.size(lines[row][:column])[0]-xscroll,rect.y+(row-self.scroll)*line_h,self.font_body.get_height(),(25,125,100))
            surface.set_clip(clip)
        else:
            notes=self.get_unlocked_notes()
            self.current_page=min(self.current_page,max(0,len(notes)-1))
            if notes:
                note=notes[self.current_page]
                draw_fitted_text(surface,note['title'],pygame.Rect(29,77,420,22),self.font_title,(35,55,75),padding=0)
                if note.get('illustration'):
                    draw_fitted_text(surface,note['body'],pygame.Rect(29,105,420,72),self.font_body,(35,55,65),padding=0)
                    illustration(surface,note['illustration'],pygame.Rect(29,185,420,65),light=True)
                elif note.get('is_sql'):draw_sql(surface,note['body'],(29,107),self.font_code,light=True)
                else:render_wrapped_text(surface,note['body'],pygame.Rect(29,105,420,148),self.font_body,color=(35,55,65),padding=0,line_spacing=2)
            else:render_wrapped_text(surface,'No hay resultados en esta sección, revisa el término o continúa las clases para desbloquear contenido',pygame.Rect(29,110,420,100),self.font_body,color=(55,70,80),padding=0)
            self.button(surface,'<',(25,261,30,17),lambda:setattr(self,'current_page',max(0,self.current_page-1)))
            self.button(surface,'>',(61,261,30,17),lambda:setattr(self,'current_page',min(max(0,len(notes)-1),self.current_page+1)))
            draw_fitted_text(surface,f'{self.current_page+1 if notes else 0}/{len(notes)} | Secciones y buscador',pygame.Rect(104,261,290,16),self.small,(85,110,120),padding=0)
        self.button(surface,'Cerrar',(403,261,50,17),self.close)
