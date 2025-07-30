# src/stbz_lib/_capture.py
import ctypes
from ctypes import wintypes

import numpy as np

from ._core._win32 import *


def _find_window(name):
    found_hwnd = None
    name_lower = name.lower()

    @WNDENUMPROC
    def enum_proc(hwnd, _):
        nonlocal found_hwnd
        if not user32.IsWindowVisible(hwnd):
            return True
        ln = user32.GetWindowTextLengthW(hwnd)
        if ln == 0:
            return True
        buf = ctypes.create_unicode_buffer(ln + 1)
        user32.GetWindowTextW(hwnd, buf, ln + 1)
        if name_lower in buf.value.lower():
            found_hwnd = hwnd
            return False
        return True

    user32.EnumWindows(enum_proc, 0)
    if not found_hwnd:
        raise RuntimeError(f"找不到標題含「{name}」的視窗")
    return found_hwnd


def _capture_window(hwnd):
    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    x, y = rect.left, rect.top
    w, h = rect.right - rect.left, rect.bottom - rect.top

    hdc = user32.GetWindowDC(hwnd)
    if not hdc:
        raise RuntimeError("無法取得視窗 DC")

    src = gdi32.CreateCompatibleDC(hdc)
    if not src:
        user32.ReleaseDC(hwnd, hdc)
        raise RuntimeError("無法建立相容 DC")

    bmp = gdi32.CreateCompatibleBitmap(hdc, w, h)
    if not bmp:
        gdi32.DeleteDC(src)
        user32.ReleaseDC(hwnd, hdc)
        raise RuntimeError("無法建立 Bitmap")

    gdi32.SelectObject(src, bmp)

    if not user32.PrintWindow(hwnd, src, PW_RENDERFULLCONTENT):
        gdi32.BitBlt(src, 0, 0, w, h, hdc, 0, 0, SRCCOPY)

    bmi = BITMAPINFO()
    bmi.bmiHeader.biSize = ctypes.sizeof(BITMAPINFOHEADER)
    bmi.bmiHeader.biWidth = w
    bmi.bmiHeader.biHeight = -h
    bmi.bmiHeader.biPlanes = 1
    bmi.bmiHeader.biBitCount = 24
    bmi.bmiHeader.biCompression = BI_RGB

    buf = ctypes.create_string_buffer(w * h * 3)
    gdi32.GetDIBits(src, bmp, 0, h, buf, ctypes.byref(bmi), DIB_RGB_COLORS)
    img = np.frombuffer(buf, dtype=np.uint8).reshape((h, w, 3))

    gdi32.DeleteObject(bmp)
    gdi32.DeleteDC(src)
    user32.ReleaseDC(hwnd, hdc)

    return img, x, y, w, h


def capture(name):
    """
    截取指定視窗
    name : 視窗標題（部分匹配）
    返回 : (image, info)
    """
    hwnd = _find_window(name)
    img, x, y, w, h = _capture_window(hwnd)
    return img, {"hwnd": hwnd, "x": x, "y": y, "width": w, "height": h}
