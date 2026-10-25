# Revisión pedagógica y técnica

## Diagnóstico comprobado

Se revisaron lecture.py, course_extension.py, curriculum.py, notebook.py, terminal.py, database.py, ui_helpers.py, rendering.py y el generador de datos iniciales

La versión anterior de lecture.py decía "alterarás toda la base de datos" al omitir WHERE en UPDATE, "Colapsa filas idénticas" para GROUP BY y prometía pasar de minutos a milisegundos con un índice

course_extension.py resumía AND y OR con "AND exige que ambas condiciones se cumplan, OR acepta cualquiera", sin recorrer casos concretos, además se añadía al final de la clase una práctica con su consulta de referencia

El cuaderno duplicaba material y presentaba como obligación de SQLite que toda columna no agregada estuviera en GROUP BY, SQLite permite columnas sueltas pero su valor puede no representar al grupo

La paginación independiente repetía el último párrafo mientras cambiaba el código, o conservaba un ejemplo anterior al avanzar la explicación

La terminal autorizaba escrituras por año académico, incluso durante tareas de lectura, el motor aceptaba allow_write sin exigir una referencia validada

## Revisión de las 16 jornadas

Cada jornada conserva sus cuatro ejercicios, los ejemplos utilizan problemas diferentes de los laboratorios y se ejecutan en una copia nueva de la plantilla

| Jornada | Prerrequisito y objetivo | Carencia anterior y demostración nueva | Comprobación y transferencia |
| --- | --- | --- | --- |
| 1/1 | Sin SQL previo, reconocer filas y columnas y consultar | Se empezaba por modelo relacional y tuplas, ahora se recorre una lista real y se consulta a profesores, DISTINCT compara los estados antes y después | Distinguir columna y valor, combinación de dos columnas con DISTINCT, laboratorio conserva estudiantes |
| 1/2 | SELECT y FROM, construir filtros | La metáfora del colador daba paso a una enumeración, ahora se comparan > 5.5 y >= 5.5, Valentina marca la diferencia, AND y OR se recorren con nombres reales | Predecir quién entra y por qué, distinguir identificador y texto, precedencia y paréntesis, transferir a notas menores a cuatro |
| 1/3 | Lectura y filtros, ordenar | Faltaba separar el resultado almacenado del orden mostrado, profesores por nombre y materias por créditos con desempate | Cambiar ASC/DESC, comprobar empates y combinar WHERE antes de ORDER BY |
| 1/4 | ORDER BY, paginar | LIMIT se describía como cantidad exacta, dos páginas de profesores muestran que la última puede ser menor | Calcular OFFSET, distinguir primeros de mejores y construir una consulta por pasos |
| 2/1 | Entender columnas, diseñar estructuras | CREATE TABLE aparecía como una receta de proyectos, clubes y actividades muestran diseño gradual, restricciones y tipos | Interpretar PRIMARY KEY y NOT NULL, distinguir afinidad de validación estricta de tipos de SQLite |
| 2/2 | Tabla, columnas y tipos, insertar | La regla de tipos era demasiado absoluta, talleres muestran correspondencia posicional y NULL | Diferenciar desconocido de cero, explicar clave duplicada y valor obligatorio |
| 2/3 | WHERE e INSERT, cambiar filas | Riesgo descrito sobre toda la base, ahora SELECT identifica el taller y UPDATE cambia una fila de esa tabla | Verificar el resto de filas y reutilizar la condición de selección |
| 2/4 | WHERE y UPDATE, eliminar con seguridad | El borrado se presentaba sin efecto visible, se muestra antes/después y se diferencia DELETE de DROP | Demostración aislada de BEGIN, borrado y ROLLBACK, sin permitir scripts en la partida |
| 3/1 | Datos, NULL y filtros, resumir | Se enumeraban funciones, tutorías permite contar cuatro filas frente a tres asistencias conocidas y calcular 1+0+1 | COUNT(columna) también cuenta ceros, AVG excluye NULL, SUM y extremos sobre datos concretos |
| 3/2 | Agregaciones, formar categorías | Se hablaba de filas completas idénticas, ahora materias distintas comparten créditos y producen un resumen por categoría | Distinguir filas originales de grupos y evitar columnas sueltas arbitrarias |
| 3/3 | WHERE y GROUP BY, filtrar resúmenes | Definición correcta pero sin proceso, se filtran materias con cupos, se agrupa y después se aplica HAVING | Quitar WHERE y predecir cómo cambia el grupo, no poner COUNT en WHERE |
| 3/4 | Identificadores y agrupación, relacionar tablas | JOIN se vinculaba a una supuesta llave compartida obligatoria, se observa estudiante_id y se construye ON con alias | Ignacio tiene dos tutorías, contar coincidencias o personas distintas son preguntas diferentes |
| 4/1 | SELECT, filtros y NULL, subconsultas | Se entregaba una expresión anidada completa sin construirla, primero se consultan ids y luego se usan con IN | Ejemplo ejecutable de NOT IN con NULL, diferenciar orden conceptual del plan físico |
| 4/2 | INNER JOIN, conservar ausencias | Se confundía dato pendiente con ausencia de relación, se comparan id de tutoría y asistencia | Predecir qué columna permite detectar una relación inexistente y respetar uno a muchos |
| 4/3 | SELECT y UPDATE, vistas y transacciones | Se juntaban definiciones sin efectos visibles, una vista de materias cambia al modificar el origen y se recupera con ROLLBACK | Vista guarda consulta, no copia, la terminal administra transacciones y acepta una sentencia |
| 4/4 | Filtros y estructuras, índices | Se prometía rendimiento sin evidencia, se compara EXPLAIN antes y después de crear un índice de profesores | SCAN puede recorrer un índice, SEARCH no mide tiempo, explicar costo de espacio y mantenimiento |

Las cuatro indicaciones de examen presentan cinco preguntas, nota mínima 4,0 con tres aciertos, pruebas sin nota y entrega definitiva separadas, se conserva el currículo de 64 ejercicios y 20 preguntas

## Implementación

- game/lessons/year1.py a year4.py separan las unidades por año, cada unidad incluye título, profesor, explicación, SQL, consulta de inspección, error y comprobación
- game/lessons/__init__.py abre la plantilla en modo lectura y usa una copia en memoria por clase, también calcula las tablas de resultados, las modificaciones de ejemplo nunca llegan a la partida
- game/lecture.py consume páginas coherentes, cada ejemplo y sus resultados permanecen asociados, se conserva escritura progresiva y navegación hacia atrás
- game/sql_syntax.py tokeniza conservando exactamente el texto, distingue comillas escapadas, identificadores entre comillas, comentarios y saltos, azul para palabras clave, blanco para identificadores, verde para texto y rojo para operadores
- game/sql_editor.py gestiona posición, selección y desplazamiento entre líneas, terminal.py integra sangría, historial, portapapeles y repetición de flechas
- database.py exige referencia autorizada para escribir, compara estructura y efectos antes de confirmar, un error o una diferencia deja la transacción sin confirmar y se revierte al cerrar
- hints.py separa orientación conceptual, estructura con nombres y valores sustituidos y solución explicada, F3 solo revela el nivel siguiente, no ejecuta ni premia
- notebook.py comparte fuentes educativas con la clase, conserva desbloqueos y muestra ejemplos con resaltado, resultados largos se identifican explícitamente como muestra
- ui_helpers.py pagina resultados según el espacio real de la tabla, los registros no desaparecen al pasar de ejemplo a resultado

## Controles de la terminal

Enter: nueva línea, Tab: cuatro espacios, flechas: mover el cursor, Shift+flechas: seleccionar, Home/End: extremos de la línea, Ctrl+Home/End: extremos del documento

Ctrl+Enter o F5: ejecutar, durante examen solo probar sin nota, Ctrl+Shift+Enter: entregar definitivamente

F1: cuaderno, F2: catálogo, F3: pistas o detalles del catálogo, F6: resultado completo, PgUp/PgDn: historial, Ctrl+A/C/X/V: selección y portapapeles, Esc: cerrar

## Validación y límites

Las pruebas verifican las cuatro carreras completas, guardados, validación de escrituras, tablas y vistas autorizadas, pistas sin soluciones de examen, editor, tokenizador, ejemplos de las 16 clases y conservación de la plantilla

El entorno permite renderizar y revisar imágenes de Pygame con controlador de vídeo simulado, eso no sustituye una sesión humana de aprendizaje ni una prueba del portapapeles real de Windows

No se incluye edición de scripts de varias sentencias ni transacciones manuales sobre la base del jugador, el control transaccional pertenece al motor, las clases lo indican

Las pistas se conservan durante la sesión, al reiniciar vuelven al primer nivel, no cambia el formato de guardado

Los datos de demostración parten de la plantilla, pueden diferir de una partida que ya modificó registros, la pantalla de resultados lo identifica como copia aislada

Se conservan personajes, diálogos aprobados, teléfono, Liga de Dioses, música y personalización, sin añadir nuevas mecánicas RPG ni empaquetado

Resultado final: 83 pruebas aprobadas, compilación de los módulos sin errores y git diff --check sin errores de formato, revisión visual de pizarra, resultados, editor y cuaderno a 1920 × 1080
