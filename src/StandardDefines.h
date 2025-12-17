#ifndef STANDARDEFINES_H
#define STANDARDEFINES_H

#include <string>
#include <optional>

// Arduino/ESP32 compatible integer types
typedef int Int;
typedef const int CInt;
typedef unsigned int UInt;
typedef const unsigned int CUInt;
typedef long Long;
typedef const long CLong;
typedef unsigned long ULong;
typedef const unsigned long CULong;
typedef unsigned char UInt8;

// Character types
typedef char Char;
typedef const char CChar;
typedef unsigned char UChar;
typedef const unsigned char CUChar;

// Boolean type
typedef bool Bool;
typedef const bool CBool;

// Size type
typedef size_t Size;
typedef const size_t CSize;

// Pointer types
typedef void* VoidPtr;
typedef const void* CVoidPtr;
typedef void Void;

// String types
typedef std::string StdString;
typedef const std::string CStdString;
using std::optional;

#define Var auto
#define Val const auto
#define Const constexpr auto

#define Private public: private:
#define Protected public: protected:
#define Public private: public:
#define Static static
#define Virtual virtual
#define Explicit explicit
#define NoDiscard [[nodiscard]]


#endif // STANDARDEFINES_H