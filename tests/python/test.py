from rixmsg.standard.header import Header

def print_header(msg: Header):
    print(f"seq: {msg.seq}")
    print(f"stamp.sec: {msg.stamp.sec}")
    print(f"stamp.nsec: {msg.stamp.nsec}")
    print(f"frame_id: {msg.frame_id}")

msg = Header()
msg.seq = 0
msg.stamp.sec = 1234
msg.stamp.nsec = 5678
msg.frame_id = "Hello, world!".encode()

print("Original:")
print_header(msg)

msg2 = Header.decode(msg.encode())

print("\nDecoded:")
print_header(msg2)