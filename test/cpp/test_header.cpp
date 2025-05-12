#include <iomanip>
#include <iostream>

#include "rix/msg/standard/Header.hpp"

using Header = rix::msg::standard::Header;

void print_header(const Header &header) {
    std::cout << "Header:\n";
    std::cout << "seq: " << header.seq << std::endl;
    std::cout << "stamp.sec: " << header.stamp.sec << std::endl;
    std::cout << "stamp.nsec: " << header.stamp.nsec << std::endl;
    std::cout << "frame_id: " << header.frame_id << std::endl;
}

void print_encoded(const std::vector<uint8_t> &encoded) {
    for (const uint8_t &byte : encoded) {
        std::cout << "0x" << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(byte) << " ";
    }
    std::cout << std::dec << std::endl;
}

int main() {
    Header header;
    header.seq = 1234;
    header.stamp.sec = 5678;
    header.stamp.nsec = 9012;
    header.frame_id = "Hello, world!";

    std::cout << "Original:\n";
    print_header(header);

    std::vector<uint8_t> encoded;
    if (!header.serialize(encoded)) {
        std::cerr << "Serialization failed!" << std::endl;
        return 1;
    }

    std::cout << "Encoded:\n";
    print_encoded(encoded);

    Header header_decoded;
    size_t offset = 0;
    if (!header_decoded.deserialize(encoded, offset)) {
        std::cerr << "Deserialization failed!" << std::endl;
        return 1;
    }

    std::cout << "\nDecoded:\n";
    print_header(header_decoded);
}