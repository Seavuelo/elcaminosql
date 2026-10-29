"""Comprueba los sistemas nativos con partidas aisladas, sin tocar la partida personal."""
import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / '.tools/godot/Godot_v4.7.2-stable_win64_console.exe'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--window', action='store_true', help='Incluye la prueba que cambia el modo de pantalla')
    args = parser.parse_args()
    destination = ROOT / '.preview/native-tests'
    destination.mkdir(parents=True, exist_ok=True)
    results = []
    for test in sorted((ROOT / 'godot/tests').glob('test_*.gd')):
        if test.stem == 'test_window' and not args.window:
            continue
        folder = destination / test.stem
        folder.mkdir(exist_ok=True)
        command = [str(ENGINE), '--path', str(ROOT / 'godot'), '--script', 'res://tests/' + test.name,
                   '--log-file', str(folder / 'engine.log'), '--', '--visual-check', '--test-dir', str(folder / 'save')]
        if test.stem != 'test_window':
            command.insert(1, '--headless')
        try:
            process = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=100)
            output = process.stdout + process.stderr
            (folder / 'output.txt').write_text(output, encoding='utf-8')
            reports = []
            for line in output.splitlines():
                if line.startswith('{'):
                    try:
                        reports.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass
            ok = process.returncode == 0 and bool(reports) and not any(r.get('failures') for r in reports) and 'SCRIPT ERROR' not in output
            results.append({'test': test.stem, 'ok': ok, 'reports': reports})
        except subprocess.TimeoutExpired:
            results.append({'test': test.stem, 'ok': False, 'error': 'timeout'})
        print(('PASS ' if results[-1]['ok'] else 'FAIL ') + test.stem, flush=True)
    (destination / 'report.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
    raise SystemExit(0 if all(item['ok'] for item in results) else 1)

if __name__ == '__main__':
    main()
