#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <cstring>

#include "rix/msg/message_base.hpp"
#include "rix/msg/example/OtherMessage.hpp"

namespace rix {
namespace msg {
namespace example {

class ExampleMessage : public MessageBase {
  public:
    uint32_t number;
    std::string word;
    bool flag;
    example::OtherMessage object;
    std::vector<float> array;
    std::array<float, 3> static_array;
    std::vector<std::string> array_of_words;
    std::array<std::string, 3> static_array_of_words;
    std::vector<example::OtherMessage> array_of_objects;
    std::array<example::OtherMessage, 3> static_array_of_objects;

    ExampleMessage() = default;
    ExampleMessage(const ExampleMessage &other) = default;
    ~ExampleMessage() = default;

    size_t size() const override {
        using namespace detail;
        size_t size = 0;
        size += size_base(number);
        size += size_string(word);
        size += size_base(flag);
        size += size_custom(object);
        size += size_base_vec(array);
        size += size_base_arr(static_array);
        size += size_string_vec(array_of_words);
        size += size_string_arr(static_array_of_words);
        size += size_custom_vec(array_of_objects);
        size += size_custom_arr(static_array_of_objects);
        return size;
    }

    std::array<uint64_t, 2> hash() const override {
        return {0xd3b5843a81f422d9ULL, 0x316fab08fd66c0d5ULL};
    }

    void serialize(std::vector<uint8_t> &buffer) const override {
        using namespace detail;
        buffer.reserve(buffer.size() + this->size());
        serialize_base(number, buffer);
        serialize_string(word, buffer);
        serialize_base(flag, buffer);
        serialize_custom(object, buffer);
        serialize_base_vec(array, buffer);
        serialize_base_arr(static_array, buffer);
        serialize_string_vec(array_of_words, buffer);
        serialize_string_arr(static_array_of_words, buffer);
        serialize_custom_vec(array_of_objects, buffer);
        serialize_custom_arr(static_array_of_objects, buffer);
    }

    void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) override {
        using namespace detail;
        deserialize_base(number, buffer, offset);
        deserialize_string(word, buffer, offset);
        deserialize_base(flag, buffer, offset);
        deserialize_custom(object, buffer, offset);
        deserialize_base_vec(array, buffer, offset);
        deserialize_base_arr(static_array, buffer, offset);
        deserialize_string_vec(array_of_words, buffer, offset);
        deserialize_string_arr(static_array_of_words, buffer, offset);
        deserialize_custom_vec(array_of_objects, buffer, offset);
        deserialize_custom_arr(static_array_of_objects, buffer, offset);
    }
};

} // namespace example
} // namespace msg
} // namespace rix