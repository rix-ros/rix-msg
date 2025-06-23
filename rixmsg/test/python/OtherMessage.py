from rixmsg.message_base import MessageBase

class OtherMessage(MessageBase):
    def __init__(self):
        self.number = 0.0
        self.flag = False

    def size(self) -> int:
        size = 0
        size += MessageBase._size_double()
        size += MessageBase._size_bool()
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        MessageBase._serialize_double(self.number, buffer)
        MessageBase._serialize_bool(self.flag, buffer)

    def deserialize(self, buffer: bytearray, context: dict) -> None:
        self.number = MessageBase._deserialize_double(buffer, context)
        self.flag = MessageBase._deserialize_bool(buffer, context)

    def hash(self) -> int:
        return [0x309c08666f8285b7, 0xe5ca3cc56cb0fbec]