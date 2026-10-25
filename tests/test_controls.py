import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
import pygame
from game.controls import ControlsOverlay,GUIDES
from game.rendering import Canvas


class ControlsTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.canvas=Canvas((480,300))
        self.canvas.fill((35,51,63))
        self.help=ControlsOverlay()

    def test_f10_toggles_and_does_not_pass_through_to_game(self):
        key=pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F10)
        self.assertTrue(self.help.handle_event(key,'SQL',self.canvas))
        self.assertTrue(self.help.active)
        self.assertEqual(self.help.context,'SQL')
        self.assertTrue(self.help.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),'SQL',self.canvas))
        self.assertTrue(self.help.active)
        self.assertTrue(self.help.handle_event(key,'SQL',self.canvas))
        self.assertFalse(self.help.active)
        self.assertFalse(self.help.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN),'SQL',self.canvas))

    def test_button_and_escape_consume_their_click_or_key(self):
        click=pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=self.help.rect.center)
        self.assertTrue(self.help.handle_event(click,'Clase',self.canvas))
        self.assertTrue(self.help.active)
        self.assertTrue(self.help.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),'Clase',self.canvas))
        self.assertFalse(self.help.active)

    def test_every_context_draws_without_accumulating_dim_or_changing_snapshot(self):
        original=pygame.image.tobytes(self.canvas,'RGB')
        for context in GUIDES:
            self.help.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F10),context,self.canvas)
            snapshot=pygame.image.tobytes(self.help.background,'RGB')
            self.help.draw(self.canvas)
            first=pygame.image.tobytes(self.canvas,'RGB')
            self.help.draw(self.canvas)
            self.assertEqual(first,pygame.image.tobytes(self.canvas,'RGB'),context)
            self.assertEqual(snapshot,pygame.image.tobytes(self.help.background,'RGB'),context)
            self.help.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE),context,self.canvas)
            pygame.Surface.blit(self.canvas,self.help.background,(0,0))
            self.assertEqual(original,pygame.image.tobytes(self.canvas,'RGB'))
