"""Regresiones del prólogo, ventanas, avisos y modelador"""
import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import sqlite3,tempfile,unittest
from pathlib import Path
from contextlib import closing
from copy import deepcopy
from unittest.mock import Mock,patch
import pygame
from game.save_system import DEFAULT_SAVE
from game.foundations import FoundationsScene
from game.logical_model import LogicalDesign
from game.character_customizer import CharacterCustomizer
from game.creator_note import CreatorNote,TEXT
from game.missions import MissionsOverlay
from game.kashut import Kashut,reward_for
from game.kashut_questions import QUESTIONS,DIAGRAMS
from game.rendering import Canvas
from game.lessons import lesson_units
from test_logical_studio import attr

class ReviewCorrectionsTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE));self.audio=Mock()
        self.scene=FoundationsScene(self.save,self.audio);self.scene.open(Mock(),Mock())

    def key(self,key,text=''):
        return pygame.event.Event(pygame.KEYDOWN,key=key,unicode=text,mod=0)

    def test_borderless_desktop_size_and_position_ignore_saved_window_size(self):
        from main import setup_display
        from pygame._sdl2.video import Window
        desktop=pygame.display.get_desktop_sizes()[0]
        for size in [(960,600),(1366,768),(1920,1080)]:
            self.assertEqual(setup_display('borderless',size).get_size(),desktop)
            self.assertEqual(Window.from_display_module().position,(0,0))
        self.assertEqual(setup_display('windowed',[960,600]).get_size(),(960,600))

    def test_lowercase_model_and_foreign_keys_work_without_case_duplicate_columns(self):
        design=LogicalDesign()
        design.save_entity(dict(name='ESTUDIANTE',attributes=[attr('id',uid=True),attr('nombre','VARCHAR'),attr('promedio')]))
        design.save_entity(dict(name='TUTORIA',attributes=[attr('id',uid=True),attr('tema','VARCHAR')]))
        design.save_relation(dict(name='ASISTE',source='ESTUDIANTE',target='TUTORIA',kind='1:N',transfer_key=True))
        with closing(design.connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE(id,nombre) VALUES(12,'Moshi')")
            conn.execute("INSERT INTO TUTORIA(id,tema,estudiante_id) VALUES(1,'Claves',12)")
            with self.assertRaises(sqlite3.IntegrityError):conn.execute('INSERT INTO TUTORIA(id,estudiante_id) VALUES(2,999)')
        self.scene.design.data=design.data;self.scene.day=2
        self.assertTrue(self.scene.model_goal()[0])
        entity=deepcopy(design.entity('ESTUDIANTE'));entity['attributes'].append(attr('ID'))
        with self.assertRaises(ValueError):design.save_entity(entity,'ESTUDIANTE')
        self.assertEqual(design.entity('ESTUDIANTE')['attributes'][0]['name'],'id')

    def test_apply_attribute_creates_clean_next_field_and_can_edit_existing(self):
        studio=self.scene.modeler;studio.create_entity();studio.tab='attributes'
        studio.attr.update(name='id',type='NUMERIC',scale=0,uid=True);studio.apply_attribute()
        self.assertEqual(studio.entity_draft['attributes'][0]['name'],'id')
        self.assertEqual(studio.attr['name'],'');self.assertIs(studio.focus[0],studio.attr)
        self.assertIsNone(studio.attribute_index)
        studio.select_attribute(0);studio.attr['precision']=8;studio.apply_attribute()
        self.assertEqual(len(studio.entity_draft['attributes']),1)
        self.assertEqual(studio.entity_draft['attributes'][0]['precision'],8)

    def test_missions_announce_new_steps_once_and_do_not_consume_t_or_f9(self):
        panel=MissionsOverlay();canvas=Canvas((480,300))
        self.assertEqual(len(panel.get_missions('foundations',None,self.scene,self.save)),1)
        panel.draw_button(canvas,'foundations',None,self.scene,self.save)
        self.assertTrue(panel.has_pending('foundations',None,self.scene,self.save))
        for key,text in [(pygame.K_t,'t'),(pygame.K_F9,'')]:self.assertFalse(panel.handle_event(self.key(key,text),'foundations'))
        panel.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=panel.rect.center),'foundations')
        self.assertFalse(panel.has_pending('foundations',None,self.scene,self.save))
        panel.close();self.scene.state['lectures']['1']=True
        self.assertTrue(panel.has_pending('foundations',None,self.scene,self.save))
        panel.draw_button(canvas,'foundations',None,self.scene,self.save);panel.open()
        self.assertFalse(MissionsOverlay().has_pending('foundations',None,self.scene,self.save))

    def test_held_arrows_repeat_and_stop_on_release_or_lost_focus(self):
        editor=CharacterCustomizer(self.audio,Mock());editor.open()
        editor.handle_event(self.key(pygame.K_DOWN));first=editor.selected_field;editor.update(.55)
        self.assertNotEqual(editor.selected_field,first)
        editor.handle_event(pygame.event.Event(pygame.KEYUP,key=pygame.K_DOWN))
        current=editor.selected_field;editor.update(2);self.assertEqual(editor.selected_field,current)
        editor.handle_event(self.key(pygame.K_UP));editor.handle_event(pygame.event.Event(pygame.WINDOWFOCUSLOST))
        self.assertIsNone(editor.repeat_key);editor.draw(Canvas((480,300)),12)
        from game.rendering import make_font
        from game.ui_helpers import fitted_text_layout
        title=make_font(19);title.set_bold(True)
        fitted,_=fitted_text_layout('Un título general bastante largo',title,100,height=20)
        self.assertLess(fitted.point_size,19)
        self.assertTrue(fitted.get_bold())

    def test_creator_letter_all_text_fits_and_is_remembered(self):
        values={};config=Mock()
        config.get.side_effect=lambda key,default=None:values.get(key,default)
        config.set.side_effect=lambda key,value:values.__setitem__(key,value)
        note=CreatorNote(config);self.assertTrue(note.active)
        for i in range(len(note.pages)):note.index=i;note.draw(Canvas((480,300)))
        self.assertEqual(''.join(''.join(note.pages).split()),''.join(TEXT.split()))
        note.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=note.close_rect.center))
        self.assertFalse(CreatorNote(config).active);self.assertIn('0% obligatorio',TEXT)

    def test_length_precision_affinity_and_later_grade_check_examples_are_real(self):
        design=LogicalDesign();short=attr('nombre','VARCHAR');short['length']=1
        design.save_entity(dict(name='ESTUDIANTE',attributes=[attr('id',uid=True),short]))
        with closing(design.connection()) as conn:
            conn.execute("INSERT INTO ESTUDIANTE VALUES(12,'A')")
            for value,name in [(13,'Ana'),(12345678901,'B'),(12.5,'B')]:
                with self.assertRaises(sqlite3.IntegrityError):conn.execute('INSERT INTO ESTUDIANTE VALUES(?,?)',(value,name))
        with closing(sqlite3.connect(':memory:')) as conn:
            for item in lesson_units(2,1):
                if item['sql']:conn.execute(item['sql'])
            for value in (1,7):conn.execute('INSERT INTO notas_demo(nota) VALUES(?)',(value,))
            for value in (0,8,None):
                with self.assertRaises(sqlite3.IntegrityError):conn.execute('INSERT INTO notas_demo(nota) VALUES(?)',(value,))
            conn.execute('CREATE TABLE afinidad(nota REAL)');conn.execute("INSERT INTO afinidad VALUES('6.5'),('pendiente')")
            self.assertEqual(conn.execute('SELECT typeof(nota) FROM afinidad').fetchall(),[('real',),('text',)])

    def test_fifty_feedback_screens_and_same_score_never_gives_duplicate_xp(self):
        canvas=Canvas((480,300));quiz=Kashut(self.save,self.audio,Mock())
        for day in range(1,6):
            self.assertEqual(len(DIAGRAMS[day]),len(QUESTIONS[day]));quiz.open(day)
            quiz.state['answers']=[(q[2]+1)%4 for q in QUESTIONS[day]];quiz.phase='review'
            for i in range(10):quiz.review_index=i;quiz.draw(canvas)
        quiz.open(2);quiz.restart()
        for q in QUESTIONS[2]:quiz.cooldown=0;quiz.answer(q[2])
        calls=self.save.award_league_xp.call_count;quiz.restart()
        for q in QUESTIONS[2]:quiz.cooldown=0;quiz.answer(q[2])
        self.assertEqual(quiz.state['xp_granted'],reward_for(10));self.assertEqual(self.save.award_league_xp.call_count,calls)
        with patch.object(quiz,'button',wraps=quiz.button) as buttons:
            quiz.draw(canvas)
        self.assertIn('Salir del Kashut',[call.args[1] for call in buttons.call_args_list])

    def test_side_profiles_keep_hair_and_animate_the_legs(self):
        from game.player import Player
        for style in range(5):
            player=Player(0,0,dict(hair_style=style))
            for side in ('left','right'):
                sprites=player.sprites[side]
                hair=sum(sprites[0].get_at((x,y))[:3]==(80,45,25) for x in range(16) for y in range(9))
                self.assertGreater(hair,7)
                a=pygame.image.tobytes(sprites[1].subsurface((0,16,16,4)),'RGBA')
                b=pygame.image.tobytes(sprites[3].subsurface((0,16,16,4)),'RGBA')
                self.assertNotEqual(a,b)

    def test_main_delivers_estudiante_and_lowercase_attribute_without_overlay_interference(self):
        import main
        from game.database import DatabaseManager
        from game.controls import ControlsOverlay
        with tempfile.TemporaryDirectory() as folder:
            data=Mock(data=deepcopy(DEFAULT_SAVE));data.exists.return_value=True
            data.data['has_save']=True;data.data['foundation']['day']=2
            db=DatabaseManager(str(Path(folder)/'practice.db'));db.reset()
            scene=FoundationsScene(data,self.audio);original=scene.open
            def opened(*args,**kwargs):
                original(*args,**kwargs);scene.day_intro_remaining=0;scene.mode='studio';scene.modeler.create_entity()
            scene.open=Mock(side_effect=opened);controls=ControlsOverlay();missions=MissionsOverlay()
            def click(x,y):return pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=(x*2,y*2))
            events=[[self.key(pygame.K_RETURN)],[click(130,100)],
                    [self.key(ord(c.lower()),c) for c in 'ESTUDIANTE'],[click(200,60)],[click(250,85)],
                    [self.key(ord(c),c) for c in 'fecha_nacimiento'],[self.key(pygame.K_F10)],[pygame.event.Event(pygame.QUIT)]]
            with (patch.dict('game.config.DEFAULT_CONFIG',{'creator_note_seen':True}),
                  patch('game.config.CONFIG_PATH',str(Path(folder)/'config.json')),
                  patch.object(main,'DatabaseManager',return_value=db),patch.object(main,'SaveSystem',return_value=data),
                  patch.object(main,'FoundationsScene',return_value=scene),patch.object(main,'ControlsOverlay',return_value=controls),
                  patch.object(main,'MissionsOverlay',return_value=missions),patch.object(missions,'draw_button',wraps=missions.draw_button) as icons,
                  patch.object(controls,'draw_button',wraps=controls.draw_button) as help_button,patch.object(pygame,'quit'),
                  patch.object(pygame.event,'get',side_effect=events)):
                with self.assertRaises(SystemExit):main.main()
            self.assertEqual(scene.modeler.entity_draft['name'],'ESTUDIANTE')
            self.assertEqual(scene.modeler.attr['name'],'fecha_nacimiento');self.assertFalse(controls.active)
            icons.assert_not_called();help_button.assert_not_called()
