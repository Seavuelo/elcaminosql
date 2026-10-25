# El Camino SQL 🎓💻

**v0.2.0-alpha.1 · Versión experimental — una beta de la beta**

Este proyecto está empezando, esta entrega sirve para jugar, probar y dar comentarios, todavía puede tener errores y detalles pendientes

Para jugar sin instalar Python, usa el ZIP de Windows x64 adjunto al [pre-release en GitHub](https://github.com/Seavuelo/elcaminosql/releases), extrae todo y abre `ElCaminoSQL.exe`, mantén `_internal` junto al ejecutable

[Notas de esta versión](docs/releases/v0.2.0-alpha.1.md) · [Cómo subir cambios y publicar](docs/PUBLICAR.md)
### *"Para todo buen final, hay un inicio..."*
*Desarrollado por Seavuelo*

Un videojuego educativo de rol y aventura en **pixel art retro**, donde todo el aprendizaje, misiones y progresión se basa en **consultas SQL reales** ejecutadas en una base de datos local SQLite.

---

## Instalación y ejecución

Si descargaste el código fuente, en Windows haz doble clic en **Jugar.cmd**. Usa el entorno local si ya existe; si falta, prepara las dependencias. Solo la primera preparación necesita internet. Requiere Python 3.10 o superior instalado.

En Windows solo se permite una instancia del juego, las aperturas adicionales se cierran
antes de cargar gráficos o audio, el bloqueo se libera automáticamente al salir

También puedes iniciar desde una consola:

```powershell
python -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python main.py
```

En Linux/macOS usa `.venv/bin/python` en lugar de `.\.venv\Scripts\python`.
La base incluida ya contiene los datos iniciales; no necesitas ejecutar el script de semillas.

Para ejecutar las pruebas automáticas sin abrir una ventana ni usar audio real:

```powershell
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Progreso y base de práctica

La partida, los ajustes y la base de práctica se guardan en `~/.config/sql-quest/`
(`savegame.json`, `config.json` y `universidad.db`). Se guarda cada ejercicio aprobado,
clase completada y respuesta de examen. Las partidas anteriores siguen siendo legibles;
el progreso dentro del día que la versión anterior no guardó no se puede recuperar.

La base de `database/universidad.db` se usa como plantilla. Una nueva partida restaura
la base de práctica. Al repetir Año 2 se restauran los datos para poder rehacer las
creaciones e inserciones; al repetir Año 4 se eliminan la vista y el índice del curso.

Los ejercicios de escritura comparan estructura y datos con el resultado esperado antes
de confirmar los cambios. Una respuesta incorrecta se deshace automáticamente.
En los exámenes, **Ctrl+Enter o F5 prueban sin nota** y **Ctrl+Shift+Enter entrega** la respuesta definitiva.
Las escrituras de prueba se revierten. No hay límite de tiempo y los errores de sintaxis
no consumen respuestas. Con 0, 1, 2, 3, 4 o 5 aciertos se obtiene respectivamente
un 1.0, 2.0, 3.0, 4.0, 5.5 o 7.0 (60% de exigencia).

La tabla de práctica `tutorias` incorpora relaciones uno a muchos, asistencias NULL
y estudiantes sin tutorías, para practicar casos que no aparecen en los datos originales.

## Carrera de cuatro años

- **Año 1:** SELECT, WHERE, ORDER BY y LIMIT.
- **Año 2:** CREATE TABLE, INSERT, UPDATE y DELETE.
- **Año 3:** agregaciones, GROUP BY y JOIN.
- **Año 4:** subconsultas, LEFT JOIN, vistas, índices y EXPLAIN QUERY PLAN.

Cada año tiene cuatro jornadas de cuatro ejercicios y un viernes con cinco preguntas de examen: 64 ejercicios y 20 preguntas en total. Las clases y el cuaderno incluyen el material adicional.

---

## ⚙️ Menú de Ajustes y Configuración (`[O]` o `[F2]`)

Al iniciar o durante la partida, puedes presionar la tecla **`[O]`** o **`[F2]`** para configurar:
- **Modo de Pantalla**: `Ventana`, `Pantalla Completa` o `Ventana sin Bordes`.
- **Resolución**: `960x600`, `1280x720`, `1366x768` o `1920x1080` (Full HD)
- **Volumen de Música**: Música de fondo lo-fi relajante para estudiar/concentrarse.
- **Volumen de Efectos**: Sonidos de teclado mecánico, campanilla de éxito satisfactoria y tiza de pizarra.
- **Persistencia**: Tus ajustes se guardan automáticamente en `~/.config/sql-quest/config.json`.

---

## 🏛️ Dinámica Pedagógica: La Semana Universitaria (Días 1 al 5)

Cada día de la semana tiene una estructura clara:
1. **La Clase Teórica en la Pizarra**:
   - El **Profesor Marco** explica el concepto en la pizarra con diagramas de tiza, tablas de datos y ejemplos de sintaxis.
2. **El Laboratorio Práctico**:
   - Te sientas en tu estación de trabajo y abres tu **Terminal SQL** para resolver la misión del día.
3. **El Ciclo Académico**:
   - **Día 1**: Introducción al modelo relacional, `SELECT` y `FROM`.
   - **Día 2**: Filtros de condición con `WHERE` y operadores numéricos/texto.
   - **Día 3**: Ordenamiento de registros con `ORDER BY` (`ASC` / `DESC`).
   - **Día 4**: Límites y combinación de `WHERE` + `ORDER BY` + `LIMIT`.
   - **Día 5 (Viernes de Examen Parcial)**:
     - 5 desafíos integradores sobre materia practicada, con catálogo y apuntes disponibles.
     - Calificación oficial en escala chilena de **1.0 a 7.0** (nota de aprobación: **4.0**).
     - **Si apruebas (>= 4.0)**: ¡Avanzas al siguiente año! Al aprobar Año 4 obtienes el título.
     - **Si repruebas (< 4.0)**: Repites la semana. El profesor Marco te recibe con su clásico: *"¡Vaya, veo caras conocidas! Un gusto verte de nuevo por aquí... parece que le tomaste cariño a la materia."*

---

## 📊 Visualizador de Tablas y Base de Datos

En la Terminal SQL:
- **Salto de línea responsivo**: Los textos y explicaciones nunca se desbordan de sus marcos.
- **Data Grid Visual**: Cuadrícula con celdas, índice de filas (`#`), líneas divisorias y rayado de cebra.
- **Catálogo de Esquema (`[F2]`)**: Permite navegar entre pestañas visuales (`[estudiantes]`, `[materias]`, `[notas_parcial]`, `[profesores]`) con las teclas `[1, 2, 3, 4]` para inspeccionar la estructura real de cada tabla.

---

## 🎮 Controles

- **`[W, A, S, D]` o `[Flechas]`**: Moverse por el aula.
- **`[E]` o `[ENTER]`**: Interactuar (PC, Profesor Marco, Biblioteca).
- **`[O]` o `[F2]`**: Abrir menú de ajustes y pantalla.
- **`[F2]`**: Ver el catálogo visual de tablas en la terminal.
- **`[ENTER]`**: Nueva línea en el editor SQL, Tab añade sangría
- **`[CTRL+ENTER]` o `[F5]`**: Ejecutar o probar sin nota en examen
- **`[CTRL+SHIFT+ENTER]`**: Entregar la respuesta definitiva en examen
- **`[PgUp/PgDn]`**: Historial, flechas para mover el cursor, Shift para seleccionar, Ctrl+A/C/X/V para seleccionar todo, copiar, cortar y pegar
- **`[F3]`**: Objetivo y pistas progresivas, orientación, estructura y solución explicada, sin soluciones en exámenes
- En el catálogo F3 muestra datos completos
- **`[C]`**: Cambiar apariencia desde el aula sin perder progreso.
- **`[FLECHAS ARRIBA / ABAJO]`**: Historial de consultas.
- **`[N]`**: Abrir el cuaderno de apuntes (en la terminal usa `[F1]`).
- **`[Q]`**: Guardar y salir desde el aula.
- **`[ESC]`**: Salir de menús o cerrar la terminal.

## Personalización y música

El editor permite elegir seis tonos de piel, nueve colores de cabello, cinco peinados,
nueve colores de ropa, seis colores de ojos, seis de pantalón, seis de zapatos y seis de
mochila. Hay cuatro estilos de ropa (polera, polerón, chaqueta y rayas) y dos de calzado.
Usa las flechas para navegar y cambiar; R gira la vista previa y ENTER confirma.
La lista se desplaza al navegar. La vista previa utiliza los mismos sprites que el juego.
Las partidas anteriores reciben las opciones nuevas con valores predeterminados.

Las letras se renderizan con tres veces más detalle y se ajustan a la resolución de la ventana
El mundo conserva sus sprites retro, cada peinado tiene vistas frontal, trasera y laterales

La pantalla principal conserva el acompañamiento original suave de acordes
Los días 1 a 4 usan Satisfying de FASSounds y los días 5 A Kind Of Hope de Scott Buckley
El volumen inicial es 18%, las preferencias guardadas se conservan y se ajustan con O
Las pistas se reproducen en bucle y cambian al avanzar la jornada, los créditos y las
licencias están en CREDITS.md, los efectos originales siguen funcionando

Los diálogos largos, clases y apuntes se dividen en páginas para conservar todo el texto.

## Compañeros y salida del aula

Al completar los ejercicios de la jornada, habla con un compañero y termina su diálogo
para que guarde sus cosas, apague el PC, se levante y camine hacia la puerta
Los viernes esta despedida se habilita al terminar el examen
Puedes volver a hablarle mientras sale, repetirá su texto y continuará el recorrido
Las conversaciones y los menús pausan las animaciones, al cambiar de día los compañeros regresan

Moshi ocupa la mesa central de la fila inferior y acompaña al jugador durante los cuatro años
Tiene pelo castaño claro, ojos pardoverdes y ropa en tonos café, sin lentes
Su pelo largo también se ve de perfil y de espaldas
Sus cuarenta diálogos combinan humor con detalles breves sobre la materia de cada jornada

Los compañeros estudian mirando el monitor, al guardar sus cosas giran de perfil
y mueven los brazos antes de apagar el equipo y levantarse
Se conservan los diálogos revisados con el usuario y los demás tienen conversaciones
propias de estudiantes, con dudas, humor y temas fuera de la clase

## Editor y catálogo SQL

El cursor es fino y sigue la altura del texto, mantén izquierda o derecha para desplazarte
También se puede mantener retroceso o suprimir, Inicio y Fin saltan a los extremos
Enter no se repite automáticamente, para evitar entregas de examen accidentales
Las pestañas, cabeceras y valores se ajustan reduciendo la fuente y usando varias líneas
sin recortar los nombres ni redondear los valores de las celdas

## Teléfono y Liga de Dioses

Abre el teléfono con P desde el aula o con F4 y el botón Teléfono desde clases y terminal
Es una actividad opcional, no necesitas jugar para avanzar en SQL

Recompensas académicas, una vez por cada logro:

- Ejercicio SQL aprobado: 100 XP
- Clase completada: 50 XP
- Jornada completada: 150 XP
- Examen aprobado: 1000 XP

La experiencia compra aumentos de visión, mecánicas, posicionamiento, objetivos y maestría
Cada aumento tiene diez niveles, empieza en 100 XP y su coste aumenta 60 XP por nivel
La maestría es independiente para Astra, Bront y Nix, los otros aumentos se comparten
Puedes elegir jugar Seguro, con Presión o En equipo, las estrategias y los dioses tienen afinidades

Las partidas son simulaciones locales de catorce segundos, no requieren internet ni cuestan XP
Siguen avanzando con el teléfono cerrado mientras juegas, al terminar muestran victoria o derrota y K/D/A
No entregan XP para evitar repetir partidas como sustituto de aprender SQL
Tres partidas de colocación permiten salir de Unranked, después los rangos son Madera,
Fierro, Platilla, Dorado, Platino, Rubí, Prime y GOD
Las victorias dan 45 puntos de liga y las derrotas restan 12, sin bajar de cero
No hay resultados garantizados, los aumentos mejoran las probabilidades y el rendimiento

Usa 1 o 2 para las pestañas, flechas para elegir dios o aumento, S para estrategia y Enter
para buscar partida o comprar el aumento seleccionado, también puedes usar el ratón
El saldo, las compras, el rango y la partida en curso se guardan con tu partida académica

### Clases y editor SQL

Las partidas nuevas comienzan en un aula opcional con el profesor Marco, Moshi, Carlos, Sofía y Matías, cinco computadores, clases en pizarra con dibujos y un Kashut de diez preguntas por d?a

7 aciertos dan tercer puesto, 8 o 9 segundo y 10 primero, con celebraci?n, retroalimentaci?n y XP para Liga de Dioses por el mejor resultado, el primer d?a solo exige conceptos

El estudio de modelamiento tiene lienzo completo, zoom y desplazamiento, propiedades de entidades y atributos, UID compuestos, tipos VARCHAR, NUMERIC y DATE, relaciones 1:1, 1:N y N:M, roles, opcionalidad, identificaci?n y conversi?n autom?tica al relacional

Las relaciones generan restricciones SQLite reales, N:M crea una tabla intermedia, las ayudas ? explican cada campo y el botón Tarea muestra el objetivo cuando existe

El cuaderno tiene secciones, buscador por palabras, ilustraciones y Mis notas para escribir apuntes propios

En la sala, E o clic interactúan, Esc abre pausa para guardar u omitir el taller, desde la carrera M permite volver al estudio, el progreso y los diseños existentes se conservan

Consulta [Taller y modelador](docs/TALLER_Y_MODELADOR.md) para controles, reglas de XP, funcionamiento y límites comprobables

Las 16 jornadas usan demostraciones con resultados reales sobre una copia aislada, el cuaderno comparte su contenido y el SQL tiene resaltado de sintaxis

F6 abre el resultado completo cuando la tabla no cabe en pantalla

La auditoría, los cambios por jornada y los límites verificados están en [docs/REVISION_PEDAGOGICA.md](docs/REVISION_PEDAGOGICA.md)

### Música y protección de la partida

El menú usa Bathroom Chill y las clases y días normales usan Lounge Chill Nu Jazz Restaurant de Alex Morgan, los días de prueba conservan A Kind Of Hope

Las versiones OGG del menú y las clases tienen fundidos circulares preparados en el propio audio para evitar un corte seco al repetirse

Si existe una partida, Nueva partida muestra una advertencia de pérdida de progreso, Cancelar está seleccionado por defecto, Esc cancela y empezar de nuevo requiere una elección explícita

### Voz del profesor Marco

Las cinco clases introductorias incluyen 69 fragmentos de Santa preparados en OGG, el juego reproduce los audios sin cargar Kokoro

El texto visible conserva su redacción, el guion de voz separado usa puntuación y pausas naturales

F7 activa o desactiva la voz, F8 repite la diapositiva y O abre los ajustes de volumen durante la clase, la música baja mientras Marco habla

### Presentación y controles

El acabado visual comparte paleta, paneles con relieve, botones centrados, pizarras de madera e ilustraciones detalladas, las aulas conservan sus dimensiones y colisiones

Un único botón Controles · F10 muestra los atajos de la pantalla actual, también se abre con F10 y se cierra con F10 o Esc, la ayuda detiene las acciones y los temporizadores mientras está abierta
