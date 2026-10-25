# Componentes de la distribución

El Camino SQL, desarrollado por Seavuelo, incluye componentes de terceros sin modificar

- Python: licencia PSF y avisos adicionales, texto completo en `LICENSES/Python-LICENSE.txt`, código fuente en https://www.python.org/downloads/source/
- Pygame 2.6.1: LGPL 2.1, texto completo en `LICENSES/pygame-LGPL-2.1.txt`, código fuente de esta versión en https://github.com/pygame/pygame/tree/2.6.1
- NumPy: licencia BSD y avisos de sus componentes, textos completos en `LICENSES/numpy/`, código fuente en https://github.com/numpy/numpy
- SDL y bibliotecas multimedia de Pygame: avisos en `LICENSES/pygame-dependencies.txt`, fuentes y procedencia en https://github.com/pygame/pygame/tree/2.6.1/buildconfig

Pygame y sus bibliotecas se distribuyen como módulos y DLL separados dentro de `_internal`, se pueden sustituir por versiones compatibles

PyInstaller se utiliza para preparar el ejecutable, su cargador tiene una excepción para distribuir las aplicaciones generadas, licencia y excepción en `LICENSES/PyInstaller-COPYING.txt`, proyecto en https://github.com/pyinstaller/pyinstaller

La música y las voces tienen sus créditos y condiciones propias en `CREDITS.md`, las licencias de las bibliotecas no se extienden automáticamente al juego ni a sus recursos
