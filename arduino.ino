#include <DHT.h>

#define DHTPIN 2          // Pin connected to DHT22 data pin
#define DHTTYPE DHT22     // DHT 22  (AM2302)
#define MOISTURE_PIN A0   // Pin connected to the soil moisture sensor

DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  // Read moisture level from soil moisture sensor
  int moistureValue = analogRead(MOISTURE_PIN);  // Read the moisture value
  int moisturePercentage = map(moistureValue, 0, 1023, 0, 100);  // Map it to a percentage

  // Read temperature and humidity from DHT22
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();  // Temperature in Celsius

  // Check if any readings failed
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
  } else {
    // Send moisture, temperature, and humidity to serial
    Serial.print(moisturePercentage);
    Serial.print(",");  // Separate each value with a comma
    Serial.print(temperature);
    Serial.print(",");  // Separate each value with a comma
    Serial.println(humidity);
  }

  delay(2000);  // Wait 2 seconds before the next reading
}
