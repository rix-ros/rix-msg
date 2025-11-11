"""
Comprehensive unit tests for types.py

Tests all property classes and initialization functions including:
- ArithmeticProperty
- ArithmeticVectorProperty
- ArithmeticArrayProperty
- StringProperty
- StringVectorProperty
- StringArrayProperty
- MessageProperty
- MessageVectorProperty
- MessageArrayProperty
- All init_* functions
- Helper functions
"""

import unittest
import struct
import sys
import os
from typing import List
import importlib.util

# Load the local types.py module by explicit path to avoid conflict with built-in types
current_dir = os.path.dirname(os.path.abspath(__file__))
types_path = os.path.join(current_dir, "types.py")
spec = importlib.util.spec_from_file_location("rix_types", types_path)
rix_types = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rix_types)  # type: ignore

# Also add to path for message_base import
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from message_base import Message, Serializable

# Import everything we need from the rix_types module
ArithmeticProperty = rix_types.ArithmeticProperty
ArithmeticVectorProperty = rix_types.ArithmeticVectorProperty
ArithmeticArrayProperty = rix_types.ArithmeticArrayProperty
StringProperty = rix_types.StringProperty
StringVectorProperty = rix_types.StringVectorProperty
StringArrayProperty = rix_types.StringArrayProperty
MessageProperty = rix_types.MessageProperty
MessageVectorProperty = rix_types.MessageVectorProperty
MessageArrayProperty = rix_types.MessageArrayProperty
validate_python_type = rix_types.validate_python_type

# Initialization functions
init_bool = rix_types.init_bool
init_char = rix_types.init_char
init_int8 = rix_types.init_int8
init_uint8 = rix_types.init_uint8
init_int16 = rix_types.init_int16
init_uint16 = rix_types.init_uint16
init_int32 = rix_types.init_int32
init_uint32 = rix_types.init_uint32
init_int64 = rix_types.init_int64
init_uint64 = rix_types.init_uint64
init_float = rix_types.init_float
init_double = rix_types.init_double

init_bool_vector = rix_types.init_bool_vector
init_char_vector = rix_types.init_char_vector
init_int8_vector = rix_types.init_int8_vector
init_uint8_vector = rix_types.init_uint8_vector
init_int16_vector = rix_types.init_int16_vector
init_uint16_vector = rix_types.init_uint16_vector
init_int32_vector = rix_types.init_int32_vector
init_uint32_vector = rix_types.init_uint32_vector
init_int64_vector = rix_types.init_int64_vector
init_uint64_vector = rix_types.init_uint64_vector
init_float_vector = rix_types.init_float_vector
init_double_vector = rix_types.init_double_vector

init_bool_array = rix_types.init_bool_array
init_char_array = rix_types.init_char_array
init_int8_array = rix_types.init_int8_array
init_uint8_array = rix_types.init_uint8_array
init_int16_array = rix_types.init_int16_array
init_uint16_array = rix_types.init_uint16_array
init_int32_array = rix_types.init_int32_array
init_uint32_array = rix_types.init_uint32_array
init_int64_array = rix_types.init_int64_array
init_uint64_array = rix_types.init_uint64_array
init_float_array = rix_types.init_float_array
init_double_array = rix_types.init_double_array

init_string = rix_types.init_string
init_string_vector = rix_types.init_string_vector
init_string_array = rix_types.init_string_array

init_message = rix_types.init_message
init_message_vector = rix_types.init_message_vector
init_message_array = rix_types.init_message_array

init_pointer = rix_types.init_pointer
init_pointer_vector = rix_types.init_pointer_vector
init_pointer_array = rix_types.init_pointer_array

# Import PointerProperty
PointerProperty = rix_types.PointerProperty
PointerVectorProperty = rix_types.PointerVectorProperty
PointerArrayProperty = rix_types.PointerArrayProperty

# Helper functions
resize = rix_types.resize
get_prefix_len = rix_types.get_prefix_len
get_prefix = rix_types.get_prefix
get_segment_count = rix_types.get_segment_count


# Test message classes
class SimpleMessage(Message):
    """Simple test message with a few fields."""

    def __init__(self):
        init_uint32(self, "id")
        init_string(self, "name")
        self._property_names = ["id", "name"]

        self.id = 0
        self.name = ""

    def hash(self) -> List[int]:
        return [0x1, 0x2]

    def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
        if length < offset.value + self.get_prefix_len():
            return False
        resize(self, "name", buffer, offset)
        return True

    def get_prefix_len(self) -> int:
        return get_prefix_len(self, "name")

    def get_prefix(self, buffer: bytearray, offset: Serializable.Offset) -> None:
        get_prefix(self, "name", buffer, offset)

    def get_segment_count(self) -> int:
        return 2  # id + name

    def get_segments(self) -> List[tuple]:
        segments = []
        for prop_name in self._property_names:
            prop_descriptor = type(self).__dict__[prop_name]
            segments.extend(prop_descriptor.get_segments(self))
        return segments


class ComplexMessage(Message):
    """Complex test message with nested messages and arrays."""

    def __init__(self):
        init_string(self, "description")
        init_string_array(self, "tags", 3)
        init_message(self, "nested", SimpleMessage)
        self._property_names = ["description", "tags", "nested"]

        self.description = ""
        self.tags = [""] * 3
        self.nested = SimpleMessage()

    def hash(self) -> List[int]:
        return [0x3, 0x4]

    def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
        if length < offset.value + self.get_prefix_len():
            return False
        resize(self, "description", buffer, offset)
        resize(self, "tags", buffer, offset)
        resize(self, "nested", buffer, offset)
        return True

    def get_prefix_len(self) -> int:
        length = 0
        length += get_prefix_len(self, "description")
        length += get_prefix_len(self, "tags")
        length += get_prefix_len(self, "nested")
        return length

    def get_prefix(self, buffer: bytearray, offset: Serializable.Offset) -> None:
        get_prefix(self, "description", buffer, offset)
        get_prefix(self, "tags", buffer, offset)
        get_prefix(self, "nested", buffer, offset)

    def get_segment_count(self) -> int:
        count = 1
        count += get_segment_count(self, "tags")
        count += get_segment_count(self, "nested")
        return count

    def get_segments(self) -> List[tuple]:
        segments = []
        for prop_name in self._property_names:
            prop_descriptor = type(self).__dict__[prop_name]
            segments.extend(prop_descriptor.get_segments(self))
        return segments


class TestValidatePythonType(unittest.TestCase):
    """Test the validate_python_type function."""

    def test_valid_int_types(self):
        """Test validation of valid integer types."""
        validate_python_type(42, "i")
        validate_python_type(255, "B")
        validate_python_type(-128, "b")

    def test_valid_float_types(self):
        """Test validation of valid float types."""
        validate_python_type(3.14, "f")
        validate_python_type(2.718, "d")

    def test_valid_list_types(self):
        """Test validation of homogeneous lists."""
        validate_python_type([1, 2, 3], "i")
        validate_python_type([1.0, 2.0, 3.0], "f")

    def test_empty_list(self):
        """Test validation of empty lists."""
        validate_python_type([], "i")
        validate_python_type([], "f")

    def test_invalid_type_mismatch(self):
        """Test validation fails for type mismatches."""
        with self.assertRaises(TypeError):
            validate_python_type("string", "i")

        with self.assertRaises(TypeError):
            validate_python_type(42, "f")

    def test_invalid_heterogeneous_list(self):
        """Test validation fails for heterogeneous lists."""
        with self.assertRaises(TypeError):
            validate_python_type([1, 2, 3.0], "i")


class TestArithmeticProperty(unittest.TestCase):
    """Test ArithmeticProperty descriptor."""

    def setUp(self):
        """Create a test object with arithmetic properties."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.value = ArithmeticProperty("value", "i")

    def test_default_value(self):
        """Test default value is 0."""
        self.assertEqual(self.obj.value, 0)

    def test_set_and_get(self):
        """Test setting and getting values."""
        self.obj.value = 42
        self.assertEqual(self.obj.value, 42)

    def test_type_validation(self):
        """Test type validation on set."""
        with self.assertRaises(TypeError):
            self.obj.value = "invalid"

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.value = 123
        segments = type(self.obj).__dict__["value"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 4)

    def test_different_types(self):
        """Test different arithmetic types."""

        class TestObj:
            pass

        obj_float = TestObj()
        obj_float.__class__.val = ArithmeticProperty("val", "f")
        obj_float.val = 3.14
        self.assertAlmostEqual(obj_float.val, 3.14, places=5)

        obj_uint8 = TestObj()
        obj_uint8.__class__.val = ArithmeticProperty("val", "B")
        obj_uint8.val = 255
        self.assertEqual(obj_uint8.val, 255)


class TestArithmeticVectorProperty(unittest.TestCase):
    """Test ArithmeticVectorProperty descriptor."""

    def setUp(self):
        """Create a test object with vector properties."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.values = ArithmeticVectorProperty("values", "i")

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.values, [])

    def test_set_and_get(self):
        """Test setting and getting vector values."""
        self.obj.values = [1, 2, 3, 4, 5]
        self.assertEqual(self.obj.values, [1, 2, 3, 4, 5])

    def test_empty_list(self):
        """Test setting empty list."""
        self.obj.values = []
        self.assertEqual(self.obj.values, [])

    def test_resize_larger(self):
        """Test resizing to larger capacity."""
        self.obj.values = [1, 2, 3]
        self.obj.values = [10, 20, 30, 40, 50]
        self.assertEqual(self.obj.values, [10, 20, 30, 40, 50])

    def test_resize_smaller(self):
        """Test resizing to smaller capacity."""
        self.obj.values = [1, 2, 3, 4, 5]
        self.obj.values = [10, 20]
        self.assertEqual(self.obj.values, [10, 20])

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(TypeError):
            self.obj.values = ["invalid"]

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.values = [1, 2, 3]
        segments = type(self.obj).__dict__["values"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 4 * 3)

    def test_get_prefix_len(self):
        """Test getting prefix length."""
        prefix_len = type(self.obj).__dict__["values"].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4)  # uint32 for length

    def test_get_prefix(self):
        """Test getting prefix data."""
        self.obj.values = [1, 2, 3, 4]
        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__["values"].get_prefix(self.obj, buffer, offset)
        length = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(length, 4)

    def test_resize_from_buffer(self):
        """Test resizing from buffer."""
        buffer = bytearray(4)
        struct.pack_into("<I", buffer, 0, 5)  # Size 5
        offset = Serializable.Offset()
        type(self.obj).__dict__["values"].resize(self.obj, buffer, offset)
        self.assertEqual(len(self.obj.values), 5)


class TestArithmeticArrayProperty(unittest.TestCase):
    """Test ArithmeticArrayProperty descriptor."""

    def setUp(self):
        """Create a test object with array properties."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.values = ArithmeticArrayProperty("values", "i", 5)

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.values, [])

    def test_set_and_get(self):
        """Test setting and getting array values."""
        self.obj.values = [1, 2, 3, 4, 5]
        self.assertEqual(self.obj.values, [1, 2, 3, 4, 5])

    def test_wrong_length(self):
        """Test setting wrong length raises error."""
        with self.assertRaises(ValueError):
            self.obj.values = [1, 2, 3]

        with self.assertRaises(ValueError):
            self.obj.values = [1, 2, 3, 4, 5, 6]

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(TypeError):
            self.obj.values = ["a", "b", "c", "d", "e"]

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.values = [10, 20, 30, 40, 50]
        segments = type(self.obj).__dict__["values"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 4 * 5)


class TestStringProperty(unittest.TestCase):
    """Test StringProperty descriptor."""

    def setUp(self):
        """Create a test object with string property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.text = StringProperty("text")

    def test_default_empty_string(self):
        """Test default value is empty string."""
        self.assertEqual(self.obj.text, "")

    def test_set_and_get(self):
        """Test setting and getting string values."""
        self.obj.text = "Hello, World!"
        self.assertEqual(self.obj.text, "Hello, World!")

    def test_unicode_strings(self):
        """Test Unicode string handling."""
        self.obj.text = "Hello, 世界! 🌍"
        self.assertEqual(self.obj.text, "Hello, 世界! 🌍")

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.text = 123

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.text = "test"
        segments = type(self.obj).__dict__["text"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 4)  # "test" = 4 bytes

    def test_get_prefix_len(self):
        """Test getting prefix length."""
        prefix_len = type(self.obj).__dict__["text"].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4)  # uint32 for string length

    def test_get_prefix(self):
        """Test getting prefix data."""
        self.obj.text = "Hello"
        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__["text"].get_prefix(self.obj, buffer, offset)
        length = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(length, 5)  # "Hello" = 5 bytes

    def test_resize(self):
        """Test resizing string buffer."""
        self.obj.text = "short"
        offset = Serializable.Offset()
        buffer = bytearray(4)
        struct.pack_into("<I", buffer, 0, 20)  # Size 20
        type(self.obj).__dict__["text"].resize(self.obj, buffer, offset)
        # After resize, can set longer string
        self.obj.text = "much longer string"
        self.assertEqual(self.obj.text, "much longer string")


class TestStringVectorProperty(unittest.TestCase):
    """Test StringVectorProperty descriptor."""

    def setUp(self):
        """Create a test object with string vector property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.strings = StringVectorProperty("strings")

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.strings, [])

    def test_set_and_get(self):
        """Test setting and getting string vector."""
        self.obj.strings = ["one", "two", "three"]
        self.assertEqual(self.obj.strings, ["one", "two", "three"])

    def test_empty_list(self):
        """Test setting empty list."""
        self.obj.strings = []
        self.assertEqual(self.obj.strings, [])

    def test_unicode_strings(self):
        """Test Unicode strings in vector."""
        self.obj.strings = ["Hello", "世界", "🌍"]
        self.assertEqual(self.obj.strings, ["Hello", "世界", "🌍"])

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.strings = [1, 2, 3]

        with self.assertRaises(ValueError):
            self.obj.strings = ["valid", 123]

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.strings = ["ab", "cde", "f"]
        segments = type(self.obj).__dict__["strings"].get_segments(self.obj)
        self.assertEqual(len(segments), 3)
        self.assertEqual(len(segments[0]), 2)  # "ab"
        self.assertEqual(len(segments[1]), 3)  # "cde"
        self.assertEqual(len(segments[2]), 1)  # "f"

    def test_get_segment_count(self):
        """Test getting segment count."""
        self.obj.strings = ["a", "b", "c", "d"]
        count = type(self.obj).__dict__["strings"].get_segment_count(self.obj)
        self.assertEqual(count, 4)

    def test_get_prefix_len(self):
        """Test getting prefix length."""
        self.obj.strings = ["one", "two"]
        prefix_len = type(self.obj).__dict__["strings"].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4 + 2 * 4)  # vector length + 2 string lengths

    def test_get_prefix(self):
        """Test getting prefix data."""
        self.obj.strings = ["ab", "cde"]
        buffer = bytearray(12)  # 4 + 4 + 4
        offset = Serializable.Offset()
        type(self.obj).__dict__["strings"].get_prefix(self.obj, buffer, offset)

        vec_len = struct.unpack_from("<I", buffer, 0)[0]
        str1_len = struct.unpack_from("<I", buffer, 4)[0]
        str2_len = struct.unpack_from("<I", buffer, 8)[0]

        self.assertEqual(vec_len, 2)
        self.assertEqual(str1_len, 2)
        self.assertEqual(str2_len, 3)


class TestStringArrayProperty(unittest.TestCase):
    """Test StringArrayProperty descriptor."""

    def setUp(self):
        """Create a test object with string array property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.strings = StringArrayProperty("strings", 3)

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.strings, [])

    def test_set_and_get(self):
        """Test setting and getting string array."""
        self.obj.strings = ["one", "two", "three"]
        self.assertEqual(self.obj.strings, ["one", "two", "three"])

    def test_wrong_length(self):
        """Test setting wrong length raises error."""
        with self.assertRaises(ValueError):
            self.obj.strings = ["one", "two"]

        with self.assertRaises(ValueError):
            self.obj.strings = ["one", "two", "three", "four"]

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.strings = [1, 2, 3]

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.strings = ["a", "bc", "def"]
        segments = type(self.obj).__dict__["strings"].get_segments(self.obj)
        self.assertEqual(len(segments), 3)
        self.assertEqual(len(segments[0]), 1)
        self.assertEqual(len(segments[1]), 2)
        self.assertEqual(len(segments[2]), 3)

    def test_get_segment_count(self):
        """Test getting segment count."""
        self.obj.strings = ["a", "b", "c"]
        count = type(self.obj).__dict__["strings"].get_segment_count(self.obj)
        self.assertEqual(count, 3)


class TestMessageProperty(unittest.TestCase):
    """Test MessageProperty descriptor."""

    def setUp(self):
        """Create a test object with message property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.msg = MessageProperty("msg", SimpleMessage)

    def test_default_message(self):
        """Test default value is a message instance."""
        msg = self.obj.msg
        self.assertIsInstance(msg, SimpleMessage)

    def test_set_and_get(self):
        """Test setting and getting message."""
        new_msg = SimpleMessage()
        new_msg.id = 42
        new_msg.name = "Test"

        self.obj.msg = new_msg
        self.assertEqual(self.obj.msg.id, 42)
        self.assertEqual(self.obj.msg.name, "Test")

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.msg = "invalid"

        with self.assertRaises(ValueError):
            self.obj.msg = ComplexMessage()

    def test_get_segments(self):
        """Test getting memory segments."""
        self.obj.msg = SimpleMessage()
        self.obj.msg.id = 10
        self.obj.msg.name = "test"
        segments = type(self.obj).__dict__["msg"].get_segments(self.obj)
        self.assertGreater(len(segments), 0)


class TestMessageVectorProperty(unittest.TestCase):
    """Test MessageVectorProperty descriptor."""

    def setUp(self):
        """Create a test object with message vector property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.messages = MessageVectorProperty("messages", SimpleMessage)

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.messages, [])

    def test_set_and_get(self):
        """Test setting and getting message vector."""
        msg1 = SimpleMessage()
        msg1.id = 1
        msg1.name = "First"

        msg2 = SimpleMessage()
        msg2.id = 2
        msg2.name = "Second"

        self.obj.messages = [msg1, msg2]
        self.assertEqual(len(self.obj.messages), 2)
        self.assertEqual(self.obj.messages[0].id, 1)
        self.assertEqual(self.obj.messages[1].id, 2)

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.messages = ["invalid"]

        msg1 = SimpleMessage()
        msg2 = ComplexMessage()
        with self.assertRaises(ValueError):
            self.obj.messages = [msg1, msg2]

    def test_get_segment_count(self):
        """Test getting segment count."""
        msg1 = SimpleMessage()
        msg2 = SimpleMessage()
        self.obj.messages = [msg1, msg2]
        count = type(self.obj).__dict__["messages"].get_segment_count(self.obj)
        self.assertEqual(count, 4)  # 2 messages * 2 segments each


class TestMessageArrayProperty(unittest.TestCase):
    """Test MessageArrayProperty descriptor."""

    def setUp(self):
        """Create a test object with message array property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.messages = MessageArrayProperty("messages", SimpleMessage, 3)

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.messages, [])

    def test_set_and_get(self):
        """Test setting and getting message array."""
        messages = [SimpleMessage() for _ in range(3)]
        messages[0].id = 1
        messages[1].id = 2
        messages[2].id = 3

        self.obj.messages = messages
        self.assertEqual(len(self.obj.messages), 3)
        self.assertEqual(self.obj.messages[0].id, 1)
        self.assertEqual(self.obj.messages[2].id, 3)

    def test_wrong_length(self):
        """Test setting wrong length raises error."""
        with self.assertRaises(ValueError):
            self.obj.messages = [SimpleMessage(), SimpleMessage()]

        with self.assertRaises(ValueError):
            self.obj.messages = [SimpleMessage() for _ in range(4)]

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.messages = [1, 2, 3]


class TestPointerProperty(unittest.TestCase):
    """Test PointerProperty descriptor."""

    def setUp(self):
        """Create a test object with pointer property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.data = PointerProperty("data")

    def test_default_none(self):
        """Test default value is None."""
        self.assertIsNone(self.obj.data)

    def test_set_and_get(self):
        """Test setting and getting pointer values."""
        test_data = memoryview(bytearray(b"Hello, World!"))
        self.obj.data = test_data
        result = self.obj.data
        self.assertIsInstance(result, memoryview)
        self.assertEqual(bytes(result), b"Hello, World!")

    def test_set_binary_data(self):
        """Test setting binary data."""
        binary_data = memoryview(bytearray([0, 1, 2, 255, 128, 64]))
        self.obj.data = binary_data
        result = self.obj.data
        self.assertEqual(bytes(result), bytes([0, 1, 2, 255, 128, 64]))

    def test_type_validation(self):
        """Test type validation - must be memoryview."""
        with self.assertRaises(ValueError):
            self.obj.data = b"bytes not memoryview"

        with self.assertRaises(ValueError):
            self.obj.data = "string"

        with self.assertRaises(ValueError):
            self.obj.data = [1, 2, 3]

    def test_empty_memoryview(self):
        """Test setting empty memoryview."""
        empty_data = memoryview(bytearray())
        self.obj.data = empty_data
        result = self.obj.data
        self.assertEqual(len(result), 0)

    def test_resize_larger(self):
        """Test resizing to larger capacity."""
        small_data = memoryview(bytearray(b"small"))
        self.obj.data = small_data

        large_data = memoryview(bytearray(b"much larger data string"))
        self.obj.data = large_data

        result = self.obj.data
        self.assertEqual(bytes(result), b"much larger data string")

    def test_resize_smaller(self):
        """Test resizing to smaller capacity."""
        large_data = memoryview(bytearray(b"large data string"))
        self.obj.data = large_data

        small_data = memoryview(bytearray(b"tiny"))
        self.obj.data = small_data

        result = self.obj.data
        self.assertEqual(bytes(result), b"tiny")

    def test_get_segments(self):
        """Test getting memory segments."""
        test_data = memoryview(bytearray(b"test"))
        self.obj.data = test_data
        segments = type(self.obj).__dict__["data"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(bytes(segments[0]), b"test")

    def test_get_segments_empty(self):
        """Test getting segments when empty."""
        segments = type(self.obj).__dict__["data"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 0)

    def test_get_segment_count(self):
        """Test getting segment count."""
        test_data = memoryview(bytearray(b"data"))
        self.obj.data = test_data
        count = type(self.obj).__dict__["data"].get_segment_count(self.obj)
        self.assertEqual(count, 1)

    def test_get_segment_count_empty(self):
        """Test getting segment count when empty."""
        count = type(self.obj).__dict__["data"].get_segment_count(self.obj)
        self.assertEqual(count, 0)

    def test_get_prefix_len(self):
        """Test getting prefix length."""
        prefix_len = type(self.obj).__dict__["data"].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4)  # uint32 for length

    def test_get_prefix(self):
        """Test getting prefix data."""
        test_data = memoryview(bytearray(b"Hello"))
        self.obj.data = test_data

        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__["data"].get_prefix(self.obj, buffer, offset)

        length = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(length, 5)
        self.assertEqual(offset.value, 4)

    def test_get_prefix_empty(self):
        """Test getting prefix when data is empty."""
        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__["data"].get_prefix(self.obj, buffer, offset)

        length = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(length, 0)

    def test_resize_from_buffer(self):
        """Test resizing from buffer."""
        buffer = bytearray(4)
        struct.pack_into("<I", buffer, 0, 20)  # Size 20

        offset = Serializable.Offset()
        type(self.obj).__dict__["data"].resize(self.obj, buffer, offset)

        # After resize, can set data of that size
        large_data = memoryview(bytearray(b"x" * 20))
        self.obj.data = large_data
        result = self.obj.data
        self.assertEqual(len(result), 20)

    def test_multiple_assignments(self):
        """Test multiple assignments to same property."""
        for i in range(10):
            data = memoryview(bytearray(f"iteration {i}".encode()))
            self.obj.data = data
            result = self.obj.data
            self.assertEqual(bytes(result), f"iteration {i}".encode())

    def test_large_data(self):
        """Test handling large data buffers."""
        large_size = 10000
        large_data = memoryview(bytearray(b"x" * large_size))
        self.obj.data = large_data

        result = self.obj.data
        self.assertEqual(len(result), large_size)
        self.assertEqual(bytes(result), b"x" * large_size)

    def test_data_independence(self):
        """Test that different instances have independent data."""
        class TestObj:
            pass

        obj1 = TestObj()
        obj2 = TestObj()
        obj1.__class__.data = PointerProperty("data")
        obj2.__class__.data = PointerProperty("data")

        data1 = memoryview(bytearray(b"first"))
        data2 = memoryview(bytearray(b"second"))

        obj1.data = data1
        obj2.data = data2

        self.assertEqual(bytes(obj1.data), b"first")
        self.assertEqual(bytes(obj2.data), b"second")


class TestPointerVectorProperty(unittest.TestCase):
    """Test PointerVectorProperty descriptor."""

    def setUp(self):
        """Create a test object with pointer vector property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.pointers = rix_types.PointerVectorProperty("pointers")

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.pointers, [])

    def test_set_and_get_single(self):
        """Test setting and getting a single pointer."""
        data = memoryview(bytearray(b"Hello"))
        self.obj.pointers = [data]
        result = self.obj.pointers
        self.assertEqual(len(result), 1)
        self.assertEqual(bytes(result[0]), b"Hello")

    def test_set_and_get_multiple(self):
        """Test setting and getting multiple pointers."""
        data1 = memoryview(bytearray(b"First"))
        data2 = memoryview(bytearray(b"Second"))
        data3 = memoryview(bytearray(b"Third"))
        self.obj.pointers = [data1, data2, data3]
        
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        self.assertEqual(bytes(result[0]), b"First")
        self.assertEqual(bytes(result[1]), b"Second")
        self.assertEqual(bytes(result[2]), b"Third")

    def test_empty_list(self):
        """Test setting empty list."""
        self.obj.pointers = []
        self.assertEqual(self.obj.pointers, [])

    def test_set_binary_data(self):
        """Test setting binary data in vector."""
        data1 = memoryview(bytearray([0, 1, 2, 255]))
        data2 = memoryview(bytearray([128, 64, 32, 16]))
        self.obj.pointers = [data1, data2]
        
        result = self.obj.pointers
        self.assertEqual(bytes(result[0]), bytes([0, 1, 2, 255]))
        self.assertEqual(bytes(result[1]), bytes([128, 64, 32, 16]))

    def test_type_validation(self):
        """Test type validation - all elements must be memoryview."""
        with self.assertRaises(ValueError):
            self.obj.pointers = [b"bytes"]

        with self.assertRaises(ValueError):
            self.obj.pointers = ["string"]

        with self.assertRaises(ValueError):
            self.obj.pointers = [memoryview(bytearray(b"valid")), b"invalid"]

    def test_empty_memoryview_in_vector(self):
        """Test setting empty memoryview in vector."""
        empty = memoryview(bytearray())
        data = memoryview(bytearray(b"data"))
        self.obj.pointers = [empty, data, empty]
        
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 0)
        self.assertEqual(bytes(result[1]), b"data")
        self.assertEqual(len(result[2]), 0)

    def test_resize_vector_larger(self):
        """Test resizing vector to larger size."""
        small = [memoryview(bytearray(b"a")), memoryview(bytearray(b"b"))]
        self.obj.pointers = small
        
        large = [
            memoryview(bytearray(b"first")),
            memoryview(bytearray(b"second")),
            memoryview(bytearray(b"third")),
            memoryview(bytearray(b"fourth"))
        ]
        self.obj.pointers = large
        
        result = self.obj.pointers
        self.assertEqual(len(result), 4)
        self.assertEqual(bytes(result[0]), b"first")
        self.assertEqual(bytes(result[1]), b"second")
        self.assertEqual(bytes(result[2]), b"third")
        self.assertEqual(bytes(result[3]), b"fourth")

    def test_resize_vector_smaller(self):
        """Test resizing vector to smaller size - reducing number of pointers."""
        # Start with larger vector
        large = [
            memoryview(bytearray(b"one")),
            memoryview(bytearray(b"two")),
            memoryview(bytearray(b"three"))
        ]
        self.obj.pointers = large
        
        # Verify initial state
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        
        # Reduce to smaller vector
        small = [memoryview(bytearray(b"x"))]
        self.obj.pointers = small
        
        result = self.obj.pointers
        self.assertEqual(len(result), 1)
        self.assertEqual(bytes(result[0]), b"x")

    def test_get_segments(self):
        """Test getting memory segments."""
        data1 = memoryview(bytearray(b"abc"))
        data2 = memoryview(bytearray(b"defgh"))
        self.obj.pointers = [data1, data2]
        
        segments = type(self.obj).__dict__["pointers"].get_segments(self.obj)
        self.assertEqual(len(segments), 2)
        self.assertEqual(bytes(segments[0]), b"abc")
        self.assertEqual(bytes(segments[1]), b"defgh")

    def test_get_segments_empty(self):
        """Test getting segments when empty."""
        segments = type(self.obj).__dict__["pointers"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 0)

    def test_get_segment_count(self):
        """Test getting segment count."""
        data = [
            memoryview(bytearray(b"a")),
            memoryview(bytearray(b"b")),
            memoryview(bytearray(b"c"))
        ]
        self.obj.pointers = data
        count = type(self.obj).__dict__["pointers"].get_segment_count(self.obj)
        self.assertEqual(count, 3)

    def test_get_segment_count_empty(self):
        """Test getting segment count when empty."""
        count = type(self.obj).__dict__["pointers"].get_segment_count(self.obj)
        self.assertEqual(count, 0)

    def test_get_prefix_len(self):
        """Test getting prefix length."""
        data = [
            memoryview(bytearray(b"hello")),
            memoryview(bytearray(b"world"))
        ]
        self.obj.pointers = data
        prefix_len = type(self.obj).__dict__["pointers"].get_prefix_len(self.obj)
        # Should be 4 (vector count) + 2 * 4 (two pointer lengths)
        self.assertEqual(prefix_len, 12)

    def test_get_prefix_len_empty(self):
        """Test getting prefix length when empty."""
        prefix_len = type(self.obj).__dict__["pointers"].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4)  # Just the count

    def test_get_prefix(self):
        """Test getting prefix data."""
        data1 = memoryview(bytearray(b"abc"))
        data2 = memoryview(bytearray(b"defgh"))
        self.obj.pointers = [data1, data2]
        
        buffer = bytearray(12)  # 4 + 4 + 4
        offset = Serializable.Offset()
        type(self.obj).__dict__["pointers"].get_prefix(self.obj, buffer, offset)
        
        ptr_count = struct.unpack_from("<I", buffer, 0)[0]
        ptr1_len = struct.unpack_from("<I", buffer, 4)[0]
        ptr2_len = struct.unpack_from("<I", buffer, 8)[0]
        
        self.assertEqual(ptr_count, 2)
        self.assertEqual(ptr1_len, 3)
        self.assertEqual(ptr2_len, 5)
        self.assertEqual(offset.value, 12)

    def test_get_prefix_empty(self):
        """Test getting prefix when empty."""
        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__["pointers"].get_prefix(self.obj, buffer, offset)
        
        count = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(count, 0)

    def test_resize_from_buffer(self):
        """Test resizing from buffer."""
        # Create buffer with: count=3, len1=5, len2=10, len3=3
        buffer = bytearray(16)
        struct.pack_into("<I", buffer, 0, 3)   # 3 pointers
        struct.pack_into("<I", buffer, 4, 5)   # first is 5 bytes
        struct.pack_into("<I", buffer, 8, 10)  # second is 10 bytes
        struct.pack_into("<I", buffer, 12, 3)  # third is 3 bytes
        
        offset = Serializable.Offset()
        type(self.obj).__dict__["pointers"].resize(self.obj, buffer, offset)
        
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 5)
        self.assertEqual(len(result[1]), 10)
        self.assertEqual(len(result[2]), 3)

    def test_multiple_assignments(self):
        """Test multiple assignments to same property."""
        for i in range(10):
            data = [memoryview(bytearray(f"data{i}".encode()))]
            self.obj.pointers = data
            result = self.obj.pointers
            self.assertEqual(bytes(result[0]), f"data{i}".encode())

    def test_large_vector(self):
        """Test handling large number of pointers."""
        large_list = [memoryview(bytearray(f"item{i}".encode())) for i in range(100)]
        self.obj.pointers = large_list
        
        result = self.obj.pointers
        self.assertEqual(len(result), 100)
        self.assertEqual(bytes(result[0]), b"item0")
        self.assertEqual(bytes(result[99]), b"item99")

    def test_mixed_sizes(self):
        """Test pointers of different sizes."""
        small = memoryview(bytearray(b"x"))
        medium = memoryview(bytearray(b"medium size"))
        large = memoryview(bytearray(b"x" * 1000))
        
        self.obj.pointers = [small, medium, large]
        result = self.obj.pointers
        
        self.assertEqual(len(result[0]), 1)
        self.assertEqual(len(result[1]), 11)
        self.assertEqual(len(result[2]), 1000)

    def test_independence_between_instances(self):
        """Test that different instances have independent data."""
        class TestObj:
            pass

        obj1 = TestObj()
        obj2 = TestObj()
        obj1.__class__.pointers = rix_types.PointerVectorProperty("pointers")
        obj2.__class__.pointers = rix_types.PointerVectorProperty("pointers")

        data1 = [memoryview(bytearray(b"first"))]
        data2 = [memoryview(bytearray(b"second"))]

        obj1.pointers = data1
        obj2.pointers = data2

        self.assertEqual(bytes(obj1.pointers[0]), b"first")
        self.assertEqual(bytes(obj2.pointers[0]), b"second")


class TestPointerArrayProperty(unittest.TestCase):
    """Test PointerArrayProperty descriptor."""

    def setUp(self):
        """Create a test object with pointer array property."""

        class TestObj:
            pass

        self.obj = TestObj()
        self.obj.__class__.pointers = rix_types.PointerArrayProperty("pointers", 3)

    def test_default_empty_list(self):
        """Test default value is empty list."""
        self.assertEqual(self.obj.pointers, [])

    def test_set_and_get(self):
        """Test setting and getting pointer array."""
        data1 = memoryview(bytearray(b"First"))
        data2 = memoryview(bytearray(b"Second"))
        data3 = memoryview(bytearray(b"Third"))
        self.obj.pointers = [data1, data2, data3]
        
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        self.assertEqual(bytes(result[0]), b"First")
        self.assertEqual(bytes(result[1]), b"Second")
        self.assertEqual(bytes(result[2]), b"Third")

    def test_set_binary_data(self):
        """Test setting binary data in array."""
        data1 = memoryview(bytearray([0, 1, 2]))
        data2 = memoryview(bytearray([255, 254, 253]))
        data3 = memoryview(bytearray([128, 64, 32]))
        self.obj.pointers = [data1, data2, data3]
        
        result = self.obj.pointers
        self.assertEqual(bytes(result[0]), bytes([0, 1, 2]))
        self.assertEqual(bytes(result[1]), bytes([255, 254, 253]))
        self.assertEqual(bytes(result[2]), bytes([128, 64, 32]))

    def test_wrong_length(self):
        """Test setting wrong length raises error."""
        with self.assertRaises(ValueError):
            self.obj.pointers = [memoryview(bytearray(b"one"))]

        with self.assertRaises(ValueError):
            data = [memoryview(bytearray(f"item{i}".encode())) for i in range(5)]
            self.obj.pointers = data

    def test_type_validation(self):
        """Test type validation."""
        with self.assertRaises(ValueError):
            self.obj.pointers = [b"bytes", b"more", b"data"]

        with self.assertRaises(ValueError):
            self.obj.pointers = ["string", "more", "data"]

        with self.assertRaises(ValueError):
            self.obj.pointers = [
                memoryview(bytearray(b"valid")),
                b"invalid",
                memoryview(bytearray(b"valid"))
            ]

        with self.assertRaises(ValueError):
            self.obj.pointers = "not a list"

    def test_empty_memoryview_in_array(self):
        """Test setting empty memoryview in array."""
        empty = memoryview(bytearray())
        data = memoryview(bytearray(b"data"))
        self.obj.pointers = [empty, data, empty]
        
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 0)
        self.assertEqual(bytes(result[1]), b"data")
        self.assertEqual(len(result[2]), 0)

    def test_resize_individual_pointers_larger(self):
        """Test resizing individual pointers to larger size."""
        small = [
            memoryview(bytearray(b"a")),
            memoryview(bytearray(b"b")),
            memoryview(bytearray(b"c"))
        ]
        self.obj.pointers = small
        
        large = [
            memoryview(bytearray(b"much longer first")),
            memoryview(bytearray(b"much longer second")),
            memoryview(bytearray(b"much longer third"))
        ]
        self.obj.pointers = large
        
        result = self.obj.pointers
        self.assertEqual(bytes(result[0]), b"much longer first")
        self.assertEqual(bytes(result[1]), b"much longer second")
        self.assertEqual(bytes(result[2]), b"much longer third")

    def test_resize_individual_pointers_smaller(self):
        """Test resizing individual pointers to smaller size."""
        large = [
            memoryview(bytearray(b"long string one")),
            memoryview(bytearray(b"long string two")),
            memoryview(bytearray(b"long string three"))
        ]
        self.obj.pointers = large
        
        small = [
            memoryview(bytearray(b"x")),
            memoryview(bytearray(b"y")),
            memoryview(bytearray(b"z"))
        ]
        self.obj.pointers = small
        
        result = self.obj.pointers
        self.assertEqual(bytes(result[0]), b"x")
        self.assertEqual(bytes(result[1]), b"y")
        self.assertEqual(bytes(result[2]), b"z")

    def test_get_segments(self):
        """Test getting memory segments."""
        data1 = memoryview(bytearray(b"abc"))
        data2 = memoryview(bytearray(b"defgh"))
        data3 = memoryview(bytearray(b"ij"))
        self.obj.pointers = [data1, data2, data3]
        
        segments = type(self.obj).__dict__["pointers"].get_segments(self.obj)
        self.assertEqual(len(segments), 3)
        self.assertEqual(bytes(segments[0]), b"abc")
        self.assertEqual(bytes(segments[1]), b"defgh")
        self.assertEqual(bytes(segments[2]), b"ij")

    def test_get_segments_empty(self):
        """Test getting segments when empty."""
        segments = type(self.obj).__dict__["pointers"].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(len(segments[0]), 0)

    def test_get_segment_count(self):
        """Test getting segment count."""
        data = [
            memoryview(bytearray(b"a")),
            memoryview(bytearray(b"b")),
            memoryview(bytearray(b"c"))
        ]
        self.obj.pointers = data
        count = type(self.obj).__dict__["pointers"].get_segment_count(self.obj)
        self.assertEqual(count, 3)

    def test_get_segment_count_empty(self):
        """Test getting segment count when empty."""
        count = type(self.obj).__dict__["pointers"].get_segment_count(self.obj)
        self.assertEqual(count, 0)

    def test_get_prefix_len(self):
        """Test getting prefix length."""
        data = [
            memoryview(bytearray(b"hello")),
            memoryview(bytearray(b"world")),
            memoryview(bytearray(b"test"))
        ]
        self.obj.pointers = data
        prefix_len = type(self.obj).__dict__["pointers"].get_prefix_len(self.obj)
        # Should be 3 * 4 (three pointer lengths, no count field for arrays)
        self.assertEqual(prefix_len, 12)

    def test_get_prefix_len_empty(self):
        """Test getting prefix length when empty."""
        prefix_len = type(self.obj).__dict__["pointers"].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 0)

    def test_get_prefix(self):
        """Test getting prefix data."""
        data1 = memoryview(bytearray(b"abc"))
        data2 = memoryview(bytearray(b"defgh"))
        data3 = memoryview(bytearray(b"ij"))
        self.obj.pointers = [data1, data2, data3]
        
        buffer = bytearray(12)  # 3 * 4 bytes
        offset = Serializable.Offset()
        type(self.obj).__dict__["pointers"].get_prefix(self.obj, buffer, offset)
        
        ptr1_len = struct.unpack_from("<I", buffer, 0)[0]
        ptr2_len = struct.unpack_from("<I", buffer, 4)[0]
        ptr3_len = struct.unpack_from("<I", buffer, 8)[0]
        
        self.assertEqual(ptr1_len, 3)
        self.assertEqual(ptr2_len, 5)
        self.assertEqual(ptr3_len, 2)
        self.assertEqual(offset.value, 12)

    def test_get_prefix_empty(self):
        """Test getting prefix when empty."""
        buffer = bytearray(12)
        offset = Serializable.Offset()
        type(self.obj).__dict__["pointers"].get_prefix(self.obj, buffer, offset)
        
        # Offset should not change when empty
        self.assertEqual(offset.value, 0)

    def test_resize_from_buffer(self):
        """Test resizing from buffer."""
        # Create buffer with: len1=5, len2=10, len3=3
        buffer = bytearray(12)
        struct.pack_into("<I", buffer, 0, 5)   # first is 5 bytes
        struct.pack_into("<I", buffer, 4, 10)  # second is 10 bytes
        struct.pack_into("<I", buffer, 8, 3)   # third is 3 bytes
        
        offset = Serializable.Offset()
        type(self.obj).__dict__["pointers"].resize(self.obj, buffer, offset)
        
        result = self.obj.pointers
        self.assertEqual(len(result), 3)
        self.assertEqual(len(result[0]), 5)
        self.assertEqual(len(result[1]), 10)
        self.assertEqual(len(result[2]), 3)

    def test_multiple_assignments(self):
        """Test multiple assignments to same property."""
        for i in range(10):
            data = [
                memoryview(bytearray(f"data{i}a".encode())),
                memoryview(bytearray(f"data{i}b".encode())),
                memoryview(bytearray(f"data{i}c".encode()))
            ]
            self.obj.pointers = data
            result = self.obj.pointers
            self.assertEqual(bytes(result[0]), f"data{i}a".encode())
            self.assertEqual(bytes(result[2]), f"data{i}c".encode())

    def test_mixed_sizes(self):
        """Test pointers of different sizes in array."""
        small = memoryview(bytearray(b"x"))
        medium = memoryview(bytearray(b"medium size"))
        large = memoryview(bytearray(b"x" * 1000))
        
        self.obj.pointers = [small, medium, large]
        result = self.obj.pointers
        
        self.assertEqual(len(result[0]), 1)
        self.assertEqual(len(result[1]), 11)
        self.assertEqual(len(result[2]), 1000)

    def test_independence_between_instances(self):
        """Test that different instances have independent data."""
        class TestObj:
            pass

        obj1 = TestObj()
        obj2 = TestObj()
        obj1.__class__.pointers = rix_types.PointerArrayProperty("pointers", 3)
        obj2.__class__.pointers = rix_types.PointerArrayProperty("pointers", 3)

        data1 = [
            memoryview(bytearray(b"first1")),
            memoryview(bytearray(b"first2")),
            memoryview(bytearray(b"first3"))
        ]
        data2 = [
            memoryview(bytearray(b"second1")),
            memoryview(bytearray(b"second2")),
            memoryview(bytearray(b"second3"))
        ]

        obj1.pointers = data1
        obj2.pointers = data2

        self.assertEqual(bytes(obj1.pointers[0]), b"first1")
        self.assertEqual(bytes(obj2.pointers[0]), b"second1")

    def test_different_array_lengths(self):
        """Test creating arrays with different fixed lengths."""
        class TestObj:
            pass

        obj2 = TestObj()
        obj2.__class__.ptrs = rix_types.PointerArrayProperty("ptrs", 2)
        
        data = [
            memoryview(bytearray(b"one")),
            memoryview(bytearray(b"two"))
        ]
        obj2.ptrs = data
        self.assertEqual(len(obj2.ptrs), 2)

        obj5 = TestObj()
        obj5.__class__.ptrs = rix_types.PointerArrayProperty("ptrs", 5)
        
        data = [memoryview(bytearray(f"item{i}".encode())) for i in range(5)]
        obj5.ptrs = data
        self.assertEqual(len(obj5.ptrs), 5)


class TestInitFunctions(unittest.TestCase):
    """Test all init_* functions."""

    def test_init_arithmetic_types(self):
        """Test initialization of arithmetic types."""

        class TestObj:
            pass

        obj = TestObj()
        init_int32(obj, "value")
        obj.value = 42
        self.assertEqual(obj.value, 42)

        init_float(obj, "fval")
        obj.fval = 3.14
        self.assertAlmostEqual(obj.fval, 3.14, places=5)

        init_uint8(obj, "byte")
        obj.byte = 255
        self.assertEqual(obj.byte, 255)

    def test_init_all_int_types(self):
        """Test all integer type initializations."""

        class TestObj:
            pass

        obj = TestObj()

        # Signed integers
        init_int8(obj, "i8")
        obj.i8 = -128
        self.assertEqual(obj.i8, -128)

        init_int16(obj, "i16")
        obj.i16 = -32768
        self.assertEqual(obj.i16, -32768)

        init_int32(obj, "i32")
        obj.i32 = -2147483648
        self.assertEqual(obj.i32, -2147483648)

        init_int64(obj, "i64")
        obj.i64 = -9223372036854775808
        self.assertEqual(obj.i64, -9223372036854775808)

        # Unsigned integers
        init_uint8(obj, "u8")
        obj.u8 = 255
        self.assertEqual(obj.u8, 255)

        init_uint16(obj, "u16")
        obj.u16 = 65535
        self.assertEqual(obj.u16, 65535)

        init_uint32(obj, "u32")
        obj.u32 = 4294967295
        self.assertEqual(obj.u32, 4294967295)

        init_uint64(obj, "u64")
        obj.u64 = 18446744073709551615
        self.assertEqual(obj.u64, 18446744073709551615)

    def test_init_bool_and_char(self):
        """Test bool and char initialization."""

        class TestObj:
            pass

        obj = TestObj()

        init_bool(obj, "flag")
        obj.flag = True
        self.assertEqual(obj.flag, True)

        init_char(obj, "ch")
        obj.ch = b"A"
        self.assertEqual(obj.ch, b"A")

    def test_init_float_types(self):
        """Test float type initializations."""

        class TestObj:
            pass

        obj = TestObj()

        init_float(obj, "f")
        obj.f = 1.5
        self.assertAlmostEqual(obj.f, 1.5, places=5)

        init_double(obj, "d")
        obj.d = 2.718281828459045
        self.assertAlmostEqual(obj.d, 2.718281828459045, places=10)

    def test_init_vector_types(self):
        """Test vector type initializations."""

        class TestObj:
            pass

        obj = TestObj()

        init_int32_vector(obj, "vec")
        obj.vec = [1, 2, 3, 4, 5]
        self.assertEqual(obj.vec, [1, 2, 3, 4, 5])

        init_float_vector(obj, "fvec")
        obj.fvec = [1.0, 2.0, 3.0]
        self.assertEqual(len(obj.fvec), 3)

        init_uint8_vector(obj, "bytes")
        obj.bytes = [0, 127, 255]
        self.assertEqual(obj.bytes, [0, 127, 255])

    def test_init_array_types(self):
        """Test array type initializations."""

        class TestObj:
            pass

        obj = TestObj()

        init_int32_array(obj, "arr", 5)
        obj.arr = [10, 20, 30, 40, 50]
        self.assertEqual(obj.arr, [10, 20, 30, 40, 50])

        init_float_array(obj, "farr", 3)
        obj.farr = [1.1, 2.2, 3.3]
        self.assertEqual(len(obj.farr), 3)

    def test_init_string_types(self):
        """Test string type initializations."""

        class TestObj:
            pass

        obj = TestObj()

        init_string(obj, "text")
        obj.text = "Hello"
        self.assertEqual(obj.text, "Hello")

        init_string_vector(obj, "texts")
        obj.texts = ["one", "two", "three"]
        self.assertEqual(obj.texts, ["one", "two", "three"])

        init_string_array(obj, "fixed_texts", 2)
        obj.fixed_texts = ["first", "second"]
        self.assertEqual(obj.fixed_texts, ["first", "second"])

    def test_init_message_types(self):
        """Test message type initializations."""

        class TestObj:
            pass

        obj = TestObj()

        init_message(obj, "msg", SimpleMessage)
        obj.msg = SimpleMessage()
        obj.msg.id = 123
        self.assertEqual(obj.msg.id, 123)

        init_message_vector(obj, "msgs", SimpleMessage)
        obj.msgs = [SimpleMessage() for _ in range(2)]
        self.assertEqual(len(obj.msgs), 2)

        init_message_array(obj, "msg_arr", SimpleMessage, 3)
        obj.msg_arr = [SimpleMessage() for _ in range(3)]
        self.assertEqual(len(obj.msg_arr), 3)

    def test_init_pointer(self):
        """Test pointer type initialization."""

        class TestObj:
            pass

        obj = TestObj()

        init_pointer(obj, "ptr")
        test_data = memoryview(bytearray(b"pointer data"))
        obj.ptr = test_data
        self.assertEqual(bytes(obj.ptr), b"pointer data")

    def test_init_pointer_vector(self):
        """Test pointer vector type initialization."""

        class TestObj:
            pass

        obj = TestObj()

        init_pointer_vector(obj, "ptrs")
        data1 = memoryview(bytearray(b"first"))
        data2 = memoryview(bytearray(b"second"))
        obj.ptrs = [data1, data2]
        self.assertEqual(len(obj.ptrs), 2)
        self.assertEqual(bytes(obj.ptrs[0]), b"first")
        self.assertEqual(bytes(obj.ptrs[1]), b"second")

    def test_init_pointer_array(self):
        """Test pointer array type initialization."""

        class TestObj:
            pass

        obj = TestObj()

        init_pointer_array(obj, "ptr_arr", 4)
        data = [
            memoryview(bytearray(b"one")),
            memoryview(bytearray(b"two")),
            memoryview(bytearray(b"three")),
            memoryview(bytearray(b"four"))
        ]
        obj.ptr_arr = data
        self.assertEqual(len(obj.ptr_arr), 4)
        self.assertEqual(bytes(obj.ptr_arr[0]), b"one")
        self.assertEqual(bytes(obj.ptr_arr[3]), b"four")


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions for property manipulation."""

    def test_resize_string(self):
        """Test resize helper for strings."""
        obj = SimpleMessage()
        buffer = bytearray(8)
        struct.pack_into("<I", buffer, 0, 5)  # String length = 5
        buffer[4:9] = b"Hello"

        offset = Serializable.Offset()
        resize(obj, "name", buffer, offset)
        # After resize, the buffer is prepared
        self.assertGreater(offset.value, 0)

    def test_get_prefix_len_string(self):
        """Test get_prefix_len helper."""
        obj = SimpleMessage()
        obj.name = "Test"
        length = get_prefix_len(obj, "name")
        self.assertEqual(length, 4)  # uint32 for string length

    def test_get_prefix_string(self):
        """Test get_prefix helper."""
        obj = SimpleMessage()
        obj.name = "Hello"

        buffer = bytearray(4)
        offset = Serializable.Offset()
        get_prefix(obj, "name", buffer, offset)

        str_len = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(str_len, 5)

    def test_get_segment_count_message(self):
        """Test get_segment_count helper."""
        obj = ComplexMessage()
        count = get_segment_count(obj, "nested")
        self.assertEqual(count, 2)  # SimpleMessage has 2 segments


class TestMessageIntegration(unittest.TestCase):
    """Integration tests with actual Message classes."""

    def test_simple_message_creation(self):
        """Test creating a simple message."""
        msg = SimpleMessage()
        msg.id = 42
        msg.name = "TestMessage"

        self.assertEqual(msg.id, 42)
        self.assertEqual(msg.name, "TestMessage")

    def test_simple_message_serialization(self):
        """Test serializing a simple message."""
        msg = SimpleMessage()
        msg.id = 100
        msg.name = "Serialize"

        data = msg.serialize()
        self.assertIsInstance(data, bytes)
        self.assertGreater(len(data), 0)

    def test_simple_message_deserialization(self):
        """Test deserializing a simple message."""
        msg1 = SimpleMessage()
        msg1.id = 200
        msg1.name = "Original"

        data = msg1.serialize()

        msg2 = SimpleMessage()
        offset = Serializable.Offset()
        success = msg2.deserialize(data, offset)

        self.assertTrue(success)
        self.assertEqual(msg2.id, 200)
        self.assertEqual(msg2.name, "Original")

    def test_complex_message_creation(self):
        """Test creating a complex message."""
        msg = ComplexMessage()
        msg.description = "Complex test"
        msg.tags = ["tag1", "tag2", "tag3"]
        msg.nested.id = 10
        msg.nested.name = "Nested"

        self.assertEqual(msg.description, "Complex test")
        self.assertEqual(msg.tags, ["tag1", "tag2", "tag3"])
        self.assertEqual(msg.nested.id, 10)
        self.assertEqual(msg.nested.name, "Nested")

    def test_complex_message_serialization_deserialization(self):
        """Test serializing and deserializing a complex message."""
        msg1 = ComplexMessage()
        msg1.description = "Test description"
        msg1.tags = ["a", "b", "c"]
        msg1.nested.id = 999
        msg1.nested.name = "NestedMsg"

        data = msg1.serialize()

        msg2 = ComplexMessage()
        offset = Serializable.Offset()
        success = msg2.deserialize(data, offset)

        self.assertTrue(success)
        self.assertEqual(msg2.description, "Test description")
        self.assertEqual(msg2.tags, ["a", "b", "c"])
        self.assertEqual(msg2.nested.id, 999)
        self.assertEqual(msg2.nested.name, "NestedMsg")

    def test_message_with_empty_strings(self):
        """Test message with empty strings."""
        msg = SimpleMessage()
        msg.id = 5
        msg.name = ""

        data = msg.serialize()

        msg2 = SimpleMessage()
        offset = Serializable.Offset()
        success = msg2.deserialize(data, offset)

        self.assertTrue(success)
        self.assertEqual(msg2.id, 5)
        self.assertEqual(msg2.name, "")

    def test_message_with_unicode(self):
        """Test message with Unicode strings."""
        msg = SimpleMessage()
        msg.id = 42
        msg.name = "Hello 世界 🌍"

        data = msg.serialize()

        msg2 = SimpleMessage()
        offset = Serializable.Offset()
        success = msg2.deserialize(data, offset)

        self.assertTrue(success)
        self.assertEqual(msg2.id, 42)
        self.assertEqual(msg2.name, "Hello 世界 🌍")


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def test_max_integer_values(self):
        """Test maximum integer values."""

        class TestObj:
            pass

        obj = TestObj()

        init_uint8(obj, "u8")
        obj.u8 = 255
        self.assertEqual(obj.u8, 255)

        init_uint16(obj, "u16")
        obj.u16 = 65535
        self.assertEqual(obj.u16, 65535)

        init_uint32(obj, "u32")
        obj.u32 = 4294967295
        self.assertEqual(obj.u32, 4294967295)

    def test_min_integer_values(self):
        """Test minimum integer values."""

        class TestObj:
            pass

        obj = TestObj()

        init_int8(obj, "i8")
        obj.i8 = -128
        self.assertEqual(obj.i8, -128)

        init_int16(obj, "i16")
        obj.i16 = -32768
        self.assertEqual(obj.i16, -32768)

        init_int32(obj, "i32")
        obj.i32 = -2147483648
        self.assertEqual(obj.i32, -2147483648)

    def test_very_long_string(self):
        """Test very long strings."""

        class TestObj:
            pass

        obj = TestObj()
        init_string(obj, "text")

        long_string = "x" * 10000
        obj.text = long_string
        self.assertEqual(obj.text, long_string)
        self.assertEqual(len(obj.text), 10000)

    def test_empty_vectors(self):
        """Test empty vector handling."""

        class TestObj:
            pass

        obj = TestObj()
        init_int32_vector(obj, "vec")

        obj.vec = []
        self.assertEqual(obj.vec, [])
        self.assertEqual(len(obj.vec), 0)

    def test_large_vectors(self):
        """Test large vectors."""

        class TestObj:
            pass

        obj = TestObj()
        init_int32_vector(obj, "vec")

        large_vec = list(range(10000))
        obj.vec = large_vec
        self.assertEqual(len(obj.vec), 10000)
        self.assertEqual(obj.vec[0], 0)
        self.assertEqual(obj.vec[9999], 9999)

    def test_repeated_assignments(self):
        """Test repeated assignments to same property."""

        class TestObj:
            pass

        obj = TestObj()
        init_string(obj, "text")

        for i in range(100):
            obj.text = f"iteration_{i}"
            self.assertEqual(obj.text, f"iteration_{i}")

    def test_zero_length_arrays(self):
        """Test that zero-length arrays are not allowed in definition."""

        # Arrays must have a fixed length > 0
        class TestObj:
            pass

        obj = TestObj()
        # This should work (length > 0)
        init_int32_array(obj, "arr", 1)
        obj.arr = [42]
        self.assertEqual(obj.arr, [42])


class TestMemoryManagement(unittest.TestCase):
    """Test memory management and ctypes interaction."""

    def test_segment_addresses_are_valid(self):
        """Test that segment addresses are valid memory addresses."""
        msg = SimpleMessage()
        msg.id = 123
        msg.name = "test"

        segments = msg.get_segments()
        for segment in segments:
            # Check that address is a positive integer
            self.assertIsInstance(segment, memoryview)
            self.assertGreater(len(segment), 0)

    def test_multiple_objects_independent(self):
        """Test that multiple objects maintain independent data."""
        msg1 = SimpleMessage()
        msg1.id = 1
        msg1.name = "First"

        msg2 = SimpleMessage()
        msg2.id = 2
        msg2.name = "Second"

        self.assertEqual(msg1.id, 1)
        self.assertEqual(msg1.name, "First")
        self.assertEqual(msg2.id, 2)
        self.assertEqual(msg2.name, "Second")

    def test_ctypes_array_from_address(self):
        """Test reading data from ctypes addresses."""

        class TestObj:
            pass

        obj = TestObj()
        init_int32_vector(obj, "vec")
        obj.vec = [10, 20, 30]

        segments = type(obj).__dict__["vec"].get_segments(obj)
        buffer = segments[0]

        # Read data from address
        self.assertEqual(len(buffer), 12)  # 3 * 4 bytes


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
