# stbz_lib

Windows 平台的低階鍵盤滑鼠控制與視窗操作函式庫。

## 安裝

```bash
pip install stbz_lib
```

## API 參考

### 鍵盤控制

#### `kb_tap(key, count=1, interval_ms=50)`
模擬按鍵點擊。
- `key`: 虛擬鍵碼 (VK_*)
- `count`: 點擊次數
- `interval_ms`: 每次點擊的間隔時間（毫秒）

#### `kb_hold(key, duration_ms=100, count=1, interval_ms=50)`
模擬按住按鍵。在按住期間會阻擋外部對該按鍵的輸入。
- `key`: 虛擬鍵碼
- `duration_ms`: 按住持續時間（毫秒）
- `count`: 重複次數
- `interval_ms`: 每次重複的間隔時間（毫秒）

#### `kb_block(keys=None)`
阻擋鍵盤輸入。
- `keys`: 要阻擋的鍵碼列表，`None` 表示阻擋所有按鍵 (0x08-0xFE)

#### `kb_unblock(keys=None)`
取消鍵盤阻擋。
- `keys`: 要取消阻擋的鍵碼列表，`None` 表示取消所有阻擋

### 滑鼠控制

#### `mouse_tap(button, count=1, interval_ms=50)`
模擬滑鼠點擊。
- `button`: 滑鼠按鍵常數
  - `MOUSE_LEFT` (0x01): 左鍵
  - `MOUSE_RIGHT` (0x02): 右鍵
  - `MOUSE_MIDDLE` (0x03): 中鍵
  - `MOUSE_X1` (0x04): 側鍵1
  - `MOUSE_X2` (0x05): 側鍵2
- `count`: 點擊次數
- `interval_ms`: 每次點擊的間隔時間（毫秒）

#### `mouse_hold(button, duration_ms=100, count=1, interval_ms=50)`
模擬按住滑鼠按鍵。在按住期間會阻擋外部對該按鍵的輸入。
- `button`: 滑鼠按鍵常數
- `duration_ms`: 按住持續時間（毫秒）
- `count`: 重複次數
- `interval_ms`: 每次重複的間隔時間（毫秒）

#### `mouse_pos(x, y)`
移動滑鼠到指定座標。
- `x`: X 座標
- `y`: Y 座標

#### `mouse_move(direction, duration_ms=1000, speed=5)`
移動滑鼠到螢幕邊緣並持續往該方向移動。
- `direction`: 移動方向常數
  - `MOVE_UP` (0x10): 向上
  - `MOVE_DOWN` (0x11): 向下
  - `MOVE_LEFT` (0x12): 向左
  - `MOVE_RIGHT` (0x13): 向右
- `duration_ms`: 持續時間（毫秒）
- `speed`: 移動速度（每次移動的像素數）

#### `mouse_block(button_list=None)`
阻擋滑鼠操作。
- `button_list`: 要阻擋的按鍵列表，`None` 表示阻擋所有滑鼠操作（包含移動）

#### `mouse_unblock(button_list=None)`
取消阻擋滑鼠操作。
- `button_list`: 要取消阻擋的按鍵列表，`None` 表示取消所有阻擋

### 麥克風控制

#### `mic_block()`
阻擋（靜音）麥克風。將系統預設麥克風設為靜音狀態。

#### `mic_unblock()`
取消阻擋（取消靜音）麥克風。恢復麥克風的聲音輸入。

### 視窗截圖

#### `capture(name)`
截取符合名稱的視窗。
- `name`: 視窗標題（部分匹配）
- 返回: `(image, info)` 
  - `image`: numpy array，形狀為 (height, width, 3)，BGR 格式
  - `info`: 字典，包含 `hwnd`、`x`、`y`、`width`、`height`

### 進程終止

#### `close(name, delay_ms=0)`
強制關閉符合名稱的所有進程。
- `name`: 視窗標題（部分匹配）
- `delay_ms`: 每個進程終止之間的延遲（毫秒）
- 返回: 終止的進程數量

### 系統控制

#### `shutdown(force=True, delay_ms=0)`
關機。
- `force`: 是否強制關閉應用程式（預設為 `True`）
- `delay_ms`: 延遲時間（毫秒）

#### `reboot(force=True, delay_ms=0)`
重新開機。
- `force`: 是否強制關閉應用程式（預設為 `True`）
- `delay_ms`: 延遲時間（毫秒）

## 常數定義

### 滑鼠按鍵
```python
from stbz_lib._mouse import MOUSE_LEFT, MOUSE_RIGHT, MOUSE_MIDDLE, MOUSE_X1, MOUSE_X2, MOUSE_MOVE

MOUSE_LEFT = 0x01    # 滑鼠左鍵
MOUSE_RIGHT = 0x02   # 滑鼠右鍵
MOUSE_MIDDLE = 0x03  # 滑鼠中鍵
MOUSE_X1 = 0x04      # 滑鼠側鍵1
MOUSE_X2 = 0x05      # 滑鼠側鍵2
MOUSE_MOVE = 0x06    # 滑鼠移動（用於阻擋）
```

### 滑鼠移動方向
```python
from stbz_lib._mouse import MOVE_UP, MOVE_DOWN, MOVE_LEFT, MOVE_RIGHT

MOVE_UP = 0x10     # 向上移動
MOVE_DOWN = 0x11   # 向下移動
MOVE_LEFT = 0x12   # 向左移動
MOVE_RIGHT = 0x13  # 向右移動
```

### 虛擬鍵碼

使用 Windows 標準虛擬鍵碼 (Virtual-Key Codes)。

完整列表：https://docs.microsoft.com/en-us/windows/win32/inputdev/virtual-key-codes

## 系統需求

- Windows 作業系統
- Python 3.12+
- numpy 2.3.0
- 管理員權限（用於設置系統級 Hook）