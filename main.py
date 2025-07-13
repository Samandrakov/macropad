import win32gui
import win32con
import win32api
import time
import logging
import serial
from ctypes import windll

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('macropad.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Коды клавиш для Яндекс.Музыки (из вашего первоначального кода)
COMMAND_ACTIONS = {
    "PLAY": 0x4B,  # K key
    "NEXT": 0x4E,  # N key
    "PREV": 0x50,  # P key
    "VOLUP": 0xAF,  # Volume Up
    "VOLDOWN": 0xAE,  # Volume Down
    "MUTE": 0xAD  # Volume Mute
}


def send_key(key_code):
    """Низкоуровневая отправка клавиши"""
    try:
        # Key down
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.05)  # Короткая задержка
        # Key up
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        logger.error(f"Key send error: {e}")
        return False


def find_yandex_window():
    """Поиск окна Яндекс.Музыки"""

    def callback(hwnd, extra):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and ("Яндекс" in title or "Yandex" in title):
                extra.append(hwnd)
        return True

    windows = []
    win32gui.EnumWindows(callback, windows)
    return windows[0] if windows else None


def activate_window(hwnd):
    """Активация окна Яндекс.Музыки"""
    try:
        # Если окно свернуто - восстановить
        if win32gui.IsIconic(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

        # Поднять окно на передний план
        win32gui.SetForegroundWindow(hwnd)
        time.sleep(0.1)  # Важная задержка для переключения окон
        return True
    except Exception as e:
        logger.error(f"Window activation error: {e}")
        return False


def start_macropad_service():
    """Основная функция управления макропадом"""
    try:
        logger.info('Starting macropad service...')

        # Находим окно Яндекс.Музыки один раз при старте
        yandex_window = find_yandex_window()
        if yandex_window:
            logger.info("Yandex Music window found")
        else:
            logger.warning("Yandex Music window not found - some commands may not work")

        with serial.Serial('COM3', 9600, timeout=1) as ser:
            logger.info(f'Connected to {ser.name}')

            while True:
                try:
                    data = ser.readline().decode('utf-8').strip()
                    if not data:
                        continue

                    logger.debug(f'Received: {data}')

                    if data in COMMAND_ACTIONS:
                        key = COMMAND_ACTIONS[data]

                        # Для управления громкостью не нужно активировать окно
                        if data in ("VOLUP", "VOLDOWN", "MUTE"):
                            send_key(key)
                        else:
                            # Для управления воспроизведением активируем окно
                            if yandex_window and activate_window(yandex_window):
                                send_key(key)
                                logger.info(f"Sent {data} command to Yandex Music")
                            else:
                                logger.warning("Failed to activate Yandex Music window")

                except UnicodeDecodeError as e:
                    logger.warning(f'Decode error: {e}')
                except Exception as e:
                    logger.error(f'Error processing data: {e}')

    except serial.SerialException as e:
        logger.critical(f'Serial port error: {e}')
    except KeyboardInterrupt:
        logger.info('Service stopped by user')
    except Exception as e:
        logger.error(f'Unexpected error: {e}')


if __name__ == '__main__':
    start_macropad_service()