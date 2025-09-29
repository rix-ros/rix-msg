import unittest
import os

os.sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src")
from message import Message
from create_py import *

class TestCreateRixmsgPyImports(unittest.TestCase):
    def test_create_rixmsg_py_imports_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'string[24]'}]
        expected = (
            ""
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.msg.package.MyNewType import MyNewType\n"
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType[256]', 'package': 'new_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.msg.new_package.AnotherNewType import AnotherNewType\n"
            "from rix.msg.package.MyNewType import MyNewType\n"
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_multi_pkg_dup(self):
        # TODO: self test is a false positive. There is no built in functionality
        #       for namespaces in JavaScript. Need to develop a way to handle self case
        #       or determine if it should be supported at all.
        fields = [{'name': 'field1', 'type': 'uint64'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType[]', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.msg.diff_package.AnotherNewType import AnotherNewType\n"
            "from rix.msg.new_package.AnotherNewType import AnotherNewType\n"
            "from rix.msg.package.MyNewType import MyNewType\n"
            "from rix.msg.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

class TestCreateRixmsgPyFields(unittest.TestCase):
    def test_create_rixmsg_py_constructor_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: list[float] = []\n"
            "self.field3: list[int] = [0 for _ in range(24)]"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: str = \"\"\n"
            "self.field3: list[float] = []"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: list[str] = [\"\" for _ in range(128)]\n"
            "self.field3: list[float] = []"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: list[str] = []\n"
            "self.field3: list[float] = []"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)
    
    def test_create_rixmsg_py_constructor_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: \"MyType\" = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: \"MyType\" = MyType()\n"
            "self.field3: \"MyNewType\" = MyNewType()\n"
            "self.field4: \"MyType\" = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_message_multi_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType[]', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType[16]', 'package': 'package'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: list[\"MyType\"] = []\n"
            "self.field3: \"MyNewType\" = MyNewType()\n"
            "self.field4: list[\"MyType\"] = [MyType() for _ in range(16)]"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: \"MyType\" = MyType()\n"
            "self.field3: \"MyNewType\" = MyNewType()\n"
            "self.field4: \"AnotherNewType\" = AnotherNewType()\n"
            "self.field5: \"MyType\" = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_message_multi_pkg_dup(self):
        # TODO: self test is a false positive. There is no built in functionality
        #       for namespaces in JavaScript. Need to develop a way to handle self case
        #       or determine if it should be supported at all.
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1: int = 0\n"
            "self.field2: \"MyType\" = MyType()\n"
            "self.field3: \"MyNewType\" = MyNewType()\n"
            "self.field4: \"AnotherNewType\" = AnotherNewType()\n"
            "self.field5: \"AnotherNewType\" = AnotherNewType()\n"
            "self.field6: \"MyType\" = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_py_constructor(message.fields)

class TestCreateRixmsgPySize(unittest.TestCase):
    def test_create_rixmsg_py_size_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_vector_number(self.field2, Message._size_float())\n"
            "size += Message._size_array_number(self.field3, Message._size_int16())"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_string(self.field2)\n"
            "size += Message._size_vector_number(self.field3, Message._size_float())"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_vector_string(self.field2)\n"
            "size += Message._size_vector_number(self.field3, Message._size_float())"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)
    
    def test_create_rixmsg_py_size_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_array_string(self.field2, 128)\n"
            "size += Message._size_vector_number(self.field3, Message._size_float())"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)
    
    def test_create_rixmsg_py_size_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_message(self.field2)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_message_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_message(self.field2)\n"
            "size += Message._size_vector_message(self.field3)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_message_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_message(self.field2)\n"
            "size += Message._size_array_message(self.field3, 10)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_message(self.field2)\n"
            "size += Message._size_message(self.field3)\n"
            "size += Message._size_message(self.field4)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_message(self.field2)\n"
            "size += Message._size_message(self.field3)\n"
            "size += Message._size_message(self.field4)\n"
            "size += Message._size_message(self.field5)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += Message._size_int32()\n"
            "size += Message._size_message(self.field2)\n"
            "size += Message._size_message(self.field3)\n"
            "size += Message._size_message(self.field4)\n"
            "size += Message._size_message(self.field5)\n"
            "size += Message._size_message(self.field6)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_size_function(message.fields), expected)

    def test_create_rixmsg_py_size_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_py_size_function(message.fields)

class TestCreateRixmsgPySerialize(unittest.TestCase):
    def test_create_rixmsg_py_serialize_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_float_vector(self.field2, buffer)\n"
            "Message._serialize_int16_array(self.field3, buffer, 24)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.maxDiff = None
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_string(self.field2, buffer)\n"
            "Message._serialize_float_vector(self.field3, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_string_vector(self.field2, buffer)\n"
            "Message._serialize_float_vector(self.field3, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_string_array(self.field2, buffer, 128)\n"
            "Message._serialize_float_vector(self.field3, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)
    
    def test_create_rixmsg_py_serialize_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_message(self.field2, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_message_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_message(self.field2, buffer)\n"
            "Message._serialize_message_vector(self.field3, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_message_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_message(self.field2, buffer)\n"
            "Message._serialize_message_array(self.field3, buffer, 10)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_message(self.field2, buffer)\n"
            "Message._serialize_message(self.field3, buffer)\n"
            "Message._serialize_message(self.field4, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_message(self.field2, buffer)\n"
            "Message._serialize_message(self.field3, buffer)\n"
            "Message._serialize_message(self.field4, buffer)\n"
            "Message._serialize_message(self.field5, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "Message._serialize_int32(self.field1, buffer)\n"
            "Message._serialize_message(self.field2, buffer)\n"
            "Message._serialize_message(self.field3, buffer)\n"
            "Message._serialize_message(self.field4, buffer)\n"
            "Message._serialize_message(self.field5, buffer)\n"
            "Message._serialize_message(self.field6, buffer)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_serialize_function(message.fields), expected)

    def test_create_rixmsg_py_serialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_py_serialize_function(message.fields)

class TestCreateRixmsgPyDeserialize(unittest.TestCase):
    def test_create_rixmsg_py_deserialize_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_float_vector(buffer, offset)\n"
            "self.field3 = Message._deserialize_int16_array(buffer, offset, 24)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_string(buffer, offset)\n"
            "self.field3 = Message._deserialize_float_vector(buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_string_vector(buffer, offset)\n"
            "self.field3 = Message._deserialize_float_vector(buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)
    
    def test_create_rixmsg_py_deserialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_string_array(buffer, offset, 128)\n"
            "self.field3 = Message._deserialize_float_vector(buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)
    
    def test_create_rixmsg_py_deserialize_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_message(buffer, offset, MyType)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_message_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_message(buffer, offset, MyType)\n"
            "self.field3 = Message._deserialize_message_vector(buffer, offset, MyType)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_message_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_message(buffer, offset, MyType)\n"
            "self.field3 = Message._deserialize_message_array(buffer, offset, 10, MyType)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_message(buffer, offset, MyType)\n"
            "self.field3 = Message._deserialize_message(buffer, offset, MyNewType)\n"
            "self.field4 = Message._deserialize_message(buffer, offset, MyType)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_message(buffer, offset, MyType)\n"
            "self.field3 = Message._deserialize_message(buffer, offset, MyNewType)\n"
            "self.field4 = Message._deserialize_message(buffer, offset, AnotherNewType)\n"
            "self.field5 = Message._deserialize_message(buffer, offset, MyType)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = Message._deserialize_int32(buffer, offset)\n"
            "self.field2 = Message._deserialize_message(buffer, offset, MyType)\n"
            "self.field3 = Message._deserialize_message(buffer, offset, MyNewType)\n"
            "self.field4 = Message._deserialize_message(buffer, offset, AnotherNewType)\n"
            "self.field5 = Message._deserialize_message(buffer, offset, AnotherNewType)\n"
            "self.field6 = Message._deserialize_message(buffer, offset, MyType)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(message.fields), expected)

    def test_create_rixmsg_py_deserialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_py_deserialize_function(message.fields)

class TestCreateRixmsgPyFullTest(unittest.TestCase):
    def test_create_rixmsg_py_full(self):
        expected ="""from rix.msg.message import Message
from rix.msg.example.OtherMessage import OtherMessage

class ExampleMessage(Message):
    def __init__(self):
        self.number: int = 0
        self.word: str = ""
        self.flag: bool = False
        self.object: "OtherMessage" = OtherMessage()
        self.array: list[int] = []
        self.static_array: list[int] = [0 for _ in range(3)]
        self.array_of_words: list[str] = []
        self.static_array_of_words: list[str] = ["" for _ in range(3)]
        self.array_of_objects: list["OtherMessage"] = []
        self.static_array_of_objects: list["OtherMessage"] = [OtherMessage() for _ in range(3)]

    def size(self) -> int:
        size = 0
        size += Message._size_uint32()
        size += Message._size_string(self.word)
        size += Message._size_bool()
        size += Message._size_message(self.object)
        size += Message._size_vector_number(self.array, Message._size_uint32())
        size += Message._size_array_number(self.static_array, Message._size_uint32())
        size += Message._size_vector_string(self.array_of_words)
        size += Message._size_array_string(self.static_array_of_words, 3)
        size += Message._size_vector_message(self.array_of_objects)
        size += Message._size_array_message(self.static_array_of_objects, 3)
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        Message._serialize_uint32(self.number, buffer)
        Message._serialize_string(self.word, buffer)
        Message._serialize_bool(self.flag, buffer)
        Message._serialize_message(self.object, buffer)
        Message._serialize_uint32_vector(self.array, buffer)
        Message._serialize_uint32_array(self.static_array, buffer, 3)
        Message._serialize_string_vector(self.array_of_words, buffer)
        Message._serialize_string_array(self.static_array_of_words, buffer, 3)
        Message._serialize_message_vector(self.array_of_objects, buffer)
        Message._serialize_message_array(self.static_array_of_objects, buffer, 3)

    def deserialize(self, buffer: bytearray, offset: Message.Offset) -> None:
        self.number = Message._deserialize_uint32(buffer, offset)
        self.word = Message._deserialize_string(buffer, offset)
        self.flag = Message._deserialize_bool(buffer, offset)
        self.object = Message._deserialize_message(buffer, offset, OtherMessage)
        self.array = Message._deserialize_uint32_vector(buffer, offset)
        self.static_array = Message._deserialize_uint32_array(buffer, offset, 3)
        self.array_of_words = Message._deserialize_string_vector(buffer, offset)
        self.static_array_of_words = Message._deserialize_string_array(buffer, offset, 3)
        self.array_of_objects = Message._deserialize_message_vector(buffer, offset, OtherMessage)
        self.static_array_of_objects = Message._deserialize_message_array(buffer, offset, 3, OtherMessage)

    def hash(self) -> list[int]:
        return [0xi_am_thirty_two_, 0xcharacters_long!]"""

        msg = {'name': 'ExampleMessage', 'package': 'example', 'fields': [
            {'name': 'number', 'type': 'uint32'},
            {'name': 'word', 'type': 'string'},
            {'name': 'flag', 'type': 'bool'},
            {'name': 'object', 'type': 'OtherMessage', 'package': 'example'},
            {'name': 'array', 'type': 'uint32[]'},
            {'name': 'static_array', 'type': 'uint32[3]'},
            {'name': 'array_of_words', 'type': 'string[]'},
            {'name': 'static_array_of_words', 'type': 'string[3]', 'package': 'example'},
            {'name': 'array_of_objects', 'type': 'OtherMessage[]', 'package': 'example'},
            {'name': 'static_array_of_objects', 'type': 'OtherMessage[3]', 'package': 'example'}
        ]}
        self.maxDiff = None
        msg['hash'] = "i_am_thirty_two_characters_long!"
        message = Message(msg['name'], msg['package'], msg['hash'], msg['fields'])
        self.assertEqual(create_rixmsg_py(message), expected)

if __name__ == "__main__":
    unittest.main()
