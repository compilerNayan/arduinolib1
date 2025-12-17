#ifndef NAYANSERIALIZER_H
#define NAYANSERIALIZER_H

#include <optional>
using std::optional;

#define Serializable
#define NotNull /* Validation Function -> DtoValidationUtility::ValidateNotNull */
#define NotEmpty /* Validation Function -> DtoValidationUtility::ValidateNotEmpty */
#define NotBlank /* Validation Function -> DtoValidationUtility::ValidateNotBlank */

#include <ArduinoJson.h>
#include "DtoValidationUtility.h"
// Suppress deprecation warning for StaticJsonDocument until migration to JsonDocument with static allocator
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wdeprecated-declarations"

ArduinoJson::JsonDocument TestJson() {
    ArduinoJson::StaticJsonDocument<200> doc;
    const char* jsonString = "{\"name\":\"nayan\"}";
    ArduinoJson::deserializeJson(doc, jsonString);
    return doc;
}

#pragma GCC diagnostic pop

int addNayan(int a, int b) {
    return a + b + 100;
}


#endif // NAYANSERIALIZER_H
