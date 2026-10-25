"""Inicia una sola copia y prepara dependencias únicamente cuando faltan"""
import importlib.util
from pathlib import Path
import runpy
import subprocess
import sys

from game.single_instance import acquire_game_lock


def main():
    if not acquire_game_lock():
        return 0
    root = Path(__file__).resolve().parent
    if any(importlib.util.find_spec(module) is None for module in ("pygame", "numpy")):
        print("Preparando el juego, la primera vez se necesita internet")
        result = subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(root / "requirements.txt")])
        if result.returncode:
            return result.returncode
    runpy.run_path(str(root / "main.py"), run_name="__main__")
    return 0


if __name__ == "__main__":
    sys.exit(main())
