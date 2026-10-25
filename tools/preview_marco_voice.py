"""Muestras opcionales de Kokoro, fuera de las dependencias y el arranque del juego"""
from pathlib import Path
import argparse
import time
import urllib.request

MODEL_URL='https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.1/'
TEXT=('Hola, soy el profesor Marco. Bienvenidos a la semana introductoria.\n\n'
      'Antes de escribir una consulta, vamos a entender cómo se organizan los datos. Mira la pizarra.\n\n'
      'Cada fila representa a una persona. Cada columna describe una característica. '
      'Por ejemplo, Moshi es un valor de la columna "nombre".\n\n'
      'Si lo piensas como una lista de asistencia, cada estudiante ocupa una fila. '
      'Su nombre aparece en la columna correspondiente. Esa es la idea que vamos a trabajar.')


def load_engine(download=False):
    import onnxruntime as ort
    from kokoro_onnx import Kokoro
    root=Path(__file__).resolve().parents[1]
    folder=root/'.preview'/'voice_models'
    folder.mkdir(parents=True,exist_ok=True)
    for filename in ('kokoro-v1.0.onnx','voices-v1.0.bin'):
        path=folder/filename
        if not path.exists():
            if not download:raise FileNotFoundError(f'Falta {filename}, usa --download para descargar los modelos de prueba')
            print('Descargando '+filename,flush=True)
            temp=path.with_suffix('.part')
            urllib.request.urlretrieve(MODEL_URL+filename,temp)
            temp.replace(path)
    options=ort.SessionOptions()
    options.intra_op_num_threads=2
    options.inter_op_num_threads=1
    session=ort.InferenceSession(str(folder/'kokoro-v1.0.onnx'),sess_options=options,providers=['CPUExecutionProvider'])
    engine=Kokoro.from_session(session,str(folder/'voices-v1.0.bin'))
    return engine


def generate(download=False,voice='em_santa'):
    import soundfile as sf
    import numpy as np
    root=Path(__file__).resolve().parents[1]
    engine=load_engine(download)
    if voice not in engine.voices:raise ValueError('La voz solicitada no está disponible')
    start=time.monotonic()
    parts=[]
    for paragraph in TEXT.split('\n\n'):
        samples,rate=engine.create(paragraph,voice=voice,speed=.95,lang='es',sentence_pause=.45,clause_pause=.16)
        if parts:parts.append(np.zeros(round(rate*.55),dtype=np.float32))
        parts.append(samples)
    samples=np.concatenate(parts)
    output=root/'.preview'/f'marco_{voice}_puntuado.wav'
    sf.write(str(output),samples,rate)
    print(f'{output.name}: {len(samples)/rate:.1f}s de voz, {time.monotonic()-start:.1f}s de generación',flush=True)
    (root/'.preview'/'marco_voice_text_puntuado.txt').write_text(TEXT,encoding='utf8')


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--download',action='store_true')
    parser.add_argument('--voice',default='em_santa')
    args=parser.parse_args()
    generate(args.download,args.voice)
