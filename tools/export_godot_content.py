"""Conserva el contenido educativo y los medios aprobados al trasladarlos a Godot."""
from copy import deepcopy
from pathlib import Path
import json
import os
import shutil
import sqlite3
import sys
import wave
from unittest.mock import Mock
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def export():
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    os.environ['SDL_AUDIODRIVER'] = 'dummy'
    import pygame
    from game.curriculum import UniversityCurriculum
    from game.save_system import DEFAULT_SAVE
    from game.foundations import FoundationsScene
    from game.foundations_content import DAYS
    from game.lecture import LectureScene
    from game.lessons import demonstration
    from game.kashut_questions import QUESTIONS, DIAGRAMS
    from game.notebook import FOUNDATION_NOTES
    from game.intro_peers import DIALOGUES
    from game.intro_classroom import MOSHI_BEFORE, MOSHI_AFTER
    from game.world import World
    from game.hints import task_hint
    from game import league
    from game import appearance
    from game.intro import IntroPrologue
    from game.kashut import reward_for
    from game.audio import AudioManager
    pygame.init()
    pygame.display.set_mode((480, 270))
    save = Mock(data=deepcopy(DEFAULT_SAVE))
    curriculum = UniversityCurriculum(Mock(), save, Mock())
    intro = FoundationsScene(save, Mock())
    intro.open(Mock(), Mock())
    lecture = LectureScene(Mock(), save)
    manifest = json.loads((ROOT/'assets/voice/marco_intro/manifest.json').read_text(encoding='utf-8'))['entries']
    content = {'lessons': {}, 'tasks': {}, 'exams': {}, 'quiz': {}, 'foundation': DAYS,
               'notes': FOUNDATION_NOTES, 'peers': [], 'intro_dialogues': {}, 'league': {}, 'appearance': {}, 'model_tasks': {}}
    content['prologue'] = IntroPrologue(Mock(), Mock()).slides
    content['kashut_rewards'] = [reward_for(score) for score in range(11)]
    for name in ('SKIN_TONES', 'HAIR_COLORS', 'SHIRT_COLORS', 'EYE_COLORS', 'PANTS_COLORS', 'SHOE_COLORS', 'BACKPACK_COLORS', 'HAIR_STYLES', 'CLOTHING_STYLES', 'SHOE_STYLES'):
        content['appearance'][name.lower()] = getattr(appearance, name)
    for day in range(1, 6):
        intro.day = day
        intro.start_lecture()
        content['lessons'][f'0_{day}'] = intro.lecture.slides
        content['model_tasks'][str(day)] = intro.task_checklist()
        content['quiz'][str(day)] = [dict(question=q[0], options=q[1], answer=q[2], feedback=q[3], diagram=DIAGRAMS[day][i])
                                   for i, q in enumerate(QUESTIONS[day])]
    for year in range(1, 5):
        for day in range(1, 6):
            content['lessons'][f'{year}_{day}'] = lecture._build_slides(year, day, 0)
            if day < 5:
                content.setdefault('demonstrations', {})[f'{year}_{day}'] = demonstration(year, day)
    for key, tasks in curriculum.tasks.items():
        content['tasks'][f'{key[0]}_{key[1]}'] = [dict(title=t.title, objective=t.objective, sql=t.canonical_query,
            explanation=t.explanation, is_write=t.is_write, note_id=t.note_id,
            hints=[task_hint(t, level) for level in range(1, 4)]) for t in tasks]
    exams = curriculum.exams if hasattr(curriculum, 'exams') else curriculum.exam_questions
    for year, questions in exams.items():
        content['exams'][str(year)] = [dict(title=q.title, objective=q.objective, sql=q.canonical_query, is_write=q.is_write) for q in questions]
    world = World()
    for peer in world.classmates:
        content['peers'].append(dict(id=peer.id, name=peer.name, first_year=peer.min_year, last_year=peer.max_year,
            skin=peer.skin_color, hair=peer.hair_color, shirt=peer.shirt_color, eyes=peer.eye_color,
            pants=peer.pants_color, shoes=peer.shoe_color, hair_style=peer.hair_style,
            before={f'{y}_{d}': text for (y, d), text in peer.dialogues_before.items()},
            after={f'{y}_{d}': text for (y, d), text in peer.dialogues_after.items()}, dropout=peer.dropout_note))
    for name, speeches in DIALOGUES.items():
        content['intro_dialogues'][name] = {'before': speeches[0], 'after': speeches[1]}
    content['intro_dialogues']['Moshi'] = {'before': list(MOSHI_BEFORE.values()), 'after': list(MOSHI_AFTER.values())}
    for name in ('GODS', 'PROFILES', 'STRATEGIES', 'STRATEGY_INFO', 'RELICS', 'UPGRADES', 'SCOUTS', 'CUE_TEXT', 'RANKS'):
        content['league'][name.lower()] = getattr(league, name)
    for slides in content['lessons'].values():
        for slide in slides:
            voice = manifest.get(slide.get('narration_id'))
            if voice is None:
                raise ValueError(f'Falta voz aprobada: {slide.get("narration_id")}')
            slide['audio'] = 'res://assets/voice/' + voice['file']
    content['boards'] = {}
    for key, slides in content['lessons'].items():
        boards = []
        previous = None
        for slide in slides:
            signature = tuple(json.dumps(slide.get(field), sort_keys=True) for field in (
                'title', 'chalk_body', 'code_example', 'table_columns', 'table_rows', 'illustration'))
            if signature != previous:
                boards.append(dict(slide, speech_parts=[]))
            boards[-1]['speech_parts'].append({'text': slide['turing'], 'audio': slide['audio'],
                                               'id': slide['narration_id'], 'focus': slide.get('code_focus', 0)})
            previous = signature
        content['boards'][key] = boards
    target = ROOT/'godot/data'
    target.mkdir(parents=True, exist_ok=True)
    (target/'course.json').write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding='utf-8')
    assets = ROOT/'godot/assets'
    (assets/'voice').mkdir(parents=True, exist_ok=True)
    for voice in manifest.values():
        shutil.copyfile(ROOT/'assets/voice/marco_intro'/voice['file'], assets/'voice'/voice['file'])
    (assets/'music').mkdir(exist_ok=True)
    for name in ('bathroom_chill_loop.ogg', 'alex_morgan_jazz_loop.ogg', 'a_kind_of_hope.mp3'):
        shutil.copyfile(ROOT/'assets/music'/name, assets/'music'/name)
    from game.league_art import portrait
    from game.creator_note import TEXT as creator_note
    content['creator_note'] = creator_note
    (target/'course.json').write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding='utf-8')
    (assets/'league').mkdir(exist_ok=True)
    for god in league.GODS:
        pygame.image.save(portrait(god, 192), assets/'league'/(god+'.png'))
    (assets/'sfx').mkdir(exist_ok=True)
    audio = AudioManager(SimpleNamespace(get=lambda key, default=None: 1.0 if key == 'sfx_volume' else default))
    for name in ('success', 'key', 'error', 'chalk', 'bell'):
        with wave.open(str(assets/'sfx'/(name+'.wav')), 'wb') as output:
            output.setnchannels(audio.channels)
            output.setsampwidth(2)
            output.setframerate(audio.sample_rate)
            output.writeframes(getattr(audio, 'snd_'+name).get_raw())
    (target/'credits.txt').write_text((ROOT/'CREDITS.md').read_text(encoding='utf-8'), encoding='utf-8')
    from database.seed_universidad import add_practice_data
    seed_path = ROOT/'database/universidad.db'
    with sqlite3.connect(seed_path.as_uri() + '?mode=ro', uri=True) as seed, sqlite3.connect(':memory:') as conn:
        seed.backup(conn)
        add_practice_data(conn)
        conn.commit()
        dump = '\n'.join(conn.iterdump())
        (target/'university.sql').write_text(dump, encoding='utf-8')
    pygame.quit()
    print(json.dumps({'lessons': len(content['lessons']), 'tasks': sum(map(len, content['tasks'].values())),
                      'exam_questions': sum(map(len, content['exams'].values())), 'voices': len(manifest),
                      'quiz_questions': sum(map(len, content['quiz'].values()))}))


if __name__ == '__main__':
    export()
