#pragma once

#include <cstdint>
#include <string>
#include <vector>

#include "rix/msg/message_base.hpp"

namespace rix {
namespace msg {

/**
 *  Accessor method that acts as backdoor to private methods declared in
 *  MessageBase. 
 * */ 
template<typename TMsg>
class Serializer {
static_assert(std::is_base_of<MessageBase, TMsg>::value, "TMsg must derive from MessageBase");
  public:
    static size_t size(const TMsg &msg);
    static Hash hash(const TMsg &msg);
    static void serialize(const TMsg &msg, std::vector<uint8_t> &buffer);
    static void deserialize(TMsg &msg, std::vector<uint8_t> buffer, size_t &offset);
};

template<typename TMsg>
size_t Serializer<TMsg>::size(const TMsg &msg) {
    // Upcast because Serializer is only friends to MessageBase
    const MessageBase *ptr = const_cast<const TMsg*>(&msg);
    return ptr->size();
}

template<typename TMsg>
Hash Serializer<TMsg>::hash(const TMsg &msg) {
    // Upcast because Serializer is only friends to MessageBase
    const MessageBase *ptr = const_cast<const TMsg*>(&msg);
    return ptr->hash();
}

template<typename TMsg>
void Serializer<TMsg>::serialize(const TMsg &msg, std::vector<uint8_t> &buffer) {
    // Upcast because Serializer is only friends to MessageBase
    const MessageBase *ptr = const_cast<const TMsg*>(&msg);
    ptr->serialize(buffer);
}

template<typename TMsg>
void Serializer<TMsg>::deserialize(TMsg &msg, std::vector<uint8_t> buffer, size_t &offset) {
    // Upcast because Serializer is only friends to MessageBase
    MessageBase *ptr = const_cast<TMsg*>(&msg);
    ptr->deserialize(buffer, offset);
}

} // namespace rix
} // namespace msg