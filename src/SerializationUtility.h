#ifndef SERIALIZATION_UTILITY_H
#define SERIALIZATION_UTILITY_H

#include <StandardDefines.h>
#include <ArduinoJson.h>
#include <string>
#include <sstream>
#include <type_traits>
#include <stdexcept>
#include <algorithm>
#include <cctype>
#include <vector>
#include <list>
#include <deque>
#include <set>
#include <unordered_set>
#include <map>
#include <unordered_map>
#include <array>
#include <forward_list>

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
        } else if constexpr (is_sequential_container_v<T>) {
            // Handle sequential containers (vector, list, deque, set, unordered_set, etc.)
            return serialize_sequential_container(value);
        } else if constexpr (is_associative_container_v<T>) {
            // Handle associative containers (map, unordered_map)
            return serialize_associative_container(value);
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
     * Type trait to check if a type is a sequential container.
     * Includes: vector, list, deque, set, unordered_set, array, forward_list
     */
    template<typename T>
    struct is_sequential_container {
        static constexpr bool value = false;
    };
    
    template<typename T, typename Alloc>
    struct is_sequential_container<std::vector<T, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Alloc>
    struct is_sequential_container<std::list<T, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Alloc>
    struct is_sequential_container<std::deque<T, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Compare, typename Alloc>
    struct is_sequential_container<std::set<T, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Hash, typename Equal, typename Alloc>
    struct is_sequential_container<std::unordered_set<T, Hash, Equal, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename T, std::size_t N>
    struct is_sequential_container<std::array<T, N>> {
        static constexpr bool value = true;
    };
    
    template<typename T, typename Alloc>
    struct is_sequential_container<std::forward_list<T, Alloc>> {
        static constexpr bool value = true;
    };
    
    // Handle StandardDefines typedefs (vector, list, etc.)
    template<typename T>
    struct is_sequential_container<vector<T>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    struct is_sequential_container<list<T>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    struct is_sequential_container<deque<T>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    struct is_sequential_container<set<T>> {
        static constexpr bool value = true;
    };
    
    template<typename T>
    struct is_sequential_container<unordered_set<T>> {
        static constexpr bool value = true;
    };
    
    
    // Helper variable template
    template<typename T>
    static constexpr bool is_sequential_container_v = is_sequential_container<T>::value;
    
    /**
     * Type trait to check if a type is an associative container (map).
     * Includes: map, unordered_map, multimap, unordered_multimap
     */
    template<typename T>
    struct is_associative_container {
        static constexpr bool value = false;
    };
    
    template<typename Key, typename Value, typename Compare, typename Alloc>
    struct is_associative_container<std::map<Key, Value, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename Key, typename Value, typename Hash, typename Equal, typename Alloc>
    struct is_associative_container<std::unordered_map<Key, Value, Hash, Equal, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename Key, typename Value, typename Compare, typename Alloc>
    struct is_associative_container<std::multimap<Key, Value, Compare, Alloc>> {
        static constexpr bool value = true;
    };
    
    template<typename Key, typename Value, typename Hash, typename Equal, typename Alloc>
    struct is_associative_container<std::unordered_multimap<Key, Value, Hash, Equal, Alloc>> {
        static constexpr bool value = true;
    };
    
    // Handle StandardDefines typedefs (std_map)
    template<typename Key, typename Value>
    struct is_associative_container<std_map<Key, Value>> {
        static constexpr bool value = true;
    };
    
    // Helper variable template
    template<typename T>
    static constexpr bool is_associative_container_v = is_associative_container<T>::value;
    
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
    
    /**
     * Serialize a sequential container (vector, list, deque, set, etc.) to JSON array.
     */
    template<typename Container>
    static StdString serialize_sequential_container(const Container& container) {
        JsonDocument doc;
        JsonArray array = doc.to<JsonArray>();
        
        for (const auto& element : container) {
            if constexpr (is_primitive_type_v<typename Container::value_type>) {
                // For primitives, add directly to array
                if constexpr (std::is_same_v<typename Container::value_type, bool> || 
                              std::is_same_v<typename Container::value_type, Bool> ||
                              std::is_same_v<typename Container::value_type, CBool>) {
                    array.add(element);
                } else if constexpr (std::is_same_v<typename Container::value_type, StdString> ||
                                     std::is_same_v<typename Container::value_type, CStdString> ||
                                     std::is_same_v<typename Container::value_type, std::string>) {
                    array.add(element.c_str());
                } else if constexpr (std::is_integral_v<typename Container::value_type>) {
                    array.add(static_cast<int64_t>(element));
                } else if constexpr (std::is_floating_point_v<typename Container::value_type>) {
                    array.add(static_cast<double>(element));
                } else {
                    // Fallback: serialize and parse
                    StdString elementJson = Serialize(element);
                    JsonDocument elemDoc;
                    if (deserializeJson(elemDoc, elementJson.c_str()) == DeserializationError::Ok) {
                        array.add(elemDoc.as<JsonVariant>());
                    } else {
                        array.add(elementJson.c_str());
                    }
                }
            } else {
                // For complex types, serialize to JSON string, then parse and add
                StdString elementJson = Serialize(element);
                JsonDocument elementDoc;
                DeserializationError error = deserializeJson(elementDoc, elementJson.c_str());
                if (error == DeserializationError::Ok) {
                    array.add(elementDoc.as<JsonVariant>());
                } else {
                    // If parsing fails, add as string (shouldn't happen for valid JSON)
                    array.add(elementJson.c_str());
                }
            }
        }
        
        StdString output;
        serializeJson(doc, output);
        return StdString(output.c_str());
    }
    
    /**
     * Serialize an associative container (map, unordered_map) to JSON object.
     */
    template<typename Map>
    static StdString serialize_associative_container(const Map& map) {
        JsonDocument doc;
        JsonObject obj = doc.to<JsonObject>();
        
        for (const auto& pair : map) {
            // Serialize key
            StdString keyJson = Serialize(pair.first);
            StdString keyStr;
            
            if (is_primitive_type_v<typename Map::key_type>) {
                if constexpr (std::is_same_v<typename Map::key_type, StdString> ||
                              std::is_same_v<typename Map::key_type, CStdString> ||
                              std::is_same_v<typename Map::key_type, std::string>) {
                    keyStr = pair.first;
                } else {
                    keyStr = keyJson;
                }
            } else {
                // For complex key types, use the serialized JSON as key (may need adjustment)
                keyStr = keyJson;
            }
            
            // Serialize value
            StdString valueJson = Serialize(pair.second);
            
            // Parse value JSON and add to object
            JsonDocument valueDoc;
            DeserializationError error = deserializeJson(valueDoc, valueJson.c_str());
            if (error == DeserializationError::Ok) {
                obj[keyStr.c_str()] = valueDoc.as<JsonVariant>();
            } else {
                // If value is primitive, add directly
                if (is_primitive_type_v<typename Map::mapped_type>) {
                    if constexpr (std::is_same_v<typename Map::mapped_type, bool> ||
                                  std::is_same_v<typename Map::mapped_type, Bool> ||
                                  std::is_same_v<typename Map::mapped_type, CBool>) {
                        obj[keyStr.c_str()] = pair.second;
                    } else if constexpr (std::is_same_v<typename Map::mapped_type, StdString> ||
                                         std::is_same_v<typename Map::mapped_type, CStdString> ||
                                         std::is_same_v<typename Map::mapped_type, std::string>) {
                        obj[keyStr.c_str()] = pair.second.c_str();
                    } else if constexpr (std::is_integral_v<typename Map::mapped_type>) {
                        obj[keyStr.c_str()] = static_cast<int64_t>(pair.second);
                    } else if constexpr (std::is_floating_point_v<typename Map::mapped_type>) {
                        obj[keyStr.c_str()] = static_cast<double>(pair.second);
                    } else {
                        obj[keyStr.c_str()] = valueJson.c_str();
                    }
                } else {
                    // For complex types, parse and add
                    JsonDocument valDoc;
                    if (deserializeJson(valDoc, valueJson.c_str()) == DeserializationError::Ok) {
                        obj[keyStr.c_str()] = valDoc.as<JsonVariant>();
                    } else {
                        obj[keyStr.c_str()] = valueJson.c_str();
                    }
                }
            }
        }
        
        StdString output;
        serializeJson(doc, output);
        return StdString(output.c_str());
    }
};

} // namespace serialization
} // namespace nayan

#endif // SERIALIZATION_UTILITY_H

