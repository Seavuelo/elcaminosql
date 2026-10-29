import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from copy import deepcopy
from unittest.mock import Mock
import pygame
from game.phone import StudentPhone
from game.league import GODS
from game.league_art import ARENA,phone_launcher,portrait
from game.rendering import Canvas,make_font


class LeagueUITests(unittest.TestCase):
    def setUp(self):
        pygame.init();pygame.display.set_mode((960,600))
        self.save=Mock(data={});self.audio=Mock();self.phone=StudentPhone(self.save,self.audio)
        self.canvas=Canvas((480,300));self.phone.open();self.phone.update(.3)

    def click(self,pos):self.phone.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))

    def test_all_gods_are_clickable_and_have_distinct_portraits(self):
        self.phone.draw(self.canvas)
        cards=[(rect,action) for rect,action in self.phone.buttons if action[0]=='god']
        self.assertEqual(len(cards),9)
        snapshots=set()
        for rect,(_,god) in cards:
            self.click(rect.center)
            self.assertEqual(self.phone.game.state['god'],god)
            snapshots.add(pygame.image.tobytes(portrait(god,64),'RGBA'))
        self.assertEqual(len(snapshots),len(GODS))

    def test_tabs_and_button_bounds_work_without_changing_match_from_rendering(self):
        for tab in ('match','plan','upgrades'):
            self.phone.tab=tab;self.phone.draw(self.canvas)
            for rect,_ in self.phone.buttons:self.assertTrue(pygame.Rect(0,0,480,280).contains(rect))
        self.phone.game.start_battle(6)
        before=deepcopy(self.phone.game.state)
        for _ in range(4):self.phone.draw(self.canvas)
        self.assertEqual(self.phone.game.state,before)
        self.phone.tab='plan';self.phone.draw(self.canvas)
        self.assertFalse(any(action[0] in ('strategy','relic','battle') for _,action in self.phone.buttons))

    def test_keyboard_and_mouse_can_connect_once_and_return_to_study(self):
        for mouse in (False,True):
            self.phone.game.state['battle']=None;self.phone.game.start_battle(2)
            battle=self.phone.game.state['battle'];cue=battle['windows'][-1]
            battle['elapsed']=cue['at']+cue['windup']+cue['window']*.5
            self.phone.tab='match';self.phone.draw(self.canvas)
            before=battle['result']['kills']
            if mouse:self.click((ARENA.x+cue['pos'][0]*ARENA.width,ARENA.y+cue['pos'][1]*ARENA.height))
            else:self.phone.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
            self.assertEqual(battle['result']['kills'],before+1)
            self.phone.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_SPACE))
            self.assertEqual(battle['result']['kills'],before+1)
            self.phone.close();self.phone.update(100)
            self.assertIsNone(self.phone.game.state['battle'])
            self.assertEqual(self.phone.game.state['xp'],0)
            self.phone.open();self.phone.update(.3);self.phone.draw(self.canvas)
            self.assertTrue(self.phone.view_result)

    def test_whole_simulation_renders_including_respawn_and_end(self):
        self.phone.game.start_battle(11)
        for frame in range(86):
            self.phone.update(.5);self.phone.draw(self.canvas,frame)
        self.assertIsNone(self.phone.game.state['battle'])
        self.assertEqual(self.phone.game.state['matches'],1)
        phone_launcher(self.canvas,pygame.Rect(296,10,82,17),make_font(12),busy=True)
