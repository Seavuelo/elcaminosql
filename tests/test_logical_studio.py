import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import sqlite3
import unittest
from contextlib import closing
from unittest.mock import Mock
from copy import deepcopy
import pygame
from game.logical_model import LogicalDesign
from game.design_studio import DesignStudio
from game.rendering import Canvas
from game.kashut import Kashut,podium_rank,reward_for
from game.kashut_questions import QUESTIONS
from game.save_system import DEFAULT_SAVE
from game.notebook import StudentNotebook


def attr(name,kind='NUMERIC',uid=False,mandatory=False,scale=0):
    return dict(name=name,type=kind,uid=uid,mandatory=mandatory,length=80,precision=10,scale=scale)


def example_design(kind='1:N',identifying=False,transferable=True):
    design=LogicalDesign()
    design.save_entity(dict(name='ESTUDIANTE',attributes=[attr('ID',uid=True),attr('NOMBRE','VARCHAR',mandatory=True),attr('PROMEDIO',scale=2)],x=0,y=0))
    design.save_entity(dict(name='TUTORIA',attributes=[attr('ID',uid=True),attr('TEMA','VARCHAR')],x=350,y=30))
    design.save_relation(dict(name='ASISTE',source='ESTUDIANTE',target='TUTORIA',kind=kind,source_role='TIENE',target_role='PERTENECE',source_optional=False,target_optional=True,identifying=identifying,transfer_key=True,transferable=transferable))
    return design


class LogicalEngineTests(unittest.TestCase):
    def test_legacy_tables_migrate_without_losing_relations(self):
        from test_foundations import workshop_model
        original=workshop_model().tables
        before=deepcopy(original)
        design=LogicalDesign(legacy=original)
        self.assertEqual(original,before)
        self.assertEqual(len(design.relations),1)
        with closing(design.connection()) as conn:
            self.assertEqual(len(conn.execute('PRAGMA foreign_key_list(TUTORIAS)').fetchall()),1)
    def test_one_many_foreign_keys_reject_missing_parent(self):
        with closing(example_design().connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8)")
            conn.execute("INSERT INTO TUTORIA VALUES(1,'SQL',1)")
            conn.execute("INSERT INTO TUTORIA VALUES(2,'Modelos',1)")
            with self.assertRaises(sqlite3.IntegrityError):conn.execute("INSERT INTO TUTORIA VALUES(3,'Sin padre',999)")

    def test_one_one_adds_unique(self):
        with closing(example_design('1:1').connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8)")
            conn.execute("INSERT INTO TUTORIA VALUES(1,'SQL',1)")
            with self.assertRaises(sqlite3.IntegrityError):conn.execute("INSERT INTO TUTORIA VALUES(2,'Otra',1)")

    def test_many_many_creates_bridge_with_composite_key(self):
        design=example_design('N:M')
        tables,_=design.relational()
        bridge=next(t for t in tables if t['name']=='ASISTE')
        self.assertEqual(len(bridge['foreign_keys']),2)
        self.assertTrue(all(a['uid'] for a in bridge['columns']))
        with closing(design.connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8)")
            conn.execute("INSERT INTO TUTORIA VALUES(10,'SQL')")
            conn.execute('INSERT INTO ASISTE VALUES(1,10)')
            with self.assertRaises(sqlite3.IntegrityError):conn.execute('INSERT INTO ASISTE VALUES(1,10)')

    def test_identifying_migrates_only_primary_key(self):
        design=example_design(identifying=True)
        tables,_=design.relational()
        child=next(t for t in tables if t['name']=='TUTORIA')
        self.assertEqual([a['name'] for a in child['columns'] if a.get('uid')],['ID','ESTUDIANTE_ID'])
        self.assertNotIn('ESTUDIANTE_NOMBRE',[a['name'] for a in child['columns']])
        with closing(design.connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8)")
            conn.execute("INSERT INTO ESTUDIANTE VALUES(2,'Carlos',5)")
            conn.execute("INSERT INTO TUTORIA VALUES(1,'SQL',1)")
            conn.execute("INSERT INTO TUTORIA VALUES(1,'SQL',2)")

    def test_optional_and_nontransferable_are_real_constraints(self):
        design=example_design(transferable=False)
        design.relations[0]['source_optional']=True
        with closing(design.connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(1,'Moshi',6.8)")
            conn.execute("INSERT INTO ESTUDIANTE VALUES(2,'Carlos',5)")
            conn.execute("INSERT INTO TUTORIA VALUES(1,'SQL',NULL)")
            conn.execute('UPDATE TUTORIA SET ESTUDIANTE_ID=1 WHERE ID=1')
            with self.assertRaises(sqlite3.IntegrityError):conn.execute('UPDATE TUTORIA SET ESTUDIANTE_ID=2 WHERE ID=1')

    def test_no_transfer_key_has_no_fake_foreign_key(self):
        design=example_design()
        design.relations[0]['transfer_key']=False
        tables,warnings=design.relational()
        self.assertFalse(next(t for t in tables if t['name']=='TUTORIA')['foreign_keys'])
        self.assertIn('solo lógica',warnings[0])

    def test_minimum_children_is_not_claimed_as_sqlite_enforced(self):
        design=example_design()
        design.relations[0]['target_optional']=False
        self.assertIn('validación de proceso',design.relational()[1][0])

    def test_date_length_and_numeric_limits(self):
        design=LogicalDesign()
        design.save_entity(dict(name='EVENTO',x=0,y=0,attributes=[attr('ID',uid=True),dict(attr('NOMBRE','VARCHAR'),length=4),attr('FECHA','DATE'),dict(attr('PRECIO'),precision=4,scale=2)]))
        with closing(design.connection()) as conn:
            conn.execute("INSERT INTO EVENTO VALUES(1,'SQL','2026-10-24',12.50)")
            for sql in ["INSERT INTO EVENTO VALUES(2,'LARGO','2026-10-24',12)","INSERT INTO EVENTO VALUES(2,'SQL','2026-02-30',12)","INSERT INTO EVENTO VALUES(2,'SQL','fecha',12)","INSERT INTO EVENTO VALUES(2,'SQL','2026-10-24',123)","INSERT INTO EVENTO VALUES(2,'SQL','2026-10-24',1.234)"]:
                with self.assertRaises(sqlite3.IntegrityError,msg=sql):conn.execute(sql)

    def test_names_and_identifying_cycles_are_validated(self):
        design=example_design(identifying=True)
        for name in ['CON ESPACIO','NIÑO','TÍTULO','1TABLA']:
            with self.assertRaises(ValueError):design.save_entity(dict(name=name,attributes=[],x=0,y=0))
        rel=dict(design.relations[0],name='VUELTA',source='TUTORIA',target='ESTUDIANTE')
        rel.pop('id')
        design.save_relation(rel)
        with self.assertRaises(ValueError):design.relational()


class StudioTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.design=example_design()
        self.changed=Mock()
        self.studio=DesignStudio(self.design,self.changed)
        self.canvas=Canvas((480,300))

    def test_full_canvas_properties_zoom_and_views_render(self):
        self.studio.draw(self.canvas)
        self.assertLessEqual(max(r.right for r,_ in self.studio.buttons),480)
        self.studio.zoom_by(.3)
        self.assertGreaterEqual(self.studio.zoom,.2)
        self.studio.draw(self.canvas)
        self.studio.create_entity(self.design.entity('ESTUDIANTE'))
        self.studio.draw(self.canvas)
        self.studio.tab='attributes';self.studio.draw(self.canvas)
        self.studio.form=None
        self.studio.create_relation('ESTUDIANTE','TUTORIA','1:N',self.design.relations[0]);self.studio.draw(self.canvas)
        self.studio.form=None;self.studio.convert();self.studio.draw(self.canvas)
        self.assertIsNotNone(self.studio.relational_tables)

    def test_mouse_keyboard_entity_attributes_and_undo(self):
        studio=DesignStudio(LogicalDesign(),self.changed)
        def click(x,y):
            studio.draw(self.canvas)
            studio.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(x,y)))
        def key(value,text=''):
            studio.handle_event(pygame.event.Event(pygame.KEYDOWN,key=value,unicode=text,mod=0))
        click(68,15);click(180,100);key(pygame.K_e,'estudiante');key(pygame.K_RETURN)
        click(190,62);click(260,90);key(pygame.K_i,'id');key(pygame.K_RETURN)
        click(250,115);click(260,170);click(260,220);click(110,274)
        self.assertEqual(studio.design.entities[0]['name'],'ESTUDIANTE')
        self.assertTrue(studio.design.entities[0]['attributes'][0]['uid'])
        studio.undo();self.assertEqual(studio.design.entities,[])

    def test_relation_line_can_open_properties(self):
        self.studio.draw(self.canvas)
        points,rel=self.studio.lines[0]
        a,b=points[1],points[2]
        pos=(int((a[0]+b[0])/2),int((a[1]+b[1])/2))
        self.studio.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        self.assertEqual(self.studio.form,'relation')


class KashutTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.quiz=Kashut(self.save,Mock(),Mock())

    def play(self,score):
        self.quiz.open(1)
        for i,q in enumerate(QUESTIONS[1]):
            self.quiz.cooldown=0
            self.quiz.answer(q[2] if i<score else (q[2]+1)%4)

    def test_rank_thresholds_and_reward_no_farming(self):
        self.assertEqual([podium_rank(n) for n in [6,7,8,9,10]],[None,3,2,2,1])
        self.play(7)
        self.assertEqual(self.quiz.state['xp_granted'],reward_for(7))
        self.quiz.restart();self.play(7)
        self.assertEqual(self.save.award_league_xp.call_count,1)
        self.quiz.restart();self.play(10)
        self.assertEqual(self.save.award_league_xp.call_args.args[0],reward_for(10)-reward_for(7))

    def test_timer_pause_focus_loss_and_resume(self):
        self.quiz.open(1);self.quiz.update(5)
        self.quiz.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.quiz.update(100)
        self.assertEqual(self.quiz.remaining,20)
        restored=Kashut(self.save,Mock(),Mock());restored.open(1)
        self.assertEqual(restored.remaining,20)
        restored.update(26)
        self.assertEqual(restored.state['answers'],[None])

    def test_feedback_and_all_podium_views_render(self):
        canvas=Canvas((480,300))
        for score in [6,7,8,9,10]:
            if hasattr(self.quiz,'state'):self.quiz.restart()
            self.play(score);self.quiz.draw(canvas)
            self.quiz.next_review()
            if self.quiz.phase=='review':
                self.quiz.draw(canvas)
                self.assertFalse(self.quiz.state['reviewed'])
                for _ in self.quiz.wrong:self.quiz.next_review()
            self.assertTrue(self.quiz.state['reviewed'])
        for day in range(1,6):
            self.assertEqual(len(QUESTIONS[day]),10)
            self.quiz.open(day);self.quiz.draw(canvas)


class NotebookTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.save.data['foundation']['completed']=True
        self.notes=StudentNotebook(Mock(),self.save)
        self.notes.open()

    def test_section_and_accent_insensitive_keyword_search(self):
        self.notes.section='Modelo';self.notes.query='identificacion'
        result=self.notes.get_unlocked_notes()
        self.assertTrue(result)
        self.assertTrue(all(n['section']=='Modelo' for n in result))
        self.assertFalse(any(n['year']>1 for n in self.notes.get_unlocked_notes()))
        self.notes.section='Todo';self.notes.query='mi concepto'
        self.save.data['personal_notes']='Mi concepto de las relaciones'
        self.assertTrue(any(n['title']=='Mis notas' for n in self.notes.get_unlocked_notes()))

    def test_personal_notes_can_be_written_and_saved(self):
        self.notes.set_section('Mis notas')
        for key,text in [(pygame.K_h,'hola'),(pygame.K_RETURN,''),(pygame.K_n,'nombre no es UID')]:
            self.notes.handle_event(pygame.event.Event(pygame.KEYDOWN,key=key,unicode=text,mod=0))
        self.notes.close()
        self.assertEqual(self.save.data['personal_notes'],'hola\nnombre no es UID')
        self.notes.open();self.notes.draw(Canvas((480,300)))

    def test_illustrated_sections_render(self):
        canvas=Canvas((480,300))
        for section in ('Bases','Modelo'):
            self.notes.set_section(section)
            for page in range(len(self.notes.get_unlocked_notes())):
                self.notes.current_page=page;self.notes.draw(canvas)
