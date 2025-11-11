import struct
from typing import List, Tuple, Any

from rix.msg import Serializable

py_to_raw_type: dict[type, List[str]] = {
    bytes: ["c"],
    bool: ["?"],
    int: ["B", "b", "H", "h", "I", "i", "Q", "q"],
    float: ["f", "d"],
}

raw_type_to_py: dict[str, type] = {
    "c": bytes,
    "?": bool,
    "B": int,
    "b": int,
    "H": int,
    "h": int,
    "I": int,
    "i": int,
    "Q": int,
    "q": int,
    "f": float,
    "d": float,
}

raw_type_to_size: dict[str, int] = {
    "c": 1,
    "?": 1,
    "B": 1,
    "b": 1,
    "H": 2,
    "h": 2,
    "I": 4,
    "i": 4,
    "Q": 8,
    "q": 8,
    "f": 4,
    "d": 8,
}


def validate_python_type(py_value: Any, ctypes_type: str) -> None:
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
    if py_type not in py_to_raw_type or ctypes_type not in py_to_raw_type[py_type]:
        raise TypeError(
            f"Type mismatch: Expected {raw_type_to_py[ctypes_type]} for {ctypes_type}, got {py_type}."
        )


class ArithmeticProperty:
    def __init__(self, name: str, type: str):
        if type not in raw_type_to_py:
            raise TypeError(
                f"Arithmetic type must be one of the following: {raw_type_to_py.keys}, got: {type}"
            )
        self.name = f"_{name}_data"
        self.type = type

    def __get__(self, obj, objtype=None):
        # Return default if not set
        if not hasattr(obj, self.name):
            return 0
        # Convert buffer based on type
        buffer = getattr(obj, self.name)
        return struct.unpack_from(self.type, buffer)[0]

    def __set__(self, obj, value: Any):
        # Validate type
        validate_python_type(value, self.type)

        # Initialize buffer if it does not exist
        if not hasattr(obj, self.name):
            setattr(obj, self.name, memoryview(bytearray(raw_type_to_size[self.type])))

        # Copy integer into buffer
        buffer = getattr(obj, self.name)
        struct.pack_into(self.type, buffer, 0, value)

    def get_segments(self, obj) -> List[memoryview]:
        # If not set, return empty segment
        if not hasattr(obj, self.name):
            return [memoryview(bytearray())]
        # Return underlying buffer
        buffer = getattr(obj, self.name)
        return [buffer]


class ArithmeticVectorProperty:
    def __init__(self, name: str, type: str):
        if type not in raw_type_to_py:
            raise TypeError(
                f"Arithmetic type must be one of the following: {raw_type_to_py.keys}, got: {type}"
            )
        self.name = f"_{name}_data"
        self.length_name = f"_{name}_length"
        self.type = type

    def set_raw(self, obj, buffer: memoryview, length: int) -> None:
        if not isinstance(buffer, memoryview):
            raise TypeError("Buffer must be a memoryview")
        if length > len(buffer):
            raise ValueError(
                "Length parameter must be less than or equal to the actual length of the buffer"
            )
        setattr(obj, self.name, buffer)
        setattr(obj, self.length_name, length)

    def get_raw(self, obj) -> Tuple[memoryview, int] | None:
        if not hasattr(obj, self.name):
            return None
        return getattr(obj, self.name), getattr(obj, self.length_name)

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            return []
        buffer = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        format_str: str = self.type * (length // raw_type_to_size[self.type])
        return list(struct.unpack_from(format_str, buffer, 0))

    def __len__(self, obj) -> int:
        if not hasattr(obj, self.length_name):
            return 0
        return getattr(obj, self.length_name)

    def __set__(self, obj, values: List[Any]):
        # If empty list, set to empty array
        if len(values) == 0:
            setattr(obj, self.name, memoryview(bytearray()))
            setattr(obj, self.length_name, 0)
            return

        # Validate type of first element
        validate_python_type(values, self.type)

        # If buffer does not exist, create it
        new_length: int = len(values) * raw_type_to_size[self.type]
        if not hasattr(obj, self.name):
            # Create new buffer
            format_str = self.type * len(values)
            buffer = memoryview(bytearray(new_length))
            struct.pack_into(format_str, buffer, 0, *values)
            setattr(obj, self.name, buffer)
            setattr(obj, self.length_name, new_length)
            return

        buffer: memoryview = getattr(obj, self.name)
        old_length: int = getattr(obj, self.length_name)
        if new_length > old_length:
            # Resize the buffer
            underlying: bytearray = buffer.obj
            buffer.release()
            if not isinstance(underlying, bytearray):
                underlying = bytearray(underlying)
            underlying.extend(bytearray(new_length - old_length))
            buffer = memoryview(underlying)
            setattr(obj, self.name, buffer)

        # Update buffer and length
        format_str = self.type * len(values)
        struct.pack_into(format_str, buffer, 0, *values)
        setattr(obj, self.length_name, new_length)

    def resize(self, obj: object, src: memoryview, offset: Serializable.Offset) -> None:
        new_length = (
            struct.unpack_from("I", src, offset.value)[0] * raw_type_to_size[self.type]
        )
        offset.value += 4

        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            setattr(obj, self.name, memoryview(bytearray(new_length)))
            setattr(obj, self.length_name, new_length)
            return

        buffer: memoryview = getattr(obj, self.name)
        old_length: int = getattr(obj, self.length_name)
        if new_length > old_length:
            # Resize the buffer
            underlying: bytearray = buffer.obj
            buffer.release()
            if not isinstance(underlying, bytearray):
                underlying = bytearray(underlying)
            underlying.extend(bytearray(new_length - old_length))
            setattr(obj, self.name, memoryview(underlying))

        setattr(obj, self.length_name, new_length)

    def get_prefix_len(self, obj) -> int:
        return 4

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        length = 0
        if hasattr(obj, self.length_name):
            length = getattr(obj, self.length_name) // raw_type_to_size[self.type]
        struct.pack_into("I", buffer, offset.value, length)
        offset.value += 4

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray())]
        buffer = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return [buffer[:length]]


class ArithmeticArrayProperty:
    def __init__(self, name: str, type: str, length: int):
        self.name = f"_{name}_data"
        self.type = type
        self.length = length

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        buffer = getattr(obj, self.name)
        format_str: str = self.type * self.length
        return list(struct.unpack_from(format_str, buffer, 0))

    def __set__(self, obj, values: List[Any]):
        if len(values) != self.length:
            raise ValueError(
                f"Array must be of length {self.length}, got {len(values)}"
            )

        # Validate type of list elements
        validate_python_type(values, self.type)

        # If array exists, update
        format_str: str = self.type * self.length
        if hasattr(obj, self.name):
            buffer = getattr(obj, self.name)
            struct.pack_into(format_str, buffer, 0, *values)
        else:
            # Create new array
            buffer = memoryview(bytearray(self.length * raw_type_to_size[self.type]))
            struct.pack_into(format_str, buffer, 0, *values)
            setattr(obj, self.name, buffer)

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray())]
        return [getattr(obj, self.name)]


class StringProperty:
    def __init__(self, name: str):
        self.name = f"_{name}_data"
        self.length_name = f"_{name}_length"

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            return ""
        buffer = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return buffer.obj.decode("utf-8")[:length]

    def __set__(self, obj, value: str):
        if not isinstance(value, str):
            raise ValueError(f"Value must be of type str, got {type(value)}")

        encoded = value.encode("utf-8")
        new_length = len(encoded)
        if not hasattr(obj, self.name):
            setattr(obj, self.name, memoryview(bytearray(encoded)))
            setattr(obj, self.length_name, new_length)
            return

        buffer: memoryview = getattr(obj, self.name)
        old_length = getattr(obj, self.length_name)
        if new_length > old_length:
            underlying: bytearray = buffer.obj
            buffer.release()
            if not isinstance(underlying, bytearray):
                underlying = bytearray(underlying)
            underlying.extend(bytearray(new_length - old_length))
            buffer = memoryview(underlying)
        buffer[:new_length] = encoded
        setattr(obj, self.name, buffer)
        setattr(obj, self.length_name, new_length)

    def resize(self, obj: object, src: bytearray, offset: Serializable.Offset) -> None:
        new_length = struct.unpack_from("I", src, offset.value)[0]
        offset.value += 4

        if not hasattr(obj, self.name):
            setattr(obj, self.name, memoryview(bytearray(new_length)))
            setattr(obj, self.length_name, new_length)
            return

        buffer: memoryview = getattr(obj, self.name)
        old_length: int = getattr(obj, self.length_name)
        if new_length > old_length:
            underlying: bytearray = buffer.obj
            buffer.release()
            if not isinstance(underlying, bytearray):
                underlying = bytearray(underlying)
            underlying.extend(bytearray(new_length - old_length))
            setattr(obj, self.name, memoryview(underlying))

        setattr(obj, self.length_name, new_length)

    def get_prefix_len(self, obj) -> int:
        return 4

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        length = 0
        if hasattr(obj, self.length_name):
            length = getattr(obj, self.length_name)
        struct.pack_into("I", buffer, offset.value, length)
        offset.value += 4

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray())]
        return [getattr(obj, self.name)]


class StringVectorProperty:
    def __init__(self, name: str):
        self.name = f"_{name}_data"
        self.lengths_name = f"_{name}_lengths"

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name) or not hasattr(obj, self.lengths_name):
            return []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        return [
            buffers[i].obj[: lengths[i]].decode("utf-8") for i in range(len(buffers))
        ]

    def __set__(self, obj, value: List[str]):
        if not all(isinstance(v, str) for v in value):
            raise ValueError("All elements must be of type str")

        buffers = []
        lengths = []
        if hasattr(obj, self.name):
            buffers = getattr(obj, self.name)
            lengths = getattr(obj, self.lengths_name)

        for i, val in enumerate(value):
            encoded = val.encode("utf-8")
            new_length = len(encoded)
            if i < len(buffers):
                old_buffer = buffers[i]
                if new_length > len(old_buffer):
                    underlying: bytearray = old_buffer.obj
                    old_buffer.release()
                    if not isinstance(underlying, bytearray):
                        underlying = bytearray(underlying)
                    underlying.extend(bytearray(new_length - len(old_buffer)))
                    buffers[i] = memoryview(underlying)
                buffers[i][:new_length] = encoded
                lengths[i] = new_length
            else:
                buffers.append(memoryview(bytearray(encoded)))
                lengths.append(new_length)
        buffers = buffers[: len(value)]
        setattr(obj, self.name, buffers)
        setattr(obj, self.lengths_name, lengths)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        new_length = struct.unpack_from("I", buffer, offset.value)[0]
        offset.value += 4

        old_buffers = None
        old_length = 0
        if hasattr(obj, self.name):
            old_buffers = getattr(obj, self.name)
            old_length = len(old_buffers)

        buffers = []
        lengths = []
        for i in range(new_length):
            str_size = struct.unpack_from("I", buffer, offset.value)[0]
            offset.value += 4
            if i < old_length and old_buffers is not None:
                old_buffer = old_buffers[i]
                if str_size > len(old_buffer):
                    underlying: bytearray = old_buffer.obj
                    old_buffer.release()
                    if not isinstance(underlying, bytearray):
                        underlying = bytearray(underlying)
                    underlying.extend(bytearray(str_size - len(old_buffer)))
                    buffers.append(memoryview(underlying))
                    lengths.append(str_size)
                else:
                    buffers.append(old_buffer)
                    lengths.append(str_size)
            else:
                buffers.append(memoryview(bytearray(str_size)))
                lengths.append(str_size)
        setattr(obj, self.name, buffers)
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
        struct.pack_into("I", buffer, offset.value, str_count)
        offset.value += 4
        if hasattr(obj, self.name):
            lengths = getattr(obj, self.lengths_name)
            for i in range(str_count):
                struct.pack_into("I", buffer, offset.value, lengths[i])
                offset.value += 4

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray())]

        # Return a segment for each string
        segments = []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            segments.append(buffers[i][: lengths[i]])
        return segments

    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        return len(getattr(obj, self.name))


class StringArrayProperty:
    def __init__(self, name: str, length: int):
        self.name = f"_{name}_data"
        self.lengths_name = f"_{name}_lengths"
        self.length = length

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        return [
            buffers[i].obj[: lengths[i]].decode("utf-8") for i in range(len(buffers))
        ]

    def __set__(self, obj, value: List[str]):
        if not isinstance(value, list):
            raise ValueError(f"Value must be of type list, got {type(value)}")
        if not all(isinstance(item, str) for item in value):
            raise ValueError("All elements must be of type str")
        if len(value) != self.length:
            raise ValueError(f"Array must be of length {self.length}, got {len(value)}")

        buffers = []
        lengths = []
        if hasattr(obj, self.name) and hasattr(obj, self.lengths_name):
            buffers = getattr(obj, self.name)
            lengths = getattr(obj, self.lengths_name)
        else:
            buffers = [memoryview(bytearray()) for _ in range(self.length)]
            lengths = [0 for _ in range(self.length)]

        for i, val in enumerate(value):
            encoded = val.encode("utf-8")
            new_length = len(encoded)
            old_buffer = buffers[i]
            if new_length > len(old_buffer):
                underlying: bytearray = old_buffer.obj
                old_buffer.release()
                if not isinstance(underlying, bytearray):
                    underlying = bytearray(underlying)
                underlying.extend(bytearray(new_length - len(underlying)))
                buffers[i] = memoryview(underlying)
            buffers[i][:new_length] = encoded
            lengths[i] = new_length

        setattr(obj, self.name, buffers)
        setattr(obj, self.lengths_name, lengths)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        old_buffers = None
        old_length = 0
        if hasattr(obj, self.name):
            old_buffers = getattr(obj, self.name)
            old_length = len(old_buffers)

        buffers = []
        lengths = []
        for i in range(self.length):
            str_size = struct.unpack_from("I", buffer, offset.value)[0]
            offset.value += 4
            if i < old_length and old_buffers is not None:
                old_buffer = old_buffers[i]
                if str_size > len(old_buffer):
                    underlying: bytearray = old_buffer.obj
                    old_buffer.release()
                    if not isinstance(underlying, bytearray):
                        underlying = bytearray(underlying)
                    underlying.extend(bytearray(str_size - len(underlying)))
                    buffers.append(memoryview(underlying))
                    lengths.append(str_size)
                else:
                    buffers.append(old_buffer)
                    lengths.append(str_size)
            else:
                buffers.append(memoryview(bytearray(str_size)))
                lengths.append(str_size)
        setattr(obj, self.name, buffers)
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
                struct.pack_into("I", buffer, offset.value, str_length)
                offset.value += 4

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray(0))]

        # Return a segment for each string
        segments = []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            segments.append(buffers[i][: lengths[i]])
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
        new_size = struct.unpack_from("I", buffer, offset.value)[0]
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
        struct.pack_into("I", buffer, offset.value, msg_count)
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

class PointerProperty:
    def __init__(self, name: str):
        self.name = f"_{name}_data"
        self.length_name = f"_{name}_length"

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            return None
        buffer = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return buffer[:length]

    def __set__(self, obj, value: Any):
        if not isinstance(value, memoryview):
            raise ValueError(f"Value must be of type memoryview, got {type(value)}")

        # If buffer does not exist, create it
        new_length: int = len(value)
        if not hasattr(obj, self.name):
            # Create new buffer
            setattr(obj, self.name, value)
            setattr(obj, self.length_name, new_length)
            return

        buffer: memoryview = getattr(obj, self.name)
        old_length: int = getattr(obj, self.length_name)
        if new_length > old_length:
            # Resize the buffer
            underlying: bytearray = buffer.obj
            buffer.release()
            if not isinstance(underlying, bytearray):
                underlying = bytearray(underlying)
            underlying.extend(bytearray(new_length - old_length))
            buffer = memoryview(underlying)
            setattr(obj, self.name, buffer)

        # Update buffer and length
        buffer[:new_length] = value
        setattr(obj, self.length_name, new_length)

    def resize(self, obj, buffer, offset) -> None:
        new_length = struct.unpack_from("I", buffer, offset.value)[0]
        offset.value += 4
        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            setattr(obj, self.name, memoryview(bytearray(new_length)))
            setattr(obj, self.length_name, new_length)
            return
        
        pointer = getattr(obj, self.name)
        old_length = len(pointer)
        if new_length > old_length:
            underlying: bytearray = pointer.obj
            pointer.release()
            if not isinstance(underlying, bytearray):
                underlying = bytearray(underlying)
            underlying.extend(bytearray(new_length - old_length))
            setattr(obj, self.name, memoryview(underlying))

        setattr(obj, self.length_name, new_length)

    def get_prefix_len(self, obj) -> int:
        return 4

    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        length = 0
        if hasattr(obj, self.length_name):
            length = getattr(obj, self.length_name)
        struct.pack_into("I", buffer, offset.value, length)
        offset.value += 4

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name) or not hasattr(obj, self.length_name):
            return [memoryview(bytearray())]
        buffer = getattr(obj, self.name)
        length = getattr(obj, self.length_name)
        return [buffer[:length]]

    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        return 1

class PointerVectorProperty:
    def __init__(self, name: str):
        self.name = f"_{name}_data"
        self.lengths_name = f"_{name}_lengths"

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name) or not hasattr(obj, self.lengths_name):
            return []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        return [buffers[i][: lengths[i]] for i in range(len(buffers))]
    
    def __set__(self, obj, value: List[memoryview]):
        if not all(isinstance(v, memoryview) for v in value):
            raise ValueError("All elements must be of type memoryview")

        buffers = []
        lengths = []
        if hasattr(obj, self.name):
            buffers = getattr(obj, self.name)
            lengths = getattr(obj, self.lengths_name)

        for i, val in enumerate(value):
            new_length = len(val)
            if i < len(buffers):
                old_buffer = buffers[i]
                if new_length > len(old_buffer):
                    underlying: bytearray = old_buffer.obj
                    old_buffer.release()
                    if not isinstance(underlying, bytearray):
                        underlying = bytearray(underlying)
                    underlying.extend(bytearray(new_length - len(underlying)))
                    buffers[i] = memoryview(underlying)
                buffers[i][:new_length] = val
                lengths[i] = new_length
            else:
                buffers.append(val)
                lengths.append(new_length)

        buffers = buffers[: len(value)]
        setattr(obj, self.name, buffers)
        setattr(obj, self.lengths_name, lengths)

    def resize(
        self, obj: object, buffer: bytearray, offset: Serializable.Offset
    ) -> None:
        new_length = struct.unpack_from("I", buffer, offset.value)[0]
        offset.value += 4

        old_buffers = None
        old_length = 0
        if hasattr(obj, self.name):
            old_buffers = getattr(obj, self.name)
            old_length = len(old_buffers)

        buffers = []
        lengths = []
        for i in range(new_length):
            ptr_size = struct.unpack_from("I", buffer, offset.value)[0]
            offset.value += 4
            if i < old_length and old_buffers is not None:
                old_buffer = old_buffers[i]
                if ptr_size > len(old_buffer):
                    underlying: bytearray = old_buffer.obj
                    old_buffer.release()
                    if not isinstance(underlying, bytearray):
                        underlying = bytearray(underlying)
                    underlying.extend(bytearray(ptr_size - len(underlying)))
                    buffers.append(memoryview(underlying))
                    lengths.append(ptr_size)
                else:
                    buffers.append(old_buffer)
                    lengths.append(ptr_size)
            else:
                buffers.append(memoryview(bytearray(ptr_size)))
                lengths.append(ptr_size)
        setattr(obj, self.name, buffers)
        setattr(obj, self.lengths_name, lengths)

    def get_prefix_len(self, obj) -> int:
        length = 4  # For the number of pointers
        if hasattr(obj, self.name):
            length += len(getattr(obj, self.name)) * 4  # Each pointer length is a uint32
        return length
    
    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        ptr_count = 0
        if hasattr(obj, self.name):
            ptr_count = len(getattr(obj, self.name))
        struct.pack_into("I", buffer, offset.value, ptr_count)
        offset.value += 4
        if hasattr(obj, self.name):
            lengths = getattr(obj, self.lengths_name)
            for i in range(ptr_count):
                struct.pack_into("I", buffer, offset.value, lengths[i])
                offset.value += 4
    
    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray())]

        # Return a segment for each pointer
        segments = []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            segments.append(buffers[i][: lengths[i]])
        return segments
    
    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        return len(getattr(obj, self.name))
    
class PointerArrayProperty:
    def __init__(self, name: str, length: int):
        self.name = f"_{name}_data"
        self.lengths_name = f"_{name}_lengths"
        self.length = length

    def __get__(self, obj, objtype=None):
        if not hasattr(obj, self.name):
            return []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        return [buffers[i][: lengths[i]] for i in range(len(buffers))]

    def __set__(self, obj, value: List[memoryview]):
        if not isinstance(value, list):
            raise ValueError(f"Value must be of type list, got {type(value)}")
        if not all(isinstance(item, memoryview) for item in value):
            raise ValueError("All elements must be of type memoryview")
        if len(value) != self.length:
            raise ValueError(f"Array must be of length {self.length}, got {len(value)}")

        buffers = []
        lengths = []
        if hasattr(obj, self.name) and hasattr(obj, self.lengths_name):
            buffers = getattr(obj, self.name)
            lengths = getattr(obj, self.lengths_name)
        else:
            buffers = [memoryview(bytearray()) for _ in range(self.length)]
            lengths = [0 for _ in range(self.length)]

        for i, val in enumerate(value):
            new_length = len(val)
            old_buffer = buffers[i]
            if new_length > len(old_buffer):
                underlying: bytearray = old_buffer.obj
                old_buffer.release()
                if not isinstance(underlying, bytearray):
                    underlying = bytearray(underlying)
                underlying.extend(bytearray(new_length - len(underlying)))
                buffers[i] = memoryview(underlying)
            buffers[i][:new_length] = val
            lengths[i] = new_length

        setattr(obj, self.name, buffers)
        setattr(obj, self.lengths_name, lengths)
    
    def resize(self, obj: object, buffer: bytearray, offset: Serializable.Offset) -> None:
        old_buffers = None
        old_length = 0
        if hasattr(obj, self.name):
            old_buffers = getattr(obj, self.name)
            old_length = len(old_buffers)

        buffers = []
        lengths = []
        for i in range(self.length):
            ptr_size = struct.unpack_from("I", buffer, offset.value)[0]
            offset.value += 4
            if i < old_length and old_buffers is not None:
                old_buffer = old_buffers[i]
                if ptr_size > len(old_buffer):
                    underlying: bytearray = old_buffer.obj
                    old_buffer.release()
                    if not isinstance(underlying, bytearray):
                        underlying = bytearray(underlying)
                    underlying.extend(bytearray(ptr_size - len(old_buffer)))
                    buffers.append(memoryview(underlying))
                    lengths.append(ptr_size)
                else:
                    buffers.append(old_buffer)
                    lengths.append(ptr_size)
            else:
                buffers.append(memoryview(bytearray(ptr_size)))
                lengths.append(ptr_size)
        setattr(obj, self.name, buffers)
        setattr(obj, self.lengths_name, lengths)

    def get_prefix_len(self, obj) -> int:
        length = 0
        if hasattr(obj, self.name):
            length += len(getattr(obj, self.name)) * 4  # Each pointer length is a uint32
        return length
    
    def get_prefix(self, obj, buffer: bytearray, offset: Serializable.Offset) -> None:
        if not hasattr(obj, self.name):
            return
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            str_length = lengths[i]
            struct.pack_into("I", buffer, offset.value, str_length)
            offset.value += 4

    def get_segments(self, obj) -> List[memoryview]:
        if not hasattr(obj, self.name):
            return [memoryview(bytearray(0))]

        # Return a segment for each pointer
        segments = []
        buffers = getattr(obj, self.name)
        lengths = getattr(obj, self.lengths_name)
        for i in range(len(lengths)):
            segments.append(buffers[i][: lengths[i]])
        return segments
    
    def get_segment_count(self, obj) -> int:
        if not hasattr(obj, self.name):
            return 0
        ptr_count = len(getattr(obj, self.name))
        return ptr_count

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
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "?"))


def init_char(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "c"))


def init_int8(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "b"))


def init_uint8(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "B"))


def init_int16(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "h"))


def init_uint16(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "H"))


def init_int32(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "i"))


def init_uint32(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "I"))


def init_int64(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "q"))


def init_uint64(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "Q"))


def init_float(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "f"))


def init_double(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, ArithmeticProperty(property_name, "d"))


def init_bool_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "?"),
    )


def init_char_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "c"),
    )


def init_int8_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "b"),
    )


def init_uint8_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "B"),
    )


def init_int16_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "h"),
    )


def init_uint16_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "H"),
    )


def init_int32_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "i"),
    )


def init_uint32_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "I"),
    )


def init_int64_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "q"),
    )


def init_uint64_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "Q"),
    )


def init_float_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "f"),
    )


def init_double_vector(obj: object, property_name: str) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticVectorProperty(property_name, "d"),
    )


def init_bool_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "?", length),
    )


def init_char_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "c", length),
    )


def init_int8_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "b", length),
    )


def init_uint8_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "B", length),
    )


def init_int16_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "h", length),
    )


def init_uint16_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "H", length),
    )


def init_int32_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "i", length),
    )


def init_uint32_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "I", length),
    )


def init_int64_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "q", length),
    )


def init_uint64_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "Q", length),
    )


def init_float_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "f", length),
    )


def init_double_array(obj: object, property_name: str, length: int) -> None:
    setattr(
        obj.__class__,
        property_name,
        ArithmeticArrayProperty(property_name, "d", length),
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


def init_pointer(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, PointerProperty(property_name))


def init_pointer_vector(obj: object, property_name: str) -> None:
    setattr(obj.__class__, property_name, PointerVectorProperty(property_name))


def init_pointer_array(obj: object, property_name: str, length: int) -> None:
    setattr(obj.__class__, property_name, PointerArrayProperty(property_name, length))


def resize(obj: object, name: str, buffer: bytes, offset: Serializable.Offset) -> None:
    type(obj).__dict__[name].resize(obj, buffer, offset)


def get_prefix_len(obj, name) -> int:
    return type(obj).__dict__[name].get_prefix_len(obj)


def get_prefix(obj, name, buffer: bytearray, offset: Serializable.Offset) -> None:
    type(obj).__dict__[name].get_prefix(obj, buffer, offset)


def get_segment_count(obj, name) -> int:
    return type(obj).__dict__[name].get_segment_count(obj)
