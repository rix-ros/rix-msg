#include <cassert>
#include <iostream>

#include "rix/msg/example/ExampleMessage.hpp"
#include "rix/msg/example/OtherMessage.hpp"
#include "rix/msg/message.hpp"

using namespace rix::msg::detail;

class MessageTest : public rix::msg::Message {
   public:
    void test_serialize_number() {
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
        encoded.resize(43);

        size_t offset = 0;
        serialize_number(encoded.data(), offset, i64);
        assert(offset == 8);
        serialize_number(encoded.data(), offset, u64);
        assert(offset == 16);
        serialize_number(encoded.data(), offset, i32);
        assert(offset == 20);
        serialize_number(encoded.data(), offset, u32);
        assert(offset == 24);
        serialize_number(encoded.data(), offset, i16);
        assert(offset == 26);
        serialize_number(encoded.data(), offset, u16);
        assert(offset == 28);
        serialize_number(encoded.data(), offset, i8);
        assert(offset == 29);
        serialize_number(encoded.data(), offset, u8);
        assert(offset == 30);
        serialize_number(encoded.data(), offset, c);
        assert(offset == 31);
        serialize_number(encoded.data(), offset, f32);
        assert(offset == 35);
        serialize_number(encoded.data(), offset, f64);
        assert(offset == 43);

        offset = 0;
        int64_t i64_copy;
        deserialize_number(i64_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 8);
        assert(i64_copy == i64);
        uint64_t u64_copy;
        deserialize_number(u64_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 16);
        assert(u64_copy == u64);
        int32_t i32_copy;
        deserialize_number(i32_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 20);
        assert(i32_copy == i32);
        uint32_t u32_copy;
        deserialize_number(u32_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 24);
        assert(u32_copy == u32);
        int16_t i16_copy;
        deserialize_number(i16_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 26);
        assert(i16_copy == i16);
        uint16_t u16_copy;
        deserialize_number(u16_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 28);
        assert(u16_copy == u16);
        int8_t i8_copy;
        deserialize_number(i8_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 29);
        assert(i8_copy == i8);
        uint8_t u8_copy;
        deserialize_number(u8_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 30);
        assert(u8_copy == u8);
        char c_copy;
        deserialize_number(c_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 31);
        assert(c_copy == c);
        float f32_copy;
        deserialize_number(f32_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 35);
        assert(f32_copy == f32);
        double f64_copy;
        deserialize_number(f64_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 43);
        assert(f64_copy == f64);
    }

    void test_serialize_number_vector() {
        std::vector<uint32_t> vec, vec_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(48);
        vec.resize(3);
        size_t offset = 0;

        vec[0] = 32;
        vec[1] = 64;
        vec[2] = 128;
        serialize_number_vector(encoded.data(), offset, vec);
        assert(offset == 16);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == 3);

        vec[0] = 256;
        vec[1] = 512;
        vec[2] = 1024;
        serialize_number_vector(encoded.data(), offset, vec);
        assert(offset == 32);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 16) == 3);

        vec[0] = 2048;
        vec[1] = 4096;
        vec[2] = 8192;
        serialize_number_vector(encoded.data(), offset, vec);
        assert(offset == 48);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 32) == 3);

        offset = 0;
        deserialize_number_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 16);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == 32);
        assert(vec_copy[1] == 64);
        assert(vec_copy[2] == 128);

        deserialize_number_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 32);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == 256);
        assert(vec_copy[1] == 512);
        assert(vec_copy[2] == 1024);

        deserialize_number_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 48);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == 2048);
        assert(vec_copy[1] == 4096);
        assert(vec_copy[2] == 8192);
    }

    void test_serialize_number_array() {
        std::array<uint32_t, 3> arr, arr_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(36);
        size_t offset = 0;

        arr[0] = 32;
        arr[1] = 64;
        arr[2] = 128;
        serialize_number_array(encoded.data(), offset, arr);
        assert(offset == 12);

        arr[0] = 256;
        arr[1] = 512;
        arr[2] = 1024;
        serialize_number_array(encoded.data(), offset, arr);
        assert(offset == 24);

        arr[0] = 2048;
        arr[1] = 4096;
        arr[2] = 8192;
        serialize_number_array(encoded.data(), offset, arr);
        assert(offset == 36);

        offset = 0;
        deserialize_number_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 12);
        assert(arr_copy[0] == 32);
        assert(arr_copy[1] == 64);
        assert(arr_copy[2] == 128);

        deserialize_number_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 24);
        assert(arr_copy[0] == 256);
        assert(arr_copy[1] == 512);
        assert(arr_copy[2] == 1024);

        deserialize_number_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 36);
        assert(arr_copy[0] == 2048);
        assert(arr_copy[1] == 4096);
        assert(arr_copy[2] == 8192);
    }

    void test_serialize_message() {
        using rix::msg::example::OtherMessage;
        OtherMessage msg, msg_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(27);
        size_t offset = 0;

        msg.flag = true;
        msg.num = 123;
        serialize_message(encoded.data(), offset, msg);
        assert(offset == 9);

        msg.flag = false;
        msg.num = 321;
        serialize_message(encoded.data(), offset, msg);
        assert(offset == 18);

        msg.flag = true;
        msg.num = 231;
        serialize_message(encoded.data(), offset, msg);
        assert(offset == 27);

        offset = 0;
        deserialize_message(msg_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 9);
        assert(msg_copy.flag == true);
        assert(msg_copy.num == 123);

        deserialize_message(msg_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 18);
        assert(msg_copy.flag == false);
        assert(msg_copy.num == 321);

        deserialize_message(msg_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 27);
        assert(msg_copy.flag == true);
        assert(msg_copy.num == 231);
    }

    void test_serialize_message_vector() {
        using rix::msg::example::OtherMessage;
        std::vector<OtherMessage> vec, vec_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(3 * (4 + 27));
        vec.resize(3);
        size_t offset = 0;

        vec[0].flag = true;
        vec[0].num = 123;
        vec[1].flag = false;
        vec[1].num = 456;
        vec[2].flag = true;
        vec[2].num = 789;
        serialize_message_vector(encoded.data(), offset, vec);
        assert(offset == 4 + 27);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == 3);

        vec[0].flag = false;
        vec[0].num = 321;
        vec[1].flag = true;
        vec[1].num = 654;
        vec[2].flag = false;
        vec[2].num = 987;
        serialize_message_vector(encoded.data(), offset, vec);
        assert(offset == 2 * (4 + 27));
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + (4 + 27)) == 3);

        vec[0].flag = true;
        vec[0].num = 231;
        vec[1].flag = false;
        vec[1].num = 564;
        vec[2].flag = true;
        vec[2].num = 897;
        serialize_message_vector(encoded.data(), offset, vec);
        assert(offset == 3 * (4 + 27));
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 2 * (4 + 27)) == 3);

        offset = 0;
        deserialize_message_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 4 + 27);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0].flag == true);
        assert(vec_copy[0].num == 123);
        assert(vec_copy[1].flag == false);
        assert(vec_copy[1].num == 456);
        assert(vec_copy[2].flag == true);
        assert(vec_copy[2].num == 789);

        deserialize_message_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 2 * (4 + 27));
        assert(vec_copy.size() == 3);
        assert(vec_copy[0].flag == false);
        assert(vec_copy[0].num == 321);
        assert(vec_copy[1].flag == true);
        assert(vec_copy[1].num == 654);
        assert(vec_copy[2].flag == false);
        assert(vec_copy[2].num == 987);

        deserialize_message_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 3 * (4 + 27));
        assert(vec_copy.size() == 3);
        assert(vec_copy[0].flag == true);
        assert(vec_copy[0].num == 231);
        assert(vec_copy[1].flag == false);
        assert(vec_copy[1].num == 564);
        assert(vec_copy[2].flag == true);
        assert(vec_copy[2].num == 897);
    }

    void test_serialize_message_array() {
        using rix::msg::example::OtherMessage;
        std::array<OtherMessage, 3> arr, arr_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(27 * 3);
        size_t offset = 0;

        arr[0].flag = true;
        arr[0].num = 123;
        arr[1].flag = false;
        arr[1].num = 456;
        arr[2].flag = true;
        arr[2].num = 789;
        serialize_message_array(encoded.data(), offset, arr);
        assert(offset == 27);

        arr[0].flag = false;
        arr[0].num = 321;
        arr[1].flag = true;
        arr[1].num = 654;
        arr[2].flag = false;
        arr[2].num = 987;
        serialize_message_array(encoded.data(), offset, arr);
        assert(offset == 27 * 2);

        arr[0].flag = true;
        arr[0].num = 231;
        arr[1].flag = false;
        arr[1].num = 564;
        arr[2].flag = true;
        arr[2].num = 897;
        serialize_message_array(encoded.data(), offset, arr);
        assert(offset == 27 * 3);

        offset = 0;
        deserialize_message_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 27);
        assert(arr_copy[0].flag == true);
        assert(arr_copy[0].num == 123);
        assert(arr_copy[1].flag == false);
        assert(arr_copy[1].num == 456);
        assert(arr_copy[2].flag == true);
        assert(arr_copy[2].num == 789);

        deserialize_message_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 2 * 27);
        assert(arr_copy[0].flag == false);
        assert(arr_copy[0].num == 321);
        assert(arr_copy[1].flag == true);
        assert(arr_copy[1].num == 654);
        assert(arr_copy[2].flag == false);
        assert(arr_copy[2].num == 987);

        deserialize_message_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 3 * 27);
        assert(arr_copy[0].flag == true);
        assert(arr_copy[0].num == 231);
        assert(arr_copy[1].flag == false);
        assert(arr_copy[1].num == 564);
        assert(arr_copy[2].flag == true);
        assert(arr_copy[2].num == 897);
    }

    void test_serialize_string() {
        std::string str, str_copy;
        std::vector<uint8_t> encoded;
        size_t offset = 0;
        encoded.resize(59);

        str = "Hello, world!";
        serialize_string(encoded.data(), offset, str);
        size_t expected_size = str.size() + 4;  // 13 + 4
        assert(offset == expected_size);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == str.size());

        str = "How are you?";
        serialize_string(encoded.data(), offset, str);
        expected_size += str.size() + 4;  // 17 + 12 + 4 == 33
        assert(offset == expected_size);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 17) == str.size());

        str = "Meh, I've been better.";
        serialize_string(encoded.data(), offset, str);
        expected_size += str.size() + 4;  // 33 + 22 + 4 == 59
        assert(offset == expected_size);
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 33) == str.size());

        offset = 0;
        deserialize_string(str_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 17);
        assert(str_copy.size() == 13);
        assert(str_copy == "Hello, world!");

        deserialize_string(str_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 33);
        assert(str_copy.size() == 12);
        assert(str_copy == "How are you?");

        deserialize_string(str_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 59);
        assert(str_copy.size() == 22);
        assert(str_copy == "Meh, I've been better.");
    }

    void test_serialize_string_vector() {
        std::vector<std::string> vec, vec_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(176);
        vec.resize(3);
        size_t offset = 0;

        vec[0] = "Hello!";
        vec[1] = "I hope you are well.";
        vec[2] = "RIX is awesome!";
        serialize_string_vector(encoded.data(), offset, vec);
        assert(offset == (4 + (4 + 6) + (4 + 20) + (4 + 15)));  // 57
        assert(*reinterpret_cast<const uint32_t *>(encoded.data()) == 3);

        vec[0] = "rixcore is a neat library";
        vec[1] = "I think rixutil is better";
        vec[2] = "rixipc is best!";
        serialize_string_vector(encoded.data(), offset, vec);
        assert(offset == 57 + (4 + (4 + 25) + (4 + 25) + (4 + 15)));  // 138
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 57) == 3);

        vec[0] = "robotics";
        vec[1] = "mbot";
        vec[2] = "middleware";
        serialize_string_vector(encoded.data(), offset, vec);
        assert(offset == 138 + (4 + (4 + 8) + (4 + 4) + (4 + 10)));  // 176
        assert(*reinterpret_cast<const uint32_t *>(encoded.data() + 138) == 3);

        offset = 0;
        deserialize_string_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 57);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == "Hello!");
        assert(vec_copy[1] == "I hope you are well.");
        assert(vec_copy[2] == "RIX is awesome!");

        deserialize_string_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 138);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == "rixcore is a neat library");
        assert(vec_copy[1] == "I think rixutil is better");
        assert(vec_copy[2] == "rixipc is best!");

        deserialize_string_vector(vec_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 176);
        assert(vec_copy.size() == 3);
        assert(vec_copy[0] == "robotics");
        assert(vec_copy[1] == "mbot");
        assert(vec_copy[2] == "middleware");
    }

    void test_serialize_string_array() {
        std::array<std::string, 3> arr, arr_copy;
        std::vector<uint8_t> encoded;
        encoded.resize(130 + ((4 + 8) + (4 + 4) + (4 + 10)));
        size_t offset = 0;

        arr[0] = "Hello!";
        arr[1] = "I hope you are well.";
        arr[2] = "RIX is awesome!";
        serialize_string_array(encoded.data(), offset, arr);
        assert(offset == ((4 + 6) + (4 + 20) + (4 + 15)));

        arr[0] = "rixcore is a neat library";
        arr[1] = "I think rixutil is better";
        arr[2] = "rixipc is best!";
        serialize_string_array(encoded.data(), offset, arr);
        assert(offset == 53 + ((4 + 25) + (4 + 25) + (4 + 15)));

        arr[0] = "robotics";
        arr[1] = "mbot";
        arr[2] = "middleware";
        serialize_string_array(encoded.data(), offset, arr);
        assert(offset == 130 + ((4 + 8) + (4 + 4) + (4 + 10)));

        offset = 0;
        deserialize_string_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 53);
        assert(arr_copy.size() == 3);
        assert(arr_copy[0] == "Hello!");
        assert(arr_copy[1] == "I hope you are well.");
        assert(arr_copy[2] == "RIX is awesome!");

        deserialize_string_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 130);
        assert(arr_copy.size() == 3);
        assert(arr_copy[0] == "rixcore is a neat library");
        assert(arr_copy[1] == "I think rixutil is better");
        assert(arr_copy[2] == "rixipc is best!");

        deserialize_string_array(arr_copy, encoded.data(), encoded.size(), offset);
        assert(offset == 164);
        assert(arr_copy.size() == 3);
        assert(arr_copy[0] == "robotics");
        assert(arr_copy[1] == "mbot");
        assert(arr_copy[2] == "middleware");
    }

    size_t size() const override { return 0; }
    std::array<uint64_t, 2> hash() const override { return {0}; }
    void serialize(uint8_t *dst, size_t &offset) const override { return; }
    bool deserialize(const uint8_t *src, size_t size, size_t &offset) override { return true; }
};

void test_other_message() {
    using rix::msg::example::OtherMessage;

    OtherMessage msg, msg_copy;
    std::vector<uint8_t> encoded;
    msg.flag = true;
    msg.num = 1234;
    assert(msg.size() == 9);
    encoded.resize(msg.size() * 4);
    size_t offset = 0;
    msg.serialize(encoded.data(), offset);
    assert(offset == 9);

    msg.flag = false;
    msg.num = 4321;
    msg.serialize(encoded.data(), offset);
    assert(offset == 2 * 9);

    msg.flag = true;
    msg.num = 1001;
    msg.serialize(encoded.data(), offset);
    assert(offset == 3 * 9);

    msg.flag = false;
    msg.num = 9876;
    msg.serialize(encoded.data(), offset);
    assert(offset == 4 * 9);

    offset = 0;
    msg_copy.deserialize(encoded.data(), encoded.size(), offset);
    assert(offset == 9);
    assert(msg_copy.flag == true);
    assert(msg_copy.num == 1234);

    msg_copy.deserialize(encoded.data(), encoded.size(), offset);
    assert(offset == 2 * 9);
    assert(msg_copy.flag == false);
    assert(msg_copy.num == 4321);

    msg_copy.deserialize(encoded.data(), encoded.size(), offset);
    assert(offset == 3 * 9);
    assert(msg_copy.flag == true);
    assert(msg_copy.num == 1001);

    msg_copy.deserialize(encoded.data(), encoded.size(), offset);
    assert(offset == 4 * 9);
    assert(msg_copy.flag == false);
    assert(msg_copy.num == 9876);
}

void test_example_message() {
    using rix::msg::example::ExampleMessage;

    ExampleMessage msg, msg_copy;
    std::vector<uint8_t> encoded;
    msg.num = 123;
    msg.str = "Hello, world!";
    msg.flag = true;
    msg.msg.flag = false;
    msg.msg.num = 4.56;
    msg.num_vec.push_back(7.89);
    msg.num_vec.push_back(1011.12);
    msg.num_vec.push_back(1314.15);
    msg.num_arr[0] = 1617.18;
    msg.num_arr[1] = 1920.21;
    msg.num_arr[2] = 2223.24;
    msg.str_vec.push_back("This is a test");
    msg.str_vec.push_back("Of the emergency broadcast system");
    msg.str_vec.push_back("This is only a test");
    msg.str_arr[0] = "This is a test";
    msg.str_arr[1] = "Of the emergency broadcast system";
    msg.str_arr[2] = "This is only a test";
    msg.msg_vec.push_back(msg.msg);
    msg.msg_vec.push_back(msg.msg);
    msg.msg_vec.push_back(msg.msg);
    msg.msg_arr[0] = msg.msg;
    msg.msg_arr[1] = msg.msg;
    msg.msg_arr[2] = msg.msg;
    msg.num_to_num_map.insert({0, 1});
    msg.num_to_num_map.insert({2, 3});
    msg.num_to_num_map.insert({4, 5});
    msg.num_to_msg_map.insert({0, msg.msg});
    msg.num_to_msg_map.insert({2, msg.msg});
    msg.num_to_msg_map.insert({4, msg.msg});
    msg.num_to_str_map.insert({0, "str0"});
    msg.num_to_str_map.insert({2, "str1"});
    msg.num_to_str_map.insert({4, "str2"});
    msg.str_to_num_map.insert({"str0", 0});
    msg.str_to_num_map.insert({"str1", 1});
    msg.str_to_num_map.insert({"str2", 2});
    msg.str_to_msg_map.insert({"str0", msg.msg});
    msg.str_to_msg_map.insert({"str1", msg.msg});
    msg.str_to_msg_map.insert({"str2", msg.msg});
    msg.str_to_str_map.insert({"str0", "str0"});
    msg.str_to_str_map.insert({"str1", "str1"});
    msg.str_to_str_map.insert({"str2", "str2"});
    size_t expected = 568;
    size_t actual = msg.size();
    // assert(msg.size() == expected);
    encoded.resize(msg.size());
    size_t offset = 0;
    msg.serialize(encoded.data(), offset);
    assert(offset == msg.size());

    offset = 0;
    msg_copy.deserialize(encoded.data(), encoded.size(), offset);
    assert(offset == expected);
    assert(msg_copy.num == 123);
    assert(msg_copy.str == "Hello, world!");
    assert(msg_copy.flag == true);
    assert(msg_copy.msg.flag == false);
    assert(msg_copy.msg.num == 4.56);
    assert(msg_copy.num_vec.size() == 3);
    assert(msg_copy.num_vec[0] == 7.89f);
    assert(msg_copy.num_vec[1] == 1011.12f);
    assert(msg_copy.num_vec[2] == 1314.15f);
    assert(msg_copy.num_arr[0] == 1617.18f);
    assert(msg_copy.num_arr[1] == 1920.21f);
    assert(msg_copy.num_arr[2] == 2223.24f);
    assert(msg_copy.str_arr.size() == 3);
    assert(msg_copy.str_arr[0] == "This is a test");
    assert(msg_copy.str_arr[1] == "Of the emergency broadcast system");
    assert(msg_copy.str_arr[2] == "This is only a test");
    assert(msg_copy.str_arr[0] == "This is a test");
    assert(msg_copy.str_arr[1] == "Of the emergency broadcast system");
    assert(msg_copy.str_arr[2] == "This is only a test");
    assert(msg_copy.msg_vec.size() == 3);
    assert(msg_copy.msg_vec[0].flag == false);
    assert(msg_copy.msg_vec[0].num == 4.56);
    assert(msg_copy.msg_vec[1].flag == false);
    assert(msg_copy.msg_vec[1].num == 4.56);
    assert(msg_copy.msg_vec[2].flag == false);
    assert(msg_copy.msg_vec[2].num == 4.56);
    assert(msg_copy.msg_arr[0].flag == false);
    assert(msg_copy.msg_arr[0].num == 4.56);
    assert(msg_copy.msg_arr[1].flag == false);
    assert(msg_copy.msg_arr[1].num == 4.56);
    assert(msg_copy.msg_arr[2].flag == false);
    assert(msg_copy.msg_arr[2].num == 4.56);
}

int main() {
    std::cout << "Running tests...\n" << std::endl;

    std::cout << "Testing MessageBase..." << std::endl;
    MessageTest test;
    test.test_serialize_number();
    std::cout << "test_serialize_number passed." << std::endl;
    test.test_serialize_number_vector();
    std::cout << "test_serialize_number_vector passed." << std::endl;
    test.test_serialize_number_array();
    std::cout << "test_serialize_number_array passed." << std::endl;
    test.test_serialize_message();
    std::cout << "test_serialize_message passed." << std::endl;
    test.test_serialize_message_vector();
    std::cout << "test_serialize_message_vector passed." << std::endl;
    test.test_serialize_message_array();
    std::cout << "test_serialize_message_array passed." << std::endl;
    test.test_serialize_string();
    std::cout << "test_serialize_string passed." << std::endl;
    test.test_serialize_string_vector();
    std::cout << "test_serialize_string_vector passed." << std::endl;
    test.test_serialize_string_array();
    std::cout << "test_serialize_string_array passed." << std::endl;
    std::cout << "MessageBase tests passed.\n" << std::endl;

    std::cout << "Testing OtherMessage..." << std::endl;
    test_other_message();
    std::cout << "OtherMessage tests passed.\n" << std::endl;

    std::cout << "Testing ExampleMessage..." << std::endl;
    test_example_message();
    std::cout << "ExampleMessage tests passed.\n" << std::endl;

    std::cout << "All tests passed." << std::endl;
}