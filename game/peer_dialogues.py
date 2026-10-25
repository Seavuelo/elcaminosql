"""Conversaciones de compañeros, conservando los textos ya revisados"""

PEER_DIALOGUES = {'sofia': {'before': {(1, 1): 'Hola, soy Sofía, ¿es tu primera vez con SQL? Yo estuve mirando la guía anoche, '
                              'pero una cosa es leerla y otra sentarse acá',
                      (1, 2): '¿Trajiste tus apuntes? Yo anoté un ejemplo de cada cosa y ahora no encuentro el '
                              'que necesito, voy a terminar poniendo pestañas como mi mamá... aunque igual ganan '
                              'bien... ¿y si me salgo?',
                      (1, 3): 'Hoy me senté adelante para ver mejor la pizarra y ahora el profe me mira cada vez '
                              'que pregunta algo, pésima estrategia',
                      (1, 4): 'Hice una lista con lo que tengo que repasar para mañana, después hice otra más '
                              'corta porque con la primera no me alcanzaba el día, ¿tú ya empezaste a estudiar?',
                      (1, 5): 'Repasé anoche y en la casa me salía todo, pero llegué acá y le pregunté a Carlos '
                              'cómo se escribía SELECT, necesito que el profe reparta la prueba antes de que se '
                              'me olvide mi nombre',
                      (2, 1): 'Traje un dibujo de cómo quiero que queden las tablas, Carlos me preguntó si estaba '
                              'haciendo el plano de una casa, si esto falla tengo el croquis listo',
                      (2, 2): 'Anoté los datos en el mismo orden que las columnas para no enredarme, igual voy a '
                              'revisar antes de apretar porque me conozco',
                      (2, 3): 'Hoy voy a mirar primero qué filas cambiaría mi consulta, después del susto de '
                              'Carlos con los sueldos prefiero no hacerme la valiente',
                      (2, 4): 'Tengo una pestaña de apuntes que dice BORRAR CON CUIDADO, así en grande, me estoy '
                              'dejando advertencias a mí misma',
                      (2, 5): 'Esta vez sí desayuné antes de venir, aprendí algo del año pasado aunque el profe '
                              'no lo ponga en la prueba',
                      (3, 1): 'Hoy toca sacar promedios, por fin voy a usar esa función para algo que no sea '
                              'calcular cuánto necesito para pasar',
                      (3, 2): 'Estoy intentando no mezclar lo que pide la pregunta con lo que yo quiero mostrar, '
                              'me emociono y termino agregando media tabla',
                      (3, 3): 'Tengo WHERE y HAVING uno al lado del otro en los apuntes, hoy vamos a descubrir si '
                              'los entiendo o si solo los subrayé bonito',
                      (3, 4): 'Hoy voy a unir tablas sin copiar todo a mano, si esto sale bien le debo una '
                              'disculpa a las tardes que perdí haciendo eso',
                      (3, 5): 'Ya somos cuatro en la sala y todavía me pongo nerviosa antes de las pruebas, Moshi '
                              'dice que es normal, yo digo que podrían ponerlas después de almuerzo',
                      (4, 1): 'Ya estamos en el último año y sigo trayendo dos lápices por si uno falla, el '
                              'computador puede tener todas las herramientas del mundo, yo igual traigo dos',
                      (4, 2): 'Leí el ejemplo del LEFT JOIN anoche y pensé que estaba listo, hoy le cambié una '
                              'condición y me dejó pensando de nuevo',
                      (4, 3): 'Si hoy podemos guardar una consulta y usarla después me interesa muchísimo, mi '
                              'carpeta de apuntes ya parece archivo municipal',
                      (4, 4): 'Me gusta que nos enseñen a mirar qué está haciendo SQLite, hasta ahora yo apretaba '
                              'ejecutar y lo miraba como esperando que me entendiera',
                      (4, 5): 'Al final quedamos Moshi, tú y yo, me acuerdo de la primera clase y me da algo, ya, '
                              'terminemos esto y después nos sacamos una foto antes de irnos'},
           'after': {(1, 1): 'Me salió, aunque al principio pedí toda la tabla cuando solo me pedían dos '
                             'columnas, ¿a ti qué te costó más?',
                     (1, 2): 'Estuve un rato cambiando la consulta y tenía mal escrito el nombre de la carrera, '
                             'lo miré tantas veces que ya lo leía bien aunque estaba malo',
                     (1, 3): 'Me quedaron ordenadas las notas de mayor a menor, ahora falta que las mías se vean '
                             'así de bonitas, ¿cómo vas tú?',
                     (1, 4): 'Ya terminé, voy a repasar con Carlos un rato porque me dijo que entendió todo y '
                             'después me preguntó qué entraba en el examen',
                     (1, 5): 'Ya entregué, no quiero comparar respuestas todavía, quiero comer algo primero, ¿vas '
                             'al casino? No alcancé a desayunar de los nervios',
                     (2, 1): 'Ya armé las tablas, me tomó más elegir nombres que escribir el resto, ahora '
                             'entiendo por qué todo el mundo termina poniendo tabla_final_final',
                     (2, 2): 'Me faltó una comilla y pensé que había roto todo, era una comilla, menos mal que no '
                             'alcancé a llamar al profe',
                     (2, 3): 'Cambié solo lo que pedían y revisé el resto, no voy a decir que me volví experta '
                             'porque después viene otro ejercicio y me ubica',
                     (2, 4): 'Ya terminé, borré menos cosas de la base que de mi borrador, voy a estudiar un rato '
                             'antes de irme',
                     (2, 5): 'Entregado, me dieron ganas de revisar una respuesta pero cerré la pantalla, ahora '
                             'sí, ¿vamos a comer algo?',
                     (3, 1): 'Conté las filas de dos formas y no daba lo mismo porque faltaban datos, ahora '
                             'quiero revisar todas las planillas que he hecho en mi vida',
                     (3, 2): 'Ahora me quedó una fila por carrera, al principio tenía una por persona y decía que '
                             'estaba resumido, resumido para mí nomás',
                     (3, 3): 'Me estaba adelantando al filtrar el promedio del grupo, lo separé en pasos y salió, '
                             'el destacador no hizo nada pero quedó precioso',
                     (3, 4): 'Había un nombre repetido porque tenía dos tutorías, yo ya le estaba echando la '
                             'culpa al computador, perdón computador',
                     (3, 5): 'Terminé, hubo una pregunta que resolví en una hoja antes de escribir, quedó tan '
                             'rayada que parece que rendí el examen a lápiz',
                     (4, 1): 'Probé primero la consulta de adentro y después la junté con la otra, me ahorré '
                             'mirar veinte líneas sin saber cuál estaba mala',
                     (4, 2): 'No era lo mismo una persona sin tutorías que una tutoría sin asistencia, menos mal '
                             'miré los datos antes de darlo por terminado',
                     (4, 3): 'La vista funciona y ya no tengo que copiar lo mismo cada vez, igual guardé una '
                             'copia en los apuntes porque todavía no confío tanto en mí',
                     (4, 4): 'Vi el plan de la consulta, no entendí cada palabra a la primera pero ya sé qué '
                             'buscar, eso también cuenta como avanzar',
                     (4, 5): 'Ya entregué el último, me quedé mirando la pantalla un rato porque no sabía qué '
                             'hacer con las manos, ¿nos sacamos esa foto antes de irnos?'}},
 'matias': {'before': {(1, 1): 'Soy Matías, me senté cerca del enchufe por costumbre y ni siquiera traje el '
                               'notebook, al menos ya tengo puesto fijo',
                       (1, 2): 'Ayer le expliqué a mi hermano que WHERE sirve para filtrar y me dijo que lo usara '
                               'para filtrar los mensajes del grupo familiar, no es mala idea',
                       (1, 3): 'Hoy quiero ordenar los resultados y después mi horario, estoy trabajando en una '
                               'cosa a la vez porque con las dos no me da',
                       (1, 4): 'Mañana hay examen y hoy salgo tarde de la pega, si me ves repasando en el '
                               'paradero no me juzgues',
                       (1, 5): 'Vine temprano para repasar tranquilo y ahora llevo diez minutos mirando la hora, '
                               'excelente uso de mi tiempo',
                       (2, 1): 'Me gusta esto de crear las tablas, aunque voy a ponerles nombres decentes antes '
                               'de que el profe vea mi intento llamado cosas',
                       (2, 2): 'Hoy traje los valores anotados para no inventar datos mientras escribo, mi '
                               'proyecto no puede llamarse prueba tres veces',
                       (2, 3): 'Voy a comprobar el WHERE antes de cambiar nada, en mi pega ya hay suficientes '
                               'sustos sin que yo importe uno de la universidad',
                       (2, 4): 'Estoy revisando lo que voy a borrar antes de borrarlo, de repente una idea '
                               'sensata aparece en mi cabeza y hay que aprovecharla',
                       (2, 5): 'Pedí cambiar el turno para venir más despierto al examen, ahora me falta la parte '
                               'de estar más despierto',
                       (3, 1): 'Hoy toca contar y sacar promedios, espero no terminar calculando cuántas horas he '
                               'dormido esta semana',
                       (3, 2): 'Traje una planilla del trabajo y ahora quiero entender cómo haría estos resúmenes '
                               'sin estar copiando celdas toda la tarde',
                       (3, 3): 'Voy a separar el filtro de personas del filtro del grupo, si los junto en mi '
                               'cabeza me sale cualquier cosa',
                       (3, 4): 'Hoy las tablas se hablan entre ellas y yo intento no perderme, por suerte Moshi '
                               'me dibujó las flechas sin cobrarme consultoría',
                       (3, 5): 'Es el último examen del año y todavía me acuerdo del primero, al menos ahora sé '
                               'de qué me estoy poniendo nervioso'},
            'after': {(1, 1): 'Me salió la consulta y no sonó ninguna alarma, buen comienzo, ¿tú ya habías visto '
                              'algo de esto?',
                      (1, 2): 'Había escrito el nombre de la carrera distinto, estuve discutiendo con un filtro '
                              'que tenía toda la razón',
                      (1, 3): 'Lo puse de menor a mayor cuando pedían lo contrario, al menos todos estaban ahí, '
                              'pero al revés de lo que servía',
                      (1, 4): 'Ya terminé, voy a guardar los ejemplos para mirarlos en el viaje, el bus también '
                              'cuenta como sala de estudio si uno se convence',
                      (1, 5): 'Ya entregué, no sé cómo me fue pero ya puedo dejar de ensayar consultas en la '
                              'cabeza por un rato',
                      (2, 1): 'Ya tienen nombre y columnas, cosas pasó a mejor vida, fue una tabla importante '
                              'durante sus treinta segundos de existencia',
                      (2, 2): 'Intenté meter un identificador repetido y no me dejó, por una vez agradezco que el '
                              'computador me diga que no',
                      (2, 3): 'Quedaron los cambios que pedían, voy a cerrar antes de que me dé por mejorar algo '
                              'que ya funcionaba',
                      (2, 4): 'Ya está limpio, ahora me toca limpiar los platos que dejé en la casa, no creo que '
                              'acepten una consulta para eso',
                      (2, 5): 'Entregado, alcancé a revisar las preguntas antes de mandarlas, hoy eso me deja '
                              'bastante tranquilo',
                      (3, 1): 'Conté las filas y después los datos que sí estaban completos, no me daba lo mismo, '
                              'era eso y no que se me hubiera olvidado contar',
                      (3, 2): 'Una fila por grupo, me hace sentido, si aprendo bien esto hay una planilla que me '
                              'va a dejar de quitar años de vida',
                      (3, 3): 'Lo hice por partes y salió, qué rabia lo bien que funciona hacerle caso a ese '
                              'consejo tan simple',
                      (3, 4): 'Me sobraban filas porque había cruzado mal las tablas, no era una base de datos '
                              'grande, era yo multiplicando gente',
                      (3, 5): 'Terminé, si seguimos estudiando el próximo año tenemos que mantener el grupo '
                              'aunque nos cambien los horarios'}},
 'valentina': {'before': {(1, 1): 'Hola, soy Valentina, elegí este puesto porque se ve bien la pizarra, después '
                                  'descubrí que también se ve bien cuando el profe te está mirando',
                          (1, 2): 'Estoy intentando leer primero la pregunta y después escribir, mi método '
                                  'anterior era escribir y después sorprenderme con la pregunta',
                          (1, 3): 'Hoy toca ordenar y eso sí me entusiasma, mi escritorio está lleno de cosas '
                                  'pero en la pantalla me gusta aparentar',
                          (1, 4): 'Tengo que estudiar para mañana, primero iba a ordenar los apuntes pero eso se '
                                  'me puede convertir en una tarde entera eligiendo colores',
                          (1, 5): 'No alcancé a dejar los apuntes bonitos pero sí a estudiarlos, creo que esta '
                                  'vez elegí bien mis prioridades',
                          (2, 1): 'Hoy vamos a crear las tablas, yo ya quiero decidir cómo se verían en una '
                                  'aplicación, el profe todavía no termina de escribir los tipos de datos',
                          (2, 2): 'Si un campo se llama nombre voy a meterle un nombre, parece obvio hasta que '
                                  'ves las cosas que uno escribe para probar rápido',
                          (2, 3): 'Hoy voy a actualizar los datos y después el archivo donde anoto lo que no '
                                  'entendí, ese también necesita mantenimiento',
                          (2, 4): 'Toca borrar, me pasa que quiero guardar todo por si sirve después, hasta las '
                                  'consultas malas me da pena eliminarlas',
                          (2, 5): 'Estuve mirando la carrera de Diseño y me tinca harto, igual quiero terminar '
                                  'bien este año, lo que aprendí aquí no me lo quita nadie'},
               'after': {(1, 1): 'Me salió, ¿a ti también te da gusto cuando el resultado queda ordenadito aunque '
                                 'todavía no tenga ningún color?',
                         (1, 2): 'El filtro ya funciona, no voy a tocarlo más por ahora, tengo un historial de '
                                 'arruinar cosas solo para dejarlas más bonitas',
                         (1, 3): 'Quedó como pedían, ahora puedo disfrutar el orden sin mirar la mochila que dejé '
                                 'abierta botando papeles',
                         (1, 4): 'Ya terminé, voy a repasar sin decorar nada, si me ves cambiándole el título a '
                                 'un apunte por quinta vez me detienes',
                         (1, 5): 'Entregué, por un momento quise ponerle un título más lindo al resultado y me '
                                 'acordé de que era un examen',
                         (2, 1): 'Listas, me gusta pensar quién tendría que usar estos datos después, no quiero '
                                 'que alguien abra mi tabla y tenga que adivinar todo',
                         (2, 2): 'Ya entraron los datos, cambié mis textos de prueba porque el profe no tiene por '
                                 'qué leer mis chistes malos en cada fila',
                         (2, 3): 'Actualizado, antes de ejecutar revisé qué quedaba igual, estoy aprendiendo a no '
                                 'arreglar una cosa rompiendo tres',
                         (2, 4): 'Listo, se fueron las filas que sobraban, igual me dio cosa aunque fuera '
                                 'exactamente lo que pedían',
                         (2, 5): 'Ya entregué, si me cambio de carrera seguimos hablando, alguien va a tener que '
                                 'decirme si mis diseños se pueden hacer de verdad'}},
 'lucas': {'before': {(1, 1): 'Soy Lucas, si me ves mirar la hora no es por la clase, es que dejé un juego '
                              'descargando y quiero saber si alcanzó a terminar',
                      (1, 2): 'Ayer expliqué WHERE como un filtro del inventario de un juego y por fin me hizo '
                              'sentido, necesito que todo tenga espadas para aprender parece',
                      (1, 3): 'ASC y DESC, uno sube y otro baja, lo tengo escrito al lado porque mi memoria '
                              'libera espacio cuando no le pregunto',
                      (1, 4): 'Me dijeron que mañana entra todo lo de la semana, yo quería que entrara solo lo '
                              'que me acuerdo, pero no quisieron negociar',
                      (1, 5): 'Alcancé a repasar, no te voy a decir cuánto porque me va a dar vergüenza, pero '
                              'algo es algo'},
           'after': {(1, 1): 'Me salió, estaba usando el nombre de una columna como si fuera la tabla, gran debut '
                             'de mi parte',
                     (1, 2): 'Funcionó, busqué solo lo que pedían y apareció, ahora quiero un WHERE para '
                             'encontrar el cable que perdí en mi pieza',
                     (1, 3): 'Lo dejé de mayor a menor, quedó parecido a una tabla de posiciones, ya me interesa '
                             'un poquito más',
                     (1, 4): 'Ya terminé, hoy sí voy a estudiar antes de jugar, si te mando una invitación en '
                             'media hora me ignoras',
                     (1, 5): 'Ya está, no quiero revisar respuestas ahora, me voy a comprar algo para comer y '
                             'después vemos si celebro o si estudio de nuevo'}},
 'camila': {'before': {(1, 1): 'Hola, soy Camila, traje lápices de más por si alguien necesita, siempre termino '
                               'prestando el único color que estaba usando yo',
                       (1, 2): 'Estoy anotando ejemplos que entiendo con mis palabras, copiar al profe me queda '
                               'precioso pero después no sé qué estaba copiando',
                       (1, 3): 'Me hice una tarjeta con ASC y DESC, cabe en cualquier parte menos en el lugar '
                               'donde la necesito cuando la busco',
                       (1, 4): 'Mi familia está viendo lo de cambiarnos a Viña, todavía no sé qué va a pasar con '
                               'la sede, mientras tanto intento estudiar para mañana',
                       (1, 5): 'Dormí bien pero soñé que llegaba sin mochila, por lo menos eso ya lo aprobé hoy, '
                               'traje todo'},
            'after': {(1, 1): 'Entendí mejor cuando vi los datos aparecer, leer la explicación ayuda pero yo '
                              'necesito apretar algo para creer',
                      (1, 2): 'El filtro me salía vacío porque escribí distinto el texto, ahora tengo anotado '
                              'revisar eso antes de entrar en pánico',
                      (1, 3): 'Ya ordené las filas, al final estaba la tarjeta dentro del cuaderno, exactamente '
                              'donde yo la había guardado',
                      (1, 4): 'Terminé, si nos cambian de sede te puedo mandar los apuntes igual, el grupo no '
                              'depende de sentarse en la misma sala',
                      (1, 5): 'Ya entregué, voy a avisar en la casa que salí para que no me llamen justo cuando '
                              'esté hablando con el profe'}},
 'diego': {'before': {(1, 1): 'Hola, soy Diego, ¿a ti también te da miedo apretar ejecutar por primera vez? Ya sé '
                              'que no voy a botar la universidad pero igual me demoro',
                      (1, 2): 'Me puse nervioso con el WHERE y todavía ni escribo nada, mi cabeza es buenísima '
                              'adelantando problemas que no han pasado',
                      (1, 3): 'Necesito mantener la beca y ya estoy calculando notas que todavía no existen, '
                              'mejor voy a intentar entender la clase de hoy primero',
                      (1, 4): 'Mañana hay examen y hoy cualquier ruido me distrae, hasta el teclado del de al '
                              'lado me suena como que está entendiendo más que yo',
                      (1, 5): 'Traje agua, lápiz y una cantidad innecesaria de nervios, ¿tú cómo vas? Capaz '
                              'hablar un rato me ayuda a bajar un cambio'},
           'after': {(1, 1): 'No se rompió nada y salieron los datos, voy a tomar eso como una victoria antes de '
                             'mirar el siguiente ejercicio',
                     (1, 2): 'El filtro funciona, el error era mucho más chico de lo que yo había imaginado, '
                             'suele pasarme',
                     (1, 3): 'Ya lo ordené, tenía ASC donde pedían DESC, por suerte eso se cambia más fácil que '
                             'el drama que me armé',
                     (1, 4): 'Terminé, me voy a estudiar y después a dormir, lo segundo también lo estoy poniendo '
                             'en el plan porque siempre se me olvida',
                     (1, 5): 'Entregado, siento que recién me acordé de respirar, voy a caminar un poco antes de '
                             'preguntar por las notas'}}}
