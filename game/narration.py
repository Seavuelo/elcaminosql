"""Reproduce una locución por diapositiva, sin cargar un modelo de IA"""
import json
from pathlib import Path
import pygame
from game.intro_voice_scripts import text_digest


class NarrationPlayer:
    def __init__(self,config,folder=None):
        self.config=config
        self.folder=Path(folder or Path(__file__).resolve().parents[1]/'assets'/'voice'/'marco_intro')
        self.entries={}
        try:
            entries=json.loads((self.folder/'manifest.json').read_text(encoding='utf8'))['entries']
            self.entries=entries if isinstance(entries,dict) else {}
        except (OSError,ValueError,KeyError):
            pass
        self.channel=None
        self.current_id=None
        self.sound=None
        self.paused=False
        self.failed=set()
        if pygame.mixer.get_init():
            pygame.mixer.set_reserved(1)
            self.channel=pygame.mixer.Channel(0)

    @property
    def enabled(self):
        return bool(self.config.get('narration_enabled',True))

    def stop(self):
        if self.channel:self.channel.stop()
        self.current_id=None
        self.sound=None
        self.paused=False
        self.restore_music()

    def restore_music(self):
        if pygame.mixer.get_init():
            pygame.mixer.music.set_volume(float(self.config.get('music_volume',.18)))

    def sync(self,slide):
        key=slide.get('narration_id')
        if not self.enabled or not key or not self.channel:
            if self.current_id:self.stop()
            return
        if key==self.current_id:return
        was_paused=self.paused
        self.stop()
        self.current_id=key
        entry=self.entries.get(key)
        if (not isinstance(entry,dict) or not isinstance(entry.get('file'),str)
                or text_digest(entry.get('display_text',''))!=text_digest(slide['turing'])
                or entry.get('narration_text')!=slide.get('narration_text')):
            return
        path=self.folder/entry['file']
        if path.parent!=self.folder:return
        try:
            self.sound=pygame.mixer.Sound(str(path))
            self.channel.set_volume(float(self.config.get('narration_volume',.85)))
            self.channel.play(self.sound)
            self.update(paused=was_paused)
        except (pygame.error,OSError) as exc:
            if key not in self.failed:
                print(f'[Narración] No se pudo reproducir {key}: {exc}')
                self.failed.add(key)

    def update(self,paused=False):
        if not self.channel:return
        if not self.enabled:
            self.stop();return
        if paused!=self.paused:
            self.channel.pause() if paused else self.channel.unpause()
            self.paused=paused
        self.channel.set_volume(float(self.config.get('narration_volume',.85)))
        talking=self.channel.get_busy() and not self.paused
        volume=float(self.config.get('music_volume',.18))
        if talking and float(self.config.get('narration_volume',.85))>0:volume*=.3
        pygame.mixer.music.set_volume(volume)

    def toggle(self):
        self.config.set('narration_enabled',not self.enabled)
        self.stop()
