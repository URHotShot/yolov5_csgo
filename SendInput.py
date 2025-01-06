from ctypes import windll, c_long, c_ulong, Structure, Union, c_int, POINTER, sizeof

# 定義基本數據類型
LONG=c_long
DWORD=c_ulong
ULONG_PTR=POINTER(DWORD)

# 定義 MOUSEINPUT 結構，用於表示滑鼠輸入事件
class MOUSEINPUT(Structure):
    _fields_=(('dx', LONG),          #滑鼠的絕對x 座標
              ('dy', LONG),          #滑鼠的絕對y 座標
              ('mouseData', DWORD),  #指定滾輪移動的數量
              ('dwFlags', DWORD),    #一組位旗標，指定滑鼠動作和按鈕點選的各種層面
              ('time', DWORD),       #事件的時間戳記
              ('dwExtraInfo', ULONG_PTR))#滑鼠事件相關聯的額外值

# 定義 _INPUTunion 聯合體，用於在輸入結構中包含滑鼠輸入結構
class _INPUTunion(Union):
    _fields_=(('mi', MOUSEINPUT),)

# 定義 INPUT 結構，用於表示輸入事件
class INPUT(Structure):
    _fields_=(('type', DWORD),
              ('union', _INPUTunion))


# 定義 SendInput 函數，用於發送輸入事件
def SendInput(*inputs):
    nInputs=len(inputs)                 # 輸入事件的數量
    LPINPUT=INPUT * nInputs             # 創建輸入事件數組
    pInputs=LPINPUT(*inputs)            # 將輸入事件打包到數組中
    cbSize =c_int(sizeof(INPUT))        # 計算 INPUT 結構的大小
    return windll.user32.SendInput(nInputs, pInputs, cbSize)# 調用 Windows API 發送輸入事件

# 定義輔助函數，用於創建 INPUT 結構
def Input(structure):
    return INPUT(0, _INPUTunion(mi=structure))

# 定義輔助函數，用於創建 MOUSEINPUT 結構
def MouseInput(flags, x, y, data):
    return MOUSEINPUT(x, y, data, flags, 0, None)

# 定義輔助函數，用於創建滑鼠事件的 Input 結構
def Mouse(flags, x=0, y=0, data=0):
    return Input(MouseInput(flags, x, y, data))

#移動鼠標
def mouse_xy(x, y):
    return SendInput(Mouse(0x0001, x, y))   # 發送滑鼠移動事件

#按下鼠標(1左鍵/2右鍵)
def mouse_down(key=1):
    if key==1:
        return SendInput(Mouse(0x0002))     # 發送左鍵按下事件
    elif key==2:
        return SendInput(Mouse(0x0008))     # 發送右鍵按下事件

#鬆開鼠標(1左鍵/2右鍵)
def mouse_up(key=1):
    if key==1:
        return SendInput(Mouse(0x0004))     # 發送左鍵鬆開事件
    elif key==2:
        return SendInput(Mouse(0x0010))     # 發送右鍵鬆開事件