import { Header } from 'rixmsg/standard/Header.js';

function print_header(msg) {
    console.log('seq:', msg.seq);
    console.log('stamp.sec:', msg.stamp.sec);
    console.log('stamp.nsec:', msg.stamp.nsec);
    console.log('frame_id:', msg.frame_id);
}

var header = new Header();
header.seq = 0;
header.stamp.sec = 1234;
header.stamp.nsec = 5678;
header.frame_id = 'Hello, world!';

console.log("Original: ");
print_header(header);

let encoded = new ArrayBuffer();
encoded = header.serialize(encoded);

console.log("\nEncoded: ");
console.log(encoded);

let context = { offset: 0 };
let decoded = new Header();
let view = new DataView(encoded);
decoded.deserialize(view, context);

console.log("\nDecoded: ");
print_header(decoded);