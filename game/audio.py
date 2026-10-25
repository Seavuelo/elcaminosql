import numpy as np
import pygame
import os
from game.narration import NarrationPlayer

class AudioManager:
    """Gestiona la música de fondo lo-fi y los efectos de sonido satisfactorios."""
    def __init__(self, config_manager):
        self.config = config_manager
        self.music_enabled = False
        self.sfx_enabled = False
        self.music_context = None
        self.music_path = None
        self.narrator = None
        
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(44100, -16, 2, 512)
            
            mixer_info = pygame.mixer.get_init()
            self.sample_rate = mixer_info[0] if mixer_info else 44100
            self.channels = mixer_info[2] if mixer_info else 2
            
            self.sfx_enabled = True
            self.music_enabled = True
            self._generate_sfx()
            self._setup_music()
            self.narrator = NarrationPlayer(self.config)
        except Exception as e:
            self.sfx_enabled = False
            self.music_enabled = False
            print(f"[AudioManager] Audio no disponible: {e}")

    def _to_stereo_sound(self, mono_pcm_float):
        """Convierte un array de audio float (-1.0 a 1.0) al formato requerido por Pygame mixer."""
        pcm_16 = (mono_pcm_float * 32767).astype(np.int16)
        if self.channels == 2:
            pcm_stereo = np.column_stack((pcm_16, pcm_16))
            return pygame.sndarray.make_sound(pcm_stereo)
        return pygame.sndarray.make_sound(pcm_16)

    def _setup_music(self):
        self.set_music_context("menu")

    def set_music_context(self, context):
        if not self.music_enabled or context == self.music_context:
            return
        tracks = {"menu": "music/bathroom_chill_loop.ogg", "study": "music/alex_morgan_jazz_loop.ogg",
                  "exam": "music/a_kind_of_hope.mp3"}
        root = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets")
        path = os.path.join(root, tracks[context])
        self.music_context = context
        if not os.path.exists(path):
            print(f"[AudioManager] Falta la pista {tracks[context]}, se usa la música del menú")
            path = os.path.join(root, tracks["menu"])
        if path == self.music_path:
            return
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.set_volume(float(self.config.get("music_volume", 0.18)))
            pygame.mixer.music.play(-1, fade_ms=1500)
            self.music_path = path
        except pygame.error as error:
            print(f"[AudioManager] Error cargando música: {error}")

    def _generate_sfx(self):
        vol = float(self.config.get("sfx_volume", 0.70))

        # 1. Chime muy satisfactorio (Arpegio Mayor 9no brillante de cristal)
        notes = [523.25, 659.25, 783.99, 987.77, 1174.66]
        durs = [0.06, 0.06, 0.06, 0.06, 0.50]
        samples = []
        for f, d in zip(notes, durs):
            n_s = int(self.sample_rate * d)
            t = np.linspace(0, d, n_s, False)
            w = 0.6 * np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t) + 0.15 * np.sin(8 * np.pi * f * t)
            env = np.exp(-3.5 * t)
            samples.append(w * env * 0.35 * vol)
        self.snd_success = self._to_stereo_sound(np.concatenate(samples))

        # 2. Clic mecánico de teclado
        t_key = np.linspace(0, 0.02, int(self.sample_rate * 0.02), False)
        w_key = np.sign(np.sin(2 * np.pi * 550 * t_key)) * np.exp(-30 * t_key) * 0.12 * vol
        self.snd_key = self._to_stereo_sound(w_key)

        # 3. Error suave
        t_err = np.linspace(0, 0.15, int(self.sample_rate * 0.15), False)
        w_err = 0.5 * np.sin(2 * np.pi * 140 * t_err) * np.exp(-4 * t_err) * 0.25 * vol
        self.snd_error = self._to_stereo_sound(w_err)

        # 4. Tiza en pizarra
        t_chalk = np.linspace(0, 0.06, int(self.sample_rate * 0.06), False)
        noise = np.random.uniform(-0.15, 0.15, len(t_chalk)) * (1.0 - np.exp(-20 * t_chalk)) * vol
        self.snd_chalk = self._to_stereo_sound(noise)

        # 5. Campana de final de clase
        t_bell = np.linspace(0, 0.6, int(self.sample_rate * 0.6), False)
        w_bell = (0.5 * np.sin(2 * np.pi * 880 * t_bell) + 0.3 * np.sin(2 * np.pi * 1760 * t_bell)) * np.exp(-3 * t_bell) * 0.3 * vol
        self.snd_bell = self._to_stereo_sound(w_bell)

    def update_volumes(self):
        music_vol = float(self.config.get("music_volume", 0.18))
        try:
            pygame.mixer.music.set_volume(music_vol)
        except Exception:
            pass
        if self.sfx_enabled:
            self._generate_sfx()
        if getattr(self,'narrator',None):self.narrator.update()

    def play_narration(self,slide):
        if self.narrator:self.narrator.sync(slide)

    def stop_narration(self):
        if self.narrator:self.narrator.stop()

    def update_narration(self,paused=False):
        if self.narrator:self.narrator.update(paused)

    def toggle_narration(self):
        if self.narrator:self.narrator.toggle()

    def repeat_narration(self,slide):
        self.stop_narration()
        self.play_narration(slide)

    def play_success(self):
        if self.sfx_enabled and hasattr(self, 'snd_success'):
            self.snd_success.play()

    def play_key(self):
        if self.sfx_enabled and hasattr(self, 'snd_key'):
            self.snd_key.play()

    def play_error(self):
        if self.sfx_enabled and hasattr(self, 'snd_error'):
            self.snd_error.play()

    def play_chalk(self):
        if self.sfx_enabled and hasattr(self, 'snd_chalk'):
            self.snd_chalk.play()

    def play_bell(self):
        if self.sfx_enabled and hasattr(self, 'snd_bell'):
            self.snd_bell.play()
