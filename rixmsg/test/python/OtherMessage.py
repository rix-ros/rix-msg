from rixmsg.message_base import MessageBase

class OtherMessage(MessageBase):
    def __init__(self):
        self.number = 0
        self.flag = False

    def size(self) -> int:
        size = 0
        size += MessageBase._size_int16(self.number)
        size += MessageBase._size_bool(self.flag)
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        MessageBase._serialize_int16(self.number, buffer)
        MessageBase._serialize_bool(self.flag, buffer)

    def deserialize(self, buffer: bytearray, context: dict) -> None:
        self.number = MessageBase._deserialize_int16(buffer, context)
        self.flag = MessageBase._deserialize_bool(buffer, context)

    def hash(self) -> int:
        return [0x3ca3b57c64691de0, 0x33fa64726faff850]