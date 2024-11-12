#include <iostream>

#include "rix/msg/common.hpp"
#include "rix/msg/standard/header.hpp"

using Header = rix::msg::standard::Header;

void print_header(const Header &header) {
    std::cout << "Header:\n";
    std::cout << "seq: " << header.seq << std::endl;
    std::cout << "stamp.sec: " << header.stamp.sec << std::endl;
    std::cout << "stamp.nsec: " << header.stamp.nsec << std::endl;
    std::cout << "frame_id: " << header.frame_id << std::endl;
}

int main() {
    ASSERT_RIXMSG_TYPE(Header);

    Header header;
    header.seq = 1234;
    header.stamp.sec = 5678;
    header.stamp.nsec = 9012;
    std::strcpy(header.frame_id, "Hello, world!");

    print_header(header);

    const Header *decodedHeader = Header::decode(header.encode(), Header::size());

    print_header(*decodedHeader);
}