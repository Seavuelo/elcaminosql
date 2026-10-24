import numpy as np
import pygame

class SoundManager:
    """Generador procedural de efectos de sonido chiptune retro (8-bit) usando NumPy y Pygame."""
    def __init__(self):
        self.enabled = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(22050, -16, 1, 512)
            self.sample_rate = 22050
            self.enabled = True
            self._generate_sounds()
        except Exception as e:
            print(f"[SoundManager] Audio no disponible: {e}")
            self.enabled = False

    def _synth_wave(self, freq_list, durations, wave_type="square", volume=0.2):
        """Genera una onda de sonido combinada a partir de frecuencias y duraciones."""
        if not self.enabled:
            return None
        total_samples = []
        for freq, dur in zip(freq_list, durations):
            num_samples = int(self.sample_rate * dur)
            t = np.linspace(0, dur, num_samples, False)
            if wave_type == "square":
                w = np.sign(np.sin(2 * np.pi * freq * t))
            elif wave_type == "sine":
                w = np.sin(2 * np.pi * freq * t)
            elif wave_type == "triangle":
                w = 2 * np.abs(2 * (t * freq - np.floor(t * freq + 0.5))) - 1
            elif wave_type == "noise":
                w = np.random.uniform(-1, 1, num_samples)
            else:
                w = np.sin(2 * np.pi * freq * t)
            
            # Envelope simple (fade out leve)
            env = np.linspace(1.0, 0.1, num_samples)
            total_samples.append(w * env * volume)
            
        full_wave = np.concatenate(total_samples)
        sound_array = (full_wave * 32767).astype(np.int16)
        return pygame.sndarray.make_sound(sound_array)

    def _generate_sounds(self):
        # 1. Tecla de teclado (Click mecánico retro)
        self.snd_key = self._synth_wave([600, 300], [0.015, 0.015], wave_type="square", volume=0.08)
        
        # 2. Éxito de misión (Fanfarria ascendente)
        self.snd_success = self._synth_wave(
            [392, 523, 659, 784, 1046], # G4, C5, E5, G5, C6
            [0.08, 0.08, 0.08, 0.10, 0.25], 
            wave_type="square", volume=0.25
        )
        
        # 3. Error en SQL (Buzzer grave descendente)
        self.snd_error = self._synth_wave(
            [220, 164, 110], 
            [0.08, 0.08, 0.15], 
            wave_type="triangle", volume=0.22
        )
        
        # 4. Abrir terminal / Ordenador
        self.snd_open = self._synth_wave(
            [440, 880], 
            [0.04, 0.08], 
            wave_type="sine", volume=0.18
        )
        
        # 5. Voz de NPC (Bleep de diálogo)
        self.snd_talk = self._synth_wave(
            [320], 
            [0.03], 
            wave_type="triangle", volume=0.10
        )

    def play_key(self):
        if self.enabled and hasattr(self, 'snd_key') and self.snd_key:
            self.snd_key.play()

    def play_success(self):
        if self.enabled and hasattr(self, 'snd_success') and self.snd_success:
            self.snd_success.play()

    def play_error(self):
        if self.enabled and hasattr(self, 'snd_error') and self.snd_error:
            self.snd_error.play()

    def play_open(self):
        if self.enabled and hasattr(self, 'snd_open') and self.snd_open:
            self.snd_open.play()

    def play_talk(self):
        if self.enabled and hasattr(self, 'snd_talk') and self.snd_talk:
            self.snd_talk.play()
