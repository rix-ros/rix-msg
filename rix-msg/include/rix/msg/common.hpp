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
    template <typename U, U> struct really_has;

    // Check for size() method
    template <typename C>
    static char (&f(really_has<uint32_t (*)(), &C::size>*))[1];

    template <typename C>
    static char (&f(...))[2];

    // Check for decode() method
    template <typename C>
    static char (&g(really_has<const C* (*)(const void*, size_t), &C::decode>*))[1];

    template <typename C>
    static char (&g(...))[2];

    // Check for encode() method
    template <typename C>
    static char (&h(really_has<const void* (*)(const C*), &C::encode>*))[1];

    template <typename C>
    static char (&h(...))[2];

    // Check for def() method
    template <typename C>
    static char (&i(really_has<std::string (*)(), &C::def>*))[1];

    template <typename C>
    static char (&i(...))[2];

    // Check for hash() method
    template <typename C>
    static char (&j(really_has<Hash (*)(), &C::hash>*))[1];

    template <typename C>
    static char (&j(...))[2];

    // Check for operator<< method
    template <typename C>
    static auto k(int) -> decltype(std::declval<std::ostream&>() << std::declval<C>(), char(0));

    template <typename C>
    static char k(...);


public:
    static constexpr bool value = sizeof(f<T>(0)) == 1 && sizeof(g<T>(0)) == 1 && sizeof(h<T>(0)) == 1 && sizeof(i<T>(0)) == 1 && sizeof(j<T>(0)) == 1 && sizeof(k<T>(0)) == 1;
};

#define ASSERT_RIXMSG_TYPE(T) static_assert(rix::msg::is_rixmsg_type<T>::value, "Type is not a rixmsg type")

} // namespace rix
} // namespace msg