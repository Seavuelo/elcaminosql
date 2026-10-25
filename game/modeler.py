from game.visuals import button, MINT
"""Lienzo y editor de tablas para el taller, sin tocar la base de la partida"""
from copy import deepcopy
import sqlite3
import pygame
from game.data_model import TYPES
from game.rendering import draw, make_font, draw_caret
from game.sql_syntax import draw_sql
from game.ui_helpers import draw_fitted_text, render_wrapped_text, paginate_text, draw_sql_grid_table

ROW_HEIGHT = 22

class VisualModeler:
    def __init__(self, model, on_change, on_test):
        self.model, self.on_change, self.on_test = model, on_change, on_test
        self.font = make_font(12)
        self.small = make_font(11)
        self.title = make_font(14)
        self.canvas = pygame.Rect(12,40,290,181)
        self.selected = None
        self.old_column = None
        self.draft = dict(name='',type='INTEGER',pk=False,not_null=False)
        self.field = None
        self.text = ''
        self.replace_text = False
        self.scroll = 0
        self.dragging = None
        self.buttons = []
        self.cards = []
        self.view_pages = []
        self.view_index = 0
        self.status = 'Nueva tabla crea una caja, pulsa una columna para editarla, arrastra el encabezado para mover la tabla, rueda del ratón para recorrer el lienzo'

    def change(self):
        self.on_change(self.model.tables)

    def select(self, table, column=None):
        self.selected = table['name']
        self.field = None
        self.old_column = column['name'] if column else None
        self.draft = deepcopy(column) if column else dict(name='',type='INTEGER',pk=False,not_null=False)

    def action(self, callback):
        try:
            callback()
        except (ValueError,sqlite3.Error) as exc:
            self.status = str(exc)

    def edit_name(self, field, value):
        self.field, self.text, self.replace_text = field,value,True

    def commit_text(self):
        if self.field == 'new_table':
            table = self.model.add_table(self.text)
            self.select(table)
            self.status = 'Tabla creada, escribe el nombre de la primera columna y pulsa Guardar'
        elif self.field == 'table':
            old = self.selected
            self.model.rename_table(old,self.text)
            self.selected = self.text.strip().lower()
            self.status = 'Tabla renombrada, sus referencias también se actualizaron'
        elif self.field == 'column':
            self.draft['name'] = self.text
        self.field = None
        self.change()

    def save_column(self):
        if not self.selected:
            raise ValueError('Crea o selecciona una tabla antes de añadir columnas')
        if self.field == 'column':
            self.draft['name'] = self.text
        self.model.set_column(self.selected,self.draft,self.old_column)
        name = self.draft['name'].strip().lower()
        column = next(c for c in self.model.table(self.selected)['columns'] if c['name']==name)
        self.select(self.model.table(self.selected),column)
        self.change()
        self.status = 'Columna guardada, PK identifica la fila, NN exige un valor, FK relaciona esta columna con otra tabla'

    def new_column(self):
        if not self.selected:
            raise ValueError('Selecciona primero una tabla')
        self.select(self.model.table(self.selected))
        self.edit_name('column','')

    def delete_column(self):
        if not self.old_column:
            raise ValueError('Selecciona una columna del lienzo para quitarla')
        self.model.delete_column(self.selected,self.old_column)
        self.select(self.model.table(self.selected))
        self.change()
        self.status = 'Columna eliminada del diseño del taller'

    def delete_table(self):
        if not self.selected:
            raise ValueError('Selecciona primero una tabla')
        self.model.delete_table(self.selected)
        self.selected = None
        self.field = None
        self.change()
        self.status = 'Tabla eliminada del diseño del taller'

    def cycle_type(self):
        self.draft['type'] = TYPES[(TYPES.index(self.draft['type'])+1)%len(TYPES)]
        self.status = 'INTEGER: enteros, TEXT: palabras, REAL: decimales, BLOB: bytes, recuerda guardar la columna'

    def toggle(self, key):
        self.draft[key] = not self.draft.get(key,False)
        if key == 'pk' and self.draft['pk']:
            self.draft['not_null'] = True

    def cycle_reference(self):
        choices = [None]+[dict(table=t['name'],column=c['name']) for t in self.model.tables for c in t['columns']
                         if c.get('pk') and c['type']==self.draft['type']
                         and (t['name'],c['name']) != (self.selected,self.old_column)]
        current = self.draft.get('reference')
        index = choices.index(current) if current in choices else 0
        selected = choices[(index+1)%len(choices)]
        if selected:
            self.draft['reference'] = selected
            self.status = f"FK: {self.selected}.{self.draft['name']} apunta a {selected['table']}.{selected['column']}, guarda para crear la relación"
        else:
            self.draft.pop('reference',None)
            self.status = 'Sin referencia, primero crea una PK del mismo tipo en la tabla de destino'

    def inspect_sql(self):
        self.view_pages = []
        for sql in self.model.statements():
            for text in paginate_text(sql,self.font,400,164,1):
                self.view_pages.append(dict(title='SQL generado por tu modelo',sql=text))
        self.view_index = 0

    def check(self):
        conn = self.model.connection()
        conn.close()
        self.status = 'SQLite construyó tus tablas y referencias en memoria, esto valida la estructura, usa Probar datos para comprobar las reglas del taller'

    def test_data(self):
        result = self.model.demonstrate_integrity()
        self.view_pages = [dict(title='estudiantes, datos de prueba',columns=['id','nombre','promedio'],rows=result['estudiantes']),
                           dict(title='tutorias, dos filas para la misma persona',columns=['id','estudiante_id','tema'],rows=result['tutorias'])]
        checks = '\n\n'.join(('RECHAZADO correctamente: ' if passed else 'REVISAR: ') + title for title,passed in result['checks'])
        self.view_pages.append(dict(title='Restricciones comprobadas por SQLite',body=checks))
        self.view_index = 0
        self.on_test(all(passed for _,passed in result['checks']))
        self.status = 'Prueba en memoria terminada, estos datos no se guardan en la base de la carrera'

    def handle_event(self,event):
        if self.view_pages:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE,pygame.K_F2):
                    self.view_pages = []
                elif event.key in (pygame.K_RIGHT,pygame.K_RETURN,pygame.K_SPACE):
                    if self.view_index+1 < len(self.view_pages):
                        self.view_index += 1
                    else:
                        self.view_pages = []
                elif event.key == pygame.K_LEFT:
                    self.view_index = max(0,self.view_index-1)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.view_index+1 < len(self.view_pages):
                    self.view_index += 1
                else:
                    self.view_pages = []
            return True
        if self.field and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.field = None
            elif event.key == pygame.K_RETURN:
                self.action(self.commit_text)
            elif event.key == pygame.K_BACKSPACE:
                self.text = '' if self.replace_text else self.text[:-1]
                self.replace_text = False
            elif event.key == pygame.K_a and getattr(event,'mod',0)&pygame.KMOD_CTRL:
                self.replace_text = True
            elif event.unicode and event.unicode.isprintable() and not getattr(event,'mod',0)&pygame.KMOD_CTRL:
                self.text = ('' if self.replace_text else self.text) + event.unicode
                self.text = self.text[:32]
                self.replace_text = False
            return True
        if event.type == pygame.MOUSEWHEEL:
            bottom = max((t['y']+30+len(t['columns'])*ROW_HEIGHT for t in self.model.tables),default=0)
            self.scroll = max(0,min(max(0,bottom-self.canvas.height+12),self.scroll-event.y*30))
            return True
        if event.type == pygame.MOUSEMOTION and self.dragging:
            table = self.model.table(self.dragging[0])
            table['x'] = max(0,min(self.canvas.width-136,event.pos[0]-self.canvas.x-self.dragging[1]))
            table['y'] = max(0,event.pos[1]-self.canvas.y+self.scroll-self.dragging[2])
            return True
        if event.type == pygame.MOUSEBUTTONUP and self.dragging:
            self.dragging = None
            self.change()
            return True
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.field == 'column':
                self.draft['name'] = self.text
            if self.field in ('new_table','table'):
                return True
            self.field = None
            for rect,callback in self.buttons:
                if rect.collidepoint(event.pos):
                    self.action(callback)
                    return True
            if self.canvas.collidepoint(event.pos):
                for rect,table in reversed(self.cards):
                    if rect.collidepoint(event.pos):
                        offset = event.pos[1]-rect.y
                        if offset < 20:
                            self.select(table)
                            self.dragging = (table['name'],event.pos[0]-rect.x,offset)
                        else:
                            index = (offset-22)//ROW_HEIGHT
                            if 0 <= index < len(table['columns']):
                                self.select(table,table['columns'][index])
                        return True
            return True
        return False

    def button(self,surface,label,rect,callback,color=(30,55,76)):
        rect = pygame.Rect(rect)
        button(surface,label,rect,self.small,accent=MINT,fill=color)
        self.buttons.append((rect,callback))

    def field_box(self,surface,label,rect,field,value):
        text = self.text if self.field==field else value
        self.button(surface,label+': '+text,rect,lambda:self.edit_name(field,value),(20,36,52))
        if self.field==field:
            draw.rect(surface,(90,210,220),rect,1)

    def draw(self,surface):
        self.buttons,self.cards = [],[]
        if self.view_pages:
            page = self.view_pages[self.view_index]
            draw.rect(surface,(14,28,40),(12,40,456,252))
            surface.blit(self.title.render(page['title'],True,(255,195,80)),(24,50))
            if 'sql' in page:
                draw_sql(surface,page['sql'],(24,78),self.font)
            elif 'columns' in page:
                draw_sql_grid_table(surface,pygame.Rect(24,78,432,168),page['columns'],page['rows'],font=self.font)
            else:
                render_wrapped_text(surface,page['body'],pygame.Rect(24,78,432,170),self.font,padding=0,line_spacing=2)
            draw_fitted_text(surface,f"{self.view_index+1}/{len(self.view_pages)}",pygame.Rect(24,267,432,17),self.small,(120,220,230))
            return
        draw.rect(surface,(13,23,34),self.canvas)
        old_clip = surface.get_clip()
        surface.set_clip(old_clip.clip(self.canvas))
        for x in range(self.canvas.x,self.canvas.right,12):
            draw.line(surface,(22,35,46),(x,self.canvas.y),(x,self.canvas.bottom))
        for table in self.model.tables:
            self.cards.append((pygame.Rect(self.canvas.x+table['x'],self.canvas.y+table['y']-self.scroll,136,26+ROW_HEIGHT*len(table['columns'])),table))
        positions = {t['name']:r for r,t in self.cards}
        for rect,table in self.cards:
            for i,col in enumerate(table['columns']):
                ref = col.get('reference')
                if ref and ref['table'] in positions:
                    target = self.model.table(ref['table'])
                    index = next(j for j,c in enumerate(target['columns']) if c['name']==ref['column'])
                    dest = positions[ref['table']]
                    source_right = rect.centerx < dest.centerx
                    start = (rect.right if source_right else rect.x,rect.y+31+i*ROW_HEIGHT)
                    end = (dest.x if source_right else dest.right,dest.y+31+index*ROW_HEIGHT)
                    draw.line(surface,(110,215,170),start,end,2)
                    draw.circle(surface,(110,215,170),start,3)
                    direction = -1 if source_right else 1
                    draw.polygon(surface,(110,215,170),[end,(end[0]+direction*6,end[1]-4),(end[0]+direction*6,end[1]+4)])
        for rect,table in self.cards:
            draw.rect(surface,(23,42,57),rect,border_radius=3)
            draw.rect(surface,(255,195,80) if table['name']==self.selected else (65,115,145),rect,1,border_radius=3)
            draw.rect(surface,(35,65,82),(rect.x+1,rect.y+1,rect.width-2,18))
            draw_fitted_text(surface,table['name'],pygame.Rect(rect.x+5,rect.y+1,126,18),self.font,(235,245,250),padding=0)
            for index,col in enumerate(table['columns']):
                tags = ('PK ' if col.get('pk') else '')+('FK ' if col.get('reference') else '')
                label = tags+col['name']+' '+col['type']+(' NN' if col.get('not_null') else '')
                color = (255,210,100) if col.get('pk') else (125,235,195) if col.get('reference') else (220,230,240)
                if table['name']==self.selected and col['name']==self.old_column:
                    draw.rect(surface,(45,68,82),(rect.x+2,rect.y+22+index*ROW_HEIGHT,132,ROW_HEIGHT))
                draw_fitted_text(surface,label,pygame.Rect(rect.x+5,rect.y+22+index*ROW_HEIGHT,126,ROW_HEIGHT),self.small,color,padding=0)
        if not self.model.tables:
            render_wrapped_text(surface,'Tu lienzo está vacío\n\nPulsa Nueva tabla para empezar\n\nCada caja representa una tabla, las líneas mostrarán las relaciones',self.canvas.inflate(-24,-24),self.font,color=(170,195,210),padding=0)
        surface.set_clip(old_clip)
        draw.rect(surface,(23,36,50),(308,40,160,181))
        if self.selected:
            self.field_box(surface,'Tabla',(314,45,148,18),'table',self.selected)
            self.field_box(surface,'Columna',(314,71,148,18),'column',self.draft['name'])
            self.button(surface,self.draft['type'],(314,96,88,18),self.cycle_type)
            self.button(surface,'PK '+('sí' if self.draft.get('pk') else 'no'),(407,96,55,18),lambda:self.toggle('pk'))
            self.button(surface,'NN '+('obligatorio' if self.draft.get('not_null') else 'permite NULL'),(314,120,148,18),lambda:self.toggle('not_null'))
            ref = self.draft.get('reference')
            label = 'FK: '+ref['table']+'.'+ref['column'] if ref else 'FK: sin referencia'
            self.button(surface,label,(314,144,148,18),self.cycle_reference)
            self.button(surface,'Guardar',(314,168,70,18),self.save_column)
            self.button(surface,'Nueva col.',(390,168,72,18),self.new_column)
            self.button(surface,'Quitar columna',(314,194,148,18),self.delete_column,(68,38,45))
        else:
            render_wrapped_text(surface,'Selecciona una tabla o crea una nueva\n\nPK: clave primaria\nNN: valor obligatorio\nFK: clave foránea\n\nLas líneas van de FK hacia PK',pygame.Rect(318,49,140,161),self.font,color=(200,220,230),padding=0)
        self.button(surface,'Nueva tabla',(12,228,84,19),lambda:self.edit_name('new_table',''))
        self.button(surface,'Quitar tabla',(102,228,84,19),self.delete_table,(68,38,45))
        self.button(surface,'Ver SQL',(192,228,80,19),self.inspect_sql)
        self.button(surface,'Comprobar',(278,228,90,19),self.check)
        self.button(surface,'Probar datos',(374,228,94,19),self.test_data)
        render_wrapped_text(surface,self.status,pygame.Rect(16,253,448,41),self.small,color=(195,220,225),padding=0,line_spacing=1)
        if self.field in ('new_table','table'):
            draw.rect(surface,(16,32,48),(65,86,350,110),border_radius=4)
            draw.rect(surface,(90,210,220),(65,86,350,110),1,border_radius=4)
            surface.blit(self.title.render('Nombre de la tabla',True,(255,195,80)),(78,98))
            draw.rect(surface,(8,18,28),(78,121,324,24))
            surface.blit(self.font.render(self.text,True,(240,245,250)),(85,128))
            draw_caret(surface,85+self.font.size(self.text)[0],128,self.font.get_height(),(110,235,190))
            render_wrapped_text(surface,'Enter: guardar, Esc: cancelar\nLetras sin tildes, números y guion bajo',pygame.Rect(78,155,324,34),self.small,padding=0)
