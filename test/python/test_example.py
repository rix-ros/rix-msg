from rixmsg.example.OtherMessage import OtherMessage
from rixmsg.example.ExampleMessage import ExampleMessage

from math import isclose

def print_other(msg):
    print("num:", msg.num)
    print("flag:", msg.flag)


def print_example(msg):
    print("num:", msg.num)
    print("str:", msg.str)
    print("flag:", msg.flag)
    print("msg:")
    print_other(msg.msg)
    print("num_vec:", msg.num_vec)
    print("num_arr:", msg.num_arr)
    print("str_vec:", msg.str_vec)
    print("str_arr:", msg.str_arr)
    print("msg_vec:", msg.msg_vec)
    print("msg_arr:", msg.msg_arr)
    print("num_to_num_map:", msg.num_to_num_map)
    print("str_to_num_map:", msg.str_to_num_map)
    print("num_to_msg_map:", msg.num_to_msg_map)
    print("num_to_str_map:", msg.num_to_str_map)
    print("str_to_str_map:", msg.str_to_str_map)
    print("str_to_msg_map:", msg.str_to_msg_map)


other = OtherMessage()
other.num = 12.34
other.flag = True

example = ExampleMessage()
example.num = 1234
example.str = "Hello, world!"
example.flag = True
example.msg = other
example.num_vec.append(1)
example.num_vec.append(2)
example.num_vec.append(3)
example.num_arr[0] = 4.5
example.num_arr[1] = 5.6
example.num_arr[2] = 6.7
example.str_vec.append("one")
example.str_vec.append("two")
example.str_vec.append("three")
example.str_arr[0] = "four"
example.str_arr[1] = "five"
example.str_arr[2] = "six"
example.msg_vec.append(other)
example.msg_vec.append(other)
example.msg_vec.append(other)
example.msg_arr[0].num = 7.8
example.msg_arr[0].flag = False
example.msg_arr[1].num = 8.9
example.msg_arr[1].flag = True
example.msg_arr[2].num = 9.0
example.msg_arr[2].flag = False
example.num_to_num_map[0] = 1
example.num_to_num_map[1] = 2
example.num_to_num_map[2] = 3
example.str_to_num_map["str0"] = 1
example.str_to_num_map["str1"] = 2
example.str_to_num_map["str2"] = 3
example.num_to_msg_map[0] = other
example.num_to_msg_map[1] = other
example.num_to_msg_map[2] = other
example.num_to_str_map[0] = "str0"
example.num_to_str_map[1] = "str1"
example.num_to_str_map[2] = "str2"
example.str_to_str_map["str0"] = "str1"
example.str_to_str_map["str1"] = "str2"
example.str_to_str_map["str2"] = "str3"
example.str_to_msg_map["str0"] = other
example.str_to_msg_map["str1"] = other
example.str_to_msg_map["str2"] = other

print("Original: ")
print_example(example)

encoded = bytearray()
example.serialize(encoded)

print("\nEncoded: ")
print(encoded)

context = {"offset": 0}
decoded = ExampleMessage()
decoded.deserialize(encoded, context)

print("\nDecoded: ")
print_example(decoded)

assert example.num == decoded.num
assert example.str == decoded.str
assert example.flag == decoded.flag
assert isclose(example.msg.num, decoded.msg.num)
assert example.msg.flag == decoded.msg.flag
assert example.num_vec == decoded.num_vec
for i in range(len(example.num_arr)):
    assert isclose(example.num_arr[i], decoded.num_arr[i], rel_tol=1e-5)
assert example.str_vec == decoded.str_vec
assert example.str_arr == decoded.str_arr
assert len(example.msg_vec) == len(decoded.msg_vec)
assert len(example.msg_arr) == len(decoded.msg_arr)
for i in range(len(example.msg_vec)):
    assert isclose(example.msg_vec[i].num, decoded.msg_vec[i].num, rel_tol=1e-5)
    assert example.msg_vec[i].flag == decoded.msg_vec[i].flag
for i in range(len(example.msg_arr)):
    assert (
        isclose(example.msg_arr[i].num, decoded.msg_arr[i].num, rel_tol=1e-5)
    )
    assert (
        isclose(example.msg_arr[i].num, decoded.msg_arr[i].num, rel_tol=1e-5)
    )
print("Success!")
