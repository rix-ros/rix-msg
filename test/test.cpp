#include <iostream>

#include "rix/msg/error.hpp"
#include "rix/msg/standard/header.hpp"

using namespace rix;

int main() {
    std::shared_ptr<msgs::standard::Header> header(new msgs::standard::Header());
    std::cout << "Header size: " << msgs::standard::Header::size() << std::endl;
    std::cout << "\nHeader def:\n" << msgs::standard::Header::def() << std::endl;

    header->seq = 1234;
    header->stamp.sec = 5678;
    header->stamp.nsec = 9012;
    std::strcpy(header->frameID, "Hello, World!");

    std::cout << "\nHeader:\n" << *header << std::endl;

    std::shared_ptr<char> encodedHeader = msgs::standard::Header::encode(header);
    std::shared_ptr<msgs::standard::Header> decodedHeader = msgs::standard::Header::decode(encodedHeader);

    std::cout << "\nDecoded Header:\n" << *decodedHeader << std::endl;

    std::cout << "\nHeader addr: " << header.get() << std::endl;
    std::cout << "Decoded Header addr: " << decodedHeader.get() << std::endl;
}