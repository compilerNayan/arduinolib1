#ifndef SERIALIZATION_UTILITY_H
#define SERIALIZATION_UTILITY_H

#include <StandardDefines.h>
#include <string>
#include <sstream>
#include <type_traits>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <vector>
#include <set>
#include <map>
#include <optional>

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
        // Handle optional types first
        if constexpr (is_optional_v<T>) {
            return serialize_optional(value);
        }
        // Handle container types (vector, set, map, etc.)
        else if constexpr (is_container_v<T>) {
            return serialize_container(value);
        }
        // Handle string types as special case - return as StdString (no conversion needed)
        else if constexpr (std::is_same_v<T, std::string> || std::is_same_v<T, StdString>) {
            // std::string or StdString (which is std::string), return as-is
            return value;
        } else if constexpr (std::is_same_v<T, const std::string> || std::is_same_v<T, CStdString>) {
            // const std::string or CStdString (const), convert to StdString
            return StdString(value);
        } else if constexpr (is_primitive_type_v<T>) {
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
            // String types (treat as primitives - no Deserialize method needed)
            std::is_same_v<T, std::string> || std::is_same_v<T, const std::string> ||
            std::is_same_v<T, StdString> || std::is_same_v<T, CStdString> ||
            // StandardDefines types
            std::is_same_v<T, Int> || std::is_same_v<T, CInt> ||
            std::is_same_v<T, UInt> || std::is_same_v<T, CUInt> ||
            std::is_same_v<T, Long> || std::is_same_v<T, CLong> ||
            std::is_same_v<T, ULong> || std::is_same_v<T, CULong> ||
            std::is_same_v<T, UInt8> ||
            std::is_same_v<T, Char> || std::is_same_v<T, CChar> ||
            std::is_same_v<T, UChar> || std::is_same_v<T, CUChar> ||
            std::is_same_v<T, Bool> || std::is_same_v<T, CBool> ||
            std::is_same_v<T, Size> || std::is_same_v<T, CSize>;
    };
    
    // Helper variable template
    template<typename T>
    static constexpr bool is_primitive_type_v = is_primitive_type<T>::value;
    
    /**
     * Type trait to check if a type is std::optional.
     */
    template<typename T>
    struct is_optional {
        static constexpr bool value = false;
    };
    
    template<typename T>
    struct is_optional<std::optional<T>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    struct is_optional<optional<T>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    static constexpr bool is_optional_v = is_optional<T>::value;
    
    /**
     * Type trait to check if a type is a container (vector, set, map, etc.).
     */
    template<typename T>
    struct is_container {
        static constexpr bool value = false;
    };
    
    template<typename T, typename Alloc>
    struct is_container<std::vector<T, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Alloc>
    struct is_container<vector<T, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Compare, typename Alloc>
    struct is_container<std::set<T, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Compare, typename Alloc>
    struct is_container<std::multiset<T, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename Key, typename Value, typename Compare, typename Alloc>
    struct is_container<std::map<Key, Value, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename Key, typename Value, typename Compare, typename Alloc>
    struct is_container<std::multimap<Key, Value, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    static constexpr bool is_container_v = is_container<T>::value;
    
    /**
     * Type trait to check if a container is a map type.
     */
    template<typename T>
    struct is_map_container {
        static constexpr bool value = false;
    };
    
    template<typename Key, typename Value, typename Compare, typename Alloc>
    struct is_map_container<std::map<Key, Value, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename Key, typename Value, typename Compare, typename Alloc>
    struct is_map_container<std::multimap<Key, Value, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    static constexpr bool is_map_container_v = is_map_container<T>::value;
    
    /**
     * Serialize an optional value.
     * Returns empty string if not present, otherwise serializes the inner value.
     */
    template<typename T>
    static StdString serialize_optional(const T& opt_value) {
        if constexpr (is_optional_v<T>) {
            if (!opt_value.has_value()) {
                return StdString("");
            }
            // Get the inner type and serialize it
            using InnerType = typename T::value_type;
            return Serialize(opt_value.value());
        }
        return StdString("");
    }
    
    /**
     * Serialize a container (vector, set, map, etc.) to JSON array format.
     * Iterates through all elements and serializes each, returns JSON array.
     */
    template<typename Container>
    static StdString serialize_container(const Container& container) {
        StdString result = "[";
        bool first = true;
        
        for (const auto& element : container) {
            if (!first) {
                result += ",";
            }
            first = false;
            
            // Check if container is a map type
            if constexpr (is_map_container_v<Container>) {
                // For maps, serialize as {"key":...,"value":...}
                StdString key_serialized = Serialize(element.first);
                StdString value_serialized = Serialize(element.second);
                
                result += "{";
                result += "\"key\":";
                // Add key (may need quoting)
                if (key_serialized.empty() || key_serialized[0] == '{' || key_serialized[0] == '[') {
                    result += key_serialized;
                } else if (key_serialized.length() >= 2 && 
                          key_serialized[0] == '"' && key_serialized[key_serialized.length() - 1] == '"') {
                    result += key_serialized;
                } else {
                    StdString escaped = escape_json_string(key_serialized);
                    result += "\"";
                    result += escaped;
                    result += "\"";
                }
                result += ",\"value\":";
                // Add value (may be JSON object/array or primitive)
                if (value_serialized.empty() || 
                    (value_serialized[0] == '{' || value_serialized[0] == '[')) {
                    result += value_serialized;
                } else if (value_serialized.length() >= 2 && 
                          value_serialized[0] == '"' && value_serialized[value_serialized.length() - 1] == '"') {
                    result += value_serialized;
                } else {
                    StdString escaped = escape_json_string(value_serialized);
                    result += "\"";
                    result += escaped;
                    result += "\"";
                }
                result += "}";
            } else {
                // For non-map containers (vector, set, etc.), serialize element directly
                StdString serialized = Serialize(element);
                
                // If the serialized value is a JSON object/array (starts with { or [), add as-is
                // Otherwise, if it's a string, we need to escape it and wrap in quotes
                // For primitives, we can add as-is
                if (serialized.empty() || 
                    (serialized[0] == '{' || serialized[0] == '[')) {
                    // Already JSON object/array, add as-is
                    result += serialized;
                } else {
                    // String or primitive - check if it needs quotes
                    // If it's already a quoted string, use as-is, otherwise quote it
                    if (serialized.length() >= 2 && 
                        serialized[0] == '"' && serialized[serialized.length() - 1] == '"') {
                        // Already quoted, use as-is
                        result += serialized;
                    } else {
                        // Need to escape and quote
                        StdString escaped = escape_json_string(serialized);
                        result += "\"";
                        result += escaped;
                        result += "\"";
                    }
                }
            }
        }
        
        result += "]";
        return result;
    }
    
    /**
     * Type trait to check if a type is a std::pair.
     */
    template<typename T>
    struct is_pair {
        static constexpr bool value = false;
    };
    
    template<typename First, typename Second>
    struct is_pair<std::pair<First, Second>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    static constexpr bool is_pair_v = is_pair<T>::value;
    
    /**
     * Escape special characters in a JSON string.
     */
    static StdString escape_json_string(const StdString& str) {
        StdString escaped;
        escaped.reserve(str.length() + 10); // Reserve some extra space
        
        for (char c : str) {
            switch (c) {
                case '"':  escaped += "\\\""; break;
                case '\\': escaped += "\\\\"; break;
                case '\b': escaped += "\\b"; break;
                case '\f': escaped += "\\f"; break;
                case '\n': escaped += "\\n"; break;
                case '\r': escaped += "\\r"; break;
                case '\t': escaped += "\\t"; break;
                default:
                    // Control characters (0x00-0x1F) should be escaped as \uXXXX
                    if (c >= 0 && c < 32) {
                        char hex[7];
                        snprintf(hex, sizeof(hex), "\\u%04x", static_cast<unsigned char>(c));
                        escaped += hex;
                    } else {
                        escaped += c;
                    }
                    break;
            }
        }
        
        return escaped;
    }
    
    /**
     * Convert a primitive type to StdString.
     * Uses overloads for special cases.
     */
    template<typename T>
    static StdString convert_primitive_to_string(const T& value) {
        if constexpr (std::is_same_v<T, bool> || std::is_same_v<T, Bool> || std::is_same_v<T, CBool>) {
            return value ? "true" : "false";
        } else if constexpr (std::is_same_v<T, std::string> || std::is_same_v<T, StdString>) {
            // std::string or StdString (which is std::string), return as-is
            return value;
        } else if constexpr (std::is_same_v<T, const std::string> || std::is_same_v<T, CStdString>) {
            // const std::string or CStdString (const), convert to StdString
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
        } else if constexpr (std::is_same_v<T, std::string> || std::is_same_v<T, StdString>) {
            // std::string or StdString (which is std::string), return as-is (no conversion needed)
            return input;
        } else if constexpr (std::is_same_v<T, const std::string> || std::is_same_v<T, CStdString>) {
            // const std::string or CStdString (const), convert to StdString
            return StdString(input);
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

