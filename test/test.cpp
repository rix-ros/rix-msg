#include <iostream>

#include "rix/msg/common.hpp"
#include "rix/msg/standard/header.hpp"

using namespace rix;

using msg::standard::Header;

int main() {
    ASSERT_RIXMSG_TYPE(Header);

    std::cout << "Header size: " << msg::standard::Header::size() << std::endl;
    std::cout << "\nHeader def:\n" << msg::standard::Header::def() << std::endl;

    Header header;
    header.seq = 1234;
    header.stamp.sec = 5678;
    header.stamp.nsec = 9012;
    std::strcpy(header.frameID, "Hello, World!");

    std::cout << "\nHeader:\n" << header << std::endl;

    const void *encodedHeader = msg::standard::Header::encode(&header);
    const Header *decodedHeader = msg::standard::Header::decode(encodedHeader, msg::standard::Header::size());

    std::cout << "\nDecoded Header:\n" << *decodedHeader << std::endl;

    std::cout << "\nHeader addr: " << &header << std::endl;
    std::cout << "Decoded Header addr: " << decodedHeader << std::endl;
}