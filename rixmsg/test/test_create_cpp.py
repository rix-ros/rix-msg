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
            "#include \"rix/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "#include \"rix/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "#include \"rix/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/package/MyType.hpp\"\n"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_include(message.fields), expected)

    def test_create_rixmsg_cpp_include_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "#include \"rix/package/MyNewType.hpp\"\n"
            "#include \"rix/package/MyType.hpp\"\n"
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
            "#include \"rix/new_package/AnotherNewType.hpp\"\n"
            "#include \"rix/package/MyNewType.hpp\"\n"
            "#include \"rix/package/MyType.hpp\"\n"
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
        expected = ("#include \"rix/diff_package/AnotherNewType.hpp\"\n"
                    "#include \"rix/new_package/AnotherNewType.hpp\"\n"
                    "#include \"rix/package/MyNewType.hpp\"\n"
                    "#include \"rix/package/MyType.hpp\"\n"
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

class TestCreateRixmsgCppGetSegmentCount(unittest.TestCase):
    def test_create_rixmsg_cpp_get_segment_count_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "count += 3;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "count += 3;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "count += 2;\n"
            "count += detail::get_segment_count(this->field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)
    
    def test_create_rixmsg_cpp_get_segment_count_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "count += 2;\n"
            "count += detail::get_segment_count(this->field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)
    
    def test_create_rixmsg_cpp_get_segment_count_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1;\n"
            "count += detail::get_segment_count(this->field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "count += 1;\n"
            "count += detail::get_segment_count(this->field2);\n"
            "count += detail::get_segment_count(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "count += 1;\n"
            "count += detail::get_segment_count(this->field2);\n"
            "count += detail::get_segment_count(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1;\n"
            "count += detail::get_segment_count(this->field2);\n"
            "count += detail::get_segment_count(this->field3);\n"
            "count += detail::get_segment_count(this->field4);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1;\n"
            "count += detail::get_segment_count(this->field2);\n"
            "count += detail::get_segment_count(this->field3);\n"
            "count += detail::get_segment_count(this->field4);\n"
            "count += detail::get_segment_count(this->field5);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)

    def test_create_rixmsg_cpp_get_segment_count_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "count += 1;\n"
            "count += detail::get_segment_count(this->field2);\n"
            "count += detail::get_segment_count(this->field3);\n"
            "count += detail::get_segment_count(this->field4);\n"
            "count += detail::get_segment_count(this->field5);\n"
            "count += detail::get_segment_count(this->field6);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segment_count(message.fields), expected)


class TestCreateRixmsgCppGetSegments(unittest.TestCase):
    def test_create_rixmsg_cpp_get_segments_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)
    
    def test_create_rixmsg_cpp_get_segments_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);\n"
            "detail::get_segments(this->field4, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);\n"
            "detail::get_segments(this->field4, segments, offset);\n"
            "detail::get_segments(this->field5, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)

    def test_create_rixmsg_cpp_get_segments_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_segments(this->field1, segments, offset);\n"
            "detail::get_segments(this->field2, segments, offset);\n"
            "detail::get_segments(this->field3, segments, offset);\n"
            "detail::get_segments(this->field4, segments, offset);\n"
            "detail::get_segments(this->field5, segments, offset);\n"
            "detail::get_segments(this->field6, segments, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_segments(message.fields), expected)


class TestCreateRixmsgCppEqualTo(unittest.TestCase):
    def test_create_rixmsg_cpp_get_segments_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)
    
    def test_create_rixmsg_cpp_equal_to_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "if (this->field4 != other.field4) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "if (this->field4 != other.field4) { return false; }\n"
            "if (this->field5 != other.field5) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)

    def test_create_rixmsg_cpp_equal_to_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "if (this->field1 != other.field1) { return false; }\n"
            "if (this->field2 != other.field2) { return false; }\n"
            "if (this->field3 != other.field3) { return false; }\n"
            "if (this->field4 != other.field4) { return false; }\n"
            "if (this->field5 != other.field5) { return false; }\n"
            "if (this->field6 != other.field6) { return false; }\n"
            "return true;"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_equal_to(message.fields), expected)


class TestCreateRixmsgCppGetPrefixLen(unittest.TestCase):
    def test_create_rixmsg_cpp_get_prefix_len_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)
    
    def test_create_rixmsg_cpp_get_prefix_len_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);\n"
            "len += detail::get_prefix_len(this->field4);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);\n"
            "len += detail::get_prefix_len(this->field4);\n"
            "len += detail::get_prefix_len(this->field5);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_len_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "len += detail::get_prefix_len(this->field2);\n"
            "len += detail::get_prefix_len(this->field3);\n"
            "len += detail::get_prefix_len(this->field4);\n"
            "len += detail::get_prefix_len(this->field5);\n"
            "len += detail::get_prefix_len(this->field6);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix_len(message.fields), expected)


class TestCreateRixmsgCppGetPrefix(unittest.TestCase):
    def test_create_rixmsg_cpp_get_prefix_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)
    
    def test_create_rixmsg_cpp_get_prefix_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);\n"
            "detail::get_prefix(this->field4, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);\n"
            "detail::get_prefix(this->field4, dst, offset);\n"
            "detail::get_prefix(this->field5, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)

    def test_create_rixmsg_cpp_get_prefix_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::get_prefix(this->field2, dst, offset);\n"
            "detail::get_prefix(this->field3, dst, offset);\n"
            "detail::get_prefix(this->field4, dst, offset);\n"
            "detail::get_prefix(this->field5, dst, offset);\n"
            "detail::get_prefix(this->field6, dst, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_get_prefix(message.fields), expected)


class TestCreateRixmsgCppResize(unittest.TestCase):
    def test_create_rixmsg_cpp_resize_number(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "detail::resize(this->field2, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_string_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)
    
    def test_create_rixmsg_cpp_resize_string_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)
    
    def test_create_rixmsg_cpp_resize_message(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::resize(this->field2, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_message_vector(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_message_array(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_message_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);\n"
            "detail::resize(this->field4, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_message_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);\n"
            "detail::resize(this->field4, src, offset);\n"
            "detail::resize(this->field5, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

    def test_create_rixmsg_cpp_resize_message_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "detail::resize(this->field2, src, offset);\n"
            "detail::resize(this->field3, src, offset);\n"
            "detail::resize(this->field4, src, offset);\n"
            "detail::resize(this->field5, src, offset);\n"
            "detail::resize(this->field6, src, offset);"
        )
        message = Message("test", "test_package", "1234567887654321", fields)
        self.assertEqual(create_rixmsg_cpp_resize(message.fields), expected)

class TestCreateRixmsgCppFullTest(unittest.TestCase):
    def test_create_rixmsg_cpp_full(self):
        expected ="""#pragma once

#include <cstdint>
#include <vector>
#include <array>
#include <string>
#include <cstring>

#include "rix/msg/message.hpp"
#include "rix/msg/serialization.hpp"
#include "rix/example/OtherMessage.hpp"

namespace rix {
namespace example {

class ExampleMessage : public Message {
  public:
    using Message::get_prefix;
    using Message::get_segments;

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

    std::array<uint64_t, 2> hash() const override {
        return {0xi_am_thirty_two_ULL, 0xcharacters_long!ULL};
    }

    bool operator==(const ExampleMessage &other) const {
        if (this->number != other.number) { return false; }
        if (this->word != other.word) { return false; }
        if (this->flag != other.flag) { return false; }
        if (this->object != other.object) { return false; }
        if (this->array != other.array) { return false; }
        if (this->static_array != other.static_array) { return false; }
        if (this->array_of_words != other.array_of_words) { return false; }
        if (this->static_array_of_words != other.static_array_of_words) { return false; }
        if (this->array_of_objects != other.array_of_objects) { return false; }
        if (this->static_array_of_objects != other.static_array_of_objects) { return false; }
        return true;
    }

    bool operator!=(const ExampleMessage &other) const {
        return !(*this == other);
    }

    size_t get_segment_count() const override {
        size_t count = 0;
        count += 5;
        count += detail::get_segment_count(this->object);
        count += detail::get_segment_count(this->array_of_words);
        count += detail::get_segment_count(this->static_array_of_words);
        count += detail::get_segment_count(this->array_of_objects);
        count += detail::get_segment_count(this->static_array_of_objects);
        return count;
    }

    bool get_segments(MessageSegment *segments, size_t len, size_t &offset) override {
        if (len < offset + get_segment_count()) {
            return false;
        }
        detail::get_segments(this->number, segments, offset);
        detail::get_segments(this->word, segments, offset);
        detail::get_segments(this->flag, segments, offset);
        detail::get_segments(this->object, segments, offset);
        detail::get_segments(this->array, segments, offset);
        detail::get_segments(this->static_array, segments, offset);
        detail::get_segments(this->array_of_words, segments, offset);
        detail::get_segments(this->static_array_of_words, segments, offset);
        detail::get_segments(this->array_of_objects, segments, offset);
        detail::get_segments(this->static_array_of_objects, segments, offset);
        return true;
    }

    bool get_segments(ConstMessageSegment *segments, size_t len, size_t &offset) const override {
        if (len < offset + get_segment_count()) {
            return false;
        }
        detail::get_segments(this->number, segments, offset);
        detail::get_segments(this->word, segments, offset);
        detail::get_segments(this->flag, segments, offset);
        detail::get_segments(this->object, segments, offset);
        detail::get_segments(this->array, segments, offset);
        detail::get_segments(this->static_array, segments, offset);
        detail::get_segments(this->array_of_words, segments, offset);
        detail::get_segments(this->static_array_of_words, segments, offset);
        detail::get_segments(this->array_of_objects, segments, offset);
        detail::get_segments(this->static_array_of_objects, segments, offset);
        return true;
    }

    uint32_t get_prefix_len() const override {
        uint32_t len = 0;
        len += detail::get_prefix_len(this->word);
        len += detail::get_prefix_len(this->object);
        len += detail::get_prefix_len(this->array);
        len += detail::get_prefix_len(this->array_of_words);
        len += detail::get_prefix_len(this->static_array_of_words);
        len += detail::get_prefix_len(this->array_of_objects);
        len += detail::get_prefix_len(this->static_array_of_objects);
        return len;
    }

    void get_prefix(uint8_t *dst, size_t &offset) const override {
        detail::get_prefix(this->word, dst, offset);
        detail::get_prefix(this->object, dst, offset);
        detail::get_prefix(this->array, dst, offset);
        detail::get_prefix(this->array_of_words, dst, offset);
        detail::get_prefix(this->static_array_of_words, dst, offset);
        detail::get_prefix(this->array_of_objects, dst, offset);
        detail::get_prefix(this->static_array_of_objects, dst, offset);
    }

    bool resize(const uint8_t *src, size_t len, size_t &offset) override {
        if (len < offset + get_prefix_len()) {
            return false;
        }
        detail::resize(this->word, src, offset);
        detail::resize(this->object, src, offset);
        detail::resize(this->array, src, offset);
        detail::resize(this->array_of_words, src, offset);
        detail::resize(this->static_array_of_words, src, offset);
        detail::resize(this->array_of_objects, src, offset);
        detail::resize(this->static_array_of_objects, src, offset);
        return true;
    }
};

} // namespace example
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
