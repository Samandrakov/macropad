# import win32api
# import win32con
# import time
# import logging
# import win32gui
#
# logging.basicConfig(level=logging.DEBUG)
# logger = logging.getLogger(__name__)
#
# def send_k_key():
#     """Функция для отправки клавиши K"""
#     try:
#         hwnd = 526520
#         # Key down
#         win32gui.SetForegroundWindow(hwnd)
#         win32api.keybd_event(0x4B, 0, 0, 0)
#         time.sleep(0.1)
#         # Key up
#         win32api.keybd_event(0x4B, 0, win32con.KEYEVENTF_KEYUP, 0)
#         logger.info("K key sent successfully")
#         return True
#     except Exception as e:
#         logger.error(f"Error sending K key: {e}")
#         return False
#
# # Тестируем отправку K
# for i in range(3):
#     print(f"Attempt {i+1} - Sending K key...")
#     send_k_key()
#     time.sleep(1)

# from pywinauto import Application
#
# app = Application(backend="uia").connect(title="Яндекс Музыка — собираем музыку для вас")
# app.top_window().set_focus()
# app.top_window().send_keystrokes('K')

# import uiautomation as auto
#
# def control_yandex():
#     yandex = auto.WindowControl(searchDepth=1, Name="Яндекс Музыка — собираем музыку для вас")
#     if yandex.Exists():
#         yandex.SetFocus()
#         yandex.SendKeys('K')
# control_yandex()

import ctypes
import time

# Структуры для SendInput
PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def press_key(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(hexKeyCode, 0x48, 0, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

    time.sleep(0.05)

    ii_.ki = KeyBdInput(hexKeyCode, 0x48, 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


# Использование
press_key(0x4B)  # Отправляем