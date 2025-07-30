# src/stbz_lib/_core/_win32.py
"""
Windows API 定義與結構
"""
import ctypes
from ctypes import wintypes

# ══════════════════════════════════════════════════════
# 指標相容性定義
# ══════════════════════════════════════════════════════
PTR = ctypes.sizeof(ctypes.c_void_p)
ULONG_PTR = ctypes.c_ulonglong if PTR == 8 else ctypes.c_ulong
LONG_PTR = ctypes.c_longlong if PTR == 8 else ctypes.c_long
WPARAM = ULONG_PTR
LPARAM = LONG_PTR
LRESULT = LONG_PTR
HHOOK = ctypes.c_void_p
HRESULT = ctypes.c_long
LPWSTR = ctypes.c_wchar_p
LPCWSTR = ctypes.c_wchar_p

# ══════════════════════════════════════════════════════
# 常數定義
# ══════════════════════════════════════════════════════

# ── Hook 相關 ────────────────────────────────────────
WH_KEYBOARD_LL = 13
WH_MOUSE_LL = 14

LLKHF_INJECTED = 0x00000010
LLMHF_INJECTED = 0x00000001

# ── 視窗訊息 ─────────────────────────────────────────
WM_QUIT = 0x0012
WM_CLOSE = 0x0010
WM_USER = 0x0400

# 鍵盤訊息
WM_KEYDOWN = 0x0100
WM_KEYUP = 0x0101

# 滑鼠訊息
WM_MOUSEMOVE = 0x0200
WM_LBUTTONDOWN = 0x0201
WM_LBUTTONUP = 0x0202
WM_RBUTTONDOWN = 0x0204
WM_RBUTTONUP = 0x0205
WM_MBUTTONDOWN = 0x0207
WM_MBUTTONUP = 0x0208
WM_XBUTTONDOWN = 0x020B
WM_XBUTTONUP = 0x020C

# ── 輸入相關 ─────────────────────────────────────────
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1
INPUT_HARDWARE = 2

# 鍵盤事件標誌
KEYEVENTF_EXTENDEDKEY = 0x0001
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004
KEYEVENTF_SCANCODE = 0x0008

# 滑鼠事件標誌
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_XDOWN = 0x0080
MOUSEEVENTF_XUP = 0x0100
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_HWHEEL = 0x1000
MOUSEEVENTF_ABSOLUTE = 0x8000

# 滑鼠按鈕
XBUTTON1 = 0x0001
XBUTTON2 = 0x0002

# 虛擬鍵碼映射
MAPVK_VK_TO_VSC = 0

# ── 系統指標 ─────────────────────────────────────────
SM_CXSCREEN = 0
SM_CYSCREEN = 1

# ── GDI/截圖相關 ─────────────────────────────────────
SRCCOPY = 0x00CC0020
PW_RENDERFULLCONTENT = 0x00000002
DIB_RGB_COLORS = 0
BI_RGB = 0

# ── 進程相關 ─────────────────────────────────────────
PROCESS_TERMINATE = 0x0001

# ── 關機相關 ─────────────────────────────────────────
EWX_SHUTDOWN = 0x00000001
EWX_REBOOT = 0x00000002
EWX_FORCE = 0x00000004
EWX_POWEROFF = 0x00000008
EWX_FORCEIFHUNG = 0x00000010
SHTDN_REASON_FLAG_PLANNED = 0x80000000

# ── 權限相關 ─────────────────────────────────────────
TOKEN_ADJUST_PRIVILEGES = 0x00000020
TOKEN_QUERY = 0x00000008
SE_PRIVILEGE_ENABLED = 0x00000002
SE_SHUTDOWN_NAME = "SeShutdownPrivilege"

# ── COM 相關 ─────────────────────────────────────────
CLSCTX_INPROC_SERVER = 0x1
CLSCTX_ALL = 0x17

# ── Audio 相關 ───────────────────────────────────────
# Device State
DEVICE_STATE_ACTIVE = 0x1
DEVICE_STATE_DISABLED = 0x2
DEVICE_STATE_NOTPRESENT = 0x4
DEVICE_STATE_UNPLUGGED = 0x8

# EDataFlow
EDATA_FLOW_RENDER = 0
EDATA_FLOW_CAPTURE = 1
EDATA_FLOW_ALL = 2

# ERole
EROLE_CONSOLE = 0
EROLE_MULTIMEDIA = 1
EROLE_COMMUNICATIONS = 2

# ══════════════════════════════════════════════════════
# 結構定義
# ══════════════════════════════════════════════════════


# ── 基礎結構 ─────────────────────────────────────────
class POINT(ctypes.Structure):
    _fields_ = [("x", wintypes.LONG), ("y", wintypes.LONG)]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", WPARAM),
        ("lParam", LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


LPMSG = ctypes.POINTER(MSG)


# ── Hook 結構 ────────────────────────────────────────
class KBDLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("vkCode", wintypes.DWORD),
        ("scanCode", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MSLLHOOKSTRUCT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("flags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


# ── 輸入結構 ─────────────────────────────────────────
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ULONG_PTR),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [("uMsg", wintypes.DWORD), ("wParamL", wintypes.WORD), ("wParamH", wintypes.WORD)]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("mi", MOUSEINPUT), ("ki", KEYBDINPUT), ("hi", HARDWAREINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [("type", wintypes.DWORD), ("u", INPUT_UNION)]


# ── GDI 結構 ─────────────────────────────────────────
class BITMAPINFOHEADER(ctypes.Structure):
    _fields_ = [
        ("biSize", wintypes.DWORD),
        ("biWidth", wintypes.LONG),
        ("biHeight", wintypes.LONG),
        ("biPlanes", wintypes.WORD),
        ("biBitCount", wintypes.WORD),
        ("biCompression", wintypes.DWORD),
        ("biSizeImage", wintypes.DWORD),
        ("biXPelsPerMeter", wintypes.LONG),
        ("biYPelsPerMeter", wintypes.LONG),
        ("biClrUsed", wintypes.DWORD),
        ("biClrImportant", wintypes.DWORD),
    ]


class BITMAPINFO(ctypes.Structure):
    _fields_ = [("bmiHeader", BITMAPINFOHEADER), ("bmiColors", wintypes.DWORD * 3)]


# ── 權限結構 ─────────────────────────────────────────
class LUID(ctypes.Structure):
    _fields_ = [
        ("LowPart", wintypes.DWORD),
        ("HighPart", wintypes.LONG),
    ]


class LUID_AND_ATTRIBUTES(ctypes.Structure):
    _fields_ = [
        ("Luid", LUID),
        ("Attributes", wintypes.DWORD),
    ]


class TOKEN_PRIVILEGES(ctypes.Structure):
    _fields_ = [
        ("PrivilegeCount", wintypes.DWORD),
        ("Privileges", LUID_AND_ATTRIBUTES * 1),
    ]


# ── COM 相關結構 ─────────────────────────────────────
class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", wintypes.BYTE * 8),
    ]

    def __init__(self, guid_str):
        guid_str = guid_str.strip('{}').replace('-', '')
        self.Data1 = int(guid_str[0:8], 16)
        self.Data2 = int(guid_str[8:12], 16)
        self.Data3 = int(guid_str[12:16], 16)
        self.Data4[0] = int(guid_str[16:18], 16)
        self.Data4[1] = int(guid_str[18:20], 16)
        for i in range(6):
            self.Data4[i + 2] = int(guid_str[20 + i * 2 : 22 + i * 2], 16)


class IUnknown(ctypes.Structure):
    """COM IUnknown 基礎介面"""

    pass


# ── Audio GUIDs ──────────────────────────────────────
CLSID_MMDeviceEnumerator = GUID('{BCDE0395-E52F-467C-8E3D-C4579291692E}')
IID_IAudioEndpointVolume = GUID('{5CDF2C82-841E-4546-9722-0CF74078229A}')
IID_IMMDevice = GUID('{D666063F-1587-4E43-81F1-B948E807363F}')
IID_IMMDeviceEnumerator = GUID('{A95664D2-9614-4F35-A746-DE8DB63617E6}')

# ══════════════════════════════════════════════════════
# DLL 載入
# ══════════════════════════════════════════════════════
user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
advapi32 = ctypes.WinDLL("advapi32", use_last_error=True)
ole32 = ctypes.oledll.ole32

# ══════════════════════════════════════════════════════
# 回調函數類型
# ══════════════════════════════════════════════════════
LowLevelKeyboardProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)
LowLevelMouseProc = ctypes.WINFUNCTYPE(LRESULT, ctypes.c_int, WPARAM, LPARAM)
WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)

# ══════════════════════════════════════════════════════
# API 函數定義
# ══════════════════════════════════════════════════════

# ── Hook 相關 API ────────────────────────────────────
# SetWindowsHookEx
user32.SetWindowsHookExW.restype = HHOOK
user32.SetWindowsHookExW.argtypes = (
    ctypes.c_int,
    ctypes.c_void_p,
    wintypes.HMODULE,
    wintypes.DWORD,
)

# CallNextHookEx
user32.CallNextHookEx.restype = LRESULT
user32.CallNextHookEx.argtypes = (HHOOK, ctypes.c_int, WPARAM, LPARAM)

# UnhookWindowsHookEx
user32.UnhookWindowsHookEx.restype = wintypes.BOOL
user32.UnhookWindowsHookEx.argtypes = (HHOOK,)

# ── 訊息處理 API ─────────────────────────────────────
# GetMessage
user32.GetMessageW.restype = wintypes.BOOL
user32.GetMessageW.argtypes = (LPMSG, wintypes.HWND, wintypes.UINT, wintypes.UINT)

# TranslateMessage
user32.TranslateMessage.restype = wintypes.BOOL
user32.TranslateMessage.argtypes = (LPMSG,)

# DispatchMessage
user32.DispatchMessageW.restype = LRESULT
user32.DispatchMessageW.argtypes = (LPMSG,)

# PostThreadMessage
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = (wintypes.DWORD, wintypes.UINT, WPARAM, LPARAM)

# PostMessage
user32.PostMessageW.restype = wintypes.BOOL
user32.PostMessageW.argtypes = [wintypes.HWND, wintypes.UINT, WPARAM, LPARAM]

# ── 輸入 API ─────────────────────────────────────────
# SendInput
user32.SendInput.restype = wintypes.UINT
user32.SendInput.argtypes = (wintypes.UINT, ctypes.POINTER(INPUT), ctypes.c_int)

# MapVirtualKey
user32.MapVirtualKeyW.restype = wintypes.UINT
user32.MapVirtualKeyW.argtypes = (wintypes.UINT, wintypes.UINT)

# GetCursorPos
user32.GetCursorPos.restype = wintypes.BOOL
user32.GetCursorPos.argtypes = (ctypes.POINTER(POINT),)

# SetCursorPos
user32.SetCursorPos.restype = wintypes.BOOL
user32.SetCursorPos.argtypes = (ctypes.c_int, ctypes.c_int)

# ── 系統 API ─────────────────────────────────────────
# GetSystemMetrics
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetSystemMetrics.argtypes = (ctypes.c_int,)

# GetModuleHandle
kernel32.GetModuleHandleW.restype = wintypes.HMODULE
kernel32.GetModuleHandleW.argtypes = (wintypes.LPCWSTR,)

# GetCurrentThreadId
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.GetCurrentThreadId.argtypes = ()

# ── 視窗列舉 API ─────────────────────────────────────
# EnumWindows
user32.EnumWindows.restype = wintypes.BOOL
user32.EnumWindows.argtypes = [WNDENUMPROC, wintypes.LPARAM]

# GetWindowTextLength
user32.GetWindowTextLengthW.restype = wintypes.INT

# GetWindowTextW
user32.GetWindowTextW.restype = wintypes.INT
user32.GetWindowTextW.argtypes = [wintypes.HWND, wintypes.LPWSTR, wintypes.INT]

# IsWindowVisible
user32.IsWindowVisible.restype = wintypes.BOOL

# GetWindowRect
user32.GetWindowRect.restype = wintypes.BOOL
user32.GetWindowRect.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.RECT)]

# ── GDI/截圖 API ─────────────────────────────────────
# PrintWindow
user32.PrintWindow.restype = wintypes.BOOL
user32.PrintWindow.argtypes = [wintypes.HWND, ctypes.c_void_p, wintypes.UINT]

# GetWindowDC
user32.GetWindowDC.restype = ctypes.c_void_p
user32.GetWindowDC.argtypes = [wintypes.HWND]

# ReleaseDC
user32.ReleaseDC.restype = wintypes.INT
user32.ReleaseDC.argtypes = [wintypes.HWND, ctypes.c_void_p]

# CreateCompatibleDC
gdi32.CreateCompatibleDC.restype = ctypes.c_void_p
gdi32.CreateCompatibleDC.argtypes = [ctypes.c_void_p]

# CreateCompatibleBitmap
gdi32.CreateCompatibleBitmap.restype = ctypes.c_void_p
gdi32.CreateCompatibleBitmap.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int]

# SelectObject
gdi32.SelectObject.restype = ctypes.c_void_p
gdi32.SelectObject.argtypes = [ctypes.c_void_p, ctypes.c_void_p]

# BitBlt
gdi32.BitBlt.restype = wintypes.BOOL
gdi32.BitBlt.argtypes = [
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_void_p,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.DWORD,
]

# GetDIBits
gdi32.GetDIBits.restype = wintypes.INT
gdi32.GetDIBits.argtypes = [
    ctypes.c_void_p,
    ctypes.c_void_p,
    wintypes.UINT,
    wintypes.UINT,
    ctypes.c_void_p,
    ctypes.POINTER(BITMAPINFO),
    wintypes.UINT,
]

# DeleteObject
gdi32.DeleteObject.restype = wintypes.BOOL
gdi32.DeleteObject.argtypes = [ctypes.c_void_p]

# DeleteDC
gdi32.DeleteDC.restype = wintypes.BOOL
gdi32.DeleteDC.argtypes = [ctypes.c_void_p]

# ── 進程相關 API ─────────────────────────────────────
# GetWindowThreadProcessId
user32.GetWindowThreadProcessId.restype = wintypes.DWORD
user32.GetWindowThreadProcessId.argtypes = [wintypes.HWND, ctypes.POINTER(wintypes.DWORD)]

# OpenProcess
kernel32.OpenProcess.restype = wintypes.HANDLE
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]

# TerminateProcess
kernel32.TerminateProcess.restype = wintypes.BOOL
kernel32.TerminateProcess.argtypes = [wintypes.HANDLE, wintypes.UINT]

# CloseHandle
kernel32.CloseHandle.restype = wintypes.BOOL
kernel32.CloseHandle.argtypes = [wintypes.HANDLE]

# ── 關機 API ─────────────────────────────────────────
# ExitWindowsEx
user32.ExitWindowsEx.restype = wintypes.BOOL
user32.ExitWindowsEx.argtypes = [wintypes.UINT, wintypes.DWORD]

# ── 權限 API ─────────────────────────────────────────
# GetCurrentProcess
kernel32.GetCurrentProcess.restype = wintypes.HANDLE
kernel32.GetCurrentProcess.argtypes = []

# OpenProcessToken
advapi32.OpenProcessToken.restype = wintypes.BOOL
advapi32.OpenProcessToken.argtypes = [wintypes.HANDLE, wintypes.DWORD, ctypes.POINTER(wintypes.HANDLE)]

# LookupPrivilegeValueW
advapi32.LookupPrivilegeValueW.restype = wintypes.BOOL
advapi32.LookupPrivilegeValueW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR, ctypes.POINTER(LUID)]

# AdjustTokenPrivileges
advapi32.AdjustTokenPrivileges.restype = wintypes.BOOL
advapi32.AdjustTokenPrivileges.argtypes = [
    wintypes.HANDLE,
    wintypes.BOOL,
    ctypes.POINTER(TOKEN_PRIVILEGES),
    wintypes.DWORD,
    ctypes.POINTER(TOKEN_PRIVILEGES),
    ctypes.POINTER(wintypes.DWORD),
]

# ── COM API ──────────────────────────────────────────
# CoInitialize
ole32.CoInitialize.argtypes = [ctypes.c_void_p]
ole32.CoInitialize.restype = HRESULT

# CoUninitialize
ole32.CoUninitialize.argtypes = []
ole32.CoUninitialize.restype = None

# CoCreateInstance
ole32.CoCreateInstance.argtypes = [
    ctypes.POINTER(GUID),
    ctypes.c_void_p,
    wintypes.DWORD,
    ctypes.POINTER(GUID),
    ctypes.POINTER(ctypes.c_void_p),
]
ole32.CoCreateInstance.restype = HRESULT
