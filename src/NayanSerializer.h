#ifndef NAYANSERIALIZER_H
#define NAYANSERIALIZER_H

#include <optional>
using std::optional;

#define Serializable
#define NotNull /* Validation Function -> nayan::validation::ValidationUtility::ValidateNotNull */
#define NotEmpty /* Validation Function -> nayan::validation::ValidationUtility::ValidateNotEmpty */
#define NotBlank /* Validation Function -> nayan::validation::ValidationUtility::ValidateNotBlank */

#include <ArduinoJson.h>
#include <StandardDefines.h>
#include "ValidationIncludes.h"

#endif // NAYANSERIALIZER_H
