#pragma once

#include <memory>
#include <ostream>
#include <type_traits>

#include "rix/msg/component/MessageInfo.hpp"
#include "rix/msg/component/ComponentInfo.hpp"
#include "rix/msg/standard/Header.hpp"
#include "rix/msg/standard/Time.hpp"
#include "rix/util/timing.hpp"

namespace rix {
namespace msg {

inline standard::Time get_time() {
    int64_t t = rix::util::nanos();
    standard::Time time;
    time.sec = t / 1000000000;
    time.nsec = t % 1000000000;
    return time;
}

inline standard::Header create_header(uint32_t seq, const std::string &frame_id) {
    standard::Header header;
    header.seq = seq;
    header.stamp = get_time();
    std::strncpy(header.frame_id, frame_id.c_str(), sizeof(header.frame_id));
    return header;
}

template <typename T>
concept RixMsgType = requires(T t, const uint8_t *data, size_t size) {
    { t.encode() } -> std::same_as<const uint8_t *>;
    { T::decode(data, size) } -> std::same_as<const T *>;
    { T::info() } -> std::same_as<rix::msg::component::MessageInfo>;
    { T::size() } -> std::same_as<uint32_t>;
};
#define ASSERT_RIXMSG_TYPE(TMsg) static_assert(rix::msg::RixMsgType<TMsg>, "TMsg is not a rixmsg type");

inline bool operator==(const component::MessageInfo &lhs, const component::MessageInfo &rhs) {
    return lhs.hash_lower == rhs.hash_lower && lhs.hash_upper == rhs.hash_upper && lhs.length == rhs.length;
}

inline bool operator!=(const component::MessageInfo &lhs, const component::MessageInfo &rhs) {
    return !(lhs == rhs);
}

}  // namespace msg
}  // namespace rix