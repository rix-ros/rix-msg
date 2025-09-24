from rixmsg.message import Message
from rixmsg.standard.Header import Header

def print_header(header: Header):
    print(f"seq: {header.seq}")
    print(f"stamp.sec: {header.stamp.sec}")
    print(f"stamp.nsec: {header.stamp.nsec}")
    print(f"frame_id: {header.frame_id}")

header = Header()
header.seq = 123
header.stamp.sec = 456
header.stamp.nsec = 789
header.frame_id = 'Hello, world!'

print("Original:")
print_header(header)
print(f"Original size: {header.size()}")

header_serialized = bytearray()
header.serialize(header_serialized)

print("Serialized:")
print(header_serialized)
print(f"Serialized size: {len(header_serialized)}")

header_deserialized = Header()
header_deserialized.deserialize(header_serialized, Message.Offset())

print("Deserialized:")
print_header(header_deserialized)
