import { OtherMessage } from "rixmsg/example/OtherMessage.js";
import { ExampleMessage } from "rixmsg/example/ExampleMessage.js";

function print_other(msg) {
    console.log('number:', msg.number);
    console.log('word:', msg.word);
}

function print_example(msg) {
    console.log('number:', msg.number);
    console.log('word:', msg.word);
    console.log('flag:', msg.flag);
    console.log('object:');
    print_other(msg.object);
    console.log('array:', msg.array);
    console.log('static_array:', msg.static_array);
    console.log('array_of_words:', msg.array_of_words);
    console.log('static_array_of_words:', msg.static_array_of_words);
    console.log('array_of_objects:', msg.array_of_objects);
    console.log('static_array_of_objects:', msg.static_array_of_objects);
}

var other = new OtherMessage();
other.number = 1234;
other.flag = true;

var example = new ExampleMessage();
example.number = 1234;
example.word = 'Hello, world!';
example.flag = true;
example.object = other;
example.array.push(1);
example.array.push(2);
example.array.push(3);
example.static_array[0] = 4;
example.static_array[1] = 5;
example.static_array[2] = 6;
example.array_of_words.push('one');
example.array_of_words.push('two');
example.array_of_words.push('three');
example.static_array_of_words[0] = 'four';
example.static_array_of_words[1] = 'five';
example.static_array_of_words[2] = 'six';
example.array_of_objects.push(other);
example.array_of_objects.push(other);
example.array_of_objects.push(other);
example.static_array_of_objects[0].number = 7;
example.static_array_of_objects[0].flag = false;
example.static_array_of_objects[1].number = 8;
example.static_array_of_objects[1].flag = true;
example.static_array_of_objects[2].number = 9;
example.static_array_of_objects[2].flag = false;

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