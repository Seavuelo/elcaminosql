"""Diseño lógico persistible y transformación explícita a SQLite"""
from copy import deepcopy
from contextlib import closing
import re
import sqlite3
import uuid

ORIGIN_TYPES = ('VARCHAR','NUMERIC','DATE','INTEGER','REAL','BLOB')


def name(value,uppercase=True):
    value = value.strip().upper() if uppercase else value.strip()
    if not re.fullmatch(r'[A-Za-z][A-Za-z0-9_]{0,39}',value):
        raise ValueError('Usa letras sin tildes ni ñ, números y _, sin espacios, empieza con una letra, máximo 40 caracteres')
    return value


def q(value):
    return '"'+value.replace('"','""')+'"'


class LogicalDesign:
    def __init__(self,data=None,legacy=None):
        self.data = deepcopy(data or dict(entities=[],relations=[]))
        self.data.setdefault('entities',[])
        self.data.setdefault('relations',[])
        if not self.entities and legacy:
            for old in legacy:
                attrs = [dict(name=c['name'].upper(),type={'TEXT':'VARCHAR'}.get(c['type'],c['type']),
                              length=80,precision=10,scale=2,uid=bool(c.get('pk')),mandatory=bool(c.get('not_null') or c.get('pk')))
                         for c in old['columns'] if not c.get('reference')]
                self.entities.append(dict(name=old['name'].upper(),attributes=attrs,x=old.get('x',0)*2,y=old.get('y',0)*2))
            for old in legacy:
                for col in old['columns']:
                    if col.get('reference'):
                        self.relations.append(dict(id=uuid.uuid4().hex,name='R_'+old['name'].upper()+'_'+col['name'].upper(),
                            source=col['reference']['table'].upper(),target=old['name'].upper(),kind='1:N',
                            source_role='TIENE',target_role='PERTENECE',source_optional=not col.get('not_null',False),
                            target_optional=True,identifying=False,transfer_key=True,transferable=True))

    @property
    def entities(self):
        return self.data['entities']

    @property
    def relations(self):
        return self.data['relations']

    def entity(self,value):
        return next((e for e in self.entities if e['name']==value),None)

    @staticmethod
    def attribute(value):
        value = deepcopy(value)
        value['name'] = name(value['name'],uppercase=False)
        if value['type'] not in ORIGIN_TYPES:
            raise ValueError('Elige un tipo de origen disponible')
        try:
            value['length'] = int(value.get('length',80))
            value['precision'] = int(value.get('precision',10))
            value['scale'] = int(value.get('scale',2))
        except (TypeError,ValueError):
            raise ValueError('Longitud, precisión y escala deben ser números enteros')
        if not 1 <= value['length'] <= 4000:
            raise ValueError('La longitud de VARCHAR debe estar entre 1 y 4000')
        if not 1 <= value['precision'] <= 15 or not 0 <= value['scale'] <= min(6,value['precision']):
            raise ValueError('Usa precisión de 1 a 15 y escala entre 0 y 6, sin superar la precisión')
        if value.get('uid'):
            value['mandatory'] = True
        return value

    def save_entity(self,value,old=None):
        value = deepcopy(value)
        value['name'] = name(value['name'])
        if any(e['name']==value['name'] and e['name']!=old for e in self.entities):
            raise ValueError('Ya existe una entidad con ese nombre')
        value['attributes'] = [self.attribute(a) for a in value['attributes']]
        if len({a['name'].casefold() for a in value['attributes']}) != len(value['attributes']):
            raise ValueError('Los atributos de una entidad no pueden repetir el nombre')
        current = self.entity(old)
        if current:
            index = self.entities.index(current)
            self.entities[index] = value
            for relation in self.relations:
                for endpoint in ('source','target'):
                    if relation[endpoint]==old:
                        relation[endpoint] = value['name']
        else:
            self.entities.append(value)

    def delete_entity(self,value):
        if any(value in (r['source'],r['target']) for r in self.relations):
            raise ValueError('Quita primero las relaciones de esta entidad')
        self.entities.remove(self.entity(value))

    def save_relation(self,value):
        value = deepcopy(value)
        value['name'] = name(value['name'])
        if not self.entity(value['source']) or not self.entity(value['target']):
            raise ValueError('Selecciona dos entidades existentes')
        if value['kind'] not in ('1:1','1:N','N:M'):
            raise ValueError('Elige una cardinalidad disponible')
        if value.get('identifying') and value.get('source_optional'):
            raise ValueError('Una relación identificadora necesita el origen, no puede ser opcional')
        if value.get('identifying') and not value.get('transfer_key'):
            raise ValueError('La relación identificadora debe transferir la clave')
        if any(r['name']==value['name'] and r['id']!=value.get('id') for r in self.relations):
            raise ValueError('Ya existe una relación con ese nombre')
        value.setdefault('id',uuid.uuid4().hex)
        current = next((r for r in self.relations if r['id']==value['id']),None)
        if current:
            self.relations[self.relations.index(current)] = value
        else:
            self.relations.append(value)

    def relational(self):
        if not self.entities:
            raise ValueError('Crea una entidad antes de convertir el modelo')
        tables = {e['name']:dict(name=e['name'],columns=deepcopy(e['attributes']),foreign_keys=[],unique=[],locks=[],x=e.get('x',0),y=e.get('y',0)) for e in self.entities}
        visiting,visited = set(),set()
        def visit(entity):
            if entity in visiting:
                raise ValueError('Las relaciones identificadoras no pueden formar un ciclo')
            if entity in visited:
                return
            visiting.add(entity)
            for rel in self.relations:
                if rel.get('identifying') and rel['target']==entity and rel['kind']!='N:M':
                    visit(rel['source'])
            visiting.remove(entity)
            visited.add(entity)
        for entity in tables:
            visit(entity)
        def transfer(rel,source,target,*,prefix=None,identifying=False,optional=False):
            primary = [a for a in source['columns'] if a.get('uid')]
            if not primary:
                raise ValueError(f"Falta un UID primario en {source['name']}")
            fields = []
            for attr in primary:
                label = (prefix or source['name'])+'_'+attr['name']
                if attr['name'].islower():label=label.lower()
                existing = next((a for a in target['columns'] if a['name'].casefold()==label.casefold()),None)
                if existing and existing['type']!=attr['type']:
                    raise ValueError(f'La columna {label} ya existe con otro tipo')
                if not existing:
                    existing = dict(attr,name=label,uid=identifying,mandatory=not optional,generated=True)
                    target['columns'].append(existing)
                existing['uid'] = existing.get('uid',False) or identifying
                existing['mandatory'] = existing.get('mandatory',False) or not optional or identifying
                fields.append(existing['name'])
            foreign = dict(name=rel['name'],columns=fields,table=source['name'],target_columns=[a['name'] for a in primary],transferable=rel.get('transferable',True))
            if not any(f['name']==rel['name'] and f['table']==source['name'] for f in target['foreign_keys']):
                target['foreign_keys'].append(foreign)
            if rel['kind']=='1:1' and fields not in target['unique']:
                target['unique'].append(fields)
        order = list(visited)
        # Un padre se convierte antes que sus hijos para propagar claves compuestas.
        built = set()
        def build(entity):
            if entity in built:
                return
            for rel in self.relations:
                if rel['target']==entity and rel.get('identifying') and rel['kind']!='N:M':
                    build(rel['source'])
                    multiple=sum(1 for r in self.relations if r['source']==rel['source'] and r['target']==entity and r['kind']!='N:M')>1
                    transfer(rel,tables[rel['source']],tables[entity],prefix=rel['name']+'_'+rel['source'] if multiple else None,identifying=True)
            built.add(entity)
        for entity in order:
            build(entity)
        warnings = []
        for rel in self.relations:
            if not rel.get('transfer_key',True):
                warnings.append(f"{rel['name']}: asociación solo lógica, no genera FK ni integridad automática")
                continue
            source,target = tables[rel['source']],tables[rel['target']]
            if rel['kind']=='N:M':
                if rel['name'] in tables:
                    raise ValueError('El nombre de la tabla intermedia coincide con una entidad, cambia el nombre de la relación')
                bridge = dict(name=rel['name'],columns=[],foreign_keys=[],unique=[],locks=[],x=(source['x']+target['x'])/2,y=max(source['y'],target['y'])+220)
                transfer(rel,source,bridge,prefix=source['name']+('_ORIGEN' if source is target else ''),identifying=True)
                transfer(rel,target,bridge,prefix=target['name']+('_DESTINO' if source is target else ''),identifying=True)
                tables[rel['name']] = bridge
            elif not rel.get('identifying'):
                multiple = sum(1 for r in self.relations if r['source']==rel['source'] and r['target']==rel['target'] and r['kind']!='N:M')>1
                transfer(rel,source,target,prefix=rel['name']+'_'+source['name'] if multiple else None,optional=rel.get('source_optional',False))
            if not rel.get('target_optional',True):
                warnings.append(f"{rel['name']}: exigir al menos un hijo requiere validación de proceso, una FK sola no garantiza esa participación mínima")
        for table in tables.values():
            if not table['columns'] or not any(a.get('uid') for a in table['columns']):
                raise ValueError(f"Define atributos y un UID primario en {table['name']}")
        return list(tables.values()),warnings

    @staticmethod
    def sql_for(table):
        parts = []
        for a in table['columns']:
            kind = a['type']
            physical = {'VARCHAR':'TEXT','DATE':'TEXT'}.get(kind,kind)
            col = q(a['name'])
            text = col+' '+physical+(' NOT NULL' if a.get('mandatory') or a.get('uid') else '')
            if kind=='VARCHAR':
                text += f" CHECK(length({col}) <= {a.get('length',80)})"
            elif kind=='DATE':
                text += f" CHECK({col} IS NULL OR (length({col}) = 10 AND date({col}, '+0 days') IS NOT NULL AND date({col}, '+0 days') = {col}))"
            elif kind=='NUMERIC':
                p,s = a.get('precision',10),a.get('scale',2)
                text += f" CHECK({col} IS NULL OR (typeof({col}) IN ('integer','real') AND abs({col}) < {10**(p-s)} AND abs({col}-round({col},{s})) < 0.000000001))"
            parts.append(text)
        parts.append('PRIMARY KEY ('+', '.join(q(a['name']) for a in table['columns'] if a.get('uid'))+')')
        for fields in table['unique']:
            parts.append('UNIQUE ('+', '.join(map(q,fields))+')')
        for fk in table['foreign_keys']:
            parts.append('CONSTRAINT '+q(fk['name'])+' FOREIGN KEY ('+', '.join(map(q,fk['columns']))+') REFERENCES '+q(fk['table'])+' ('+', '.join(map(q,fk['target_columns']))+')')
        return 'CREATE TABLE '+q(table['name'])+' (\n  '+',\n  '.join(parts)+'\n);'

    def statements(self):
        tables,_ = self.relational()
        statements = [self.sql_for(table) for table in tables]
        for table in tables:
            for index,fk in enumerate(table['foreign_keys']):
                if not fk['transferable']:
                    known = ' AND '.join('OLD.'+q(c)+' IS NOT NULL' for c in fk['columns'])
                    changed = ' OR '.join('OLD.'+q(c)+' IS NOT NEW.'+q(c) for c in fk['columns'])
                    statements.append('CREATE TRIGGER '+q('LOCK_'+table['name']+'_'+str(index))+' BEFORE UPDATE OF '+', '.join(map(q,fk['columns']))+' ON '+q(table['name'])+' WHEN ('+known+') AND ('+changed+") BEGIN SELECT RAISE(ABORT, 'Relacion no transferible'); END;")
        return statements

    def connection(self):
        conn = sqlite3.connect(':memory:')
        try:
            conn.execute('PRAGMA foreign_keys=ON')
            for sql in self.statements():
                conn.execute(sql)
            return conn
        except Exception:
            conn.close()
            raise

    def verify(self):
        tables,warnings = self.relational()
        with closing(self.connection()) as conn:
            return tables,warnings,conn.execute('PRAGMA foreign_key_check').fetchall()
