#pragma once

#include <cstdint>
#include <string>
#include <type_traits>
#include <vector>

#include "message.hpp"

namespace rix {
namespace detail {
// Helper for static_assert(false) with dependent types
template <typename T> struct always_false : std::false_type {};

// ===== GET_SEGMENT_COUNT HELPERS =====

// Overload for Message types
inline size_t get_segment_count(const Message& msg) { return msg.get_segment_count(); }

// Overload for vectors of Message types
template <typename T>
typename std::enable_if<std::is_base_of<Message, T>::value, size_t>::type get_segment_count(const std::vector<T>& vec) {
  size_t total_count = 0;
  for (const auto& item : vec) {
    total_count += item.get_segment_count();
  }
  return total_count;
}

// Overload for arrays of Message types
template <typename T, size_t N>
typename std::enable_if<std::is_base_of<Message, T>::value, size_t>::type
get_segment_count(const std::array<T, N>& arr) {
  size_t total_count = 0;
  for (const auto& item : arr) {
    total_count += item.get_segment_count();
  }
  return total_count;
}

// Overload for std::vector<std::string>
inline size_t get_segment_count(const std::vector<std::string>& vec) { return vec.size(); }

// Overload for std::array<std::string, N>
template <size_t N> inline size_t get_segment_count(const std::array<std::string, N>& arr) { return N; }

// Overload for ptr_t
inline size_t get_segment_count(const ptr_t& ptr) { return ptr.get() != nullptr && ptr.size() > 0 ? 1 : 0; }

// ===== NON-CONST GET_SEGMENT HELPERS =====

// Primary template for arithmetic types (integers, floats, bool, etc.)
template <typename T>
typename std::enable_if<std::is_arithmetic<T>::value, void>::type
get_segments(T& obj, MessageSegment* segments, size_t& offset) {
  segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(&obj), sizeof(T));
}

// Overload for std::string
inline void get_segments(std::string& str, MessageSegment* segments, size_t& offset) {
  segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(str.data()), str.size());
}

// Overload for Message types
inline void get_segments(Message& msg, MessageSegment* segments, size_t& offset) {
  size_t len = msg.get_segment_count() + offset; // Forge length (segment length is checked beforehand)
  msg.get_segments(segments, len, offset);
}

// Overload for vectors
template <typename T>
typename std::enable_if<!std::is_same<T, std::string>::value, void>::type
get_segments(std::vector<T>& vec, MessageSegment* segments, size_t& offset) {
  if constexpr (std::is_arithmetic_v<T>) {
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(vec.data()), vec.size() * sizeof(T));
  } else if constexpr (std::is_base_of_v<Message, T>) {
    for (auto& item : vec) {
      size_t len = item.get_segment_count() + offset; // Forge length (segment length is checked beforehand)
      item.get_segments(segments, len, offset);
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported vector element type");
  }
}

// Overload for arrays
template <typename T, size_t N>
typename std::enable_if<!std::is_same<T, std::string>::value, void>::type
get_segments(std::array<T, N>& arr, MessageSegment* segments, size_t& offset) {
  if constexpr (std::is_arithmetic_v<T>) {
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(arr.data()), arr.size() * sizeof(T));
  } else if constexpr (std::is_base_of_v<Message, T>) {
    for (auto& item : arr) {
      size_t len = item.get_segment_count() + offset; // Forge length (segment length is checked beforehand)
      item.get_segments(segments, len, offset);
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported array element type");
  }
}

// Overload for vector of strings
inline void get_segments(std::vector<std::string>& vec, MessageSegment* segments, size_t& offset) {
  for (auto& str : vec) {
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(str.data()), str.size());
  }
}

// Overload for array of strings
template <size_t N>
inline void get_segments(std::array<std::string, N>& arr, MessageSegment* segments, size_t& offset) {
  for (auto& str : arr) {
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(str.data()), str.size());
  }
}

// Overload for ptr_t
inline void get_segments(ptr_t& ptr, MessageSegment* segments, size_t& offset) {
  if (ptr.get() != nullptr && ptr.size() > 0) {
    segments[offset++] = MessageSegment(reinterpret_cast<uint8_t*>(ptr.get()), ptr.size());
  }
}

// ===== CONST GET_SEGMENT HELPERS =====

// Primary template for arithmetic types (integers, floats, bool, etc.)
template <typename T>
typename std::enable_if<std::is_arithmetic<T>::value, void>::type
get_segments(const T& obj, ConstMessageSegment* segments, size_t& offset) {
  segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(&obj), sizeof(T));
}

// Overload for std::string
inline void get_segments(const std::string& str, ConstMessageSegment* segments, size_t& offset) {
  segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(str.data()), str.size());
}

// Overload for const Message types
inline void get_segments(const Message& msg, ConstMessageSegment* segments, size_t& offset) {
  size_t len = msg.get_segment_count() + offset; // Forge length (segment length is checked beforehand)
  msg.get_segments(segments, len, offset);
}

// Overload for const vectors
template <typename T>
typename std::enable_if<!std::is_same<T, std::string>::value, void>::type
get_segments(const std::vector<T>& vec, ConstMessageSegment* segments, size_t& offset) {
  if constexpr (std::is_arithmetic_v<T>) {
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(vec.data()), vec.size() * sizeof(T));
  } else if constexpr (std::is_base_of_v<Message, T>) {
    for (const auto& item : vec) {
      size_t len = item.get_segment_count() + offset; // Forge length (segment length is checked beforehand)
      item.get_segments(segments, len, offset);
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported vector element type");
  }
}

// Overload for const arrays
template <typename T, size_t N>
typename std::enable_if<!std::is_same<T, std::string>::value, void>::type
get_segments(const std::array<T, N>& arr, ConstMessageSegment* segments, size_t& offset) {
  if constexpr (std::is_arithmetic_v<T>) {
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(arr.data()), arr.size() * sizeof(T));
  } else if constexpr (std::is_base_of_v<Message, T>) {
    for (const auto& item : arr) {
      size_t len = item.get_segment_count() + offset; // Forge length (segment length is checked beforehand)
      item.get_segments(segments, len, offset);
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported array element type");
  }
}

// Overload for const vector of strings
inline void get_segments(const std::vector<std::string>& vec, ConstMessageSegment* segments, size_t& offset) {
  for (const auto& str : vec) {
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(str.data()), str.size());
  }
}

// Overload for const array of strings
template <size_t N>
inline void get_segments(const std::array<std::string, N>& arr, ConstMessageSegment* segments, size_t& offset) {
  for (const auto& str : arr) {
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(str.data()), str.size());
  }
}

// Overload for const ptr_t
inline void get_segments(const ptr_t& ptr, ConstMessageSegment* segments, size_t& offset) {
  if (ptr.get() != nullptr && ptr.size() > 0) {
    segments[offset++] = ConstMessageSegment(reinterpret_cast<const uint8_t*>(ptr.get()), ptr.size());
  }
}

// ===== GET_PREFIX_LEN HELPERS =====

// Overload for std::string
inline uint32_t get_prefix_len(const std::string& /*str*/) { return 4; }

// Overload for Message types
inline uint32_t get_prefix_len(const Message& msg) { return msg.get_prefix_len(); }

// Overload for vectors
template <typename T>
typename std::enable_if<!std::is_same<T, std::string>::value, uint32_t>::type
get_prefix_len(const std::vector<T>& vec) {
  uint32_t total_len = 4; // uint32_t for count
  if constexpr (std::is_arithmetic_v<T>) {
    // No additional prefix lengths for arithmetic types
    return total_len;
  } else if constexpr (std::is_base_of_v<Message, T>) {
    for (const auto& item : vec) {
      total_len += item.get_prefix_len();
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported vector element type");
  }
  return total_len;
}

// Overload for array of Message types
template <typename T, size_t N>
typename std::enable_if<std::is_base_of<Message, T>::value, uint32_t>::type
get_prefix_len(const std::array<T, N>& arr) {
  uint32_t total_len = 0;
  for (const auto& item : arr) {
    total_len += item.get_prefix_len();
  }
  return total_len;
}

// Overload for vector of strings
inline uint32_t get_prefix_len(const std::vector<std::string>& vec) {
  uint32_t total_len = 4 + 4 * static_cast<uint32_t>(vec.size()); // uint32_t for count + uint32_t for each string size
  return total_len;
}

// Overload for array of strings
template <size_t N> inline uint32_t get_prefix_len(const std::array<std::string, N>& arr) {
  uint32_t total_len = 4 * static_cast<uint32_t>(N); // uint32_t for each string size
  return total_len;
}

// Overload for ptr_t
inline uint32_t get_prefix_len(const ptr_t& /*ptr*/) { return 4; }

// ===== GET_PREFIX HELPERS =====

// Overload for strings
inline void get_prefix(const std::string& str, uint8_t* sizes, size_t& offset) {
  *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(str.size());
  offset += 4;
}

// Overload for Message types
inline void get_prefix(const Message& msg, uint8_t* sizes, size_t& offset) { msg.get_prefix(sizes, offset); }

// Overload for vectors
template <typename T>
typename std::enable_if<!std::is_same<T, std::string>::value, void>::type
get_prefix(const std::vector<T>& vec, uint8_t* sizes, size_t& offset) {
  if constexpr (std::is_arithmetic_v<T>) {
    *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(vec.size());
    offset += 4;
  } else if constexpr (std::is_base_of_v<Message, T>) {
    *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(vec.size());
    offset += 4;
    for (const auto& item : vec) {
      item.get_prefix(sizes, offset);
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported vector element type");
  }
}

// Overload for array of Message types
template <typename T, size_t N>
typename std::enable_if<std::is_base_of<Message, T>::value, void>::type
get_prefix(const std::array<T, N>& arr, uint8_t* sizes, size_t& offset) {
  for (const auto& item : arr) {
    item.get_prefix(sizes, offset);
  }
}

// Overload for vector of strings
inline void get_prefix(const std::vector<std::string>& vec, uint8_t* sizes, size_t& offset) {
  *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(vec.size());
  offset += 4;
  for (const auto& str : vec) {
    *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(str.size());
    offset += 4;
  }
}

// Overload for array of strings
template <size_t N> inline void get_prefix(const std::array<std::string, N>& arr, uint8_t* sizes, size_t& offset) {
  for (const auto& str : arr) {
    *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(str.size());
    offset += 4;
  }
}

// Overload for ptr_t
inline void get_prefix(const ptr_t& ptr, uint8_t* sizes, size_t& offset) {
  *reinterpret_cast<uint32_t*>(sizes + offset) = static_cast<uint32_t>(ptr.size());
  offset += 4;
}

// ===== RESIZE HELPERS =====

// Overload for strings
inline void resize(std::string& str, const uint8_t* sizes, size_t& offset) {
  str.resize(*reinterpret_cast<const uint32_t*>(sizes + offset));
  offset += 4;
}

// Overload for Message types
inline void resize(Message& msg, const uint8_t* sizes, size_t& offset) {
  size_t len = msg.get_prefix_len() + offset; // Forge length (prefix length is checked beforehand)
  msg.resize(sizes, len, offset);
}

// Overload for vectors
template <typename T>
typename std::enable_if<!std::is_same<T, std::string>::value, void>::type
resize(std::vector<T>& vec, const uint8_t* sizes, size_t& offset) {
  if constexpr (std::is_arithmetic_v<T>) {
    uint32_t count = *reinterpret_cast<const uint32_t*>(sizes + offset);
    offset += 4;
    vec.resize(count);
  } else if constexpr (std::is_base_of_v<Message, T>) {
    uint32_t count = *reinterpret_cast<const uint32_t*>(sizes + offset);
    offset += 4;
    vec.resize(count);
    for (auto& item : vec) {
      size_t len = item.get_prefix_len() + offset; // Forge length (prefix length is checked beforehand)
      item.resize(sizes, len, offset);
    }
  } else {
    static_assert(always_false<T>::value, "Unsupported vector element type");
  }
}

// Overload for array of Message types
template <typename T, size_t N>
typename std::enable_if<std::is_base_of<Message, T>::value, void>::type
resize(std::array<T, N>& arr, const uint8_t* sizes, size_t& offset) {
  for (auto& item : arr) {
    size_t len = item.get_prefix_len() + offset; // Forge length (prefix length is checked beforehand)
    item.resize(sizes, len, offset);
  }
}

// Overload for vector of strings
inline void resize(std::vector<std::string>& vec, const uint8_t* sizes, size_t& offset) {
  uint32_t count = *reinterpret_cast<const uint32_t*>(sizes + offset);
  offset += 4;
  vec.resize(count);
  for (auto& str : vec) {
    str.resize(*reinterpret_cast<const uint32_t*>(sizes + offset));
    offset += 4;
  }
}

// Overload for array of strings
template <size_t N> inline void resize(std::array<std::string, N>& arr, const uint8_t* sizes, size_t& offset) {
  for (auto& str : arr) {
    str.resize(*reinterpret_cast<const uint32_t*>(sizes + offset));
    offset += 4;
  }
}

// Overload for ptr_t
inline void resize(ptr_t& ptr, const uint8_t* sizes, size_t& offset) {
  uint32_t size = *reinterpret_cast<const uint32_t*>(sizes + offset);
  offset += 4;
  ptr.resize(size);
}

} // namespace detail
} // namespace rix