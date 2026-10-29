# El Camino SQL

**0.3.0-beta.1 · Beta gratuita para Windows x64**

Una aventura educativa de Seavuelo, desde los primeros conceptos de bases de datos hasta consultas, proyectos y recomendaciones profesionales, con clases narradas de Marco, una facultad para explorar y una casa que haces tuya

Proyecto personal para aprender y compartir en GitHub, siempre gratuito, esta beta todavía puede tener errores

## Jugar

Extrae **ElCaminoSQL-Godot-0.3.0-beta.1-Windows-x64.zip** completo y abre **ElCaminoSQL.exe**, conserva junto al ejecutable las bibliotecas incluidas, no necesitas Python ni instalar Godot

El paquete se prepara localmente en dist/, los cambios no se publican automáticamente en GitHub

Con el código fuente, abre **Jugar.cmd** o **Jugar-Godot.cmd**, ambos inician la versión nativa, si falta el motor ejecuta **Preparar-Godot.cmd**, **Abrir-Godot.cmd** abre el editor

## Qué puedes hacer

- Estudiar cinco días introductorios y cuatro años, con 25 clases, pizarras ilustradas y 287 archivos de voz del profesor
- Resolver 64 ejercicios SQL, 20 desafíos de examen y 50 preguntas de Kashut, con pistas por niveles y retroalimentación
- Construir entidades, atributos y relaciones en el modelador, generar el modelo relacional y verificar el SQL con SQLite real
- Usar el cuaderno con buscador y apuntes, experimentar en una base independiente y revisar clases anteriores
- Ayudar mediante Nexo, resolver 15 encargos con datos de prueba y desarrollar tres proyectos de cuatro etapas
- Investigar dos casos mediante documentos, practicar cinco desafíos de filtros, orden, claves, predicción y depuración
- Exportar proyectos con modelo, base SQLite, consultas y pruebas que puedes ejecutar fuera del juego
- Decorar tu habitación, comprar 11 mejoras y artículos, presentar un proyecto final y elegir oportunidades según tus contactos y entregas
- Jugar Liga de Dioses, con nueve dioses, estrategias, reliquias, aumentos y oportunidades de precisión opcionales

La reputación de Nexo, el dinero de la casa y la XP de Liga son independientes, las actividades opcionales no bloquean la carrera, practicar no resta reputación

## Controles y progreso

**WASD** para caminar, **E** para interactuar, el botón **Controles** reúne las instrucciones, **Esc** cierra la interfaz actual, en el editor SQL puedes usar selección, portapapeles, varias líneas y repetición normal del teclado

Marco cierra la jornada cuando completas lo obligatorio, sales por la puerta para volver a casa y duermes para avanzar, puedes seguir practicando antes de irte

Godot guarda en **%APPDATA%/ElCaminoSQL-Godot/study.json**, conserva study.json.bak y aparta los archivos dañados para recuperación, nueva partida pide confirmación

Al detectar una partida anterior, se copia el progreso compatible y una instantánea de su base, sin modificar los archivos de Pygame, los avances de Godot se guardan por separado

Las escrituras solo están permitidas en tareas autorizadas o en el laboratorio libre, las respuestas incorrectas no cambian los datos de las clases, los exámenes no tienen límite de tiempo y los errores de sintaxis no consumen una respuesta

## Desarrollar y comprobar

### Continuar desde otro PC

En el otro PC instala Git y Python 3.11 o superior, clona el repositorio y prepara el motor local

    git clone https://github.com/Seavuelo/elcaminosql.git
    cd elcaminosql
    python tools/setup_godot.py --templates

Después abre **Abrir-Godot.cmd** para editar el proyecto, las voces, música, fuentes y datos del curso están incluidos en el repositorio

Si ya tienes el repositorio clonado y no tienes cambios locales pendientes, usa **git pull --ff-only** para actualizarlo, guarda tus cambios en un commit antes de cambiar de PC y súbelos con **git push**

Las partidas personales, el motor descargado, las cachés y los ejecutables generados se quedan en cada PC, GitHub sincroniza el código y los recursos del proyecto

### Herramientas y pruebas

El motor y los recursos se preparan con versiones y hashes fijados en tools/setup_godot.py, el proyecto nativo está en godot/project.godot, SQLite funciona mediante el complemento incluido

    python tools/setup_godot.py
    python tools/test_godot.py
    python tools/test_godot.py --window
    python tools/build_godot.py

La opción --window comprueba modos de pantalla en el monitor real, las pruebas usan partidas aisladas en .preview/, la construcción prueba el ejecutable y después vuelve a probar el ZIP extraído

El contenido académico original se exporta con python tools/export_godot_content.py, los encargos de Nexo y sus actividades están en JSON propios dentro de godot/data/

[Detalles de la migración](docs/MIGRACION_GODOT.md) · [Diseño y alcance](docs/DISENO_GODOT.md) · [Cambios de la beta](docs/releases/v0.3.0-beta.1.md) · [Música y créditos](CREDITS.md)

La implementación anterior sigue disponible con **Jugar-Pygame.cmd**, su documentación se conserva en [Referencia Pygame](docs/REFERENCIA_PYGAME.md), sus pruebas se ejecutan con python -m unittest discover -s tests -q

## Créditos

Creado por **Seavuelo**, Godot y Godot-SQLite usan licencia MIT, Inter, Fraunces y JetBrains Mono usan SIL OFL, la música mantiene sus atribuciones, puedes consultar los avisos completos dentro de Controles → Licencias y componentes

[Repositorio](https://github.com/Seavuelo/elcaminosql)
