# Versión nativa de Godot

La beta 0.3.0-beta.1 reúne la carrera y las actividades de RPG en Godot, el juego exportado usa SQLite nativo y no inicia Python para las consultas

## Organización

- main.gd conecta la portada, mundo e interfaces
- campaign.gd, study_state.gd y course_data.gd gestionan calendario, guardado y contenido académico
- lecture_view.gd, learning_figure.gd y audio_service.gd presentan pizarras, ilustraciones y narraciones sincronizadas
- school_sql.gd, sql_service.gd y sql_worker.gd ejecutan consultas en un proceso separado, con límite de cinco segundos y bases temporales
- model_logic.gd y modeler_view.gd separan el modelo de sus controles visuales
- nexo_game.gd, nexo_sql.gd y portfolio.gd gestionan ayudas, pruebas de proyectos y exportación
- activities.gd y career.gd incorporan investigaciones, retos y cierre de universidad
- room_layout.gd, room_view.gd y home_shop.gd permiten decorar sin bloquear accesos esenciales
- league_game.gd y league_view.gd implementan Liga y su simulación

Estos archivos viven en godot/scripts/

## Datos y compatibilidad

El progreso de Godot vive en una carpeta propia, al importar se lee el guardado anterior y se copia la base SQLite mediante su API de respaldo, no se trabaja sobre la base original

El historial académico reconstruye solo soluciones aprobadas de escritura, cada intento se evalúa en una copia independiente, el laboratorio libre tiene historial separado

Los proyectos de Nexo comparan tres conjuntos de datos por etapa, los resultados se comparan por valores y no por cantidad de palabras coincidentes, las entregas y compras se revierten si no pueden guardarse

El portafolio incluye ocho archivos por proyecto, entre ellos una base utilizable, el modelo JSON y un verificador de biblioteca estándar Python, ese verificador es opcional y se usa fuera del juego

## Construcción

tools/build_godot.py importa recursos, exporta Windows x64, comprueba el ejecutable y repite la prueba después de extraer el ZIP a otra carpeta, produce un SHA256 para el archivo final

El motor y sus plantillas están fijados en tools/setup_godot.py, no se incluyen en Git, tampoco las partidas, capturas ni archivos de agentes

## Límites de esta beta

El cierre profesional ofrece tres caminos narrativos y permite seguir practicando, todavía no representa una simulación de empleo posterior a la universidad

Nexo es una red ficticia local, sus publicaciones, contactos y recomendaciones no se envían a servicios externos, los likes expresan la progresión del juego

La entrega distribuida y comprobada corresponde a Windows x64, no se han preparado paquetes para otros sistemas
