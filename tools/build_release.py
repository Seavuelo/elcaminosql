"""Construye y comprueba la distribución portátil de Windows desde este proyecto"""
import hashlib
from importlib.metadata import distribution
import json
import os
from pathlib import Path
import platform
import runpy
import shutil
import subprocess
import sys
import zipfile

ROOT=Path(__file__).resolve().parents[1]
VERSION=runpy.run_path(str(ROOT/'game'/'version.py'))['VERSION']


def run(*args,**kwargs):
    subprocess.run([str(arg) for arg in args],cwd=ROOT,check=True,**kwargs)


def copy_licenses(destination):
    destination.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(Path(sys.base_prefix)/'LICENSE.txt',destination/'Python-LICENSE.txt')
    for name in ('numpy',):
        package=distribution(name)
        for file in package.files or []:
            if '/licenses/' in str(file).replace('\\','/'):
                relative=str(file).replace('\\','/').split('/licenses/',1)[1]
                target=destination/name/relative
                target.parent.mkdir(parents=True,exist_ok=True)
                shutil.copyfile(package.locate_file(file),target)
    for file in (ROOT/'packaging'/'licenses').iterdir():
        if file.is_file():shutil.copyfile(file,destination/file.name)


def main():
    if sys.platform!='win32' or platform.machine().upper() not in ('AMD64','X86_64'):
        raise SystemExit('Este paquete debe compilarse en Windows x64')
    build=ROOT/'build';dist=ROOT/'dist'
    build.mkdir(exist_ok=True);dist.mkdir(exist_ok=True)
    env=os.environ.copy();env.update(SDL_VIDEODRIVER='dummy',SDL_AUDIODRIVER='dummy')
    run(sys.executable,'-m','unittest','discover','-s','tests',env=env)
    numeric=tuple(int(part) for part in VERSION.split('-')[0].split('.'))+(int(VERSION.rsplit('.',1)[-1]),)
    info=build/'version_info.txt'
    info.write_text(f"""VSVersionInfo(
 ffi=FixedFileInfo(filevers={numeric!r},prodvers={numeric!r},mask=0x3f,flags=0x2,OS=0x40004,fileType=0x1,subtype=0x0,date=(0,0)),
 kids=[StringFileInfo([StringTable('040904B0',[
 StringStruct('CompanyName','Seavuelo'),
 StringStruct('FileDescription','El Camino SQL - version experimental'),
 StringStruct('FileVersion',{VERSION!r}),
 StringStruct('ProductName','El Camino SQL'),
 StringStruct('ProductVersion',{VERSION!r}),
 StringStruct('OriginalFilename','ElCaminoSQL.exe')])]),
 VarFileInfo([VarStruct('Translation',[1033,1200])])])
""",encoding='utf8')
    run(sys.executable,'-m','PyInstaller','--noconfirm','--onedir','--windowed',
        '--name','ElCaminoSQL','--distpath',dist/'portable','--workpath',build/'pyinstaller',
        '--specpath',build,'--icon',ROOT/'assets'/'icon.ico','--version-file',info,
        '--add-data',str(ROOT/'assets')+':assets',
        '--add-data',str(ROOT/'database'/'universidad.db')+':database',ROOT/'main.py')
    app=dist/'portable'/'ElCaminoSQL'
    for source,name in [('packaging/LEEME.txt','LEEME.txt'),('CREDITS.md','CREDITS.md'),
                        (f'docs/releases/v{VERSION}.md','NOVEDADES.md'),
                        ('packaging/THIRD_PARTY_NOTICES.md','THIRD_PARTY_NOTICES.md')]:
        shutil.copyfile(ROOT/source,app/name)
    copy_licenses(app/'LICENSES')
    report=build/'install-check.json'
    run(app/'ElCaminoSQL.exe','--check-install',report,timeout=60)
    result=json.loads(report.read_text(encoding='utf8'))
    if not result.get('success') or result.get('version')!=VERSION:
        raise RuntimeError('El ejecutable no pasó la verificación: '+str(result))
    archive=dist/f'ElCaminoSQL-{VERSION}-Windows-x64.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as bundle:
        for file in sorted(app.rglob('*')):
            if file.is_file():bundle.write(file,Path('ElCaminoSQL')/file.relative_to(app))
    with zipfile.ZipFile(archive) as bundle:
        bad=bundle.testzip()
        if bad:raise RuntimeError('El ZIP está dañado: '+bad)
    with archive.open('rb') as stream:checksum=hashlib.file_digest(stream,'sha256').hexdigest()
    sums=dist/'SHA256SUMS.txt'
    sums.write_text(f'{checksum}  {archive.name}\n',encoding='utf8')
    print(f'Paquete verificado: {archive}\nSHA256: {checksum}',flush=True)


if __name__=='__main__':main()
