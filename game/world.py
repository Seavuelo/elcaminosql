from game.visuals import backdrop, desk, window, plant, board, monitor_details, marco_sprite, teacher_notice, chair, netbook
import pygame
from game.rendering import draw, make_font
import math
from game.constants import *
from game.player import Player
from game.peer_dialogues import PEER_DIALOGUES

class Classmate:
    def __init__(self, id_name, name, desk_x, desk_y, pc_offset, min_year, max_year,
                 skin_color, hair_color, shirt_color, dialogues_before, dialogues_after, dropout_note,
                 eye_color=(65, 50, 30), pants_color=(40, 50, 75), shoe_color=(30, 25, 20),
                 glasses=False, hoodie=False, hair_style=None):
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
        self.eye_color = eye_color
        self.pants_color = pants_color
        self.shoe_color = shoe_color
        self.glasses = glasses
        self.hoodie = hoodie
        self.hair_style = hair_style if hair_style is not None else {
            "carlos": 2, "sofia": 1, "matias": 4, "valentina": 1,
            "lucas": 0, "camila": 1, "diego": 3,
        }.get(id_name, 0)
        self._build_walking_sprites()
        self.reset_day()
        # Zona interactiva alrededor de la silla (al sur de la mesa)
        self.zone = pygame.Rect(self.px - 6, self.py + 18, 32, 26)

    def _build_walking_sprites(self):
        player = Player(0, 0, {"hair_style": self.hair_style,
                               "clothing_style": 1 if self.hoodie else 0})
        palette = {
            (255, 205, 148): self.skin_color,
            (204, 164, 118): tuple(int(c * 0.8) for c in self.skin_color),
            (80, 45, 25): self.hair_color,
            (30, 144, 255): self.shirt_color,
            (18, 86, 153): tuple(int(c * 0.6) for c in self.shirt_color),
            (40, 50, 75): self.pants_color,
            (30, 25, 20): self.shoe_color,
            (55, 35, 25): self.eye_color,
            (220, 90, 40): tuple(int(c * 0.75) for c in self.shirt_color),
        }
        for base,target in list(palette.items()):
            if base==(80,45,25):palette[tuple(min(255,int(v*1.15)+8) for v in base)]=tuple(min(255,int(v*1.15)+8) for v in target)
            if base==(30,144,255):palette[tuple(min(255,int(v*1.12)+5) for v in base)]=tuple(min(255,int(v*1.12)+5) for v in target)
            if base==(40,50,75):palette[tuple(int(v*.65) for v in base)]=tuple(int(v*.65) for v in target)
        self.sprites = player.sprites
        for direction, frames in self.sprites.items():
            for sprite in frames:
                for x in range(sprite.get_width()):
                    for y in range(sprite.get_height()):
                        color = sprite.get_at((x, y))
                        if color.a and tuple(color[:3]) in palette:
                            sprite.set_at((x, y), palette[tuple(color[:3])])
                if self.glasses and direction != "up":
                    self.draw_glasses(sprite, 0, 0, direction)

    @staticmethod
    def draw_glasses(surface, x, y, direction="down"):
        color = (50, 40, 30)
        if direction == "down":
            draw.rect(surface, color, (x + 4, y + 5, 4, 4), 1)
            draw.rect(surface, color, (x + 8, y + 5, 4, 4), 1)
            draw.line(surface, color, (x + 7, y + 6), (x + 8, y + 6))
        else:
            eye_x = 3 if direction == "left" else 9
            draw.rect(surface, color, (x + eye_x, y + 5, 4, 4), 1)

    def reset_day(self):
        self.state = "studying"
        self.elapsed = 0.0
        self.x, self.y = float(self.px + 4), float(self.desk_y + 30)
        self.direction = "down"
        self.walk_time = 0.0
        self.route = []
        self.departure_speech = None

    @property
    def pc_on(self):
        return self.state in ("studying", "packing")

    @property
    def interaction_zone(self):
        if self.state in ("walking", "exiting"):
            return pygame.Rect(round(self.x) - 8, round(self.y) - 8, 32, 36)
        return self.zone

    def start_departure(self, speech):
        if self.state != "studying":
            return
        self.state = "packing"
        self.elapsed = 0.0
        self.departure_speech = speech
        aisle_x = self.desk_x - 24 if self.pc_offset == 12 else self.desk_x + 88
        self.route = [(self.x, self.desk_y + 38), (aisle_x, self.desk_y + 38),
                      (aisle_x, 98), (24, 98), (24, 58)]

    def update(self, dt):
        self.elapsed += dt
        if self.state == "packing" and self.elapsed >= 1.4:
            self.state, self.elapsed = "shutdown", 0.0
        elif self.state == "shutdown" and self.elapsed >= 0.6:
            self.state, self.elapsed = "standing", 0.0
        elif self.state == "standing" and self.elapsed >= 0.5:
            self.state, self.elapsed = "walking", 0.0
        elif self.state == "walking":
            self.walk_time += dt
            budget = 32 * dt
            while self.route and budget > 0:
                tx, ty = self.route[0]
                dx, dy = tx - self.x, ty - self.y
                distance = math.hypot(dx, dy)
                if distance == 0:
                    self.route.pop(0)
                    continue
                self.direction = ("right" if dx > 0 else "left") if dx else ("down" if dy > 0 else "up")
                step = min(budget, distance)
                self.x += dx / distance * step
                self.y += dy / distance * step
                budget -= step
                if step == distance:
                    self.route.pop(0)
            if not self.route:
                self.state, self.elapsed = "exiting", 0.0
        elif self.state == "exiting" and self.elapsed >= 0.5:
            self.state = "gone"

    def draw_walking(self, surface):
        if self.state not in ("standing", "walking", "exiting"):
            return
        frame = int(self.walk_time * 7) % 4 if self.state == "walking" else 0
        sprite = self.sprites[self.direction][frame]
        if self.state == "exiting":
            sprite = sprite.copy()
            sprite.set_alpha(max(0, round(255 * (1 - self.elapsed / 0.5))))
        draw_y = self.y
        if self.state == "standing":
            seated_y = self.py + 9
            draw_y = seated_y + (self.y - seated_y) * min(1, self.elapsed / 0.5)
        surface.blit(sprite, (round(self.x), round(draw_y)))

    def is_present(self, year):
        return self.min_year <= year <= self.max_year

    def get_speech(self, year, day, day_completed):
        if self.departure_speech is not None:
            return self.departure_speech
        pool = self.dialogues_after if day_completed else self.dialogues_before
        if (year, day) in pool:
            return pool[(year, day)]
        if year in pool:
            return pool[year]
        return pool.get("default", "Hola compañero, acá dándole duro al laboratorio de SQL.")


class World:
    def __init__(self):
        self.desks = [(70, 120), (330, 120), (70, 190), (200, 190), (330, 190)]
        self.day_key = None
        self.colliders = []
        self._build_classroom()
        self._build_classmates()
        self.font_tiny = make_font(12)
        self.font_name_tag = make_font(10)
        self._build_static_background()

    def _build_static_background(self):
        self.bg_surface = pygame.Surface((VIRTUAL_WIDTH,VIRTUAL_HEIGHT))
        art=self.bg_surface
        backdrop(art)
        draw.rect(art,(46,59,62),(16,58,448,226))
        for y in range(58,284,16):
            for x in range(16,464,24):
                color=(59,69,73) if (x//24+y//16)%2 else (62,72,75)
                draw.rect(art,color,(x,y,min(23,464-x),min(15,284-y)))
                draw.line(art,(69,79,80),(x+1,y+1),(min(x+21,463),y+1))
        draw.rect(art,(88,98,95),(16,0,448,58))
        draw.rect(art,(45,64,65),(16,54,448,4))
        draw.line(art,(169,154,118),(16,54),(463,54))
        for wx in (67,357):
            window(art,(wx,14,43,31))
            draw.polygon(art,(70,84,82),[(wx,59),(wx+40,59),(wx+70,109),(wx+20,109)])
        draw.rect(art,(120,87,58),(20,18,25,40))
        draw.rect(art,(76,63,50),(23,21,19,35))
        draw.line(art,(155,119,77),(24,22),(40,22))
        draw.circle(art,(225,185,111),(39,40),2)
        board(art,(145,10,190,42))
        plant(art,23,72);plant(art,440,245)
        # Reloj y panel de anuncios, fuera de las zonas de paso
        draw.circle(art,(52,68,69),(128,25),10)
        draw.circle(art,(224,218,188),(128,25),8)
        draw.line(art,(65,81,78),(128,25),(128,19))
        draw.line(art,(65,81,78),(128,25),(132,27))
        draw.rect(art,(103,76,54),(411,5,42,31))
        draw.rect(art,(155,126,83),(413,7,38,27))
        for i in range(3):
            draw.rect(art,(226,220,190),(416+i*11,11+i%2*3,8,14))
            draw.line(art,(120,145,137),(418+i*11,15+i%2*3),(421+i*11,15+i%2*3))
        bx,by,bw,bh=410,45,45,40
        draw.rect(art,(73,57,45),(bx,by,bw,bh))
        for shelf_y in (by+6,by+23):
            for i in range(6):
                xx=bx+3+i*6;hh=10+i%3
                color=[(173,101,77),(79,129,137),(202,169,99),(90,143,104),(132,108,142),(192,145,105)][i]
                draw.rect(art,color,(xx,shelf_y+13-hh,5,hh))
                draw.line(art,(221,204,164),(xx+1,shelf_y+5),(xx+3,shelf_y+5))
            draw.line(art,(153,115,75),(bx+1,shelf_y+14),(bx+bw-2,shelf_y+14),2)
        desk(art,(210,65,60,25))
        draw.rect(art,(232,224,196),(217,68,13,10))
        draw.line(art,(134,154,144),(219,71),(226,71))
        draw.rect(art,(45,65,75),(241,67,17,12))
        netbook(art,243,63)
        draw.rect(art,(197,173,119),(261,68,5,6))
        for dx,dy in self.desks:
            desk(art,(dx,dy,80,28))
            for pc_offset in (12,48):
                px,py=dx+pc_offset,dy+3
                draw.rect(art,(54,68,75),(px+3,py+18,14,13),border_radius=2)
                draw.line(art,(84,104,107),(px+4,py+19),(px+15,py+19))
                draw.rect(art,(174,185,182),(px,py,20,16),border_radius=1)
                draw.rect(art,(102,121,125),(px+6,py+16,8,4))
                draw.rect(art,(177,186,177),(px+4,py+19,12,2))
                draw.rect(art,(154,168,165),(px+2,py+21,16,4))
                monitor_details(art,(px,py,20,16))
            draw.rect(art,(224,218,188),(dx+34,dy+5,8,11))
            draw.line(art,(139,159,142),(dx+35,dy+7),(dx+40,dy+7))

    def _build_classroom(self):
        self.colliders = []
        
        # Paredes del aula
        self.colliders.append(pygame.Rect(0, 0, 480, 58))
        self.colliders.append(pygame.Rect(0, 0, 16, 300))
        self.colliders.append(pygame.Rect(464, 0, 16, 300))
        self.colliders.append(pygame.Rect(0, 284, 480, 16))

        # Escritorio del profesor
        self.colliders.append(pygame.Rect(210, 65, 60, 25))
        self.colliders.append(pygame.Rect(230,48,17,24))
        # Estantería de libros
        self.colliders.append(pygame.Rect(410, 55, 45, 30))

        # Mesas de computadores
        self.colliders.extend(pygame.Rect(x, y, 80, 30) for x, y in self.desks)

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
                    (1, 1): "Hola compañer@, me llamo Carlos. Estoy hasta con calzoncillos largos porque el aire acondicionado de esta sala me congela entero. Ojalá la clase dure poco.",
                    (1, 2): "¿Entendiste bien lo de WHERE? Igual no soy el mejor para las matemáticas, me confundo entre el mayor y menor con ese signo de Pac-Man. Espero entender...",
                    (1, 3): "Siento que me estoy quedando atrás. A Sofía le tomó cinco segundos hacer el ORDER BY; yo sigo sin entender qué poner ahí, columnas, tablas... ¿Tú realmente lo entiendes?",
                    (1, 4): "Con LIMIT 3 dejamos a solo los mejores tres de la facultad. ¿Así se harán los rankings de juegos y cosas así? Como que lo voy entendiendo todo... Lo entendí todo.",
                    (1, 5): "Llegó el viernes del juicio, herman@. Lee bien y muchas veces lo que piden, eso nos aconsejó el profesor. Espero que nos vaya bien o nos vemos de vuelta al inicio del curso.",
                    (2, 1): "Sobrevivimos al primer año. Mira, la sala quedó con algunos asientos vacíos... Ahora nos toca modelar datos desde cero, crear las tablas. Me voy a volver LOCO.",
                    (2, 2): "Cuidado con los tipos de datos al hacer el INSERT, si metes un texto donde va un número el PC explota.",
                    (2, 3): "El profe advirtió tres veces no tirar un UPDATE sin WHERE, casi actualizo el sueldo de toda la universidad compa.",
                    (2, 4): "Otro día más de clases, se acerca el examen, tengo miedo... Ya, que hay que hacer los ejercicios.",
                    (2, 5): 'Anoche dije "una partida mas y estudio"... ya, no te voy a mentir, fueron como cinco, ¿alcanzamos a repasar algo antes de empezar?'
                },
                dialogues_after={
                    (1, 1): "Qué rápido, compa. Lo entendiste de una. ¿Vas a irte o te quedarás practicando?",
                    (1, 2): "Oye, tus filtros funcionaron. ¿Me enseñas otro día? Yo sigo estancado, o mándame el código por Discord después, jeje. Si te vas a ir, habla con el profe para que te dejen presente.",
                    (1, 3): "Lo entendí al final. Igual siempre es bueno practicar. ¿Te quedarás un rato más o te vas para la casa? Ya quiero jugarme un lolsito...",
                    (1, 4): "No entendí nada, pero ya practicaré en la casa. Aunque igual es fácil el LIMIT... creo. Mañana es el examen, estudia harto, dicen que está fea la cosa. Te tengo fe, amigo.",
                    (1, 5): "Ya terminó todo... Se siente el relajo. Ahora a esperar que el profe este feo nos dé la nota, siento que nos tiene mala...",
                    (2, 1): "Igual no fue tan difícil, creo que es cosa de practicar. Viva Dios.",
                    (2, 2): "Poblaste la base de datos... Eres Dios. Cada vez estamos más cerca del nivel senior, ¿o no? No entiendo, ¿siquiera somos junior? ¿Un píxel de junior? Ya mejor vámonos para la casa...",
                    (2, 3): "Ok, no UPDATE sin WHERE, hay que acordarse de eso. Vi un meme de alguien que no hizo eso y dejó la media cagaita. Después te mando el tistos.",
                    (2, 4): "Limpiamos PRIME los datos, somos god, prime, prima, dios, dioses... Perdón, caí en la locura... Mejor me voy para la casa...",
                    (2, 5): "Ya entregué, había una que la cambié como tres veces y al final dejé la primera... no me digas si estaba mala todavía"
                },
                dropout_note="Nota pegada de Carlos: 'Encontró trabajo como soporte técnico y no le dieron permiso laboral para los horarios de 3er año...'"
            ),

            # 2. Sofia (Mesa 2, PC 1). ¡Está presente los 4 años completos!
            Classmate(
                "sofia", "Sofía", 330, 120, 12, min_year=1, max_year=4,
                skin_color=(255, 215, 175), hair_color=(180, 120, 40), shirt_color=(190, 60, 90),
                dialogues_before=PEER_DIALOGUES["sofia"]["before"],
                dialogues_after=PEER_DIALOGUES["sofia"]["after"],
                dropout_note=""
            ),

            # 3. Matias (Mesa 2, PC 2). Años 1, 2 y 3.
            Classmate(
                "matias", "Matías", 330, 120, 48, min_year=1, max_year=3,
                skin_color=(230, 180, 130), hair_color=(30, 30, 35), shirt_color=(50, 150, 80),
                dialogues_before=PEER_DIALOGUES["matias"]["before"],
                dialogues_after=PEER_DIALOGUES["matias"]["after"],
                dropout_note="Post-it de Matías: 'Llegó hasta 4to año pero congeló para terminar el proyecto de título con calma el próximo semestre...'"
            ),

            # 4. Valentina (Mesa 3, PC 1). Años 1 y 2.
            Classmate(
                "valentina", "Valentina", 70, 190, 12, min_year=1, max_year=2,
                skin_color=(245, 200, 160), hair_color=(120, 50, 30), shirt_color=(140, 70, 180),
                dialogues_before=PEER_DIALOGUES["valentina"]["before"],
                dialogues_after=PEER_DIALOGUES["valentina"]["after"],
                dropout_note="Nota de Valentina: 'Se cambió a Diseño UX/UI en 3er año, dijo que el álgebra relacional no era lo suyo...'"
            ),

            # 5. Lucas (Mesa 3, PC 2). Solo Año 1.
            Classmate(
                "lucas", "Lucas", 70, 190, 48, min_year=1, max_year=1,
                skin_color=(255, 210, 160), hair_color=(210, 180, 70), shirt_color=(210, 130, 40),
                dialogues_before=PEER_DIALOGUES["lucas"]["before"],
                dialogues_after=PEER_DIALOGUES["lucas"]["after"],
                dropout_note="Sticker de Lucas: 'Se cambió a Ingeniería Comercial tras reprobar el ramo con nota 2.8...'"
            ),

            # 6. Camila (Mesa 4, PC 1). Solo Año 1.
            Classmate(
                "camila", "Camila", 330, 190, 12, min_year=1, max_year=1,
                skin_color=(240, 190, 150), hair_color=(40, 30, 20), shirt_color=(40, 160, 150),
                dialogues_before=PEER_DIALOGUES["camila"]["before"],
                dialogues_after=PEER_DIALOGUES["camila"]["after"],
                dropout_note="Nota de Camila: 'Se transfirió de sede universitaria a Viña del Mar por motivos familiares...'"
            ),

            # 7. Diego (Mesa 4, PC 2). Solo Año 1.
            Classmate(
                "diego", "Diego", 330, 190, 48, min_year=1, max_year=1,
                skin_color=(250, 205, 155), hair_color=(70, 50, 40), shirt_color=(160, 50, 50),
                dialogues_before=PEER_DIALOGUES["diego"]["before"],
                dialogues_after=PEER_DIALOGUES["diego"]["after"],
                dropout_note="Post-it de Diego: 'Se tomó un año sabático para replantearse su vocación profesional...'"
            )
        ]
        from game.moshi import create_moshi
        self.classmates.append(create_moshi(Classmate))

    def sync_day(self, curriculum):
        key = (curriculum.current_year, curriculum.current_day, curriculum.get_year_attempts())
        if key != self.day_key:
            self.day_key = key
            for cm in self.classmates:
                cm.reset_day()

    def update(self, dt, curriculum, paused=False):
        self.sync_day(curriculum)
        if not paused:
            for cm in self.classmates:
                if cm.is_present(curriculum.current_year):
                    cm.update(dt)

    def finish_conversation(self, cm, curriculum):
        self.sync_day(curriculum)
        if curriculum.day_task_completed or (curriculum.current_day == 5 and curriculum.exam_finished):
            speech = cm.get_speech(curriculum.current_year, curriculum.current_day, True)
            cm.start_departure(speech)

    def check_interaction(self, player_rect, curriculum):
        self.sync_day(curriculum)
        # Priorizar a los compañeros que caminan, incluso frente a otra zona interactiva
        for cm in self.classmates:
            if (cm.is_present(curriculum.current_year) and cm.state in ("walking", "exiting")
                    and player_rect.colliderect(cm.interaction_zone)):
                return "classmate", f"Pulsa [E] para hablar con {cm.name}", cm
        # 1. PC del jugador
        if player_rect.colliderect(self.pc_zone):
            if curriculum.current_day == 5:
                return "pc", f"Pulsa [E] para rendir el EXAMEN DE AÑO {curriculum.current_year} en tu terminal", None
            status = " [✓ Completado]" if curriculum.day_task_completed else " [Pendiente]"
            return "pc", f"Pulsa [E] para abrir tu Terminal SQL (Año {curriculum.current_year}, Día {curriculum.current_day}){status}", None

        # 2. Profesor Marco
        elif player_rect.colliderect(self.prof_zone):
            if not curriculum.lecture_done_for_day:
                return "prof", "Pulsa [E] para atender la Clase del Profesor Marco", None
            elif curriculum.day_task_completed and curriculum.current_day < 5:
                return "prof", "Pulsa [E] para despedirte del Profesor Marco y pasar al siguiente día", None
            elif curriculum.exam_finished:
                return "prof", "Pulsa [E] para recibir tu Calificación Final con Marco", None
            else:
                return "prof", "Pulsa [E] para pedir ayuda o pistas al Profesor Marco", None

        # 3. Biblioteca / Apuntes
        elif player_rect.colliderect(self.book_zone):
            return "book", "Pulsa [E] para consultar la Biblioteca o pulsa [N] para tus Apuntes", None

        # 4. Compañeros de clase o puestos vacíos
        cur_y = curriculum.current_year
        for cm in self.classmates:
            if player_rect.colliderect(cm.interaction_zone):
                if cm.is_present(cur_y):
                    if cm.state not in ("gone", "walking", "exiting"):
                        return "classmate", f"Pulsa [E] para hablar con {cm.name}", cm
                else:
                    return "empty_desk", f"Pulsa [E] para leer la nota en el puesto de {cm.name}", cm

        return None, None, None

    def draw(self, surface, tick, curriculum, save_system):
        # 1. Fondo del aula estático pre-renderizado (Optimizado para CPU/GPU)
        surface.blit(self.bg_surface, (0, 0))

        # 2. Pizarra Verde Gigante (Contenido dinámico)
        board_col = (45, 20, 25) if curriculum.current_day == 5 else COLOR_BOARD
        draw.rect(surface, board_col, (148, 13, 184, 36))
        
        if curriculum.current_day == 5:
            if curriculum.current_year == 4:
                chalk_surf = self.font_tiny.render("¡DEFENSA DE TÍTULO DE GRADO!", True, (255, 200, 100))
            else:
                chalk_surf = self.font_tiny.render(f"EXAMEN FINAL - AÑO {curriculum.current_year} DE 4", True, (255, 180, 180))
            surface.blit(chalk_surf, (155, 18))
            att = curriculum.get_year_attempts()
            sub_txt = f"Aciertos: {curriculum.exam_score}/{len(curriculum.get_current_exam_questions())}  |  Intento #{att}"
            chalk_sub = self.font_tiny.render(sub_txt, True, COLOR_AMBER)
            surface.blit(chalk_sub, (155, 32))
        else:
            chalk_surf = self.font_tiny.render(f"Ingeniería Informática  |  AÑO {curriculum.current_year} (DÍA {curriculum.current_day}/5)", True, COLOR_CHALK_TEXT)
            surface.blit(chalk_surf, (155, 18))
            task = curriculum.get_current_task()
            sub_txt = task.title if task else "SELECT * FROM futuro;"
            chalk_sub = self.font_tiny.render(sub_txt[:34], True, (160, 210, 160))
            surface.blit(chalk_sub, (155, 32))

        # 3. Sprite dinámico del Profesor Marco
        prof_x, prof_y = 230, 50
        marco_sprite(surface,prof_x,prof_y-2)

        # Indicador animado sobre el profesor
        ready=curriculum.day_task_completed if curriculum.current_day<5 else curriculum.exam_finished
        if not curriculum.lecture_done_for_day or ready:
            teacher_notice(surface,(prof_x+8,prof_y-10),tick,ready)

        # 4. Monitores interactivos y personajes sentados

        pname = save_system.data.get("player_name", "Novato")
        cur_year = curriculum.current_year

        # Mapear compañeros por coordenadas de PC
        cm_map = {(cm.desk_x, cm.desk_y, cm.pc_offset): cm for cm in self.classmates}

        for dx, dy in self.desks:
            is_player_desk = (dx, dy) == (70, 120)
            for pc_offset in [12, 48]:
                px = dx + pc_offset
                py = dy + 3

                chair(surface,(px+3,py+20,15,16))

                # PC del jugador (Mesa 1, offset 12)
                if is_player_desk and pc_offset == 12:
                    pulse = int(180 + 40 * math.sin(tick * 0.1))
                    glow_color = (220, 60, 60) if curriculum.current_day == 5 else (20, pulse, 100)
                    draw.rect(surface, glow_color, (px + 2, py + 2, 16, 12))
                    draw.line(surface, (255, 255, 255), (px + 4, py + 5), (px + 12, py + 5), 1)
                    draw.line(surface, (255, 255, 255), (px + 4, py + 8), (px + 10, py + 8), 1)

                    arrow_y = int(py - 12 + 3 * math.sin(tick * 0.15))
                    draw.polygon(surface, COLOR_AMBER, [
                        (px + 10, arrow_y + 6),
                        (px + 6, arrow_y),
                        (px + 14, arrow_y)
                    ])

                else:
                    # PC de compañero
                    cm = cm_map.get((dx, dy, pc_offset))
                    if cm and cm.is_present(cur_year) and cm.pc_on:
                        # PC Encendida del compañero
                        draw.rect(surface, (15, 35, 60), (px + 2, py + 2, 16, 12))
                        draw.line(surface, (0, 229, 255), (px + 4, py + 5), (px + 14, py + 5), 1)
                        draw.line(surface, (0, 255, 136), (px + 4, py + 8), (px + 11, py + 8), 1)

                    else:
                        # Computador apagado o con post-it de deserción
                        draw.rect(surface, COLOR_PC_SCREEN_OFF, (px + 2, py + 2, 16, 12))
                        draw.line(surface, (45, 55, 65), (px + 4, py + 5), (px + 14, py + 5), 1)
                        # Silla vacía
                        draw.rect(surface, (40, 45, 55), (px + 4, py + 20, 12, 10))
                        
                        # Post-it amarillo en la pantalla si el alumno desertó
                        if cm and not cm.is_present(cur_year):
                            draw.rect(surface, (255, 230, 80), (px + 10, py + 3, 6, 6))
                            draw.rect(surface, (200, 40, 40), (px + 12, py + 2, 2, 2))

                    if cm and cm.is_present(cur_year) and cm.state in ("studying", "packing", "shutdown"):
                        draw.rect(surface, (40, 45, 55), (px + 4, py + 20, 12, 10))
                        bob = int(math.sin(tick * 0.08 + px))
                        pose = "right" if cm.state in ("packing", "shutdown") else "up"
                        surface.blit(cm.sprites[pose][0], (px + 4, py + 9 + bob))
                        if cm.state == "packing":
                            reach = int(math.sin(cm.elapsed * 10) * 3)
                            draw.line(surface, cm.shirt_color, (px + 12, py + 19), (px + 17, py + 18 + reach), 2)
                            draw.rect(surface, cm.skin_color, (px + 16, py + 18 + reach, 3, 2))
                            draw.rect(surface, cm.skin_color, (px + 10, py + 22 - reach, 3, 2))
                            draw.rect(surface, (235, 220, 180), (px + 13, py + 20 - reach, 5, 4))

        for cm in sorted(self.classmates, key=lambda student: student.y):
            if cm.is_present(cur_year):
                cm.draw_walking(surface)
