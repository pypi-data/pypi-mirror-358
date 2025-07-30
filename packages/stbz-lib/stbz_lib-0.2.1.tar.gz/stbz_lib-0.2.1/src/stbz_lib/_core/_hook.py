# src/stbz_lib/_core/_hook.py
import ctypes
import threading

from ._win32 import *


class HookManager:
    """
    統一的 Hook 管理器
    確保鍵盤和滑鼠 Hook 在同一個線程中運行
    """

    def __init__(self):
        self._hook_thread = None
        self._hook_active = False
        self._thread_id = None
        self._keyboard_hook = None
        self._mouse_hook = None
        self._keyboard_cb = None
        self._mouse_cb = None
        self._lock = threading.Lock()
        self._ready_event = threading.Event()

    def set_callbacks(self, keyboard_callback=None, mouse_callback=None):
        """設置 callbacks，但不啟動 Hook"""
        with self._lock:
            if keyboard_callback:
                self._keyboard_cb = keyboard_callback
            if mouse_callback:
                self._mouse_cb = mouse_callback

    def ensure_started(self):
        """確保 Hook 線程已啟動"""
        with self._lock:
            if not self._hook_active and (self._keyboard_cb or self._mouse_cb):
                self._ready_event.clear()
                self._hook_thread = threading.Thread(target=self._worker, daemon=True)
                self._hook_thread.start()
                self._ready_event.wait(timeout=5.0)

    def stop(self):
        """停止 Hook 線程"""
        with self._lock:
            if self._hook_active and self._thread_id:
                user32.PostThreadMessageW(self._thread_id, WM_QUIT, 0, 0)
                if self._hook_thread:
                    self._hook_thread.join(timeout=2.0)
                self._thread_id = None
                self._hook_thread = None
                self._hook_active = False

    def _worker(self):
        """Hook 工作線程"""
        try:
            self._thread_id = kernel32.GetCurrentThreadId()
            hmod = kernel32.GetModuleHandleW(None)

            if self._keyboard_cb:
                self._keyboard_hook = user32.SetWindowsHookExW(WH_KEYBOARD_LL, self._keyboard_cb, hmod, 0)
                if not self._keyboard_hook:
                    raise ctypes.WinError(ctypes.get_last_error())

            if self._mouse_cb:
                self._mouse_hook = user32.SetWindowsHookExW(WH_MOUSE_LL, self._mouse_cb, hmod, 0)
                if not self._mouse_hook:
                    raise ctypes.WinError(ctypes.get_last_error())

            self._hook_active = True
            self._ready_event.set()

            msg = MSG()
            while True:
                ret = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if ret == 0 or msg.message == WM_QUIT:
                    break
                if ret == -1:
                    raise ctypes.WinError(ctypes.get_last_error())

                user32.TranslateMessage(ctypes.byref(msg))
                user32.DispatchMessageW(ctypes.byref(msg))

        except Exception as e:
            print(f"Hook worker error: {e}")
        finally:
            if self._keyboard_hook:
                user32.UnhookWindowsHookEx(self._keyboard_hook)
                self._keyboard_hook = None
            if self._mouse_hook:
                user32.UnhookWindowsHookEx(self._mouse_hook)
                self._mouse_hook = None
            self._hook_active = False
            self._ready_event.set()


_hook_manager = HookManager()


def register_keyboard_hook(callback):
    """註冊鍵盤 Hook"""
    _hook_manager.set_callbacks(keyboard_callback=callback)


def register_mouse_hook(callback):
    """註冊滑鼠 Hook"""
    _hook_manager.set_callbacks(mouse_callback=callback)


def ensure_hooks_started():
    """確保 Hooks 已啟動"""
    _hook_manager.ensure_started()


def stop_hooks():
    """停止所有 Hooks"""
    _hook_manager.stop()


# 清理
import atexit

atexit.register(stop_hooks)
