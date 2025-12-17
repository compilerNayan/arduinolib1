#ifndef NAYANSERIALIZER_H
#define NAYANSERIALIZER_H

#include <optional>
using std::optional;

#define Serializable
#define NotNull /* Validation Function -> DtoValidationUtility::ValidateNotNull */
#define NotEmpty /* Validation Function -> DtoValidationUtility::ValidateNotEmpty */
#define NotBlank /* Validation Function -> DtoValidationUtility::ValidateNotBlank */

#include <ArduinoJson.h>
#include "ValidationIncludes.h"

#endif // NAYANSERIALIZER_H
