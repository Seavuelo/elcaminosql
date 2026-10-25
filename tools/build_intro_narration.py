"""Exporta textos con el entorno del juego y genera voces en el entorno de preparación"""
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
SOURCE=ROOT/'.preview'/'intro_voice_source.json'
OUTPUT=ROOT/'assets'/'voice'/'marco_intro'
PRONUNCIATIONS={
 'SQLite':'ese cu ele láit','SQL':'ese cu ele','SELECT':'select','FROM':'from',
 'INTEGER':'ínteyer','TEXT':'text','REAL':'real','VARCHAR':'var char',
 'NUMERIC':'niúmeric','DATE':'deit','BLOB':'blob','NULL':'nul',
 'PRIMARY KEY':'práimari ki','FOREIGN KEY':'fórin ki','UID':'u i de',
 'PK':'pe ka','FK':'efe ka','NN':'ene ene','CREATE TABLE':'crieit téibol',
}


def synthesis_text(text):
    pattern=r'\b('+ '|'.join(re.escape(key) for key in sorted(PRONUNCIATIONS,key=len,reverse=True))+r')\b'
    return re.sub(pattern,lambda match:PRONUNCIATIONS[match.group()],text)


def export():
    os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ['SDL_AUDIODRIVER']='dummy'
    import pygame
    from copy import deepcopy
    from unittest.mock import Mock
    from game.save_system import DEFAULT_SAVE
    from game.foundations import FoundationsScene
    pygame.init()
    scene=FoundationsScene(Mock(data=deepcopy(DEFAULT_SAVE)),Mock())
    scene.open(Mock(),Mock())
    entries=[]
    for day in range(1,6):
        scene.day=day;scene.start_lecture()
        for slide in scene.lecture.slides:
            entries.append(dict(id=slide['narration_id'],day=day,title=slide['title'],display_text=' '.join(slide['turing'].split()),narration_text=slide['narration_text']))
    SOURCE.parent.mkdir(parents=True,exist_ok=True)
    SOURCE.write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf8')
    pygame.quit()
    print(f'{len(entries)} guiones exportados',flush=True)


def generate():
    from tools.preview_marco_voice import load_engine
    import soundfile as sf
    import numpy as np
    engine=load_engine()
    entries=json.loads(SOURCE.read_text(encoding='utf8'))
    OUTPUT.mkdir(parents=True,exist_ok=True)
    manifest=dict(voice='em_santa',engine='Kokoro-82M',speed=.95,sentence_pause=.45,clause_pause=.16,entries={})
    started=time.monotonic()
    for i,entry in enumerate(entries,1):
        spoken=synthesis_text(entry['narration_text'])
        signature=hashlib.sha256(json.dumps([entry['display_text'],entry['narration_text'],spoken,'em_santa',.95,.45,.16],ensure_ascii=False).encode('utf8')).hexdigest()[:16]
        filename=entry['id']+'_'+signature+'.ogg'
        target=OUTPUT/filename
        if not target.exists():
            samples,rate=engine.create(spoken,voice='em_santa',speed=.95,lang='es',sentence_pause=.45,clause_pause=.16)
            if not len(samples) or not np.isfinite(samples).all():raise ValueError('El motor produjo audio vacío o inválido')
            samples=np.concatenate((samples,np.zeros(round(rate*.20),dtype=np.float32)))
            temp=SOURCE.parent/'intro_voice_render.wav'
            sf.write(str(temp),samples,rate)
            subprocess.run(['ffmpeg','-v','error','-y','-i',str(temp),'-c:a','libvorbis','-q:a','4',str(target)],check=True)
        info=sf.info(str(target))
        manifest['entries'][entry['id']]=dict(entry,file=filename,duration=info.duration,synthesis_text=spoken)
        print(f'{i}/{len(entries)} {entry["id"]}: {info.duration:.1f}s | {time.monotonic()-started:.0f}s acumulados',flush=True)
    temp_manifest=OUTPUT/'manifest.tmp'
    temp_manifest.write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
    temp_manifest.replace(OUTPUT/'manifest.json')
    print('Locución introductoria completa',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--export',action='store_true')
    args=parser.parse_args()
    export() if args.export else generate()
