#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <cstring>

#include "rix/msg/message_base.hpp"

namespace rix {
namespace msg {
namespace example {

class OtherMessage : public MessageBase {
  public:
    double number;
    bool flag;

    OtherMessage() = default;
    OtherMessage(const OtherMessage &other) = default;
    ~OtherMessage() = default;

    size_t size() const override {
        using namespace detail;
        size_t size = 0;
        size += size_base(number);
        size += size_base(flag);
        return size;
    }

    std::array<uint64_t, 2> hash() const override {
        return {0x309c08666f8285b7ULL, 0xe5ca3cc56cb0fbecULL};
    }

    void serialize(std::vector<uint8_t> &buffer) const override {
        using namespace detail;
        buffer.reserve(buffer.size() + this->size());
        serialize_base(number, buffer);
        serialize_base(flag, buffer);
    }

    void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) override {
        using namespace detail;
        deserialize_base(number, buffer, offset);
        deserialize_base(flag, buffer, offset);
    }
};

} // namespace example
} // namespace msg
} // namespace rix