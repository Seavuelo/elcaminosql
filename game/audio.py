import numpy as np
import pygame
import os

class AudioManager:
    """Gestiona la música de fondo lo-fi y los efectos de sonido satisfactorios."""
    def __init__(self, config_manager):
        self.config = config_manager
        self.music_enabled = False
        self.sfx_enabled = False
        
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
        except Exception as e:
            print(f"[AudioManager] Audio no disponible: {e}")

    def _to_stereo_sound(self, mono_pcm_float):
        """Convierte un array de audio float (-1.0 a 1.0) al formato requerido por Pygame mixer."""
        pcm_16 = (mono_pcm_float * 32767).astype(np.int16)
        if self.channels == 2:
            pcm_stereo = np.column_stack((pcm_16, pcm_16))
            return pygame.sndarray.make_sound(pcm_stereo)
        return pygame.sndarray.make_sound(pcm_16)

    def _setup_music(self):
        bgm_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "bgm_lofi.wav")
        if os.path.exists(bgm_path):
            try:
                pygame.mixer.music.load(bgm_path)
                vol = float(self.config.get("music_volume", 0.25))
                pygame.mixer.music.set_volume(vol)
                pygame.mixer.music.play(-1)
            except Exception as e:
                print(f"[AudioManager] Error cargando BGM: {e}")

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
        music_vol = float(self.config.get("music_volume", 0.25))
        try:
            pygame.mixer.music.set_volume(music_vol)
        except Exception:
            pass
        self._generate_sfx()

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
