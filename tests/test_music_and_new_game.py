import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import Mock
import numpy as np
import pygame
from game.save_system import DEFAULT_SAVE
from game.title_screen import TitleScreen
from game.rendering import Canvas
from tools.prepare_music_loop import circular_crossfade


class NewGameConfirmationTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.save.exists.return_value=True
        self.start=Mock()
        self.continue_game=Mock()
        self.title=TitleScreen(Mock(),self.save,self.continue_game,self.start,Mock(),Mock())
        self.title.selected_idx=1

    def key(self,value):
        self.title.handle_event(pygame.event.Event(pygame.KEYDOWN,key=value,unicode=''))

    def test_enter_cannot_accidentally_overwrite_save(self):
        before=deepcopy(self.save.data)
        self.key(pygame.K_RETURN)
        self.assertTrue(self.title.confirm_new_game)
        self.title.draw(Canvas((480,300)),0)
        self.assertEqual(self.title.confirmation_choice,0)
        self.key(pygame.K_RETURN)
        self.start.assert_not_called()
        self.assertTrue(self.title.active)
        self.assertEqual(self.save.data,before)
        self.save.save.assert_not_called()

    def test_escape_cancels_and_explicit_choice_starts_once(self):
        self.key(pygame.K_RETURN);self.key(pygame.K_ESCAPE)
        self.start.assert_not_called()
        self.key(pygame.K_RETURN);self.key(pygame.K_RIGHT);self.key(pygame.K_RETURN)
        self.start.assert_called_once()
        self.assertFalse(self.title.active)
        self.assertFalse(self.title.confirm_new_game)

    def test_mouse_requires_separate_confirm_click(self):
        def click(pos):self.title.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,button=1,pos=pos))
        click((200,158))
        self.start.assert_not_called()
        click((120,194))
        self.assertFalse(self.title.confirm_new_game)
        click((200,158));click((310,194))
        self.start.assert_called_once()

    def test_continue_and_first_game_do_not_have_false_loss_warning(self):
        self.title.selected_idx=0;self.key(pygame.K_RETURN)
        self.continue_game.assert_called_once()
        self.title.active=True
        self.save.exists.return_value=False
        self.title.selected_idx=0;self.key(pygame.K_RETURN)
        self.start.assert_called_once()


class MusicLoopTests(unittest.TestCase):
    def test_circular_join_continues_into_next_sample(self):
        t=np.linspace(0,30,10000)
        audio=np.column_stack((np.sin(t)*.3,np.cos(t)*.3)).astype(np.float32)
        overlap=400
        loop=circular_crossfade(audio,overlap)
        np.testing.assert_allclose(loop[0],audio[overlap])
        np.testing.assert_allclose(loop[-1],audio[overlap-1],atol=1e-7)
        np.testing.assert_allclose(loop[-overlap],audio[-overlap],atol=1e-7)
        self.assertEqual(len(loop),len(audio)-overlap)

    def test_overlap_keeps_peak_safe_and_rejects_short_audio(self):
        loop=circular_crossfade(np.ones((1000,2),dtype=np.float32),100)
        self.assertLessEqual(float(np.max(np.abs(loop))),.981)
        with self.assertRaises(ValueError):circular_crossfade(np.zeros((100,2)),60)

    def test_shipped_tracks_decode_and_loop_with_no_silent_boundary(self):
        pygame.init()
        root=Path(__file__).resolve().parents[1]/'assets'/'music'
        for name in ['alex_morgan_jazz_loop.ogg','bathroom_chill_loop.ogg']:
            path=root/name
            sound=pygame.mixer.Sound(str(path))
            samples=pygame.sndarray.array(sound).astype(np.float32)/32768
            window=44100//2
            seam=np.concatenate((samples[-window:],samples[:window]))
            self.assertGreater(float(np.sqrt(np.mean(seam**2))),.02)
            jump=float(np.max(np.abs(samples[0]-samples[-1])))
            ordinary=float(np.quantile(np.max(np.abs(np.diff(seam,axis=0)),axis=1),.99))
            self.assertLess(jump,ordinary)
            pygame.mixer.music.load(str(path))
            pygame.mixer.music.play(-1)
            self.assertTrue(pygame.mixer.music.get_busy())
            pygame.mixer.music.stop()
