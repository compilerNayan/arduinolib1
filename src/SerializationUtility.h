#ifndef SERIALIZATION_UTILITY_H
#define SERIALIZATION_UTILITY_H

#include <StandardDefines.h>
#include <string>
#include <sstream>
#include <type_traits>
#include <stdexcept>
#include <algorithm>
#include <cctype>

namespace nayan {
namespace serializer {

/**
 * Generic Serialization Utility
 * Provides a static template method to serialize any type.
 * 
 * For primitive types (int, char, bool, float, double, and types from StandardDefines),
 * converts the value to StdString.
 * 
 * For non-primitive types, calls the type's Serialize() method.
 */
class SerializationUtility {
public:
    /**
     * Serialize a value to StdString.
     * 
     * @tparam T The type to serialize
     * @param value The value to serialize
     * @return StdString representation of the value
     */
    template<typename T>
    static StdString Serialize(const T& value) {
        if constexpr (is_primitive_type_v<T>) {
            // Convert primitive type to string
            return convert_primitive_to_string(value);
        } else {
            // Call the type's Serialize method
            return value.Serialize();
        }
    }

    /**
     * Deserialize a string to a value of the specified type.
     * 
     * @tparam ReturnType The type to deserialize to
     * @param input The string input to deserialize
     * @return The deserialized value of type ReturnType
     */
    template<typename ReturnType>
    static ReturnType Deserialize(const StdString& input) {
        if constexpr (is_primitive_type_v<ReturnType>) {
            // Convert string to primitive type
            return convert_string_to_primitive<ReturnType>(input);
        } else {
            // Call the type's Deserialize method
            return ReturnType::Deserialize(input);
        }
    }

private:
    /**
     * Type trait to check if a type is a primitive type.
     * Includes: int, char, bool, float, double, and all types from StandardDefines.
     */
    template<typename T>
    struct is_primitive_type {
        static constexpr bool value = 
            std::is_same_v<T, int> || std::is_same_v<T, unsigned int> ||
            std::is_same_v<T, long> || std::is_same_v<T, unsigned long> ||
            std::is_same_v<T, short> || std::is_same_v<T, unsigned short> ||
            std::is_same_v<T, char> || std::is_same_v<T, unsigned char> ||
            std::is_same_v<T, bool> || std::is_same_v<T, float> ||
            std::is_same_v<T, double> || std::is_same_v<T, size_t> ||
            // StandardDefines types
            std::is_same_v<T, Int> || std::is_same_v<T, CInt> ||
            std::is_same_v<T, UInt> || std::is_same_v<T, CUInt> ||
            std::is_same_v<T, Long> || std::is_same_v<T, CLong> ||
            std::is_same_v<T, ULong> || std::is_same_v<T, CULong> ||
            std::is_same_v<T, UInt8> ||
            std::is_same_v<T, Char> || std::is_same_v<T, CChar> ||
            std::is_same_v<T, UChar> || std::is_same_v<T, CUChar> ||
            std::is_same_v<T, Bool> || std::is_same_v<T, CBool> ||
            std::is_same_v<T, Size> || std::is_same_v<T, CSize> ||
            std::is_same_v<T, StdString> || std::is_same_v<T, CStdString>;
    };
    
    // Helper variable template
    template<typename T>
    static constexpr bool is_primitive_type_v = is_primitive_type<T>::value;
    
    /**
     * Convert a primitive type to StdString.
     * Uses overloads for special cases.
     */
    template<typename T>
    static StdString convert_primitive_to_string(const T& value) {
        if constexpr (std::is_same_v<T, bool> || std::is_same_v<T, Bool> || std::is_same_v<T, CBool>) {
            return value ? "true" : "false";
        } else if constexpr (std::is_same_v<T, StdString>) {
            return value;
        } else if constexpr (std::is_same_v<T, CStdString>) {
            return StdString(value);
        } else {
            std::ostringstream oss;
            oss << value;
            return StdString(oss.str());
        }
    }
    
    /**
     * Convert a string to a primitive type.
     * 
     * @tparam T The primitive type to convert to
     * @param input The string input
     * @return The converted value of type T
     */
    template<typename T>
    static T convert_string_to_primitive(const StdString& input) {
        if constexpr (std::is_same_v<T, bool> || std::is_same_v<T, Bool> || std::is_same_v<T, CBool>) {
            // Handle boolean: "true", "false", "1", "0"
            StdString lower = input;
            std::transform(lower.begin(), lower.end(), lower.begin(), ::tolower);
            if (lower == "true" || lower == "1") {
                return true;
            } else if (lower == "false" || lower == "0") {
                return false;
            } else {
                throw std::invalid_argument("Invalid boolean value: " + input);
            }
        } else if constexpr (std::is_same_v<T, StdString> || std::is_same_v<T, CStdString>) {
            // Already a string, just return it
            return input;
        } else if constexpr (std::is_integral_v<T>) {
            // Integer types
            try {
                if constexpr (std::is_signed_v<T>) {
                    return static_cast<T>(std::stoll(input));
                } else {
                    return static_cast<T>(std::stoull(input));
                }
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid integer value: " + input);
            }
        } else if constexpr (std::is_floating_point_v<T>) {
            // Floating point types
            try {
                return static_cast<T>(std::stod(input));
            } catch (const std::exception& e) {
                throw std::invalid_argument("Invalid floating point value: " + input);
            }
        } else if constexpr (std::is_same_v<T, char> || std::is_same_v<T, Char> || std::is_same_v<T, CChar> ||
                             std::is_same_v<T, unsigned char> || std::is_same_v<T, UChar> || std::is_same_v<T, CUChar> ||
                             std::is_same_v<T, UInt8>) {
            // Character types
            if (input.length() == 1) {
                return static_cast<T>(input[0]);
            } else if (input.length() == 0) {
                return static_cast<T>(0);
            } else {
                // Try to parse as integer for character types
                try {
                    return static_cast<T>(std::stoi(input));
                } catch (const std::exception& e) {
                    throw std::invalid_argument("Invalid character value: " + input);
                }
            }
        } else {
            // Fallback: try to use stringstream
            std::istringstream iss(input);
            T value;
            if (!(iss >> value)) {
                throw std::invalid_argument("Cannot convert string to type: " + input);
            }
            return value;
        }
    }
};

} // namespace serialization
} // namespace nayan

#endif // SERIALIZATION_UTILITY_H

