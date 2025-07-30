# src/stbz_lib/_mic.py
import ctypes
import threading
from ctypes import HRESULT, POINTER
from ctypes.wintypes import BOOL, DWORD

from ._core._win32 import (
    CLSCTX_ALL,
    DEVICE_STATE_ACTIVE,
    EDATA_FLOW_CAPTURE,
    EROLE_CONSOLE,
    GUID,
    CLSID_MMDeviceEnumerator,
    IID_IAudioEndpointVolume,
    IID_IMMDevice,
    IID_IMMDeviceEnumerator,
    ole32,
)

# COM 介面虛擬函數表索引
IUNKNOWN_QUERY_INTERFACE = 0
IUNKNOWN_ADD_REF = 1
IUNKNOWN_RELEASE = 2

# IMMDeviceEnumerator 方法索引
IMMDEVICEENUMERATOR_ENUM_AUDIO_ENDPOINTS = 3
IMMDEVICEENUMERATOR_GET_DEFAULT_AUDIO_ENDPOINT = 4

# IMMDevice 方法索引
IMMDEVICE_ACTIVATE = 3

# IAudioEndpointVolume 方法索引
IAUDIOENDPOINTVOLUME_SET_MUTE = 14
IAUDIOENDPOINTVOLUME_GET_MUTE = 15

# 全域變數
_mic_muted = False
_mic_lock = threading.Lock()
_com_initialized = False
_volume_endpoint = None
_device_enumerator = None


def _ensure_com_initialized():
    global _com_initialized
    if not _com_initialized:
        hr = ole32.CoInitialize(None)
        if hr < 0 and hr != -2147417850:  # RPC_E_CHANGED_MODE
            raise ctypes.WinError(hr)
        _com_initialized = True


def _com_release(interface):
    if interface:
        release_func = ctypes.cast(
            ctypes.cast(interface, POINTER(POINTER(ctypes.c_void_p))).contents[IUNKNOWN_RELEASE],
            ctypes.WINFUNCTYPE(ctypes.c_ulong, ctypes.c_void_p),
        )
        release_func(interface)


def _get_device_enumerator():
    global _device_enumerator

    if _device_enumerator is None:
        _ensure_com_initialized()

        enumerator_ptr = ctypes.c_void_p()
        hr = ole32.CoCreateInstance(
            ctypes.byref(CLSID_MMDeviceEnumerator),
            None,
            CLSCTX_ALL,
            ctypes.byref(IID_IMMDeviceEnumerator),
            ctypes.byref(enumerator_ptr),
        )

        if hr < 0:
            raise ctypes.WinError(hr)

        _device_enumerator = enumerator_ptr.value

    return _device_enumerator


def _get_default_audio_device():
    enumerator = _get_device_enumerator()

    device_ptr = ctypes.c_void_p()

    vtbl = ctypes.cast(enumerator, POINTER(POINTER(ctypes.c_void_p))).contents
    get_default_func = ctypes.cast(
        vtbl[IMMDEVICEENUMERATOR_GET_DEFAULT_AUDIO_ENDPOINT],
        ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, DWORD, DWORD, POINTER(ctypes.c_void_p)),
    )

    hr = get_default_func(enumerator, EDATA_FLOW_CAPTURE, EROLE_CONSOLE, ctypes.byref(device_ptr))

    if hr < 0:
        raise ctypes.WinError(hr)

    return device_ptr.value


def _get_volume_endpoint():
    global _volume_endpoint

    if _volume_endpoint is None:
        device = _get_default_audio_device()

        try:
            endpoint_ptr = ctypes.c_void_p()

            vtbl = ctypes.cast(device, POINTER(POINTER(ctypes.c_void_p))).contents
            activate_func = ctypes.cast(
                vtbl[IMMDEVICE_ACTIVATE],
                ctypes.WINFUNCTYPE(
                    HRESULT, ctypes.c_void_p, POINTER(GUID), DWORD, ctypes.c_void_p, POINTER(ctypes.c_void_p)
                ),
            )

            hr = activate_func(
                device, ctypes.byref(IID_IAudioEndpointVolume), CLSCTX_ALL, None, ctypes.byref(endpoint_ptr)
            )

            if hr < 0:
                raise ctypes.WinError(hr)

            _volume_endpoint = endpoint_ptr.value

        finally:
            _com_release(device)

    return _volume_endpoint


def mic_block():
    """
    阻擋（靜音）麥克風
    """
    global _mic_muted

    with _mic_lock:
        try:
            endpoint = _get_volume_endpoint()

            vtbl = ctypes.cast(endpoint, POINTER(POINTER(ctypes.c_void_p))).contents
            set_mute_func = ctypes.cast(
                vtbl[IAUDIOENDPOINTVOLUME_SET_MUTE],
                ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, BOOL, POINTER(GUID)),
            )

            hr = set_mute_func(endpoint, True, None)
            if hr < 0:
                raise ctypes.WinError(hr)

            _mic_muted = True
        except Exception as e:
            raise RuntimeError(f"無法靜音麥克風: {e}")


def mic_unblock():
    """
    取消阻擋（取消靜音）麥克風
    """
    global _mic_muted

    with _mic_lock:
        try:
            endpoint = _get_volume_endpoint()

            vtbl = ctypes.cast(endpoint, POINTER(POINTER(ctypes.c_void_p))).contents
            set_mute_func = ctypes.cast(
                vtbl[IAUDIOENDPOINTVOLUME_SET_MUTE],
                ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, BOOL, POINTER(GUID)),
            )

            hr = set_mute_func(endpoint, False, None)
            if hr < 0:
                raise ctypes.WinError(hr)

            _mic_muted = False
        except Exception as e:
            raise RuntimeError(f"無法取消靜音麥克風: {e}")


def is_mic_blocked():
    """
    檢查麥克風是否被阻擋（靜音）
    返回 : True 表示被阻擋（靜音），False 表示未被阻擋
    """
    with _mic_lock:
        try:
            endpoint = _get_volume_endpoint()

            vtbl = ctypes.cast(endpoint, POINTER(POINTER(ctypes.c_void_p))).contents
            get_mute_func = ctypes.cast(
                vtbl[IAUDIOENDPOINTVOLUME_GET_MUTE], ctypes.WINFUNCTYPE(HRESULT, ctypes.c_void_p, POINTER(BOOL))
            )

            is_muted = BOOL()
            hr = get_mute_func(endpoint, ctypes.byref(is_muted))
            if hr < 0:
                raise ctypes.WinError(hr)

            return bool(is_muted.value)
        except Exception:
            return _mic_muted


def _cleanup():
    global _volume_endpoint, _device_enumerator, _com_initialized, _mic_muted

    if _mic_muted:
        try:
            mic_unblock()
        except:
            pass

    if _volume_endpoint:
        _com_release(_volume_endpoint)
        _volume_endpoint = None

    if _device_enumerator:
        _com_release(_device_enumerator)
        _device_enumerator = None

    if _com_initialized:
        ole32.CoUninitialize()
        _com_initialized = False


import atexit

atexit.register(_cleanup)
