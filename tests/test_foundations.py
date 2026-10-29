import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock, patch
import pygame
from game.data_model import DataModel, DEFAULT_FOUNDATION
from game.foundations import FoundationsScene
from game.foundations_content import DAYS
from game.modeler import VisualModeler
from game.rendering import Canvas
from game.save_system import SaveSystem, DEFAULT_SAVE


def workshop_model():
    model = DataModel()
    model.add_table('estudiantes')
    for name,kind,pk,nn in [('id','INTEGER',True,True),('nombre','TEXT',False,True),('promedio','REAL',False,False)]:
        model.set_column('estudiantes',dict(name=name,type=kind,pk=pk,not_null=nn))
    model.add_table('tutorias')
    model.set_column('tutorias',dict(name='id',type='INTEGER',pk=True))
    model.set_column('tutorias',dict(name='estudiante_id',type='INTEGER',not_null=True,reference=dict(table='estudiantes',column='id')))
    model.set_column('tutorias',dict(name='tema',type='TEXT'))
    return model


class DataModelTests(unittest.TestCase):
    def test_drawing_generates_executable_tables_and_foreign_keys(self):
        model = workshop_model()
        with closing(model.connection()) as conn:
            self.assertEqual(conn.execute('PRAGMA foreign_keys').fetchone(),(1,))
            self.assertEqual(conn.execute('PRAGMA foreign_key_list(tutorias)').fetchone()[2:5],('estudiantes','estudiante_id','id'))
        self.assertTrue(model.day_goal(5)[0])
        result = model.demonstrate_integrity()
        self.assertTrue(all(passed for _,passed in result['checks']))
        self.assertEqual(len(result['estudiantes']),1)
        self.assertEqual([r[1] for r in result['tutorias']],[1,1])

    def test_duplicate_keys_null_names_and_missing_parent_are_rejected(self):
        with closing(workshop_model().connection()) as conn:
            conn.execute("INSERT INTO estudiantes VALUES(1,'Moshi',6.8)")
            for sql in ["INSERT INTO estudiantes VALUES(1,'Otro',5)","INSERT INTO estudiantes VALUES(2,NULL,5)","INSERT INTO tutorias VALUES(1,999,'Tema')"]:
                with self.assertRaises(sqlite3.IntegrityError):
                    conn.execute(sql)
            conn.execute("INSERT INTO tutorias VALUES(1,1,'Tema')")
            conn.execute("INSERT INTO tutorias VALUES(2,1,'Otro tema')")
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM tutorias').fetchone(),(2,))

    def test_invalid_edit_rolls_back_and_names_are_validated(self):
        model = workshop_model()
        before = deepcopy(model.tables)
        with self.assertRaises(ValueError):
            model.set_column('tutorias',dict(name='estudiante_id',type='TEXT',reference=dict(table='estudiantes',column='id')),'estudiante_id')
        self.assertEqual(model.tables,before)
        for name in ['estudiantes','bad name','x); DROP TABLE estudiantes;','1tabla','']:
            with self.assertRaises(ValueError):
                model.add_table(name)

    def test_rename_updates_relations_and_prevents_orphans(self):
        model = workshop_model()
        model.rename_table('estudiantes','alumnos')
        model.set_column('alumnos',dict(name='codigo',type='INTEGER',pk=True),'id')
        ref = model.table('tutorias')['columns'][1]['reference']
        self.assertEqual(ref,dict(table='alumnos',column='codigo'))
        with self.assertRaises(ValueError):
            model.delete_table('alumnos')
        with self.assertRaises(ValueError):
            model.delete_column('alumnos','codigo')
        model.delete_column('tutorias','estudiante_id')
        model.delete_table('alumnos')
        self.assertIsNone(model.table('alumnos'))

    def test_foreign_key_requires_a_real_primary_key(self):
        model = workshop_model()
        with self.assertRaises(ValueError):
            model.set_column('tutorias',dict(name='otra',type='TEXT',reference=dict(table='estudiantes',column='nombre')))
        with self.assertRaises(ValueError):
            model.set_column('estudiantes',dict(name='segunda_pk',type='INTEGER',pk=True))

    def test_lesson_goals_are_progressive(self):
        model = DataModel()
        self.assertTrue(model.day_goal(1)[0])
        self.assertFalse(model.day_goal(2)[0])
        model.add_table('estudiantes')
        for name,kind in [('id','INTEGER'),('nombre','TEXT'),('promedio','REAL')]:
            model.set_column('estudiantes',dict(name=name,type=kind))
        self.assertTrue(model.day_goal(2)[0])
        self.assertFalse(model.day_goal(3)[0])
        model.set_column('estudiantes',dict(name='id',type='INTEGER',pk=True),'id')
        model.set_column('estudiantes',dict(name='nombre',type='TEXT',not_null=True),'nombre')
        self.assertTrue(model.day_goal(3)[0])
        self.assertFalse(model.day_goal(4)[0])


class FoundationSceneTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.audio=Mock()
        self.finish,self.exit=Mock(),Mock()
        self.scene=FoundationsScene(self.save,self.audio)
        self.scene.open(self.finish,self.exit)

    def test_room_has_five_computers_and_no_day_one_model_task(self):
        self.assertEqual(self.scene.mode,'room')
        self.assertTrue(self.scene.model_goal()[0])
        self.assertEqual(self.scene.moshi.name,'Moshi')
        self.assertEqual(len(self.scene.desks),5)
        self.assertEqual([p.name for p in self.scene.peers],['Carlos','Sofía','Matías'])
        self.scene.open_pc()
        self.assertTrue(self.scene.dialog.active)
        self.assertEqual(self.scene.mode,'room')
        self.scene.advance_day()
        self.assertEqual(self.scene.day,1)

    def test_escape_from_lecture_returns_safely_without_completing_it(self):
        self.scene.start_lecture()
        self.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(self.scene.mode,'room')
        self.assertFalse(self.scene.state['lectures'].get('1'))
        self.assertIn('1',self.scene.state['lecture_pages'])
        self.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(self.scene.mode,'pause')
        self.scene.leave()
        self.exit.assert_called_once()

    def test_five_days_require_kashut_and_current_model_test(self):
        from test_logical_studio import example_design
        from game.kashut_questions import QUESTIONS
        self.scene.design.data=example_design().data
        for day in range(1,6):
            self.scene.state['lectures'][str(day)]=True
            self.scene.kashut.open(day)
            for question in QUESTIONS[day]:
                self.scene.kashut.cooldown=0
                self.scene.kashut.answer(question[2])
            self.scene.kashut.next_review()
            if day==5:
                self.scene.advance_day()
                self.finish.assert_not_called()
                self.scene.test_workshop()
                self.assertEqual(self.scene.state['tested_sql'],self.scene.design.statements())
            self.scene.advance_day()
        self.finish.assert_called_once()
        self.assertTrue(self.scene.state['completed'])
        self.assertEqual((self.save.data['current_year'],self.save.data['current_day']),(1,1))

    def test_all_intro_speeches_and_diagrams_fit(self):
        from game.ui_helpers import wrap_text_lines
        canvas=Canvas((480,300))
        for day in range(1,6):
            self.scene.day=day
            self.scene.start_lecture()
            self.assertTrue(any(page.get('illustration') for page in self.scene.lecture.slides))
            for index,page in enumerate(self.scene.lecture.slides):
                lines=wrap_text_lines(page['turing'],self.scene.lecture.font_body,394)
                self.assertLessEqual(len(lines)*(self.scene.lecture.font_body.get_linesize()+2)-2,52)
                self.scene.lecture.slide_index=index
                self.scene.lecture.chalk_is_done=True
                self.scene.lecture.chalk_char_index=10000
                self.scene.draw(canvas)
            self.scene.after_lecture()
            self.scene.dialog.active=False
            self.scene.draw(canvas)

    def test_review_and_optional_skip_preserve_academic_progress(self):
        self.save.data.update(current_year=3,current_day=4,current_task_idx=2)
        self.scene.open(self.finish,self.exit,review=True)
        self.assertEqual(self.scene.mode,'studio')
        self.scene.skip()
        self.finish.assert_called_once()
        self.assertEqual((self.save.data['current_year'],self.save.data['current_day'],self.save.data['current_task_idx']),(3,4,2))

    def test_logical_design_and_partial_lecture_resume(self):
        from test_logical_studio import example_design
        self.scene.design.data=example_design().data
        self.scene.start_lecture()
        self.scene.lecture.slide_index=2
        self.scene.persist()
        restored=FoundationsScene(self.save,self.audio)
        restored.open(self.finish,self.exit)
        restored.start_lecture()
        self.assertEqual(restored.lecture.slide_index,2)
        self.assertEqual(restored.design.data,self.scene.design.data)
        restored.restart_lecture()
        self.assertEqual(restored.lecture.slide_index,0)


class FoundationSaveTests(unittest.TestCase):
    def test_escape_menu_return_can_continue_again(self):
        import main
        from game.database import DatabaseManager
        pygame.init()
        with tempfile.TemporaryDirectory() as folder:
            path=str(Path(folder)/'save.json')
            db=DatabaseManager(str(Path(folder)/'practice.db'));db.reset()
            def key(value):return pygame.event.Event(pygame.KEYDOWN,key=value,unicode='',mod=0)
            events=iter([[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],[key(pygame.K_DOWN)]*12+[key(pygame.K_RETURN)]]+
                        [[] for _ in range(21)]+[[key(pygame.K_ESCAPE)],'menu',[key(pygame.K_RETURN)],[pygame.event.Event(pygame.QUIT)]])
            def next_events():
                value=next(events)
                if value=='menu':
                    w,h=pygame.display.get_surface().get_size()
                    return [pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(w//2,int(135*h/300)))]
                return value
            open_scene=main.FoundationsScene.open
            with patch.dict('game.config.DEFAULT_CONFIG',{'creator_note_seen':True}), \
                    patch('game.save_system.SAVE_DIR',folder),patch('game.save_system.SAVE_FILE',path), \
                    patch.object(main,'DatabaseManager',return_value=db), \
                    patch.object(main.FoundationsScene,'open',autospec=True,side_effect=open_scene) as opened, \
                    patch.object(pygame.time,'Clock',return_value=Mock(tick=Mock(return_value=100))), \
                    patch.object(pygame,'quit'),patch.object(pygame.event,'get',side_effect=next_events):
                with self.assertRaises(SystemExit):main.main()
                self.assertEqual(opened.call_count,2)

    def test_old_saves_skip_intro_but_new_games_include_it(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/'save.json')
            with patch('game.save_system.SAVE_DIR',folder),patch('game.save_system.SAVE_FILE',path):
                Path(path).write_text(json.dumps(dict(has_save=True,current_year=3,current_day=2)),encoding='utf8')
                old = SaveSystem()
                self.assertTrue(old.data['foundation']['completed'])
                self.assertEqual(old.data['current_year'],3)
                old.reset_new_game('Test','neutral',0,0,0,0)
                self.assertFalse(old.data['foundation']['completed'])
                self.assertEqual(old.data['foundation']['tables'],[])
                self.assertFalse(SaveSystem().data['foundation']['completed'])

    def test_real_save_preserves_diagram_and_midweek_progress(self):
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/'save.json')
            with patch('game.save_system.SAVE_DIR',folder),patch('game.save_system.SAVE_FILE',path):
                save = SaveSystem()
                save.data['foundation'].update(day=4,tables=workshop_model().tables,answers={'1':True,'2':True,'3':True})
                save.save()
                restored = SaveSystem()
                self.assertEqual(restored.data['foundation'],save.data['foundation'])
                self.assertTrue(DataModel(restored.data['foundation']['tables']).day_goal(4)[0])

    def test_new_game_enters_intro_before_first_year_lecture(self):
        import main
        from game.database import DatabaseManager
        pygame.init()
        with tempfile.TemporaryDirectory() as folder:
            path = str(Path(folder)/'save.json')
            db = DatabaseManager(str(Path(folder)/'practice.db'))
            db.reset()
            def key(value):
                return pygame.event.Event(pygame.KEYDOWN,key=value,unicode='',mod=0)
            events = [[key(pygame.K_RETURN)],[key(pygame.K_ESCAPE)],
                      [key(pygame.K_DOWN)]*12+[key(pygame.K_RETURN)],
                      [pygame.event.Event(pygame.QUIT)]]
            open_scene = main.FoundationsScene.open
            with patch.dict('game.config.DEFAULT_CONFIG',{'creator_note_seen':True}), \
                    patch('game.save_system.SAVE_DIR',folder),patch('game.save_system.SAVE_FILE',path), \
                    patch.object(main,'DatabaseManager',return_value=db), \
                    patch.object(main.FoundationsScene,'open',autospec=True,side_effect=open_scene) as opened, \
                    patch.object(main.LectureScene,'start_lecture') as lecture, \
                    patch.object(pygame,'quit'),patch.object(pygame.event,'get',side_effect=events):
                with self.assertRaises(SystemExit):
                    main.main()
                opened.assert_called_once()
                lecture.assert_not_called()
                self.assertFalse(SaveSystem().data['foundation']['completed'])
