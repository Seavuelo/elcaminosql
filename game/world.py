import pygame
import math
from game.constants import *

class Classmate:
    def __init__(self, id_name, name, desk_x, desk_y, pc_offset, min_year, max_year,
                 skin_color, hair_color, shirt_color, dialogues_before, dialogues_after, dropout_note):
        self.id = id_name
        self.name = name
        self.desk_x = desk_x
        self.desk_y = desk_y
        self.pc_offset = pc_offset
        self.px = desk_x + pc_offset
        self.py = desk_y + 3
        self.min_year = min_year
        self.max_year = max_year
        self.skin_color = skin_color
        self.hair_color = hair_color
        self.shirt_color = shirt_color
        self.dialogues_before = dialogues_before
        self.dialogues_after = dialogues_after
        self.dropout_note = dropout_note
        # Zona interactiva alrededor de la silla (al sur de la mesa)
        self.zone = pygame.Rect(self.px - 6, self.py + 18, 32, 26)

    def is_present(self, year):
        return self.min_year <= year <= self.max_year

    def get_speech(self, year, day, day_completed):
        pool = self.dialogues_after if day_completed else self.dialogues_before
        if (year, day) in pool:
            return pool[(year, day)]
        if year in pool:
            return pool[year]
        return pool.get("default", "Hola compañero, acá dándole duro al laboratorio de SQL.")


class World:
    def __init__(self):
        self.colliders = []
        self._build_classroom()
        self._build_classmates()
        self.font_tiny = pygame.font.Font(None, 12)
        self.font_name_tag = pygame.font.Font(None, 10)
        self._build_static_background()

    def _build_static_background(self):
        self.bg_surface = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
        self.bg_surface.fill(COLOR_BG)

        # 1. Suelo ajedrezado
        tile_size = 20
        for y in range(58, 284, tile_size):
            for x in range(16, 464, tile_size):
                color = COLOR_FLOOR_A if ((x // tile_size) + (y // tile_size)) % 2 == 0 else COLOR_FLOOR_B
                pygame.draw.rect(self.bg_surface, color, (x, y, tile_size, tile_size))
                pygame.draw.line(self.bg_surface, (50, 58, 75), (x, y), (x + tile_size, y), 1)
                pygame.draw.line(self.bg_surface, (50, 58, 75), (x, y), (x, y + tile_size), 1)

        # 2. Pared Frontal
        pygame.draw.rect(self.bg_surface, COLOR_WALL, (16, 0, 448, 58))
        pygame.draw.rect(self.bg_surface, COLOR_WALL_TOP, (16, 54, 448, 4))
        
        # Puerta de entrada
        pygame.draw.rect(self.bg_surface, (70, 50, 35), (20, 18, 25, 40))
        pygame.draw.rect(self.bg_surface, (50, 35, 25), (22, 20, 21, 38))
        pygame.draw.circle(self.bg_surface, COLOR_AMBER, (40, 40), 2)

        # Ventanas al exterior
        for wx in [70, 360]:
            pygame.draw.rect(self.bg_surface, (140, 150, 170), (wx, 12, 40, 32))
            pygame.draw.rect(self.bg_surface, (90, 180, 230), (wx + 2, 14, 36, 28))
            pygame.draw.rect(self.bg_surface, (40, 140, 60), (wx + 8, 26, 24, 16))
            pygame.draw.rect(self.bg_surface, (140, 150, 170), (wx + 19, 14, 2, 28))

        # Marco exterior de la pizarra
        pygame.draw.rect(self.bg_surface, COLOR_BOARD_FRAME, (145, 10, 190, 42))

        # 4. Estantería de Libros
        bx, by, bw, bh = 410, 45, 45, 40
        pygame.draw.rect(self.bg_surface, (80, 55, 40), (bx, by, bw, bh))
        book_colors = [(200, 50, 50), (50, 120, 200), (220, 180, 40), (40, 160, 80), (160, 60, 180)]
        for shelf_y in [by + 8, by + 24]:
            pygame.draw.line(self.bg_surface, (50, 35, 25), (bx + 2, shelf_y + 12), (bx + bw - 2, shelf_y + 12), 2)
            cur_x = bx + 4
            for i, c in enumerate(book_colors):
                w_b = 6 if i % 2 == 0 else 7
                pygame.draw.rect(self.bg_surface, c, (cur_x, shelf_y, w_b, 12))
                cur_x += w_b + 1

        # 5. Escritorio del Profesor Turing (base estática)
        pygame.draw.rect(self.bg_surface, COLOR_DESK, (210, 65, 60, 25))
        pygame.draw.rect(self.bg_surface, COLOR_DESK_SHADOW, (210, 85, 60, 5))
        pygame.draw.rect(self.bg_surface, (230, 230, 230), (218, 68, 12, 10))
        pygame.draw.rect(self.bg_surface, (60, 65, 75), (242, 67, 16, 12))

        # 6. Mesas y carcasas de Computadores
        desks = [
            (70, 120),
            (330, 120),
            (70, 190),
            (330, 190)
        ]
        for dx, dy in desks:
            pygame.draw.rect(self.bg_surface, COLOR_DESK, (dx, dy, 80, 28))
            pygame.draw.rect(self.bg_surface, COLOR_DESK_SHADOW, (dx, dy + 24, 80, 4))
            pygame.draw.rect(self.bg_surface, (50, 60, 75), (dx + 15, dy + 28, 16, 8))
            pygame.draw.rect(self.bg_surface, (50, 60, 75), (dx + 50, dy + 28, 16, 8))

            for pc_offset in [12, 48]:
                px = dx + pc_offset
                py = dy + 3
                pygame.draw.rect(self.bg_surface, COLOR_PC_BASE, (px, py, 20, 16))
                pygame.draw.rect(self.bg_surface, (140, 140, 145), (px + 6, py + 16, 8, 4))
                pygame.draw.rect(self.bg_surface, COLOR_PC_BASE, (px + 4, py + 19, 12, 2))
                pygame.draw.rect(self.bg_surface, (190, 190, 195), (px + 2, py + 21, 16, 4))

    def _build_classroom(self):
        self.colliders = []
        
        # Paredes del aula
        self.colliders.append(pygame.Rect(0, 0, 480, 58))
        self.colliders.append(pygame.Rect(0, 0, 16, 300))
        self.colliders.append(pygame.Rect(464, 0, 16, 300))
        self.colliders.append(pygame.Rect(0, 284, 480, 16))

        # Escritorio del profesor
        self.colliders.append(pygame.Rect(210, 65, 60, 25))
        # Estantería de libros
        self.colliders.append(pygame.Rect(410, 55, 45, 30))

        # Mesas de computadores
        self.colliders.append(pygame.Rect(70, 120, 80, 30))
        self.colliders.append(pygame.Rect(330, 120, 80, 30))
        self.colliders.append(pygame.Rect(70, 190, 80, 30))
        self.colliders.append(pygame.Rect(330, 190, 80, 30))

        # Zonas interactivas del entorno
        self.pc_zone = pygame.Rect(74, 146, 36, 26)
        self.prof_zone = pygame.Rect(210, 90, 60, 25)
        self.book_zone = pygame.Rect(410, 85, 45, 20)

    def _build_classmates(self):
        self.classmates = [
            # 1. Carlos (Mesa 1, PC 2 - al lado del jugador). Años 1 y 2.
            Classmate(
                "carlos", "Carlos", 70, 120, 48, min_year=1, max_year=2,
                skin_color=(255, 205, 148), hair_color=(60, 40, 25), shirt_color=(45, 110, 180),
                dialogues_before={
                    (1, 1): "Hola compañero de banco, me vine con tres polerones porque el aire acondicionado de este laboratorio congela hasta las ideas, ojalá no nos toque una consulta muy larga.",
                    (1, 2): "Ojo con la condición WHERE compa, fíjate bien en el menor estricto para no meter alumnos aprobados en la lista de riesgo.",
                    (1, 3): "A Sofía le tomó cinco segundos hacer el ORDER BY, yo todavía estoy buscando la tecla de comillas simples en este teclado medio suelto.",
                    (1, 4): "Con LIMIT tres dejamos solo a los mejores de la facultad, ojalá algún día mi nombre aparezca en ese ranking de promedios.",
                    (1, 5): "Llegó el viernes del juicio compa, acuérdate de leer bien lo que pide cada enunciado antes de mandarle ENTER al terminal.",
                    (2, 1): "Sobrevivimos al primer año compa, mira qué vacía quedó la sala tras las deserciones, ahora nos toca modelar datos desde cero con CREATE TABLE.",
                    (2, 2): "Cuidado con los tipos de datos al hacer INSERT, si metes un texto donde va un número SQLite se vuelve loco.",
                    (2, 3): "El profe advirtió tres veces no tirar un UPDATE sin WHERE, casi actualizo el sueldo de toda la universidad compa.",
                    (2, 4): "Hoy es día de limpieza con DELETE, un paso en falso y mandamos los registros a la papelera sin retorno.",
                    (2, 5): "Segundo examen de año compa, ya no somos los novatos asustados del año pasado, a ponerle talento."
                },
                dialogues_after={
                    (1, 1): "Qué velocidad compa, te demoraste nada en sacar el SELECT, anda a despedirte de Turing antes de que se le ocurra mandarnos tarea para la casa.",
                    (1, 2): "Bien jugado con los filtros compa, ya tienes la jornada lista, anda a marcar asistencia con Turing para que quede registrado en el acta.",
                    (1, 3): "Listo el podio de notas compa, te quedó filete la consulta, pasa al escritorio del profe a avisarle que ya terminaste.",
                    (1, 4): "Excelente rendimiento compa, mañana se viene el viernes de examen así que guarda bien tus apuntes antes de salir.",
                    (1, 5): "Ya cumplimos la misión compa, ahora a esperar que Turing nos dé la nota para saber si pasamos invictos.",
                    (2, 1): "Buena tabla compa, ya le agarraste el truco al diseño de tablas, avísale al profe para cerrar la clase.",
                    (2, 2): "Poblaste la base sin fallos compa, cada vez estamos más cerca del nivel senior, anda con Turing a visar el laboratorio.",
                    (2, 3): "Salvados por la cláusula WHERE compa, modificaste justo lo necesario, habla con el profe para dar por cerrado el día.",
                    (2, 4): "Limpieza quirúrgica compa, borraste exactamente lo pedido, avísale a Turing antes de que empiece a apagar las luces.",
                    (2, 5): "Terminamos el examen de segundo año compa, qué alivio tremendo sacarse esta materia de encima."
                },
                dropout_note="Nota pegada de Carlos: 'Encontró trabajo como soporte técnico y no le dieron permiso laboral para los horarios de 3er año...'"
            ),

            # 2. Sofia (Mesa 2, PC 1). ¡Está presente los 4 años completos!
            Classmate(
                "sofia", "Sofía", 330, 120, 12, min_year=1, max_year=4,
                skin_color=(255, 215, 175), hair_color=(180, 120, 40), shirt_color=(190, 60, 90),
                dialogues_before={
                    (1, 1): "Hola colega, me leí el libro de Codd anoche, la proyección de atributos en el álgebra relacional es bellísima si comprendes bien los conjuntos.",
                    (1, 2): "Recuerda separar siempre las columnas con comas y no poner comas antes de FROM, ese es el detalle donde cae la mayoría.",
                    (1, 3): "El ORDER BY evalúa el orden después de seleccionar las filas, por eso va casi al final de la consulta según el estándar internacional.",
                    (1, 4): "LIMIT combinado con ORDER BY es la técnica que usan los motores de búsqueda para entregar resultados en milisegundos.",
                    (1, 5): "Respira profundo antes de contestar cada pregunta del examen, confía en tu preparación y revisa el esquema con TAB si dudas.",
                    (2, 1): "Definir llaves primarias con PRIMARY KEY es la base de la integridad referencial, sin eso los datos se corrompen en producción.",
                    (2, 2): "Al insertar tuplas respeta el orden de las columnas declaradas, así evitas conversiones implícitas que degradan el rendimiento.",
                    (2, 3): "Un UPDATE sin WHERE es la pesadilla de cualquier pasante en una empresa, siempre haz un SELECT previo para verificar qué filas tocarás.",
                    (2, 4): "Con DELETE debes tener el mismo cuidado que con UPDATE, asegurando que solo afectes las tuplas obsoletas.",
                    (2, 5): "Segundo examen parcial, Alex, demostremos todo lo que aprendimos sobre manipulación de datos.",
                    (3, 1): "Las funciones de agregación como COUNT y AVG colapsan miles de filas en un solo valor analítico, es pura magia estadística.",
                    (3, 2): "GROUP BY agrupa por categorías, recuerda que cualquier columna en el SELECT debe estar en el GROUP BY o dentro de un agregado.",
                    (3, 3): "La diferencia clave entre WHERE y HAVING es temporal, WHERE filtra antes de agrupar y HAVING filtra los grupos ya calculados.",
                    (3, 4): "El INNER JOIN es el corazón del modelo relacional de Codd, donde dos mundos separados se unen mediante llaves foráneas.",
                    (3, 5): "Examen de 3er año, Alex, solo quedamos tres en la sala pero nuestro nivel técnico es altísimo, a darlo todo.",
                    (4, 1): "Las subconsultas anidadas permiten que el resultado de una consulta alimente a otra dinámicamente, es computación pura.",
                    (4, 2): "El LEFT JOIN asegura que ningún registro de la entidad principal quede fuera, rellenando con NULL donde no hay coincidencia.",
                    (4, 3): "Crear vistas y gestionar transacciones con ACID es lo que separa a un aficionado de un verdadero ingeniero de software.",
                    (4, 4): "Un índice en árbol B transforma búsquedas de costo lineal en búsquedas logarítmicas, optimizar es el sello del senior.",
                    (4, 5): "Llegó el Examen de Grado, Alex, no puedo creer que de los ocho que entramos en primer año solo quedemos tú y yo en esta sala, vamos a titularnos juntos."
                },
                dialogues_after={
                    (1, 1): "Brillante trabajo de proyección, Alex, anda a registrar tu firma en el escritorio del profesor para irnos a descansar.",
                    (1, 2): "Excelente filtrado de datos, Alex, te felicito por la precisión con los tipos de datos, avísale a Turing para avanzar.",
                    (1, 3): "Quedó impecable la clasificación, Alex, tienes futuro como administradora o administrador de bases de datos, no olvides hablar con el profe.",
                    (1, 4): "Misión cumplida por hoy, ya dominamos la lectura completa, mañana a dar un examen brillante frente al profesor.",
                    (1, 5): "Sabía que lo lograrías con creces, compañero, vamos con el profesor Turing a revisar el acta final.",
                    (2, 1): "Estructura impecable, Alex, crear tablas limpias es la mitad del trabajo de cualquier arquitecto de software.",
                    (2, 2): "Datos consistentes y bien ingresados, Turing va a estar muy contento con nuestra rigurosidad hoy.",
                    (2, 3): "Actualización segura y precisa, eso demuestra verdadera madurez profesional en el laboratorio.",
                    (2, 4): "Registros depurados a la perfección, ahora la base de datos está normalizada y libre de redundancia.",
                    (2, 5): "Excelente examen, compañero, dos años aprobados con distinción, cada vez más cerca del título.",
                    (3, 1): "Cálculo analítico perfecto, ya no solo consultamos datos, ahora producimos métricas para la toma de decisiones.",
                    (3, 2): "Agrupamiento sin fallas, Alex, esa consulta responde exactamente lo que pediría una gerencia de ingeniería.",
                    (3, 3): "Dominaste la sutileza de HAVING, muy pocos programadores junior entienden esa distinción al primer intento.",
                    (3, 4): "Cruce de tablas impecable, ya podemos conectar cualquier esquema empresarial sin problemas.",
                    (3, 5): "Aprobamos 3er año, Alex, mañana entramos al último año de la carrera, casi podemos tocar el título con las manos.",
                    (4, 1): "Subconsulta elegante y eficiente, Alex, estamos listos para los desafíos de arquitectura más complejos.",
                    (4, 2): "Manejo perfecto de valores nulos, muy pocos logran esa fineza en consultas multitabla.",
                    (4, 3): "Transacción atómica y vista creada, el sistema es consistente y tolerante a fallos.",
                    (4, 4): "Plan de ejecución verificado con EXPLAIN, ya no hay cuellos de botella en nuestra base de datos.",
                    (4, 5): "Lo logramos, Alex, somos oficialmente Ingenieros Informáticos titulados, qué orgullo haber sido tu compañera todos estos años."
                },
                dropout_note=""
            ),

            # 3. Matias (Mesa 2, PC 2). Años 1, 2 y 3.
            Classmate(
                "matias", "Matías", 330, 120, 48, min_year=1, max_year=3,
                skin_color=(230, 180, 130), hair_color=(30, 30, 35), shirt_color=(50, 150, 80),
                dialogues_before={
                    (1, 1): "Buena compa, mi ventilador está sonando como turbina de avión pero este SELECT no me va a ganar la pulseada.",
                    (1, 2): "Casi me da un patatús compa, puse nota menor a cuatro pero se me olvidó la comilla simple y me salían cero filas.",
                    (1, 3): "En C++ programar un ordenamiento me tomaba cincuenta líneas de código, acá con ORDER BY se hace en una pura palabra compa.",
                    (1, 4): "Me tomé dos tazas de café bien cargado para no quedarme dormido sobre el teclado, mañana es la prueba de fuego.",
                    (1, 5): "Modo concentración activado compa, que la fuerza de los servidores nos acompañe hoy día.",
                    (2, 1): "Le cambié la pasta térmica al PC del laboratorio compa, ahora sí que este CREATE TABLE vuela.",
                    (2, 2): "Estoy metiendo los registros uno por uno con INSERT, me siento como digitador de banco en los años noventa.",
                    (2, 3): "El teclado me tiró un doble ENTER y casi meto el UPDATE sin el filtro, me salvé por un pelo de alterar todo.",
                    (2, 4): "DELETE es como formatear el disco duro compa, hay que hacerlo con las dos manos firmes y sin distracciones.",
                    (2, 5): "Segundo viernes de examen compa, a demostrar que los del fondo también sabemos programar.",
                    (3, 1): "Quedamos poquísimos en 3er año compa, mira las mesas vacías, pero acá seguimos firmes con las funciones de agregación.",
                    (3, 2): "GROUP BY me tenía mareado pero entendí que es como armar carpetas con los archivos del disco duro.",
                    (3, 3): "HAVING es el filtro de los grupos compa, no te vayas a confundir con WHERE que Turing no perdona esa.",
                    (3, 4): "INNER JOIN es la gloria compa, unir dos tablas por su ID es lo más satisfactorio que he visto en toda la carrera.",
                    (3, 5): "Examen de 3er año compa, si aprobamos hoy ya estamos a un paso de la tesis."
                },
                dialogues_after={
                    (1, 1): "Wena compa, le sacaste brillo a la consola, avísale a Turing que ya tienes todo listo para ir a tomar aire.",
                    (1, 2): "Te quedó de lujo el filtro compa, yo ya casi encuentro el error tipográfico en mi terminal, pásale el visto bueno al profe.",
                    (1, 3): "Qué velocidad compa, ordenaste la base completa sin transpirar, anda a reportarle al profe Turing.",
                    (1, 4): "Listo por hoy compa, a descansar los ojos de la pantalla que mañana tenemos que estar despiertos para el examen.",
                    (1, 5): "Sobrevivimos compa, si Turing me aprueba hoy juro que le limpio los cables al computador del laboratorio.",
                    (2, 1): "Buena tabla compa, ya no nos caemos con la sintaxis, habla con Turing antes de que se vaya al departamento.",
                    (2, 2): "Impecable compa, cero errores de llave duplicada, avísale al profe para ir a comprar café.",
                    (2, 3): "Actualización quirúrgica compa, avísale a Turing que ya tienes el laboratorio en el bolsillo.",
                    (2, 4): "Listo el borrado compa, anda a registrar la firma con el profe Turing.",
                    (2, 5): "Uf qué alivio compa, dos años adentro y todavía conservamos la cordura.",
                    (3, 1): "Excelente cálculo compa, el COUNT y el AVG te salieron a la primera, avísale a Turing.",
                    (3, 2): "Buena agrupación compa, vamos a reportarle al profe para cerrar la jornada.",
                    (3, 3): "Sacaste el HAVING compa, eres una máquina, anda a mostrarle al profe.",
                    (3, 4): "Tablas cruzadas sin errores compa, ya tenemos nivel de ingeniero de verdad.",
                    (3, 5): "Aprobado compa, aunque te confieso que el próximo año congelo para avanzar con calma en el proyecto de título."
                },
                dropout_note="Post-it de Matías: 'Llegó hasta 4to año pero congeló para terminar el proyecto de título con calma el próximo semestre...'"
            ),

            # 4. Valentina (Mesa 3, PC 1). Años 1 y 2.
            Classmate(
                "valentina", "Valentina", 70, 190, 12, min_year=1, max_year=2,
                skin_color=(245, 200, 160), hair_color=(120, 50, 30), shirt_color=(140, 70, 180),
                dialogues_before={
                    (1, 1): "Hola Alex, me encanta el diseño de esta terminal aunque le hace falta una paleta de colores pastel para que no fatigue la vista.",
                    (1, 2): "La precisión en el filtrado es como la armonía en una interfaz gráfica, si dejas datos de más se rompe toda la experiencia.",
                    (1, 3): "Estuve revisando la lista de materias y sus créditos, visualmente se ve mucho mejor cuando todo está ordenado de mayor a menor.",
                    (1, 4): "Tener un podio de tres lugares es el clásico diseño de leaderboard que ocupan todas las aplicaciones modernas.",
                    (1, 5): "Mucho éxito en el examen parcial, Alex, recuerda que un buen ingeniero no solo programa bien sino que entrega todo prolijo.",
                    (2, 1): "Las tablas bien diseñadas son como los sistemas de diseño en Figma, cada campo tiene su propósito y su tipo armónico.",
                    (2, 2): "Al poblar la tabla me aseguro de que los datos tengan coherencia visual y no parezcan texto de relleno.",
                    (2, 3): "Actualizar registros con WHERE asegura que no rompamos la consistencia de la interfaz de usuario.",
                    (2, 4): "Borrar tuplas requiere precisión milimétrica, como quitar capas innecesarias en un prototipo.",
                    (2, 5): "Segundo examen de año, Alex, aunque creo que el próximo año me cambiaré a Diseño UX porque el código puro me agota bastante."
                },
                dialogues_after={
                    (1, 1): "Se ve súper elegante tu salida de datos, Alex, anda a mostrarle al profesor Turing para que anote tu avance.",
                    (1, 2): "Filtrado perfecto y ordenado, Alex, pasa a despedirte de Turing antes de que empiece a apagar las luces del aula.",
                    (1, 3): "Impecable presentación de resultados, Alex, habla con el profesor para dar por concluida la sesión de hoy.",
                    (1, 4): "Genial, terminamos todas las prácticas previas al viernes, a guardar energía para el examen de mañana.",
                    (1, 5): "Qué gran examen dimos, Alex, vamos con el profesor a escuchar las notas de la semana.",
                    (2, 1): "Qué hermosa tabla creaste, Alex, habla con Turing para sellar el laboratorio de hoy.",
                    (2, 2): "Datos cargados con perfecta armonía, anda a registrar la asistencia con el profesor.",
                    (2, 3): "Modificación impecable, Alex, te felicito por la prolijidad de tu consulta.",
                    (2, 4): "Base de datos limpia y ordenada, pasa con Turing a cerrar la jornada.",
                    (2, 5): "Lo aprobamos, Alex, qué linda experiencia compartir estos dos años de código contigo."
                },
                dropout_note="Nota de Valentina: 'Se cambió a Diseño UX/UI en 3er año, dijo que el álgebra relacional no era lo suyo...'"
            ),

            # 5. Lucas (Mesa 3, PC 2). Solo Año 1.
            Classmate(
                "lucas", "Lucas", 70, 190, 48, min_year=1, max_year=1,
                skin_color=(255, 210, 160), hair_color=(210, 180, 70), shirt_color=(210, 130, 40),
                dialogues_before={
                    (1, 1): "Buena compa, ojalá terminemos rápido este SELECT porque a las siete abro Steam para jugar unas partidas con los chiquillos.",
                    (1, 2): "Hermano, el profesor Turing no perdona nada con el WHERE, como le pifie a una comilla me quedo sin recreo.",
                    (1, 3): "El ORDER BY DESC me confunde entero compa, prefiero ordenar el inventario de mis juegos que ordenar las tablas de la facultad.",
                    (1, 4): "Dicen que mañana viernes el examen va a estar brígido, yo le voy a rezar a Gaben y a San Turing para sacarme un cuatro pelado.",
                    (1, 5): "Tengo los dedos cruzados compa, si repruebo este viernes mi mamá me quita el computador gamer hasta segundo semestre."
                },
                dialogues_after={
                    (1, 1): "Wena, ya lo sacaste, yo sigo acá peleando con el punto y coma pero al menos ya casi cierro para irme a jugar.",
                    (1, 2): "Menos mal saliste victorioso compa, anda a registrar la firma con Turing y vámonos a comprar una empanada al casino.",
                    (1, 3): "Buena máquina, te quedó impecable el ranking, ojalá mis notas subieran tan rápido como las tuyas.",
                    (1, 4): "Terminaste los ejercicios compa, ahora sí que no hay vuelta atrás, mañana nos vemos las caras con el examen parcial.",
                    (1, 5): "Uf se acabó la tortura compa, no quiero ver una consulta SQL hasta el lunes, me voy directo al Discord."
                },
                dropout_note="Sticker de Lucas: 'Se cambió a Ingeniería Comercial tras reprobar el ramo con nota 2.8...'"
            ),

            # 6. Camila (Mesa 4, PC 1). Solo Año 1.
            Classmate(
                "camila", "Camila", 330, 190, 12, min_year=1, max_year=1,
                skin_color=(240, 190, 150), hair_color=(40, 30, 20), shirt_color=(40, 160, 150),
                dialogues_before={
                    (1, 1): "Hola, traje marcadores de colores para resumir la cátedra de Turing, si quieres te presto mis apuntes en el recreo.",
                    (1, 2): "Tengo anotado que en SQLite el texto no distingue mayúsculas en algunos cotejamientos, pero es mejor escribir los nombres idénticos.",
                    (1, 3): "Hice una ficha de estudio comparando ASC y DESC, el ordenamiento ascendente viene por defecto así que no es obligatorio escribirlo.",
                    (1, 4): "Repasé tres veces el orden de las cláusulas: primero SELECT, luego FROM, WHERE, ORDER BY y finalmente LIMIT.",
                    (1, 5): "Éxito a todos, confiemos en el estudio y en la constancia de toda esta primera semana."
                },
                dialogues_after={
                    (1, 1): "Completaste el ejercicio muy rápido, no olvides presionar la tecla F1 o N para ver cómo se actualiza tu cuaderno con las notas de hoy.",
                    (1, 2): "Muy buen resultado, anda con el profesor Turing para que te valide la asistencia del Día dos.",
                    (1, 3): "Excelente ejercicio, tienes todo listo para el laboratorio de paginación de mañana.",
                    (1, 4): "Perfecto, Alex, mañana es el examen parcial, duerme bien para rendir al cien por ciento.",
                    (1, 5): "Prueba terminada, a esperar que el sistema procese nuestras respuestas con calma."
                },
                dropout_note="Nota de Camila: 'Se transfirió de sede universitaria a Viña del Mar por motivos familiares...'"
            ),

            # 7. Diego (Mesa 4, PC 2). Solo Año 1.
            Classmate(
                "diego", "Diego", 330, 190, 48, min_year=1, max_year=1,
                skin_color=(250, 205, 155), hair_color=(70, 50, 40), shirt_color=(160, 50, 50),
                dialogues_before={
                    (1, 1): "Buenas compa, anoche soñé que ponía una coma de más y el servidor de la universidad explotaba en llamas.",
                    (1, 2): "Ojalá no me toque una consulta con condiciones raras, con el puro WHERE ya siento la presión de los cuatro créditos del ramo.",
                    (1, 3): "Leí las estadísticas de deserción de informática y casi me desmayo, tengo que sacarme puros sietes para asegurar la beca.",
                    (1, 4): "Mañana es viernes y el cuerpo lo sabe, pero el cerebro sabe que hay examen con Turing y no me deja estar en paz.",
                    (1, 5): "Tengo el corazón en la garganta compa, que no nos pregunten nada que no hayamos visto en la pizarra por favor."
                },
                dialogues_after={
                    (1, 1): "Qué alivio verte terminar tan tranquilo, yo sigo transpirando helado frente a mi pantalla, anda a marcar con Turing.",
                    (1, 2): "Bien hecho compa, saliste ileso del filtrado, anda a avisarle al profe antes de que se arrepienta de darnos la hora libre.",
                    (1, 3): "Terminaste compa, qué envidia de la sana, yo todavía estoy rezando para que mi consulta no se quede pegada.",
                    (1, 4): "Prácticas listas compa, si sobrevivimos mañana juro que el fin de semana duermo veinticuatro horas seguidas.",
                    (1, 5): "Ya está hecho compa, que sea lo que Dios y el algoritmo de corrección quieran."
                },
                dropout_note="Post-it de Diego: 'Se tomó un año sabático para replantearse su vocación profesional...'"
            )
        ]

    def check_interaction(self, player_rect, curriculum):
        # 1. PC del jugador
        if player_rect.colliderect(self.pc_zone):
            if curriculum.current_day == 5:
                return "pc", f"Pulsa [E] para rendir el EXAMEN DE AÑO {curriculum.current_year} en tu terminal", None
            status = " [✓ Completado]" if curriculum.day_task_completed else " [Pendiente]"
            return "pc", f"Pulsa [E] para abrir tu Terminal SQL (Año {curriculum.current_year}, Día {curriculum.current_day}){status}", None

        # 2. Profesor Turing
        elif player_rect.colliderect(self.prof_zone):
            if not curriculum.lecture_done_for_day:
                return "prof", "Pulsa [E] para atender la Clase del Profesor Turing", None
            elif curriculum.day_task_completed and curriculum.current_day < 5:
                return "prof", "Pulsa [E] para despedirte del Profesor Turing y pasar al siguiente día", None
            elif curriculum.exam_finished:
                return "prof", "Pulsa [E] para recibir tu Calificación Final con Turing", None
            else:
                return "prof", "Pulsa [E] para pedir ayuda o pistas al Profesor Turing", None

        # 3. Biblioteca / Apuntes
        elif player_rect.colliderect(self.book_zone):
            return "book", "Pulsa [E] para consultar la Biblioteca o pulsa [N] para tus Apuntes", None

        # 4. Compañeros de clase o puestos vacíos
        cur_y = curriculum.current_year
        for cm in self.classmates:
            if player_rect.colliderect(cm.zone):
                if cm.is_present(cur_y):
                    return "classmate", f"Pulsa [E] para hablar con {cm.name}", cm
                else:
                    return "empty_desk", f"Pulsa [E] para leer la nota en el puesto de {cm.name}", cm

        return None, None, None

    def draw(self, surface, tick, curriculum, save_system):
        # 1. Fondo del aula estático pre-renderizado (Optimizado para CPU/GPU)
        surface.blit(self.bg_surface, (0, 0))

        # 2. Pizarra Verde Gigante (Contenido dinámico)
        board_col = (45, 20, 25) if curriculum.current_day == 5 else COLOR_BOARD
        pygame.draw.rect(surface, board_col, (148, 13, 184, 36))
        
        if curriculum.current_day == 5:
            if curriculum.current_year == 4:
                chalk_surf = self.font_tiny.render("¡DEFENSA DE TÍTULO DE GRADO!", True, (255, 200, 100))
            else:
                chalk_surf = self.font_tiny.render(f"EXAMEN FINAL - AÑO {curriculum.current_year} DE 4", True, (255, 180, 180))
            surface.blit(chalk_surf, (155, 18))
            att = curriculum.get_year_attempts()
            sub_txt = f"Aciertos: {curriculum.exam_score}/3  |  Intento #{att}"
            chalk_sub = self.font_tiny.render(sub_txt, True, COLOR_AMBER)
            surface.blit(chalk_sub, (155, 32))
        else:
            chalk_surf = self.font_tiny.render(f"Ingeniería Informática  |  AÑO {curriculum.current_year} (DÍA {curriculum.current_day}/5)", True, COLOR_CHALK_TEXT)
            surface.blit(chalk_surf, (155, 18))
            task = curriculum.get_current_task()
            sub_txt = task.title if task else "SELECT * FROM futuro;"
            chalk_sub = self.font_tiny.render(sub_txt[:34], True, (160, 210, 160))
            surface.blit(chalk_sub, (155, 32))

        # 3. Sprite dinámico del Profesor Turing
        prof_x, prof_y = 230, 50
        pygame.draw.rect(surface, (220, 220, 225), (prof_x + 3, prof_y - 2, 10, 6))
        pygame.draw.rect(surface, (255, 205, 148), (prof_x + 4, prof_y + 2, 8, 6))
        pygame.draw.rect(surface, (30, 30, 30), (prof_x + 5, prof_y + 4, 2, 2))
        pygame.draw.rect(surface, (30, 30, 30), (prof_x + 9, prof_y + 4, 2, 2))
        pygame.draw.line(surface, (30, 30, 30), (prof_x + 6, prof_y + 5), (prof_x + 8, prof_y + 5), 1)
        pygame.draw.rect(surface, (65, 85, 60), (prof_x + 3, prof_y + 8, 10, 8))
        pygame.draw.rect(surface, (240, 240, 245), (prof_x + 7, prof_y + 8, 2, 4))

        # Indicador animado sobre el profesor
        if not curriculum.lecture_done_for_day or (curriculum.day_task_completed and curriculum.current_day < 5):
            pulse = int(4 * math.sin(tick * 0.2))
            badge_color = (0, 255, 136) if curriculum.day_task_completed else COLOR_AMBER
            pygame.draw.circle(surface, badge_color, (prof_x + 8, prof_y - 10 + pulse), 6)
            symbol = "✓" if curriculum.day_task_completed else "!"
            p_excl = self.font_tiny.render(symbol, True, COLOR_BLACK)
            surface.blit(p_excl, (prof_x + 5, prof_y - 14 + pulse))

        # 4. Monitores interactivos y personajes sentados
        desks = [
            (70, 120, True),
            (330, 120, False),
            (70, 190, False),
            (330, 190, False)
        ]

        pname = save_system.data.get("player_name", "Novato")
        cur_year = curriculum.current_year

        # Mapear compañeros por coordenadas de PC
        cm_map = {(cm.desk_x, cm.pc_offset): cm for cm in self.classmates}

        for dx, dy, is_player_desk in desks:
            for pc_offset in [12, 48]:
                px = dx + pc_offset
                py = dy + 3

                # PC del jugador (Mesa 1, offset 12)
                if is_player_desk and pc_offset == 12:
                    pulse = int(180 + 40 * math.sin(tick * 0.1))
                    glow_color = (220, 60, 60) if curriculum.current_day == 5 else (20, pulse, 100)
                    pygame.draw.rect(surface, glow_color, (px + 2, py + 2, 16, 12))
                    pygame.draw.line(surface, (255, 255, 255), (px + 4, py + 5), (px + 12, py + 5), 1)
                    pygame.draw.line(surface, (255, 255, 255), (px + 4, py + 8), (px + 10, py + 8), 1)

                    arrow_y = int(py - 12 + 3 * math.sin(tick * 0.15))
                    pygame.draw.polygon(surface, COLOR_AMBER, [
                        (px + 10, arrow_y + 6),
                        (px + 6, arrow_y),
                        (px + 14, arrow_y)
                    ])

                    # Placa identificadora con el nombre del jugador
                    plate_w = 42
                    plate_rect = pygame.Rect(dx + 2, dy + 22, plate_w, 8)
                    pygame.draw.rect(surface, (30, 40, 60), plate_rect)
                    pygame.draw.rect(surface, COLOR_AMBER, plate_rect, 1)
                    name_tag = self.font_name_tag.render(pname[:8], True, (255, 255, 255))
                    surface.blit(name_tag, (plate_rect.x + 2, plate_rect.y))
                else:
                    # PC de compañero
                    cm = cm_map.get((dx, pc_offset))
                    if cm and cm.is_present(cur_year):
                        # PC Encendida del compañero
                        pygame.draw.rect(surface, (15, 35, 60), (px + 2, py + 2, 16, 12))
                        pygame.draw.line(surface, (0, 229, 255), (px + 4, py + 5), (px + 14, py + 5), 1)
                        pygame.draw.line(surface, (0, 255, 136), (px + 4, py + 8), (px + 11, py + 8), 1)

                        # Sprite del Alumno sentado de espaldas / semi-perfil trabajando
                        bob = int(math.sin(tick * 0.08 + px) * 1)
                        # Silla
                        pygame.draw.rect(surface, (40, 45, 55), (px + 4, py + 20, 12, 10))
                        # Torso (camisa)
                        pygame.draw.rect(surface, cm.shirt_color, (px + 4, py + 16 + bob, 12, 9))
                        # Cuello y cabeza
                        pygame.draw.rect(surface, cm.skin_color, (px + 6, py + 9 + bob, 8, 8))
                        # Cabello
                        pygame.draw.rect(surface, cm.hair_color, (px + 5, py + 7 + bob, 10, 5))
                    else:
                        # Computador apagado o con post-it de deserción
                        pygame.draw.rect(surface, COLOR_PC_SCREEN_OFF, (px + 2, py + 2, 16, 12))
                        pygame.draw.line(surface, (45, 55, 65), (px + 4, py + 5), (px + 14, py + 5), 1)
                        # Silla vacía
                        pygame.draw.rect(surface, (40, 45, 55), (px + 4, py + 20, 12, 10))
                        
                        # Post-it amarillo en la pantalla si el alumno desertó
                        if cm:
                            pygame.draw.rect(surface, (255, 230, 80), (px + 10, py + 3, 6, 6))
                            pygame.draw.rect(surface, (200, 40, 40), (px + 12, py + 2, 2, 2))
