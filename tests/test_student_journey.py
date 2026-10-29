"""Recorrido de fundamentos, tareas y cuatro módulos con el motor real"""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import sqlite3
import tempfile
import unittest
from contextlib import closing
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock
import pygame
from game.save_system import DEFAULT_SAVE
from game.foundations import FoundationsScene
from game.curriculum import UniversityCurriculum
from game.database import DatabaseManager
from game.terminal import SQLTerminal
from game.lessons import demonstration
from game.missions import MissionsOverlay
from game.rendering import Canvas,make_font
from game.ui_helpers import draw_fitted_text,fitted_text_layout
from game.kashut import reading_seconds
from test_logical_studio import example_design


class StudentJourneyTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.audio=Mock()
        self.scene=FoundationsScene(self.save,self.audio)
        self.scene.open(Mock(),Mock())

    def test_primary_key_and_foreign_key_examples_are_true_in_sqlite(self):
        with closing(example_design().connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(11,'Carlos',5)")
            conn.execute("INSERT INTO ESTUDIANTE VALUES(12,'Carlos',6)")
            self.assertEqual(conn.execute('SELECT COUNT(*) FROM ESTUDIANTE').fetchone(),(2,))
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO ESTUDIANTE VALUES(12,'Otro',5)")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO ESTUDIANTE VALUES(13,NULL,5)")
            conn.execute("INSERT INTO TUTORIA VALUES(20,'Claves',11)")
            conn.execute("INSERT INTO TUTORIA VALUES(21,'Tipos',11)")
            with self.assertRaises(sqlite3.IntegrityError):
                conn.execute("INSERT INTO TUTORIA VALUES(22,'Sin estudiante',999)")
            self.assertEqual(conn.execute('SELECT ESTUDIANTE_ID,COUNT(*) FROM TUTORIA GROUP BY ESTUDIANTE_ID').fetchall(),[(11,2)])

    def test_each_module_supports_a_concrete_prediction(self):
        greater=next(i for i in demonstration(1,2) if i['title']=='Comparar un promedio')
        inclusive=next(i for i in demonstration(1,2) if i['title']=='Incluir el valor del límite')
        self.assertEqual(set(inclusive['rows'])-set(greater['rows']),{('Valentina Rojas',5.5)})
        restored=demonstration(2,4)[-1]['rows']
        self.assertEqual([r[0] for r in restored],[1,2])
        self.assertEqual(restored[0][2],12.5)
        self.assertEqual(demonstration(3,4)[-1]['rows'],[(4,3)])
        left=next(i for i in demonstration(4,2) if i['title']=='Conservar también las ausencias')['rows']
        pending=next(i for i in demonstration(4,2) if i['title']=='Ausencia de relación o dato pendiente')['rows']
        self.assertEqual(sum(row[1] is None for row in left),9)
        self.assertTrue(any(row[1] is not None and row[2] is None for row in pending))

    def test_task_pages_reach_every_requirement_and_invalid_model_stays_pending(self):
        self.scene.day=5
        self.scene.open_task()
        self.scene.draw(Canvas((480,300)))
        buttons=self.scene.modeler.buttons
        self.scene.modeler.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(70,14)))
        self.assertEqual(self.scene.modeler.form,'task_modal')
        next_button=next((rect,callback) for rect,callback in buttons if rect.x==322 and rect.y==250)
        next_button[1]()
        self.scene.draw(Canvas((480,300)))
        self.assertEqual(self.scene.modeler.task_page,1)
        self.assertFalse(self.scene.task_checklist()['is_complete'])
        self.assertFalse(self.scene.model_goal()[0])
        self.scene.design.data=example_design().data
        self.scene.test_workshop()
        self.assertTrue(self.scene.task_checklist()['is_complete'])
        self.scene.design.entities[0]['attributes'][1]['length']=90
        self.assertFalse(self.scene.task_checklist()['is_complete'])

    def test_objectives_require_feedback_and_keep_phone_optional(self):
        overlay=MissionsOverlay()
        self.scene.state['lectures']['1']=True
        self.scene.state.setdefault('kashut',{})['1']=dict(complete=True,reviewed=False)
        missions=overlay.get_missions('foundations',None,self.scene,self.save)
        self.assertFalse(missions[2][1])
        self.assertFalse(any('Liga' in title for title,_,_ in missions))
        self.scene.state['kashut']['1']['reviewed']=True
        missions=overlay.get_missions('foundations',None,self.scene,self.save)
        self.assertTrue(all(done for _,done,_ in missions[:-1]))
        self.assertIn('Marco',missions[-1][0])

    def test_wrapping_keeps_readable_font_and_never_paints_outside_box(self):
        font=make_font(13)
        selected,lines=fitted_text_layout('Una explicación clara necesita espacio para leerse sin reducir toda la frase a una sola línea',font,160,height=65)
        self.assertEqual(selected.point_size,13)
        self.assertGreater(len(lines),1)
        surface=pygame.Surface((220,100));surface.fill((255,0,255))
        rect=pygame.Rect(20,20,150,25)
        draw_fitted_text(surface,'palabra '*200,rect,font)
        for point in [(19,20),(170,30),(30,45),(200,80)]:
            self.assertEqual(surface.get_at(point)[:3],(255,0,255))

    def test_quiz_gives_reading_time_without_speed_scoring(self):
        from game.kashut_questions import QUESTIONS
        for day in range(1,6):
            self.assertEqual(len(QUESTIONS[day]),10)
            for index,question in enumerate(QUESTIONS[day]):
                self.assertEqual(len(question[1]),4)
                self.assertIn(question[2],range(4))
                self.assertTrue(question[3])
                self.assertTrue(25<=reading_seconds(day,index)<=45)

    def test_all_four_years_can_be_completed_through_the_actual_terminal(self):
        with tempfile.TemporaryDirectory() as folder:
            db=DatabaseManager(str(Path(folder)/'practice.db'));db.reset()
            course=UniversityCurriculum(db,self.save,self.audio)
            terminal=SQLTerminal(db,self.audio,course)
            for year in range(1,5):
                for day in range(1,5):
                    self.assertEqual((course.current_year,course.current_day),(year,day))
                    course.complete_lecture()
                    for task in course.tasks[year,day]:
                        terminal.input_text=task.canonical_query
                        terminal.execute()
                        self.assertTrue(terminal.feedback_is_success,(year,day,task.title,terminal.feedback_message))
                    self.assertTrue(course.day_task_completed)
                    course.finish_day()
                for question in course.get_current_exam_questions():
                    terminal.input_text=question.canonical_query
                    terminal.execute(submit=True)
                    self.assertTrue(terminal.feedback_is_success,(year,question.title,terminal.feedback_message))
                self.assertEqual(course.exam_final_grade,7.0)
                course.advance_to_next_year()
            self.assertTrue(self.save.data['is_graduated'])
