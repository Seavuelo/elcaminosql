import os
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
import hashlib
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
import pygame
from game.database import DatabaseManager
from game.curriculum import UniversityCurriculum
from game.save_system import DEFAULT_SAVE
from copy import deepcopy
from game.terminal import SQLTerminal
from game.sql_syntax import tokenize, sql_width
from game.sql_editor import SQLBuffer
from game.lessons import demonstration, lesson_units, slides_for


class PedagogyTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.db = DatabaseManager(str(Path(self.temp.name)/'practice.db'))
        self.db.reset()
        self.save = Mock(data=deepcopy(DEFAULT_SAVE))
        self.audio = Mock()
        self.course = UniversityCurriculum(self.db,self.save,self.audio)
        self.terminal = SQLTerminal(self.db,self.audio,self.course)
        self.terminal.open()

    def key(self,key,mod=0,text=""):
        self.terminal.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key,mod=mod,unicode=text))

    def test_no_general_write_permission(self):
        for sql in ["UPDATE estudiantes SET promedio=1", "DELETE FROM materias", "CREATE TABLE trampa(id)"]:
            self.assertFalse(self.db.execute_query(sql,allow_write=True)['success'])
        self.assertEqual(self.db.execute_query('SELECT COUNT(*) FROM estudiantes')['rows'],[(12,)])

    def test_read_task_and_completed_day_deny_writes(self):
        for year,day,completed in [(3,1,False),(2,3,True),(4,3,True)]:
            self.course.current_year,self.course.current_day = year,day
            self.course.day_task_completed = completed
            self.terminal.input_text = "UPDATE estudiantes SET promedio=1"
            self.terminal.execute()
            self.assertFalse(self.terminal.last_result['success'])
        self.assertEqual(self.db.execute_query('SELECT promedio FROM estudiantes WHERE id=1')['rows'],[(6.2,)])

    def test_wrong_target_and_multistatement_rollback(self):
        canonical = "UPDATE estudiantes SET estado='Graduado' WHERE id=1"
        for sql in ["DELETE FROM profesores", canonical+'; DELETE FROM materias;',"UPDATE estudiantes SET estado='Graduado'"]:
            result = self.db.execute_query(sql,allow_write=True,expected_query=canonical)
            self.assertFalse(result['success'])
        self.assertEqual(self.db.execute_query('SELECT estado FROM estudiantes WHERE id=1')['rows'],[('Activo',)])
        self.assertEqual(self.db.execute_query('SELECT COUNT(*) FROM profesores')['rows'],[(3,)])

    def test_correct_preview_is_rolled_back(self):
        sql = "UPDATE estudiantes SET estado='Graduado' WHERE id=1"
        self.assertTrue(self.db.execute_query(sql,allow_write=True,expected_query=sql,commit=False)['success'])
        self.assertEqual(self.db.execute_query('SELECT estado FROM estudiantes WHERE id=1')['rows'],[('Activo',)])

    def test_seed_cannot_be_opened_as_practice(self):
        with self.assertRaises(ValueError):
            DatabaseManager(self.db.seed_path)

    def test_tokenizer_preserves_multiline_quotes_and_comments(self):
        sql = 'SELECT "a b", \'don\'\'t\', 1.5 >= 1 -- WHERE\nFROM [tabla] /* SELECT\nNULL */;'
        tokens = list(tokenize(sql))
        self.assertEqual(''.join(value for _,value in tokens),sql)
        self.assertIn(('string',"'don''t'"),tokens)
        self.assertIn(('identifier','"a b"'),tokens)
        self.assertIn(('operator','>='),tokens)
        self.assertIn(('comment','/* SELECT\nNULL */'),tokens)
        self.assertIn(('keyword','FROM'),tokens)

    def test_all_demonstrations_are_repeatable_and_leave_seed_unchanged(self):
        before = hashlib.sha256(Path(self.db.seed_path).read_bytes()).digest()
        for year in range(1,5):
            for day in range(1,5):
                result = demonstration(year,day)
                self.assertEqual(result,demonstration(year,day))
                self.assertTrue(any(item['sql'] and item['columns'] for item in result))
                self.assertTrue(any(item['check'] for item in result))
                self.assertTrue(all(item['speech'] for item in result))
        self.assertEqual(before,hashlib.sha256(Path(self.db.seed_path).read_bytes()).digest())

    def test_boundary_and_null_examples_have_expected_results(self):
        items = demonstration(1,2)
        self.assertNotIn(('Valentina Rojas',5.5),items[1]['rows'])
        self.assertIn(('Valentina Rojas',5.5),items[2]['rows'])
        self.assertEqual(demonstration(3,1)[1]['rows'],[(4,3)])
        self.assertEqual(demonstration(4,1)[3]['rows'],[(None,)])

    def test_table_pages_never_drop_rows(self):
        for year in range(1,5):
            for day in range(1,5):
                pages = slides_for(year,day)
                for item in demonstration(year,day):
                    rows = [row for page in pages if page['title']==item['title'] for row in page.get('table_rows',[])]
                    self.assertEqual(rows,item['rows'])

    def test_examples_do_not_duplicate_lab_solutions(self):
        def normalized(sql):
            return ''.join(value.upper() for kind,value in tokenize(sql) if kind not in ('space','comment','punctuation'))
        for key,tasks in self.course.tasks.items():
            examples = {normalized(item['sql']) for item in lesson_units(*key)}
            for task in tasks:
                self.assertNotIn(normalized(task.canonical_query),examples,key)

    def test_hints_are_progressive_and_do_not_advance(self):
        self.course.current_day=2
        task = self.course.get_current_task()
        self.assertNotIn(task.canonical_query,task.progressive_hint(1))
        self.assertNotIn('notas_parcial',task.progressive_hint(2))
        self.assertIn(task.canonical_query,task.progressive_hint(3))
        for level in range(1,4):
            self.key(pygame.K_F3)
            self.assertIn(f'Pista {level}/3',self.terminal.details.text)
            self.terminal.details.active=False
        self.assertEqual(self.course.current_task_idx,0)

    def test_exam_has_no_solution_hints(self):
        self.course.current_day=5
        self.key(pygame.K_F3)
        self.assertNotIn(self.course.get_current_exam_question().canonical_query,self.terminal.details.text)

    def test_editor_newlines_indentation_selection_and_delete(self):
        self.terminal.input_text='SELECT nombre'
        self.terminal.cursor_pos=len(self.terminal.input_text)
        self.key(pygame.K_RETURN)
        self.key(pygame.K_TAB)
        self.key(pygame.K_f,text='FROM estudiantes;')
        self.assertEqual(self.terminal.input_text,'SELECT nombre\n    FROM estudiantes;')
        self.key(pygame.K_HOME)
        self.key(pygame.K_END,pygame.KMOD_SHIFT)
        self.key(pygame.K_BACKSPACE)
        self.assertEqual(self.terminal.input_text,'SELECT nombre\n')

    def test_vertical_movement_preserves_preferred_column(self):
        buffer=SQLBuffer()
        text='abcdef\nx\nabcdef'
        cursor=buffer.move(text,5,'down')
        self.assertEqual(cursor,8)
        self.assertEqual(buffer.move(text,cursor,'down'),14)

    def test_exam_shortcuts_require_explicit_submission(self):
        self.course.current_day=5
        self.terminal.execute=Mock()
        self.key(pygame.K_RETURN)
        self.terminal.execute.assert_not_called()
        self.key(pygame.K_RETURN,pygame.KMOD_CTRL)
        self.terminal.execute.assert_called_with(submit=False)
        self.key(pygame.K_F5)
        self.terminal.execute.assert_called_with(submit=False)
        self.key(pygame.K_RETURN,pygame.KMOD_CTRL|pygame.KMOD_SHIFT)
        self.terminal.execute.assert_called_with(submit=True)

    def test_long_multiline_query_executes_as_one_statement(self):
        query = "SELECT\n nombre, promedio\nFROM estudiantes\nWHERE promedio > 5\nORDER BY promedio DESC"
        result=self.db.execute_query(query)
        self.assertTrue(result['success'])
        self.assertGreater(len(result['rows']),0)

    def test_code_fits_with_actual_bold_metrics(self):
        from game.rendering import make_font
        font=make_font(13)
        for year in range(1,5):
            for day in range(1,5):
                for item in lesson_units(year,day):
                    for line in item['sql'].splitlines():
                        self.assertLessEqual(sql_width(line,font),412,(year,day,line))

    def test_tab_indents_and_f2_opens_catalogue(self):
        before=self.terminal.input_text
        self.key(pygame.K_TAB)
        self.assertEqual(self.terminal.input_text,before+'    ')
        self.assertFalse(self.terminal.show_schema)
        self.key(pygame.K_F2)
        self.assertTrue(self.terminal.show_schema)
        self.key(pygame.K_F2)
        self.assertFalse(self.terminal.show_schema)

    def test_mouse_positions_cursor_and_f6_opens_full_results(self):
        from game.rendering import Canvas
        self.terminal.input_text='SELECT nombre\nFROM estudiantes;'
        self.terminal.cursor_pos=0
        self.terminal.last_result=self.db.execute_query(self.terminal.input_text)
        self.terminal.draw(Canvas((480,300)),0)
        rect=self.terminal.editor_rect
        self.terminal.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(rect.x,rect.y+self.terminal.font_code.get_linesize()+1)))
        self.assertEqual(self.terminal.cursor_pos,len('SELECT nombre\n'))
        self.key(pygame.K_F6)
        self.assertIn('Fila 12',self.terminal.details.text)

    def test_canonical_exercises_and_exams_are_preserved(self):
        self.assertEqual(sum(map(len,self.course.tasks.values())),64)
        self.assertEqual(sum(map(len,self.course.exams.values())),20)
