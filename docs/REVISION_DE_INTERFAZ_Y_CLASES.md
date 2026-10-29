# Patrones detectados en la revisión

Esta lista recoge los problemas generales de la revisión del prólogo y del día 2, se aplicó también a las otras aulas, a las cincuenta preguntas de Kashut y a las clases posteriores

| Patrón | Qué había que comprobar | Corrección aplicada |
| --- | --- | --- |
| Atajos globales que capturan escritura | ¿Una letra de un formulario abre otra interfaz? | Los controles y las misiones se limitan a caminar en la sala, las misiones se abren solo con clic, se prueba escribir ESTUDIANTE y fecha_nacimiento desde el bucle real del juego |
| Confundir pendiente con no leído | ¿El aviso sigue parpadeando después de revisarlo? | Se recuerdan las misiones vistas por jornada y se anuncian solo pasos nuevos, tanto en la introducción como en la carrera |
| Presentar todas las tareas antes de tiempo | ¿La persona sabe cuál es la siguiente acción posible? | Clase, Kashut, revisión, modelo y cierre aparecen por etapas |
| Confundir el tamaño de ventana con el escritorio | ¿Sin bordes utiliza realmente todo el escritorio? | Ese modo conserva el monitor actual, usa su resolución y coloca la ventana en su origen, se verificó tamaño y posición en los tres monitores conectados, cambiar a ventana recupera el tamaño elegido |
| Dibujar texto o símbolos sin medir | ¿Caben la frase completa, sus comillas y el indicador de avance? | Prólogo y títulos aprovechan el espacio y ajustan el tamaño, las flechas, el cruce de conjuntos y las estrellas se dibujan con figuras, sin depender de glifos ausentes |
| Reutilizar un dibujo sin adaptarlo al tamaño | ¿Los iconos se pisan con las etiquetas en tarjetas pequeñas? | Los tipos de datos tienen una presentación compacta para el cuaderno y la retroalimentación, además de la versión de pizarra |
| Explicar un término con otros términos nuevos | ¿Se explicó afinidad, regla del negocio o ISO antes de utilizarlos? | El día 2 usa conversiones concretas, notas de 1 a 7 y fechas escritas, las preguntas se contrastan con la materia previa |
| Confundir capacidad con longitud exacta | ¿El estudiante entiende por qué 12 cabe en NUMERIC(10,0)? | Se explica hasta diez posiciones, no exactamente diez, y se muestran límites, decimales y valores más cortos |
| Mezclar diseño lógico y motor SQL | ¿Queda claro por qué se usan VARCHAR y NUMERIC, pero también TEXT, INTEGER y REAL? | Se presentan los dos niveles y la conversión real del modelador, sin prometer equivalencias idénticas entre motores |
| Convertir un estilo de nombres en una regla universal | ¿Se confunde mayúscula o minúscula con una obligación de SQL? | Se distingue el estilo del proyecto de las posibilidades de SQL, se aceptan atributos en minúsculas y se rechazan duplicados que SQLite consideraría iguales |
| Ayudas sin ejemplos | ¿Longitud 1, 80 o 100 significa algo concreto? | Las ayudas muestran qué textos caben, por qué se rechazan y qué capacidad estamos eligiendo |
| Prometer una validación futura sin enseñarla | ¿Dónde se comprueba finalmente la nota ocho? | La clase de creación de tablas del año 2 explica CHECK y sus límites, se prueba en SQLite aceptar 1 y 7 y rechazar 0, 8 y NULL |
| Formularios que exigen pasos innecesarios | ¿Aplicar un atributo deja listo el siguiente? | Al aplicar se conserva el atributo y se limpia el nombre para continuar, Guardar entidad confirma el borrador completo |
| Siluetas y decoraciones ambiguas | ¿Los laterales, brazos, zapatos y objetos se reconocen? | Los sprites compartidos mejoran pelo y piernas laterales, las salas incorporan sillas y portátil, el prólogo muestra una torre y mouse, Marco tiene colisión |
| Recompensas poco claras | ¿Repetir podría producir XP indefinidamente? | Un mismo puntaje no vuelve a premiarse, mejorar la mejor marca entrega solo la diferencia, ese comportamiento se comprueba con el Kashut real |

## Cómo comprobar una clase desde cero

1. Escribir qué debe saber la persona al entrar y qué se explicará por primera vez
2. Introducir cada idea mediante un caso pequeño, con datos que se puedan comprobar a mano
3. Contrastar un caso válido y uno que no cumpla la regla, explicando el motivo
4. Mostrar la misma idea en la pizarra, en sus resultados y en el cuaderno sin cambiar sus nombres arbitrariamente
5. Comprobar que cada pregunta se entiende con lo ya explicado, sin exigir adivinar preferencias del programa
6. Recorrer la tarea desde la interfaz, incluyendo escritura, ayudas, guardado y avisos de finalización
7. Verificar las diapositivas y los audios correspondientes antes de empaquetar

La revisión automática comprueba coherencia, ejecución e interfaces, observar a una persona principiante sigue siendo necesario para evaluar cómo aprende realmente
