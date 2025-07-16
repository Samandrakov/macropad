import win32gui
import win32con
import win32api
import win32process
import time
import logging
import serial
import psutil

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('macropad.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

FILENAME = 'yaamp.exe'
TARGET_CLASS = 'Chrome_WidgetWin_1' #Класс приложения
#Команды на вход с ардуино
COMMAND_ACTIONS = {
    "KEY-9": 0x43,  # C key
    "KEY-8": 0x42,  # B key
    "KEY-7": 0x5A,  # Z key
    "KEY-6": 0xAF,  # Volume Up
    "KEY-5": 0xAE,  # Volume Down
    "KEY-4": 0xAD,  # Volume Mute
    "KEY-3": None  # Volume Mute
    "KEY-2": None  # Volume Mute
    "KEY-1": None  # Volume Mute
}

def find_and_maximize_window():
    """Находит и разворачивает окно с классом Chrome_WidgetWin_1"""
    window_opened = False

    target_class = "Chrome_WidgetWin_1"
    target_processes = ["yaamp.exe", "winamp.exe"]  # Добавьте другие нужные процессы

    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'].lower() in target_processes:
            pid = proc.pid
            print(f"Найден процесс: {proc.info['name']} (PID: {pid})")

            def callback(hwnd, extra):
                _, window_pid = win32process.GetWindowThreadProcessId(hwnd)
                if window_pid == pid:
                    class_name = win32gui.GetClassName(hwnd)
                    if class_name == target_class:
                        title = win32gui.GetWindowText(hwnd)
                        print(f"Найдено целевое окно: HWND={hwnd}, Заголовок='{title}'")

                        if win32gui.IsIconic(hwnd):  # Если свернуто
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)

                        # Поднимаем на передний план
                        win32gui.SetForegroundWindow(hwnd)

                return None
            hwnd = win32gui.EnumWindows(callback, None)
    return None


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

def start_macropad_service():
    """Основная функция управления макропадом"""
    try:
        logger.info('Starting macropad service...')

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
                            find_and_maximize_window()

                            send_key(key)
                            logger.info(f"Sent {data} command to {FILENAME}")


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