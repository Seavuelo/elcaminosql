"""Guion de locución independiente del texto visible, voz Santa de Marco"""
import hashlib

INVITATION='Ya, vamos a hacer un Kashut. Únanse desde su computador, a ver si quedan en el podio. Lean con calma antes de responder. Después repasamos juntos las preguntas que hayan costado.'
SCRIPTS={
1:[
 'Soy el profesor Marco. Estas clases son opcionales y sirven para entender bien los fundamentos, antes de empezar la carrera.',
 'Hoy nos acompañan Moshi, Carlos, Sofía y Matías. Primero conversaremos sobre las ideas. No tienes que crear tablas el primer día.',
 'Imagina que la universidad anota estudiantes y tutorías en papeles distintos. Cuando alguien cambia su nombre, cuesta saber qué registros corregir.',
 'Una base de datos organiza esa información. Así podemos encontrarla, relacionarla y mantenerla coherente.',
 'En esta lista, cada fila representa a una persona. Las columnas indican qué sabemos de ella.',
 'El nombre de una columna describe una característica. Moshi es un valor de esa característica. No es una columna.',
 'SQL significa lenguaje de consulta estructurada. Sirve para definir tablas, consultar registros y cambiar información.',
 'SQLite es el programa que interpreta SQL en este juego. El dibujo del modelo ayuda a planificar. No reemplaza al motor.',
 'Para pedir los nombres, indicamos qué columna queremos y de qué tabla debe salir. No recorremos las filas a mano.',
 'SELECT elige la información. FROM nombra su origen. Durante la carrera aprenderemos a construir estas consultas.',
 'Primero decide qué representa cada fila y qué datos necesitas guardar. El modelo es ese plan.',
 'Una tabla de estudiantes y otra de tutorías representan cosas distintas. Pronto las conectaremos, sin copiar el nombre del estudiante en cada tutoría.',
 'Un estudiante es algo que queremos representar. A ese tipo de cosa le llamamos entidad. Su nombre y su promedio son atributos.',
 'Al organizar esos datos en tablas y definir cómo se relacionan, construimos un modelo relacional. Las cajas del dibujo nos ayudan a pensar ese diseño.',
 INVITATION],
2:[
 'Queremos guardar un identificador, el nombre y el promedio de cada estudiante.',
 'Separarlos permite buscar y ordenar cada característica. Juntar nombre y promedio en un solo texto dificultaría trabajar con el promedio como número.',
 'INTEGER es adecuado para identificadores o cantidades enteras. TEXT se usa para nombres. REAL, para valores que pueden tener decimales.',
 'Por ejemplo, el identificador uno es de tipo INTEGER. Moshi es un valor de tipo TEXT. El promedio seis coma ocho es de tipo REAL.',
 'En el modelador elegimos VARCHAR para texto, NUMERIC para números y DATE para fechas.',
 'NUMERIC, con precisión diez y escala dos, significa diez dígitos totales y dos decimales. Para un identificador entero, podemos usar escala cero. Una fecha se representará con el año, el mes y el día.',
 'Un código como cero, cero, uno, dos, puede necesitar conservar sus ceros iniciales. Un teléfono también puede incluir un signo más.',
 'Si no vamos a hacer cálculos con esos valores, TEXT puede representar mejor su significado. BLOB se utiliza para bytes. Por ejemplo, para el contenido de un archivo.',
 'Si el promedio todavía no está calculado, podemos dejarlo como NULL. Eso expresa que falta información.',
 'No es lo mismo que un promedio cero. Tampoco es la palabra NULL guardada como texto. Más adelante aprenderemos a consultar esas diferencias.',
 'SQLite usa afinidades de tipos. Puede convertir o aceptar valores que otros motores rechazarían.',
 'Elegir REAL no impone, por sí solo, una nota entre uno y siete. Una regla del negocio necesita una restricción o una validación adicional.',
 'En tu computador, abre el modelador y pulsa Nueva entidad. En la sección General escribe ESTUDIANTE, en singular y mayúsculas.',
 'En Atributos, añade un identificador numérico, un nombre de tipo VARCHAR y un promedio numérico. Aplica cada atributo y guarda la entidad. Hoy todavía no necesitas relacionarla con otra.',
 INVITATION],
3:[
 'Dos estudiantes pueden llamarse igual, y una persona puede corregir su nombre. Por eso no conviene usarlo para distinguir registros.',
 'Una clave primaria identifica cada fila sin confundirla con otra. Puede ser un identificador que se mantenga estable.',
 'PK significa PRIMARY KEY. El identificador no puede repetirse entre filas de la misma tabla.',
 'En este taller usamos una columna como clave primaria. La marcamos también como obligatoria. El identificador no tiene que coincidir con el número de asiento.',
 'NN significa NOT NULL. Exige un valor en esa columna.',
 'Para inscribir a alguien, necesitamos su nombre. Pero podemos dejar su promedio pendiente. El nombre será obligatorio. El promedio podrá aceptar NULL.',
 'Abre las propiedades de ESTUDIANTE. En Atributos, marca el identificador como UID primario, y el nombre como obligatorio.',
 'Al convertir, el UID se transforma en PRIMARY KEY. Si varios atributos forman el identificador, su combinación será una clave primaria compuesta. No se exige que cada parte sea única por separado.',
 INVITATION],
4:[
 'Moshi puede asistir a dos tutorías. Si copiamos su nombre en cada una, tendríamos que corregirlo en varios lugares.',
 'Guardaremos a Moshi una sola vez en estudiantes. Cada tutoría conservará el identificador de su estudiante.',
 'En la tabla de tutorías, el identificador del estudiante guardará un valor que ya existe en la clave de estudiantes.',
 'Esa referencia es una clave foránea. FK significa FOREIGN KEY. La flecha del modelador muestra qué columna apunta a qué clave.',
 'Un estudiante puede tener varias tutorías. Pero cada tutoría de este modelo pertenece a un estudiante.',
 'El lado de estudiantes es el uno. El lado de tutorías es el muchos. El identificador del estudiante puede repetirse. Quien no debe repetirse es el identificador de la tutoría.',
 'Con la comprobación de claves foráneas activada, SQLite rechaza una tutoría que apunta al estudiante novecientos noventa y nueve, si ese estudiante no existe.',
 'Una clave foránea que permite NULL podría no indicar estudiante. Aquí la marcaremos como obligatoria, porque toda tutoría debe tener uno.',
 'Crea TUTORIA con un identificador primario y un tema de tipo VARCHAR. Pulsa uno a muchos. Selecciona primero ESTUDIANTE y después TUTORIA.',
 'Nombra la relación y marca pasar UID. Al generar el relacional, aparecerá el identificador del estudiante como clave foránea en TUTORIA. No necesitas escribir ni copiar a mano esa columna.',
 'Un estudiante puede cursar varias materias. Una materia puede tener varios estudiantes. Ahí ambos lados son muchos.',
 'Podemos crear una tabla intermedia, inscripciones. Tendrá una clave foránea al estudiante y otra a la materia. Cada fila representa una inscripción. Nuestro taller empieza con la relación más sencilla de tutorías.',
 'La pata de gallo indica muchos. La barra indica uno. Un círculo permite cero instancias.',
 'En el taller dibujamos punteada la relación si el origen es opcional. Eso permite que el destino exista sin un padre. Exigir que un padre tenga hijos necesita, además, una regla del proceso.',
 'Una línea de un pedido puede identificarse con el identificador del pedido y el número de línea. El identificador del padre participa en el del hijo.',
 'Eso es una relación identificadora. No copia todos los datos del padre. Si el hijo ya tiene su propio identificador independiente, esa identificación compartida puede no ser necesaria.',
 'En una relación uno a uno, cada destino puede vincularse con un solo origen. La clave foránea también será única.',
 'Transferible permite cambiar el padre de una instancia. Si se desmarca, el SQL generado bloqueará cambiar una referencia que ya estaba asignada. Los nombres tiene y pertenece describen los dos sentidos.',
 INVITATION],
5:[
 'El modelador puede transformar tus cajas, columnas y relaciones en una instrucción CREATE TABLE.',
 'Ver SQL muestra la definición que produciría tu diseño. La comprobación construye esas tablas en una base temporal de SQLite. Tu base de la carrera queda separada.',
 'Nuestro diseño lógico no es una base Oracle. Lo convertimos a SQLite para practicar aquí.',
 'VARCHAR se transforma en TEXT, con una comprobación de longitud. DATE se transforma en texto con una fecha validada. NUMERIC conserva sus límites de precisión y escala, dentro de las posibilidades del taller.',
 'Un diseño no se comprueba solo guardando un registro válido.',
 'Vamos a intentar repetir una clave primaria, omitir un nombre obligatorio y crear una tutoría de un estudiante inexistente. Lo correcto será que el motor rechace esos tres intentos.',
 'Desde tu computador, pulsa Probar modelo del taller. Se insertará una estudiante y dos tutorías en una base temporal.',
 'Verás los resultados y los intentos rechazados. No cambiamos la base de la carrera. Eso permite comparar el dibujo con lo que SQLite realmente acepta.',
 'Ya puedes explicar qué representa una tabla, cómo identifica sus filas y cómo se relaciona con otra.',
 'Ahora empieza el primer año. Aprenderás a consultar esos datos con SQL. Podrás volver al modelador desde la sala, con la tecla M.',
 INVITATION],
}


def text_digest(text):
    return hashlib.sha256(' '.join(text.split()).encode('utf8')).hexdigest()


def attach_voice_scripts(day,slides):
    scripts=SCRIPTS[day]
    if len(scripts)!=len(slides):
        raise ValueError(f'El día {day} tiene {len(slides)} páginas pero {len(scripts)} guiones, revisa la locución antes de publicar')
    for index,(slide,script) in enumerate(zip(slides,scripts),1):
        slide['narration_id']=f'intro_d{day}_s{index:02}'
        slide['narration_text']=script
