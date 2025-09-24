import unittest
import os

os.sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src")
from create_cpp import *

class TestCreateRixmsgCppInclude(unittest.TestCase):
    def test_create_rixmsg_cpp_include_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'string[24]'}]
        expected = (
            ""
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyNewType.hpp\"\n"
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType[256]', 'package': 'new_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/new_package/AnotherNewType.hpp\"\n"
            "#include \"rix/msg/package/MyNewType.hpp\"\n"
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'uint64'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType[]', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = ("#include \"rix/msg/diff_package/AnotherNewType.hpp\"\n"
                    "#include \"rix/msg/new_package/AnotherNewType.hpp\"\n"
                    "#include \"rix/msg/package/MyNewType.hpp\"\n"
                    "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_cpp_include(message.fields)

class TestCreateRixmsgCppFields(unittest.TestCase):
    def test_create_rixmsg_cpp_fields_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "int32_t field1{};\n"
            "std::vector<float> field2{};\n"
            "std::array<int16_t, 24> field3{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "int32_t field1{};\n"
            "std::string field2{};\n"
            "std::vector<float> field3{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "int32_t field1{};\n"
            "std::array<std::string, 128> field2{};\n"
            "std::vector<float> field3{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "int32_t field1{};\n"
            "std::vector<std::string> field2{};\n"
            "std::vector<float> field3{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)
    
    def test_create_rixmsg_cpp_fields_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1{};\n"
            "package::MyType field2{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1{};\n"
            "package::MyType field2{};\n"
            "package::MyNewType field3{};\n"
            "package::MyType field4{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_message_multi_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType[]', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType[16]', 'package': 'package'}]
        expected = (
            "int32_t field1{};\n"
            "std::vector<package::MyType> field2{};\n"
            "package::MyNewType field3{};\n"
            "std::array<package::MyType, 16> field4{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1{};\n"
            "package::MyType field2{};\n"
            "package::MyNewType field3{};\n"
            "new_package::AnotherNewType field4{};\n"
            "package::MyType field5{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1{};\n"
            "package::MyType field2{};\n"
            "package::MyNewType field3{};\n"
            "new_package::AnotherNewType field4{};\n"
            "diff_package::AnotherNewType field5{};\n"
            "package::MyType field6{};"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_fields(message.fields), expected)

    def test_create_rixmsg_cpp_fields_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_cpp_fields(message.fields)

class TestCreateRixmsgCppSize(unittest.TestCase):
    def test_create_rixmsg_cpp_size_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_number_vector(field2);\n"
            "size += size_number_array(field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_string(field2);\n"
            "size += size_number_vector(field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_string_vector(field2);\n"
            "size += size_number_vector(field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)
    
    def test_create_rixmsg_cpp_size_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_string_array(field2);\n"
            "size += size_number_vector(field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)
    
    def test_create_rixmsg_cpp_size_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_message(field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_message(field2);\n"
            "size += size_message_vector(field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_message(field2);\n"
            "size += size_message_array(field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_message(field2);\n"
            "size += size_message(field3);\n"
            "size += size_message(field4);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_message(field2);\n"
            "size += size_message(field3);\n"
            "size += size_message(field4);\n"
            "size += size_message(field5);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_number(field1);\n"
            "size += size_message(field2);\n"
            "size += size_message(field3);\n"
            "size += size_message(field4);\n"
            "size += size_message(field5);\n"
            "size += size_message(field6);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_size_function(message.fields), expected)

    def test_create_rixmsg_cpp_size_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_cpp_size_function(message.fields)

class TestCreateRixmsgCppSerialize(unittest.TestCase):
    def test_create_rixmsg_cpp_serialize_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_number_vector(dst, offset, field2);\n"
            "serialize_number_array(dst, offset, field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_string(dst, offset, field2);\n"
            "serialize_number_vector(dst, offset, field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_string_vector(dst, offset, field2);\n"
            "serialize_number_vector(dst, offset, field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_string_array(dst, offset, field2);\n"
            "serialize_number_vector(dst, offset, field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)
    
    def test_create_rixmsg_cpp_serialize_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_message(dst, offset, field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_message(dst, offset, field2);\n"
            "serialize_message_vector(dst, offset, field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_message(dst, offset, field2);\n"
            "serialize_message_array(dst, offset, field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_message(dst, offset, field2);\n"
            "serialize_message(dst, offset, field3);\n"
            "serialize_message(dst, offset, field4);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_message(dst, offset, field2);\n"
            "serialize_message(dst, offset, field3);\n"
            "serialize_message(dst, offset, field4);\n"
            "serialize_message(dst, offset, field5);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_number(dst, offset, field1);\n"
            "serialize_message(dst, offset, field2);\n"
            "serialize_message(dst, offset, field3);\n"
            "serialize_message(dst, offset, field4);\n"
            "serialize_message(dst, offset, field5);\n"
            "serialize_message(dst, offset, field6);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_serialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_cpp_serialize_function(message.fields)

class TestCreateRixmsgCppDeserialize(unittest.TestCase):
    def test_create_rixmsg_cpp_deserialize_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_number_vector(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_number_array(field3, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_string(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_number_vector(field3, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_string_vector(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_number_vector(field3, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)
    
    def test_create_rixmsg_cpp_deserialize_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_string_array(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_number_vector(field3, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)
    
    def test_create_rixmsg_cpp_deserialize_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field2, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_message_vector(field3, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_message_array(field3, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field3, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field4, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field3, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field4, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field5, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (!deserialize_number(field1, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field2, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field3, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field4, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field5, src, size, offset)) { return false; };\n"
            "if (!deserialize_message(field6, src, size, offset)) { return false; };"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(message.fields), expected)

    def test_create_rixmsg_cpp_deserialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            message = Message("test", "test_package", "1234567887654321", fields)
            create_rixmsg_cpp_deserialize_function(message.fields)

class TestCreateRixmsgCppFullTest(unittest.TestCase):
    def test_create_rixmsg_cpp_full(self):
        expected ="""#pragma once

#include <cstdint>
#include <vector>
#include <array>
#include <map>
#include <string>
#include <cstring>

#include "rix/msg/serialization.hpp"
#include "rix/msg/message.hpp"
#include "rix/msg/example/OtherMessage.hpp"

namespace rix {
namespace msg {
namespace example {

class ExampleMessage : public Message {
  public:
    uint32_t number{};
    std::string word{};
    bool flag{};
    example::OtherMessage object{};
    std::vector<uint32_t> array{};
    std::array<uint32_t, 3> static_array{};
    std::vector<std::string> array_of_words{};
    std::array<std::string, 3> static_array_of_words{};
    std::vector<example::OtherMessage> array_of_objects{};
    std::array<example::OtherMessage, 3> static_array_of_objects{};

    ExampleMessage() = default;
    ExampleMessage(const ExampleMessage &other) = default;
    ~ExampleMessage() = default;

    size_t size() const override {
        using namespace detail;
        size_t size = 0;
        size += size_number(number);
        size += size_string(word);
        size += size_number(flag);
        size += size_message(object);
        size += size_number_vector(array);
        size += size_number_array(static_array);
        size += size_string_vector(array_of_words);
        size += size_string_array(static_array_of_words);
        size += size_message_vector(array_of_objects);
        size += size_message_array(static_array_of_objects);
        return size;
    }

    std::array<uint64_t, 2> hash() const override {
        return {0xi_am_thirty_two_ULL, 0xcharacters_long!ULL};
    }

    void serialize(uint8_t *dst, size_t &offset) const override {
        using namespace detail;
        serialize_number(dst, offset, number);
        serialize_string(dst, offset, word);
        serialize_number(dst, offset, flag);
        serialize_message(dst, offset, object);
        serialize_number_vector(dst, offset, array);
        serialize_number_array(dst, offset, static_array);
        serialize_string_vector(dst, offset, array_of_words);
        serialize_string_array(dst, offset, static_array_of_words);
        serialize_message_vector(dst, offset, array_of_objects);
        serialize_message_array(dst, offset, static_array_of_objects);
    }

    bool deserialize(const uint8_t *src, size_t size, size_t &offset) override {
        using namespace detail;
        if (!deserialize_number(number, src, size, offset)) { return false; };
        if (!deserialize_string(word, src, size, offset)) { return false; };
        if (!deserialize_number(flag, src, size, offset)) { return false; };
        if (!deserialize_message(object, src, size, offset)) { return false; };
        if (!deserialize_number_vector(array, src, size, offset)) { return false; };
        if (!deserialize_number_array(static_array, src, size, offset)) { return false; };
        if (!deserialize_string_vector(array_of_words, src, size, offset)) { return false; };
        if (!deserialize_string_array(static_array_of_words, src, size, offset)) { return false; };
        if (!deserialize_message_vector(array_of_objects, src, size, offset)) { return false; };
        if (!deserialize_message_array(static_array_of_objects, src, size, offset)) { return false; };
        return true;
    }
};

} // namespace example
} // namespace msg
} // namespace rix"""

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
        self.assertEqual(create_rixmsg_cpp(message), expected)

if __name__ == "__main__":
    unittest.main()
