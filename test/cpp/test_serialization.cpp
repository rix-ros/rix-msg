#include <gtest/gtest.h>
#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

#include "../../cpp/message.hpp"
#include "../../cpp/serialization.hpp"

using namespace rix;
using namespace rix::detail;

// ===== MOCK MESSAGE CLASS FOR TESTING =====

class MockMessage : public Message {
private:
  int value_;
  std::string text_;
  
public:
  MockMessage() : value_(0), text_("") {}
  MockMessage(int val, const std::string& txt) : value_(val), text_(txt) {}
  
  int get_value() const { return value_; }
  std::string get_text() const { return text_; }
  void set_value(int val) { value_ = val; }
  void set_text(const std::string& txt) { text_ = txt; }
  
  std::array<uint64_t, 2> hash() const override {
    return {0, 0};
  }
  
  uint32_t get_prefix_len() const override {
    return 4; // uint32_t for text size
  }
  
  void get_prefix(uint8_t* sizes, size_t& offset) const override {
    *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(text_.size());
    offset += 4;
  }
  
  size_t get_segment_count() const override {
    return 2; // one for value_, one for text_
  }
  
  bool get_segments(MessageSegment* segments, size_t len, size_t& offset) override {
    if (offset + 2 > len) return false;
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(&value_), sizeof(value_));
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(text_.data()), text_.size());
    return true;
  }
  
  bool get_segments(ConstMessageSegment* segments, size_t len, size_t& offset) const override {
    if (offset + 2 > len) return false;
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(&value_), sizeof(value_));
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(text_.data()), text_.size());
    return true;
  }
  
  bool resize(const uint8_t* sizes, size_t len, size_t& offset) override {
    if (offset + 4 > len) return false;
    uint32_t text_size = *reinterpret_cast<const uint32_t*>(sizes + offset);
    offset += 4;
    text_.resize(text_size);
    return true;
  }
};

// ===== GET_SEGMENT_COUNT TESTS =====

class GetSegmentCountTest : public ::testing::Test {
protected:
  MockMessage msg;
  std::vector<MockMessage> msg_vec;
  std::array<MockMessage, 3> msg_arr;
  
  void SetUp() override {
    msg = MockMessage(42, "test");
    msg_vec = {MockMessage(1, "a"), MockMessage(2, "b")};
    msg_arr = {MockMessage(1, "x"), MockMessage(2, "y"), MockMessage(3, "z")};
  }
};

TEST_F(GetSegmentCountTest, MessageType) {
  EXPECT_EQ(get_segment_count(msg), 2);
}

TEST_F(GetSegmentCountTest, VectorOfMessages) {
  EXPECT_EQ(get_segment_count(msg_vec), 4); // 2 messages * 2 segments each
}

TEST_F(GetSegmentCountTest, ArrayOfMessages) {
  EXPECT_EQ(get_segment_count(msg_arr), 6); // 3 messages * 2 segments each
}

TEST_F(GetSegmentCountTest, VectorOfStrings) {
  std::vector<std::string> str_vec = {"hello", "world", "test"};
  EXPECT_EQ(get_segment_count(str_vec), 3);
}

TEST_F(GetSegmentCountTest, ArrayOfStrings) {
  std::array<std::string, 4> str_arr = {"a", "b", "c", "d"};
  EXPECT_EQ(get_segment_count(str_arr), 4);
}

TEST_F(GetSegmentCountTest, PtrT) {
  ptr_t ptr(100);
  EXPECT_EQ(get_segment_count(ptr), 1);
  
  ptr_t empty_ptr;
  EXPECT_EQ(get_segment_count(empty_ptr), 0);
}

TEST_F(GetSegmentCountTest, VectorOfPtrT) {
  std::vector<ptr_t> ptr_vec;
  ptr_vec.push_back(ptr_t(50));
  ptr_vec.push_back(ptr_t(100));
  ptr_vec.push_back(ptr_t(75));
  EXPECT_EQ(get_segment_count(ptr_vec), 3);
}

TEST_F(GetSegmentCountTest, ArrayOfPtrT) {
  std::array<ptr_t, 2> ptr_arr = {ptr_t(30), ptr_t(60)};
  EXPECT_EQ(get_segment_count(ptr_arr), 2);
}

// ===== GET_SEGMENTS NON-CONST TESTS =====

class GetSegmentsNonConstTest : public ::testing::Test {
protected:
  std::vector<MessageSegment> segments;
  size_t offset;
  
  void SetUp() override {
    segments.resize(10);
    offset = 0;
  }
};

TEST_F(GetSegmentsNonConstTest, ArithmeticTypes) {
  int32_t val_int = 42;
  float val_float = 3.14f;
  double val_double = 2.718;
  bool val_bool = true;
  
  get_segments(val_int, segments.data(), offset);
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), sizeof(int32_t));
  EXPECT_EQ(*reinterpret_cast<int32_t*>(segments[0].ptr()), 42);
  
  get_segments(val_float, segments.data(), offset);
  EXPECT_EQ(offset, 2);
  EXPECT_EQ(segments[1].len(), sizeof(float));
  
  get_segments(val_double, segments.data(), offset);
  EXPECT_EQ(offset, 3);
  EXPECT_EQ(segments[2].len(), sizeof(double));
  
  get_segments(val_bool, segments.data(), offset);
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(segments[3].len(), sizeof(bool));
}

TEST_F(GetSegmentsNonConstTest, String) {
  std::string str = "Hello, World!";
  get_segments(str, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), str.size());
  EXPECT_EQ(std::string(reinterpret_cast<char*>(segments[0].ptr()), segments[0].len()), str);
}

TEST_F(GetSegmentsNonConstTest, Message) {
  MockMessage msg(123, "test_msg");
  get_segments(msg, segments.data(), offset);
  
  EXPECT_EQ(offset, 2);
}

TEST_F(GetSegmentsNonConstTest, VectorOfArithmetic) {
  std::vector<int32_t> vec = {1, 2, 3, 4, 5};
  get_segments(vec, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), vec.size() * sizeof(int32_t));
  
  int32_t* data_ptr = reinterpret_cast<int32_t*>(segments[0].ptr());
  for (size_t i = 0; i < vec.size(); ++i) {
    EXPECT_EQ(data_ptr[i], vec[i]);
  }
}

TEST_F(GetSegmentsNonConstTest, ArrayOfArithmetic) {
  std::array<float, 3> arr = {1.1f, 2.2f, 3.3f};
  get_segments(arr, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), arr.size() * sizeof(float));
}

TEST_F(GetSegmentsNonConstTest, VectorOfStrings) {
  std::vector<std::string> vec = {"alpha", "beta", "gamma"};
  get_segments(vec, segments.data(), offset);
  
  EXPECT_EQ(offset, 3);
  EXPECT_EQ(segments[0].len(), 5); // "alpha"
  EXPECT_EQ(segments[1].len(), 4); // "beta"
  EXPECT_EQ(segments[2].len(), 5); // "gamma"
}

TEST_F(GetSegmentsNonConstTest, ArrayOfStrings) {
  std::array<std::string, 2> arr = {"first", "second"};
  get_segments(arr, segments.data(), offset);
  
  EXPECT_EQ(offset, 2);
  EXPECT_EQ(segments[0].len(), 5);
  EXPECT_EQ(segments[1].len(), 6);
}

TEST_F(GetSegmentsNonConstTest, PtrT) {
  ptr_t ptr(50);
  for (size_t i = 0; i < 50; ++i) {
    ptr.get()[i] = static_cast<uint8_t>(i);
  }
  
  get_segments(ptr, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), 50);
  for (size_t i = 0; i < 50; ++i) {
    EXPECT_EQ(segments[0].ptr()[i], static_cast<uint8_t>(i));
  }
}

TEST_F(GetSegmentsNonConstTest, VectorOfPtrT) {
  std::vector<ptr_t> vec;
  vec.push_back(ptr_t(10));
  vec.push_back(ptr_t(20));
  
  get_segments(vec, segments.data(), offset);
  
  EXPECT_EQ(offset, 2);
  EXPECT_EQ(segments[0].len(), 10);
  EXPECT_EQ(segments[1].len(), 20);
}

TEST_F(GetSegmentsNonConstTest, ArrayOfPtrT) {
  std::array<ptr_t, 2> arr = {ptr_t(15), ptr_t(25)};
  get_segments(arr, segments.data(), offset);
  
  EXPECT_EQ(offset, 2);
  EXPECT_EQ(segments[0].len(), 15);
  EXPECT_EQ(segments[1].len(), 25);
}

// ===== GET_SEGMENTS CONST TESTS =====

class GetSegmentsConstTest : public ::testing::Test {
protected:
  std::vector<ConstMessageSegment> segments;
  size_t offset;
  
  void SetUp() override {
    segments.resize(10);
    offset = 0;
  }
};

TEST_F(GetSegmentsConstTest, ArithmeticTypes) {
  const int64_t val = 9876543210L;
  get_segments(val, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), sizeof(int64_t));
  EXPECT_EQ(*reinterpret_cast<const int64_t*>(segments[0].ptr()), 9876543210L);
}

TEST_F(GetSegmentsConstTest, String) {
  const std::string str = "Const String Test";
  get_segments(str, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), str.size());
}

TEST_F(GetSegmentsConstTest, Message) {
  const MockMessage msg(456, "const_test");
  get_segments(msg, segments.data(), offset);
  
  EXPECT_EQ(offset, 2);
}

TEST_F(GetSegmentsConstTest, VectorOfArithmetic) {
  const std::vector<uint16_t> vec = {100, 200, 300};
  get_segments(vec, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), vec.size() * sizeof(uint16_t));
}

TEST_F(GetSegmentsConstTest, ArrayOfArithmetic) {
  const std::array<double, 2> arr = {1.23, 4.56};
  get_segments(arr, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), arr.size() * sizeof(double));
}

TEST_F(GetSegmentsConstTest, VectorOfStrings) {
  const std::vector<std::string> vec = {"one", "two", "three"};
  get_segments(vec, segments.data(), offset);
  
  EXPECT_EQ(offset, 3);
  EXPECT_EQ(segments[0].len(), 3);
  EXPECT_EQ(segments[1].len(), 3);
  EXPECT_EQ(segments[2].len(), 5);
}

TEST_F(GetSegmentsConstTest, ArrayOfStrings) {
  const std::array<std::string, 3> arr = {"a", "bb", "ccc"};
  get_segments(arr, segments.data(), offset);
  
  EXPECT_EQ(offset, 3);
  EXPECT_EQ(segments[0].len(), 1);
  EXPECT_EQ(segments[1].len(), 2);
  EXPECT_EQ(segments[2].len(), 3);
}

TEST_F(GetSegmentsConstTest, PtrT) {
  ptr_t ptr(30);
  const ptr_t& const_ptr = ptr;
  
  get_segments(const_ptr, segments.data(), offset);
  
  EXPECT_EQ(offset, 1);
  EXPECT_EQ(segments[0].len(), 30);
}

// ===== GET_PREFIX_LEN TESTS =====

class GetPrefixLenTest : public ::testing::Test {};

TEST_F(GetPrefixLenTest, String) {
  std::string str = "test";
  EXPECT_EQ(get_prefix_len(str), 4);
}

TEST_F(GetPrefixLenTest, Message) {
  MockMessage msg(10, "hello");
  EXPECT_EQ(get_prefix_len(msg), 4); // MockMessage has prefix_len of 4
}

TEST_F(GetPrefixLenTest, VectorOfArithmetic) {
  std::vector<int32_t> vec = {1, 2, 3};
  EXPECT_EQ(get_prefix_len(vec), 4); // uint32_t for count
}

TEST_F(GetPrefixLenTest, VectorOfMessages) {
  std::vector<MockMessage> vec = {MockMessage(1, "a"), MockMessage(2, "b")};
  EXPECT_EQ(get_prefix_len(vec), 4 + 4 + 4); // count + 2 message prefixes
}

TEST_F(GetPrefixLenTest, ArrayOfMessages) {
  std::array<MockMessage, 3> arr = {MockMessage(1, "x"), MockMessage(2, "y"), MockMessage(3, "z")};
  EXPECT_EQ(get_prefix_len(arr), 4 + 4 + 4); // 3 message prefixes (no count for arrays)
}

TEST_F(GetPrefixLenTest, VectorOfStrings) {
  std::vector<std::string> vec = {"a", "bb", "ccc"};
  EXPECT_EQ(get_prefix_len(vec), 4 + 3 * 4); // count + 3 string sizes
}

TEST_F(GetPrefixLenTest, ArrayOfStrings) {
  std::array<std::string, 2> arr = {"hello", "world"};
  EXPECT_EQ(get_prefix_len(arr), 2 * 4); // 2 string sizes (no count for arrays)
}

TEST_F(GetPrefixLenTest, PtrT) {
  ptr_t ptr(100);
  EXPECT_EQ(get_prefix_len(ptr), 4);
}

TEST_F(GetPrefixLenTest, VectorOfPtrT) {
  std::vector<ptr_t> vec;
  vec.push_back(ptr_t(10));
  vec.push_back(ptr_t(20));
  vec.push_back(ptr_t(30));
  EXPECT_EQ(get_prefix_len(vec), 4 + 3 * 4); // count + 3 ptr sizes
}

TEST_F(GetPrefixLenTest, ArrayOfPtrT) {
  std::array<ptr_t, 4> arr = {ptr_t(5), ptr_t(10), ptr_t(15), ptr_t(20)};
  EXPECT_EQ(get_prefix_len(arr), 4 * 4); // 4 ptr sizes (no count for arrays)
}

// ===== GET_PREFIX TESTS =====

class GetPrefixTest : public ::testing::Test {
protected:
  std::vector<uint8_t> buffer;
  size_t offset;
  
  void SetUp() override {
    buffer.resize(100);
    offset = 0;
  }
};

TEST_F(GetPrefixTest, String) {
  std::string str = "test string";
  get_prefix(str, buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), static_cast<uint32_t>(str.size()));
}

TEST_F(GetPrefixTest, Message) {
  MockMessage msg(42, "message");
  get_prefix(msg, buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 7u); // "message" length
}

TEST_F(GetPrefixTest, VectorOfArithmetic) {
  std::vector<int32_t> vec = {10, 20, 30, 40};
  get_prefix(vec, buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 4u);
}

TEST_F(GetPrefixTest, VectorOfMessages) {
  std::vector<MockMessage> vec = {MockMessage(1, "a"), MockMessage(2, "bb")};
  get_prefix(vec, buffer.data(), offset);
  
  EXPECT_EQ(offset, 12); // 4 (count) + 4 (first msg prefix) + 4 (second msg prefix)
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 2u); // count
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 4), 1u); // "a" length
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 8), 2u); // "bb" length
}

TEST_F(GetPrefixTest, ArrayOfMessages) {
  std::array<MockMessage, 2> arr = {MockMessage(10, "hello"), MockMessage(20, "world")};
  get_prefix(arr, buffer.data(), offset);
  
  EXPECT_EQ(offset, 8); // 4 (first msg prefix) + 4 (second msg prefix)
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 5u); // "hello" length
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 4), 5u); // "world" length
}

TEST_F(GetPrefixTest, VectorOfStrings) {
  std::vector<std::string> vec = {"alpha", "beta", "gamma"};
  get_prefix(vec, buffer.data(), offset);
  
  EXPECT_EQ(offset, 16); // 4 (count) + 3 * 4 (string sizes)
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 3u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 4), 5u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 8), 4u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 12), 5u);
}

TEST_F(GetPrefixTest, ArrayOfStrings) {
  std::array<std::string, 3> arr = {"x", "yy", "zzz"};
  get_prefix(arr, buffer.data(), offset);
  
  EXPECT_EQ(offset, 12); // 3 * 4 (string sizes, no count for arrays)
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 1u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 4), 2u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 8), 3u);
}

TEST_F(GetPrefixTest, PtrT) {
  ptr_t ptr(256);
  get_prefix(ptr, buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 256u);
}

TEST_F(GetPrefixTest, VectorOfPtrT) {
  std::vector<ptr_t> vec;
  vec.push_back(ptr_t(100));
  vec.push_back(ptr_t(200));
  get_prefix(vec, buffer.data(), offset);
  
  EXPECT_EQ(offset, 12); // 4 (count) + 2 * 4 (ptr sizes)
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 2u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 4), 100u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 8), 200u);
}

TEST_F(GetPrefixTest, ArrayOfPtrT) {
  std::array<ptr_t, 2> arr = {ptr_t(50), ptr_t(75)};
  get_prefix(arr, buffer.data(), offset);
  
  EXPECT_EQ(offset, 8); // 2 * 4 (ptr sizes, no count for arrays)
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data()), 50u);
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(buffer.data() + 4), 75u);
}

// ===== RESIZE TESTS =====

class ResizeTest : public ::testing::Test {
protected:
  std::vector<uint8_t> sizes_buffer;
  size_t offset;
  
  void SetUp() override {
    sizes_buffer.resize(100);
    offset = 0;
  }
};

TEST_F(ResizeTest, String) {
  std::string str;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 15;
  
  resize(str, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(str.size(), 15u);
}

TEST_F(ResizeTest, Message) {
  MockMessage msg;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 10;
  
  resize(msg, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(msg.get_text().size(), 10u);
}

TEST_F(ResizeTest, VectorOfArithmetic) {
  std::vector<float> vec;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 5;
  
  resize(vec, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(vec.size(), 5u);
}

TEST_F(ResizeTest, VectorOfMessages) {
  std::vector<MockMessage> vec;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 3; // count
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 4) = 10; // first msg text size
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 8) = 20; // second msg text size
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 12) = 30; // third msg text size
  
  resize(vec, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 16);
  EXPECT_EQ(vec.size(), 3u);
  EXPECT_EQ(vec[0].get_text().size(), 10u);
  EXPECT_EQ(vec[1].get_text().size(), 20u);
  EXPECT_EQ(vec[2].get_text().size(), 30u);
}

TEST_F(ResizeTest, ArrayOfMessages) {
  std::array<MockMessage, 2> arr;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 5; // first msg text size
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 4) = 8; // second msg text size
  
  resize(arr, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 8);
  EXPECT_EQ(arr[0].get_text().size(), 5u);
  EXPECT_EQ(arr[1].get_text().size(), 8u);
}

TEST_F(ResizeTest, VectorOfStrings) {
  std::vector<std::string> vec;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 3; // count
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 4) = 4; // first string size
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 8) = 6; // second string size
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 12) = 8; // third string size
  
  resize(vec, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 16);
  EXPECT_EQ(vec.size(), 3u);
  EXPECT_EQ(vec[0].size(), 4u);
  EXPECT_EQ(vec[1].size(), 6u);
  EXPECT_EQ(vec[2].size(), 8u);
}

TEST_F(ResizeTest, ArrayOfStrings) {
  std::array<std::string, 3> arr;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 2;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 4) = 3;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 8) = 5;
  
  resize(arr, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 12);
  EXPECT_EQ(arr[0].size(), 2u);
  EXPECT_EQ(arr[1].size(), 3u);
  EXPECT_EQ(arr[2].size(), 5u);
}

TEST_F(ResizeTest, PtrT) {
  ptr_t ptr;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 128;
  
  resize(ptr, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 4);
  EXPECT_EQ(ptr.size(), 128u);
}

TEST_F(ResizeTest, VectorOfPtrT) {
  std::vector<ptr_t> vec;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 2; // count
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 4) = 64; // first ptr size
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 8) = 128; // second ptr size
  
  resize(vec, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 12);
  EXPECT_EQ(vec.size(), 2u);
  EXPECT_EQ(vec[0].size(), 64u);
  EXPECT_EQ(vec[1].size(), 128u);
}

TEST_F(ResizeTest, ArrayOfPtrT) {
  std::array<ptr_t, 3> arr;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data()) = 10;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 4) = 20;
  *reinterpret_cast<uint32_t*>(sizes_buffer.data() + 8) = 30;
  
  resize(arr, sizes_buffer.data(), offset);
  
  EXPECT_EQ(offset, 12);
  EXPECT_EQ(arr[0].size(), 10u);
  EXPECT_EQ(arr[1].size(), 20u);
  EXPECT_EQ(arr[2].size(), 30u);
}

// ===== INTEGRATION TESTS =====

class IntegrationTest : public ::testing::Test {};

TEST_F(IntegrationTest, CompleteMessageSerialization) {
  // Create a message with data
  MockMessage original(42, "integration");
  
  // Get prefix
  std::vector<uint8_t> prefix_buffer(original.get_prefix_len());
  size_t prefix_offset = 0;
  get_prefix(original, prefix_buffer.data(), prefix_offset);
  
  // Get segments
  size_t segment_count = get_segment_count(original);
  std::vector<ConstMessageSegment> segments(segment_count);
  size_t segment_offset = 0;
  get_segments(original, segments.data(), segment_offset);
  
  // Create a new message and resize
  MockMessage restored;
  size_t resize_offset = 0;
  resize(restored, prefix_buffer.data(), resize_offset);
  
  // Get segments for restoration
  std::vector<MessageSegment> restore_segments(segment_count);
  size_t restore_offset = 0;
  restored.get_segments(restore_segments.data(), restore_segments.size(), restore_offset);
  
  // Copy data
  for (size_t i = 0; i < segment_count; ++i) {
    std::memcpy(restore_segments[i].ptr(), segments[i].ptr(), segments[i].len());
  }
  
  // Verify
  EXPECT_EQ(restored.get_value(), 42);
  EXPECT_EQ(restored.get_text(), "integration");
}

TEST_F(IntegrationTest, VectorOfMixedTypes) {
  // std::vector<int32_t> int_vec = {100, 200, 300};
  std::vector<std::string> str_vec = {"one", "two", "three"};
  
  // Test prefix lengths
  // uint32_t int_prefix_len = get_prefix_len(int_vec);
  uint32_t str_prefix_len = get_prefix_len(str_vec);
  
  // EXPECT_EQ(int_prefix_len, 4u);
  EXPECT_EQ(str_prefix_len, 16u); // 4 + 3*4
  
  // Test segment counts
  // size_t int_segment_count = get_segment_count(int_vec);
  size_t str_segment_count = get_segment_count(str_vec);
  
  // EXPECT_EQ(int_segment_count, 1u);
  EXPECT_EQ(str_segment_count, 3u);
}

TEST_F(IntegrationTest, EmptyContainers) {
  std::vector<int32_t> empty_int_vec;
  std::vector<std::string> empty_str_vec;
  
  // Prefix length should still be 4 for the count
  EXPECT_EQ(get_prefix_len(empty_int_vec), 4u);
  EXPECT_EQ(get_prefix_len(empty_str_vec), 4u);
  
  // Segment count should be 1 for arithmetic vector (empty data segment)
  // EXPECT_EQ(get_segment_count(empty_int_vec), 1u);
  EXPECT_EQ(get_segment_count(empty_str_vec), 0u);
}

TEST_F(IntegrationTest, LargeDataset) {
  std::vector<double> large_vec(1000);
  for (size_t i = 0; i < 1000; ++i) {
    large_vec[i] = static_cast<double>(i) * 1.5;
  }
  
  std::vector<uint8_t> prefix_buffer(get_prefix_len(large_vec));
  size_t prefix_offset = 0;
  get_prefix(large_vec, prefix_buffer.data(), prefix_offset);
  
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(prefix_buffer.data()), 1000u);
  
  std::vector<ConstMessageSegment> segments(1);
  size_t segment_offset = 0;
  get_segments(large_vec, segments.data(), segment_offset);
  
  EXPECT_EQ(segments[0].len(), 1000u * sizeof(double));
}

TEST_F(IntegrationTest, NestedMessages) {
  // Create vectors of messages
  std::vector<MockMessage> msg_vec;
  msg_vec.push_back(MockMessage(1, "first"));
  msg_vec.push_back(MockMessage(2, "second"));
  msg_vec.push_back(MockMessage(3, "third"));
  
  // Calculate prefix length
  uint32_t prefix_len = get_prefix_len(msg_vec);
  EXPECT_EQ(prefix_len, 16u); // 4 (count) + 3 * 4 (each message prefix)
  
  // Get prefix data
  std::vector<uint8_t> prefix_buffer(prefix_len);
  size_t prefix_offset = 0;
  get_prefix(msg_vec, prefix_buffer.data(), prefix_offset);
  
  // Verify count
  EXPECT_EQ(*reinterpret_cast<uint32_t*>(prefix_buffer.data()), 3u);
  
  // Calculate segment count
  size_t segment_count = get_segment_count(msg_vec);
  EXPECT_EQ(segment_count, 6u); // 3 messages * 2 segments each
}

// ===== MAIN =====

int main(int argc, char** argv) {
  ::testing::InitGoogleTest(&argc, argv);
  return RUN_ALL_TESTS();
}
