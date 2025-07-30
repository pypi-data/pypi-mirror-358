import time

import stbz_lib


def 開火():
    """開一槍 (左鍵)"""
    stbz_lib.mouse_tap(0x01)


def 持續開火(duration_ms=5000):
    """
    持續開火 (左鍵)

    Args:
        duration_ms: 持續時間(毫秒)
    """
    stbz_lib.mouse_hold(0x01, duration_ms)


def 抬頭(duration_ms=800, speed=100):
    """
    抬頭 - 視角向上

    Args:
        duration_ms: 持續時間(毫秒)
        speed: 移動速度
    """
    stbz_lib.mouse_move(0x10, duration_ms, speed)


def 低頭(duration_ms=800, speed=100):
    """
    低頭 - 視角向下

    Args:
        duration_ms: 持續時間(毫秒)
        speed: 移動速度
    """
    stbz_lib.mouse_move(0x11, duration_ms, speed)


def 轉圈(duration_ms=5000, speed=100):
    """
    轉圈 - 360度旋轉視角

    Args:
        duration_ms: 總時間(毫秒)
        speed: 旋轉速度
    """
    stbz_lib.mouse_move(0x13, duration_ms / 2, speed)
    stbz_lib.mouse_move(0x12, duration_ms / 2, speed)


def 向前(duration_ms=5000):
    """
    向前移動 (W鍵)

    Args:
        duration_ms: 移動時間(毫秒)
    """
    stbz_lib.kb_hold(0x57, duration_ms)


def 向後(duration_ms=5000):
    """
    向後移動 (S鍵)

    Args:
        duration_ms: 移動時間(毫秒)
    """
    stbz_lib.kb_hold(0x53, duration_ms)


def 向左(duration_ms=5000):
    """
    向左移動 (A鍵)

    Args:
        duration_ms: 移動時間(毫秒)
    """
    stbz_lib.kb_hold(0x41, duration_ms)


def 向右(duration_ms=5000):
    """
    向右移動 (D鍵)

    Args:
        duration_ms: 移動時間(毫秒)
    """
    stbz_lib.kb_hold(0x44, duration_ms)


def 跳躍():
    """跳躍 (空白鍵)"""
    stbz_lib.kb_tap(0x20)


def 蹲下():
    """蹲下 (C鍵)"""
    stbz_lib.kb_tap(0x43)


def 趴下():
    """趴下 (Z鍵)"""
    stbz_lib.kb_tap(0x5A)


def 跳車():
    """跳車 - 按住 (F鍵) 3.5秒"""
    stbz_lib.kb_hold(0x46, 3500)


def 繳械():
    """
    繳械 - 自動丟棄武器
    支援解析度:
    - 1920x1080 (無邊框模式)
    - 1920x1080 (有邊框模式)
    - 1616x939 (視窗化模式)
    """
    image, info = stbz_lib.capture("PUBG:")
    width = info['width']
    height = info['height']
    window_x = info['x']
    window_y = info['y']

    print(f"解析度: {width}x{height}, 視窗位置: ({window_x}, {window_y})")

    if width == 1920 and height == 1080:
        coords = [(1311, 93), (1311, 318)]
    elif width == 1936 and height == 1119:
        coords = [(1327, 132), (1327, 357)]
    elif width == 1616 and height == 939:
        coords = [(1117, 107), (1117, 296)]
    else:
        return

    stbz_lib.kb_tap(0x09)

    for coord in coords:
        target_x, target_y = coord
        screen_x = window_x + target_x
        screen_y = window_y + target_y
        stbz_lib.mouse_pos(screen_x, screen_y)
        stbz_lib.mouse_tap(0x02)

    stbz_lib.kb_tap(0x09)
    stbz_lib.kb_unblock([0x10, 0xA0, 0xA1])


def 開地圖():
    """開啟地圖 (M鍵)"""
    stbz_lib.kb_tap(0x4D)


def 罰站(duration_ms=5000):
    """
    罰站 - 暫時無法移動(封鎖WASD)

    Args:
        duration_ms: 罰站時間(毫秒)
    """
    stbz_lib._kb._keyup(0x41)
    stbz_lib._kb._keyup(0x44)
    stbz_lib._kb._keyup(0x57)
    stbz_lib._kb._keyup(0x53)
    stbz_lib.kb_block([0x41, 0x44, 0x57, 0x53])
    time.sleep(duration_ms / 1000)
    stbz_lib.kb_unblock([0x41, 0x44, 0x57, 0x53])


def 禁止開火(duration_ms=5000):
    """
    禁止開火 - 暫時無法使用滑鼠左鍵

    Args:
        duration_ms: 禁止時間(毫秒)
    """
    stbz_lib.mouse_block([0x01])
    time.sleep(duration_ms / 1000)
    stbz_lib.mouse_unblock([0x01])


def 關遊戲(delay_ms=5000):
    """
    關閉遊戲

    Args:
        delay_ms: 延遲時間(毫秒)
    """
    stbz_lib.close("PUBG:", delay_ms)


if __name__ == "__main__":
    tests = [
        (開火, [], 3),
        (持續開火, [5000], 3),
        (抬頭, [800], 3),
        (向前, [5000], 3),
        (繳械, [], 3),
        (罰站, [5000], 3),
        (禁止開火, [5000], 0),
    ]

print("3秒後開始測試...")
time.sleep(3)

for i, (func, args, delay) in enumerate(tests, 3):
    print(f"{i}. 測試 {func.__name__}")
    func(*args)
    time.sleep(delay)

print("測試完成！")
