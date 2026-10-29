"""Cada concepto de la introducción tiene su propio esquema y foco visual"""


def board_for(day,title,part):
    if title=='Bienvenidos al taller':
        return 'welcome','Marco, Moshi, Carlos, Sofía, Matías y tú | Taller opcional'
    if 'herramienta' in title.lower() or 'modelador' in title.lower() or 'datamodeler' in title.lower():
        return 'table', ('Herramientas visuales: Oracle Data Modeler, Workbench', 'En tu PC tienes el Modelador de Datos para crear tablas y relaciones')[part%2]
    if 'tarea' in title.lower():
        return 'table', ('¡Tarea asignada! Revisa el botón Tarea (!) en el modelador', 'Crea ESTUDIANTE con ID, NOMBRE y PROMEDIO')[part%2]
    if day==1:
        if 'problema' in title:return 'scattered',('Datos repartidos, una corrección en varios lugares','Una base organiza los registros y evita listas contradictorias')[part%2]
        if 'fila' in title:return 'table',('Una FILA reúne los datos de una persona','Una COLUMNA describe una característica')[part%2]
        if 'SQL es' in title:return 'pipeline',('SQL: el lenguaje para expresar lo que necesitamos','SQLite: el motor que interpreta la petición')[part%2]
        if 'Describir' in title:return None,('SELECT elige qué columna queremos ver','FROM indica de qué tabla salen los datos')[part%2]
        if 'mundo real' in title:return ('attributes' if part%2==0 else 'entities'),('La entidad representa una cosa, sus atributos la describen','Organizamos las entidades y conectamos sus datos')[part%2]
        return 'entities',('Primero identificamos las cosas y sus características','Después pensamos cómo se relacionan')[part%2]
    if day==2:
        if 'NUMERIC(10' in title:return 'capacity','10 es el máximo, 12 ocupa solo dos posiciones, 0 indica ningún decimal'
        if 'Precisión' in title:return 'precision','Precisión: máximo de dígitos totales | Escala: decimales permitidos'
        if 'tipos distintos' in title:return 'type_mapping','Diseño lógico y SQLite son dos niveles del mismo proyecto'
        if 'modelador sigue' in title:return 'type_mapping','VARCHAR se convierte en TEXT, NUMERIC añade validaciones'
        if 'teléfono' in title:return 'codes','Un código o teléfono no es una cantidad para sumar'
        if 'Fechas y archivos' in title:return 'binary','DATE representa una fecha, BLOB representa bytes de un archivo'
        if 'afinidad' in title:return 'affinity','SQLite intenta convertir el valor, otras reglas comprueban su validez'
        if 'rango válido' in title:return 'range','REAL permite 8, otra validación debe exigir una nota de 1 a 7'
        if 'Nombres' in title:return 'names','ESTUDIANTE para la entidad | fecha_nacimiento para el atributo'
        if 'desconocido' in title:return 'null',('NULL: todavía no conocemos el dato','Cero y texto vacío son valores diferentes de NULL')[part%2]
        if 'dígitos' in title:return 'codes',('0012 es un código, no necesariamente una cantidad','El tipo representa el significado, no solo el aspecto')[part%2]
        if 'reglas' in title:return 'range',('Un tipo numérico no define el rango de una nota','El rango de 1 a 7 es una regla adicional del negocio')[part%2]
        if 'entidad' in title or 'columna' in title:return 'entities',('Cada característica tiene su propio atributo','ID, NOMBRE y PROMEDIO describen a ESTUDIANTE')[part%2]
        return 'types',('Texto, número y fecha representan datos distintos','Elegimos el tipo antes de guardar valores')[part%2]
    if day==3:
        if 'NN' in title:return 'null',('Obligatorio: el nombre no puede ser NULL','Opcional: el promedio puede quedar pendiente')[part%2]
        if 'compuesta' in title:return 'identifying','PEDIDO_ID + NUMERO_LINEA identifican la línea completa'
        if 'Obligatorio' in title:return 'null','NOT NULL exige un dato, no exige que sea único'
        return 'key',('Los nombres pueden coincidir, los identificadores distinguen','El UID completo no puede repetirse')[part%2]
    if day==4:
        if 'muchos a ambos' in title:return 'junction','Una inscripción conecta estudiante y materia'
        if 'identificador' in title:return 'identifying','La clave del padre participa en la clave del hijo'
        if 'transferible' in title:return 'reparent','Transferible permite cambiar la referencia al padre'
        return 'relation',('Una persona puede tener varias tutorías','La FK conserva el identificador de la persona relacionada')[part%2]
    if 'tipos' in title:return 'types','El tipo lógico se adapta a lo que soporta SQLite'
    if 'errores' in title:return 'checks','Probar también los casos que deben rechazarse'
    return 'conversion',('Entidades y relaciones del modelo lógico','Tablas, columnas y restricciones en el relacional')[part%2]
