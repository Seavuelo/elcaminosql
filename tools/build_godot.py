"""Exporta y prueba la versión nativa de Godot en Windows x64."""
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
ENGINE = ROOT / '.tools/godot/Godot_v4.7.2-stable_win64_console.exe'
OUTPUT = ROOT / 'dist/godot-0.3.0-beta.1'
VERSION = '0.3.0-beta.1'


def run(*args):
    subprocess.run([str(arg) for arg in args], cwd=ROOT, check=True, timeout=180)


def main():
    if not ENGINE.exists():
        raise SystemExit('Ejecuta Preparar-Godot.cmd primero')
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (ROOT / '.preview').mkdir(exist_ok=True)
    project = ROOT / 'godot'
    run(ENGINE, '--headless', '--editor', '--path', project, '--import', '--quit',
        '--log-file', ROOT / '.preview/godot-build-import.log')
    executable = OUTPUT / 'ElCaminoSQL.exe'
    run(ENGINE, '--headless', '--path', project, '--export-release', 'Windows Desktop', executable,
        '--log-file', ROOT / '.preview/godot-build-export.log')
    with tempfile.TemporaryDirectory(prefix='godot-export-', dir=ROOT / '.preview') as directory:
        run(executable, '--headless', '--log-file', Path(directory) / 'engine.log',
            '--', '--self-test', '--test-dir', directory)
        report = Path(directory) / 'report.json'
        result = json.loads(report.read_text(encoding='utf-8'))
        if not result['success']:
            raise SystemExit('La versión exportada no superó las comprobaciones')
        destination = ROOT / 'build/godot-install-check.json'
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(report, destination)
    shutil.copyfile(ROOT / 'godot/LEEME.txt', OUTPUT / 'LEEME.txt')
    archive = ROOT / f'dist/ElCaminoSQL-Godot-{VERSION}-Windows-x64.zip'
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=6) as package:
        for file in sorted(OUTPUT.rglob('*')):
            if file.is_file():
                package.write(file, Path('ElCaminoSQL-Godot') / file.relative_to(OUTPUT))
    with archive.open('rb') as source:
        digest = hashlib.file_digest(source, 'sha256').hexdigest()
    with tempfile.TemporaryDirectory(prefix='godot-unpacked-', dir=ROOT / '.preview') as directory:
        with zipfile.ZipFile(archive) as package:
            package.extractall(directory)
        unpacked = Path(directory) / 'ElCaminoSQL-Godot'
        isolated_save = Path(directory) / 'save'
        isolated_save.mkdir()
        run(unpacked / executable.name, '--headless', '--log-file', isolated_save / 'engine.log',
            '--', '--self-test', '--test-dir', isolated_save)
        unpacked_result = json.loads((isolated_save / 'report.json').read_text(encoding='utf-8'))
        if not unpacked_result['success']:
            raise SystemExit('El ZIP extraído no superó las comprobaciones')
    archive.with_suffix('.sha256').write_text(f'{digest}  {archive.name}\n', encoding='ascii')
    print(f'Listo: {archive}\nSHA256: {digest}', flush=True)


if __name__ == '__main__':
    main()
