#pragma once

#include <type_traits>
#include <memory>
#include <ostream>

namespace rix {
namespace msg {

struct Hash {
    uint64_t top;
    uint64_t bottom;

    Hash() : top(0), bottom(0) {}
    Hash(uint64_t top, uint64_t bottom) : top(top), bottom(bottom) {}

    bool operator==(const Hash &other) const {
        return top == other.top && bottom == other.bottom;
    }
    bool operator!=(const Hash &other) const {
        return !(*this == other);
    }
    bool operator<(const Hash &other) const {
        return top < other.top || (top == other.top && bottom < other.bottom);
    }
};


template <typename T>
class is_rixmsg_type {
  private:
    template <typename U, U> struct really_has;

    // Check for encode() method
    template <typename C>
    static char (&has_encode(really_has<const uint8_t* (C::*)() const, &C::encode>*))[1];

    template <typename C>
    static char (&has_encode(...))[2];

    // Check for decode() method
    template <typename C>
    static char (&has_decode(really_has<const C* (*)(const uint8_t*, size_t), &C::decode>*))[1];

    template <typename C>
    static char (&has_decode(...))[2];

    // Check for hash() method
    template <typename C>
    static char (&has_hash(really_has<Hash (*)(), &C::hash>*))[1];

    template <typename C>
    static char (&has_hash(...))[2];

  public:
    static constexpr bool value = sizeof(has_encode<T>(0)) == 1 && 
                                  sizeof(has_decode<T>(0)) == 1 && 
                                  sizeof(has_hash<T>(0)) == 1;
};

#define ASSERT_RIXMSG_TYPE(T) static_assert(rix::msg::is_rixmsg_type<T>::value, "Type is not a rixmsg type");

}
}