import os
os.environ.setdefault('SDL_VIDEODRIVER','dummy')
os.environ.setdefault('SDL_AUDIODRIVER','dummy')
import json
import tempfile
import unittest
from pathlib import Path
from copy import deepcopy
from unittest.mock import Mock,patch
import pygame
from game.narration import NarrationPlayer
from game.foundations import FoundationsScene
from game.save_system import DEFAULT_SAVE
from game.rendering import Canvas
from game.intro_voice_scripts import SCRIPTS,text_digest


class NarrationPlaybackTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.folder=Path(self.temp.name)
        self.values=dict(narration_enabled=True,narration_volume=.8,music_volume=.2)
        self.config=Mock()
        self.config.get.side_effect=lambda key,default=None:self.values.get(key,default)
        self.config.set.side_effect=lambda key,value:self.values.__setitem__(key,value)
        self.slides=[dict(narration_id='one',turing='Hola, soy Marco',narration_text='Hola. Soy Marco.'),dict(narration_id='two',turing='Mira la pizarra',narration_text='Mira la pizarra.')]
        entries={s['narration_id']:dict(display_text=s['turing'],narration_text=s['narration_text'],file=s['narration_id']+'.ogg') for s in self.slides}
        (self.folder/'manifest.json').write_text(json.dumps(dict(entries=entries)),encoding='utf8')
        self.channel=Mock()
        self.channel.get_busy.return_value=True
        patches=[patch.object(pygame.mixer,'get_init',return_value=(44100,-16,2)),patch.object(pygame.mixer,'set_reserved'),patch.object(pygame.mixer,'Channel',return_value=self.channel),patch.object(pygame.mixer,'Sound'),patch.object(pygame.mixer,'music')]
        self.sound=patches[3].start();self.addCleanup(patches[3].stop)
        self.music=patches[4].start();self.addCleanup(patches[4].stop)
        for item in patches[:3]:item.start();self.addCleanup(item.stop)
        self.player=NarrationPlayer(self.config,self.folder)

    def test_same_page_plays_once_and_next_page_replaces_it(self):
        for _ in range(5):self.player.sync(self.slides[0])
        self.channel.play.assert_called_once()
        self.sound.assert_called_once()
        self.player.sync(self.slides[1])
        self.assertEqual(self.channel.play.call_count,2)
        self.assertEqual(self.player.current_id,'two')
        self.player.stop()
        self.assertIsNone(self.player.current_id)
        self.music.set_volume.assert_called_with(.2)

    def test_mute_reenable_and_pause_restore_music(self):
        self.player.sync(self.slides[0])
        self.music.set_volume.assert_called_with(.06)
        self.player.update(paused=True)
        self.channel.pause.assert_called_once()
        self.music.set_volume.assert_called_with(.2)
        self.player.update(paused=False)
        self.channel.unpause.assert_called_once()
        self.player.toggle()
        self.assertFalse(self.values['narration_enabled'])
        count=self.channel.play.call_count
        self.player.sync(self.slides[0]);self.assertEqual(self.channel.play.call_count,count)
        self.player.toggle();self.player.sync(self.slides[0])
        self.assertEqual(self.channel.play.call_count,count+1)

    def test_finished_voice_and_zero_volume_do_not_duck_music(self):
        self.player.sync(self.slides[0])
        self.channel.get_busy.return_value=False
        self.player.update();self.music.set_volume.assert_called_with(.2)
        self.channel.get_busy.return_value=True
        self.values['narration_volume']=0
        self.player.update();self.music.set_volume.assert_called_with(.2)

    def test_missing_stale_or_malformed_entry_does_not_read_wrong_text(self):
        for entry in [None,{},dict(file='one.ogg',display_text='Otro texto',narration_text='Hola. Soy Marco.')]:
            self.player.entries['one']=entry
            self.player.stop();self.player.sync(self.slides[0])
        self.channel.play.assert_not_called()
        self.player.sync(dict(turing='Clase del año 1'))
        self.assertIsNone(self.player.current_id)

    def test_new_page_respects_existing_pause(self):
        self.player.update(paused=True)
        self.player.sync(self.slides[0])
        self.assertTrue(self.player.paused)
        self.music.set_volume.assert_called_with(.2)


class IntroVoiceIntegrationTests(unittest.TestCase):
    def setUp(self):
        pygame.init()
        self.audio=Mock()
        self.save=Mock(data=deepcopy(DEFAULT_SAVE))
        self.scene=FoundationsScene(self.save,self.audio)
        self.scene.open(Mock(),Mock())

    def test_each_intro_page_has_separate_script_without_changing_visible_style(self):
        count=0
        for day in range(1,6):
            self.scene.day=day;self.scene.start_lecture()
            self.assertEqual(len(self.scene.lecture.slides),len(SCRIPTS[day]))
            for slide in self.scene.lecture.slides:
                self.assertIn('narration_id',slide)
                self.assertTrue(slide['narration_text'].endswith('.'))
                self.assertNotEqual(slide['narration_text'],slide['turing'])
                count+=1
        self.assertEqual(count,69)
        self.scene.day=1;self.scene.start_lecture()
        self.assertIn('Marco, estas clases',self.scene.lecture.slides[0]['turing'])
        self.assertIn('Marco. Estas clases',self.scene.lecture.slides[0]['narration_text'])

    def test_navigation_repeat_toggle_and_escape_stop_the_clip(self):
        self.scene.start_lecture()
        lecture=self.scene.lecture
        lecture.chalk_is_done=True
        self.audio.reset_mock()
        lecture.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F8))
        self.audio.repeat_narration.assert_called_once_with(lecture.slides[0])
        lecture.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_F7))
        self.audio.toggle_narration.assert_called_once()
        lecture.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RIGHT))
        self.audio.stop_narration.assert_called_once()
        self.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_ESCAPE))
        self.assertEqual(self.scene.mode,'room')
        self.assertEqual(self.audio.stop_narration.call_count,2)

    def test_settings_offer_independent_voice_controls_and_fit(self):
        from game.settings_menu import SettingsMenu
        values={}
        config=Mock()
        config.get.side_effect=lambda key,default=None:values.get(key,default)
        config.set.side_effect=lambda key,value:values.__setitem__(key,value)
        menu=SettingsMenu(config,self.audio,Mock());menu.open()
        menu.selected_idx=menu.items.index('narration_enabled')
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_RETURN))
        self.assertFalse(values['narration_enabled'])
        menu.selected_idx=menu.items.index('narration_volume')
        menu.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_LEFT))
        self.assertEqual(values['narration_volume'],.8)
        self.assertNotIn('music_volume',values)
        menu.draw(Canvas((480,300)))
        opened=Mock();self.scene.on_settings=opened
        self.scene.start_lecture()
        self.scene.handle_event(pygame.event.Event(pygame.KEYDOWN,key=pygame.K_o))
        opened.assert_called_once()

    def test_pronunciation_preparation_does_not_modify_visible_sql(self):
        from tools.build_intro_narration import synthesis_text
        self.assertEqual(synthesis_text('SQLite usa SQL y UID.'),'ese cu ele láit usa ese cu ele y u i de.')

    def test_all_shipped_clips_match_scripts_and_decode(self):
        folder=Path(__file__).resolve().parents[1]/'assets'/'voice'/'marco_intro'
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
        entries=manifest['entries']
        self.assertEqual(manifest['voice'],'em_santa')
        self.assertEqual(len(entries),69)
        for day in range(1,6):
            self.scene.day=day;self.scene.start_lecture()
            for slide in self.scene.lecture.slides:
                entry=entries[slide['narration_id']]
                self.assertEqual(text_digest(slide['turing']),text_digest(entry['display_text']))
                self.assertEqual(slide['narration_text'],entry['narration_text'])
                sound=pygame.mixer.Sound(str(folder/entry['file']))
                self.assertGreater(sound.get_length(),2)
                self.assertAlmostEqual(sound.get_length(),entry['duration'],delta=.08)
