import ctypes
import struct
from typing import List, Tuple, Any
from message_base import Message, Serializable

type_mapping = {
    bytes: [ctypes.c_char],
    bool: [ctypes.c_bool],
    int: [
        ctypes.c_uint8,
        ctypes.c_uint16,
        ctypes.c_uint32,
        ctypes.c_uint64,
        ctypes.c_int8,
        ctypes.c_int16,
        ctypes.c_int32,
        ctypes.c_int64,
    ],
    float: [ctypes.c_float, ctypes.c_double],
}


def validate_python_type(py_value: Any, ctypes_type: type) -> None:
    if isinstance(py_value, list):
        if len(py_value) == 0:
            return
        first = py_value[0]
        validate_python_type(first, ctypes_type)
        if not all(isinstance(v, type(first)) for v in py_value):
            raise TypeError(
                f"Type mismatch in list: Expected all elements of type {type(first)}, got {py_value}."
            )
        return

    py_type = type(py_value)
    if py_type not in type_mapping or ctypes_type not in type_mapping[py_type]:
        raise TypeError(
            f"Type mismatch: Expected {py_value} for {ctypes_type}, got {py_value}."
        )


class ArithmeticProperty:
    def __init__(self, name: str, type: object):
        self.name = f"_{name}_data"
        self.type = type

    def __get__(self, obj, objtype=None):
        # Return default if not set
        if not hasattr(obj, self.name):
            return 0
        # Return value
        return getattr(obj, self.name).value

    def __set__(self, obj, value: Any):
        # Validate type
        validate_python_type(value, self.type)

        # Set value
        if hasattr(obj, self.name):
            c_value = getattr(obj, self.name)
            c_value.value = value
        else:
            setattr(obj, self.name, self.type(value))

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        # If not set, return empty segment
        if not hasattr(obj, self.name):
            return [(0, 0)]
        # Return address and size of the ctype value
        c_value = getattr(obj, self.name)
        return [(ctypes.addressof(c_value), ctypes.sizeof(c_value))]


class ArithmeticVectorProperty:
    def __init__(self, name: str, type: object):
        self.name = f"_{name}_data"
        self.length_name = f"_{name}_length"
        self.type = type

    def get_raw(self, obj) -> Tuple[ctypes.Array, int] | None:
        if not hasattr(obj, self.name):
            return None
        return getattr(obj, self.name), getattr(obj, self.length_name)

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            return []
        array = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return array[:length]

    def __len__(self, obj) -> int:
        if not hasattr(obj, self.length_name):
            return 0
        return getattr(obj, self.length_name)

    def __set__(self, obj, values: List[Any]):
        # If empty list, set to empty array
        if len(values) == 0:
            setattr(obj, self.name, [])
            return

        # Validate type of first element
        validate_python_type(values, self.type)

        # If array exists, resize or update
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            capacity = len(array)
            if len(values) > capacity:
                # Resize the array
                array_type = self.type * len(values)
                array = array_type(*values)
                setattr(obj, self.name, array)
                setattr(obj, self.length_name, len(values))
            else:
                # Update existing array
                array[: len(values)] = values
                setattr(obj, self.length_name, len(values))
        else:
            # Create new array
            array_type = self.type * len(values)
            array = array_type(*values)
            setattr(obj, self.name, array)
            setattr(obj, self.length_name, len(values))

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        new_size = struct.unpack_from("<I", buffer, offset.value)[0]
        offset.value += 4
        new_array = (self.type * new_size)()
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            length = getattr(obj, self.length_name)
            new_array[: min(length, new_size)] = array[: min(length, new_size)]
            setattr(obj, self.name, new_array)
            setattr(obj, self.length_name, new_size)
        else:
            setattr(obj, self.name, new_array)
            setattr(obj, self.length_name, new_size)

    def get_prefix_len(self, obj) -> int:
        return 4

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        length = 0
        if hasattr(obj, self.length_name):
            length = getattr(obj, self.length_name)
        struct.pack_into("<I", buffer, offset.value, length)
        offset.value += 4

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]
        array = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return [(ctypes.addressof(array), ctypes.sizeof(self.type) * length)]


class ArithmeticArrayProperty:
    def __init__(self, name: str, type: object, length: int):
        self.name = f"_{name}_data"
        self.type = type
        self.length = length

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        array = getattr(obj, self.name)
        return array[:]

    def __set__(self, obj, values: List[Any]):
        # If empty list, set to empty array
        if len(values) != self.length:
            raise ValueError(
                f"Array must be of length {self.length}, got {len(values)}"
            )

        # Validate type of first element
        validate_python_type(values, self.type)

        # If array exists, resize or update
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            capacity = len(array)
            array[:] = values
        else:
            # Create new array
            array_type = self.type * len(values)
            array = array_type(*values)
            setattr(obj, self.name, array)

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]
        array = getattr(obj, self.name)
        return [(ctypes.addressof(array), ctypes.sizeof(self.type) * len(array))]


class StringProperty:
    def __init__(self, name: str):
        self.name = f"_{name}_data"
        self.length_name = f"_{name}_length"

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return ""
        ptr = getattr(obj, self.name)
        return ptr.value.decode("utf-8")

    def __set__(self, obj, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Value must be of type str, got {type(value)}")
        if hasattr(obj, self.name):
            ptr = getattr(obj, self.name)
            encoded = value.encode("utf-8")
            # Resize the buffer if necessary
            if len(encoded) != len(ptr.value):
                new_ptr = ctypes.create_string_buffer(encoded)
                setattr(obj, self.name, new_ptr)
                setattr(obj, self.length_name, len(encoded))
            else:
                ctypes.memmove(ptr, encoded, len(encoded) + 1)
        else:
            encoded = value.encode("utf-8")
            ptr = ctypes.create_string_buffer(encoded)
            setattr(obj, self.name, ptr)
            setattr(obj, self.length_name, len(encoded))

    def resize(self, obj: object, buffer: bytearray, offset: Serializable.Offset) -> None:
        new_size = struct.unpack_from("<I", buffer, offset.value)[0]
        offset.value += 4
        if hasattr(obj, self.name):
            ptr = getattr(obj, self.name)
            new_ptr = ctypes.create_string_buffer(new_size)
            ctypes.memmove(new_ptr, ptr, min(len(ptr), new_size))
            setattr(obj, self.name, new_ptr)
            setattr(obj, self.length_name, new_size)
        else:
            new_ptr = ctypes.create_string_buffer(new_size)
            setattr(obj, self.name, new_ptr)
            setattr(obj, self.length_name, new_size)

    def get_prefix_len(self, obj) -> int:
        return 4

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        length = 0
        if hasattr(obj, self.length_name):
            length = getattr(obj, self.length_name)
        struct.pack_into("<I", buffer, offset.value, length)
        offset.value += 4

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]
        ptr = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return [(ctypes.addressof(ptr), length)]


class StringVectorProperty:
    def __init__(self, name: str):
        self.name = f"_{name}_data"
        self.lengths_name = f"_{name}_lengths"

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        array = getattr(obj, self.name)
        return [array[i].value.decode("utf-8") for i in range(len(array))]

    def __set__(self, obj, value: List[str]):
        if not all(isinstance(v, str) for v in value):
            raise ValueError("All elements must be of type str")
        ptr_list = []
        lengths = []
        for val in value:
            encoded = val.encode("utf-8")
            ptr = ctypes.create_string_buffer(encoded)
            ptr_list.append(ptr)
            lengths.append(len(encoded))

        setattr(obj, self.name, ptr_list)
        setattr(obj, self.lengths_name, lengths)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        new_size = struct.unpack_from("<I", buffer, offset.value)[0]
        offset.value += 4
        old_array = None
        old_length = 0
        if hasattr(obj, self.name):
            old_array = getattr(obj, self.name)
            old_length = len(old_array)
        ptr_list = []
        lengths = []
        for i in range(new_size):
            str_size = struct.unpack_from("<I", buffer, offset.value)[0]
            offset.value += 4
            if i < old_length and old_array is not None:
                old_ptr = old_array[i]
                new_ptr = ctypes.create_string_buffer(str_size)
                ctypes.memmove(new_ptr, old_ptr, min(len(old_ptr), str_size))
                ptr_list.append(new_ptr)
                lengths.append(str_size)
            else:
                new_ptr = ctypes.create_string_buffer(str_size)
                ptr_list.append(new_ptr)
                lengths.append(str_size)
        setattr(obj, self.name, ptr_list)
        setattr(obj, self.lengths_name, lengths)

    def get_prefix_len(self, obj) -> int:
        length = 4  # For the number of strings
        if hasattr(obj, self.name):
            length += len(getattr(obj, self.name)) * 4  # Each string length is a uint32
        return length

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        str_count = 0
        if hasattr(obj, self.name):
            str_count = len(getattr(obj, self.name))
        struct.pack_into("<I", buffer, offset.value, str_count)
        offset.value += 4
        if hasattr(obj, self.name):
            lengths = getattr(obj, self.lengths_name)
            for i in range(str_count):
                str_length = lengths[i]
                struct.pack_into("<I", buffer, offset.value, str_length)
                offset.value += 4

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]

        # Return a segment for each string
        segments = []
        array = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            ptr = array[i]
            str_length = lengths[i]
            segments.append((ctypes.addressof(ptr), str_length))
        return segments

    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        str_count = len(getattr(obj, self.name))
        return str_count


class StringArrayProperty:
    def __init__(self, name: str, length: int):
        self.name = f"_{name}_data"
        self.lengths_name = f"_{name}_lengths"
        self.length = length

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        array = getattr(obj, self.name)
        return [array[i].value.decode("utf-8") for i in range(len(array))]

    def __set__(self, obj, value: List[str]):
        if not isinstance(value, list):
            raise ValueError(f"Value must be of type list, got {type(value)}")
        if not all(isinstance(item, str) for item in value):
            raise ValueError("All elements must be of type str")
        if len(value) != self.length:
            raise ValueError(f"Array must be of length {self.length}, got {len(value)}")
        ptr_list = []
        lengths = []
        for val in value:
            ptr = ctypes.create_string_buffer(val.encode("utf-8"))
            ptr_list.append(ptr)
            lengths.append(len(val))
        setattr(obj, self.name, ptr_list)
        setattr(obj, self.lengths_name, lengths)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        old_array = None
        old_length = 0
        if hasattr(obj, self.name):
            old_array = getattr(obj, self.name)
            old_length = len(old_array)
        ptr_list = []
        lengths = []
        for i in range(self.length):
            str_size = struct.unpack_from("<I", buffer, offset.value)[0]
            offset.value += 4
            if i < old_length and old_array is not None:
                old_ptr = old_array[i]
                new_ptr = ctypes.create_string_buffer(str_size)
                ctypes.memmove(new_ptr, old_ptr, min(len(old_ptr), str_size))
                ptr_list.append(new_ptr)
                lengths.append(str_size)
            else:
                new_ptr = ctypes.create_string_buffer(str_size)
                ptr_list.append(new_ptr)
                lengths.append(str_size)
        setattr(obj, self.name, ptr_list)
        setattr(obj, self.lengths_name, lengths)

    def get_prefix_len(self, obj) -> int:
        length = 0
        if hasattr(obj, self.name):
            length += len(getattr(obj, self.name)) * 4  # Each string length is a uint32
        return length

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        str_count = 0
        if hasattr(obj, self.lengths_name):
            lengths = getattr(obj, self.lengths_name)
            str_count = len(lengths)
            for i in range(str_count):
                str_length = lengths[i]
                struct.pack_into("<I", buffer, offset.value, str_length)
                offset.value += 4

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]

        # Return a segment for each string
        segments = []
        array = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            ptr = array[i]
            str_length = lengths[i]
            segments.append((ctypes.addressof(ptr), str_length))
        return segments

    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        str_count = len(getattr(obj, self.name))
        return str_count


class MessageProperty:
    def __init__(self, name: str, message_type: type):
        self.name = f"_{name}_data"
        self.message_type = message_type

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return self.message_type()
        return getattr(obj, self.name)

    def __set__(self, obj, value):
        if not isinstance(value, self.message_type):
            raise ValueError(f"Value must be of type {self.message_type.__name__}")
        setattr(obj, self.name, value)

    def resize(self, obj, buffer, offset) -> None:
        if not hasattr(obj, self.name):
            message = self.message_type()
            setattr(obj, self.name, message)
        message = getattr(obj, self.name)
        message.resize(buffer, len(buffer), offset)

    def get_prefix_len(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        message = getattr(obj, self.name)
        return message.get_prefix_len()

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        if not hasattr(obj, self.name):
            return
        message = getattr(obj, self.name)
        message.get_prefix(buffer, offset)

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]
        message = getattr(obj, self.name)
        return message.get_segments()
    
    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        message = getattr(obj, self.name)
        return message.get_segment_count()


class MessageVectorProperty:
    def __init__(self, name: str, message_type: type):
        self.name = f"_{name}_data"
        self.message_type = message_type

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        return getattr(obj, self.name)

    def __set__(self, obj, value: List[Any]):
        if not all(isinstance(v, self.message_type) for v in value):
            raise ValueError(
                f"All elements must be of type {self.message_type.__name__}"
            )
        setattr(obj, self.name, value)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        new_size = struct.unpack_from("<I", buffer, offset.value)[0]
        offset.value += 4
        old_array = None
        old_length = 0
        if hasattr(obj, self.name):
            old_array = getattr(obj, self.name)
            old_length = len(old_array)
        message_list = []
        for i in range(new_size):
            if i < old_length and old_array is not None:
                message = old_array[i]
            else:
                message = self.message_type()
            message.resize(buffer, len(buffer), offset)
            message_list.append(message)
        setattr(obj, self.name, message_list)

    def get_prefix_len(self, obj) -> int:
        length = 4  # For the number of messages
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            for message in array:
                length += message.get_prefix_len()
        return length

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        msg_count = 0
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            msg_count = len(array)
        struct.pack_into("<I", buffer, offset.value, msg_count)
        offset.value += 4
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            for message in array:
                message.get_prefix(buffer, offset)

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]

        segments = []
        array = getattr(obj, self.name)
        for message in array:
            segments.extend(message.get_segments())
        return segments

    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        count = 0
        array = getattr(obj, self.name)
        for message in array:
            count += message.get_segment_count()
        return count


class MessageArrayProperty:
    def __init__(self, name: str, message_type: type, length: int):
        self.name = f"_{name}_data"
        self.message_type = message_type
        self.length = length

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        return getattr(obj, self.name)

    def __set__(self, obj, value: List[Any]):
        if len(value) != self.length:
            raise ValueError(f"Array must be of length {self.length}, got {len(value)}")
        if not all(isinstance(v, self.message_type) for v in value):
            raise ValueError(
                f"All elements must be of type {self.message_type.__name__}"
            )
        setattr(obj, self.name, value)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        old_array = None
        old_length = 0
        if hasattr(obj, self.name):
            old_array = getattr(obj, self.name)
            old_length = len(old_array)
        message_list = []
        for i in range(self.length):
            if i < old_length and old_array is not None:
                message = old_array[i]
            else:
                message = self.message_type()
            message.resize(buffer, len(buffer), offset)
            message_list.append(message)
        setattr(obj, self.name, message_list)

    def get_prefix_len(self, obj) -> int:
        length = 0
        if hasattr(obj, self.name):
            array = getattr(obj, self.name)
            for message in array:
                length += message.get_prefix_len()
        return length

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        if not hasattr(obj, self.name):
            return
        array = getattr(obj, self.name)
        for message in array:
            message.get_prefix(buffer, offset)

    def get_segments(self, obj) -> List[Tuple[int, int]]:
        if not hasattr(obj, self.name):
            return [(0, 0)]

        segments = []
        array = getattr(obj, self.name)
        for message in array:
            segments.extend(message.get_segments())
        return segments

    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        count = 0
        array = getattr(obj, self.name)
        for message in array:
            count += message.get_segment_count()
        return count


def init_string(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, StringProperty(property_name))


def init_string_vector(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, StringVectorProperty(property_name))


def init_string_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        StringArrayProperty(property_name, length),
    )


def init_bool(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_bool)
    )


def init_char(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_char)
    )


def init_int8(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_int8)
    )


def init_uint8(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_uint8)
    )


def init_int16(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_int16)
    )


def init_uint16(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_uint16)
    )


def init_int32(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_int32)
    )


def init_uint32(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_uint32)
    )


def init_int64(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_int64)
    )


def init_uint64(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_uint64)
    )


def init_float(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_float)
    )


def init_double(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__, property_name, ArithmeticProperty(property_name, ctypes.c_double)
    )


def init_bool_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_bool),
    )


def init_char_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_char),
    )


def init_int8_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_int8),
    )


def init_uint8_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_uint8),
    )


def init_int16_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_int16),
    )


def init_uint16_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_uint16),
    )


def init_int32_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_int32),
    )


def init_uint32_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_uint32),
    )


def init_int64_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_int64),
    )


def init_uint64_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_uint64),
    )


def init_float_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_float),
    )


def init_double_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, ctypes.c_double),
    )


def init_bool_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_bool, length),
    )


def init_char_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_char, length),
    )


def init_int8_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_int8, length),
    )


def init_uint8_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_uint8, length),
    )


def init_int16_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_int16, length),
    )


def init_uint16_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_uint16, length),
    )


def init_int32_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_int32, length),
    )


def init_uint32_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_uint32, length),
    )


def init_int64_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_int64, length),
    )


def init_uint64_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_uint64, length),
    )


def init_float_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_float, length),
    )


def init_double_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, ctypes.c_double, length),
    )


def init_message(obj: object, property_name: str, message_type: type) -> None:
    setattr(obj.__class__, property_name, MessageProperty(property_name, message_type))


def init_message_vector(obj: object, property_name: str, message_type: type) -> None:
    setattr(
        obj.__class__,
        property_name,
        MessageVectorProperty(property_name, message_type),
    )


def init_message_array(
    obj: object, property_name: str, message_type: type, length: int
) -> None:
    setattr(
        obj.__class__,
        property_name,
        MessageArrayProperty(property_name, message_type, length),
    )


def resize(obj: object, name: str, buffer: bytes, offset: Serializable.Offset) -> None:
    type(obj).__dict__[name].resize(obj, buffer, offset)


def get_prefix_len(obj, name) -> int:
    return type(obj).__dict__[name].get_prefix_len(obj)


def get_prefix(obj, name, buffer: bytearray, offset: Serializable.Offset) -> None:
    type(obj).__dict__[name].get_prefix(obj, buffer, offset)


def get_segment_count(obj, name) -> int:
    return type(obj).__dict__[name].get_segment_count(obj)


# class ExampleB(Message):
#     def __init__(self):
#         init_uint32(self, "id")
#         init_string(self, "description")
#         init_string_array(self, "tags", 5)
#         self._property_names = ["id", "description", "tags"]

#         self.id = 0
#         self.description = ""
#         self.tags = [""] * 5

#     def hash(self) -> List[int]:
#         return [0x2, 0x3]

#     def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
#         if length < offset.value + self.get_prefix_len():
#             return False
#         resize(self, "description", buffer, offset)
#         resize(self, "tags", buffer, offset)
#         return True

#     def get_prefix_len(self) -> int:
#         length = 0
#         length += get_prefix_len(self, "description")
#         length += get_prefix_len(self, "tags")
#         return length

#     def get_prefix(self, buffer: bytearray, offset: Serializable.Offset) -> None:
#         get_prefix(self, "description", buffer, offset)

#     def get_segment_count(self) -> int:
#         count = 0
#         count += 4  # for id
#         count += get_segment_count(self, "description")
#         count += get_segment_count(self, "tags")
#         return count

#     def get_segments(self) -> list[Tuple[int, int]]:
#         # Returns a list of (ptr, length) tuples for each segment
#         segments = []
#         for prop_name in self._property_names:
#             # Access the descriptor from the class, not the instance
#             prop_descriptor = type(self).__dict__[prop_name]
#             segments.extend(prop_descriptor.get_segments(self))
#         return segments


# class Example(Message):
#     def __init__(self):
#         init_string(self, "name")
#         init_uint32(self, "age")
#         init_double_vector(self, "scores")
#         init_int16_array(self, "data", 10)
#         init_string_vector(self, "data_strings")
#         init_message(self, "nested", ExampleB)
#         init_message_vector(self, "nested_vector", ExampleB)
#         init_message_array(self, "nested_array", ExampleB, 3)
#         self._property_names = [
#             "name",
#             "age",
#             "scores",
#             "data",
#             "data_strings",
#             "nested",
#             "nested_vector",
#             "nested_array",
#         ]

#         self.name = ""
#         self.age = 0
#         self.scores = []
#         self.data = [0] * 10
#         self.data_strings = []
#         self.nested = ExampleB()
#         self.nested_vector = []
#         self.nested_array = [ExampleB() for _ in range(3)]

#     def hash(self) -> List[int]:
#         return [0x0, 0x1]

#     def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
#         if length < offset.value + self.get_prefix_len():
#             return False
#         resize(self, "name", buffer, offset)
#         resize(self, "scores", buffer, offset)
#         resize(self, "data_strings", buffer, offset)
#         resize(self, "nested", buffer, offset)
#         resize(self, "nested_vector", buffer, offset)
#         resize(self, "nested_array", buffer, offset)
#         return True

#     def get_prefix_len(self) -> int:
#         length = 0
#         length += get_prefix_len(self, "name")
#         length += get_prefix_len(self, "scores")
#         length += get_prefix_len(self, "data_strings")
#         length += get_prefix_len(self, "nested")
#         length += get_prefix_len(self, "nested_vector")
#         length += get_prefix_len(self, "nested_array")
#         return length

#     def get_prefix(self, buffer: bytearray, offset: Serializable.Offset) -> None:
#         get_prefix(self, "name", buffer, offset)
#         get_prefix(self, "scores", buffer, offset)
#         get_prefix(self, "data_strings", buffer, offset)
#         get_prefix(self, "nested", buffer, offset)
#         get_prefix(self, "nested_vector", buffer, offset)
#         get_prefix(self, "nested_array", buffer, offset)

#     def get_segment_count(self) -> int:
#         count = 0
#         count += 4
#         count += get_segment_count(self, "data_strings")
#         count += get_segment_count(self, "nested")
#         count += get_segment_count(self, "nested_vector")
#         count += get_segment_count(self, "nested_array")
#         return count

#     def get_segments(self) -> list[Tuple[int, int]]:
#         # Returns a list of (ptr, length) tuples for each segment
#         segments = []
#         for prop_name in self._property_names:
#             # Access the descriptor from the class, not the instance
#             prop_descriptor = type(self).__dict__[prop_name]
#             segments.extend(prop_descriptor.get_segments(self))
#         return segments


# def test():
#     example = Example()
#     example.name = "Alice"
#     example.age = 30
#     example.scores = [95.5, 88.0, 76.5]
#     example.data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
#     example.data_strings = ["one", "two", "three"]
#     example.nested.id = 1
#     example.nested.description = "This is a nested message."
#     example.nested.tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
#     example.nested_vector = [ExampleB() for _ in range(3)]
#     example.nested_array = [ExampleB() for _ in range(3)]
#     print(f"Name: {example.name}")
#     print(f"Age: {example.age}")
#     print(f"Scores: {example.scores}")
#     print(f"Scores Raw: {example.get_raw('scores')}")
#     print(f"Data: {example.data}")
#     print(f"Data Strings: {example.data_strings}")
#     print(f"Nested ID: {example.nested.id}")
#     print(f"Nested Description: {example.nested.description}")
#     print(f"Nested Tags: {example.nested.tags}")

#     # Get segments
#     segments = example.get_segments()
#     for i, (ptr, length) in enumerate(segments):
#         print(f"Segment {i}: ptr=0x{ptr:x}, length={length}")

#     # Reassign properties
#     example.name = "Nicholas"
#     example.age = 25
#     example.scores = [85.0, 90.0, 92.5, 88.0]
#     example.data = [10, 9, 8, 7, 6, 5, 4, 3, 2, 1]
#     example.data_strings = ["ten", "nine", "eight", "seven"]
#     example.nested.id = 2
#     example.nested.description = "Nested Example"
#     example.nested.tags = ["newtag1", "newtag2", "newtag3", "newtag4", "newtag5"]
#     print(f"Updated Name: {example.name}")
#     print(f"Updated Age: {example.age}")
#     print(f"Updated Scores: {example.scores}")
#     print(f"Updated Scores Raw: {example.get_raw('scores')}")
#     print(f"Updated Data: {example.data}")
#     print(f"Updated Data Strings: {example.data_strings}")
#     print(f"Updated Nested ID: {example.nested.id}")
#     print(f"Updated Nested Description: {example.nested.description}")
#     print(f"Updated Nested Tags: {example.nested.tags}")

#     # Get segments again
#     segments = example.get_segments()
#     for i, (ptr, length) in enumerate(segments):
#         print(f"Segment {i}: ptr=0x{ptr:x}, length={length}")

#     # Example 2
#     example2 = Example()
#     example2.name = "Charlie"
#     example2.age = 40
#     example2.scores = [100.0]
#     example2.data = [0, -1, -2, -3, -4, -5, -6, -7, -8, -9]
#     example2.data_strings = ["zero", "minus one", "minus two"]
#     example2.nested.id = 3
#     example2.nested.description = "Another nested message."
#     example2.nested.tags = ["tag1", "tag2", "tag3", "tag4", "tag5"]
#     print(f"Example2 Name: {example2.name}")
#     print(f"Example2 Age: {example2.age}")
#     print(f"Example2 Scores: {example2.scores}")
#     print(f"Example2 Scores Raw: {example2.get_raw('scores')}")
#     print(f"Example2 Data: {example2.data}")
#     print(f"Example2 Data Strings: {example2.data_strings}")
#     print(f"Example2 Nested ID: {example2.nested.id}")
#     print(f"Example2 Nested Description: {example2.nested.description}")
#     print(f"Example2 Nested Tags: {example2.nested.tags}")

#     # Get the segments
#     segments = example2.get_segments()

#     # Print location and length of each segment
#     for i, (ptr, length) in enumerate(segments):
#         print(f"Segment {i}: ptr=0x{ptr:x}, length={length}")

#     # Get prefix bytes
#     prefix_bytes = example.get_prefix_bytes()
#     print(f"Prefix bytes: {prefix_bytes}")


# if __name__ == "__main__":
#     test()
