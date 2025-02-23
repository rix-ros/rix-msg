import unittest
import os

os.sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src")
from type_regex import add_flags_to_fields
from create_py import *

class TestCreateRixmsgPyImports(unittest.TestCase):
    def test_create_rixmsg_py_imports_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'string[24]'}]
        expected = (
            ""
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rixmsg.package.MyNewType import MyNewType\n"
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType[256]', 'package': 'new_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "from rixmsg.new_package.AnotherNewType import AnotherNewType\n"
            "from rixmsg.package.MyNewType import MyNewType\n"
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_custom_multi_pkg_dup(self):
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
            "from rixmsg.diff_package.AnotherNewType import AnotherNewType\n"
            "from rixmsg.new_package.AnotherNewType import AnotherNewType\n"
            "from rixmsg.package.MyNewType import MyNewType\n"
            "from rixmsg.package.MyType import MyType\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_imports(fields), expected)

    def test_create_rixmsg_py_imports_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_py_imports(fields)

class TestCreateRixmsgPyFields(unittest.TestCase):
    def test_create_rixmsg_py_constructor_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = []\n"
            "self.field3 = [0 for _ in range(24)]"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = \"\"\n"
            "self.field3 = []"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = [\"\" for _ in range(128)]\n"
            "self.field3 = []"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = []\n"
            "self.field3 = []"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)
    
    def test_create_rixmsg_py_constructor_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = MyType()"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = MyType()\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = MyType()"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_custom_multi_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType[]', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType[16]', 'package': 'package'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = []\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = [MyType() for _ in range(16)]"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = 0\n"
            "self.field2 = MyType()\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = AnotherNewType()\n"
            "self.field5 = MyType()"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_custom_multi_pkg_dup(self):
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
            "self.field1 = 0\n"
            "self.field2 = MyType()\n"
            "self.field3 = MyNewType()\n"
            "self.field4 = AnotherNewType()\n"
            "self.field5 = AnotherNewType()\n"
            "self.field6 = MyType()"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_constructor(fields), expected)

    def test_create_rixmsg_py_constructor_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_py_constructor(fields)

class TestCreateRixmsgPySize(unittest.TestCase):
    def test_create_rixmsg_py_size_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_vector_base(self.field2, MessageBase._size_float())\n"
            "size += MessageBase._size_fixed_array_base(self.field3, MessageBase._size_int16())"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_string(self.field2)\n"
            "size += MessageBase._size_vector_base(self.field3, MessageBase._size_float())"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_vector_string(self.field2)\n"
            "size += MessageBase._size_vector_base(self.field3, MessageBase._size_float())"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)
    
    def test_create_rixmsg_py_size_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_fixed_array_string(self.field2, 128)\n"
            "size += MessageBase._size_vector_base(self.field3, MessageBase._size_float())"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)
    
    def test_create_rixmsg_py_size_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_custom(self.field2)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_custom(self.field2)\n"
            "size += MessageBase._size_vector_custom(self.field3)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_custom(self.field2)\n"
            "size += MessageBase._size_fixed_array_custom(self.field3, 10)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_custom(self.field2)\n"
            "size += MessageBase._size_custom(self.field3)\n"
            "size += MessageBase._size_custom(self.field4)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_custom(self.field2)\n"
            "size += MessageBase._size_custom(self.field3)\n"
            "size += MessageBase._size_custom(self.field4)\n"
            "size += MessageBase._size_custom(self.field5)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32()\n"
            "size += MessageBase._size_custom(self.field2)\n"
            "size += MessageBase._size_custom(self.field3)\n"
            "size += MessageBase._size_custom(self.field4)\n"
            "size += MessageBase._size_custom(self.field5)\n"
            "size += MessageBase._size_custom(self.field6)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_size_function(fields), expected)

    def test_create_rixmsg_py_size_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_py_size_function(fields)

class TestCreateRixmsgPySerialize(unittest.TestCase):
    def test_create_rixmsg_py_serialize_base(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_vector(self.field2, buffer, MessageBase._serialize_float)\n"
            "MessageBase._serialize_fixed_array(self.field3, buffer, MessageBase._serialize_int16, 24)"
        )
        add_flags_to_fields(fields)
        self.maxDiff = None
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_string(self.field2, buffer)\n"
            "MessageBase._serialize_vector(self.field3, buffer, MessageBase._serialize_float)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_vector(self.field2, buffer, MessageBase._serialize_string)\n"
            "MessageBase._serialize_vector(self.field3, buffer, MessageBase._serialize_float)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_fixed_array(self.field2, buffer, MessageBase._serialize_string, 128)\n"
            "MessageBase._serialize_vector(self.field3, buffer, MessageBase._serialize_float)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)
    
    def test_create_rixmsg_py_serialize_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_custom(self.field2, buffer)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_custom(self.field2, buffer)\n"
            "MessageBase._serialize_vector(self.field3, buffer, MessageBase._serialize_custom)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_custom(self.field2, buffer)\n"
            "MessageBase._serialize_fixed_array(self.field3, buffer, MessageBase._serialize_custom, 10)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_custom(self.field2, buffer)\n"
            "MessageBase._serialize_custom(self.field3, buffer)\n"
            "MessageBase._serialize_custom(self.field4, buffer)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_custom(self.field2, buffer)\n"
            "MessageBase._serialize_custom(self.field3, buffer)\n"
            "MessageBase._serialize_custom(self.field4, buffer)\n"
            "MessageBase._serialize_custom(self.field5, buffer)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "MessageBase._serialize_int32(self.field1, buffer)\n"
            "MessageBase._serialize_custom(self.field2, buffer)\n"
            "MessageBase._serialize_custom(self.field3, buffer)\n"
            "MessageBase._serialize_custom(self.field4, buffer)\n"
            "MessageBase._serialize_custom(self.field5, buffer)\n"
            "MessageBase._serialize_custom(self.field6, buffer)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_serialize_function(fields), expected)

    def test_create_rixmsg_py_serialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_py_serialize_function(fields)

class TestCreateRixmsgPyDeserialize(unittest.TestCase):
    def test_create_rixmsg_py_deserialize_base(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float)\n"
            "self.field3 = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_int16, 24)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_string(buffer, context)\n"
            "self.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string)\n"
            "self.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)
    
    def test_create_rixmsg_py_deserialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, 128)\n"
            "self.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)
    
    def test_create_rixmsg_py_deserialize_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_custom(buffer, context, MyType)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_custom(buffer, context, MyType)\n"
            "self.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, MyType)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_custom(buffer, context, MyType)\n"
            "self.field3 = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, 10, MyType)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_custom(buffer, context, MyType)\n"
            "self.field3 = MessageBase._deserialize_custom(buffer, context, MyNewType)\n"
            "self.field4 = MessageBase._deserialize_custom(buffer, context, MyType)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_custom(buffer, context, MyType)\n"
            "self.field3 = MessageBase._deserialize_custom(buffer, context, MyNewType)\n"
            "self.field4 = MessageBase._deserialize_custom(buffer, context, AnotherNewType)\n"
            "self.field5 = MessageBase._deserialize_custom(buffer, context, MyType)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "self.field1 = MessageBase._deserialize_int32(buffer, context)\n"
            "self.field2 = MessageBase._deserialize_custom(buffer, context, MyType)\n"
            "self.field3 = MessageBase._deserialize_custom(buffer, context, MyNewType)\n"
            "self.field4 = MessageBase._deserialize_custom(buffer, context, AnotherNewType)\n"
            "self.field5 = MessageBase._deserialize_custom(buffer, context, AnotherNewType)\n"
            "self.field6 = MessageBase._deserialize_custom(buffer, context, MyType)"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_py_deserialize_function(fields), expected)

    def test_create_rixmsg_py_deserialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_py_deserialize_function(fields)

class TestCreateRixmsgPyFullTest(unittest.TestCase):
    def test_create_rixmsg_py_full(self):
        expected ="""from rixmsg.message_base import MessageBase
from rixmsg.example.OtherMessage import OtherMessage

class ExampleMessage(MessageBase):
    def __init__(self):
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

    def size(self) -> int:
        size = 0
        size += MessageBase._size_uint32()
        size += MessageBase._size_string(self.word)
        size += MessageBase._size_bool()
        size += MessageBase._size_custom(self.object)
        size += MessageBase._size_vector_base(self.array, MessageBase._size_uint32())
        size += MessageBase._size_fixed_array_base(self.static_array, MessageBase._size_uint32())
        size += MessageBase._size_vector_string(self.array_of_words)
        size += MessageBase._size_fixed_array_string(self.static_array_of_words, 3)
        size += MessageBase._size_vector_custom(self.array_of_objects)
        size += MessageBase._size_fixed_array_custom(self.static_array_of_objects, 3)
        return size
    
    def serialize(self, buffer: bytearray) -> None:
        MessageBase._serialize_uint32(self.number, buffer)
        MessageBase._serialize_string(self.word, buffer)
        MessageBase._serialize_bool(self.flag, buffer)
        MessageBase._serialize_custom(self.object, buffer)
        MessageBase._serialize_vector(self.array, buffer, MessageBase._serialize_uint32)
        MessageBase._serialize_fixed_array(self.static_array, buffer, MessageBase._serialize_uint32, 3)
        MessageBase._serialize_vector(self.array_of_words, buffer, MessageBase._serialize_string)
        MessageBase._serialize_fixed_array(self.static_array_of_words, buffer, MessageBase._serialize_string, 3)
        MessageBase._serialize_vector(self.array_of_objects, buffer, MessageBase._serialize_custom)
        MessageBase._serialize_fixed_array(self.static_array_of_objects, buffer, MessageBase._serialize_custom, 3)

    def deserialize(self, buffer: bytearray, context: dict) -> None:
        self.number = MessageBase._deserialize_uint32(buffer, context)
        self.word = MessageBase._deserialize_string(buffer, context)
        self.flag = MessageBase._deserialize_bool(buffer, context)
        self.object = MessageBase._deserialize_custom(buffer, context, OtherMessage)
        self.array = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_uint32)
        self.static_array = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_uint32, 3)
        self.array_of_words = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string)
        self.static_array_of_words = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, 3)
        self.array_of_objects = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, OtherMessage)
        self.static_array_of_objects = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, 3, OtherMessage)

    def hash(self) -> int:
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
        add_flags_to_fields(msg['fields'])
        self.assertEqual(create_rixmsg_py(msg), expected)

if __name__ == "__main__":
    unittest.main()
