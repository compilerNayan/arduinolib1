#ifndef NAYANMATH_H
#define NAYANMATH_H

#include <ArduinoJson.h>

namespace NayanMath {

/**
 * Adds two integers and returns their sum
 * @param a First integer
 * @param b Second integer
 * @return Sum of a and b
 */
inline int add(int a, int b) {
    return a + b;
}

/**
 * Sample function that demonstrates ArduinoJson parsing
 * Parses a hardcoded JSON string and extracts values
 * @return Sum of parsed integer values, or -1 if parsing fails
 */
inline int parseJsonSample() {
    // Hardcoded JSON string
    const char* jsonString = R"({
        "sensor": "temperature",
        "value": 25,
        "unit": "celsius",
        "timestamp": 1234567890,
        "active": true
    })";
    
    // Parse JSON document
    StaticJsonDocument<200> doc;
    DeserializationError error = deserializeJson(doc, jsonString);
    
    // Check for parsing errors
    if (error) {
        return -1; // Return error code
    }
    
    // Extract values from JSON
    int value = doc["value"] | 0;           // Default to 0 if not found
    long timestamp = doc["timestamp"] | 0;    // Default to 0 if not found
    const char* sensor = doc["sensor"] | "unknown";
    bool active = doc["active"] | false;
    
    // Return sum of numeric values as example
    return value + (int)(timestamp % 1000); // Return value + last 3 digits of timestamp
}

} // namespace NayanMath

#endif // NAYANMATH_H

