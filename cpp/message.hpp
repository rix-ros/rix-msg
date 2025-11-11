#pragma once

#include <array>
#include <cstdint>
#include <memory>
#include <string>
#include <vector>

namespace rix {

template <typename T> class MessageSegmentBase {
public:
  MessageSegmentBase() = default;
  MessageSegmentBase(T* ptr, uint32_t len) : ptr_(ptr), len_(len) {}

  MessageSegmentBase(const MessageSegmentBase& other) = default;
  MessageSegmentBase& operator=(const MessageSegmentBase& other) = default;
  ~MessageSegmentBase() = default;

  T* ptr() const { return ptr_; }
  uint32_t len() const { return len_; }

private:
  T* ptr_{nullptr};
  uint32_t len_{0};
};

using MessageSegment = MessageSegmentBase<uint8_t>;
using ConstMessageSegment = MessageSegmentBase<const uint8_t>;

class Serializable {
protected:
  template <typename Derived>
  static const std::shared_ptr<Derived>& checked_cast(std::shared_ptr<Serializable> size_prefix) {
    static_assert(std::is_base_of<Serializable, Derived>::value, "Derived must derive from Serializable");
    return std::static_pointer_cast<Derived>(size_prefix);
  }

public:
  Serializable() = default;
  virtual ~Serializable() = default;
  virtual size_t size() const = 0;
  virtual void serialize(uint8_t* dst, size_t& offset) const = 0;
  void serialize(std::vector<uint8_t>& dst) const {
    dst.resize(size());
    size_t offset = 0;
    serialize(dst.data(), offset);
  }
  virtual bool deserialize(const uint8_t* src, size_t size, size_t& offset) = 0;
  bool deserialize(const std::vector<uint8_t>& src) {
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

  virtual bool resize(const uint8_t* sizes, size_t len, size_t& offset) = 0;

  virtual uint32_t get_prefix_len() const = 0;
  virtual void get_prefix(uint8_t* sizes, size_t& offset) const = 0;
  std::vector<uint8_t> get_prefix() const {
    std::vector<uint8_t> sizes_(get_prefix_len());
    size_t offset = 0;
    get_prefix(sizes_.data(), offset);
    return sizes_;
  }

  virtual size_t get_segment_count() const = 0;
  virtual bool get_segments(MessageSegment* segments, size_t len, size_t& offset) = 0;
  virtual bool get_segments(ConstMessageSegment* segments, size_t len, size_t& offset) const = 0;

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
    for (const auto& seg : segments) {
      msg_size += seg.len();
    }
    return msg_size;
  }

  void serialize(uint8_t* dst, size_t& offset) const override {
    get_prefix(dst, offset);
    serialize_segments_(dst, offset);
  }

  bool deserialize(const uint8_t* src, size_t len, size_t& offset) override {
    if (!resize(src, len, offset)) {
      return false;
    }
    return deserialize_segments_(src, len, offset);
  }

private:
  void serialize_segments_(uint8_t* dst, size_t& offset) const {
    std::vector<ConstMessageSegment> segments(get_segments());
    for (const auto& seg : segments) {
      if (seg.len() == 0) {
        continue;
      }
      std::memcpy(dst + offset, seg.ptr(), seg.len());
      offset += seg.len();
    }
  }

  bool deserialize_segments_(const uint8_t* src, size_t len, size_t& offset) {
    std::vector<MessageSegment> segments(get_segments());
    for (const auto& seg : segments) {
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

class ptr_t {
private:
  std::shared_ptr<uint8_t> owned_ptr_;
  uint8_t* raw_ptr_;
  size_t size_;
  bool owned_;

public:
  ptr_t() : owned_ptr_(nullptr), raw_ptr_(nullptr), size_(0), owned_(false) {}
  ptr_t(size_t size_)
      : owned_ptr_(new uint8_t[size_], std::default_delete<uint8_t[]>()), raw_ptr_(owned_ptr_.get()), size_(size_),
        owned_(true) {}
  ptr_t(uint8_t* raw_ptr_, size_t size_) : owned_ptr_(nullptr), raw_ptr_(raw_ptr_), size_(size_), owned_(false) {}

  ~ptr_t() = default;

  ptr_t(const ptr_t& other)
      : owned_ptr_(other.owned_ptr_), raw_ptr_(other.raw_ptr_), size_(other.size_), owned_(other.owned_) {}
  ptr_t& operator=(const ptr_t& other) {
    if (this != &other) {
      owned_ptr_ = other.owned_ptr_;
      raw_ptr_ = other.raw_ptr_;
      size_ = other.size_;
      owned_ = other.owned_;
    }
    return *this;
  }
  ptr_t(ptr_t&& other) noexcept
      : owned_ptr_(std::move(other.owned_ptr_)), raw_ptr_(other.raw_ptr_), size_(other.size_), owned_(other.owned_) {
    other.raw_ptr_ = nullptr;
    other.size_ = 0;
    other.owned_ = false;
  }
  ptr_t& operator=(ptr_t&& other) noexcept {
    if (this != &other) {
      owned_ptr_ = std::move(other.owned_ptr_);
      raw_ptr_ = other.raw_ptr_;
      size_ = other.size_;
      owned_ = other.owned_;
      other.raw_ptr_ = nullptr;
      other.size_ = 0;
      other.owned_ = false;
    }
    return *this;
  }

  bool operator==(const ptr_t& other) const {
    if (size_ != other.size_) {
      return false;
    }
    if (raw_ptr_ == other.raw_ptr_) {
      return true;
    }
    return true;
  }

  bool operator!=(const ptr_t& other) const { return !(*this == other); }

  uint8_t* get() { return raw_ptr_; }
  const uint8_t* get() const { return raw_ptr_; }
  size_t size() const { return size_; }
  bool owned() const { return owned_; }

  void resize(size_t new_size_) {
    owned_ptr_.reset(new uint8_t[new_size_], std::default_delete<uint8_t[]>());
    raw_ptr_ = owned_ptr_.get();
    size_ = new_size_;
    owned_ = true;
  }
};

} // namespace rix