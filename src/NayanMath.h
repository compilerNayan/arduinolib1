#ifndef NAYANMATH_H
#define NAYANMATH_H

#include <ArduinoJsonee.h>

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

} // namespace NayanMath

#endif // NAYANMATH_H

