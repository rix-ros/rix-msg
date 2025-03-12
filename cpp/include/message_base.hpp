#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace rix {
namespace msg {

typedef std::array<uint64_t, 2> Hash;

template<typename TMsg>
class Serializer; // forward declaration

class MessageBase {
    template<typename TMsg>
    friend class Serializer;

  protected:
    /**
     * We declare the following methods as protected because they are only meant
     * to be used by the derived classes. They are static because they do not 
     * modify the state of the class.
     * 
     * These could be declared in the rix::msg namespace, but we do not want 
     * them to pollute the namespace since the user is not meant to use them.
     * 
     * There are 9 cases to consider:
     * 1. Base type (int, float, double, etc.)
     * 2. Base type vector (std::vector<int>, std::vector<float>, etc.)
     * 3. Base type array (std::array<int, N>, std::array<float, N>, etc.)
     * 4. Custom type (derived from MessageBase)
     * 5. Custom type vector (std::vector<CustomType>)
     * 6. Custom type array (std::array<CustomType, N>)
     * 7. std::string
     * 8. std::vector<std::string>
     * 9. std::array<std::string, N>
     * 
     * There are serialize, deserialize, and size methods for each of these 
     * cases.
     */
    
    template<typename T>
    static inline void serialize_base(const T &val, std::vector<uint8_t> &buffer);
    template<typename T>
    static inline void serialize_base_vec(const std::vector<T> &vec, std::vector<uint8_t> &buffer);
    template<typename T, size_t N>
    static inline void serialize_base_arr(const std::array<T, N> &arr, std::vector<uint8_t> &buffer);

    static inline void serialize_custom(const MessageBase &msg, std::vector<uint8_t> &buffer);
    template<typename TMsg>
    static inline void serialize_custom_vec(const std::vector<TMsg> &vec, std::vector<uint8_t> &buffer);
    template<typename TMsg, size_t N>
    static inline void serialize_custom_arr(const std::array<TMsg, N> &arr, std::vector<uint8_t> &buffer);

    static inline void serialize_string(const std::string &str, std::vector<uint8_t> &buffer);
    static inline void serialize_string_vec(const std::vector<std::string> &vec, std::vector<uint8_t> &buffer);
    template<size_t N>
    static inline void serialize_string_arr(const std::array<std::string, N> &arr, std::vector<uint8_t> &buffer);

    template<typename T>
    static inline void deserialize_base(T &val, const std::vector<uint8_t> &buffer, size_t &offset);
    template<typename T>
    static inline void deserialize_base_vec(std::vector<T> &vec, const std::vector<uint8_t> &buffer, size_t &offset);
    template<typename T, size_t N>
    static inline void deserialize_base_arr(std::array<T, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset);

    static inline void deserialize_custom(MessageBase &msg, const std::vector<uint8_t> &buffer, size_t &offset);
    template<typename TMsg>
    static inline void deserialize_custom_vec(std::vector<TMsg> &vec, const std::vector<uint8_t> &buffer, size_t &offset);
    template<typename TMsg, size_t N>
    static inline void deserialize_custom_arr(std::array<TMsg, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset);

    static inline void deserialize_string(std::string &str, const std::vector<uint8_t> &buffer, size_t &offset);
    static inline void deserialize_string_vec(std::vector<std::string> &vec, const std::vector<uint8_t> &buffer, size_t &offset);
    template<size_t N>
    static inline void deserialize_string_arr(std::array<std::string, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset);

    template<typename T>
    static inline size_t size_base(const T &val);
    template<typename T>
    static inline size_t size_base_vec(const std::vector<T> &vec);
    template<typename T, size_t N>
    static inline size_t size_base_arr(const std::array<T, N> &arr);

    static inline size_t size_custom(const MessageBase &msg);
    template<typename TMsg>
    static inline size_t size_custom_vec(const std::vector<TMsg> &vec);
    template<typename TMsg, size_t N>
    static inline size_t size_custom_arr(const std::array<TMsg, N> &vec);

    static inline size_t size_string(const std::string &str);
    static inline size_t size_string_vec(const std::vector<std::string> &vec);
    template<size_t N>
    static inline size_t size_string_arr(const std::array<std::string, N> &arr);

    /**
     * These methods are meant to be overridden by derived classes. They are 
     * declared private because they are not meant to be used by the user. 
     * It is necessary, however, for sibling classes to access these functions.
     * When we have one message type as a field in another, the outer message 
     * must be able to serialize the inner message without knowledge of the 
     * inner message's fields. This problemm is a result of message auto-
     * generation. The generator is unaware of the fields of inner messages.
     * If we declared these protected, they would still be inaccessible to 
     * siblings, so we default to the lowest access (private).
     * 
     * How do we allow siblings to access these methods?
     * 1. Friend classes
     *     - Breaks encapsulation
     *     - Every time a message is used within another, the implementation 
     *       file for the inner message would need to be modified with the new
     *       outer class as a friend
     *     - Generally bad practice
     * 2. Public methods
     *     - We don't want the user to be able to use these functions directly.
     *       A user should use this class like a c-struct. It is a simple object
     *       that contains data. However, other methods (in rixcore) need to
     *       access these methods too, so maybe this isn't a bad idea? Just add
     *       a warning doxygen comment that they aren't necessary to use?
     *     - Better than friend class, less confusing interface, less work for 
     *       developer
     *     - Might be the easiest path, but breaks the interface
     * 3. Access sibling as the parent class
     *     - Need to upcast all sibling types before invoking the private 
     *       functions
     *     - Easy for single types, but annoying for containers. Need to cast
     *       individual elements, no implicit conversion
     *     - To make a standard interface, we can creator an accessor class that
     *       is a friend class with MessageBase. We can use this accessor in the
     *       protected methods, rixcore can use this class, and, optionally, the
     *       user can use this class when absolutely necessary.
     * 
     * I have landed on creating an accessor class (Serializer). However, I am
     * not using it in the protected methods. I will manually upcast there. This
     * is so that I can keep the classes in separate header files so that only
     * a user who manually includes rix/msg/serializer.hpp will be able to 
     * serialize the message types.
     * 
     */

  private:
    virtual size_t size() const = 0;
    virtual Hash hash() const = 0;
    virtual void serialize(std::vector<uint8_t> &buffer) const = 0;
    virtual void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) = 0;
};

template<typename T>
void MessageBase::serialize_base(const T &val, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    const uint8_t *data = reinterpret_cast<const uint8_t*>(&val);
    buffer.insert(buffer.end(), data, data + sizeof(T));
}

template<typename T>
void MessageBase::serialize_base_vec(const std::vector<T> &vec, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    uint32_t size = vec.size();
    serialize_base(size, buffer);
    const uint8_t *data = reinterpret_cast<const uint8_t*>(vec.data());
    buffer.insert(buffer.end(), data, data + size * sizeof(T));
}

template<typename T, size_t N>
void MessageBase::serialize_base_arr(const std::array<T, N> &arr, std::vector<uint8_t> &buffer) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    const uint8_t *data = reinterpret_cast<const uint8_t*>(arr.data());
    buffer.insert(buffer.end(), data, data + N * sizeof(T));
}

void MessageBase::serialize_custom(const MessageBase &msg, std::vector<uint8_t> &buffer) {
    msg.serialize(buffer);
}

template<typename TMsg>
void MessageBase::serialize_custom_vec(const std::vector<TMsg> &vec, std::vector<uint8_t> &buffer) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    uint32_t size = vec.size();
    serialize_base(size, buffer);
    for (const auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->serialize(buffer);
    }
}

template<typename TMsg, size_t N>
void MessageBase::serialize_custom_arr(const std::array<TMsg, N> &arr, std::vector<uint8_t> &buffer) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    for (const auto &msg : arr) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->serialize(buffer);
    }
}

void MessageBase::serialize_string(const std::string &str, std::vector<uint8_t> &buffer) {
    uint32_t size = str.size();
    serialize_base(size, buffer);
    const uint8_t *data = reinterpret_cast<const uint8_t*>(str.data());
    buffer.insert(buffer.end(), data, data + size);
}

void MessageBase::serialize_string_vec(const std::vector<std::string> &vec, std::vector<uint8_t> &buffer) {
    uint32_t size = vec.size();
    serialize_base(size, buffer);
    for (const auto &str : vec) {
        serialize_string(str, buffer);
    }
}

template<size_t N>
void MessageBase::serialize_string_arr(const std::array<std::string, N> &arr, std::vector<uint8_t> &buffer) {
    for (const auto &str : arr) {
        serialize_string(str, buffer);
    }
}

template<typename T>
void MessageBase::deserialize_base(T &val, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    val = *reinterpret_cast<const T*>(buffer.data() + offset);
    offset += sizeof(T);
}

template<typename T>
void MessageBase::deserialize_base_vec(std::vector<T> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");

    uint32_t size;
    deserialize_base(size, buffer, offset);
    vec.resize(size);

    size_t len = size * sizeof(T); // length of data in bytes
    size_t stop = offset + len; // end of data
    uint8_t *data = reinterpret_cast<uint8_t*>(vec.data());
    std::copy(buffer.begin() + offset, buffer.begin() + stop, data);
    offset += len;
}

template<typename T, size_t N>
void MessageBase::deserialize_base_arr(std::array<T, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    size_t len = N * sizeof(T); // length of data in bytes
    size_t stop = offset + len; // end of data
    uint8_t *data = reinterpret_cast<uint8_t*>(arr.data());
    std::copy(buffer.begin() + offset, buffer.begin() + stop, data);
    offset += len;
}

void MessageBase::deserialize_custom(MessageBase &msg, const std::vector<uint8_t> &buffer, size_t &offset) {
    msg.deserialize(buffer, offset);
}

template<typename TMsg>
void MessageBase::deserialize_custom_vec(std::vector<TMsg> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
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

template<typename TMsg, size_t N>
void MessageBase::deserialize_custom_arr(std::array<TMsg, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    for (auto &msg : arr) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        ptr->deserialize(buffer, offset);
    }
}

void MessageBase::deserialize_string(std::string &str, const std::vector<uint8_t> &buffer, size_t &offset) {
    uint32_t size;
    deserialize_base(size, buffer, offset);
    const uint8_t *data = reinterpret_cast<const uint8_t*>(buffer.data() + offset);
    str = std::string(data, data + size);
    offset += size;
}

void MessageBase::deserialize_string_vec(std::vector<std::string> &vec, const std::vector<uint8_t> &buffer, size_t &offset) {
    uint32_t size;
    deserialize_base(size, buffer, offset);
    vec.resize(size);

    for (auto &elt : vec) {
        deserialize_string(elt, buffer, offset);
    }
}

template<size_t N>
void MessageBase::deserialize_string_arr(std::array<std::string, N> &arr, const std::vector<uint8_t> &buffer, size_t &offset) {
    for (auto &elt : arr) {
        deserialize_string(elt, buffer, offset);
    }
}

template<typename T>
size_t MessageBase::size_base(const T &val) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return sizeof(T);
}

template<typename T>
size_t MessageBase::size_base_vec(const std::vector<T> &vec) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return sizeof(uint32_t) + vec.size() * sizeof(T);
}

template<typename T, size_t N>
size_t MessageBase::size_base_arr(const std::array<T, N> &arr) {
    static_assert(std::is_arithmetic<T>::value, "T must be an arithmetic type");
    return N * sizeof(T);
}

size_t MessageBase::size_custom(const MessageBase &msg) {
    return msg.size();
}

template<typename TMsg>
size_t MessageBase::size_custom_vec(const std::vector<TMsg> &vec) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    size_t size = sizeof(uint32_t);
    for (const auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        size += ptr->size();
    }
    return size;
}

template<typename TMsg, size_t N>
size_t MessageBase::size_custom_arr(const std::array<TMsg, N> &vec) {
    static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
    size_t size = 0;
    for (const auto &msg : vec) {
        // Need to upcast because this method is inaccessible from a sibling class
        MessageBase *ptr = const_cast<TMsg *>(&msg);
        size += ptr->size();
    }
    return size;
}

size_t MessageBase::size_string(const std::string &str) {
    return sizeof(uint32_t) + str.size();
}

size_t MessageBase::size_string_vec(const std::vector<std::string> &vec) {
    size_t size = sizeof(uint32_t);
    for (const auto &str : vec) {
        size += size_string(str);
    }
    return size;
}

template<size_t N>
size_t MessageBase::size_string_arr(const std::array<std::string, N> &arr) {
    size_t size = 0;
    for (const auto &str : arr) {
        size += size_string(str);
    }
    return size;
}

} // namespace rix
} // namespace msg