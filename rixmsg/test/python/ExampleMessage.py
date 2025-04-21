from rixmsg.message_base import MessageBase
from rixmsg.example.OtherMessage import OtherMessage

class ExampleMessage(MessageBase):
    def __init__(self):
        self.number = 0
        self.word = ""
        self.flag = False
        self.object = OtherMessage()
        self.array = []
        self.static_array = [0.0 for _ in range(3)]
        self.array_of_words = []
        self.static_array_of_words = ["" for _ in range(3)]
        self.array_of_objects = []
        self.static_array_of_objects = [OtherMessage() for _ in range(3)]

    def size(self) -> int:
        size = 0
        size += MessageBase._size_uint32()
        size += MessageBase._size_string(self.word)
        size += MessageBase._size_bool()
        size += MessageBase._size_custom(self.object)
        size += MessageBase._size_vector_base(self.array, MessageBase._size_float())
        size += MessageBase._size_fixed_array_base(self.static_array, MessageBase._size_float())
        size += MessageBase._size_vector_string(self.array_of_words)
        size += MessageBase._size_fixed_array_string(self.static_array_of_words, 3)
        size += MessageBase._size_vector_custom(self.array_of_objects)
        size += MessageBase._size_fixed_array_custom(self.static_array_of_objects, 3)
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        MessageBase._serialize_uint32(self.number, buffer)
        MessageBase._serialize_string(self.word, buffer)
        MessageBase._serialize_bool(self.flag, buffer)
        MessageBase._serialize_custom(self.object, buffer)
        MessageBase._serialize_float(self.array, buffer, len(self.array), False)
        MessageBase._serialize_float(self.static_array, buffer, 3, True)
        MessageBase._serialize_string(self.array_of_words, buffer, len(self.array_of_words), False)
        MessageBase._serialize_string(self.static_array_of_words, buffer, 3, True)
        MessageBase._serialize_custom(self.array_of_objects, buffer, len(self.array_of_objects), False)
        MessageBase._serialize_custom(self.static_array_of_objects, buffer, 3, True)

    def deserialize(self, buffer: bytearray, context: dict) -> None:
        self.number = MessageBase._deserialize_uint32(buffer, context)
        self.word = MessageBase._deserialize_string(buffer, context)
        self.flag = MessageBase._deserialize_bool(buffer, context)
        self.object = MessageBase._deserialize_custom(buffer, context, OtherMessage)
        self.array = MessageBase._deserialize_float(buffer, context, False)
        self.static_array = MessageBase._deserialize_float(buffer, context, True, 3)
        self.array_of_words = MessageBase._deserialize_string(buffer, context, False)
        self.static_array_of_words = MessageBase._deserialize_string(buffer, context, True, 3)
        self.array_of_objects = MessageBase._deserialize_custom(buffer, context, OtherMessage, False)
        self.static_array_of_objects = MessageBase._deserialize_custom(buffer, context, OtherMessage, True, 3)

    def hash(self) -> int:
        return [0xd3b5843a81f422d9, 0x316fab08fd66c0d5]