import ctypes
from abc import ABC, abstractmethod
from typing import List, Tuple, Any


class Serializable(ABC):
    class Offset:
        def __init__(self):
            self.value = 0

    @abstractmethod
    def size(self) -> int:
        """
        Get the total size of the serialized object in bytes.

        Returns:
            Size in bytes
        """
        pass

    @abstractmethod
    def serialize(self) -> bytes:
        """
        Serialize the object to a bytes object.

        Returns:
            Serialized bytes
        """
        pass

    @abstractmethod
    def deserialize(self, data: bytes, offset: Offset) -> bool:
        """
        Deserialize the object from a bytes object.

        Args:
            data: Serialized bytes

        Returns:
            True if deserialization was successful, False otherwise
        """
        pass


class Message(Serializable):
    """Abstract base class for messages with zero-copy serialization support."""

    def set_raw(self, property_name: str, buffer: bytes, length: int) -> None:
        """Set the raw ctypes data for a property."""
        prop_descriptor = type(self).__dict__.get(property_name)
        if prop_descriptor is None:
            raise AttributeError(f"Property '{property_name}' not found")
        if hasattr(prop_descriptor, "set_raw"):
            prop_descriptor.set_raw(self, buffer, length)
            return
        internal_name = f"_{property_name}_data"
        array_type = (ctypes.c_uint8 * length)
        array = array_type.from_buffer_copy(buffer)
        setattr(self, internal_name, array)

    def get_raw(self, property_name: str) -> Any:
        """Get the raw ctypes data for a property."""
        prop_descriptor = type(self).__dict__.get(property_name)
        if prop_descriptor is None:
            raise AttributeError(f"Property '{property_name}' not found")
        if hasattr(prop_descriptor, "get_raw"):
            return prop_descriptor.get_raw(self)
        internal_name = f"_{property_name}_data"
        if hasattr(self, internal_name):
            return getattr(self, internal_name)
        return None

    @abstractmethod
    def hash(self) -> List[int]:
        """
        Get the hash of the message type.

        Returns:
            List of two 64-bit integers representing the hash
        """
        pass

    @abstractmethod
    def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
        """
        Resize dynamic fields based on the size prefix.

        Args:
            sizes: Buffer containing size information (serialized vector of uint32)
            length: Length of the sizes buffer
            offset: Current offset in the buffer

        Returns:
            True if resize was successful, False otherwise
        """
        pass

    @abstractmethod
    def get_prefix_len(self) -> int:
        """
        Get the length of the size prefix in bytes.

        Returns:
            Length of the prefix
        """
        pass

    @abstractmethod
    def get_prefix(self, buffer: bytearray, offset: Serializable.Offset) -> None:
        """
        Write the size prefix to a buffer.

        Args:
            buffer: Destination buffer for size information (serialized vector of uint32)
            offset: Current offset in the buffer
        """
        pass

    def get_prefix_bytes(self) -> bytes:
        """
        Get the size prefix as bytes.

        Returns:
            Size prefix as bytes
        """
        prefix_len = self.get_prefix_len()
        buffer = bytearray(prefix_len)
        offset = Serializable.Offset()
        self.get_prefix(buffer, offset)
        return bytes(buffer)

    @abstractmethod
    def get_segment_count(self) -> int:
        """
        Get the number of memory segments in this message.

        Returns:
            Number of segments
        """
        pass

    @abstractmethod
    def get_segments(self) -> List[memoryview]:
        pass

    def size(self) -> int:
        msg_size = self.get_prefix_len()
        segments = self.get_segments()
        for seg in segments:
            msg_size += len(seg)
        return msg_size

    def serialize(self) -> bytes:
        total_size = self.size()
        buffer = bytearray(total_size)
        offset = Serializable.Offset()

        # Write prefix
        self.get_prefix(buffer, offset)

        # Write segments
        segments = self.get_segments()
        for seg in segments:
            seg_length = len(seg)
            buffer[offset.value : offset.value + seg_length] = seg
            offset.value += seg_length

        return bytes(buffer)

    def deserialize(self, data: bytes, offset: Serializable.Offset) -> bool:
        # Resize dynamic fields first
        if not self.resize(data, len(data), offset):
            return False

        # Read segments
        segments = self.get_segments()
        for seg in segments:
            seg_length = len(seg)
            seg[:] = data[offset.value : offset.value + seg_length]
            offset.value += seg_length
        return True
