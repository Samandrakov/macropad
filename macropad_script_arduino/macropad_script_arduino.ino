const int numButtons = 6; // Количество кнопок
const int buttons[] = {2, 3, 4, 5, 6, 7, 8, 9, 10}; // Пины кнопок
// const String commands[] = {"ENTER", "CTRL+C", "CTRL+V", "ALT+TAB", "MEDIA_NEXT", "VOL_UP"}; // Команды
const String commands[] = {
  "KEY-9",
  "KEY-8",
  "KEY-7",
  "KEY-6",
  "KEY-5",
  "KEY-4",
  "KEY-3",
  "KEY-2",
  "KEY-1",
};


int lastButtonStates[numButtons] = {HIGH}; // Состояния кнопок
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50; // Задержка для антидребезга

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttons[i], INPUT_PULLUP);
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  for (int i = 0; i < numButtons; i++) {
    int reading = digitalRead(buttons[i]);
    
    // Если состояние изменилось (учет дребезга)
    if (reading != lastButtonStates[i]) {
      lastDebounceTime = currentTime;
      lastButtonStates[i] = reading;
    }
    
    // Если прошло достаточно времени с момента последнего изменения
    if ((currentTime - lastDebounceTime) > debounceDelay) {
      // Если кнопка нажата (LOW, так как INPUT_PULLUP)
      if (reading == LOW) {
        Serial.println(commands[i]);
        while(digitalRead(buttons[i]) == LOW); // Ждем отпускания кнопки
      }
    }
  }
}