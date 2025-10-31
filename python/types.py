import ctypes
import struct
from typing import List, Tuple, Any

from rix.msg import Serializable

py_to_ctypes = {
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

ctypes_to_py = {
    ctypes.c_char: bytes,
    ctypes.c_bool: bool,
    ctypes.c_uint8: int,
    ctypes.c_uint16: int,
    ctypes.c_uint32: int,
    ctypes.c_uint64: int,
    ctypes.c_int8: int,
    ctypes.c_int16: int,
    ctypes.c_int32: int,
    ctypes.c_int64: int,
    ctypes.c_float: float,
    ctypes.c_double: float,
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
    if py_type not in py_to_ctypes or ctypes_type not in py_to_ctypes[py_type]:
        raise TypeError(
            f"Type mismatch: Expected {ctypes_to_py[ctypes_type]} for {ctypes_type}, got {py_type}."
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