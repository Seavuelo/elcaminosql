import os
import tempfile
import unittest
import subprocess
import sys
from pathlib import Path
from unittest.mock import Mock, patch

os.environ["SDL_VIDEODRIVER"] = "dummy"
os.environ["SDL_AUDIODRIVER"] = "dummy"
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"

import pygame

from game.database import DatabaseManager
from game.curriculum import UniversityCurriculum, DailyTask, ExamQuestion
from game.save_system import SaveSystem, DEFAULT_SAVE
from game.terminal import SQLTerminal


class GameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pygame.init()

    @classmethod
    def tearDownClass(cls):
        pygame.quit()

    def setUp(self):
        pygame.init()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.save_path = str(Path(self.temp.name) / "savegame.json")
        self.config_path = str(Path(self.temp.name) / "config.json")
        self.patches = [patch("game.save_system.SAVE_DIR", self.temp.name),
                        patch("game.save_system.SAVE_FILE", self.save_path),
                        patch("game.config.CONFIG_PATH", self.config_path),
                        patch.dict('game.config.DEFAULT_CONFIG',{'creator_note_seen':True})]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        self.db = DatabaseManager(str(Path(self.temp.name) / "practice.db"))
        self.db.reset()
        self.save = SaveSystem()
        self.audio = Mock()
        self.course = UniversityCurriculum(self.db, self.save, self.audio)
        self.terminal = SQLTerminal(self.db, self.audio, self.course)

    def query(self, sql, **kwargs):
        return self.db.execute_query(sql, **kwargs)

    def execute(self, sql):
        self.terminal.input_text = sql
        self.terminal.execute()
        return self.terminal.last_result

    def test_read_permissions_use_sqlite_not_text(self):
        for sql in ("DELETE\nFROM estudiantes", "DROP TABLE profesores",
                    "WITH x AS (SELECT 1) UPDATE estudiantes SET estado='Otro'",
                    "PRAGMA user_version=10", "ATTACH ':memory:' AS otra"):
            with self.subTest(sql=sql):
                self.assertFalse(self.query(sql)["success"])
        self.assertTrue(self.query("SELECT 'CREATE TABLE INSERT UPDATE DELETE' AS texto")["success"])
        self.assertEqual(self.query("SELECT COUNT(*) FROM estudiantes")["rows"], [(12,)])

    def test_core_schema_and_external_files_are_protected(self):
        for sql in ('DROP TABLE\n"estudiantes"',
                    'ALTER TABLE profesores RENAME TO otros',
                    "ATTACH ':memory:' AS otra", "PRAGMA writable_schema=ON"):
            with self.subTest(sql=sql):
                self.assertFalse(self.query(sql, allow_write=True)["success"])
        self.assertTrue(self.query("SELECT * FROM profesores")["success"])

    def test_invalid_write_is_rolled_back(self):
        expected = "UPDATE estudiantes SET estado='Graduado' WHERE promedio >= 6.8"
        result = self.query("UPDATE estudiantes SET estado='Graduado'", allow_write=True,
                            expected_query=expected)
        self.assertFalse(result["success"])
        self.assertEqual(self.query("SELECT COUNT(*) FROM estudiantes WHERE estado='Graduado'")["rows"], [(0,)])
        self.assertTrue(self.query(expected, allow_write=True, expected_query=expected)["success"])

    def test_ddl_structure_and_equivalent_formatting(self):
        expected = "CREATE TABLE IF NOT EXISTS proyectos (id INTEGER PRIMARY KEY, titulo TEXT, nota REAL)"
        self.assertFalse(self.query("CREATE TABLE proyectos (id TEXT)", allow_write=True,
                                    expected_query=expected)["success"])
        self.assertNotIn("proyectos", self.db.get_schema())
        self.assertTrue(self.query("CREATE TABLE proyectos(id INTEGER PRIMARY KEY,titulo TEXT,nota REAL)",
                                   allow_write=True, expected_query=expected)["success"])

    def test_write_words_inside_select_preserve_results(self):
        result = self.query("SELECT 'UPDATE' AS palabra", allow_write=True)
        self.assertEqual(result["columns"], ["palabra"])
        self.assertEqual(result["rows"], [("UPDATE",)])

    def test_schema_handles_quoted_names_and_views(self):
        self.assertTrue(self.query('CREATE TABLE "mi tabla" ("a b" TEXT)', allow_write=True, expected_query='CREATE TABLE "mi tabla" ("a b" TEXT)')["success"])
        self.assertTrue(self.query('CREATE VIEW vista AS SELECT * FROM "mi tabla"', allow_write=True, expected_query='CREATE VIEW vista AS SELECT * FROM "mi tabla"')["success"])
        self.assertIn("mi tabla", self.db.get_schema())
        self.assertIn("vista", self.db.get_schema())
        with self.db.get_connection() as conn:
            conn.execute("CREATE VIEW incompleta AS SELECT * FROM inexistente")
        conn.close()
        self.assertNotIn("incompleta", self.db.get_schema())

    def test_queries_have_a_work_limit(self):
        sql = "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x+1 FROM n) SELECT sum(x) FROM n"
        self.assertFalse(self.query(sql)["success"])
        self.assertTrue(self.query("SELECT 1")["success"])

    def test_sql_error_releases_write_lock(self):
        self.assertFalse(self.query("INSERT INTO estudiantes(id) VALUES(1)", allow_write=True)["success"])
        self.assertTrue(self.query("UPDATE estudiantes SET estado='Activo' WHERE id=1", allow_write=True, expected_query="UPDATE estudiantes SET estado='Activo' WHERE id=1")["success"])

    def test_progress_survives_restart(self):
        self.course.complete_lecture()
        self.course.advance_daily_task()
        restored = UniversityCurriculum(self.db, SaveSystem(), self.audio)
        self.assertEqual(restored.current_task_idx, 1)
        self.assertTrue(restored.lecture_done_for_day)
        while not self.course.day_task_completed:
            self.course.advance_daily_task()
        restored = UniversityCurriculum(self.db, SaveSystem(), self.audio)
        self.assertTrue(restored.day_task_completed)

    def test_default_save_has_no_shared_mutable_state(self):
        self.save.data["passed_notes"].append("test")
        self.save.data["year_attempts"]["1"] = 10
        self.assertEqual(DEFAULT_SAVE["passed_notes"], [])
        self.assertEqual(DEFAULT_SAVE["year_attempts"]["1"], 1)

    def test_failed_save_preserves_previous_file(self):
        self.save.save()
        previous = Path(self.save_path).read_bytes()
        self.save.data["player_name"] = "Nuevo"
        with patch("game.save_system.os.replace", side_effect=OSError("disco no disponible")):
            self.save.save()
        self.assertEqual(Path(self.save_path).read_bytes(), previous)

    def test_audio_settings_work_without_audio_device(self):
        from game.audio import AudioManager
        config = Mock()
        config.get.return_value = 0.5
        with patch.object(pygame.mixer, "get_init", return_value=None), \
                patch.object(pygame.mixer, "init", side_effect=pygame.error("sin dispositivo")):
            audio = AudioManager(config)
        self.assertFalse(audio.sfx_enabled)
        audio.update_volumes()

    def test_failed_exam_advances_and_survives_restart(self):
        self.course.current_day = 5
        for index in range(len(self.course.get_current_exam_questions())):
            self.assertTrue(self.execute("SELECT 1 AS incorrecto")["success"])
            self.assertEqual(self.course.exam_q_index, index + 1)
        self.assertTrue(self.course.exam_finished)
        self.assertEqual(self.course.exam_final_grade, 1.0)
        restored = UniversityCurriculum(self.db, SaveSystem(), self.audio)
        self.assertTrue(restored.exam_finished)
        self.assertEqual(restored.exam_score, 0)
        self.course.repeat_current_year()
        self.assertEqual(self.course.current_day, 1)
        self.assertEqual(self.course.get_year_attempts(), 2)

    def test_complete_four_year_course_through_terminal(self):
        for year in range(1, 5):
            self.assertEqual(self.course.current_year, year)
            for day in range(1, 5):
                for _ in range(self.course.get_total_tasks_today()):
                    task = self.course.get_current_task()
                    result = self.execute(task.canonical_query)
                    self.assertTrue(result["success"], (task.title, result))
                    self.assertTrue(self.terminal.feedback_is_success, self.terminal.feedback_message)
                self.assertTrue(self.course.day_task_completed)
                self.course.finish_day()
            for question in self.course.get_current_exam_questions():
                result = self.execute(question.canonical_query)
                self.assertTrue(result["success"], result)
                self.assertTrue(self.terminal.feedback_is_success, self.terminal.feedback_message)
            self.assertEqual(self.course.exam_final_grade, 7.0)
            self.course.advance_to_next_year()
        self.assertTrue(self.save.data["is_graduated"])

    def test_repeat_second_year_restores_practice_data(self):
        self.course.current_year = 2
        self.query("CREATE TABLE proyectos (id INTEGER)", allow_write=True)
        self.query("DELETE FROM materias", allow_write=True)
        self.course.repeat_current_year()
        self.assertNotIn("proyectos", self.db.get_schema())
        self.assertEqual(self.query("SELECT COUNT(*) FROM materias")["rows"], [(6,)])

    def test_null_and_float_results_do_not_crash_validation(self):
        sql = "SELECT NULL AS valor UNION ALL SELECT 1.5"
        result = self.query(sql)
        task = DailyTask(1, 1, 0, "", "", "", sql, "Bien")
        exam = ExamQuestion(1, "", "", sql)
        self.assertTrue(task.validate(self.db, result)[0])
        self.assertTrue(exam.validate(self.db, result)[0])

    def test_window_close_does_not_create_a_blank_save(self):
        import main
        with patch.object(main, "DatabaseManager", return_value=self.db), \
                patch.object(pygame, "quit"), \
                patch.object(pygame.event, "get", side_effect=[[], [pygame.event.Event(pygame.QUIT)]]):
            with self.assertRaises(SystemExit):
                main.main()
        self.assertFalse(Path(self.save_path).exists())

    def test_new_game_and_scaled_notebook_click(self):
        import main
        from game.notebook import StudentNotebook
        notebook = StudentNotebook(self.audio, self.save)

        def key(value):
            return pygame.event.Event(pygame.KEYDOWN, key=value, unicode="")

        events = [
            [key(pygame.K_RETURN)], [key(pygame.K_ESCAPE)],
            [key(pygame.K_DOWN)] * 12 + [key(pygame.K_RETURN)],
            [key(pygame.K_ESCAPE)], [key(pygame.K_e)],
            [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(800, 30))],
            [key(pygame.K_ESCAPE)], [key(pygame.K_ESCAPE)],
            [key(pygame.K_o)], [key(pygame.K_ESCAPE)],
            [key(pygame.K_c)],
            [key(pygame.K_DOWN)] * 2 + [key(pygame.K_RIGHT)],
            [key(pygame.K_DOWN)] * 10 + [key(pygame.K_RETURN)],
            [pygame.event.Event(pygame.QUIT)],
        ]
        with patch.object(main, "DatabaseManager", return_value=self.db), \
                patch.object(main, "StudentNotebook", return_value=notebook), \
                patch("game.foundations.FoundationsScene.open", lambda scene, on_finish, on_exit, review=False: on_finish()), \
                patch.object(notebook, "open", wraps=notebook.open) as open_notes, \
                patch.object(pygame, "quit"), \
                patch.object(pygame.event, "get", side_effect=events):
            with self.assertRaises(SystemExit):
                main.main()
        open_notes.assert_called_once()
        self.assertFalse(SaveSystem().data["lecture_done_for_day"])
        self.assertEqual(SaveSystem().data["skin_tone"], 1)

    def test_table_rendering_stays_inside_its_panel(self):
        from game.ui_helpers import draw_sql_grid_table
        surface = pygame.Surface((480, 300))
        background = (255, 0, 255)
        surface.fill(background)
        rect = pygame.Rect(20, 20, 200, 80)
        draw_sql_grid_table(surface, rect, ["columna muy larga"] * 8,
                            [["dato largo"] * 8] * 10)
        self.assertEqual(surface.get_clip(), surface.get_rect())
        for point in ((220, 30), (30, 100), (225, 95)):
            self.assertEqual(surface.get_at(point)[:3], background)

    def test_character_name_length_includes_spaces(self):
        from game.character_customizer import CharacterCustomizer
        customizer = CharacterCustomizer(self.audio, Mock())
        customizer.open()
        customizer.typing_name = True
        customizer.player_name = "A" * 14
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE, unicode=" ")
        customizer.handle_event(event)
        self.assertEqual(len(customizer.player_name), 14)

    def test_customization_matches_game_and_survives_save(self):
        from game.appearance import CUSTOM_FIELDS
        from game.character_customizer import CharacterCustomizer
        from game.player import Player
        editor = CharacterCustomizer(self.audio, Mock())
        editor.open()
        for key, (_, options) in editor.OPTIONS.items():
            editor.values[key] = len(options) - 1
        editor._refresh_preview()
        self.save.reset_new_game(**editor._data())
        restored = SaveSystem()
        player = Player(0, 0, restored.data)
        for key in CUSTOM_FIELDS:
            self.assertEqual(restored.data[key], editor.values[key])
        for direction in player.sprites:
            self.assertEqual(pygame.image.tobytes(player.sprites[direction][0], "RGBA"),
                             pygame.image.tobytes(editor.preview.sprites[direction][0], "RGBA"))

    def test_each_appearance_option_changes_the_sprite(self):
        from game.character_customizer import CharacterCustomizer
        from game.player import Player
        base = Player(0, 0)
        original = pygame.image.tobytes(base.sprites["down"][0], "RGBA")
        for key, (_, choices) in CharacterCustomizer.OPTIONS.items():
            for value in range(1, len(choices)):
                with self.subTest(key=key, value=value):
                    sprite = Player(0, 0, {key: value}).sprites["down"][0]
                    self.assertNotEqual(pygame.image.tobytes(sprite, "RGBA"), original)

    def test_exam_preview_does_not_consume_an_answer(self):
        self.course.current_day = 5
        self.terminal.input_text = self.course.get_current_exam_question().canonical_query
        self.terminal.execute(submit=False)
        self.assertEqual(self.course.exam_q_index, 0)
        self.terminal.execute(submit=True)
        self.assertEqual(self.course.exam_q_index, 1)

    def test_exam_write_preview_rolls_back_and_submit_commits(self):
        self.course.current_year, self.course.current_day = 2, 5
        self.course.exam_q_index = 3
        self.terminal.input_text = self.course.get_current_exam_question().canonical_query
        self.terminal.execute(submit=False)
        self.assertNotIn("revision", self.db.get_schema())
        self.assertEqual(self.course.exam_q_index, 3)
        self.terminal.execute()
        self.assertIn("revision", self.db.get_schema())
        self.assertEqual(self.course.exam_q_index, 4)

    def test_wrong_exam_write_counts_but_does_not_damage_data(self):
        self.course.current_year, self.course.current_day = 2, 5
        self.course.exam_q_index = 3
        self.execute("CREATE TABLE equivocada (id TEXT)")
        self.assertNotIn("equivocada", self.db.get_schema())
        self.assertEqual(self.course.exam_q_index, 4)
        self.assertEqual(self.course.exam_score, 0)

    def test_exam_rubric_has_sixty_percent_pass_mark(self):
        for score, grade in [(0, 1.0), (1, 2.0), (2, 3.0), (3, 4.0), (4, 5.5), (5, 7.0)]:
            self.course.exam_q_index = 4
            self.course.exam_score = score
            self.course.advance_exam_question(False)
            self.assertEqual(self.course.exam_final_grade, grade)

    def test_query_aliases_are_accepted(self):
        task = self.course.get_current_task()
        result = self.query("SELECT id AS codigo, nombre AS persona, carrera AS programa, semestre AS periodo, promedio AS media, estado AS situacion FROM estudiantes")
        self.assertTrue(task.validate(self.db, result)[0])

    def test_dialog_pages_are_complete_and_callback_runs_at_the_end(self):
        from game.dialog import DialogBox
        from game.ui_helpers import wrap_text_lines
        dialog = DialogBox(self.audio)
        text = "Una conversación que ocupa varias páginas. " * 30
        callback = Mock()
        dialog.show("Prueba", text, callback=callback)
        self.assertGreater(len(dialog.pages), 1)
        self.assertEqual(" ".join(" ".join(dialog.pages).split()), " ".join(text.split()))
        for page in dialog.pages:
            lines = wrap_text_lines(page, dialog.font_text, 382)
            self.assertLessEqual(len(lines) * (dialog.font_text.get_linesize() + 2) - 2, 56)
        while dialog.page_index < len(dialog.pages) - 1:
            dialog.advance()
            callback.assert_not_called()
        dialog.advance()
        callback.assert_called_once()

    def test_every_lesson_page_fits_its_text_boxes(self):
        from game.lecture import LectureScene
        from game.ui_helpers import wrap_text_lines
        lecture = LectureScene(self.audio, self.save)
        screen = pygame.Surface((480, 300))
        for year in range(1, 5):
            for day in range(1, 6):
                lecture.start_lecture(year, day, 1, Mock())
                if day < 5:
                    self.assertGreaterEqual(len(lecture.slides), 3)
                for index, slide in enumerate(lecture.slides):
                    for key, font, width, height, spacing in (
                        ("chalk_body", lecture.font_chalk, 424, 58 if slide["code_example"] else 146, 2),
                        ("code_example", lecture.font_code, 412, 76, 1),
                        ("turing", lecture.font_body, 394, 52, 2),
                    ):
                        lines = wrap_text_lines(slide[key], font, width)
                        self.assertLessEqual(len(lines) * (font.get_linesize() + spacing) - spacing, height)
                    lecture.slide_index = index
                    lecture.chalk_is_done = True
                    lecture.chalk_char_index = 10000
                    lecture.draw(screen)

    def test_practice_data_has_nulls_duplicates_and_missing_relations(self):
        result = self.query("SELECT COUNT(*), COUNT(asistencia), COUNT(DISTINCT estudiante_id) FROM tutorias")
        self.assertEqual(result["rows"], [(4, 3, 3)])
        self.assertEqual(self.query("SELECT COUNT(*) FROM estudiantes WHERE id NOT IN (SELECT estudiante_id FROM tutorias)")["rows"], [(9,)])

    @unittest.skipUnless(os.name == "nt", "Lanzador para Windows")
    def test_windows_launcher_starts_game_from_another_directory(self):
        bootstrap = Path(self.temp.name) / "sitecustomize.py"
        bootstrap.write_text('''
import os
import pygame
import game.save_system as save
import game.database as database
import game.config as config
folder = os.environ["ELCAMINO_TEST_DIR"]
save.SAVE_DIR = folder
save.SAVE_FILE = os.path.join(folder, "launcher_save.json")
database.SAVE_DIR = folder
config.CONFIG_PATH = os.path.join(folder, "config.json")
frames = iter([[], [pygame.event.Event(pygame.QUIT)]])
pygame.event.get = lambda: next(frames)
''', encoding="utf-8")
        root = Path(__file__).resolve().parents[1]
        env = dict(os.environ, PYTHONPATH=os.pathsep.join((self.temp.name, str(root))),
                   ELCAMINO_TEST_DIR=self.temp.name)
        result = subprocess.run(["cmd", "/c", str(root / "Jugar-Pygame.cmd")], cwd=self.temp.name,
                                env=env, capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((Path(self.temp.name) / "launcher_save.json").exists())

    @unittest.skipUnless(os.name == "nt", "Bloqueo de instancia en Windows")
    def test_repeated_launches_exit_without_loading_the_game(self):
        root = Path(__file__).resolve().parents[1]
        mutex_name = f"Local\\ElCaminoSQL.Test.{os.getpid()}.{id(self)}"
        holder_code = ("from game.single_instance import acquire_game_lock; "
                       f"print('locked' if acquire_game_lock({mutex_name!r}) else 'busy', flush=True); input()")
        holder = subprocess.Popen([sys.executable, "-u", "-c", holder_code], cwd=root,
                                  stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(holder.stdout.readline().strip(), "locked")
            duplicate_code = ("from unittest.mock import patch; import launch_game; "
                              "from game.single_instance import acquire_game_lock; "
                              f"launch_game.acquire_game_lock = lambda: acquire_game_lock({mutex_name!r}); "
                              "guard = patch('runpy.run_path', side_effect=AssertionError('duplicate game')); "
                              "guard.start(); raise SystemExit(launch_game.main())")
            for _ in range(3):
                result = subprocess.run([sys.executable, "-c", duplicate_code], cwd=root,
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            direct_code = ("import runpy; import game.single_instance as guard; "
                           "original = guard.acquire_game_lock; "
                           f"guard.acquire_game_lock = lambda: original({mutex_name!r}); "
                           "runpy.run_path('main.py', run_name='__main__')")
            direct = subprocess.run([sys.executable, "-c", direct_code], cwd=root,
                                    capture_output=True, text=True, timeout=5)
            self.assertEqual(direct.returncode, 0, direct.stdout + direct.stderr)
            self.assertEqual(direct.stdout, "")
        finally:
            holder.communicate(input="\n", timeout=5)
        released = subprocess.run([sys.executable, "-c",
                                   f"from game.single_instance import acquire_game_lock; assert acquire_game_lock({mutex_name!r})"],
                                  cwd=root, capture_output=True, text=True, timeout=5)
        self.assertEqual(released.returncode, 0, released.stderr)

    def test_classmates_stay_until_after_completed_day_conversation(self):
        from game.world import World
        world = World()
        cm = world.classmates[0]
        world.finish_conversation(cm, self.course)
        self.assertEqual(cm.state, "studying")
        self.course.day_task_completed = True
        world.update(10, self.course)
        self.assertEqual(cm.state, "studying")
        world.finish_conversation(cm, self.course)
        self.assertEqual(cm.state, "packing")
        self.assertTrue(cm.pc_on)
        world.update(1.4, self.course)
        self.assertEqual(cm.state, "shutdown")
        self.assertFalse(cm.pc_on)
        world.update(0.6, self.course)
        self.assertEqual(cm.state, "standing")

    def test_every_departure_route_avoids_the_furniture(self):
        from game.world import World
        world = World()
        self.course.day_task_completed = True
        for cm in world.classmates:
            world.finish_conversation(cm, self.course)
        for _ in range(1800):
            world.update(1 / 60, self.course)
            for cm in world.classmates:
                if cm.state in ("standing", "walking", "exiting"):
                    rect = pygame.Rect(round(cm.x), round(cm.y), 16, 20)
                    self.assertFalse(any(rect.colliderect(item) for item in world.colliders),
                                     (cm.name, cm.state, rect))
        self.assertTrue(all(cm.state == "gone" for cm in world.classmates))

    def test_departing_classmate_can_repeat_dialogue_without_restarting(self):
        from game.world import World
        world = World()
        self.course.day_task_completed = True
        cm = world.classmates[0]
        world.finish_conversation(cm, self.course)
        world.update(1.4, self.course)
        world.update(0.6, self.course)
        world.update(0.5, self.course)
        world.update(1.0, self.course)
        position, route = (cm.x, cm.y), list(cm.route)
        speech = cm.get_speech(1, 1, True)
        kind, _, target = world.check_interaction(pygame.Rect(round(cm.x), round(cm.y), 16, 20), self.course)
        self.assertEqual(kind, "classmate")
        self.assertIs(target, cm)
        world.update(3, self.course, paused=True)
        self.assertEqual((cm.x, cm.y), position)
        world.finish_conversation(cm, self.course)
        self.assertEqual(cm.state, "walking")
        self.assertEqual(cm.route, route)
        self.assertEqual(cm.get_speech(1, 1, False), speech)

    def test_new_day_and_repeat_year_restore_classmates(self):
        from game.world import World
        world = World()
        self.course.day_task_completed = True
        cm = world.classmates[0]
        world.finish_conversation(cm, self.course)
        cm.state = "gone"
        self.course.current_day = 2
        world.update(0, self.course, paused=True)
        self.assertEqual(cm.state, "studying")
        self.assertTrue(cm.pc_on)
        self.assertIsNone(cm.departure_speech)
        cm.state = "gone"
        self.save.data["year_attempts"]["1"] = 2
        world.update(0, self.course)
        self.assertEqual(cm.state, "studying")

    def test_friday_departure_uses_exam_completion(self):
        from game.world import World
        world = World()
        cm = world.classmates[0]
        self.course.current_day = 5
        world.finish_conversation(cm, self.course)
        self.assertEqual(cm.state, "studying")
        self.course.exam_finished = True
        world.finish_conversation(cm, self.course)
        self.assertEqual(cm.state, "packing")
        self.assertEqual(cm.departure_speech, cm.dialogues_after[(1, 5)])

    def test_moshi_appearance_dialogues_and_presence_in_every_year(self):
        from game.world import World
        import re
        world = World()
        moshi = next(cm for cm in world.classmates if cm.id == "moshi")
        self.assertFalse(moshi.glasses)
        self.assertTrue(moshi.hoodie)
        self.assertEqual(moshi.hair_color, (175, 125, 75))
        self.assertEqual(moshi.eye_color, (125, 145, 75))
        self.assertEqual(moshi.shirt_color, (190, 155, 115))
        self.assertEqual(moshi.pants_color, (80, 55, 40))
        self.assertEqual(moshi.shoe_color, (65, 45, 30))
        sprite = moshi.sprites["down"][0]
        self.assertEqual(sprite.get_at((5, 6))[:3], moshi.eye_color)
        self.assertNotEqual(sprite.get_at((4, 5))[:3], (50, 40, 30))
        for year in range(1, 5):
            self.assertTrue(moshi.is_present(year))
            for day in range(1, 6):
                for completed in (False, True):
                    pool = moshi.dialogues_after if completed else moshi.dialogues_before
                    self.assertIn((year, day), pool)
                    self.assertFalse(re.search(r"(?<!\.)\.(?!\.)", pool[(year, day)]))
        seats = [(cm.desk_x, cm.desk_y, cm.pc_offset) for cm in world.classmates]
        self.assertEqual(len(seats), len(set(seats)))

    def test_all_classmate_animation_states_and_portrait_render(self):
        from game.world import World
        from game.dialog import DialogBox
        world = World()
        screen = pygame.Surface((480, 300))
        self.course.day_task_completed = True
        moshi = next(cm for cm in world.classmates if cm.id == "moshi")
        world.finish_conversation(moshi, self.course)
        for state in ("studying", "packing", "shutdown", "standing", "walking", "exiting", "gone"):
            moshi.state = state
            world.draw(screen, 30, self.course, self.save)
        dialog = DialogBox(self.audio)
        dialog.show("Moshi", moshi.get_speech(1, 1, True), speaker="Moshi", portrait=moshi.sprites["down"][0])
        dialog.draw(screen)

    def test_every_classmate_has_side_hair_and_moshi_has_long_hair(self):
        from game.world import World
        for cm in World().classmates:
            for direction in ("left", "right"):
                for sprite in cm.sprites[direction]:
                    hair = [(x, y) for x in range(16) for y in range(1, 14)
                            if sprite.get_at((x, y))[:3] == cm.hair_color]
                    self.assertGreaterEqual(len(hair), 20, (cm.name, direction))
                    if cm.id == "moshi":
                        self.assertGreaterEqual(max(y for _, y in hair), 12)
            self.assertGreater(len(set(pygame.image.tobytes(sprite, "RGBA")
                                       for sprite in cm.sprites["right"])), 1)

    def test_studying_faces_screen_and_packing_has_moving_hands(self):
        from game.world import World
        world = World()
        # Comparar capturas con toda el aula conserva la animación de manos
        self.course.day_task_completed = True
        moshi = next(cm for cm in world.classmates if cm.id == "moshi")
        canvas = pygame.Surface((480, 300))
        world.draw(canvas, 0, self.course, self.save)
        self.assertEqual(canvas.get_at((moshi.px + 8, moshi.py + 11))[:3], moshi.hair_color)
        world.finish_conversation(moshi, self.course)
        world.draw(canvas, 0, self.course, self.save)
        first = pygame.image.tobytes(canvas, "RGBA")
        moshi.elapsed = 0.15
        world.draw(canvas, 0, self.course, self.save)
        self.assertNotEqual(first, pygame.image.tobytes(canvas, "RGBA"))

    def test_text_is_rendered_with_more_detail_than_upscaled_pixels(self):
        from game.rendering import Canvas, make_font, draw, DETAIL
        font = make_font(15)
        text = font.render("WHERE, ¿y el completito?", True, (240, 240, 240))
        canvas = Canvas((480, 300))
        canvas.fill((10, 15, 20))
        canvas.blit(text, (10, 10))
        self.assertEqual(canvas.get_size(), (480 * DETAIL, 300 * DETAIL))
        nearest = pygame.transform.scale(text, (text.get_width() * DETAIL, text.get_height() * DETAIL))
        actual = pygame.Surface.subsurface(canvas, pygame.Rect(30, 30, nearest.get_width(), nearest.get_height()))
        self.assertNotEqual(pygame.image.tobytes(actual, "RGB"), pygame.image.tobytes(nearest, "RGB"))
        canvas.set_clip(pygame.Rect(10, 10, 20, 20))
        draw.rect(canvas, (255, 0, 0), pygame.Rect(0, 0, 100, 100))
        self.assertEqual(canvas.get_at((31, 31))[:3], (255, 0, 0))
        self.assertEqual(canvas.get_at((1, 1))[:3], (10, 15, 20))
        canvas.set_clip(None)

    def test_full_hd_resolution_is_available_and_applied(self):
        from game.settings_menu import SettingsMenu
        config = Mock()
        config.get.side_effect = lambda key, default=None: default
        apply = Mock()
        menu = SettingsMenu(config, self.audio, apply)
        menu.temp_res_idx = menu.resolutions.index([1920, 1080])
        menu.apply_changes()
        apply.assert_called_once_with("windowed", [1920, 1080])
        config.set.assert_any_call("resolution", [1920, 1080])

    def test_rewritten_peers_have_complete_dialogues_without_sentence_periods(self):
        import re
        from game.world import World
        for cm in World().classmates:
            if cm.id in ("carlos", "moshi"):
                continue
            for year in range(cm.min_year, cm.max_year + 1):
                for day in range(1, 6):
                    for pool in (cm.dialogues_before, cm.dialogues_after):
                        self.assertIn((year, day), pool)
                        self.assertFalse(re.search(r"(?<!\.)\.(?!\.)", pool[(year, day)]), cm.name)

    def test_holding_arrow_repeats_until_release_without_repeating_enter(self):
        terminal = self.terminal
        terminal.open()
        terminal.input_text = "SELECT nombre FROM estudiantes"
        terminal.cursor_pos = len(terminal.input_text)
        end = terminal.cursor_pos
        terminal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, unicode=""))
        self.assertEqual(terminal.cursor_pos, end - 1)
        terminal.update(0.29)
        self.assertEqual(terminal.cursor_pos, end - 1)
        terminal.update(0.22)
        self.assertLess(terminal.cursor_pos, end - 3)
        terminal.handle_event(pygame.event.Event(pygame.KEYUP, key=pygame.K_LEFT))
        position = terminal.cursor_pos
        terminal.update(1)
        self.assertEqual(terminal.cursor_pos, position)
        with patch.object(terminal, "execute") as execute:
            terminal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="", mod=0))
            terminal.update(1)
            execute.assert_not_called()
            terminal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN, unicode="", mod=pygame.KMOD_CTRL))
            terminal.update(1)
            execute.assert_called_once()

    def test_repeat_stops_on_focus_loss_and_when_opening_notes(self):
        terminal = self.terminal
        terminal.open()
        terminal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_LEFT, unicode=""))
        terminal.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertIsNone(terminal.repeat_key)
        terminal.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT, unicode=""))
        terminal.update(0.5, enabled=False)
        self.assertIsNone(terminal.repeat_key)

    def test_caret_is_one_physical_pixel_wide_and_matches_text_height(self):
        from game.rendering import Canvas, draw_caret, DETAIL
        canvas = Canvas((40, 20))
        canvas.fill((0, 0, 0))
        rect = draw_caret(canvas, 5, 4, 7, (0, 255, 136))
        self.assertEqual(rect.width, 1)
        self.assertLessEqual(rect.height, 7 * DETAIL)
        self.assertEqual(canvas.get_at((15, 12))[:3], (0, 255, 136))
        self.assertEqual(canvas.get_at((16, 12))[:3], (0, 0, 0))

    def test_fitting_preserves_entire_names_and_values(self):
        from game.ui_helpers import fitted_text_layout, draw_sql_grid_table
        from game.rendering import make_font
        for text in ("notas_parcial", "estudiante_nombre", "Valentina Rojas", "123.45678"):
            font, lines = fitted_text_layout(text, make_font(12), 34)
            self.assertEqual("".join(lines).replace(" ", ""), text.replace(" ", ""))
            self.assertTrue(all(font.size(line)[0] <= 34 for line in lines))
        self.terminal.open()
        self.terminal.show_schema = True
        screen = pygame.Surface((480, 300))
        from game.ui_helpers import draw_fitted_text
        from game.visuals import button
        with patch("game.terminal.button", wraps=button) as fit:
            self.terminal.draw(screen, 0)
            labels = [call.args[1] for call in fit.call_args_list]
            self.assertIn("notas_parcial", labels)
            self.assertIn("estudiantes", labels)
        with patch("game.ui_helpers.draw_fitted_text", wraps=draw_fitted_text) as fit:
            draw_sql_grid_table(screen, pygame.Rect(20, 20, 400, 200),
                                ["estudiante_nombre", "nota"], [("Valentina Rojas", 6.12345)])
            labels = [call.args[1] for call in fit.call_args_list]
            self.assertIn("estudiante_nombre", labels)
            self.assertIn("Valentina Rojas", labels)
            self.assertIn("6.12345", labels)

    def test_music_follows_context_without_restarting_every_frame(self):
        from game.audio import AudioManager
        audio = AudioManager.__new__(AudioManager)
        audio.config = Mock()
        audio.config.get.return_value = 0.18
        audio.music_enabled = True
        audio.music_context = None
        audio.music_path = None
        with patch.object(pygame.mixer, "music") as music:
            for context in ("menu", "menu", "study", "study", "exam", "exam", "menu"):
                audio.set_music_context(context)
            paths = [call.args[0] for call in music.load.call_args_list]
            self.assertEqual([Path(path).name for path in paths],
                             ["bathroom_chill_loop.ogg", "alex_morgan_jazz_loop.ogg", "a_kind_of_hope.mp3", "bathroom_chill_loop.ogg"])
            self.assertEqual(music.play.call_count, 4)

    def test_verified_exercises_award_one_hundred_xp_and_persist(self):
        result = self.execute(self.course.get_current_task().canonical_query)
        self.assertTrue(result["success"])
        self.assertEqual(self.save.data["league"]["xp"], 100)
        self.assertIn("+100 XP", self.terminal.feedback_message)
        self.assertEqual(SaveSystem().data["league"]["xp"], 100)
        self.course.current_task_idx = 0
        self.execute(self.course.get_current_task().canonical_query)
        self.assertEqual(self.save.data["league"]["xp"], 100)

    def test_lesson_day_and_exam_rewards_are_not_repeatable(self):
        self.course.complete_lecture()
        self.course.complete_lecture()
        self.assertEqual(self.save.data["league"]["xp"], 50)
        self.course.day_task_completed = True
        self.course.finish_day()
        self.assertEqual(self.save.data["league"]["xp"], 200)
        self.course.current_day = 1
        self.course.finish_day()
        self.assertEqual(self.save.data["league"]["xp"], 200)
        self.course.current_day = 5
        self.course.exam_q_index = 4
        self.course.exam_score = 4
        self.course.advance_exam_question(True)
        self.assertEqual(self.save.data["league"]["xp"], 1200)
        self.course.exam_q_index = 4
        self.course.exam_score = 4
        self.course.advance_exam_question(True)
        self.assertEqual(self.save.data["league"]["xp"], 1200)

    def test_phone_purchase_battle_and_background_progress(self):
        from game.phone import StudentPhone
        from game.league import award_xp
        from game.rendering import Canvas
        phone = StudentPhone(self.save, self.audio)
        award_xp(self.save, 300, "test")
        phone.open()
        phone.update(0.3)
        screen = Canvas((480, 300))
        phone.draw(screen)
        phone.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_2))
        phone.draw(screen)
        phone.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(100, 95)))
        self.assertEqual(phone.game.level("vision"), 1)
        self.assertEqual(phone.game.state["xp"], 200)
        self.assertIn("jungla", phone.message)
        phone.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_1))
        phone.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN))
        self.assertIsNotNone(phone.game.state["battle"])
        phone.update(4)
        phone.draw(screen)
        phone.close()
        phone.update(phone.game.state['battle']['duration'])
        self.assertEqual(phone.game.state["matches"], 1)
        self.assertEqual(SaveSystem().data["league"]["matches"], 1)

    def test_phone_global_button_and_shortcut_do_not_steal_sql_letters(self):
        import main
        from game.phone import StudentPhone
        self.save.data["has_save"] = True
        self.save.data["lecture_done_for_day"] = True
        self.save.data["foundation"]["completed"] = True
        self.save.save()
        phone = StudentPhone(self.save, self.audio)

        def key(value, text=""):
            return pygame.event.Event(pygame.KEYDOWN, key=value, unicode=text, mod=0)

        events = [[key(pygame.K_RETURN)], [key(pygame.K_e)], [key(pygame.K_p, "p")],
                  [pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(620, 30))],
                  [key(pygame.K_ESCAPE)], [key(pygame.K_ESCAPE)], [key(pygame.K_p, "p")],
                  [key(pygame.K_ESCAPE)], [pygame.event.Event(pygame.QUIT)]]
        with patch.object(main, "DatabaseManager", return_value=self.db), \
                patch.object(main, "SaveSystem", return_value=self.save), \
                patch.object(main, "SQLTerminal", return_value=self.terminal), \
                patch.object(main, "StudentPhone", return_value=phone), \
                patch.object(phone, "open", wraps=phone.open) as opened, \
                patch.object(pygame, "quit"), \
                patch.object(pygame.event, "get", side_effect=events):
            with self.assertRaises(SystemExit):
                main.main()
        self.assertEqual(opened.call_count, 2)
        self.assertIn("p", self.terminal.input_text)
        self.assertFalse(phone.active)


if __name__ == "__main__":
    unittest.main()
