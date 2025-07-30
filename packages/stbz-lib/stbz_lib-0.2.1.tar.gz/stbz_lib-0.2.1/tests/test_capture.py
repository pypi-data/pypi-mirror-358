# tests/test_capture.py
from stbz_lib import capture

print("=== 截圖測試 ===")
print("測試截取 PUBG...")

try:
    img, info = capture("PUBG:")
    print("✓ 成功截取 PUBG")
    print(f"  HWND: {info['hwnd']}")
    print(f"  位置: ({info['x']}, {info['y']})")
    print(f"  大小: {info['width']} x {info['height']}")
    print(f"  圖像: {img.shape} {img.dtype}")
except RuntimeError as e:
    print(f"✗ PUBG - {e}")

print("\n=== 測試完成 ===")
