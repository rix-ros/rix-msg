import struct
import abc

class MessageBase(abc.ABC):
    @abc.abstractmethod
    def serialize(self, buffer: bytearray) -> None:
        pass

    @abc.abstractmethod
    def deserialize(self, buffer: bytearray, context: dict) -> None:
        pass

    @abc.abstractmethod
    def size(self) -> int:
        pass

    @abc.abstractmethod
    def hash(self) -> int:
        pass

    @staticmethod
    def _serialize_int8(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('b', value))

    @staticmethod
    def _serialize_uint8(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('B', value))

    @staticmethod
    def _serialize_char(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('c', value))

    @staticmethod
    def _serialize_bool(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('?', value))

    @staticmethod
    def _serialize_int16(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('h', value))

    @staticmethod
    def _serialize_uint16(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('H', value))
        
    @staticmethod
    def _serialize_int32(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('i', value))

    @staticmethod
    def _serialize_uint32(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('I', value))

    @staticmethod
    def _serialize_int64(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('q', value))

    @staticmethod
    def _serialize_uint64(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('Q', value))

    @staticmethod
    def _serialize_float32(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('f', value))

    @staticmethod
    def _serialize_float64(value: int, buffer: bytearray) -> None:
        buffer.extend(struct.pack('d', value))

    @staticmethod
    def _serialize_string(value: str, buffer: bytearray) -> None:
        MessageBase._serialize_uint32(len(value), buffer)
        buffer.extend(struct.pack(f'{len(value)}s', value.encode()))

    @staticmethod
    def _serialize_custom(value: object, buffer: bytearray) -> None:
        value.serialize(buffer)

    @staticmethod
    def _serialize_vector(value: list, buffer: bytearray, func: callable) -> None:
        MessageBase._serialize_uint32(len(value), buffer)
        for item in value:
            func(item, buffer)

    @staticmethod
    def _serialize_fixed_array(value: list, buffer: bytearray, func: callable, size: int) -> None:
        for item in value[:size]:
            func(item, buffer)

    @staticmethod
    def _deserialize_int8(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('b', buffer, context['offset'])[0]
        context['offset'] += 1
        return value
    
    @staticmethod
    def _deserialize_uint8(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('B', buffer, context['offset'])[0]
        context['offset'] += 1
        return value
    
    @staticmethod
    def _deserialize_char(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('c', buffer, context['offset'])[0]
        context['offset'] += 1
        return value
    
    @staticmethod
    def _deserialize_bool(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('?', buffer, context['offset'])[0]
        context['offset'] += 1
        return value
    
    @staticmethod
    def _deserialize_int16(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('h', buffer, context['offset'])[0]
        context['offset'] += 2
        return value
    
    @staticmethod
    def _deserialize_uint16(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('H', buffer, context['offset'])[0]
        context['offset'] += 2
        return value
    
    @staticmethod
    def _deserialize_int32(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('i', buffer, context['offset'])[0]
        context['offset'] += 4
        return value
    
    @staticmethod
    def _deserialize_uint32(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('I', buffer, context['offset'])[0]
        context['offset'] += 4
        return value
    
    @staticmethod
    def _deserialize_int64(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('q', buffer, context['offset'])[0]
        context['offset'] += 8
        return value
    
    @staticmethod
    def _deserialize_uint64(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('Q', buffer, context['offset'])[0]
        context['offset'] += 8
        return value
    
    @staticmethod
    def _deserialize_float32(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('f', buffer, context['offset'])[0]
        context['offset'] += 4
        return value
    
    @staticmethod
    def _deserialize_float64(buffer: bytearray, context: dict) -> int:
        value = struct.unpack_from('d', buffer, context['offset'])[0]
        context['offset'] += 8
        return value
    
    @staticmethod
    def _deserialize_string(buffer: bytearray, context: dict) -> int:
        size = MessageBase._deserialize_uint32(buffer, context)
        value = struct.unpack_from(f'{size}s', buffer, context['offset'])[0].decode()
        context['offset'] += size
        return value
    
    @staticmethod
    def _deserialize_custom(buffer: bytearray, context: dict, obj_type: type) -> object:
        obj = obj_type()
        obj.deserialize(buffer, context)
        return obj
    
    @staticmethod
    def _deserialize_vector(buffer: bytearray, context: dict, func: callable, obj_type: type=None) -> list:
        size = MessageBase._deserialize_uint32(buffer, context)
        if obj_type is not None:
            return [func(buffer, context, obj_type) for _ in range(size)]
        return [func(buffer, context) for _ in range(size)]
    
    @staticmethod
    def _deserialize_fixed_array(buffer: bytearray, context: dict, func: callable, size: int, obj_type: type=None) -> list:
        if obj_type is not None:
            return [func(buffer, context, obj_type) for _ in range(size)]
        return [func(buffer, context) for _ in range(size)]

    @staticmethod
    def _size_int8() -> int:
        return 1
    
    @staticmethod
    def _size_uint8() -> int:
        return 1
    
    @staticmethod
    def _size_char() -> int:
        return 1
    
    @staticmethod
    def _size_bool() -> int:
        return 1
    
    @staticmethod
    def _size_int16() -> int:
        return 2
    
    @staticmethod
    def _size_uint16() -> int:
        return 2
    
    @staticmethod
    def _size_int32() -> int:
        return 4
    
    @staticmethod
    def _size_uint32() -> int:
        return 4
    
    @staticmethod
    def _size_int64() -> int:
        return 8
    
    @staticmethod
    def _size_uint64() -> int:
        return 8
    
    @staticmethod
    def _size_float32() -> int:
        return 4
    
    @staticmethod
    def _size_float64() -> int:
        return 8
    
    @staticmethod
    def _size_string(value: str) -> int:
        return len(value)

    @staticmethod
    def _size_custom(value: object) -> int:
        return value.size()
    
    @staticmethod
    def _size_vector_base(value: list, size: int) -> int:
        return 4 + len(value) * size
    
    @staticmethod
    def _size_vector_string(value: list) -> int:
        return 4 + sum(len(item) for item in value)
    
    @staticmethod
    def _size_vector_custom(value: list) -> int:
        return 4 + sum(item.size() for item in value)
    
    @staticmethod
    def _size_fixed_array_base(value: list, size: int) -> int:
        return len(value) * size
    
    @staticmethod
    def _size_fixed_array_string(value: list, size: int) -> int:
        # return sum(len(item) for item in value)
        return sum(MessageBase._size_string(item) for item in value[:size])
    
    @staticmethod
    def _size_fixed_array_custom(value: list, size: int) -> int:
        return sum(MessageBase._size_custom(item) for item in value[:size])
    