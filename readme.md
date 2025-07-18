# MacroPad Controller for Yaamp

Программа для управления медиа через макропад на базе arduino nano. Поддерживает горячие клавиши, управление громкостью и автоматическую активацию целевых окон.
Решение представлено на микроконтроллере без hid функций (CH340C).
## 📋 Требования

- Windows 10/11
- Python 3.12
- Arduino nano с прошивкой для макропада (CH340C/UART)
- Драйвер CH340 ([скачать](http://www.wch.cn/downloads/CH341SER_EXE.html))
- Кастомный плеер yaamp (winamp)

## ⚙️ Установка

### Загрузка скрипта на микроконтроллер

1. Запустите arduino ide
2. Подключите arduino к COM-порту
3. Проверьте скрипт из macropad/macropad_script_arduino на валидность 
4. Если используется больше/меньше кнопок в вашем макропаде, измените следующие переменные

Ключи вывода при нажатии на кнопку
```Arduino
const String commands[] = {
  "KEY-9",
  "KEY-8",
  "KEY-7",
   # ... другие ключи
};
```
Пины кнопок
```Arduino
const int buttons[] = {2, 3, 4, 5, 6, 7, 8, 9, 10};
```


3. Загрузите скрипт

### Порядок подключения свитчей

### Установка macropad контроллера 
1. Установите зависимости:
```bash
pip install -r requirements.txt
```
2. Проверьте номер порта в скрипте на совпадение с вашем в диспетчере устройств или arduino ide 
3. Настройте бинд кнопок в соответствии с нужными ключами клавиш - словарь COMMAND_ACTIONS. 
```pyhton
COMMAND_ACTIONS = {
    "KEY-9": 0x43,  # Код клавиши C
    "KEY-8": 0x42,  # Код клавиши B
    # ... другие клавиши
}
```
4. Настройте нужное для работы вам приложение изменив: 
   1. FILENAME - название процесса; 
   2. TARGET_CLASS - класс процесса.

### Соберите проект:
   
```bash
pyinstaller macropad_script.spec
```
## TODO
- [ ] Собрать базовый gui на PyQt5
- [ ] Задать возможность бинда в gui
- [ ] Задать возможность выбора окна-процесса из gui
- [ ] Совместимость с linux
- [ ] Тесты
