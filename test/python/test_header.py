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
header.frame_id = "Hello, world!"

print("Original:")
print_header(header)

header_serialized = bytearray()
header.serialize(header_serialized)
print("\Serialized:")
print(header_serialized)

context = {'offset': 0}
header_deserialized = Header()
header_deserialized.deserialize(header_serialized, context)

print("\Deserialized:")
print_header(header_deserialized)
