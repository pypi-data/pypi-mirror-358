# src/stbz_lib/_close.py
import ctypes
import time
from ctypes import wintypes

from ._core._win32 import *


def _find_windows_and_pids(name):
    found_pids = set()
    name_lower = name.lower()

    @WNDENUMPROC
    def enum_proc(hwnd, _):
        if not user32.IsWindowVisible(hwnd):
            return True

        ln = user32.GetWindowTextLengthW(hwnd)
        if ln == 0:
            return True

        buf = ctypes.create_unicode_buffer(ln + 1)
        user32.GetWindowTextW(hwnd, buf, ln + 1)

        if name_lower in buf.value.lower():
            pid = wintypes.DWORD()
            user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
            found_pids.add(pid.value)

        return True

    user32.EnumWindows(enum_proc, 0)
    return found_pids


def _terminate_process(pid):
    hProcess = kernel32.OpenProcess(PROCESS_TERMINATE, False, pid)
    if not hProcess:
        return False

    try:
        result = kernel32.TerminateProcess(hProcess, 0)
        return bool(result)
    finally:
        kernel32.CloseHandle(hProcess)


def close(name, delay_ms=0):
    """
    強制關閉所有符合名稱的進程
    name     : 視窗標題（部分匹配）
    delay_ms : 每個進程終止之間的延遲（毫秒）
    返回     : 終止的進程數量
    """
    pids = _find_windows_and_pids(name)

    if not pids:
        return 0

    terminated = 0
    for i, pid in enumerate(pids):
        if i > 0 and delay_ms > 0:
            time.sleep(delay_ms / 1000.0)
        if _terminate_process(pid):
            terminated += 1

    return terminated
