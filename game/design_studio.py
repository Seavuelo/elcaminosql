from game.visuals import panel, button, backdrop, draw_pixel_icon, GOLD, MINT, CRIMSON, AZURE, EMERALD, MUTED, BTN_DANGER, BTN_CREATE, BTN_SUCCESS, BTN_TASK, BTN_NEUTRAL
"""Editor lógico con formularios, relaciones, conversión, zoom y desplazamiento"""
from copy import deepcopy
import math
import pygame
from game.logical_model import LogicalDesign, ORIGIN_TYPES
from game.rendering import draw,make_font
from game.ui_helpers import draw_fitted_text,render_wrapped_text,paginate_text,draw_sql_grid_table
from game.sql_syntax import draw_sql

HELP = {
 'name':'Para las entidades usamos singular y MAYÚSCULAS, como ESTUDIANTE\n\nLos atributos pueden escribirse en minúsculas, como nombre o fecha_nacimiento\n\nUsa _ para separar palabras, anio en lugar de año y letras sin tildes, evita espacios, empieza con una letra',
 'type':'VARCHAR describe texto, por ejemplo Moshi\n\nNUMERIC describe números, como 12 o 6.5, DATE describe fechas\n\nAl convertir a SQLite, VARCHAR pasa a TEXT, NUMERIC conserva validaciones de precisión y escala, INTEGER es para enteros y REAL para decimales',
 'length':'Longitud es el máximo de caracteres permitidos, no una reserva fija de espacio\n\nCon longitud 1 cabe A, pero Ana tiene 3 caracteres y no cabe\n\nCon longitud 80 caben hasta 80 caracteres, con 100 hasta 100\n\nEn esta base generada, superar el máximo rechaza el registro, un límite muy pequeño impide guardar nombres reales y uno enorme permite textos innecesariamente largos',
 'precision':'Precisión es el máximo de dígitos totales, contando enteros y decimales\n\nNUMERIC(4,2) admite 12.50, son 4 dígitos y 2 decimales\n\n125.50 no cabe, necesita 5 dígitos\n\nEs una capacidad máxima, no necesitas llenar todas las posiciones',
 'scale':'Escala indica cuántos decimales se permiten\n\nNUMERIC(10,0) admite hasta 10 dígitos enteros y ningún decimal, el 12 cabe porque usa solo 2 de esas 10 posiciones\n\nEl 10 es un máximo, no la cantidad que cada valor debe tener\n\n12.5 no cabe con escala 0, para decimales elige otra escala',
 'uid':'UID primario identifica una instancia de la entidad, puedes marcar varios atributos, juntos formarán una clave primaria compuesta en el modelo relacional',
 'mandatory':'Obligatorio exige un valor, opcional permite NULL, no confundas dato desconocido con cero o texto vacío',
 'transfer_key':'Al convertir, lleva solo los atributos del identificador del origen al destino para formar la FK, si lo desmarcas la asociación queda solo en el modelo lógico, sin integridad automática',
 'source_optional':'Si el origen es opcional, una instancia del destino puede no tener padre, la FK acepta NULL y dibujamos la relación punteada',
 'target_optional':'Si el destino es opcional, un padre puede no tener hijos, exigir al menos uno necesita validación de proceso, una FK por sí sola no lo garantiza',
 'identifying':'La clave del padre forma parte de la clave primaria del hijo, no copia todos sus atributos, por ejemplo PEDIDO_ID y NUMERO_LINEA identifican una línea del pedido',
 'transferable':'Permite cambiar una instancia de padre después de asignarla, si se desmarca el SQLite generado añade un disparador que impide cambiar esa FK una vez asignada',
 'roles':'Los nombres describen ambos sentidos, ESTUDIANTE tiene TUTORIA y TUTORIA pertenece a ESTUDIANTE, no son columnas adicionales',
 'kind':'1:N lleva la clave del uno al muchos, 1:1 añade UNIQUE a la FK, N:M genera una tabla intermedia con ambas claves, no necesitas esa tercera tabla para una relación 1:N',
}


class DesignStudio:
    def __init__(self,design,on_change,on_notes=lambda:None,task=None,on_test=lambda passed:None,task_checklist=None):
        self.design,self.on_change,self.on_notes,self.task,self.on_test,self.task_checklist = design,on_change,on_notes,task,on_test,task_checklist
        self.font,self.small,self.title = make_font(12),make_font(10),make_font(15)
        self.zoom = .7
        self.offset = [30,55]
        self.mouse = (240,150)
        self.buttons=[]
        self.fields=[]
        self.cards=[]
        self.lines=[]
        self.form=None
        self.task_page=0
        self.focus=None
        self.selection=True
        self.cursor=0
        self.tab='general'
        self.status='Rueda: zoom, arrastra el fondo para mover el lienzo, clic en entidad o línea: propiedades, Ctrl+Z: deshacer'
        self.message=None
        self.message_index=0
        self.history=[]
        self.drag=None
        self.connect_kind=None
        self.source=None
        self.relational_tables=None
        self.attribute_index=None
        self.attr_scroll=0

    def remember(self):
        self.history.append(deepcopy(self.design.data))
        self.history=self.history[-30:]

    def changed(self):
        self.relational_tables=None
        self.on_change(deepcopy(self.design.data))

    def show(self,title,text,sql=False):
        self.message=[dict(title=title,body=page,sql=sql) for page in paginate_text(text,self.font,400,180,2)]
        self.message_index=0
        self.focus=None

    def action(self,callback):
        try:
            callback()
        except (ValueError,KeyError) as exc:
            self.show('Revisa el diseño',str(exc))

    def create_entity(self,current=None):
        self.old_entity=current['name'] if current else None
        self.entity_draft=deepcopy(current) if current else dict(name='',attributes=[],x=(150-self.offset[0])/self.zoom,y=(90-self.offset[1])/self.zoom)
        self.attr=dict(name='',type='VARCHAR',length=80,precision=10,scale=2,uid=False,mandatory=False)
        self.attribute_index=None
        self.attr_scroll=0
        self.form='entity'
        self.tab='general'
        self.focus=None

    def apply_attribute(self):
        value=LogicalDesign.attribute(self.attr)
        attrs=self.entity_draft['attributes']
        if any(a['name'].casefold()==value['name'].casefold() and i!=self.attribute_index for i,a in enumerate(attrs)):
            raise ValueError('Ya existe un atributo con ese nombre')
        if self.attribute_index is None:
            attrs.append(value)
        else:
            attrs[self.attribute_index]=value
        self.new_attribute()
        self.attr_scroll=max(0,len(attrs)-7)
        self.focus=(self.attr,'name')
        self.cursor=0
        self.selection=False
        self.status='Atributo aplicado al borrador, Guardar entidad confirma el conjunto'

    def new_attribute(self):
        self.attribute_index=None
        self.attr=dict(name='',type='VARCHAR',length=80,precision=10,scale=2,uid=False,mandatory=False)
        self.focus=None

    def select_attribute(self,index):
        self.attribute_index=index
        self.attr=deepcopy(self.entity_draft['attributes'][index])
        self.focus=None

    def remove_attribute(self):
        if self.attribute_index is not None:
            self.entity_draft['attributes'].pop(self.attribute_index)
            self.new_attribute()

    def save_entity(self):
        if self.tab=='attributes' and self.attr['name']:
            self.apply_attribute()
        self.remember()
        self.design.save_entity(self.entity_draft,self.old_entity)
        self.changed()
        self.form=None
        self.focus=None

    def delete_entity(self):
        if not self.old_entity:
            self.form=None
            return
        self.remember()
        self.design.delete_entity(self.old_entity)
        self.changed()
        self.form=None

    def create_relation(self,source,target,kind,current=None):
        self.relation_draft=deepcopy(current) if current else dict(name='R_'+source+'_'+target,source=source,target=target,kind=kind,
             source_role='TIENE',target_role='PERTENECE',source_optional=False,target_optional=True,identifying=False,transfer_key=True,transferable=True)
        self.form='relation'
        self.focus=None
        self.connect_kind=None
        self.source=None

    def save_relation(self):
        self.remember()
        self.design.save_relation(self.relation_draft)
        self.changed()
        self.form=None
        self.focus=None

    def delete_relation(self):
        self.remember()
        identifier=self.relation_draft.get('id')
        self.design.data['relations']=[r for r in self.design.relations if r['id']!=identifier]
        self.changed()
        self.form=None

    def relation_tool(self,kind):
        if len(self.design.entities)<2:
            raise ValueError('Crea primero dos entidades, después selecciona origen y destino de la relación')
        self.relational_tables=None
        self.connect_kind=kind
        self.source=None
        self.status='Relación '+kind+': pulsa primero la entidad de origen y después la de destino, Esc cancela'

    def convert(self):
        import sqlite3
        try:
            tables,warnings,violations=self.design.verify()
        except sqlite3.Error as exc:
            raise ValueError('SQLite no pudo construir el diseño, '+str(exc)) from exc
        if violations:
            raise ValueError('SQLite encontró una referencia incorrecta')
        self.relational_tables=tables
        self.fit()
        self.status='Modelo relacional generado, las columnas verdes proceden de las relaciones, clic en una tabla muestra su SQL'
        if warnings:
            self.show('Conversión y reglas del modelo','\n\n'.join(warnings))

    def switch_view(self):
        if self.relational_tables is not None:
            self.relational_tables=None
        else:
            self.convert()

    def fit(self):
        nodes=self.relational_tables if self.relational_tables is not None else self.design.entities
        if not nodes:
            return
        left=min(n['x'] for n in nodes)
        top=min(n['y'] for n in nodes)
        right=max(n['x']+210 for n in nodes)
        bottom=max(n['y']+32+len(n.get('attributes',n.get('columns',[])))*20 for n in nodes)
        self.zoom=max(.2,min(1.2,430/max(1,right-left),210/max(1,bottom-top)))
        self.offset=[24-left*self.zoom,48-top*self.zoom]

    def zoom_by(self,factor):
        old=self.zoom
        self.zoom=max(.2,min(2.,self.zoom*factor))
        self.offset=[self.mouse[i]-(self.mouse[i]-self.offset[i])*self.zoom/old for i in (0,1)]

    def undo(self):
        if self.history:
            self.design.data=self.history.pop()
            self.changed()
            self.status='Cambio deshecho'

    def test(self):
        tables,warnings,_=self.design.verify()
        self.on_test(True)
        self.show('Diseño comprobado',f'SQLite construyó {len(tables)} tablas y activó sus claves foráneas\n\n'+('\n\n'.join(warnings) if warnings else 'Las FK, UID, tipos y campos obligatorios se generaron sin errores')+'\n\nLa prueba valida estructura, las cardinalidades mínimas de hijos necesitan además una regla de proceso')

    def handle_event(self,event):
        if self.message:
            if event.type==pygame.KEYDOWN:
                if event.key==pygame.K_ESCAPE:
                    self.message=None
                elif event.key in (pygame.K_RETURN,pygame.K_RIGHT,pygame.K_SPACE):
                    self.message_index+=1
                    if self.message_index>=len(self.message): self.message=None
                elif event.key==pygame.K_LEFT:
                    self.message_index=max(0,self.message_index-1)
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                self.message_index+=1
                if self.message_index>=len(self.message): self.message=None
            return True
        if event.type==pygame.KEYDOWN:
            mod=getattr(event,'mod',0)
            if event.key==pygame.K_ESCAPE:
                if self.focus: self.focus=None
                elif self.form: self.form=None
                elif self.connect_kind: self.connect_kind=None
                else: return False
                return True
            if self.focus:
                obj,key=self.focus
                value=str(obj[key])
                if event.key==pygame.K_RETURN:
                    self.focus=None
                elif event.key==pygame.K_a and mod&pygame.KMOD_CTRL:
                    self.selection=True
                elif event.key in (pygame.K_LEFT,pygame.K_RIGHT,pygame.K_HOME,pygame.K_END):
                    self.selection=False
                    self.cursor=0 if event.key==pygame.K_HOME else len(value) if event.key==pygame.K_END else max(0,min(len(value),self.cursor+(-1 if event.key==pygame.K_LEFT else 1)))
                elif event.key in (pygame.K_BACKSPACE,pygame.K_DELETE):
                    if self.selection: value=''; self.cursor=0
                    elif event.key==pygame.K_BACKSPACE and self.cursor: value=value[:self.cursor-1]+value[self.cursor:]; self.cursor-=1
                    elif event.key==pygame.K_DELETE: value=value[:self.cursor]+value[self.cursor+1:]
                    self.selection=False
                    obj[key]=value
                elif event.unicode and event.unicode.isprintable() and not mod&pygame.KMOD_CTRL:
                    if self.selection: value=''; self.cursor=0
                    value=value[:self.cursor]+event.unicode+value[self.cursor:]
                    self.cursor+=len(event.unicode)
                    obj[key]=value[:80] if obj is self.attr and key=='name' else value[:80].upper()
                    self.selection=False
                return True
            if mod&pygame.KMOD_CTRL and event.key==pygame.K_z:
                self.undo(); return True
            if event.key==pygame.K_f:
                self.fit(); return True
            if event.key==pygame.K_F6:
                self.action(lambda:self.show('SQL generado, destino SQLite','\n\n'.join(self.design.statements()),sql=True));return True
        if event.type==pygame.MOUSEWHEEL:
            if self.form=='entity' and self.tab=='attributes':
                self.attr_scroll=max(0,min(max(0,len(self.entity_draft['attributes'])-7),self.attr_scroll-event.y))
            elif not self.form:
                self.zoom_by(1.15**event.y)
            return True
        if event.type==pygame.MOUSEMOTION:
            self.mouse=event.pos
            if self.drag:
                kind,original,point=self.drag
                delta=[(event.pos[i]-point[i]) for i in (0,1)]
                if kind=='pan': self.offset=[original[i]+delta[i] for i in (0,1)]
                else:
                    node=next(n for n in self.design.entities if n['name']==kind)
                    node['x'],node['y']=original[0]+delta[0]/self.zoom,original[1]+delta[1]/self.zoom
                return True
        if event.type==pygame.MOUSEBUTTONUP and self.drag:
            kind,_,point=self.drag
            moved=math.dist(point,event.pos)>3
            if kind!='pan':
                if moved: self.changed()
                else: self.create_entity(self.design.entity(kind))
            self.drag=None
            return True
        if event.type==pygame.MOUSEBUTTONDOWN:
            self.mouse=event.pos
            if event.button not in (1,2,3): return False
            for rect,callback in self.buttons:
                if rect.collidepoint(event.pos):
                    self.focus=None
                    self.action(callback)
                    return True
            for rect,obj,key in self.fields:
                if rect.collidepoint(event.pos):
                    self.focus=(obj,key); self.cursor=len(str(obj[key])); self.selection=True
                    return True
            self.focus=None
            if self.form: return True
            for rect,node in reversed(self.cards):
                if rect.collidepoint(event.pos):
                    if self.connect_kind:
                        if self.source is None:
                            self.source=node['name']; self.status='Origen '+self.source+', ahora selecciona el destino'
                        else:
                            self.create_relation(self.source,node['name'],self.connect_kind)
                    elif self.relational_tables is not None:
                        self.show('SQL de '+node['name'],self.design.sql_for(node),sql=True)
                    else:
                        self.remember()
                        self.drag=(node['name'],(node['x'],node['y']),event.pos)
                    return True
            for points,rel in self.lines:
                if any(self.distance(event.pos,a,b)<5 for a,b in zip(points,points[1:])):
                    if self.relational_tables is None:
                        self.create_relation(rel['source'],rel['target'],rel['kind'],rel)
                    return True
            self.drag=('pan',list(self.offset),event.pos)
            return True
        return False

    @staticmethod
    def distance(p,a,b):
        dx,dy=b[0]-a[0],b[1]-a[1]
        t=max(0,min(1,((p[0]-a[0])*dx+(p[1]-a[1])*dy)/max(1,dx*dx+dy*dy)))
        return math.hypot(p[0]-a[0]-t*dx,p[1]-a[1]-t*dy)

    def button(self,surface,label,rect,callback,active=False,accent=MINT,fill=None,icon=None,pulse=False):
        rect=pygame.Rect(rect)
        button(surface,label,rect,self.small,selected=active,accent=accent,fill=fill,icon=icon,pulse=pulse)
        self.buttons.append((rect,callback))

    def help(self,surface,key,x,y):
        draw.circle(surface,(65,125,150),(x,y),6)
        surface.blit(self.small.render('?',True,(245,250,255)),(x-2,y-3))
        self.buttons.append((pygame.Rect(x-7,y-7,14,14),lambda:self.show('Ayuda',HELP[key])))

    def field(self,surface,obj,key,label,rect,help_key=None):
        rect=pygame.Rect(rect)
        focused=self.focus is not None and self.focus[0] is obj and self.focus[1]==key
        draw.rect(surface,(12,23,34),rect)
        draw.rect(surface,(100,225,195) if focused else (70,95,120),rect,1)
        draw_fitted_text(surface,label+': '+str(obj[key]),rect,self.small,(230,240,245),padding=3)
        self.fields.append((rect,obj,key))
        if focused and self.selection:
            draw.line(surface,(100,225,195),(rect.x+3,rect.bottom-3),(rect.right-3,rect.bottom-3))
        if help_key: self.help(surface,help_key,rect.right+9,rect.centery)

    def check(self,surface,obj,key,label,rect,help_key=None):
        def toggle():
            obj[key]=not obj.get(key,False)
            if key=='uid' and obj[key]: obj['mandatory']=True
            if key=='identifying' and obj[key]: obj.update(source_optional=False,transfer_key=True)
        self.button(surface,('[x] ' if obj.get(key) else '[ ] ')+label,rect,toggle,obj.get(key,False))
        if help_key: self.help(surface,help_key,pygame.Rect(rect).right+9,pygame.Rect(rect).centery)

    def draw_form(self,surface):
        self.buttons=[]
        self.fields=[]
        if self.form=='task_modal':
            panel(surface,pygame.Rect(44,20,392,260),(16,26,38),GOLD,radius=4)
            surface.blit(self.title.render('TAREA DE MODELAMIENTO',True,GOLD),(58,28))
            task_info=self.task_checklist() if self.task_checklist else {"general":self.task() if self.task else "Sin tarea","items":[],"is_complete":True}
            gen_rect=pygame.Rect(58,50,364,48)
            panel(surface,gen_rect,(22,34,48),(80,110,140),shadow=False,radius=3)
            draw_fitted_text(surface,task_info.get("general",""),gen_rect,self.small,(220,235,245),padding=5)

            items=task_info.get("items",[])
            total_pages=max(1,(len(items)+5)//6)
            self.task_page=max(0,min(self.task_page,total_pages-1))
            complete=sum(bool(done) for _,done in items)
            draw_fitted_text(surface,f'Requisitos: {complete}/{len(items)} | Página {self.task_page+1}/{total_pages}',pygame.Rect(58,102,364,16),self.small,(180,205,220))
            for i,(req_label,is_done) in enumerate(items[self.task_page*6:(self.task_page+1)*6]):
                item_y=120+i*18
                box_color=EMERALD if is_done else GOLD
                draw.rect(surface,(14,22,32),(58,item_y,364,18),border_radius=2)
                draw.rect(surface,box_color,(58,item_y,364,18),1,border_radius=2)
                draw.rect(surface,(20,36,44),(62,item_y+2,14,14),border_radius=2)
                draw.rect(surface,box_color,(62,item_y+2,14,14),1,border_radius=2)
                if is_done:draw_pixel_icon(surface,"check",69,item_y+9,EMERALD)
                else:draw_pixel_icon(surface,"!",69,item_y+9,GOLD)
                text_color=(200,245,215) if is_done else (235,230,215)
                draw_fitted_text(surface,req_label,pygame.Rect(82,item_y+1,335,16),self.small,text_color,padding=0)

            all_done=task_info.get("is_complete",False)
            st_color=EMERALD if all_done else GOLD
            st_msg="Diseño completo, revisa tu jornada desde el computador" if all_done else "Sigue las casillas pendientes, tus cambios se guardan en el taller"
            draw_fitted_text(surface,st_msg,pygame.Rect(58,230,364,16),self.small,st_color)
            if self.task_page>0:self.button(surface,'Anterior',(58,250,100,22),lambda:setattr(self,'task_page',self.task_page-1))
            self.button(surface,"Cerrar tarea",(180,250,120,22),lambda:setattr(self,'form',None),accent=GOLD,fill=(48,38,18))
            if self.task_page+1<total_pages:self.button(surface,'Siguiente',(322,250,100,22),lambda:setattr(self,'task_page',self.task_page+1))
            return

        panel(surface,pygame.Rect(46,25,388,267),(18,30,43),GOLD)
        surface.blit(self.title.render('Propiedades de '+('entidad' if self.form=='entity' else 'relación'),True,(250,205,110)),(60,34))
        if self.form=='entity':
            self.button(surface,'General',(60,53,90,19),lambda:setattr(self,'tab','general'),self.tab=='general',accent=AZURE if self.tab=='general' else MUTED)
            self.button(surface,'Atributos',(156,53,90,19),lambda:setattr(self,'tab','attributes'),self.tab=='attributes',accent=AZURE if self.tab=='attributes' else MUTED)
            if self.tab=='general':
                self.field(surface,self.entity_draft,'name','Nombre singular',(65,90,335,23),'name')
                render_wrapped_text(surface,'Ejemplo: ESTUDIANTE\n\nEl modelo lógico contiene entidades y atributos, al convertirlo se crearán las tablas y sus columnas\n\nUsa UID para identificar cada instancia, los atributos todavía se pueden editar antes de generar la base',pygame.Rect(65,127,340,113),self.font,color=(195,215,225),padding=0,line_spacing=3)
            else:
                draw.rect(surface,(19,32,45),(60,80,116,140))
                for i,a in enumerate(self.entity_draft['attributes'][self.attr_scroll:self.attr_scroll+7],self.attr_scroll):
                    self.button(surface,('* ' if a.get('uid') else '')+a['name'],(62,82+(i-self.attr_scroll)*19,112,18),lambda j=i:self.select_attribute(j),i==self.attribute_index,accent=AZURE if i==self.attribute_index else MUTED)
                self.field(surface,self.attr,'name','Nombre',(186,80,214,20),'name')
                def cycle(): self.attr['type']=ORIGIN_TYPES[(ORIGIN_TYPES.index(self.attr['type'])+1)%len(ORIGIN_TYPES)]
                self.button(surface,'Tipo de origen: '+self.attr['type'],(186,105,214,20),cycle,accent=AZURE)
                self.help(surface,'type',409,115)
                if self.attr['type']=='VARCHAR':
                    self.field(surface,self.attr,'length','Longitud',(186,131,214,20),'length')
                elif self.attr['type']=='NUMERIC':
                    self.field(surface,self.attr,'precision','Precisión',(186,131,94,20),'precision')
                    self.field(surface,self.attr,'scale','Escala',(306,131,94,20),'scale')
                self.check(surface,self.attr,'uid','UID primario',(186,160,214,19),'uid')
                self.check(surface,self.attr,'mandatory','Obligatorio, no permite NULL',(186,184,214,19),'mandatory')
                self.button(surface,'Aplicar atributo',(186,211,214,20),self.apply_attribute,accent=EMERALD,fill=(18,48,30),icon='check')
                self.button(surface,'+ Añadir otro atributo',(60,226,116,25),self.new_attribute,accent=AZURE,fill=(22,38,62),icon='+')
                self.button(surface,'Quitar atributo',(186,236,214,19),self.remove_attribute,accent=CRIMSON,fill=(52,24,28),icon='delete')
            self.button(surface,'Guardar entidad',(60,265,117,19),self.save_entity,accent=EMERALD,fill=(18,50,32),icon='check')
            self.button(surface,'Eliminar',(183,265,100,19),self.delete_entity,accent=CRIMSON,fill=(52,24,28),icon='delete')
        else:
            r=self.relation_draft
            self.field(surface,r,'name','Nombre',(60,59,340,19),'name')
            draw_fitted_text(surface,r['source']+'  '+r['kind']+'  '+r['target'],pygame.Rect(60,82,350,18),self.font,(125,230,190))
            self.field(surface,r,'source_role','Nombre origen',(60,104,340,19),'roles')
            self.field(surface,r,'target_role','Nombre destino',(60,128,340,19),'roles')
            fields=[('transfer_key','Pasar UID para generar FK'),('transferable','Transferible'),('source_optional','Origen opcional'),('target_optional','Destino opcional'),('identifying','Con identificación')]
            for i,(key,label) in enumerate(fields):
                self.check(surface,r,key,label,(60,154+i*20,340,18),key)
            self.button(surface,'Guardar relación',(60,265,117,19),self.save_relation,accent=EMERALD,fill=(18,50,32),icon='check')
            self.button(surface,'Eliminar',(183,265,100,19),self.delete_relation,accent=CRIMSON,fill=(52,24,28),icon='delete')
        self.button(surface,'Cancelar',(289,265,117,19),lambda:setattr(self,'form',None),accent=MUTED,fill=(36,42,50))

    def draw(self,surface):
        backdrop(surface,(13,24,35))
        panel(surface,pygame.Rect(0,0,480,33),(22,37,49),MINT,shadow=False)
        self.buttons,self.fields,self.cards,self.lines=[],[],[],[]
        task_lbl = 'Tarea'
        task_acc = MUTED
        task_pulse = False
        task_cb = lambda: self.show('Tarea actual', 'No hay ninguna tarea actual')
        if self.task_checklist:
            chk = self.task_checklist()
            done = chk.get("is_complete", False)
            task_lbl = "Tarea (✓)" if done else "Tarea (!)"
            task_acc = EMERALD if done else GOLD
            task_pulse = not done
            task_cb = lambda: setattr(self, 'form', 'task_modal')
        elif self.task:
            task_acc = GOLD
            task_cb = lambda: self.show('Tarea actual', self.task() if self.task else 'No hay ninguna tarea actual')

        self.button(surface, task_lbl, (4, 3, 40, 27), task_cb, accent=task_acc, pulse=task_pulse)
        if self.task_checklist and done:
            panel(surface,pygame.Rect(4,37,89,18),(16,49,37),EMERALD,shadow=False)
            draw_fitted_text(surface,'¡Completado!',pygame.Rect(8,38,81,15),self.small,EMERALD,padding=0)
        self.button(surface, '+ Entidad', (47, 3, 48, 27), lambda: self.create_entity(), accent=AZURE, fill=(22, 38, 62))
        for x_pos, k in ((98, '1:N'), (126, '1:1'), (154, 'N:M')):
            self.button(surface, k, (x_pos, 3, 25, 27), lambda kind=k: self.relation_tool(kind), accent=(100, 180, 240))
        self.button(surface, 'Generar\nSQL', (183, 3, 46, 27), self.convert, accent=EMERALD, fill=(18, 48, 32))
        self.button(surface, 'Vista\n' + ('Lógica' if self.relational_tables is None else 'SQL'), (232, 3, 44, 27), self.switch_view, accent=(120, 205, 235))
        self.button(surface, 'Cuaderno', (279, 3, 46, 27), self.on_notes, accent=GOLD)
        self.button(surface, '-', (328, 3, 18, 27), lambda: self.zoom_by(1 / 1.2), accent=MUTED)
        self.button(surface, '+', (349, 3, 18, 27), lambda: self.zoom_by(1.2), accent=MUTED)
        self.button(surface, 'Ajustar', (370, 3, 40, 27), self.fit, accent=MUTED)
        area=pygame.Rect(0,34,480,243)
        clip=surface.get_clip()
        surface.set_clip(clip.clip(area))
        spacing=max(8,int(24*self.zoom))
        for gx in range(int(self.offset[0])%spacing,480,spacing):
            for gy in range(34+int(self.offset[1])%spacing,277,spacing):draw.rect(surface,(39,58,68),(gx,gy,1,1))
        nodes=self.relational_tables if self.relational_tables is not None else self.design.entities
        for node in nodes:
            attrs=node.get('attributes',node.get('columns',[]))
            rect=pygame.Rect(self.offset[0]+node['x']*self.zoom,self.offset[1]+node['y']*self.zoom,210*self.zoom,(32+len(attrs)*20)*self.zoom)
            self.cards.append((rect,node))
        positions={node['name']:rect for rect,node in self.cards}
        labels=[]
        relations=self.design.relations if self.relational_tables is None else [dict(name=fk['name'],source=fk['table'],target=node['name'],kind='1:1' if fk['columns'] in node['unique'] else '1:N',source_optional=any(not c.get('mandatory') for c in node['columns'] if c['name'] in fk['columns']),target_optional=True,identifying=all(c.get('uid') for c in node['columns'] if c['name'] in fk['columns']),source_role='',target_role='') for node in nodes for fk in node.get('foreign_keys',[])]
        for rel in relations:
            if rel['source'] not in positions or rel['target'] not in positions: continue
            a,b=positions[rel['source']],positions[rel['target']]
            start=(a.right,a.centery); end=(b.left,b.centery)
            if a.centerx>b.centerx: start=(a.left,a.centery);end=(b.right,b.centery)
            mid=(start[0]+end[0])/2
            points=[start,(mid,start[1]),(mid,end[1]),end]
            if a is b: points=[(a.right,a.centery),(a.right+25,a.centery),(a.right+25,a.top-16),(a.centerx,a.top-16),(a.centerx,a.top)]
            self.lines.append((points,rel))
            for p1,p2 in zip(points,points[1:]):
                if rel.get('source_optional'):
                    length=math.dist(p1,p2)
                    for s in range(0,int(length),8):
                        t=min(length,s+4)
                        if length: draw.line(surface,(100,205,180),(p1[0]+(p2[0]-p1[0])*s/length,p1[1]+(p2[1]-p1[1])*s/length),(p1[0]+(p2[0]-p1[0])*t/length,p1[1]+(p2[1]-p1[1])*t/length))
                else: draw.line(surface,(100,205,180),p1,p2,1)
            for point,toward,many,optional in [(points[0],points[1],rel['kind']=='N:M',rel.get('source_optional',False)),(points[-1],points[-2],rel['kind'] in ('1:N','N:M'),rel.get('target_optional',True))]:
                dx,dy=toward[0]-point[0],toward[1]-point[1]; length=max(1,math.hypot(dx,dy)); ux,uy=dx/length,dy/length; vx,vy=-uy,ux
                back=(point[0]+ux*9,point[1]+uy*9)
                if many:
                    for spread in (-5,0,5): draw.line(surface,(135,230,195),(point[0]+vx*spread,point[1]+vy*spread),back)
                else: draw.line(surface,(135,230,195),(point[0]+ux*4+vx*5,point[1]+uy*4+vy*5),(point[0]+ux*4-vx*5,point[1]+uy*4-vy*5))
                mark=(round(point[0]+ux*14),round(point[1]+uy*14))
                if optional: draw.circle(surface,(135,230,195),mark,3,1)
                else: draw.line(surface,(135,230,195),(mark[0]+vx*4,mark[1]+vy*4),(mark[0]-vx*4,mark[1]-vy*4))
            label=rel['name']+(' [UID]' if rel.get('identifying') else '')
            width=max(65,abs(end[0]-start[0])-8)
            labels.append((label,rel.get('source_role','')+' / '+rel.get('target_role',''),pygame.Rect(mid-width/2,(start[1]+end[1])/2-30,width,48)))
        for rect,node in self.cards:
            attrs=node.get('attributes',node.get('columns',[]))
            panel(surface,rect,(25,42,55),MINT,radius=3)
            size=max(4,min(13,int(12*self.zoom)))
            font=make_font(size)
            header=max(6,int(29*self.zoom))
            draw.rect(surface,(39,61,69),(rect.x+2,rect.y+2,rect.width-4,header-2),border_radius=2)
            draw.line(surface,(77,113,115),(rect.x+3,rect.y+header),(rect.right-3,rect.y+header))
            draw_fitted_text(surface,node['name'],pygame.Rect(rect.x+2,rect.y+1,rect.width-4,header),font,(255,215,130),padding=1)
            for i,attr in enumerate(attrs):
                kind=attr['type']+('('+str(attr.get('length',80))+')' if attr['type']=='VARCHAR' else '')
                label=('* ' if attr.get('uid') else '')+attr['name']+' '+kind+(' M' if attr.get('mandatory') else ' O')
                draw_fitted_text(surface,label,pygame.Rect(rect.x+3,rect.y+header+i*20*self.zoom,rect.width-6,max(3,int(20*self.zoom))),font,(130,235,190) if attr.get('generated') else (220,232,240),padding=0)
        for title,roles,rect in labels:
            draw_fitted_text(surface,title,pygame.Rect(rect.x,rect.y,rect.width,22),self.small,(165,225,210),padding=0)
            if roles.strip(' /'):draw_fitted_text(surface,roles,pygame.Rect(rect.x,rect.y+23,rect.width,25),self.small,(140,185,180),padding=0)
        if not nodes:
            render_wrapped_text(surface,'Modelo lógico\n\nCrea una entidad, define sus atributos y UID\n\nDespués conecta las entidades con relaciones\n\nRueda para zoom, arrastra el fondo para desplazarte',pygame.Rect(50,80,380,150),self.font,color=(150,180,200),padding=0,line_spacing=4)
        surface.set_clip(clip)
        draw.rect(surface,(17,31,43),(0,278,480,22))
        status=self.status if not self.status.startswith('Rueda:') else ''
        draw_fitted_text(surface,f'{round(self.zoom*100)}% | '+status,pygame.Rect(8,280,376,16),self.small,(170,205,215),padding=0)
        if self.form: self.draw_form(surface)
        if self.message:
            page=self.message[self.message_index]
            panel(surface,pygame.Rect(15,35,450,255),(18,31,44),MINT)
            draw_fitted_text(surface,page['title'],pygame.Rect(28,44,424,20),self.title,(255,205,100),padding=0)
            if page.get('sql'): draw_sql(surface,page['body'],(28,74),self.font)
            else: render_wrapped_text(surface,page['body'],pygame.Rect(28,75,424,186),self.font,padding=0,line_spacing=2)
            draw_fitted_text(surface,f'{self.message_index+1}/{len(self.message)}',pygame.Rect(28,268,424,15),self.small,(100,220,210),padding=0)
