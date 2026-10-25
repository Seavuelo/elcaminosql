"""Prepara un ciclo OGG con fundido circular, ffmpeg solo se usa al preparar assets"""
import argparse
import subprocess
from pathlib import Path
import numpy as np


def circular_crossfade(samples,overlap):
    if samples.ndim!=2 or overlap<2 or len(samples)<=2*overlap:
        raise ValueError('La pista debe tener dos canales y superar dos veces la transición')
    phase=np.linspace(0,np.pi/2,overlap,dtype=np.float64)[:,None]
    blend=samples[-overlap:]*np.cos(phase)+samples[:overlap]*np.sin(phase)
    # El ciclo termina en el inicio de la pista y continúa por la muestra siguiente.
    result=np.concatenate((samples[overlap:-overlap],blend)).astype(np.float32)
    peak=float(np.max(np.abs(result)))
    if peak>.98:result*=.98/peak
    return result


def prepare(source,target,seconds=6):
    rate=44100
    raw=subprocess.run(['ffmpeg','-v','error','-i',str(source),'-f','f32le','-ar',str(rate),'-ac','2','pipe:1'],check=True,capture_output=True).stdout
    samples=np.frombuffer(raw,dtype='<f4').reshape(-1,2)
    loop=circular_crossfade(samples,round(seconds*rate))
    Path(target).parent.mkdir(parents=True,exist_ok=True)
    subprocess.run(['ffmpeg','-v','error','-y','-f','f32le','-ar',str(rate),'-ac','2','-i','pipe:0','-c:a','libvorbis','-q:a','6',str(target)],input=loop.astype('<f4').tobytes(),check=True)
    print(f'{target}: {len(loop)/rate:.2f} s, transición circular {seconds:g} s, pico {np.max(np.abs(loop)):.3f}')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source')
    parser.add_argument('target')
    parser.add_argument('--seconds',type=float,default=6)
    args=parser.parse_args()
    prepare(args.source,args.target,args.seconds)
