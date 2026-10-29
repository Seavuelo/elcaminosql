# Taller opcional, Kashut y estudio de modelamiento

## Aula y navegación

El profesor se llama Marco en la carrera, en la introducción, en los diálogos y en los datos de profesores, las partidas existentes actualizan el nombre sin reiniciar la carrera

La semana introductoria ocurre en una sala pequeña con cinco computadores, para el protagonista, Moshi, Carlos, Sofía y Matías, WASD o flechas permiten moverse, E o clic interactúan con el profesor, Moshi y el computador

Marco presenta el taller como opcional, explica en la pizarra con ilustraciones y termina invitando a Kashut, el primer día no exige diseñar tablas, los talleres de diseño comienzan después de los conceptos

Esc durante una explicación vuelve a la sala y conserva la página para continuar, sin marcar la clase como terminada, Esc en la sala abre una pausa con opciones para guardar y volver al menú u omitir el taller, al regresar al menú se reactiva TitleScreen

El cuaderno se abre con N, F1 o el botón Cuaderno del estudio, el teléfono se puede abrir con F4 desde la sala

## Kashut

Diez preguntas por jornada, 50 en total, con 25 a 45 segundos por pregunta según el texto que debe leerse, el podio depende de los aciertos y no de la rapidez

- 10 aciertos: primer lugar
- 8 o 9: segundo lugar
- 7: tercer lugar
- Menos de 7: sin podio, con repaso y posibilidad de continuar

El Kashut es local y el podio utiliza a los compañeros presentes en la sala, no a grupos externos

Se celebra entrar al podio y el primer puesto tiene más confeti, después se revisan las respuestas incorrectas, no hace falta quedar en el podio para avanzar

Esc pausa el reloj, Enter continúa y otro Esc guarda y vuelve a la sala, perder el foco de la ventana también pausa, cerrar el juego conserva las respuestas y el tiempo restante

La XP de Liga de Dioses es 40 por completar, 20 por acierto y un bono de 30, 60 o 100 por tercer, segundo o primer puesto, repetir solo concede la diferencia si mejora el mejor resultado, máximo 340 por jornada

## Modelo lógico

El lienzo aprovecha la pantalla completa, con zoom de 20% a 200%, desplazamiento al arrastrar el fondo, entidades movibles y Ctrl+Z para deshacer

Nueva entidad abre propiedades con General y Atributos, para las entidades usamos singular y MAYÚSCULAS, como ESTUDIANTE, y los atributos pueden escribirse en minúsculas, como id o fecha_nacimiento, el guion bajo separa palabras y usamos anio en lugar de año

Aplicar atributo conserva el dato en el borrador y deja vacío el nombre para continuar con el siguiente, Guardar entidad confirma el conjunto, las ayudas muestran ejemplos de longitud, precisión y escala

Cada atributo tiene tipo de origen, longitud o precisión y escala cuando corresponda, UID primario y obligatoriedad, varios atributos pueden formar un UID compuesto

Los botones 1:N, 1:1 y N:M permiten elegir origen y destino, después se abre la relación, también se pueden abrir sus propiedades pulsando la línea

Las propiedades incluyen nombre, roles del origen y destino, transferencia del UID para generar FK, transferibilidad, opcionalidad de ambos extremos e identificación, los botones ? explican el significado de cada campo

La notación muestra patas de gallo, barras y círculos, el origen opcional se dibuja punteado, las etiquetas muestran los roles y una marca UID distingue las relaciones identificadoras

Una relación identificadora incorpora la clave del padre a la primaria del hijo, no copia todos sus datos, es la distinción que documenta la [guía oficial de Oracle Data Modeler](https://docs.oracle.com/en/database/oracle/sql-developer-data-modeler/20.2/dmdug/data-modeler-concepts-usage.html)

## Conversión al relacional y ejecución

Generar relacional construye las tablas en una conexión temporal con claves foráneas activadas, también cambia la vista al esquema generado, pulsar una tabla muestra su SQL

- 1:N transfiere la clave al lado muchos
- 1:1 añade una restricción UNIQUE a la FK
- N:M crea una tabla intermedia con ambas claves, no se necesita esa tabla para una 1:N corriente
- La identificación produce claves primarias compuestas cuando corresponde
- Origen opcional permite una FK NULL
- Transferible desmarcado genera un trigger que impide cambiar una FK ya asignada
- Transferir UID desmarcado conserva la relación solo en el lógico y muestra que no genera integridad automática

VARCHAR se adapta a TEXT con CHECK de longitud, DATE a texto ISO con validación de fecha y NUMERIC a afinidad numérica con comprobaciones de precisión y escala dentro de los límites del taller

La opción Probar modelo del taller en el computador inserta una estudiante y dos tutorías, comprueba el rechazo de una PK duplicada, un nombre NULL y una tutoría con padre inexistente, todo en memoria

## Cuaderno

Secciones Todo, Bases, Modelo, Año 1 a 4 y Mis notas, búsqueda por palabras sin distinguir tildes ni mayúsculas, ilustraciones de filas, claves y relaciones, ejemplos de SQL y apuntes personales editables

Ctrl+F abre el buscador, Enter sale del campo de búsqueda, en Mis notas se escribe con Enter y se guardan con Esc o al cerrar, las notas también se guardan al salir del juego

## Límites explícitos

Es un modelador educativo con SQLite como destino, no un clon completo de Oracle, no se agregan paquetes externos, conexión a Oracle ni ingeniería inversa de servidores

Los nombres singulares son una convención explicada, la validación automática comprueba el formato, no intenta deducir la gramática de cada nombre

La participación mínima que exige hijos para todo padre necesita validación de proceso, una FK sola no la garantiza, al convertir se informa de esta diferencia

NUMERIC usa la aritmética disponible de SQLite, el taller limita precisión a 15 y escala a 6 y no promete exactitud decimal financiera

El diseño y el Kashut se guardan, los modelos de la versión anterior se migran al formato lógico sin borrar los originales, las restricciones adicionales creadas por el alumno pueden requerir datos de prueba adicionales

Las comprobaciones visuales se generan con el controlador de vídeo simulado de Pygame, todavía se necesita una sesión humana completa para evaluar comodidad del ratón, ritmo de las preguntas y claridad de las clases

Validaci?n final: 118 pruebas aprobadas, compilaci?n sin errores y revisi?n visual de sala, pizarra, propiedades, modelo relacional, Kashut y cuaderno a 1920 ? 1080

Las pizarras introductorias cambian de esquema y foco por concepto, se revelan progresivamente al sonar la tiza, cada jornada muestra una transición de dos segundos con Semana Introductoria y su día

Las cinco clases introductorias y las veinte de la carrera tienen 287 audios Santa en assets/voice/marco_intro, los guiones tienen puntuación independiente del texto visible y sus identificadores dependen del contenido, añadir una diapositiva no desplaza las voces de las demás

F7 activa o desactiva la voz, F8 repite el fragmento y O abre ajustes con volumen propio, la narración se corta al cambiar de diapositiva o salir y se pausa al abrir paneles o perder el foco, la música baja mientras habla Marco

Para regenerar: ejecutar tools/build_intro_narration.py --export con el entorno del juego y después tools/build_intro_narration.py con el entorno de preparación, los modelos y dependencias Kokoro permanecen en .preview y no se necesitan al jugar


La estación de estudio muestra la clase, las diez preguntas, su retroalimentación y el taller por separado, los requisitos del modelador se pueden recorrer por páginas y una edición posterior invalida la comprobación del modelo anterior
