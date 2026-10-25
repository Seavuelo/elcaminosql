"""Diagnóstico del paquete, con datos temporales y sin tocar la partida"""
import json
import os
from pathlib import Path
import tempfile
import traceback
from copy import deepcopy
from game.version import VERSION


def check_install(report_path):
    os.environ['SDL_VIDEODRIVER']='dummy'
    os.environ['SDL_AUDIODRIVER']='dummy'
    import pygame
    report={'version':VERSION,'success':False,'checks':[]}
    try:
        from game.config import DEFAULT_CONFIG
        from game.save_system import DEFAULT_SAVE
        from game.database import DatabaseManager
        from game.audio import AudioManager
        from game.foundations import FoundationsScene
        from game.title_screen import TitleScreen
        from game.rendering import Canvas

        class MemoryConfig:
            def __init__(self):self.data=deepcopy(DEFAULT_CONFIG)
            def get(self,key,default=None):return self.data.get(key,default)
            def set(self,key,value):self.data[key]=value

        class MemorySave:
            def __init__(self):self.data=deepcopy(DEFAULT_SAVE)
            def save(self):pass
            def exists(self):return False

        pygame.init();pygame.display.set_mode((480,300))
        config,save=MemoryConfig(),MemorySave()
        audio=AudioManager(config)
        if not audio.music_enabled or not audio.narrator:raise RuntimeError('No se pudo iniciar el audio')
        for context in ('menu','study','exam'):audio.set_music_context(context)
        report['checks'].append('Tres pistas de música cargadas')
        if len(audio.narrator.entries)!=69:raise RuntimeError('El manifiesto de voz está incompleto')
        for entry in audio.narrator.entries.values():
            if pygame.mixer.Sound(str(audio.narrator.folder/entry['file'])).get_length()<=0:
                raise RuntimeError('Audio de voz vacío')
        report['checks'].append('69 fragmentos de voz decodificados')
        with tempfile.TemporaryDirectory() as folder:
            db=DatabaseManager(str(Path(folder)/'practice.db'));db.reset()
            result=db.execute_query('SELECT COUNT(*) FROM estudiantes;')
            if not result['success'] or result['rows'][0][0]<1:raise RuntimeError('Falta la plantilla de datos')
        report['checks'].append('Base de práctica creada desde la plantilla')
        canvas=Canvas((480,300))
        TitleScreen(audio,save,lambda:None,lambda:None,lambda:None,lambda:None).draw(canvas,1)
        room=FoundationsScene(save,audio);room.open(lambda:None,lambda:None)
        for day in range(1,6):
            room.day=day;room.start_lecture()
            room.lecture.draw(canvas)
            if not audio.narrator.channel.get_busy():raise RuntimeError(f'Falta la narración del día {day}')
        audio.stop_narration()
        report['checks'].append('Menú y cinco clases renderizados con narración')
        report['success']=True
    except Exception:
        report['error']=traceback.format_exc()
    finally:
        pygame.quit()
    Path(report_path).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
    return 0 if report['success'] else 1
