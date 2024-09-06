#include <type_traits>
#include <memory>

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
    static char (&g(really_has<std::shared_ptr<C> (*)(const std::shared_ptr<char>&), &C::decode>*))[1];

    template <typename C>
    static char (&g(...))[2];

    // Check for encode() method
    template <typename C>
    static char (&h(really_has<std::shared_ptr<char> (*)(const std::shared_ptr<C>&), &C::encode>*))[1];

    template <typename C>
    static char (&h(...))[2];

    // Check for def() method
    template <typename C>
    static char (&i(really_has<std::string (*)(), &C::def>*))[1];

    template <typename C>
    static char (&i(...))[2];


public:
    static constexpr bool value = sizeof(f<T>(0)) == 1 && sizeof(g<T>(0)) == 1 && sizeof(h<T>(0)) == 1 && sizeof(i<T>(0)) == 1;
};