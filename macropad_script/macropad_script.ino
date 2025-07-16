const int numButtons = 6; // Количество кнопок
const int buttonPins[] = {2, 3, 4, 5, 6, 7, 8, 9, 10}; // Пины кнопок
const char* commands[] = {
  "KEY-9",
  "KEY-8",
  "KEY-7",
  "KEY-6",
  "KEY-5",
  "KEY-4",
  "KEY-3",
  "KEY-2",
  "KEY-1"
};

int lastButtonStates[] = {HIGH, HIGH, HIGH, HIGH, HIGH, HIGH};
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50; // Задержка антидребезга (мс)

void setup() {
  Serial.begin(9600);
  for (int i = 0; i < numButtons; i++) {
    pinMode(buttonPins[i], INPUT_PULLUP); // Используем встроенные подтягивающие резисторы
  }
}

void loop() {
  unsigned long currentTime = millis();
  
  for (int i = 0; i < numButtons; i++) {
    int reading = digitalRead(buttonPins[i]);
    
    // Если состояние изменилось (учет дребезга)
    if (reading != lastButtonStates[i]) {
      lastDebounceTime = currentTime;
      lastButtonStates[i] = reading;
    }
    
    // Если прошло достаточно времени с момента последнего изменения
    if ((currentTime - lastDebounceTime) > debounceDelay) {
      // Если кнопка нажата (LOW, так как INPUT_PULLUP)
      if (reading == LOW) {
        Serial.println(commands[i]); // Отправляем команду
        while(digitalRead(buttonPins[i]) == LOW); // Ждем отпускания кнопки
        delay(20); // Короткая задержка после отпускания
      }
    }
  }
}