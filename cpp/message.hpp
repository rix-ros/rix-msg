#pragma once

#include <array>
#include <cstdint>
#include <fcntl.h>
#include <iostream>
#include <sys/uio.h>
#include <unistd.h>
#include <vector>

template <typename T> class MessageSegmentBase {
public:
  MessageSegmentBase() = default;
  MessageSegmentBase(T *ptr, uint32_t len) : ptr_(ptr), len_(len) {}

  MessageSegmentBase(const MessageSegmentBase &other) = default;
  MessageSegmentBase &operator=(const MessageSegmentBase &other) = default;
  ~MessageSegmentBase() = default;

  T *ptr() const { return ptr_; }
  uint32_t len() const { return len_; }

private:
  T *ptr_{nullptr};
  uint32_t len_{0};
};

using MessageSegment = MessageSegmentBase<uint8_t>;
using ConstMessageSegment = MessageSegmentBase<const uint8_t>;

class Serializable {
protected:
  template <typename Derived>
  static const std::shared_ptr<Derived> &
  checked_cast(std::shared_ptr<Serializable> size_prefix) {
    static_assert(std::is_base_of<Serializable, Derived>::value,
                  "Derived must derive from Serializable");
    return std::static_pointer_cast<Derived>(size_prefix);
  }

public:
  Serializable() = default;
  virtual ~Serializable() = default;
  virtual size_t size() const = 0;
  virtual void serialize(uint8_t *dst, size_t &offset) const = 0;
  void serialize(std::vector<uint8_t> &dst) const {
    dst.resize(size());
    size_t offset = 0;
    serialize(dst.data(), offset);
  }
  virtual bool deserialize(const uint8_t *src, size_t size, size_t &offset) = 0;
  bool deserialize(const std::vector<uint8_t> &src) {
    size_t offset = 0;
    return deserialize(src.data(), src.size(), offset);
  }
};

class Message : public Serializable {
public:
  using Serializable::deserialize;
  using Serializable::serialize;

  Message() = default;
  virtual ~Message() = default;

  virtual std::array<uint64_t, 2> hash() const = 0;

  virtual bool resize(const uint8_t *sizes, size_t len, size_t &offset) = 0;

  virtual uint32_t get_prefix_len() const = 0;
  virtual void get_prefix(uint8_t *sizes, size_t &offset) const = 0;
  std::vector<uint8_t> get_prefix() const {
    std::vector<uint8_t> sizes_(get_prefix_len());
    size_t offset = 0;
    get_prefix(sizes_.data(), offset);
    return sizes_;
  }

  virtual size_t get_segment_count() const = 0;
  virtual bool get_segments(MessageSegment *segments, size_t len,
                            size_t &offset) = 0;
  virtual bool get_segments(ConstMessageSegment *segments, size_t len,
                            size_t &offset) const = 0;

  std::vector<MessageSegment> get_segments() {
    size_t segment_count = get_segment_count();
    std::vector<MessageSegment> segments_(segment_count);
    size_t offset = 0;
    get_segments(segments_.data(), segments_.size(), offset);
    return segments_;
  }

  std::vector<ConstMessageSegment> get_segments() const {
    size_t segment_count = get_segment_count();
    std::vector<ConstMessageSegment> segments_(segment_count);
    size_t offset = 0;
    get_segments(segments_.data(), segments_.size(), offset);
    return segments_;
  }

  size_t size() const override {
    size_t msg_size = get_prefix_len();
    std::vector<ConstMessageSegment> segments(get_segments());
    for (const auto &seg : segments) {
      msg_size += seg.len();
    }
    return msg_size;
  }

  void serialize(uint8_t *dst, size_t &offset) const override {
    get_prefix(dst, offset);
    serialize_segments_(dst, offset);
  }

  bool deserialize(const uint8_t *src, size_t len, size_t &offset) override {
    if (!resize(src, len, offset)) {
      return false;
    }
    return deserialize_segments_(src, len, offset);
  }

private:
  void serialize_segments_(uint8_t *dst, size_t &offset) const {
    std::vector<ConstMessageSegment> segments(get_segments());
    for (const auto &seg : segments) {
      if (seg.len() == 0) {
        continue;
      }
      std::memcpy(dst + offset, seg.ptr(), seg.len());
      offset += seg.len();
    }
  }

  bool deserialize_segments_(const uint8_t *src, size_t len, size_t &offset) {
    std::vector<MessageSegment> segments(get_segments());
    for (const auto &seg : segments) {
      if (seg.len() == 0) {
        continue;
      }
      if (offset + seg.len() > len) {
        return false;
      }
      std::memcpy(seg.ptr(), src + offset, seg.len());
      offset += seg.len();
    }
    return true;
  }
};
