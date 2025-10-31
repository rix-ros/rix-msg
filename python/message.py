import struct
import abc
from collections.abc import Callable, Sequence
from typing import TypeVar

T = TypeVar("T", bound="Message")

class Message(abc.ABC):

    class Offset:
        def __init__(self, value: int = 0):
            self.value = value

    @abc.abstractmethod
    def serialize(self, buffer: bytearray) -> None:
        pass

    @abc.abstractmethod
    def deserialize(self, buffer: bytearray, offset: Offset) -> None:
        pass

    @abc.abstractmethod
    def size(self) -> int:
        pass

    @abc.abstractmethod
    def hash(self) -> list[int]:
        pass

    @staticmethod
    def _serialize_int8(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("b", value))

    @staticmethod
    def _serialize_int8_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        Message._serialize_uint32(len(value), buffer)
        if type(value) is bytearray:
            buffer.extend(value)
        else:
            buffer.extend(struct.pack(f"{len(value)}b", *value))

    @staticmethod
    def _serialize_int8_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size:
                value.extend(b"\x00" * (size - len(value)))
            buffer.extend(value)
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{size}b", *value))

    @staticmethod
    def _serialize_char(
        value: int | str,
        buffer: bytearray,
    ) -> None:
        if type(value) is str:
            Message._serialize_int8(ord(value[0]), buffer)
        elif type(value) is int:
            Message._serialize_int8(value, buffer)

    @staticmethod
    def _serialize_char_vector(
        value: str | list[int] | list[str] | bytearray,
        buffer: bytearray,
    ) -> None:
        print(type(value))
        if type(value) is str:
            Message._serialize_string(value, buffer)
        elif type(value) is bytearray or type(value) is list[int]:
            Message._serialize_int8_vector(value, buffer)
        elif type(value) is list:
            Message._serialize_int8_vector([ord(c) for c in value], buffer)

    @staticmethod
    def _serialize_char_array(
        value: str | list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is str:
            if len(value) < size:
                value = value.ljust(size, "\x00")
            buffer.extend(value[:size].encode())
        elif type(value) is bytearray or type(value) is list[int]:
            if len(value) < size:
                if type(value) is bytearray:
                    value.extend(b"\x00" * (size - len(value)))
                else:
                    value.extend([0] * (size - len(value)))
            Message._serialize_int8_array(value, buffer, size)

    @staticmethod
    def _serialize_uint8(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("B", value))

    @staticmethod
    def _serialize_uint8_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        Message._serialize_uint32(len(value), buffer)
        if type(value) is bytearray:
            buffer.extend(value)
        else:
            buffer.extend(struct.pack(f"{len(value)}B", *value))

    @staticmethod
    def _serialize_uint8_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size:
                value.extend(b"\x00" * (size - len(value)))
            buffer.extend(value[:size])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{size}B", *value[:size]))

    @staticmethod
    def _serialize_bool(
        value: bool,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("?", value))

    @staticmethod
    def _serialize_bool_vector(
        value: list[bool] | bytearray,
        buffer: bytearray,
    ) -> None:
        Message._serialize_uint32(len(value), buffer)
        if type(value) is bytearray:
            buffer.extend(value)
        else:
            buffer.extend(struct.pack(f"{len(value)}?", *value))

    @staticmethod
    def _serialize_bool_array(
        value: list[bool] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size:
                value.extend(b"\x00" * (size - len(value)))
            buffer.extend(value[:size])
        else:
            if len(value) < size:
                value.extend([False] * (size - len(value)))
            buffer.extend(struct.pack(f"{size}?", *value[:size]))

    @staticmethod
    def _serialize_int16(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("h", value))

    @staticmethod
    def _serialize_int16_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 2, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}h", *value))

    @staticmethod
    def _serialize_int16_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 2:
                value.extend(b"\x00" * (size * 2 - len(value)))
            buffer.extend(value[: size * 2])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}h", *value))

    @staticmethod
    def _serialize_uint16(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("H", value))

    @staticmethod
    def _serialize_uint16_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 2, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}H", *value))

    @staticmethod
    def _serialize_uint16_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 2:
                value.extend(b"\x00" * (size * 2 - len(value)))
            buffer.extend(value[: size * 2])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}H", *value))

    @staticmethod
    def _serialize_int32(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("i", value))

    @staticmethod
    def _serialize_int32_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 4, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}i", *value))

    @staticmethod
    def _serialize_int32_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 4:
                value.extend(b"\x00" * (size * 4 - len(value)))
            buffer.extend(value[: size * 4])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}i", *value))

    @staticmethod
    def _serialize_uint32(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("I", value))

    @staticmethod
    def _serialize_uint32_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 4, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}I", *value))

    @staticmethod
    def _serialize_uint32_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 4:
                value.extend(b"\x00" * (size * 4 - len(value)))
            buffer.extend(value[: size * 4])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}I", *value))

    @staticmethod
    def _serialize_int64(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("q", value))

    @staticmethod
    def _serialize_int64_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 8, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}q", *value))

    @staticmethod
    def _serialize_int64_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 8:
                value.extend(b"\x00" * (size * 8 - len(value)))
            buffer.extend(value[: size * 8])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}q", *value))

    @staticmethod
    def _serialize_uint64(
        value: int,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("Q", value))

    @staticmethod
    def _serialize_uint64_vector(
        value: list[int] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 8, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}Q", *value))

    @staticmethod
    def _serialize_uint64_array(
        value: list[int] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 8:
                value.extend(b"\x00" * (size * 8 - len(value)))
            buffer.extend(value[: size * 8])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}Q", *value))

    @staticmethod
    def _serialize_float(
        value: float,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("f", value))

    @staticmethod
    def _serialize_float_vector(
        value: list[float] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 4, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}f", *value))

    @staticmethod
    def _serialize_float_array(
        value: list[float] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 4:
                value.extend(b"\x00" * (size * 4 - len(value)))
            buffer.extend(value[: size * 4])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}f", *value))

    @staticmethod
    def _serialize_double(
        value: float,
        buffer: bytearray,
    ) -> None:
        buffer.extend(struct.pack("d", value))

    @staticmethod
    def _serialize_double_vector(
        value: list[float] | bytearray,
        buffer: bytearray,
    ) -> None:
        if type(value) is bytearray:
            Message._serialize_uint32(len(value) // 8, buffer)
            buffer.extend(value)
        else:
            Message._serialize_uint32(len(value), buffer)
            buffer.extend(struct.pack(f"{len(value)}d", *value))

    @staticmethod
    def _serialize_double_array(
        value: list[float] | bytearray,
        buffer: bytearray,
        size: int,
    ) -> None:
        if type(value) is bytearray:
            if len(value) < size * 8:
                value.extend(b"\x00" * (size * 8 - len(value)))
            buffer.extend(value[: size * 8])
        else:
            if len(value) < size:
                value.extend([0] * (size - len(value)))
            buffer.extend(struct.pack(f"{len(value)}d", *value))

    @staticmethod
    def _serialize_string(
        value: str,
        buffer: bytearray,
    ) -> None:
        Message._serialize_uint32(len(value), buffer)
        # buffer.extend(struct.pack(f"{size}s", value.encode()))
        buffer.extend(value.encode())

    @staticmethod
    def _serialize_string_vector(
        value: list[str],
        buffer: bytearray,
    ) -> None:
        Message._serialize_uint32(len(value), buffer)
        for item in value:
            Message._serialize_string(item, buffer)

    @staticmethod
    def _serialize_string_array(
        value: list[str],
        buffer: bytearray,
        size: int,
    ) -> None:
        if len(value) < size:
            value.extend([""] * (size - len(value)))
        for item in value[:size]:
            Message._serialize_string(item, buffer)

    @staticmethod
    def _serialize_message(
        value: "Message",
        buffer: bytearray,
    ) -> None:
        value.serialize(buffer)

    @staticmethod
    def _serialize_message_vector(
        value: Sequence["Message"],
        buffer: bytearray,
    ) -> None:
        Message._serialize_uint32(len(value), buffer)
        for item in value:
            item.serialize(buffer)

    @staticmethod
    def _serialize_message_array(
        value: Sequence["Message"],
        buffer: bytearray,
        size: int,
    ) -> None:
        if len(value) < size:
            # We do not have access to the message type here to create empty messages, so we raise an error
            raise ValueError("Error: Not enough elements in message array")
        for item in value[:size]:
            item.serialize(buffer)

    @staticmethod
    def _serialize_map(
        value: dict[str, int],
        buffer: bytearray,
        key_func: Callable[
            [Sequence[int | float | str | T], bytearray], None
        ],
        value_func: Callable[
            [Sequence[int | float | str | T], bytearray], None
        ],
    ) -> None:
        """
        Serialize a map to the buffer. The key_func and value_func are functions
        that serialize the key and value types respectively.
        """
        key_func(list(value.keys()), buffer)
        value_func(list(value.values()), buffer)

    @staticmethod
    def _deserialize_int8(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("b", buffer, offset.value)[0]
        offset.value += 1
        return value

    @staticmethod
    def _deserialize_int8_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}b", buffer, offset.value)
        offset.value += size
        return list(value)

    @staticmethod
    def _deserialize_int8_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}b", buffer, offset.value)
        offset.value += size
        return list(value)

    @staticmethod
    def _deserialize_uint8(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("B", buffer, offset.value)[0]
        offset.value += 1
        return value

    @staticmethod
    def _deserialize_uint8_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> bytearray:
        size = Message._deserialize_uint32(buffer, offset)
        value = buffer[offset.value : offset.value + size]
        offset.value += size
        return value

    @staticmethod
    def _deserialize_uint8_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> bytearray:
        value = buffer[offset.value : offset.value + size]
        offset.value += size
        return value

    @staticmethod
    def _deserialize_char(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("c", buffer, offset.value)[0]
        offset.value += 1
        return value

    @staticmethod
    def _deserialize_char_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> str:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}c", buffer, offset.value)
        offset.value += size
        return b"".join(value).decode()

    @staticmethod
    def _deserialize_char_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}c", buffer, offset.value)
        offset.value += size
        return list(value)

    @staticmethod
    def _deserialize_bool(
        buffer: bytearray,
        offset: Offset,
    ) -> bool:
        value = struct.unpack_from("?", buffer, offset.value)[0]
        offset.value += 1
        return value

    @staticmethod
    def _deserialize_bool_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[bool]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}?", buffer, offset.value)
        offset.value += size
        return [bool(v) for v in value]

    @staticmethod
    def _deserialize_bool_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[bool]:
        value = struct.unpack_from(f"{size}?", buffer, offset.value)
        offset.value += size
        return [bool(v) for v in value]

    @staticmethod
    def _deserialize_int16(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("h", buffer, offset.value)[0]
        offset.value += 2
        return value

    @staticmethod
    def _deserialize_int16_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}h", buffer, offset.value)
        offset.value += size * 2
        return list(value)

    @staticmethod
    def _deserialize_int16_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}h", buffer, offset.value)
        offset.value += size * 2
        return list(value)

    @staticmethod
    def _deserialize_uint16(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("H", buffer, offset.value)[0]
        offset.value += 2
        return value

    @staticmethod
    def _deserialize_uint16_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}H", buffer, offset.value)
        offset.value += size * 2
        return list(value)

    @staticmethod
    def _deserialize_uint16_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}H", buffer, offset.value)
        offset.value += size * 2
        return list(value)

    @staticmethod
    def _deserialize_int32(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("i", buffer, offset.value)[0]
        offset.value += 4
        return value

    @staticmethod
    def _deserialize_int32_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}i", buffer, offset.value)
        offset.value += size * 4
        return list(value)

    @staticmethod
    def _deserialize_int32_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}i", buffer, offset.value)
        offset.value += size * 4
        return list(value)

    @staticmethod
    def _deserialize_uint32(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("I", buffer, offset.value)[0]
        offset.value += 4
        return value

    @staticmethod
    def _deserialize_uint32_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}I", buffer, offset.value)
        offset.value += size * 4
        return list(value)

    @staticmethod
    def _deserialize_uint32_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}I", buffer, offset.value)
        offset.value += size * 4
        return list(value)

    @staticmethod
    def _deserialize_int64(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("q", buffer, offset.value)[0]
        offset.value += 8
        return value

    @staticmethod
    def _deserialize_int64_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}q", buffer, offset.value)
        offset.value += size * 8
        return list(value)

    @staticmethod
    def _deserialize_int64_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}q", buffer, offset.value)
        offset.value += size * 8
        return list(value)

    @staticmethod
    def _deserialize_uint64(
        buffer: bytearray,
        offset: Offset,
    ) -> int:
        value = struct.unpack_from("Q", buffer, offset.value)[0]
        offset.value += 8
        return value

    @staticmethod
    def _deserialize_uint64_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[int]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}Q", buffer, offset.value)
        offset.value += size * 8
        return list(value)

    @staticmethod
    def _deserialize_uint64_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[int]:
        value = struct.unpack_from(f"{size}Q", buffer, offset.value)
        offset.value += size * 8
        return list(value)

    @staticmethod
    def _deserialize_float(
        buffer: bytearray,
        offset: Offset,
    ) -> float:
        value = struct.unpack_from("f", buffer, offset.value)[0]
        offset.value += 4
        return value

    @staticmethod
    def _deserialize_float_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[float]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}f", buffer, offset.value)
        offset.value += size * 4
        return list(value)

    @staticmethod
    def _deserialize_float_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[float]:
        value = struct.unpack_from(f"{size}f", buffer, offset.value)
        offset.value += size * 4
        return list(value)

    @staticmethod
    def _deserialize_double(
        buffer: bytearray,
        offset: Offset,
    ) -> float:
        value = struct.unpack_from("d", buffer, offset.value)[0]
        offset.value += 8
        return value

    @staticmethod
    def _deserialize_double_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[float]:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}d", buffer, offset.value)
        offset.value += size * 8
        return list(value)

    @staticmethod
    def _deserialize_double_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[float]:
        value = struct.unpack_from(f"{size}d", buffer, offset.value)
        offset.value += size * 8
        return list(value)

    @staticmethod
    def _deserialize_string(
        buffer: bytearray,
        offset: Offset,
    ) -> str:
        size = Message._deserialize_uint32(buffer, offset)
        value = struct.unpack_from(f"{size}s", buffer, offset.value)[0]
        offset.value += size
        return value.decode()

    @staticmethod
    def _deserialize_string_vector(
        buffer: bytearray,
        offset: Offset,
    ) -> list[str]:
        size = Message._deserialize_uint32(buffer, offset)
        value: list[str] = []
        for _ in range(size):
            value.append(Message._deserialize_string(buffer, offset))
        return value

    @staticmethod
    def _deserialize_string_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
    ) -> list[str]:
        value: list[str] = []
        for _ in range(size):
            value.append(Message._deserialize_string(buffer, offset))
        return value

    @staticmethod
    def _deserialize_message(
        buffer: bytearray,
        offset: Offset,
        message: Callable[[], T],
    ) -> T:
        msg = message()
        msg.deserialize(buffer, offset)
        return msg

    @staticmethod
    def _deserialize_message_vector(
        buffer: bytearray,
        offset: Offset,
        message: Callable[[], T],
    ) -> list[T]:
        size = Message._deserialize_uint32(buffer, offset)
        value: list[T] = []
        for _ in range(size):
            msg = message()
            msg.deserialize(buffer, offset)
            value.append(msg)
        return value

    @staticmethod
    def _deserialize_message_array(
        buffer: bytearray,
        offset: Offset,
        size: int,
        message: Callable[[], T],
    ) -> list[T]:
        value: list[T] = []
        for _ in range(size):
            msg = message()
            msg.deserialize(buffer, offset)
            value.append(msg)
        return value

    @staticmethod
    def _deserialize_map(
        buffer: bytearray,
        offset: Offset,
        key_func: Callable[
            [bytearray, Offset],
            Sequence[int | float | str] | bytearray,
        ],
        value_func: Callable[
            [bytearray, Offset, None | Callable[[], "Message"]],
            Sequence[int | float | str | T] | bytearray,
        ],
        message: None | Callable[[], "Message"] = None,
    ) -> dict[int | float | str, int | float | str | T]:
        """
        Deserialize a map from the buffer. The key_func and value_func are functions
        that deserialize vectors of the key and value types respectively.
        Valid key types include:
        - int8, uint8, char, bool, int16, uint16, int32, uint32, int64, uint64, float, double, string
        Valid value types include:
        - int8, uint8, char, bool, int16, uint16, int32, uint32, int64, uint64, float, double, string, Message
        """
        keys = key_func(buffer, offset)
        if message is None:
            values = value_func(buffer, offset)
        else:
            values = value_func(buffer, offset, message)
        if type(keys) is bytearray:
            keys = list(keys)
        if type(values) is bytearray:
            values = list(values)
        return dict(zip(keys, values))

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
    def _size_float() -> int:
        return 4

    @staticmethod
    def _size_double() -> int:
        return 8

    @staticmethod
    def _size_string(value: str) -> int:
        return 4 + len(value)

    @staticmethod
    def _size_message(value: "Message") -> int:
        return value.size()

    @staticmethod
    def _size_vector_number(value: Sequence[int | float], size: int) -> int:
        return 4 + len(value) * size

    @staticmethod
    def _size_vector_string(value: list[str]) -> int:
        return 4 + sum(Message._size_string(item) for item in value)

    @staticmethod
    def _size_vector_message(value: Sequence["Message"]) -> int:
        return 4 + sum(item.size() for item in value)

    @staticmethod
    def _size_array_number(value: Sequence[int | float], size: int) -> int:
        return len(value) * size

    @staticmethod
    def _size_array_string(value: list[str], size: int) -> int:
        # return sum(len(item) for item in value)
        return sum(Message._size_string(item) for item in value[:size])

    @staticmethod
    def _size_array_message(value: Sequence["Message"], size: int) -> int:
        return sum(Message._size_message(item) for item in value[:size])

    @staticmethod
    def _size_map_number_to_number(
        value: dict[str, int], key_size: int, value_size: int
    ) -> int:
        return 8 + len(value) * (key_size + value_size)

    @staticmethod
    def _size_map_number_to_string(value: dict[int | float, str], key_size: int) -> int:
        return (
            8
            + len(value) * key_size
            + sum(Message._size_string(item) for item in value.values())
        )

    @staticmethod
    def _size_map_number_to_message(value: dict[int | float, "Message"], key_size: int) -> int:
        return (
            8
            + len(value) * key_size
            + sum(Message._size_message(item) for item in value.values())
        )

    @staticmethod
    def _size_map_string_to_number(value: dict[str, int | float], value_size: int) -> int:
        return (
            8
            + sum(Message._size_string(item) for item in value.keys())
            + len(value) * value_size
        )

    @staticmethod
    def _size_map_string_to_string(value: dict[str, str]) -> int:
        return 8 + sum(
            Message._size_string(k) + Message._size_string(v) for k, v in value.items()
        )

    @staticmethod
    def _size_map_string_to_message(value: dict[str, "Message"]) -> int:
        return 8 + sum(
            Message._size_string(k) + Message._size_message(v) for k, v in value.items()
        )
