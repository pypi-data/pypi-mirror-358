"""
stbz_lib 對外 API。
"""

__version__ = "0.2.1"
__author__ = "bzstudio"
__license__ = "MIT"

from ._capture import capture
from ._close import close
from ._kb import kb_block, kb_hold, kb_tap, kb_unblock
from ._mic import mic_block, mic_unblock
from ._mouse import mouse_block, mouse_hold, mouse_move, mouse_pos, mouse_tap, mouse_unblock
from ._shutdown import reboot, shutdown

__all__ = [
    # 鍵盤
    "kb_block",
    "kb_unblock",
    "kb_tap",
    "kb_hold",
    # 滑鼠
    "mouse_block",
    "mouse_unblock",
    "mouse_tap",
    "mouse_hold",
    "mouse_pos",
    "mouse_move",
    # 截圖
    "capture",
    # 視窗控制
    "close",
    # 系統控制
    "shutdown",
    "reboot",
    # 麥克風
    "mic_block",
    "mic_unblock",
]
