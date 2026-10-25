"""Genera un acompañamiento original suave, sin percusión, con bucle continuo."""
from pathlib import Path
import wave
import numpy as np


def generate(path):
    rate, duration = 22050, 32
    t = np.arange(rate * duration) / rate
    audio = np.zeros_like(t)
    chords = [(130.81, 164.81, 196.00, 246.94),
              (110.00, 130.81, 164.81, 196.00),
              (87.31, 110.00, 130.81, 164.81),
              (98.00, 123.47, 146.83, 196.00)]
    for index, chord in enumerate(chords):
        local = (t - index * 8) % duration
        envelope = np.where(local < 10, np.sin(np.pi * local / 10) ** 2, 0)
        for frequency in chord:
            frequency = round(frequency * duration) / duration
            tone = np.sin(2 * np.pi * frequency * t)
            tone += 0.12 * np.sin(2 * np.pi * frequency * 2 * t)
            audio += tone * envelope
    audio *= 0.18 / max(np.max(np.abs(audio)), 1)
    with wave.open(str(path), 'wb') as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes((audio * 32767).astype('<i2').tobytes())


if __name__ == '__main__':
    generate(Path(__file__).resolve().parents[1] / 'assets' / 'bgm_ambient.wav')
