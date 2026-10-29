"""Prepara Godot portátil y SQLite con descargas fijadas y comprobadas."""
import argparse
import hashlib
from pathlib import Path
import shutil
import urllib.request
import zipfile

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.tools' / 'downloads'
ENGINE = ROOT / '.tools' / 'godot'
VERSION = '4.7.2-stable'
PACKAGES = {
    'engine': (
        f'https://github.com/godotengine/godot-builds/releases/download/{VERSION}/Godot_v{VERSION}_win64.exe.zip',
        '731980f9608d61333e5baf54a2ef17210acc7a538446c0cb9969f002aca1e953'),
    'sqlite': (
        'https://github.com/2shady4u/godot-sqlite/releases/download/v4.9/addons.zip',
        '95e91b72fe32984a84edaf6357a78753661f37a170cb362f5b948e0ede7c2cb0'),
    'templates': (
        f'https://github.com/godotengine/godot-builds/releases/download/{VERSION}/Godot_v{VERSION}_export_templates.tpz',
        'f298490b8d44d934be425a5a65a51bf15f422428b229a06a6e11d9ffea248011'),
}


def download(key):
    url, digest = PACKAGES[key]
    CACHE.mkdir(parents=True, exist_ok=True)
    target = CACHE / url.rsplit('/', 1)[-1]
    if target.exists():
        with target.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() == digest:
                return target
    partial = target.with_suffix('.part')
    print(f'Descargando {key}...', flush=True)
    request = urllib.request.Request(url, headers={'User-Agent': 'ElCaminoSQL-setup'})
    try:
        with urllib.request.urlopen(request, timeout=90) as source, partial.open('wb') as output:
            shutil.copyfileobj(source, output, 1024 * 1024)
        with partial.open('rb') as source:
            if hashlib.file_digest(source, 'sha256').hexdigest() != digest:
                raise ValueError(f'La descarga de {key} no coincide con su SHA256 oficial')
        partial.replace(target)
    finally:
        partial.unlink(missing_ok=True)
    return target


def extract(archive, destination, include=lambda name: True):
    destination.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as package:
        for member in package.infolist():
            if member.is_dir() or not include(member.filename):
                continue
            target = (destination / member.filename).resolve()
            if not target.is_relative_to(destination.resolve()):
                raise ValueError('Ruta no válida en el paquete')
            target.parent.mkdir(parents=True, exist_ok=True)
            with package.open(member) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--templates', action='store_true', help='También prepara la exportación de Windows')
    options = parser.parse_args()
    extract(download('engine'), ENGINE)
    (ENGINE / '_sc_').touch()
    extract(download('sqlite'), ROOT / 'godot', lambda name: '/bin/' not in name or name.endswith('.dll'))
    if options.templates:
        extract(download('templates'), ENGINE, lambda name: name.rsplit('/', 1)[-1] in (
            'windows_release_x86_64.exe', 'windows_debug_x86_64.exe', 'version.txt'))
    print(f'Godot listo en {ENGINE}', flush=True)


if __name__ == '__main__':
    main()
