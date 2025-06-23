import { OtherMessage } from "rixmsg/example/OtherMessage.js";
import { ExampleMessage } from "rixmsg/example/ExampleMessage.js";

function print_other(msg) {
    console.log('num:', msg.num);
    console.log('flag:', msg.flag);
}

function print_example(msg) {
    console.log('num:', msg.num);
    console.log('str:', msg.str);
    console.log('flag:', msg.flag);
    console.log('msg:');
    print_other(msg.msg);
    console.log('num_vec:', msg.num_vec);
    console.log('num_arr:', msg.num_arr);
    console.log('str_vec:', msg.str_vec);
    console.log('str_arr:', msg.str_arr);
    console.log('msg_vec:', msg.msg_vec);
    console.log('msg_arr:', msg.msg_arr);
    console.log("num_to_num_map:", msg.num_to_num_map);
    console.log("str_to_num_map:", msg.str_to_num_map);
    console.log("num_to_msg_map:", msg.num_to_msg_map);
    console.log("num_to_str_map:", msg.num_to_str_map);
    console.log("str_to_str_map:", msg.str_to_str_map);
    console.log("str_to_msg_map:", msg.str_to_msg_map);
}

var other = new OtherMessage();
other.num = 12.34;
other.flag = true;

var example = new ExampleMessage();
example.num = 1234;
example.str = 'Hello, world!';
example.flag = true;
example.msg = other;
example.num_vec.push(1.2);
example.num_vec.push(2.3);
example.num_vec.push(3.4);
example.num_arr[0] = 4.5;
example.num_arr[1] = 5.6;
example.num_arr[2] = 6.7;
example.str_vec.push('one');
example.str_vec.push('two');
example.str_vec.push('three');
example.str_arr[0] = 'four';
example.str_arr[1] = 'five';
example.str_arr[2] = 'six';
example.msg_vec.push(other);
example.msg_vec.push(other);
example.msg_vec.push(other);
example.msg_arr[0].num = 7.8;
example.msg_arr[0].flag = false;
example.msg_arr[1].num = 8.9;
example.msg_arr[1].flag = true;
example.msg_arr[2].num = 9.0;
example.msg_arr[2].flag = false;
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

console.log("Original: ");
print_example(example);

let encoded = new ArrayBuffer();
encoded = example.serialize(encoded);

console.log("\nEncoded: ");
// Log entire buffer
console.log(encoded);

let context = { offset: 0 };
let decoded = new ExampleMessage();
let view = new DataView(encoded);
decoded.deserialize(view, context);

console.log("\nDecoded: ");
print_example(decoded);