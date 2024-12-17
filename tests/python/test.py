from rixmsg.standard.Header import Header

def print_header(header: Header):
    print(f"seq: {header.seq}")
    print(f"stamp.sec: {header.stamp.sec}")
    print(f"stamp.nsec: {header.stamp.nsec}")
    print(f"frame_id: {header.frame_id}")

header = Header()
header.seq = 0
header.stamp.sec = 1234
header.stamp.nsec = 5678
header.frame_id = "Hello, world!".encode()

print("Original:")
print_header(header)

header_encoded = header.encode()
print("\nEncoded:")
print(header_encoded)

header_decoded = Header.decode(header_encoded)

print("\nDecoded:")
print_header(header_decoded)
