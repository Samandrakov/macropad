import tkinter as tk
from tkinter import ttk
import threading
import queue
import time
import win32gui
import win32con
import win32api
import win32process
import logging
import serial
import psutil

# Оригинальный код макропада без изменений
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        # logging.FileHandler('macropad.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

FILENAME = 'yaamp.exe'
TARGET_CLASS = 'Chrome_WidgetWin_1'
COMMAND_ACTIONS = {
    "KEY-9": 0x43,  # C key
    "KEY-8": 0x42,  # B key
    "KEY-7": 0x5A,  # Z key
    "KEY-6": 0xAF,  # Volume Up
    "KEY-5": 0xAE,  # Volume Down
    "KEY-4": 0xAD,  # Volume Mute
    "KEY-3": None,
    "KEY-2": None,
    "KEY-1": None,
}


def find_and_maximize_window():
    """Оригинальная функция без изменений"""
    window_opened = False
    target_class = "Chrome_WidgetWin_1"
    target_processes = ["yaamp.exe", "winamp.exe"]

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

                        if win32gui.IsIconic(hwnd):
                            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)

                        win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
                        win32gui.SetForegroundWindow(hwnd)
                return None

            hwnd = win32gui.EnumWindows(callback, None)
    return None


def send_key(key_code):
    """Оригинальная функция без изменений"""
    try:
        win32api.keybd_event(key_code, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(key_code, 0, win32con.KEYEVENTF_KEYUP, 0)
        return True
    except Exception as e:
        logger.error(f"Key send error: {e}")
        return False


class MacroPadOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MacroPad Controller")
        self.root.attributes('-alpha', 0.85)
        self.root.attributes('-topmost', True)
        self.root.overrideredirect(True)
        self.root.geometry('300x200+50+50')
        self._offset_x = 0
        self._offset_y = 0
        self.message_queue = queue.Queue()
        self.create_widgets()
        self.check_queue()
        self.bind_events()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        self.title_label = ttk.Label(
            main_frame,
            text="MacroPad Controller",
            font=('Arial', 10, 'bold')
        )
        self.title_label.pack(pady=(0, 10))

        self.status_label = ttk.Label(
            main_frame,
            text="Status: Disconnected",
            font=('Arial', 8)
        )
        self.status_label.pack(anchor=tk.W)

        self.last_command_label = ttk.Label(
            main_frame,
            text="Last command: None",
            font=('Arial', 8)
        )
        self.last_command_label.pack(anchor=tk.W, pady=(5, 0))

        self.last_time_label = ttk.Label(
            main_frame,
            text="Last time: Never",
            font=('Arial', 8)
        )
        self.last_time_label.pack(anchor=tk.W)

        close_btn = ttk.Button(
            main_frame,
            text="X",
            width=3,
            command=self.root.destroy
        )
        close_btn.place(relx=1.0, x=-2, y=2, anchor=tk.NE)

        minimize_btn = ttk.Button(
            main_frame,
            text="_",
            width=3,
            command=self.root.iconify
        )
        minimize_btn.place(relx=1.0, x=-30, y=2, anchor=tk.NE)

    def bind_events(self):
        self.title_label.bind("<ButtonPress-1>", self.start_move)
        self.title_label.bind("<B1-Motion>", self.on_move)
        self.title_label.bind("<Double-Button-1>", lambda e: self.root.iconify())

    def start_move(self, event):
        self._offset_x = event.x
        self._offset_y = event.y

    def on_move(self, event):
        x = self.root.winfo_pointerx() - self._offset_x
        y = self.root.winfo_pointery() - self._offset_y
        self.root.geometry(f"+{x}+{y}")

    def update_status(self, status):
        self.status_label.config(text=f"Status: {status}")

    def update_last_command(self, command):
        current_time = time.strftime("%H:%M:%S")
        self.last_command_label.config(text=f"Last command: {command}")
        self.last_time_label.config(text=f"Last time: {current_time}")

    def check_queue(self):
        try:
            while True:
                message = self.message_queue.get_nowait()
                if message.startswith("STATUS:"):
                    self.update_status(message[7:])
                elif message.startswith("COMMAND:"):
                    self.update_last_command(message[8:])
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)

    def run(self):
        self.root.mainloop()


def start_macropad_service(overlay):
    """Оригинальная функция с добавлением обновления интерфейса"""
    try:
        overlay.message_queue.put("STATUS:Starting macropad service...")
        logger.info('Starting macropad service...')

        with serial.Serial('COM3', 9600, timeout=1) as ser:
            overlay.message_queue.put("STATUS:Connected to COM3")
            logger.info(f'Connected to {ser.name}')

            while True:
                try:
                    data = ser.readline().decode('utf-8').strip()
                    if not data:
                        continue

                    logger.debug(f'Received: {data}')
                    overlay.message_queue.put(f"COMMAND:{data}")

                    if data in COMMAND_ACTIONS:
                        key = COMMAND_ACTIONS[data]

                        if data in ("KEY-6", "KEY-5", "KEY-4"):  # Volume controls
                            send_key(key)
                        else:
                            find_and_maximize_window()
                            send_key(key)
                            logger.info(f"Sent {data} command to {FILENAME}")

                except UnicodeDecodeError as e:
                    logger.warning(f'Decode error: {e}')
                except Exception as e:
                    logger.error(f'Error processing data: {e}')
                    overlay.message_queue.put(f"STATUS:Error: {str(e)}")

    except serial.SerialException as e:
        logger.critical(f'Serial port error: {e}')
        overlay.message_queue.put(f"STATUS:Serial error: {str(e)}")
    except KeyboardInterrupt:
        logger.info('Service stopped by user')
        overlay.message_queue.put("STATUS:Stopped by user")
    except Exception as e:
        logger.error(f'Unexpected error: {e}')
        overlay.message_queue.put(f"STATUS:Unexpected error: {str(e)}")


if __name__ == '__main__':
    overlay = MacroPadOverlay()
    macropad_thread = threading.Thread(
        target=start_macropad_service,
        args=(overlay,),
        daemon=True
    )
    macropad_thread.start()
    overlay.run()