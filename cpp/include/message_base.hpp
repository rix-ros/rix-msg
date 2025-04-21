#pragma once

#include <cstdint>
#include <string>
#include <vector>
#include <array>

namespace rix {
namespace msg {

class MessageBase {
   public:
    virtual size_t size() const = 0;
    virtual std::array<uint64_t, 2> hash() const = 0;
    virtual void serialize(std::vector<uint8_t> &buffer) const = 0;
    virtual void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) = 0;
};

namespace detail {

template <typename T>
inline void serialize_base(const T &val, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    const uint8_t *data = reinterpret_cast<const uint8_t *>(&val);
    buffer.insert(buffer.end(), data, data + sizeof(T));
}

template <typename T>
inline void serialize_base_vec(const std::vector<T> &vec, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t size = vec.size();
    serialize_base(size, buffer);
    const uint8_t *data = reinterpret_cast<const uint8_t *>(vec.data());
    buffer.insert(buffer.end(), data, data + size * sizeof(T));
}

template <typename T, size_t N>
inline void serialize_base_arr(const std::array<T, N> &arr, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    const uint8_t *data = reinterpret_cast<const uint8_t *>(arr.data());
    buffer.insert(buffer.end(), data, data + N * sizeof(T));
}

inline void serialize_custom(const MessageBase &msg, std::vector<uint8_t> &buffer) { msg.serialize(buffer); }

template <typename TMsg>
inline void serialize_custom_vec(const std::vector<TMsg> &vec, std::vector<uint8_t> &buffer) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    uint32_t size = vec.size();
    serialize_base(size, buffer);
    for (const auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->serialize(buffer);
    }
}

template <typename TMsg, size_t N>
inline void serialize_custom_arr(const std::array<TMsg, N> &arr, std::vector<uint8_t> &buffer) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    for (const auto &msg : arr) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->serialize(buffer);
    }
}

inline void serialize_string(const std::string &str, std::vector<uint8_t> &buffer) {
    uint32_t size = str.size();
    serialize_base(size, buffer);
    const uint8_t *data = reinterpret_cast<const uint8_t *>(str.data());
    buffer.insert(buffer.end(), data, data + size);
}

inline void serialize_string_vec(const std::vector<std::string> &vec, std::vector<uint8_t> &buffer) {
    uint32_t size = vec.size();
    serialize_base(size, buffer);
    for (const auto &str : vec) {
        serialize_string(str, buffer);
    }
}

template <size_t N>
inline void serialize_string_arr(const std::array<std::string, N> &arr, std::vector<uint8_t> &buffer) {
    for (const auto &str : arr) {
        serialize_string(str, buffer);
    }
}

template <typename T>
inline void deserialize_base(T &val, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    val = *reinterpret_cast<const T *>(buffer.data() + offset);
    offset += sizeof(T);
}

template <typename T>
inline void deserialize_base_vec(std::vector<T> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");

    uint32_t size;
    deserialize_base(size, buffer, offset);
    vec.resize(size);

    size_t len = size * sizeof(T);  // length of data in bytes
    size_t stop = offset + len;     // end of data
    uint8_t *data = reinterpret_cast<uint8_t *>(vec.data());
    std::copy(buffer.begin() + offset, buffer.begin() + stop, data);
    offset += len;
}

template <typename T, size_t N>
inline void deserialize_base_arr(std::array<T, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    size_t len = N * sizeof(T);  // length of data in bytes
    size_t stop = offset + len;  // end of data
    uint8_t *data = reinterpret_cast<uint8_t *>(arr.data());
    std::copy(buffer.begin() + offset, buffer.begin() + stop, data);
    offset += len;
}

inline void deserialize_custom(MessageBase &msg, const std::vector<uint8_t> &buffer, size_t &offset) {
    msg.deserialize(buffer, offset);
}

template <typename TMsg>
inline void deserialize_custom_vec(std::vector<TMsg> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");

    uint32_t size;
    deserialize_base(size, buffer, offset);
    vec.resize(size);

    for (auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->deserialize(buffer, offset);
    }
}

template <typename TMsg, size_t N>
inline void deserialize_custom_arr(std::array<TMsg, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    for (auto &msg : arr) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->deserialize(buffer, offset);
    }
}

inline void deserialize_string(std::string &str, const std::vector<uint8_t> &buffer, size_t &offset) {
    uint32_t size;
    deserialize_base(size, buffer, offset);
    const uint8_t *data = reinterpret_cast<const uint8_t *>(buffer.data() + offset);
    str = std::string(data, data + size);
    offset += size;
}

inline void deserialize_string_vec(std::vector<std::string> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    uint32_t size;
    deserialize_base(size, buffer, offset);
    vec.resize(size);

    for (auto &elt : vec) {
        deserialize_string(elt, buffer, offset);
    }
}

template <size_t N>
inline void deserialize_string_arr(std::array<std::string, N> &arr, const std::vector<uint8_t> &buffer,
                                   size_t &offset) {
    for (auto &elt : arr) {
        deserialize_string(elt, buffer, offset);
    }
}

template <typename T>
inline size_t size_base(const T &val) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return sizeof(T);
}

template <typename T>
inline size_t size_base_vec(const std::vector<T> &vec) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return sizeof(uint32_t) + vec.size() * sizeof(T);
}

template <typename T, size_t N>
inline size_t size_base_arr(const std::array<T, N> &arr) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return N * sizeof(T);
}

inline size_t size_custom(const MessageBase &msg) { return msg.size(); }

template <typename TMsg>
inline size_t size_custom_vec(const std::vector<TMsg> &vec) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    size_t size = sizeof(uint32_t);
    for (const auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        size += ptr->size();
    }
    return size;
}

template <typename TMsg, size_t N>
inline size_t size_custom_arr(const std::array<TMsg, N> &vec) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    size_t size = 0;
    for (const auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        size += ptr->size();
    }
    return size;
}

inline size_t size_string(const std::string &str) { return sizeof(uint32_t) + str.size(); }

inline size_t size_string_vec(const std::vector<std::string> &vec) {
    size_t size = sizeof(uint32_t);
    for (const auto &str : vec) {
        size += size_string(str);
    }
    return size;
}

template <size_t N>
inline size_t size_string_arr(const std::array<std::string, N> &arr) {
    size_t size = 0;
    for (const auto &str : arr) {
        size += size_string(str);
    }
    return size;
}

}  // namespace detail

}  // namespace msg
}  // namespace rix