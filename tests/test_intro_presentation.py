import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from unittest.mock import Mock
from copy import deepcopy
import pygame
from game.foundations import FoundationsScene
from game.save_system import DEFAULT_SAVE
from game.rendering import Canvas
from game.learning_diagrams import illustration
from game.intro_peers import INTRO_NAMES,speech_for


class IntroPresentationTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.audio=Mock()
        self.scene=FoundationsScene(self.save,self.audio)
        self.scene.open(Mock(),Mock())

    def test_day_one_changes_the_board_instead_of_repeating_pipeline(self):
        self.scene.start_lecture()
        pages=self.scene.lecture.slides
        kinds={p.get('illustration') for p in pages}
        self.assertGreaterEqual(len(kinds),7)
        self.assertLessEqual(sum(p.get('illustration')=='pipeline' for p in pages),2)
        self.assertTrue(any('code_focus' in p for p in pages))
        speech=' '.join(p['turing'] for p in pages)
        for unwanted in ['Liga de Dioses','siete aciertos','tercer lugar','segundo','simulados']:
            self.assertNotIn(unwanted,speech)

    def test_concept_variants_are_visually_different(self):
        for kind in ['welcome','table','pipeline','types','entities','key','null','relation']:
            snapshots=[]
            for variant in [0,1]:
                canvas=Canvas((480,300));canvas.fill((20,50,36))
                illustration(canvas,kind,pygame.Rect(28,80,424,102),variant=variant)
                snapshots.append(pygame.image.tostring(canvas,'RGB'))
            self.assertNotEqual(*snapshots,kind)

    def test_chalk_reveals_diagram_then_stops_sound(self):
        self.scene.start_lecture()
        lecture=self.scene.lecture
        canvas=Canvas((480,300))
        lecture.draw(canvas)
        initial=pygame.image.tostring(canvas,'RGB')
        while not lecture.chalk_is_done:lecture.draw(canvas)
        self.assertNotEqual(initial,pygame.image.tostring(canvas,'RGB'))
        calls=self.audio.play_chalk.call_count
        for _ in range(60):lecture.draw(canvas)
        self.assertEqual(self.audio.play_chalk.call_count,calls)

    def test_day_card_lasts_two_seconds_and_does_not_skip_on_key(self):
        self.scene.day=2;self.scene.day_intro_remaining=2
        self.scene.draw(Canvas((480,300)))
        self.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(self.scene.mode,'room')
        self.scene.update(1.9)
        self.assertGreater(self.scene.day_intro_remaining,0)
        self.scene.update(.2)
        self.assertEqual(self.scene.day_intro_remaining,0)
        self.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(self.scene.mode,'pause')

    def test_classmates_and_quiz_share_the_same_attendees(self):
        self.assertEqual(set(INTRO_NAMES),{self.scene.moshi.name}|{p.name for p in self.scene.peers})
        for peer in self.scene.peers:
            for day in range(1,6):
                self.assertTrue(speech_for(peer.name,day,False))
                self.assertTrue(speech_for(peer.name,day,True))
            self.scene.speak_peer(peer)
            self.assertEqual(self.scene.dialog.speaker,peer.name)

    def test_five_desks_do_not_overlap_spawn_or_each_other(self):
        rectangles=[pygame.Rect(x,y,65,27) for x,y,_,_ in self.scene.desks]
        for index,rect in enumerate(rectangles):
            self.assertFalse(rect.colliderect(self.scene.player.get_rect()))
            self.assertFalse(any(rect.colliderect(other) for other in rectangles[index+1:]))
