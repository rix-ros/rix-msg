import unittest
import os

os.sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/../src")
from type_regex import add_flags_to_fields
from create_js import *

class TestCreateRixmsgJSImports(unittest.TestCase):
    def test_create_rixmsg_js_imports_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'string[24]'}]
        expected = (
            ""
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "import { MyNewType } from \"../package/MyNewType.js\";\n"
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType[256]', 'package': 'new_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "import { AnotherNewType } from \"../new_package/AnotherNewType.js\";\n"
            "import { MyNewType } from \"../package/MyNewType.js\";\n"
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_custom_multi_pkg_dup(self):
        # TODO: This test is a false positive. There is no built in functionality
        #       for namespaces in JavaScript. Need to develop a way to handle this case
        #       or determine if it should be supported at all.
        fields = [{'name': 'field1', 'type': 'uint64'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType[]', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "import { AnotherNewType } from \"../diff_package/AnotherNewType.js\";\n"
            "import { AnotherNewType } from \"../new_package/AnotherNewType.js\";\n"
            "import { MyNewType } from \"../package/MyNewType.js\";\n"
            "import { MyType } from \"../package/MyType.js\";\n"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_imports(fields), expected)

    def test_create_rixmsg_js_imports_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_js_imports(fields)

class TestCreateRixmsgJSFields(unittest.TestCase):
    def test_create_rixmsg_js_constructor_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = [];\n"
            "this.field3 = Array.from({length: 24}, () => 0);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = \'\';\n"
            "this.field3 = [];"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = Array.from({length: 128}, () => \'\');\n"
            "this.field3 = [];"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = [];\n"
            "this.field3 = [];"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)
    
    def test_create_rixmsg_js_constructor_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = new MyType();"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = new MyType();\n"
            "this.field3 = new MyNewType();\n"
            "this.field4 = new MyType();"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_custom_multi_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType[]', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType[16]', 'package': 'package'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = [];\n"
            "this.field3 = new MyNewType();\n"
            "this.field4 = Array.from({length: 16}, () => new MyType());"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = new MyType();\n"
            "this.field3 = new MyNewType();\n"
            "this.field4 = new AnotherNewType();\n"
            "this.field5 = new MyType();"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_custom_multi_pkg_dup(self):
        # TODO: This test is a false positive. There is no built in functionality
        #       for namespaces in JavaScript. Need to develop a way to handle this case
        #       or determine if it should be supported at all.
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = 0;\n"
            "this.field2 = new MyType();\n"
            "this.field3 = new MyNewType();\n"
            "this.field4 = new AnotherNewType();\n"
            "this.field5 = new AnotherNewType();\n"
            "this.field6 = new MyType();"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_constructor(fields), expected)

    def test_create_rixmsg_js_constructor_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_js_constructor(fields)

class TestCreateRixmsgJSSize(unittest.TestCase):
    def test_create_rixmsg_js_size_simple(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_vector_base(this.field2, MessageBase._size_float());\n"
            "size += MessageBase._size_fixed_array_base(this.field3, MessageBase._size_int16());"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_string(this.field2);\n"
            "size += MessageBase._size_vector_base(this.field3, MessageBase._size_float());"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_vector_string(this.field2);\n"
            "size += MessageBase._size_vector_base(this.field3, MessageBase._size_float());"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)
    
    def test_create_rixmsg_js_size_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_fixed_array_string(this.field2, 128);\n"
            "size += MessageBase._size_vector_base(this.field3, MessageBase._size_float());"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)
    
    def test_create_rixmsg_js_size_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_custom(this.field2);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_custom(this.field2);\n"
            "size += MessageBase._size_vector_custom(this.field3);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_custom(this.field2);\n"
            "size += MessageBase._size_fixed_array_custom(this.field3, 10);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_custom(this.field2);\n"
            "size += MessageBase._size_custom(this.field3);\n"
            "size += MessageBase._size_custom(this.field4);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_custom(this.field2);\n"
            "size += MessageBase._size_custom(this.field3);\n"
            "size += MessageBase._size_custom(this.field4);\n"
            "size += MessageBase._size_custom(this.field5);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "size += MessageBase._size_int32();\n"
            "size += MessageBase._size_custom(this.field2);\n"
            "size += MessageBase._size_custom(this.field3);\n"
            "size += MessageBase._size_custom(this.field4);\n"
            "size += MessageBase._size_custom(this.field5);\n"
            "size += MessageBase._size_custom(this.field6);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_size_function(fields), expected)

    def test_create_rixmsg_js_size_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_js_size_function(fields)

class TestCreateRixmsgJSSerialize(unittest.TestCase):
    def test_create_rixmsg_js_serialize_base(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_vector(this.field2, buffer, MessageBase._serialize_float);\n"
            "buffer = MessageBase._serialize_fixed_array(this.field3, buffer, MessageBase._serialize_int16, 24);"
        )
        add_flags_to_fields(fields)
        self.maxDiff = None
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_string(this.field2, buffer);\n"
            "buffer = MessageBase._serialize_vector(this.field3, buffer, MessageBase._serialize_float);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_vector(this.field2, buffer, MessageBase._serialize_string);\n"
            "buffer = MessageBase._serialize_vector(this.field3, buffer, MessageBase._serialize_float);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_fixed_array(this.field2, buffer, MessageBase._serialize_string, 128);\n"
            "buffer = MessageBase._serialize_vector(this.field3, buffer, MessageBase._serialize_float);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)
    
    def test_create_rixmsg_js_serialize_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field2, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field2, buffer);\n"
            "buffer = MessageBase._serialize_vector(this.field3, buffer, MessageBase._serialize_custom);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field2, buffer);\n"
            "buffer = MessageBase._serialize_fixed_array(this.field3, buffer, MessageBase._serialize_custom, 10);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field2, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field3, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field4, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field2, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field3, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field4, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field5, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "buffer = MessageBase._serialize_int32(this.field1, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field2, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field3, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field4, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field5, buffer);\n"
            "buffer = MessageBase._serialize_custom(this.field6, buffer);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_serialize_function(fields), expected)

    def test_create_rixmsg_js_serialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_js_serialize_function(fields)

class TestCreateRixmsgJSDeserialize(unittest.TestCase):
    def test_create_rixmsg_js_deserialize_base(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'float[]'},
                  {'name': 'field3', 'type': 'int16[24]'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float);\n"
            "this.field3 = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_int16, 24);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_string(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_string(buffer, context);\n"
            "this.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_string_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string);\n"
            "this.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)
    
    def test_create_rixmsg_js_deserialize_string_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'string[128]'},
                  {'name': 'field3', 'type': 'float[]'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, 128);\n"
            "this.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)
    
    def test_create_rixmsg_js_deserialize_custom(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_custom(buffer, context, MyType);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_custom_vec(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[]', 'package': 'package'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_custom(buffer, context, MyType);\n"
            "this.field3 = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, MyType);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_custom_arr(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyType[10]', 'package': 'package'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_custom(buffer, context, MyType);\n"
            "this.field3 = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, 10, MyType);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_custom_multi(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_custom(buffer, context, MyType);\n"
            "this.field3 = MessageBase._deserialize_custom(buffer, context, MyNewType);\n"
            "this.field4 = MessageBase._deserialize_custom(buffer, context, MyType);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_custom_multi_pkg(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_custom(buffer, context, MyType);\n"
            "this.field3 = MessageBase._deserialize_custom(buffer, context, MyNewType);\n"
            "this.field4 = MessageBase._deserialize_custom(buffer, context, AnotherNewType);\n"
            "this.field5 = MessageBase._deserialize_custom(buffer, context, MyType);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_custom_multi_pkg_dup(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'MyType', 'package': 'package'}]
        expected = (
            "this.field1 = MessageBase._deserialize_int32(buffer, context);\n"
            "this.field2 = MessageBase._deserialize_custom(buffer, context, MyType);\n"
            "this.field3 = MessageBase._deserialize_custom(buffer, context, MyNewType);\n"
            "this.field4 = MessageBase._deserialize_custom(buffer, context, AnotherNewType);\n"
            "this.field5 = MessageBase._deserialize_custom(buffer, context, AnotherNewType);\n"
            "this.field6 = MessageBase._deserialize_custom(buffer, context, MyType);"
        )
        add_flags_to_fields(fields)
        self.assertEqual(create_rixmsg_js_deserialize_function(fields), expected)

    def test_create_rixmsg_js_deserialize_failure(self):
        fields = [{'name': 'field1', 'type': 'int32'}, 
                  {'name': 'field2', 'type': 'MyType', 'package': 'package'},
                  {'name': 'field3', 'type': 'MyNewType', 'package': 'package'},
                  {'name': 'field4', 'type': 'AnotherNewType', 'package': 'new_package'},
                  {'name': 'field5', 'type': 'AnotherNewType', 'package': 'diff_package'},
                  {'name': 'field6', 'type': 'YetAnotherNewType'}, # No package defined for nonstandard type
                  {'name': 'field7', 'type': 'MyType', 'package': 'package'}]
        with self.assertRaises(ValueError):
            add_flags_to_fields(fields)
            create_rixmsg_js_deserialize_function(fields)

class TestCreateRixmsgJSFullTest(unittest.TestCase):
    def test_create_rixmsg_js_full(self):
        expected ="""import { MessageBase } from "../message_base.js";
import { OtherMessage } from "../example/OtherMessage.js";

export class ExampleMessage extends MessageBase {
    constructor() {
        super();
        this.number = 0;
        this.word = '';
        this.flag = false;
        this.object = new OtherMessage();
        this.array = [];
        this.static_array = Array.from({length: 3}, () => 0);
        this.array_of_words = [];
        this.static_array_of_words = Array.from({length: 3}, () => '');
        this.array_of_objects = [];
        this.static_array_of_objects = Array.from({length: 3}, () => new OtherMessage());
    }

    size() {
        let size = 0;
        size += MessageBase._size_uint32();
        size += MessageBase._size_string(this.word);
        size += MessageBase._size_bool();
        size += MessageBase._size_custom(this.object);
        size += MessageBase._size_vector_base(this.array, MessageBase._size_uint32());
        size += MessageBase._size_fixed_array_base(this.static_array, MessageBase._size_uint32());
        size += MessageBase._size_vector_string(this.array_of_words);
        size += MessageBase._size_fixed_array_string(this.static_array_of_words, 3);
        size += MessageBase._size_vector_custom(this.array_of_objects);
        size += MessageBase._size_fixed_array_custom(this.static_array_of_objects, 3);
        return size;
    }

    hash() {
        return [BigInt(0xi_am_thirty_two_), BigInt(0xcharacters_long!)];
    }

    serialize(buffer) {
        buffer = MessageBase._serialize_uint32(this.number, buffer);
        buffer = MessageBase._serialize_string(this.word, buffer);
        buffer = MessageBase._serialize_bool(this.flag, buffer);
        buffer = MessageBase._serialize_custom(this.object, buffer);
        buffer = MessageBase._serialize_vector(this.array, buffer, MessageBase._serialize_uint32);
        buffer = MessageBase._serialize_fixed_array(this.static_array, buffer, MessageBase._serialize_uint32, 3);
        buffer = MessageBase._serialize_vector(this.array_of_words, buffer, MessageBase._serialize_string);
        buffer = MessageBase._serialize_fixed_array(this.static_array_of_words, buffer, MessageBase._serialize_string, 3);
        buffer = MessageBase._serialize_vector(this.array_of_objects, buffer, MessageBase._serialize_custom);
        buffer = MessageBase._serialize_fixed_array(this.static_array_of_objects, buffer, MessageBase._serialize_custom, 3);
        return buffer;
    }

    deserialize(buffer, context) {
        this.number = MessageBase._deserialize_uint32(buffer, context);
        this.word = MessageBase._deserialize_string(buffer, context);
        this.flag = MessageBase._deserialize_bool(buffer, context);
        this.object = MessageBase._deserialize_custom(buffer, context, OtherMessage);
        this.array = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_uint32);
        this.static_array = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_uint32, 3);
        this.array_of_words = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string);
        this.static_array_of_words = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, 3);
        this.array_of_objects = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, OtherMessage);
        this.static_array_of_objects = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, 3, OtherMessage);
    }
}"""

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
        self.assertEqual(create_rixmsg_js(msg), expected)

if __name__ == "__main__":
    unittest.main()
