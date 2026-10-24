import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.config import ConfigManager
from game.save_system import SaveSystem
from game.audio import AudioManager
from game.database import DatabaseManager
from game.curriculum import UniversityCurriculum
from game.player import Player
from game.world import World
from game.terminal import SQLTerminal
from game.dialog import DialogBox
from game.lecture import LectureScene
from game.settings_menu import SettingsMenu
from game.notebook import StudentNotebook
from game.character_customizer import CharacterCustomizer
from game.intro import IntroPrologue
from game.title_screen import TitleScreen

def main():
    pygame.init()
    pygame.font.init()

    # 1. Configuración, Guardado y Subsistemas
    config = ConfigManager()
    save = SaveSystem()
    audio = AudioManager(config)
    db = DatabaseManager()
    curriculum = UniversityCurriculum(db, save, audio)

    # 2. Modo de Pantalla
    screen_mode = config.get("screen_mode", "windowed")
    resolution = config.get("resolution", [960, 600])

    def setup_display(mode, res):
        flags = 0
        if mode == "fullscreen":
            flags = pygame.FULLSCREEN
        elif mode == "borderless":
            flags = pygame.NOFRAME
        else:
            flags = pygame.RESIZABLE
        win = pygame.display.set_mode((res[0], res[1]), flags)
        pygame.display.set_caption("El Camino SQL: Para todo buen final, hay un inicio...")
        return win

    window = setup_display(screen_mode, resolution)

    def on_apply_video_mode(new_mode, new_res):
        nonlocal window, resolution, screen_mode
        screen_mode = new_mode
        resolution = new_res
        window = setup_display(new_mode, new_res)

    def clean_quit():
        save.save()
        audio.play_bell()
        pygame.quit()
        sys.exit(0)

    virtual_screen = pygame.Surface((VIRTUAL_WIDTH, VIRTUAL_HEIGHT))
    clock = pygame.time.Clock()
    tick = 0

    # 3. Entidades y Capas
    world = World()
    player = Player(x=100, y=165, custom_data=save.data)
    terminal = SQLTerminal(db, audio, curriculum)
    dialog = DialogBox(audio)
    lecture = LectureScene(audio, save)
    settings = SettingsMenu(config, audio, on_apply_video_mode, on_quit_game=clean_quit)
    notebook = StudentNotebook(audio, save)

    # Estado de flujo principal: "title", "intro", "customizer", "game"
    current_state = "title"

    # Callbacks de Título y Creación
    def start_game_from_save():
        nonlocal current_state
        current_state = "game"
        player.update_customization(save.data)
        if not curriculum.lecture_done_for_day:
            lecture.start_lecture(
                curriculum.current_year,
                curriculum.current_day,
                curriculum.get_year_attempts(),
                on_finish=lambda: setattr(curriculum, "lecture_done_for_day", True)
            )

    def on_intro_finished():
        nonlocal current_state
        current_state = "customizer"
        customizer.open()

    def on_customization_confirmed(data):
        nonlocal current_state
        save.reset_new_game(
            name=data["name"],
            gender=data["gender"],
            skin_tone=data["skin_tone"],
            hair_color=data["hair_color"],
            hair_style=data["hair_style"],
            shirt_color=data["shirt_color"]
        )
        player.update_customization(save.data)
        curriculum.current_year = 1
        curriculum.current_day = 1
        curriculum.day_task_completed = False
        curriculum.lecture_done_for_day = False
        current_state = "game"
        lecture.start_lecture(
            1, 1, 1,
            on_finish=lambda: setattr(curriculum, "lecture_done_for_day", True)
        )

    def start_new_game():
        nonlocal current_state
        current_state = "intro"
        intro.start()

    intro = IntroPrologue(audio, on_intro_finished)
    customizer = CharacterCustomizer(audio, on_customization_confirmed)
    title_screen = TitleScreen(
        audio, save,
        on_continue=start_game_from_save,
        on_new_game=start_new_game,
        on_open_notes=lambda: notebook.open(),
        on_open_settings=lambda: settings.open()
    )

    # Fuentes en caché para optimizar el bucle principal de renderizado (60 FPS estables)
    font_prompt = pygame.font.Font(None, 14)
    font_hud = pygame.font.Font(None, 12)
    font_watermark = pygame.font.Font(None, 12)

    running = True
    while running:
        clock.tick(FPS)
        tick += 1

        # 4. Procesamiento de Eventos
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break

            # Menú de Opciones (prioridad global)
            if settings.active:
                if settings.handle_event(event):
                    continue

            # Cuaderno de Apuntes (prioridad global)
            if notebook.active:
                if notebook.handle_event(event):
                    continue

            # Máquina de estados principal
            if current_state == "title":
                if title_screen.handle_event(event):
                    continue

            elif current_state == "intro":
                if intro.handle_event(event):
                    continue

            elif current_state == "customizer":
                if customizer.handle_event(event):
                    continue

            elif current_state == "game":
                # Clase en pizarra
                if lecture.active:
                    if lecture.handle_event(event):
                        continue

                # Diálogos con NPCs
                if dialog.active:
                    if dialog.handle_event(event):
                        continue

                # Terminal SQL
                if terminal.active:
                    if terminal.handle_event(event):
                        if terminal.request_notebook:
                            terminal.request_notebook = False
                            notebook.open()
                        continue

                # Modo Libre
                if event.type == pygame.KEYDOWN:
                    # Tecla N: Cuaderno de Apuntes
                    if event.key == pygame.K_n:
                        notebook.open()
                        continue

                    # Tecla Q: Salir del Juego
                    if event.key == pygame.K_q:
                        clean_quit()
                        continue

                    # Tecla O o F2: Ajustes
                    if event.key in [pygame.K_o, pygame.K_F2]:
                        settings.open()
                        audio.play_key()
                        continue

                    if event.key == pygame.K_ESCAPE:
                        settings.open()
                        continue

                    # Tecla E o ENTER o ESPACIO: Interactuar
                    if event.key in [pygame.K_e, pygame.K_RETURN, pygame.K_SPACE]:
                        obj_type, _, target_obj = world.check_interaction(player.get_rect(), curriculum)

                        if obj_type == "pc":
                            terminal.open()

                        elif obj_type == "classmate" and target_obj:
                            audio.play_key()
                            speech = target_obj.get_speech(curriculum.current_year, curriculum.current_day, curriculum.day_task_completed)
                            dialog.show(
                                title=f"{target_obj.name} (Compañero/a)",
                                text=speech,
                                speaker=target_obj.name
                            )

                        elif obj_type == "empty_desk" and target_obj:
                            audio.play_key()
                            dialog.show(
                                title=f"Puesto de {target_obj.name} (Vacío)",
                                text=target_obj.dropout_note,
                                speaker="Nota pegada en el monitor"
                            )

                        elif obj_type == "prof":
                            audio.play_key()
                            pname = save.data.get("player_name", "Estudiante")
                            prole = save.data.get("title_role", "Alumno")

                            # 1. Si la clase teórica de hoy no se ha visto, iniciar clase
                            if not curriculum.lecture_done_for_day:
                                lecture.start_lecture(
                                    curriculum.current_year,
                                    curriculum.current_day,
                                    curriculum.get_year_attempts(),
                                    on_finish=lambda: setattr(curriculum, "lecture_done_for_day", True)
                                )

                            # 2. Si completó la tarea del día y estamos de Lunes a Jueves (Días 1 a 4)
                            elif curriculum.day_task_completed and curriculum.current_day < 5:
                                p_day = curriculum.current_day
                                def advance_day():
                                    curriculum.finish_day()
                                    lecture.start_lecture(
                                        curriculum.current_year,
                                        curriculum.current_day,
                                        curriculum.get_year_attempts(),
                                        on_finish=lambda: setattr(curriculum, "lecture_done_for_day", True)
                                    )

                                dialog.show(
                                    title=f"¡Laboratorio Completado (Día {p_day})!",
                                    text=f"¡Gran trabajo hoy, {pname}! Has completado todos los ejercicios del Día {p_day}. He registrado el resumen en tu Cuaderno de Apuntes [N]. Descansemos y nos vemos mañana.",
                                    speaker="Prof. Turing",
                                    callback=advance_day
                                )

                            # 3. Si terminó el Examen del Viernes (Día 5)
                            elif curriculum.current_day == 5 and curriculum.exam_finished:
                                grade = curriculum.exam_final_grade
                                if grade >= 4.0:
                                    if curriculum.current_year < 4:
                                        next_y = curriculum.current_year + 1
                                        def advance_year():
                                            curriculum.advance_to_next_year()
                                            lecture.start_lecture(
                                                curriculum.current_year,
                                                curriculum.current_day,
                                                curriculum.get_year_attempts(),
                                                on_finish=lambda: setattr(curriculum, "lecture_done_for_day", True)
                                            )
                                        dialog.show(
                                            title=f"¡AÑO {curriculum.current_year} APROBADO CON ÉXITO!",
                                            text=f"¡Excelente rendimiento, {prole} {pname}! Tu nota final es un {grade:.1f}. Quedas oficialmente promovido al Año {next_y} de la carrera.",
                                            speaker="Prof. Turing",
                                            callback=advance_year
                                        )
                                    else:
                                        # ¡GRADUACIÓN DE 4TO AÑO!
                                        curriculum.advance_to_next_year()
                                        dialog.show(
                                            title="🎓 ¡TITULACIÓN DE INGENIERO INFORMÁTICO! 🎓",
                                            text=f"¡IMPRESIONANTE, {pname}! Has aprobado tu Examen de Grado con nota {grade:.1f}. En nombre del Instituto Tecnológico, te confiero formalmente tu TÍTULO OFICIAL DE INGENIERO INFORMÁTICO. ¡Estás listo para conquistar la industria!",
                                            speaker="Prof. Turing"
                                        )
                                else:
                                    # Reprobó el año: Repite el año actual (nunca retrocede)
                                    cur_y = curriculum.current_year
                                    def repeat_year():
                                        curriculum.repeat_current_year()
                                        lecture.start_lecture(
                                            curriculum.current_year,
                                            1,
                                            curriculum.get_year_attempts(),
                                            on_finish=lambda: setattr(curriculum, "lecture_done_for_day", True)
                                        )

                                    dialog.show(
                                        title=f"Resultado del Examen (Año {cur_y})",
                                        text=f"Tu nota final fue un {grade:.1f}. Para pasar de año se requiere un 4.0 mínimo. No te desanimes {pname}, los mejores ingenieros se forjan con perseverancia. Repetiremos el Año {cur_y} hasta dominarlo por completo.",
                                        speaker="Prof. Turing",
                                        callback=repeat_year
                                    )

                            # 4. Tarea aún pendiente: Turing da pistas de ayuda
                            else:
                                if curriculum.current_day <= 4:
                                    task = curriculum.get_current_task()
                                    dialog.show(
                                        title=f"Pista del Profesor ({pname})",
                                        text=f"Para el ejercicio actual: {task.hint}. Revisa también tus Apuntes pulsando la tecla [N].",
                                        speaker="Prof. Turing"
                                    )
                                else:
                                    dialog.show(
                                        title=f"Viernes de Examen ({pname})",
                                        text="Hoy es tu Examen. Ve a tu estación de trabajo y pulsa [E] para responder las 3 preguntas acumulativas.",
                                        speaker="Prof. Turing"
                                    )

                        elif obj_type == "book":
                            audio.play_key()
                            notebook.open()

        # 5. Actualizar Lógica de Juego
        if current_state == "game":
            if not terminal.active and not dialog.active and not lecture.active and not settings.active and not notebook.active:
                keys = pygame.key.get_pressed()
                player.update(keys, world.colliders)

        # 6. Renderizar según el estado activo
        if current_state == "title":
            title_screen.draw(virtual_screen, tick)

        elif current_state == "intro":
            intro.draw(virtual_screen, tick)

        elif current_state == "customizer":
            customizer.draw(virtual_screen, tick)

        elif current_state == "game":
            world.draw(virtual_screen, tick, curriculum, save)
            player.draw(virtual_screen)

            # Indicador Contextual Flotante
            if not terminal.active and not dialog.active and not lecture.active and not settings.active and not notebook.active:
                obj_type, prompt_text, _ = world.check_interaction(player.get_rect(), curriculum)
                if prompt_text:
                    p_surf = font_prompt.render(prompt_text, True, COLOR_AMBER)
                    p_w = p_surf.get_width() + 16
                    bx = VIRTUAL_WIDTH // 2 - p_w // 2
                    by = 265
                    pygame.draw.rect(virtual_screen, (10, 15, 25, 230), (bx, by, p_w, 20))
                    pygame.draw.rect(virtual_screen, COLOR_AMBER, (bx, by, p_w, 20), 1)
                    virtual_screen.blit(p_surf, (bx + 8, by + 4))

            # HUD Superior
            if not terminal.active and not lecture.active and not settings.active and not notebook.active:
                pname = save.data.get("player_name", "Novato")
                prole = save.data.get("title_role", "Alumno")

                if curriculum.current_day <= 4:
                    hud_txt = f"{prole} {pname}  |  AÑO {curriculum.current_year}/4 (DÍA {curriculum.current_day}/5)  |  [N] Apuntes  |  [O] Ajustes  |  [Q] Salir"
                else:
                    hud_txt = f"{prole} {pname}  |  AÑO {curriculum.current_year}/4 - ¡EXAMEN VIERNES! (Aciertos: {curriculum.exam_score}/3)  |  [N] Apuntes  |  [O] Ajustes  |  [Q] Salir"

                h_surf = font_hud.render(hud_txt, True, (230, 240, 255))
                pygame.draw.rect(virtual_screen, (12, 18, 30, 210), (8, 6, h_surf.get_width() + 14, 18))
                pygame.draw.rect(virtual_screen, (40, 65, 100), (8, 6, h_surf.get_width() + 14, 18), 1)
                virtual_screen.blit(h_surf, (15, 9))

                # Marca de autoría en la esquina superior derecha: by Seavuelo
                wm_surf = font_watermark.render("by Seavuelo", True, (0, 229, 255))
                wm_w = wm_surf.get_width() + 10
                pygame.draw.rect(virtual_screen, (12, 18, 30, 210), (VIRTUAL_WIDTH - wm_w - 8, 6, wm_w, 18))
                pygame.draw.rect(virtual_screen, (40, 65, 100), (VIRTUAL_WIDTH - wm_w - 8, 6, wm_w, 18), 1)
                virtual_screen.blit(wm_surf, (VIRTUAL_WIDTH - wm_w - 3, 9))

            # Capas superpuestas
            if dialog.active:
                dialog.draw(virtual_screen)

            if terminal.active:
                terminal.draw(virtual_screen, tick)

            if lecture.active:
                lecture.draw(virtual_screen)

        # Capas globales (accesibles en cualquier pantalla)
        if notebook.active:
            notebook.draw(virtual_screen)

        if settings.active:
            settings.draw(virtual_screen)

        # 7. Escalar a Ventana
        if resolution[0] == VIRTUAL_WIDTH and resolution[1] == VIRTUAL_HEIGHT:
            window.blit(virtual_screen, (0, 0))
        else:
            scaled = pygame.transform.scale(virtual_screen, (resolution[0], resolution[1]))
            window.blit(scaled, (0, 0))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
