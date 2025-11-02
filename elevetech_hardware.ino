#include <HX711.h>

// Pin Definitions
#define MQ2_PIN     D18
#define SW420_PIN   D35
#define LM35_PIN    D5
#define HX711_DT    RXO
#define HX711_SCK   TXO
#define US_TRIG     D13
#define US_ECHO     D14
#define BF350_PIN   D19



HardwareSerial mySerial(2);

HX711 scale;

// Threshold values (tune for your project)
#define MQ2_THRESHOLD   600     // Gas value above this = possible leak
#define VIB_THRESHOLD   1       // SW420 vibration
#define TEMP_HIGH       40.0    // High temperature (°C)
#define TEMP_LOW        5.0     // Low temperature (°C)
#define WEIGHT_THRESHOLD 10.0   // Overload if weight exceeds this (kg, tune calibration)
#define ULTRA_THRESHOLD 30      // Obstacle if distance < this (cm)
#define BF350_THRESHOLD 1.0     // Example tension threshold (calibrate)

void setup() {
  Serial.begin(115200);
  mySerial.begin(9600, SERIAL_8N1, 16, 17);
  pinMode(MQ2_PIN, INPUT);
  pinMode(SW420_PIN, INPUT);
  pinMode(LM35_PIN, INPUT);
  pinMode(US_TRIG, OUTPUT);
  pinMode(US_ECHO, INPUT);
  pinMode(BF350_PIN, INPUT);

  scale.begin(HX711_DT, HX711_SCK);
}

long readUltrasonicCM(int trigPin, int echoPin) {
  digitalWrite(trigPin, LOW); delayMicroseconds(2);
  digitalWrite(trigPin, HIGH); delayMicroseconds(10); digitalWrite(trigPin, LOW);
  long duration = pulseIn(echoPin, HIGH, 30000);
  return duration * 0.034 / 2;
}

float readLM35() {
  int adcValue = analogRead(LM35_PIN);
  float voltage = adcValue * (3.3 / 4095.0);
  return voltage * 100.0;
}

float readBF350() {
  int value = analogRead(BF350_PIN);
  float voltage = value * (3.3 / 4095.0);
  return voltage;
}

void loop() {
  int mq2Value = analogRead(MQ2_PIN);
  int sw420State = digitalRead(SW420_PIN);
  float lm35Temp = readLM35();
  float hx711Weight = scale.get_units(10);
  long distance = readUltrasonicCM(US_TRIG, US_ECHO);
  float bf350Val = readBF350();

  // Detailed printout per sensor
  Serial.println("===== Elevator Shaft Monitoring Report =====");

  Serial.print("Gas sensor (MQ2): "); Serial.println(mq2Value);
  if (mq2Value > MQ2_THRESHOLD) Serial.println("WARNING: Possible gas/smoke detected!");

  Serial.print("Vibration (SW420): ");
  if (sw420State >= VIB_THRESHOLD) Serial.println("High vibrations detected!");
  else Serial.println("Normal vibration level.");

  Serial.print("Temperature (LM35): "); Serial.print(lm35Temp); Serial.println(" °C");
  if (lm35Temp > TEMP_HIGH) Serial.println("ALERT: Over-temperature risk!");
  else if (lm35Temp < TEMP_LOW) Serial.println("ALERT: Below safe temperature range!");

  Serial.print("Load (HX711/BF350): "); Serial.print(hx711Weight); Serial.print(" kg");
  Serial.print(" / Tension value: "); Serial.println(bf350Val);
  if (hx711Weight > WEIGHT_THRESHOLD) Serial.println("WARNING: Possible shaft overload!");
  if (bf350Val < BF350_THRESHOLD) Serial.println("ALERT: Low tension/wear risk!");

  Serial.print("Obstacle distance (Ultrasonic): "); Serial.print(distance); Serial.println(" cm");
  if (distance < ULTRA_THRESHOLD) Serial.println("WARNING: Obstruction/close obstacle detected!");

  Serial.println("===========================================");
  Serial.println();

  // Send structured results to ESP32-CAM (can add status codes/messages if desired)
  String outStr = String(mq2Value) + "," +
                  String(sw420State) + "," +
                  String(lm35Temp) + "," +
                  String(hx711Weight) + "," +
                  String(distance) + "," +
                  String(bf350Val);
  mySerial.println(outStr);

  delay(3000); // 3 seconds delay
}
