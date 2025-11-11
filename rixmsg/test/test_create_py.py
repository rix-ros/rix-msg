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
            "from rix.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "from rix.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "from rix.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.package.MyType import MyType\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_imports(message.fields), expected)

    def test_create_rixmsg_py_imports_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rix.package.MyNewType import MyNewType\n"
            "from rix.package.MyType import MyType\n"
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
            "from rix.new_package.AnotherNewType import AnotherNewType\n"
            "from rix.package.MyNewType import MyNewType\n"
            "from rix.package.MyType import MyType\n"
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
            "from rix.diff_package.AnotherNewType import AnotherNewType\n"
            "from rix.new_package.AnotherNewType import AnotherNewType\n"
            "from rix.package.MyNewType import MyNewType\n"
            "from rix.package.MyType import MyType\n"
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
            "init_int32(self, 'field1')\n"
            "init_float_vector(self, 'field2')\n"
            "init_int16_array(self, 'field3', 24)\n"
            "self._property_names = ['field1', 'field2', 'field3']\n"
            "self.field1 = 0\n"
            "self.field2 = []\n"
            "self.field3 = [0 for _ in range(24)]"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "init_int32(self, 'field1')\n"
            "init_string(self, 'field2')\n"
            "init_float_vector(self, 'field3')\n"
            "self._property_names = ['field1', 'field2', 'field3']\n"
            "self.field1 = 0\n"
            "self.field2 = \"\"\n"
            "self.field3 = []"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "init_int32(self, 'field1')\n"
            "init_string_array(self, 'field2', 128)\n"
            "init_float_vector(self, 'field3')\n"
            "self._property_names = ['field1', 'field2', 'field3']\n"
            "self.field1 = 0\n"
            "self.field2 = [\"\" for _ in range(128)]\n"
            "self.field3 = []"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "init_int32(self, 'field1')\n"
            "init_string_vector(self, 'field2')\n"
            "init_float_vector(self, 'field3')\n"
            "self._property_names = ['field1', 'field2', 'field3']\n"
            "self.field1 = 0\n"
            "self.field2 = []\n"
            "self.field3 = []"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)
    
    def test_create_rixmsg_py_constructor_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "init_int32(self, 'field1')\n"
            "init_message(self, 'field2', MyType)\n"
            "self._property_names = ['field1', 'field2']\n"
            "self.field1 = 0\n"
            "self.field2 = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "init_int32(self, 'field1')\n"
            "init_message(self, 'field2', MyType)\n"
            "init_message(self, 'field3', MyNewType)\n"
            "init_message(self, 'field4', MyType)\n"
            "self._property_names = ['field1', 'field2', 'field3', 'field4']\n"
            "self.field1 = 0\n"
            "self.field2 = MyType()\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)

    def test_create_rixmsg_py_constructor_message_multi_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType[]', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType[16]', 'package': 'package'}]
        expected = (
            "init_int32(self, 'field1')\n"
            "init_message_vector(self, 'field2', MyType)\n"
            "init_message(self, 'field3', MyNewType)\n"
            "init_message_array(self, 'field4', MyType, 16)\n"
            "self._property_names = ['field1', 'field2', 'field3', 'field4']\n"
            "self.field1 = 0\n"
            "self.field2 = []\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = [MyType() for _ in range(16)]"
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
            "init_int32(self, 'field1')\n"
            "init_message(self, 'field2', MyType)\n"
            "init_message(self, 'field3', MyNewType)\n"
            "init_message(self, 'field4', AnotherNewType)\n"
            "init_message(self, 'field5', MyType)\n"
            "self._property_names = ['field1', 'field2', 'field3', 'field4', 'field5']\n"
            "self.field1 = 0\n"
            "self.field2 = MyType()\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = AnotherNewType()\n"
            "self.field5 = MyType()"
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
            "init_int32(self, 'field1')\n"
            "init_message(self, 'field2', MyType)\n"
            "init_message(self, 'field3', MyNewType)\n"
            "init_message(self, 'field4', AnotherNewType)\n"
            "init_message(self, 'field5', AnotherNewType)\n"
            "init_message(self, 'field6', MyType)\n"
            "self._property_names = ['field1', 'field2', 'field3', 'field4', 'field5', 'field6']\n"
            "self.field1 = 0\n"
            "self.field2 = MyType()\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = AnotherNewType()\n"
            "self.field5 = AnotherNewType()\n"
            "self.field6 = MyType()"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_constructor(message.fields), expected)


class TestCreateRixmsgPyGetSegmentCount(unittest.TestCase):
    def test_create_rixmsg_py_get_segment_count_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "count += 3"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "count += 3"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "count += 2\n"
            "count += get_segment_count(self, 'field2')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)
    
    def test_create_rixmsg_py_get_segment_count_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "count += 2\n"
            "count += get_segment_count(self, 'field2')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)
    
    def test_create_rixmsg_py_get_segment_count_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1\n"
            "count += get_segment_count(self, 'field2')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "count += 1\n"
            "count += get_segment_count(self, 'field2')\n"
            "count += get_segment_count(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "count += 1\n"
            "count += get_segment_count(self, 'field2')\n"
            "count += get_segment_count(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1\n"
            "count += get_segment_count(self, 'field2')\n"
            "count += get_segment_count(self, 'field3')\n"
            "count += get_segment_count(self, 'field4')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1\n"
            "count += get_segment_count(self, 'field2')\n"
            "count += get_segment_count(self, 'field3')\n"
            "count += get_segment_count(self, 'field4')\n"
            "count += get_segment_count(self, 'field5')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)

    def test_create_rixmsg_py_get_segment_count_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1\n"
            "count += get_segment_count(self, 'field2')\n"
            "count += get_segment_count(self, 'field3')\n"
            "count += get_segment_count(self, 'field4')\n"
            "count += get_segment_count(self, 'field5')\n"
            "count += get_segment_count(self, 'field6')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_segment_count(message.fields), expected)


class TestCreateRixmsgPyGetPrefixLen(unittest.TestCase):
    def test_create_rixmsg_py_get_prefix_len_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)
    
    def test_create_rixmsg_py_get_prefix_len_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')\n"
            "prefix_len += get_prefix_len(self, 'field4')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')\n"
            "prefix_len += get_prefix_len(self, 'field4')\n"
            "prefix_len += get_prefix_len(self, 'field5')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_len_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "prefix_len += get_prefix_len(self, 'field2')\n"
            "prefix_len += get_prefix_len(self, 'field3')\n"
            "prefix_len += get_prefix_len(self, 'field4')\n"
            "prefix_len += get_prefix_len(self, 'field5')\n"
            "prefix_len += get_prefix_len(self, 'field6')"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix_len(message.fields), expected)


class TestCreateRixmsgPyGetPrefix(unittest.TestCase):
    def test_create_rixmsg_py_get_prefix_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)
    
    def test_create_rixmsg_py_get_prefix_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)\n"
            "get_prefix(self, 'field4', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)\n"
            "get_prefix(self, 'field4', buffer, offset)\n"
            "get_prefix(self, 'field5', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)

    def test_create_rixmsg_py_get_prefix_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "get_prefix(self, 'field2', buffer, offset)\n"
            "get_prefix(self, 'field3', buffer, offset)\n"
            "get_prefix(self, 'field4', buffer, offset)\n"
            "get_prefix(self, 'field5', buffer, offset)\n"
            "get_prefix(self, 'field6', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_get_prefix(message.fields), expected)


class TestCreateRixmsgPyResize(unittest.TestCase):
    def test_create_rixmsg_py_resize_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "resize(self, 'field2', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)
    
    def test_create_rixmsg_py_resize_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)
    
    def test_create_rixmsg_py_resize_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "resize(self, 'field2', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)\n"
            "resize(self, 'field4', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)\n"
            "resize(self, 'field4', buffer, offset)\n"
            "resize(self, 'field5', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)

    def test_create_rixmsg_py_resize_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "resize(self, 'field2', buffer, offset)\n"
            "resize(self, 'field3', buffer, offset)\n"
            "resize(self, 'field4', buffer, offset)\n"
            "resize(self, 'field5', buffer, offset)\n"
            "resize(self, 'field6', buffer, offset)"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_py_resize(message.fields), expected)
class TestCreateRixmsgPyFullTest(unittest.TestCase):
    def test_create_rixmsg_py_full(self):
        expected ="""from rix.msg import *
from rix.example.OtherMessage import OtherMessage

class ExampleMessage(Message):
    def __init__(self):
        init_uint32(self, 'number')
        init_string(self, 'word')
        init_bool(self, 'flag')
        init_message(self, 'object', OtherMessage)
        init_uint32_vector(self, 'array')
        init_uint32_array(self, 'static_array', 3)
        init_string_vector(self, 'array_of_words')
        init_string_array(self, 'static_array_of_words', 3)
        init_message_vector(self, 'array_of_objects', OtherMessage)
        init_message_array(self, 'static_array_of_objects', OtherMessage, 3)
        self._property_names = ['number', 'word', 'flag', 'object', 'array', 'static_array', 'array_of_words', 'static_array_of_words', 'array_of_objects', 'static_array_of_objects']
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

    def hash(self) -> list[int]:
        return [0xi_am_thirty_two_, 0xcharacters_long!]

    def resize(self, buffer: bytes, length: int, offset: Serializable.Offset) -> bool:
        if length < offset.value + self.get_prefix_len():
            return False
        resize(self, 'word', buffer, offset)
        resize(self, 'object', buffer, offset)
        resize(self, 'array', buffer, offset)
        resize(self, 'array_of_words', buffer, offset)
        resize(self, 'static_array_of_words', buffer, offset)
        resize(self, 'array_of_objects', buffer, offset)
        resize(self, 'static_array_of_objects', buffer, offset)
        return True
    
    def get_prefix_len(self) -> int:
        prefix_len = 0
        prefix_len += get_prefix_len(self, 'word')
        prefix_len += get_prefix_len(self, 'object')
        prefix_len += get_prefix_len(self, 'array')
        prefix_len += get_prefix_len(self, 'array_of_words')
        prefix_len += get_prefix_len(self, 'static_array_of_words')
        prefix_len += get_prefix_len(self, 'array_of_objects')
        prefix_len += get_prefix_len(self, 'static_array_of_objects')
        return prefix_len

    def get_prefix(self, buffer: bytearray, offset: Message.Offset) -> None:
        get_prefix(self, 'word', buffer, offset)
        get_prefix(self, 'object', buffer, offset)
        get_prefix(self, 'array', buffer, offset)
        get_prefix(self, 'array_of_words', buffer, offset)
        get_prefix(self, 'static_array_of_words', buffer, offset)
        get_prefix(self, 'array_of_objects', buffer, offset)
        get_prefix(self, 'static_array_of_objects', buffer, offset)

    def get_segment_count(self) -> int:
        count = 0
        count += 5
        count += get_segment_count(self, 'object')
        count += get_segment_count(self, 'array_of_words')
        count += get_segment_count(self, 'static_array_of_words')
        count += get_segment_count(self, 'array_of_objects')
        count += get_segment_count(self, 'static_array_of_objects')
        return count

    def get_segments(self) -> list[memoryview]:
        segments = []
        for prop_name in self._property_names:
            prop_descriptor = type(self).__dict__[prop_name]
            segments.extend(prop_descriptor.get_segments(self))
        return segments
"""

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
