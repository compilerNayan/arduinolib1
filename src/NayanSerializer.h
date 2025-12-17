#ifndef NAYANSERIALIZER_H
#define NAYANSERIALIZER_H

#include <optional>
using std::optional;

#define Serializable
#define NotNull /* Validation Function -> nayan::validation::DtoValidationUtility::ValidateNotNull */
#define NotEmpty /* Validation Function -> nayan::validation::DtoValidationUtility::ValidateNotEmpty */
#define NotBlank /* Validation Function -> nayan::validation::DtoValidationUtility::ValidateNotBlank */

#include <ArduinoJson.h>
#include "StandardDefines.h"
#include "ValidationIncludes.h"

#endif // NAYANSERIALIZER_H
