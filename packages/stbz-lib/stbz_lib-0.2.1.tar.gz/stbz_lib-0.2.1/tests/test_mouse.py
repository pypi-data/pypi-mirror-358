# tests/test_mouse.py
import time

from stbz_lib import mouse_block, mouse_hold, mouse_move, mouse_pos, mouse_tap, mouse_unblock
from stbz_lib._mouse import (
    MOUSE_LEFT,
    MOUSE_MIDDLE,
    MOUSE_MOVE,
    MOUSE_RIGHT,
    MOVE_DOWN,
    MOVE_LEFT,
    MOVE_RIGHT,
    MOVE_UP,
    get_blocked_buttons,
    get_mouse_pos,
    is_button_blocked,
)

print("=== 滑鼠功能測試 ===")
print("確保螢幕上沒有重要操作")
print("3秒後開始...")
time.sleep(3)

# 測試1：基本功能
print("\n測試1：基本功能")
print("- 點擊左鍵")
mouse_tap(MOUSE_LEFT)
time.sleep(0.5)

print("- 雙擊左鍵")
mouse_tap(MOUSE_LEFT, count=2, interval_ms=50)
time.sleep(0.5)

print("- 按住右鍵 1秒")
mouse_hold(MOUSE_RIGHT, duration_ms=1000)
time.sleep(0.5)

# 測試2：移動功能
print("\n測試2：移動功能")
original_pos = get_mouse_pos()
print(f"- 原始位置: {original_pos}")

print("- 移動到 (300, 300)")
mouse_pos(300, 300)
time.sleep(0.5)

print("- 移動到 (500, 500)")
mouse_pos(500, 500)
time.sleep(0.5)

print("- 返回原位")
mouse_pos(*original_pos)

# 測試3：阻擋功能
print("\n測試3：阻擋功能")
print("- 阻擋左右鍵")
mouse_block([MOUSE_LEFT, MOUSE_RIGHT])
print(f"  已阻擋 {len(get_blocked_buttons())} 個按鍵")
print("- 請點擊滑鼠（應該無效）...")
time.sleep(3)

print("- 取消阻擋左鍵")
mouse_unblock([MOUSE_LEFT])
assert not is_button_blocked(MOUSE_LEFT)
assert is_button_blocked(MOUSE_RIGHT)
print("- 請點擊左鍵（有效）和右鍵（無效）...")
time.sleep(2)

print("- 取消所有阻擋")
mouse_unblock()
assert len(get_blocked_buttons()) == 0

# 測試4：阻擋移動
print("\n測試4：阻擋移動")
print("- 阻擋滑鼠移動")
mouse_block([MOUSE_MOVE])
print("- 請移動滑鼠（應該無法移動）...")
time.sleep(2)
mouse_unblock()

# 測試5：邊緣移動（安全測試）
print("\n測試5：邊緣移動（安全測試）")
try:
    print("- 先移到安全位置 (400, 400)")
    mouse_pos(400, 400)
    time.sleep(0.5)
    print("- 向上移動 0.3秒")
    mouse_move(MOVE_UP, duration_ms=300, speed=5)
    time.sleep(0.5)
except Exception as e:
    print(f"  邊緣移動測試跳過: {e}")

print("\n測試6：組合操作")
print("- 射擊(左鍵x3) + 瞄準(右鍵)")
mouse_tap(MOUSE_LEFT, count=3, interval_ms=100)
mouse_hold(MOUSE_RIGHT, duration_ms=1000)

print("\n=== 測試完成 ===")
mouse_unblock()  # 確保清理
