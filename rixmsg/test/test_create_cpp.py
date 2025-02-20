import unittest
import os

os.sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../python")
from create_cpp import *

class TestCreateRixmsgCppInclude(unittest.TestCase):
    def test_create_rixmsg_cpp_include_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'string[24]'}]
        expected = (
            ""
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/msg/package/MyNewType.hpp\"\n"
            "#include \"rix/msg/package/MyType.hpp\"\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom_multi_pkg(self):
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
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_custom_multi_pkg_dup(self):
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
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_include(fields), expected)

    def test_create_rixmsg_cpp_include_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_cpp_include(fields)

class TestCreateRixmsgCppFields(unittest.TestCase):
    def test_create_rixmsg_cpp_fields_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "int32_t field1;\n"
            "std::vector<float> field2;\n"
            "std::array<int16_t, 24> field3;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "int32_t field1;\n"
            "std::string field2;\n"
            "std::vector<float> field3;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "int32_t field1;\n"
            "std::array<std::string, 128> field2;\n"
            "std::vector<float> field3;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "int32_t field1;\n"
            "std::vector<std::string> field2;\n"
            "std::vector<float> field3;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)
    
    def test_create_rixmsg_cpp_fields_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1;\n"
            "package::MyType field2;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1;\n"
            "package::MyType field2;\n"
            "package::MyNewType field3;\n"
            "package::MyType field4;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_custom_multi_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType[]', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType[16]', 'package': 'package'}]
        expected = (
            "int32_t field1;\n"
            "std::vector<package::MyType> field2;\n"
            "package::MyNewType field3;\n"
            "std::array<package::MyType, 16> field4;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1;\n"
            "package::MyType field2;\n"
            "package::MyNewType field3;\n"
            "new_package::AnotherNewType field4;\n"
            "package::MyType field5;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "int32_t field1;\n"
            "package::MyType field2;\n"
            "package::MyNewType field3;\n"
            "new_package::AnotherNewType field4;\n"
            "diff_package::AnotherNewType field5;\n"
            "package::MyType field6;"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_fields(fields), expected)

    def test_create_rixmsg_cpp_fields_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_cpp_fields(fields)

class TestCreateRixmsgCppSize(unittest.TestCase):
    def test_create_rixmsg_cpp_size_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_base_vec(field2);\n"
            "size += size_base_arr(field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_string(field2);\n"
            "size += size_base_vec(field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_string_vec(field2);\n"
            "size += size_base_vec(field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)
    
    def test_create_rixmsg_cpp_size_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_string_arr(field2);\n"
            "size += size_base_vec(field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)
    
    def test_create_rixmsg_cpp_size_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_custom(field2);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_custom(field2);\n"
            "size += size_custom_vec(field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_custom(field2);\n"
            "size += size_custom_arr(field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_custom(field2);\n"
            "size += size_custom(field3);\n"
            "size += size_custom(field4);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_custom(field2);\n"
            "size += size_custom(field3);\n"
            "size += size_custom(field4);\n"
            "size += size_custom(field5);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += size_base(field1);\n"
            "size += size_custom(field2);\n"
            "size += size_custom(field3);\n"
            "size += size_custom(field4);\n"
            "size += size_custom(field5);\n"
            "size += size_custom(field6);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_size_function(fields), expected)

    def test_create_rixmsg_cpp_size_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_cpp_size_function(fields)

class TestCreateRixmsgCppSerialize(unittest.TestCase):
    def test_create_rixmsg_cpp_serialize_base(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_base_vec(field2, buffer);\n"
            "serialize_base_arr(field3, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_string(field2, buffer);\n"
            "serialize_base_vec(field3, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_string_vec(field2, buffer);\n"
            "serialize_base_vec(field3, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_string_arr(field2, buffer);\n"
            "serialize_base_vec(field3, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)
    
    def test_create_rixmsg_cpp_serialize_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_custom(field2, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_custom(field2, buffer);\n"
            "serialize_custom_vec(field3, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_custom(field2, buffer);\n"
            "serialize_custom_arr(field3, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_custom(field2, buffer);\n"
            "serialize_custom(field3, buffer);\n"
            "serialize_custom(field4, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_custom(field2, buffer);\n"
            "serialize_custom(field3, buffer);\n"
            "serialize_custom(field4, buffer);\n"
            "serialize_custom(field5, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "serialize_base(field1, buffer);\n"
            "serialize_custom(field2, buffer);\n"
            "serialize_custom(field3, buffer);\n"
            "serialize_custom(field4, buffer);\n"
            "serialize_custom(field5, buffer);\n"
            "serialize_custom(field6, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_serialize_function(fields), expected)

    def test_create_rixmsg_cpp_serialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_cpp_serialize_function(fields)

class TestCreateRixmsgCppDeserialize(unittest.TestCase):
    def test_create_rixmsg_cpp_deserialize_base(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_base_vec(field2, buffer, offset);\n"
            "deserialize_base_arr(field3, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_string(field2, buffer, offset);\n"
            "deserialize_base_vec(field3, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_string_vec(field2, buffer, offset);\n"
            "deserialize_base_vec(field3, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)
    
    def test_create_rixmsg_cpp_deserialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_string_arr(field2, buffer, offset);\n"
            "deserialize_base_vec(field3, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)
    
    def test_create_rixmsg_cpp_deserialize_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_custom(field2, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_custom(field2, buffer, offset);\n"
            "deserialize_custom_vec(field3, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_custom(field2, buffer, offset);\n"
            "deserialize_custom_arr(field3, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_custom(field2, buffer, offset);\n"
            "deserialize_custom(field3, buffer, offset);\n"
            "deserialize_custom(field4, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_custom(field2, buffer, offset);\n"
            "deserialize_custom(field3, buffer, offset);\n"
            "deserialize_custom(field4, buffer, offset);\n"
            "deserialize_custom(field5, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "deserialize_base(field1, buffer, offset);\n"
            "deserialize_custom(field2, buffer, offset);\n"
            "deserialize_custom(field3, buffer, offset);\n"
            "deserialize_custom(field4, buffer, offset);\n"
            "deserialize_custom(field5, buffer, offset);\n"
            "deserialize_custom(field6, buffer, offset);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_cpp_deserialize_function(fields), expected)

    def test_create_rixmsg_cpp_deserialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_cpp_deserialize_function(fields)

class TestCreateRixmsgCppFullTest(unittest.TestCase):
    def test_create_rixmsg_cpp_full(self):
        expected ="""#pragma once

#include <cstdint>
#include <vector>
#include <string>
#include <cstring>

#include "rix/msg/message_base.hpp"
#include "rix/msg/serializer.hpp"
#include "rix/msg/example/OtherMessage.hpp"

namespace rix {
namespace msg {
namespace example {

class ExampleMessage : public MessageBase {
  public:
    uint32_t number;
    std::string word;
    bool flag;
    example::OtherMessage object;
    std::vector<uint32_t> array;
    std::array<uint32_t, 3> static_array;
    std::vector<std::string> array_of_words;
    std::array<std::string, 3> static_array_of_words;
    std::vector<example::OtherMessage> array_of_objects;
    std::array<example::OtherMessage, 3> static_array_of_objects;

    ExampleMessage() = default;
    ExampleMessage(const ExampleMessage &other) = default;
    ~ExampleMessage() = default;

  private:
    size_t size() const override {
        size_t size = 0;
        size += size_base(number);
        size += size_string(word);
        size += size_base(flag);
        size += size_custom(object);
        size += size_base_vec(array);
        size += size_base_arr(static_array);
        size += size_string_vec(array_of_words);
        size += size_string_arr(static_array_of_words);
        size += size_custom_vec(array_of_objects);
        size += size_custom_arr(static_array_of_objects);
        return size;
    }

    rix::msg::Hash hash() const override {
        return {0xi_am_thirty_two_ULL, 0xcharacters_long!ULL};
    }

    void serialize(std::vector<uint8_t> &buffer) const override {
        buffer.reserve(buffer.size() + this->size());
        serialize_base(number, buffer);
        serialize_string(word, buffer);
        serialize_base(flag, buffer);
        serialize_custom(object, buffer);
        serialize_base_vec(array, buffer);
        serialize_base_arr(static_array, buffer);
        serialize_string_vec(array_of_words, buffer);
        serialize_string_arr(static_array_of_words, buffer);
        serialize_custom_vec(array_of_objects, buffer);
        serialize_custom_arr(static_array_of_objects, buffer);
    }

    void deserialize(const std::vector<uint8_t> &buffer, size_t &offset) override {
        deserialize_base(number, buffer, offset);
        deserialize_string(word, buffer, offset);
        deserialize_base(flag, buffer, offset);
        deserialize_custom(object, buffer, offset);
        deserialize_base_vec(array, buffer, offset);
        deserialize_base_arr(static_array, buffer, offset);
        deserialize_string_vec(array_of_words, buffer, offset);
        deserialize_string_arr(static_array_of_words, buffer, offset);
        deserialize_custom_vec(array_of_objects, buffer, offset);
        deserialize_custom_arr(static_array_of_objects, buffer, offset);
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
        self.assertEqual(create_rixmsg_cpp(msg), expected)

if __name__ == "__main__":
    unittest.main()
