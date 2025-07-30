# tests/test_kb.py
import time

from stbz_lib import kb_block, kb_hold, kb_tap, kb_unblock
from stbz_lib._kb import get_blocked_keys, is_key_blocked

VK_W = 0x57
VK_A = 0x41
VK_S = 0x53
VK_D = 0x44

print("=== 鍵盤功能測試 ===")
print("請打開記事本查看輸出")
print("3秒後開始...")
time.sleep(3)

# 測試1：基本功能
print("\n測試1：基本功能")
print("- 單次按 W")
kb_tap(VK_W)
time.sleep(0.5)

print("- 連續按 A 3次")
kb_tap(VK_A, count=3, interval_ms=100)
time.sleep(0.5)

print("- 按住 S 1秒")
kb_hold(VK_S, duration_ms=1000)
time.sleep(0.5)

# 測試2：阻擋功能
print("\n測試2：阻擋功能")
print("- 阻擋 WASD")
kb_block([VK_W, VK_A, VK_S, VK_D])
print(f"  已阻擋 {len(get_blocked_keys())} 個按鍵")
print("- 請按 WASD（應該無效）...")
time.sleep(3)

print("- 取消阻擋 W")
kb_unblock([VK_W])
assert not is_key_blocked(VK_W)
assert is_key_blocked(VK_A)
print("- 請按 W（有效）和 ASD（無效）...")
time.sleep(2)

print("- 取消所有阻擋")
kb_unblock()
assert len(get_blocked_keys()) == 0

# 測試3：阻擋所有
print("\n測試3：阻擋所有按鍵")
kb_block()
print(f"- 已阻擋 {len(get_blocked_keys())} 個按鍵")
print("- 請按任意鍵（應該都無效）...")
time.sleep(2)
kb_unblock()

# 測試4：組合操作
print("\n測試4：組合操作")
print("- 前進(W) + 左右閃避(A-D)")
kb_hold(VK_W, duration_ms=1000)
kb_tap(VK_A)
time.sleep(0.2)
kb_tap(VK_D)

print("\n=== 測試完成 ===")
kb_unblock()  # 確保清理
