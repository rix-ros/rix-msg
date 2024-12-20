#include <iostream>
#include <iomanip>
#include "rix/msg/common.hpp"
#include "rix/msg/standard/Header.hpp"

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

    std::cout << "Original:\n";
    print_header(header);

    const uint8_t *encoded_header = header.encode();
    std::cout << "\nEncoded:\n";
    for (size_t i = 0; i < Header::size(); i++) {
        std::cout << "0x" << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(encoded_header[i]) << " ";
    }
    std::cout << std::dec << std::endl;

    const Header *decoded_header = Header::decode(header.encode(), Header::size());
    
    std::cout << "\nDecoded:\n";
    print_header(*decoded_header);
}