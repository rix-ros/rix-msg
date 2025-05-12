#pragma once

#include <array>
#include <cstdint>
#include <string>
#include <vector>

namespace rix {
namespace msg {

class MessageBase {
   public:
    virtual size_t size() const = 0;
    virtual std::array<uint64_t, 2> hash() const = 0;
    virtual bool serialize(std::vector<uint8_t> &buffer) const = 0;
    virtual bool deserialize(const std::vector<uint8_t> &buffer, size_t &offset) = 0;
};

namespace detail {

inline bool has_capacity_at_offset(const std::vector<uint8_t> &buffer, size_t offset, size_t size) {
    return buffer.size() >= offset + size;
}

template <typename T>
inline void serialize_base(const T &val, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    // if (!can_expand_without_overflow(buffer, sizeof(T))) {
    //     return false;
    // }
    const uint8_t *data = reinterpret_cast<const uint8_t *>(&val);
    buffer.insert(buffer.end(), data, data + sizeof(T));
    // return true;
}

template <typename T>
inline void serialize_base_vec(const std::vector<T> &vec, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t size = vec.size();
    // if (!serialize_base(size, buffer)) {
    //     return false;
    // }
    serialize_base(size, buffer);
    // if (!can_expand_without_overflow(buffer, size * sizeof(T))) {
    //     return false;
    // }
    const uint8_t *data = reinterpret_cast<const uint8_t *>(vec.data());
    buffer.insert(buffer.end(), data, data + size * sizeof(T));
    // return true;
}

template <typename T, size_t N>
inline void serialize_base_arr(const std::array<T, N> &arr, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    // if (!can_expand_without_overflow(buffer, N * sizeof(T))) {
    //     return false;
    // }
    const uint8_t *data = reinterpret_cast<const uint8_t *>(arr.data());
    buffer.insert(buffer.end(), data, data + N * sizeof(T));
    // return true;
}

inline void serialize_custom(const MessageBase &msg, std::vector<uint8_t> &buffer) {
    // if (!can_expand_without_overflow(buffer, msg.size())) {
    //     return false;
    // }
    // return msg.serialize(buffer);
    msg.serialize(buffer);
}

template <typename TMsg>
inline void serialize_custom_vec(const std::vector<TMsg> &vec, std::vector<uint8_t> &buffer) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    uint32_t size = vec.size();
    // if (!serialize_base(size, buffer)) {
    //     return false;
    // }
    serialize_base(size, buffer);
    for (const auto &msg : vec) {
        // Use the serialize member function to avoid calculating size
        // if (!msg.serialize(buffer)) {
        //     return false;
        // }
        msg.serialize(buffer);
    }
    // return true;
}

template <typename TMsg, size_t N>
inline void serialize_custom_arr(const std::array<TMsg, N> &arr, std::vector<uint8_t> &buffer) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    for (const auto &msg : arr) {
        // Use the serialize member function to avoid calculating size
        // if (!msg.serialize(buffer)) {
        //     return false;
        // }
        msg.serialize(buffer);
    }
    // return true;
}

inline void serialize_string(const std::string &str, std::vector<uint8_t> &buffer) {
    uint32_t size = str.size();
    // if (!serialize_base(size, buffer)) {
    //     return false;
    // }
    serialize_base(size, buffer);
    // if (!can_expand_without_overflow(buffer, size)) {
    //     return false;
    // }
    const uint8_t *data = reinterpret_cast<const uint8_t *>(str.data());
    buffer.insert(buffer.end(), data, data + size);
    // return true;
}

inline void serialize_string_vec(const std::vector<std::string> &vec, std::vector<uint8_t> &buffer) {
    uint32_t size = vec.size();
    // if (!serialize_base(size, buffer)) {
    //     return false;
    // }
    serialize_base(size, buffer);
    for (const auto &str : vec) {
        // if (!serialize_string(str, buffer)) {
        //     return false;
        // }
        serialize_string(str, buffer);
    }
    // return true;
}

template <size_t N>
inline void serialize_string_arr(const std::array<std::string, N> &arr, std::vector<uint8_t> &buffer) {
    for (const auto &str : arr) {
        // if (!serialize_string(str, buffer)) {
        //     return false;
        // }
        serialize_string(str, buffer);
    }
    // return true;
}

template <typename T>
inline bool deserialize_base(T &val, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    if (!has_capacity_at_offset(buffer, offset, sizeof(T))) {
        return false;
    }
    val = *reinterpret_cast<const T *>(buffer.data() + offset);
    offset += sizeof(T);
    return true;
}

template <typename T>
inline bool deserialize_base_vec(std::vector<T> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t size;
    if (!deserialize_base(size, buffer, offset)) {
        return false;
    }
    if (!has_capacity_at_offset(buffer, offset, size * sizeof(T))) {
        return false;
    }
    vec.resize(size);
    size_t len = size * sizeof(T);  // length of data in bytes
    size_t stop = offset + len;     // end of data
    uint8_t *data = reinterpret_cast<uint8_t *>(vec.data());
    std::copy(buffer.begin() + offset, buffer.begin() + stop, data);
    offset += len;
    return true;
}

template <typename T, size_t N>
inline bool deserialize_base_arr(std::array<T, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    if (!has_capacity_at_offset(buffer, offset, N * sizeof(T))) {
        return false;
    }
    size_t len = N * sizeof(T);  // length of data in bytes
    size_t stop = offset + len;  // end of data
    uint8_t *data = reinterpret_cast<uint8_t *>(arr.data());
    std::copy(buffer.begin() + offset, buffer.begin() + stop, data);
    offset += len;
    return true;
}

inline bool deserialize_custom(MessageBase &msg, const std::vector<uint8_t> &buffer, size_t &offset) {
    if (!has_capacity_at_offset(buffer, offset, msg.size())) {
        return false;
    }
    return msg.deserialize(buffer, offset);
}

template <typename TMsg>
inline bool deserialize_custom_vec(std::vector<TMsg> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    uint32_t size;
    if (!deserialize_base(size, buffer, offset)) {
        return false;
    }
    vec.resize(size);
    for (auto &msg : vec) {
        // Use the deserialize member function to avoid calculating size
        if (!msg.deserialize(buffer, offset)) {
            return false;
        }
    }
    return true;
}

template <typename TMsg, size_t N>
inline bool deserialize_custom_arr(std::array<TMsg, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    for (auto &msg : arr) {
        // Use the deserialize member function to avoid calculating size
        if (!msg.deserialize(buffer, offset)) {
            return false;
        }
    }
    return true;
}

inline bool deserialize_string(std::string &str, const std::vector<uint8_t> &buffer, size_t &offset) {
    uint32_t size;
    if (!deserialize_base(size, buffer, offset)) {
        return false;
    }
    if (!has_capacity_at_offset(buffer, offset, size)) {
        return false;
    }
    const uint8_t *data = reinterpret_cast<const uint8_t *>(buffer.data() + offset);
    str = std::string(data, data + size);
    offset += size;
    return true;
}

inline bool deserialize_string_vec(std::vector<std::string> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    uint32_t size;
    if (!deserialize_base(size, buffer, offset)) {
        return false;
    }
    vec.resize(size);
    for (auto &elt : vec) {
        if (!deserialize_string(elt, buffer, offset)) {
            return false;
        }
    }
    return true;
}

template <size_t N>
inline bool deserialize_string_arr(std::array<std::string, N> &arr, const std::vector<uint8_t> &buffer,
                                   size_t &offset) {
    for (auto &elt : arr) {
        if (!deserialize_string(elt, buffer, offset)) {
            return false;
        }
    }
    return true;
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
        size += msg.size();
    }
    return size;
}

template <typename TMsg, size_t N>
inline size_t size_custom_arr(const std::array<TMsg, N> &vec) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    size_t size = 0;
    for (const auto &msg : vec) {
        size += msg.size();
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