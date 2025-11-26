#include <LowPower.h>
#include <LiquidCrystal.h>
#include <DHT.h>
#include <TimeLib.h> // Incluye la librería Time

// --- Configuración Adaptada a la Imagen ---
// El pin de datos del DHT11 (cable verde) está conectado a A0
#define DHTTYPE DHT11  // DHT 11
const int DHTPin = A0; // Pin A0 conectado al DHT11

// Pines de control del LCD según la imagen:
// RS -> A5 (Cable Naranja)
// E  -> 13 (Cable Púrpura)
// D4 -> 8  (Cable Blanco)
// D5 -> 7  (Cable Blanco)
// D6 -> 6  (Cable Blanco)
// D7 -> 5  (Cable Blanco)
// NOTA: RW está conectado a GND, lo cual es correcto para el modo de solo escritura.
// NOTA: El potenciómetro controla el contraste (V0).
LiquidCrystal lcd(A5, 13, 8, 7, 6, 5);

DHT dht(DHTPin, DHTTYPE);

void setup() {
  Serial.begin(9600);
  lcd.begin(16, 2);   // Inicia un LCD 16x02 (columnas, fila)
  dht.begin();        // Inicia el sensor de temp y humedad
  
  // Inicializa la librería Time
  setTime(0, 0, 0, 1, 1, 2023); // Establece la fecha y hora inicial
}

void loop() {
  float h = dht.readHumidity();
  float t = dht.readTemperature();

  if (isnan(h) || isnan(t)) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("DHT Error");
    // Muestra el mensaje de error por 10 segundos antes de intentar leer de nuevo
    for (int i = 0; i < 75; i++) { // 75 ciclos * 8s por ciclo = 600s = 10 minutos
      LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
    }
    return;
  }

  // --- Muestra Temperatura y Humedad ---
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Temp: ");
  lcd.print(t);
  lcd.print((char)223); // Carácter de grado (°)
  lcd.print("C");

  lcd.setCursor(0, 1);
  lcd.print("Hum: ");
  lcd.print(h);
  lcd.print("%");

  // --- Muestra la Fecha ---
  // Obtén la fecha y hora actual
  tmElements_t tm;
  breakTime(now(), tm);

  lcd.setCursor(9, 0); // Lo ponemos en la línea superior para mejor visualización
  lcd.print(tm.Day);
  lcd.print("/");
  lcd.print(tm.Month);
  lcd.print("/");
  lcd.print(tmYearToCalendar(tm.Year));

  // --- Modo Sleep ---
  // El ciclo LowPower.powerDown(SLEEP_8S, ...) se ejecuta 30 veces (30 * 8 segundos = 240 segundos = 4 minutos)
  for (int i = 0; i < 30; i++) {
    LowPower.powerDown(SLEEP_8S, ADC_OFF, BOD_OFF);
  }

  // Después de despertar del modo de bajo consumo, imprime un mensaje
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("Despertando...");
  delay(2000); // Muestra el mensaje por 2 segundos antes de la siguiente medición
}