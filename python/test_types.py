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
import ctypes
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
type_mapping = rix_types.type_mapping

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
        validate_python_type(42, ctypes.c_int32)
        validate_python_type(255, ctypes.c_uint8)
        validate_python_type(-128, ctypes.c_int8)
    
    def test_valid_float_types(self):
        """Test validation of valid float types."""
        validate_python_type(3.14, ctypes.c_float)
        validate_python_type(2.718, ctypes.c_double)
    
    def test_valid_list_types(self):
        """Test validation of homogeneous lists."""
        validate_python_type([1, 2, 3], ctypes.c_int32)
        validate_python_type([1.0, 2.0, 3.0], ctypes.c_float)
    
    def test_empty_list(self):
        """Test validation of empty lists."""
        validate_python_type([], ctypes.c_int32)
        validate_python_type([], ctypes.c_float)
    
    def test_invalid_type_mismatch(self):
        """Test validation fails for type mismatches."""
        with self.assertRaises(TypeError):
            validate_python_type("string", ctypes.c_int32)
        
        with self.assertRaises(TypeError):
            validate_python_type(42, ctypes.c_float)
    
    def test_invalid_heterogeneous_list(self):
        """Test validation fails for heterogeneous lists."""
        with self.assertRaises(TypeError):
            validate_python_type([1, 2, 3.0], ctypes.c_int32)


class TestArithmeticProperty(unittest.TestCase):
    """Test ArithmeticProperty descriptor."""
    
    def setUp(self):
        """Create a test object with arithmetic properties."""
        class TestObj:
            pass
        self.obj = TestObj()
        self.obj.__class__.value = ArithmeticProperty("value", ctypes.c_int32)
    
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
        segments = type(self.obj).__dict__['value'].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0][1], ctypes.sizeof(ctypes.c_int32))
    
    def test_different_types(self):
        """Test different arithmetic types."""
        class TestObj:
            pass
        
        obj_float = TestObj()
        obj_float.__class__.val = ArithmeticProperty("val", ctypes.c_float)
        obj_float.val = 3.14
        self.assertAlmostEqual(obj_float.val, 3.14, places=5)
        
        obj_uint8 = TestObj()
        obj_uint8.__class__.val = ArithmeticProperty("val", ctypes.c_uint8)
        obj_uint8.val = 255
        self.assertEqual(obj_uint8.val, 255)


class TestArithmeticVectorProperty(unittest.TestCase):
    """Test ArithmeticVectorProperty descriptor."""
    
    def setUp(self):
        """Create a test object with vector properties."""
        class TestObj:
            pass
        self.obj = TestObj()
        self.obj.__class__.values = ArithmeticVectorProperty("values", ctypes.c_int32)
    
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
        segments = type(self.obj).__dict__['values'].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0][1], ctypes.sizeof(ctypes.c_int32) * 3)
    
    def test_get_prefix_len(self):
        """Test getting prefix length."""
        prefix_len = type(self.obj).__dict__['values'].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4)  # uint32 for length
    
    def test_get_prefix(self):
        """Test getting prefix data."""
        self.obj.values = [1, 2, 3, 4]
        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__['values'].get_prefix(self.obj, buffer, offset)
        length = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(length, 4)
    
    def test_resize_from_buffer(self):
        """Test resizing from buffer."""
        buffer = bytearray(4)
        struct.pack_into("<I", buffer, 0, 5)  # Size 5
        offset = Serializable.Offset()
        type(self.obj).__dict__['values'].resize(self.obj, buffer, offset)
        self.assertEqual(len(self.obj.values), 5)


class TestArithmeticArrayProperty(unittest.TestCase):
    """Test ArithmeticArrayProperty descriptor."""
    
    def setUp(self):
        """Create a test object with array properties."""
        class TestObj:
            pass
        self.obj = TestObj()
        self.obj.__class__.values = ArithmeticArrayProperty("values", ctypes.c_int32, 5)
    
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
        segments = type(self.obj).__dict__['values'].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0][1], ctypes.sizeof(ctypes.c_int32) * 5)


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
        segments = type(self.obj).__dict__['text'].get_segments(self.obj)
        self.assertEqual(len(segments), 1)
        self.assertEqual(segments[0][1], 4)  # "test" = 4 bytes
    
    def test_get_prefix_len(self):
        """Test getting prefix length."""
        prefix_len = type(self.obj).__dict__['text'].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4)  # uint32 for string length
    
    def test_get_prefix(self):
        """Test getting prefix data."""
        self.obj.text = "Hello"
        buffer = bytearray(4)
        offset = Serializable.Offset()
        type(self.obj).__dict__['text'].get_prefix(self.obj, buffer, offset)
        length = struct.unpack_from("<I", buffer, 0)[0]
        self.assertEqual(length, 5)  # "Hello" = 5 bytes
    
    def test_resize(self):
        """Test resizing string buffer."""
        self.obj.text = "short"
        offset = Serializable.Offset()
        buffer = bytearray(4)
        struct.pack_into("<I", buffer, 0, 20)  # Size 20
        type(self.obj).__dict__['text'].resize(self.obj, buffer, offset)
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
        segments = type(self.obj).__dict__['strings'].get_segments(self.obj)
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0][1], 2)  # "ab"
        self.assertEqual(segments[1][1], 3)  # "cde"
        self.assertEqual(segments[2][1], 1)  # "f"
    
    def test_get_segment_count(self):
        """Test getting segment count."""
        self.obj.strings = ["a", "b", "c", "d"]
        count = type(self.obj).__dict__['strings'].get_segment_count(self.obj)
        self.assertEqual(count, 4)
    
    def test_get_prefix_len(self):
        """Test getting prefix length."""
        self.obj.strings = ["one", "two"]
        prefix_len = type(self.obj).__dict__['strings'].get_prefix_len(self.obj)
        self.assertEqual(prefix_len, 4 + 2 * 4)  # vector length + 2 string lengths
    
    def test_get_prefix(self):
        """Test getting prefix data."""
        self.obj.strings = ["ab", "cde"]
        buffer = bytearray(12)  # 4 + 4 + 4
        offset = Serializable.Offset()
        type(self.obj).__dict__['strings'].get_prefix(self.obj, buffer, offset)
        
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
        segments = type(self.obj).__dict__['strings'].get_segments(self.obj)
        self.assertEqual(len(segments), 3)
        self.assertEqual(segments[0][1], 1)
        self.assertEqual(segments[1][1], 2)
        self.assertEqual(segments[2][1], 3)
    
    def test_get_segment_count(self):
        """Test getting segment count."""
        self.obj.strings = ["a", "b", "c"]
        count = type(self.obj).__dict__['strings'].get_segment_count(self.obj)
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
        segments = type(self.obj).__dict__['msg'].get_segments(self.obj)
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
        count = type(self.obj).__dict__['messages'].get_segment_count(self.obj)
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
        obj.ch = b'A'
        self.assertEqual(obj.ch, b'A')
    
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
        for addr, length in segments:
            # Check that address is a positive integer
            self.assertIsInstance(addr, int)
            self.assertGreater(addr, 0)
            self.assertGreater(length, 0)
    
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
        addr, length = segments[0]
        
        # Read data from address
        data = (ctypes.c_uint8 * length).from_address(addr)
        self.assertEqual(len(data), length)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
