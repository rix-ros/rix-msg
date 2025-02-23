from rixmsg.message_base import MessageBase
from OtherMessage import OtherMessage

class ExampleMessage(MessageBase):
    def __init__(self):
        self.number = 0
        self.word = ""
        self.flag = False
        self.object = OtherMessage()
        self.array = []
        self.static_array = [0 for _ in range(3)]
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
        size += MessageBase._size_vector_base(self.array, MessageBase._size_uint32())
        size += MessageBase._size_fixed_array_base(self.static_array, MessageBase._size_uint32())
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
        MessageBase._serialize_vector(self.array, buffer, MessageBase._serialize_uint32)
        MessageBase._serialize_fixed_array(self.static_array, buffer, MessageBase._serialize_uint32, 3)
        MessageBase._serialize_vector(self.array_of_words, buffer, MessageBase._serialize_string)
        MessageBase._serialize_fixed_array(self.static_array_of_words, buffer, MessageBase._serialize_string, 3)
        MessageBase._serialize_vector(self.array_of_objects, buffer, MessageBase._serialize_custom)
        MessageBase._serialize_fixed_array(self.static_array_of_objects, buffer, MessageBase._serialize_custom, 3)

    def deserialize(self, buffer: bytearray, context: dict) -> None:
        self.number = MessageBase._deserialize_uint32(buffer, context)
        self.word = MessageBase._deserialize_string(buffer, context)
        self.flag = MessageBase._deserialize_bool(buffer, context)
        self.object = MessageBase._deserialize_custom(buffer, context, OtherMessage)
        self.array = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_uint32)
        self.static_array = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_uint32, 3)
        self.array_of_words = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string)
        self.static_array_of_words = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, 3)
        self.array_of_objects = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, OtherMessage)
        self.static_array_of_objects = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, 3, OtherMessage)

    def hash(self) -> int:
        return [0x0e63fe00552e3b79, 0x788cc5abcae0282b]