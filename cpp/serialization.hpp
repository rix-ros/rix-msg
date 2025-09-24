#pragma once

#include <array>
#include <cstdint>
#include <cstring>
#include <map>
#include <string>
#include <vector>

#include "rix/msg/message.hpp"

namespace rix {
namespace msg {
namespace detail {
/**
 * Size functions return the number of bytes that `src` will occupy in the
 * serialized buffer.
 */

template <typename T>
inline uint32_t size_number(const T &src) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return sizeof(src);
}
inline uint32_t size_string(const std::string &src) { return 4 + src.size(); }
inline uint32_t size_message(const Message &src) { return src.size(); }

template <typename T, size_t N>
inline uint32_t size_number_array(const std::array<T, N> &src) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return N * sizeof(src[0]);
}
template <size_t N>
inline uint32_t size_string_array(const std::array<std::string, N> &src) {
    uint32_t size = 0;
    for (const auto &s : src) size += size_string(s);
    return size;
}
template <typename T, size_t N>
inline uint32_t size_message_array(const std::array<T, N> &src) {
    static_assert(std::is_base_of<Message, T>::value, "T must derive from Message");
    uint32_t size = 0;
    for (const auto &m : src) size += size_message(m);
    return size;
}

template <typename T>
inline uint32_t size_number_vector(const std::vector<T> &src) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return 4 + src.size() * sizeof(T);
}
inline uint32_t size_string_vector(const std::vector<std::string> &src) {
    uint32_t size = 4;
    for (const auto &s : src) size += size_string(s);
    return size;
}
template <typename T>
inline uint32_t size_message_vector(const std::vector<T> &src) {
    static_assert(std::is_base_of<Message, T>::value, "T must derive from Message");
    uint32_t size = 4;
    for (const auto &m : src) size += size_message(m);
    return size;
}

template <typename K, typename V>
inline uint32_t size_number_to_number_map(const std::map<K, V> &src) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    static_assert(std::is_arithmetic<V>::value, "V must be an arithmetic type");
    return 8 + src.size() * (sizeof(K) + sizeof(V));
}
template <typename K>
inline uint32_t size_number_to_string_map(const std::map<K, std::string> &src) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    size_t size = 8 + src.size() * sizeof(K);
    for (const auto &s : src) size += size_string(s.second);
    return size;
}
template <typename K, typename V>
inline uint32_t size_number_to_message_map(const std::map<K, V> &src) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    static_assert(std::is_base_of<Message, V>::value, "V must derive from Message");
    size_t size = 8 + src.size() * sizeof(K);
    for (const auto &s : src) size += size_message(s.second);
    return size;
}
template <typename V>
inline uint32_t size_string_to_number_map(const std::map<std::string, V> &src) {
    static_assert(std::is_arithmetic<V>::value, "V must be an arithmetic type");
    size_t size = 8 + src.size() * sizeof(V);
    for (const auto &s : src) size += size_string(s.first);
    return size;
}
inline uint32_t size_string_to_string_map(const std::map<std::string, std::string> &src) {
    size_t size = 8;
    for (const auto &s : src) size += size_string(s.first) + size_string(s.second);
    return size;
}
template <typename V>
inline uint32_t size_string_to_message_map(const std::map<std::string, V> &src) {
    static_assert(std::is_base_of<Message, V>::value, "V must derive from Message");
    size_t size = 8;
    for (const auto &s : src) size += size_string(s.first) + size_message(s.second);
    return size;
}

/**
 * Serialize functions convert the Message into a string of bytes and stores it
 * into the specified destination byte array. The size of the byte array can
 * be calculate beforehand using `Message::size()`. The size of the `dst` array
 * must be at least this many bytes.
 */

template <typename T>
inline void serialize_number(uint8_t *dst, size_t &offset, const T &src) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    std::memcpy(dst + offset, &src, sizeof(T));
    offset += sizeof(T);
}
inline void serialize_string(uint8_t *dst, size_t &offset, const std::string &src) {
    uint32_t size = src.size();
    std::memcpy(dst + offset, &size, 4);
    offset += 4;
    std::memcpy(dst + offset, src.data(), size);
    offset += size;
}
inline void serialize_message(uint8_t *dst, size_t &offset, const Message &src) { src.serialize(dst, offset); }
template <typename T, size_t N>
inline void serialize_number_array(uint8_t *dst, size_t &offset, const std::array<T, N> &src) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t size = N * sizeof(T);
    std::memcpy(dst + offset, src.data(), size);
    offset += size;
}
template <size_t N>
inline void serialize_string_array(uint8_t *dst, size_t &offset, const std::array<std::string, N> &src) {
    for (const auto &s : src) serialize_string(dst, offset, s);
}
template <typename T, size_t N>
inline void serialize_message_array(uint8_t *dst, size_t &offset, const std::array<T, N> &src) {
    static_assert(std::is_base_of<Message, T>::value, "T must derive from Message");
    for (const auto &m : src) serialize_message(dst, offset, m);
}
template <typename T>
inline void serialize_number_vector(uint8_t *dst, size_t &offset, const std::vector<T> &src) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t size = src.size();
    serialize_number(dst, offset, size);
    size *= sizeof(T);
    std::memcpy(dst + offset, src.data(), size);
    offset += size;
}
inline void serialize_string_vector(uint8_t *dst, size_t &offset, const std::vector<std::string> &src) {
    uint32_t size = src.size();
    serialize_number(dst, offset, size);
    for (const auto &s : src) serialize_string(dst, offset, s);
}
template <typename T>
inline void serialize_message_vector(uint8_t *dst, size_t &offset, const std::vector<T> &src) {
    static_assert(std::is_base_of<Message, T>::value, "T must derive from Message");
    uint32_t size = src.size();
    serialize_number(dst, offset, size);
    for (const auto &m : src) serialize_message(dst, offset, m);
}
template <typename K, typename V>
inline void serialize_number_to_number_map(uint8_t *dst, size_t &offset, const std::map<K, V> &src) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    static_assert(std::is_arithmetic<V>::value, "V must be an arithmetic type");
    uint32_t size = src.size();
    std::vector<K> k;
    std::vector<V> v;
    k.reserve(size);
    v.reserve(size);
    for (const auto &p : src) {
        k.push_back(p.first);
        v.push_back(p.second);
    }
    serialize_number_vector(dst, offset, k);
    serialize_number_vector(dst, offset, v);
}
template <typename K>
inline void serialize_number_to_string_map(uint8_t *dst, size_t &offset, const std::map<K, std::string> &src) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    uint32_t size = src.size();
    std::vector<K> k;
    std::vector<std::string> v;
    k.reserve(size);
    v.reserve(size);
    for (const auto &p : src) {
        k.push_back(p.first);
        v.push_back(p.second);
    }
    serialize_number_vector(dst, offset, k);
    serialize_string_vector(dst, offset, v);
}
template <typename K, typename V>
inline void serialize_number_to_message_map(uint8_t *dst, size_t &offset, const std::map<K, V> &src) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    static_assert(std::is_base_of<Message, V>::value, "V must derive from Message");
    uint32_t size = src.size();
    std::vector<K> k;
    std::vector<V> v;
    k.reserve(size);
    v.reserve(size);
    for (const auto &p : src) {
        k.push_back(p.first);
        v.push_back(p.second);
    }
    serialize_number_vector(dst, offset, k);
    serialize_message_vector(dst, offset, v);
}
template <typename V>
inline void serialize_string_to_number_map(uint8_t *dst, size_t &offset, const std::map<std::string, V> &src) {
    static_assert(std::is_arithmetic<V>::value, "V must be an arithmetic type");
    uint32_t size = src.size();
    std::vector<std::string> k;
    std::vector<V> v;
    k.reserve(size);
    v.reserve(size);
    for (const auto &p : src) {
        k.push_back(p.first);
        v.push_back(p.second);
    }
    serialize_string_vector(dst, offset, k);
    serialize_number_vector(dst, offset, v);
}
inline void serialize_string_to_string_map(uint8_t *dst, size_t &offset,
                                           const std::map<std::string, std::string> &src) {
    uint32_t size = src.size();
    std::vector<std::string> k;
    std::vector<std::string> v;
    k.reserve(size);
    v.reserve(size);
    for (const auto &p : src) {
        k.push_back(p.first);
        v.push_back(p.second);
    }
    serialize_string_vector(dst, offset, k);
    serialize_string_vector(dst, offset, v);
}
template <typename V>
inline void serialize_string_to_message_map(uint8_t *dst, size_t &offset, const std::map<std::string, V> &src) {
    static_assert(std::is_base_of<Message, V>::value, "V must derive from Message");
    uint32_t size = src.size();
    std::vector<std::string> k;
    std::vector<V> v;
    k.reserve(size);
    v.reserve(size);
    for (const auto &p : src) {
        k.push_back(p.first);
        v.push_back(p.second);
    }
    serialize_string_vector(dst, offset, k);
    serialize_message_vector(dst, offset, v);
}

/**
 * The deserialize functions convert a byte array into a Message. Because
 * Messages support dynamically sized arrays, we cannot determine beforehand if
 * deserialization will be successful without parsing the bytes. These functions
 * return false if there are not enough bytes in the `src` array to completely
 * deserialize.
 */
template <typename T>
inline bool deserialize_number(T &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    if (offset + sizeof(T) > size) return false;
    dst = *reinterpret_cast<const T *>(src + offset);
    offset += sizeof(T);
    return true;
}
inline bool deserialize_string(std::string &dst, const uint8_t *src, size_t size, size_t &offset) {
    uint32_t str_size;
    if (!deserialize_number(str_size, src, size, offset)) return false;
    if (offset + str_size > size) return false;
    dst.resize(str_size);
    std::memcpy(dst.data(), src + offset, str_size);
    offset += str_size;
    return true;
}
inline bool deserialize_message(Message &dst, const uint8_t *src, size_t size, size_t &offset) {
    return dst.deserialize(src, size, offset);
}
template <typename T, size_t N>
inline bool deserialize_number_array(std::array<T, N> &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t arr_size = N * sizeof(T);
    if (offset + arr_size > size) return false;
    std::memcpy(dst.data(), src + offset, arr_size);
    offset += arr_size;
    return true;
}
template <size_t N>
inline bool deserialize_string_array(std::array<std::string, N> &dst, const uint8_t *src, size_t size, size_t &offset) {
    for (auto &s : dst) {
        if (!deserialize_string(s, src, size, offset)) return false;
    }
    return true;
}
template <typename T, size_t N>
inline bool deserialize_message_array(std::array<T, N> &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_base_of<Message, T>::value, "T must derive from Message");
    for (auto &m : dst) {
        if (!deserialize_message(m, src, size, offset)) return false;
    }
    return true;
}
template <typename T>
inline bool deserialize_number_vector(std::vector<T> &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t vec_size;
    if (!deserialize_number(vec_size, src, size, offset)) return false;
    if (offset + vec_size > size) return false;
    dst.resize(vec_size);
    size_t size_bytes = vec_size * sizeof(T);
    std::memcpy(dst.data(), src + offset, size_bytes);
    offset += size_bytes;
    return true;
}
inline bool deserialize_string_vector(std::vector<std::string> &dst, const uint8_t *src, size_t size, size_t &offset) {
    uint32_t vec_size;
    if (!deserialize_number(vec_size, src, size, offset)) return false;
    dst.resize(vec_size);
    for (auto &s : dst) {
        if (!deserialize_string(s, src, size, offset)) return false;
    }
    return true;
}
template <typename T>
inline bool deserialize_message_vector(std::vector<T> &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_base_of<Message, T>::value, "T must derive from Message");
    uint32_t vec_size;
    if (!deserialize_number(vec_size, src, size, offset)) return false;
    dst.resize(vec_size);
    for (auto &m : dst) {
        if (!deserialize_message(m, src, size, offset)) return false;
    }
    return true;
}
template <typename K, typename V>
inline bool deserialize_number_to_number_map(std::map<K, V> &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    static_assert(std::is_arithmetic<V>::value, "V must be an arithmetic type");
    std::vector<K> k;
    std::vector<V> v;
    if (!deserialize_number_vector(k, src, size, offset)) return false;
    if (!deserialize_number_vector(v, src, size, offset)) return false;
    const size_t n = k.size();
    if (n != v.size()) return false;
    for (size_t i = 0; i < n; i++) {
        dst.insert({k[i], v[i]});
    }
    return true;
}
template <typename K>
inline bool deserialize_number_to_string_map(std::map<K, std::string> &dst, const uint8_t *src, size_t size,
                                             size_t &offset) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    std::vector<K> k;
    std::vector<std::string> v;
    if (!deserialize_number_vector(k, src, size, offset)) return false;
    if (!deserialize_string_vector(v, src, size, offset)) return false;
    const size_t n = k.size();
    if (n != v.size()) return false;
    for (size_t i = 0; i < n; i++) {
        dst.insert({k[i], v[i]});
    }
    return true;
}
template <typename K, typename V>
inline bool deserialize_number_to_message_map(std::map<K, V> &dst, const uint8_t *src, size_t size, size_t &offset) {
    static_assert(std::is_arithmetic<K>::value, "K must be an arithmetic type");
    static_assert(std::is_base_of<Message, V>::value, "V must derive from Message");
    std::vector<K> k;
    std::vector<V> v;
    if (!deserialize_number_vector(k, src, size, offset)) return false;
    if (!deserialize_message_vector(v, src, size, offset)) return false;
    const size_t n = k.size();
    if (n != v.size()) return false;
    for (size_t i = 0; i < n; i++) {
        dst.insert({k[i], v[i]});
    }
    return true;
}
template <typename V>
inline bool deserialize_string_to_number_map(std::map<std::string, V> &dst, const uint8_t *src, size_t size,
                                             size_t &offset) {
    std::vector<std::string> k;
    std::vector<V> v;
    if (!deserialize_string_vector(k, src, size, offset)) return false;
    if (!deserialize_number_vector(v, src, size, offset)) return false;
    const size_t n = k.size();
    if (n != v.size()) return false;
    for (size_t i = 0; i < n; i++) {
        dst.insert({k[i], v[i]});
    }
    return true;
}
inline bool deserialize_string_to_string_map(std::map<std::string, std::string> &dst, const uint8_t *src, size_t size,
                                             size_t &offset) {
    std::vector<std::string> k;
    std::vector<std::string> v;
    if (!deserialize_string_vector(k, src, size, offset)) return false;
    if (!deserialize_string_vector(v, src, size, offset)) return false;
    const size_t n = k.size();
    if (n != v.size()) return false;
    for (size_t i = 0; i < n; i++) {
        dst.insert({k[i], v[i]});
    }
    return true;
}
template <typename V>
inline bool deserialize_string_to_message_map(std::map<std::string, V> &dst, const uint8_t *src, size_t size,
                                              size_t &offset) {
    static_assert(std::is_base_of<Message, V>::value, "V must derive from Message");
    std::vector<std::string> k;
    std::vector<V> v;
    if (!deserialize_string_vector(k, src, size, offset)) return false;
    if (!deserialize_message_vector(v, src, size, offset)) return false;
    const size_t n = k.size();
    if (n != v.size()) return false;
    for (size_t i = 0; i < n; i++) {
        dst.insert({k[i], v[i]});
    }
    return true;
}
}  // namespace detail
}  // namespace msg
}  // namespace rix