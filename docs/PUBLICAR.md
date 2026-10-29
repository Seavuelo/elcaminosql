# Subir la actualización y preparar la publicación

El remoto `origin` ya apunta a `https://github.com/Seavuelo/elcaminosql.git`, estos comandos se ejecutan dentro de la carpeta `elcaminosql`

## Actualizar el código en GitHub

```powershell
git status
git add .
git diff --cached --stat
git commit -m "Prepara El Camino SQL v0.2.0-alpha.4"
git push origin main
```

Si GitHub pide iniciar sesión, completa la autenticación en tu navegador, nunca pongas una contraseña o token dentro de los archivos del proyecto

Si el push se rechaza por cambios remotos, revisa `git fetch origin` y `git log --oneline --left-right main...origin/main` antes de integrar esos cambios, no uses `--force`

`.gitignore` excluye entornos, capturas, modelos de voz, compilaciones y documentos locales de agentes, los binarios de `dist/` se adjuntan al release y no se añaden al historial Git

## Publicar la versión para jugar

1. Primero sube el commit a `main`
2. Abre https://github.com/Seavuelo/elcaminosql/releases/new
3. Crea el tag `v0.2.0-alpha.4` con `main` como destino
4. Título: `El Camino SQL v0.2.0-alpha.4 — Versión experimental`
5. Copia las notas de `docs/releases/v0.2.0-alpha.4.md`
6. Adjunta `dist/ElCaminoSQL-0.2.0-alpha.4-Windows-x64.zip` y `dist/SHA256SUMS.txt`
7. Marca **This is a pre-release** y deja desmarcado **Set as latest release**
8. Usa **Save draft** para revisarlo o **Publish release** para hacerlo público

No publiques el archivo de código fuente como si fuera el ejecutable, las personas que quieran jugar deben descargar el ZIP de Windows que adjuntaste

## Volver a construir el paquete

Desde Windows x64, con Python 3.13 y un entorno del proyecto:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-build.txt
.\.venv\Scripts\python.exe tools/build_release.py
```

El script ejecuta las pruebas, crea el paquete con PyInstaller, verifica el ejecutable, comprueba el ZIP y calcula SHA256, no sube ni publica nada

Para repetir solo la comprobación de instalación:

```powershell
.\dist\portable\ElCaminoSQL\ElCaminoSQL.exe --check-install .\build\install-check.json
Get-Content .\build\install-check.json
```

Esta comprobación usa vídeo y audio simulados y una base temporal, no abre una ventana ni modifica tu partida

Documentación oficial: https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository
