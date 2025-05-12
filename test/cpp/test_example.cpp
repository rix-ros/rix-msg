#include <cassert>
#include <iostream>

#include "rix/msg/example/ExampleMessage.hpp"
#include "rix/msg/example/OtherMessage.hpp"
#include "rix/msg/message_base.hpp"

using namespace rix::msg::detail;

class MessageBaseTest : public rix::msg::MessageBase {
   public:
    void test_serialize_base() {
        int64_t i64 = 1234567890;
        uint64_t u64 = 9876543210;
        int32_t i32 = 12345;
        uint32_t u32 = 54321;
        int16_t i16 = 123;
        uint16_t u16 = 321;
        int8_t i8 = 12;
        uint8_t u8 = 21;
        char c = 'a';
        float f32 = 3.14159;
        double f64 = 3.14159265359;
        std::vector<uint8_t> encoded;

        serialize_base(i64, encoded);
        assert(encoded.size() == 8);
        serialize_base(u64, encoded);
        assert(encoded.size() == 16);
        serialize_base(i32, encoded);
        assert(encoded.size() == 20);
        serialize_base(u32, encoded);
        assert(encoded.size() == 24);
        serialize_base(i16, encoded);
        assert(encoded.size() == 26);
        serialize_base(u16, encoded);
        assert(encoded.size() == 28);
        serialize_base(i8, encoded);
        assert(encoded.size() == 29);
        serialize_base(u8, encoded);
        assert(encoded.size() == 30);
        serialize_base(c, encoded);
        assert(encoded.size() == 31);
        serialize_base(f32, encoded);
        assert(encoded.size() == 35);
        serialize_base(f64, encoded);
        assert(encoded.size() == 43);

        size_t offset = 0;
        int64_t i64_copy;
        deserialize_base(i64_copy, encoded, offset);
        assert(offset == 8);
        assert(i64_copy == i64);
        uint64_t u64_copy;
        deserialize_base(u64_copy, encoded, offset);
        assert(offset == 16);
        assert(u64_copy == u64);
        int32_t i32_copy;
        deserialize_base(i32_copy, encoded, offset);
        assert(offset == 20);
        assert(i32_copy == i32);
        uint32_t u32_copy;
        deserialize_base(u32_copy, encoded, offset);
        assert(offset == 24);
        assert(u32_copy == u32);
        int16_t i16_copy;
        deserialize_base(i16_copy, encoded, offset);
        assert(offset == 26);
        assert(i16_copy == i16);
        uint16_t u16_copy;
        deserialize_base(u16_copy, encoded, offset);
        assert(offset == 28);
        assert(u16_copy == u16);
        int8_t i8_copy;
        deserialize_base(i8_copy, encoded, offset);
        assert(offset == 29);
        assert(i8_copy == i8);
        uint8_t u8_copy;
        deserialize_base(u8_copy, encoded, offset);
        assert(offset == 30);
        assert(u8_copy == u8);
        char c_copy;
        deserialize_base(c_copy, encoded, offset);
        assert(offset == 31);
        assert(c_copy == c);
        float f32_copy;
        deserialize_base(f32_copy, encoded, offset);
        assert(offset == 35);
        assert(f32_copy == f32);
        double f64_copy;
        deserialize_base(f64_copy, encoded, offset);
        assert(offset == 43);
        assert(f64_copy == f64);
    }

    void test_serialize_base_vec() {
        std::vector<uint32_t> vec, vec_copy;
        std::vector<uint8_t> encoded;
        vec.resize(3);

        vec[0] = 32;
        vec[1] = 64;
        vec[2] = 128;
        serialize_base_vec(vec, encoded);
        assert(encoded.size() == 16);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == 3);

        vec[0] = 256;
        vec[1] = 512;
        vec[2] = 1024;
        serialize_base_vec(vec, encoded);
        assert(encoded.size() == 32);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 16) == 3);

        vec[0] = 2048;
        vec[1] = 4096;
        vec[2] = 8192;
        serialize_base_vec(vec, encoded);
        assert(encoded.size() == 48);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 32) == 3);

        size_t offset = 0;
        deserialize_base_vec(vec_copy, encoded, offset);
        assert(offset == 16);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == 32);
        assert(vec_copy[1] == 64);
        assert(vec_copy[2] == 128);

        deserialize_base_vec(vec_copy, encoded, offset);
        assert(offset == 32);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == 256);
        assert(vec_copy[1] == 512);
        assert(vec_copy[2] == 1024);

        deserialize_base_vec(vec_copy, encoded, offset);
        assert(offset == 48);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == 2048);
        assert(vec_copy[1] == 4096);
        assert(vec_copy[2] == 8192);
    }

    void test_serialize_base_arr() {
        std::array<uint32_t, 3> arr, arr_copy;
        std::vector<uint8_t> encoded;

        arr[0] = 32;
        arr[1] = 64;
        arr[2] = 128;
        serialize_base_arr(arr, encoded);
        assert(encoded.size() == 12);

        arr[0] = 256;
        arr[1] = 512;
        arr[2] = 1024;
        serialize_base_arr(arr, encoded);
        assert(encoded.size() == 24);

        arr[0] = 2048;
        arr[1] = 4096;
        arr[2] = 8192;
        serialize_base_arr(arr, encoded);
        assert(encoded.size() == 36);

        size_t offset = 0;
        deserialize_base_arr(arr_copy, encoded, offset);
        assert(offset == 12);
        assert(arr_copy[0] == 32);
        assert(arr_copy[1] == 64);
        assert(arr_copy[2] == 128);

        deserialize_base_arr(arr_copy, encoded, offset);
        assert(offset == 24);
        assert(arr_copy[0] == 256);
        assert(arr_copy[1] == 512);
        assert(arr_copy[2] == 1024);

        deserialize_base_arr(arr_copy, encoded, offset);
        assert(offset == 36);
        assert(arr_copy[0] == 2048);
        assert(arr_copy[1] == 4096);
        assert(arr_copy[2] == 8192);
    }

    void test_serialize_custom() {
        using rix::msg::example::OtherMessage;
        OtherMessage msg, msg_copy;
        std::vector<uint8_t> encoded;

        msg.flag = true;
        msg.number = 123;
        serialize_custom(msg, encoded);
        assert(encoded.size() == 9);

        msg.flag = false;
        msg.number = 321;
        serialize_custom(msg, encoded);
        assert(encoded.size() == 18);

        msg.flag = true;
        msg.number = 231;
        serialize_custom(msg, encoded);
        assert(encoded.size() == 27);

        size_t offset = 0;
        deserialize_custom(msg_copy, encoded, offset);
        assert(offset == 9);
        assert(msg_copy.flag == true);
        assert(msg_copy.number == 123);

        deserialize_custom(msg_copy, encoded, offset);
        assert(offset == 18);
        assert(msg_copy.flag == false);
        assert(msg_copy.number == 321);

        deserialize_custom(msg_copy, encoded, offset);
        assert(offset == 27);
        assert(msg_copy.flag == true);
        assert(msg_copy.number == 231);
    }

    void test_serialize_custom_vec() {
        using rix::msg::example::OtherMessage;
        std::vector<OtherMessage> vec, vec_copy;
        std::vector<uint8_t> encoded;
        vec.resize(3);

        vec[0].flag = true;
        vec[0].number = 123;
        vec[1].flag = false;
        vec[1].number = 456;
        vec[2].flag = true;
        vec[2].number = 789;
        serialize_custom_vec(vec, encoded);
        assert(encoded.size() == 4 + 27);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == 3);

        vec[0].flag = false;
        vec[0].number = 321;
        vec[1].flag = true;
        vec[1].number = 654;
        vec[2].flag = false;
        vec[2].number = 987;
        serialize_custom_vec(vec, encoded);
        assert(encoded.size() == 2 * (4 + 27));
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + (4 + 27)) == 3);

        vec[0].flag = true;
        vec[0].number = 231;
        vec[1].flag = false;
        vec[1].number = 564;
        vec[2].flag = true;
        vec[2].number = 897;
        serialize_custom_vec(vec, encoded);
        assert(encoded.size() == 3 * (4 + 27));
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 2 * (4 + 27)) == 3);

        size_t offset = 0;
        deserialize_custom_vec(vec_copy, encoded, offset);
        assert(offset == 4 + 27);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0].flag == true);
        assert(vec_copy[0].number == 123);
        assert(vec_copy[1].flag == false);
        assert(vec_copy[1].number == 456);
        assert(vec_copy[2].flag == true);
        assert(vec_copy[2].number == 789);

        deserialize_custom_vec(vec_copy, encoded, offset);
        assert(offset == 2 * (4 + 27));
        assert(vec_copy.size() == 3);
        assert(vec_copy[0].flag == false);
        assert(vec_copy[0].number == 321);
        assert(vec_copy[1].flag == true);
        assert(vec_copy[1].number == 654);
        assert(vec_copy[2].flag == false);
        assert(vec_copy[2].number == 987);

        deserialize_custom_vec(vec_copy, encoded, offset);
        assert(offset == 3 * (4 + 27));
        assert(vec_copy.size() == 3);
        assert(vec_copy[0].flag == true);
        assert(vec_copy[0].number == 231);
        assert(vec_copy[1].flag == false);
        assert(vec_copy[1].number == 564);
        assert(vec_copy[2].flag == true);
        assert(vec_copy[2].number == 897);
    }

    void test_serialize_custom_arr() {
        using rix::msg::example::OtherMessage;
        std::array<OtherMessage, 3> arr, arr_copy;
        std::vector<uint8_t> encoded;

        arr[0].flag = true;
        arr[0].number = 123;
        arr[1].flag = false;
        arr[1].number = 456;
        arr[2].flag = true;
        arr[2].number = 789;
        serialize_custom_arr(arr, encoded);
        assert(encoded.size() == 27);

        arr[0].flag = false;
        arr[0].number = 321;
        arr[1].flag = true;
        arr[1].number = 654;
        arr[2].flag = false;
        arr[2].number = 987;
        serialize_custom_arr(arr, encoded);
        assert(encoded.size() == 27 * 2);

        arr[0].flag = true;
        arr[0].number = 231;
        arr[1].flag = false;
        arr[1].number = 564;
        arr[2].flag = true;
        arr[2].number = 897;
        serialize_custom_arr(arr, encoded);
        assert(encoded.size() == 27 * 3);

        size_t offset = 0;
        deserialize_custom_arr(arr_copy, encoded, offset);
        assert(offset == 27);
        assert(arr_copy[0].flag == true);
        assert(arr_copy[0].number == 123);
        assert(arr_copy[1].flag == false);
        assert(arr_copy[1].number == 456);
        assert(arr_copy[2].flag == true);
        assert(arr_copy[2].number == 789);

        deserialize_custom_arr(arr_copy, encoded, offset);
        assert(offset == 2 * 27);
        assert(arr_copy[0].flag == false);
        assert(arr_copy[0].number == 321);
        assert(arr_copy[1].flag == true);
        assert(arr_copy[1].number == 654);
        assert(arr_copy[2].flag == false);
        assert(arr_copy[2].number == 987);

        deserialize_custom_arr(arr_copy, encoded, offset);
        assert(offset == 3 * 27);
        assert(arr_copy[0].flag == true);
        assert(arr_copy[0].number == 231);
        assert(arr_copy[1].flag == false);
        assert(arr_copy[1].number == 564);
        assert(arr_copy[2].flag == true);
        assert(arr_copy[2].number == 897);
    }

    void test_serialize_string() {
        std::string str, str_copy;
        std::vector<uint8_t> encoded;

        str = "Hello, world!";
        serialize_string(str, encoded);
        size_t expected_size = str.size() + 4;  // 13 + 4
        assert(encoded.size() == expected_size);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == str.size());

        str = "How are you?";
        serialize_string(str, encoded);
        expected_size += str.size() + 4;  // 17 + 12 + 4 == 33
        assert(encoded.size() == expected_size);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 17) == str.size());

        str = "Meh, I've been better.";
        serialize_string(str, encoded);
        expected_size += str.size() + 4;  // 33 + 22 + 4 == 59
        assert(encoded.size() == expected_size);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 33) == str.size());

        size_t offset = 0;
        deserialize_string(str_copy, encoded, offset);
        assert(offset == 17);
        assert(str_copy.size() == 13);
        assert(str_copy == "Hello, world!");

        deserialize_string(str_copy, encoded, offset);
        assert(offset == 33);
        assert(str_copy.size() == 12);
        assert(str_copy == "How are you?");

        deserialize_string(str_copy, encoded, offset);
        assert(offset == 59);
        assert(str_copy.size() == 22);
        assert(str_copy == "Meh, I've been better.");
    }

    void test_serialize_string_vec() {
        std::vector<std::string> vec, vec_copy;
        std::vector<uint8_t> encoded;
        vec.resize(3);

        vec[0] = "Hello!";
        vec[1] = "I hope you are well.";
        vec[2] = "RIX is awesome!";
        serialize_string_vec(vec, encoded);
        assert(encoded.size() == (4 + (4 + 6) + (4 + 20) + (4 + 15)));  // 57
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == 3);

        vec[0] = "rixcore is a neat library";
        vec[1] = "I think rixutil is better";
        vec[2] = "rixipc is best!";
        serialize_string_vec(vec, encoded);
        assert(encoded.size() == 57 + (4 + (4 + 25) + (4 + 25) + (4 + 15)));  // 138
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 57) == 3);

        vec[0] = "robotics";
        vec[1] = "mbot";
        vec[2] = "middleware";
        serialize_string_vec(vec, encoded);
        assert(encoded.size() == 138 + (4 + (4 + 8) + (4 + 4) + (4 + 10)));  // 176
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 138) == 3);

        size_t offset = 0;
        deserialize_string_vec(vec_copy, encoded, offset);
        assert(offset == 57);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == "Hello!");
        assert(vec_copy[1] == "I hope you are well.");
        assert(vec_copy[2] == "RIX is awesome!");

        deserialize_string_vec(vec_copy, encoded, offset);
        assert(offset == 138);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == "rixcore is a neat library");
        assert(vec_copy[1] == "I think rixutil is better");
        assert(vec_copy[2] == "rixipc is best!");

        deserialize_string_vec(vec_copy, encoded, offset);
        assert(offset == 176);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == "robotics");
        assert(vec_copy[1] == "mbot");
        assert(vec_copy[2] == "middleware");
    }

    void test_serialize_string_arr() {
        std::array<std::string, 3> arr, arr_copy;
        std::vector<uint8_t> encoded;

        arr[0] = "Hello!";
        arr[1] = "I hope you are well.";
        arr[2] = "RIX is awesome!";
        serialize_string_arr(arr, encoded);
        assert(encoded.size() == ((4 + 6) + (4 + 20) + (4 + 15)));

        arr[0] = "rixcore is a neat library";
        arr[1] = "I think rixutil is better";
        arr[2] = "rixipc is best!";
        serialize_string_arr(arr, encoded);
        assert(encoded.size() == 53 + ((4 + 25) + (4 + 25) + (4 + 15)));

        arr[0] = "robotics";
        arr[1] = "mbot";
        arr[2] = "middleware";
        serialize_string_arr(arr, encoded);
        assert(encoded.size() == 130 + ((4 + 8) + (4 + 4) + (4 + 10)));

        size_t offset = 0;
        deserialize_string_arr(arr_copy, encoded, offset);
        assert(offset == 53);
        assert(arr_copy.size() == 3);
        assert(arr_copy[0] == "Hello!");
        assert(arr_copy[1] == "I hope you are well.");
        assert(arr_copy[2] == "RIX is awesome!");

        deserialize_string_arr(arr_copy, encoded, offset);
        assert(offset == 130);
        assert(arr_copy.size() == 3);
        assert(arr_copy[0] == "rixcore is a neat library");
        assert(arr_copy[1] == "I think rixutil is better");
        assert(arr_copy[2] == "rixipc is best!");

        deserialize_string_arr(arr_copy, encoded, offset);
        assert(offset == 164);
        assert(arr_copy.size() == 3);
        assert(arr_copy[0] == "robotics");
        assert(arr_copy[1] == "mbot");
        assert(arr_copy[2] == "middleware");
    }

   private:
    size_t size() const override { return 0; }

    std::array<uint64_t, 2> hash() const override { return {0}; }

    bool serialize(std::vector<uint8_t> &buffer) const override { return true; }

    bool deserialize(const std::vector<uint8_t> &buffer, size_t &offset) override { return true; }
};

void test_other_message() {
    using rix::msg::example::OtherMessage;

    OtherMessage msg, msg_copy;
    std::vector<uint8_t> encoded;
    msg.flag = true;
    msg.number = 1234;
    assert(msg.size() == 9);
    msg.serialize(encoded);
    assert(encoded.size() == 9);

    msg.flag = false;
    msg.number = 4321;
    msg.serialize(encoded);
    assert(encoded.size() == 2 * 9);

    msg.flag = true;
    msg.number = 1001;
    msg.serialize(encoded);
    assert(encoded.size() == 3 * 9);

    msg.flag = false;
    msg.number = 9876;
    msg.serialize(encoded);
    assert(encoded.size() == 4 * 9);

    size_t offset = 0;
    msg_copy.deserialize(encoded, offset);
    assert(offset == 9);
    assert(msg_copy.flag == true);
    assert(msg_copy.number == 1234);

    msg_copy.deserialize(encoded, offset);
    assert(offset == 2 * 9);
    assert(msg_copy.flag == false);
    assert(msg_copy.number == 4321);

    msg_copy.deserialize(encoded, offset);
    assert(offset == 3 * 9);
    assert(msg_copy.flag == true);
    assert(msg_copy.number == 1001);

    msg_copy.deserialize(encoded, offset);
    assert(offset == 4 * 9);
    assert(msg_copy.flag == false);
    assert(msg_copy.number == 9876);
}

void test_example_message() {
    using rix::msg::example::ExampleMessage;

    ExampleMessage msg, msg_copy;
    std::vector<uint8_t> encoded;
    msg.number = 123;
    msg.word = "Hello, world!";
    msg.flag = true;
    msg.object.flag = false;
    msg.object.number = 4.56;
    msg.array.push_back(7.89);
    msg.array.push_back(1011.12);
    msg.array.push_back(1314.15);
    msg.static_array[0] = 1617.18;
    msg.static_array[1] = 1920.21;
    msg.static_array[2] = 2223.24;
    msg.array_of_words.push_back("This is a test");
    msg.array_of_words.push_back("Of the emergency broadcast system");
    msg.array_of_words.push_back("This is only a test");
    msg.static_array_of_words[0] = "This is a test";
    msg.static_array_of_words[1] = "Of the emergency broadcast system";
    msg.static_array_of_words[2] = "This is only a test";
    msg.array_of_objects.push_back(msg.object);
    msg.array_of_objects.push_back(msg.object);
    msg.array_of_objects.push_back(msg.object);
    msg.static_array_of_objects[0] = msg.object;
    msg.static_array_of_objects[1] = msg.object;
    msg.static_array_of_objects[2] = msg.object;
    size_t expected = 4 + (4 + 13) + 1 + (8 + 1) + (4 + 3 * 4) + (3 * 4) + (4 + (4 + 14) + (4 + 33) + (4 + 19)) +
                      ((4 + 14) + (4 + 33) + (4 + 19)) + (4 + 3 * (8 + 1)) + (3 * (8 + 1));
    assert(msg.size() == expected);

    msg.serialize(encoded);
    assert(encoded.size() == msg.size());

    size_t offset = 0;
    msg_copy.deserialize(encoded, offset);
    assert(offset == expected);
    assert(msg_copy.number == 123);
    assert(msg_copy.word == "Hello, world!");
    assert(msg_copy.flag == true);
    assert(msg_copy.object.flag == false);
    assert(msg_copy.object.number == 4.56);
    assert(msg_copy.array.size() == 3);
    assert(msg_copy.array[0] == 7.89f);
    assert(msg_copy.array[1] == 1011.12f);
    assert(msg_copy.array[2] == 1314.15f);
    assert(msg_copy.static_array[0] == 1617.18f);
    assert(msg_copy.static_array[1] == 1920.21f);
    assert(msg_copy.static_array[2] == 2223.24f);
    assert(msg_copy.array_of_words.size() == 3);
    assert(msg_copy.array_of_words[0] == "This is a test");
    assert(msg_copy.array_of_words[1] == "Of the emergency broadcast system");
    assert(msg_copy.array_of_words[2] == "This is only a test");
    assert(msg_copy.static_array_of_words[0] == "This is a test");
    assert(msg_copy.static_array_of_words[1] == "Of the emergency broadcast system");
    assert(msg_copy.static_array_of_words[2] == "This is only a test");
    assert(msg_copy.array_of_objects.size() == 3);
    assert(msg_copy.array_of_objects[0].flag == false);
    assert(msg_copy.array_of_objects[0].number == 4.56);
    assert(msg_copy.array_of_objects[1].flag == false);
    assert(msg_copy.array_of_objects[1].number == 4.56);
    assert(msg_copy.array_of_objects[2].flag == false);
    assert(msg_copy.array_of_objects[2].number == 4.56);
    assert(msg_copy.static_array_of_objects[0].flag == false);
    assert(msg_copy.static_array_of_objects[0].number == 4.56);
    assert(msg_copy.static_array_of_objects[1].flag == false);
    assert(msg_copy.static_array_of_objects[1].number == 4.56);
    assert(msg_copy.static_array_of_objects[2].flag == false);
    assert(msg_copy.static_array_of_objects[2].number == 4.56);
}

int main() {
    std::cout << "Running tests...\n" << std::endl;

    std::cout << "Testing MessageBase..." << std::endl;
    MessageBaseTest test;
    test.test_serialize_base();
    test.test_serialize_base_vec();
    test.test_serialize_base_arr();
    test.test_serialize_custom();
    test.test_serialize_custom_vec();
    test.test_serialize_custom_arr();
    test.test_serialize_string();
    test.test_serialize_string_vec();
    test.test_serialize_string_arr();
    std::cout << "MessageBase tests passed.\n" << std::endl;

    std::cout << "Testing OtherMessage..." << std::endl;
    test_other_message();
    std::cout << "OtherMessage tests passed.\n" << std::endl;

    std::cout << "Testing ExampleMessage..." << std::endl;
    test_example_message();
    std::cout << "ExampleMessage tests passed.\n" << std::endl;

    std::cout << "All tests passed." << std::endl;
}