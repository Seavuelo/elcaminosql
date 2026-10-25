"""Impide abrir varias copias del juego, incluso con clics simultáneos"""
import atexit
import os

_handle = None


def acquire_game_lock(name="Local\\ElCaminoSQL.Game"):
    global _handle
    if os.name != "nt" or _handle is not None:
        return True

    import ctypes
    from ctypes import wintypes

    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel.CreateMutexW.argtypes = [wintypes.LPVOID, wintypes.BOOL, wintypes.LPCWSTR]
    kernel.CreateMutexW.restype = wintypes.HANDLE
    kernel.CloseHandle.argtypes = [wintypes.HANDLE]
    kernel.CloseHandle.restype = wintypes.BOOL
    handle = kernel.CreateMutexW(None, False, name)
    if not handle:
        raise ctypes.WinError(ctypes.get_last_error())
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        kernel.CloseHandle(handle)
        return False
    _handle = handle
    atexit.register(kernel.CloseHandle, handle)
    return True
