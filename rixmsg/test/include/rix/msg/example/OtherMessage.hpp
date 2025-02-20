#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <cstring>

#include "rix/msg/message_base.hpp"
#include "rix/msg/serializer.hpp"

namespace rix {
namespace msg {
namespace example {

class OtherMessage : public MessageBase {
  public:
    int16_t number;
    bool flag;

    OtherMessage() = default;
    OtherMessage(const OtherMessage &other) = default;
    ~OtherMessage() = default;

  private:
    size_t size() const override {
        size_t size = 0;
        size += size_base(number);
        size += size_base(flag);
        return size;
    }

    rix::msg::Hash hash() const override {
        return {0x3ca3b57c64691de0ULL, 0x33fa64726faff850ULL};
    }

    void serialize(std::vector<uint8_t> &buffer) const override {
        buffer.reserve(buffer.size() + this->size());
        serialize_base(number, buffer);
        serialize_base(flag, buffer);
    }

    void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) override {
        deserialize_base(number, buffer, offset);
        deserialize_base(flag, buffer, offset);
    }
};

} // namespace example
} // namespace msg
} // namespace rix