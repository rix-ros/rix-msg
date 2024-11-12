import { Header } from 'rix-msg/standard/header.js';

function print_header(msg) {
    console.log('seq:', msg.seq);
    console.log('stamp.sec:', msg.stamp.sec);
    console.log('stamp.nsec:', msg.stamp.nsec);
    console.log('frame_id:', msg.frame_id);
}

const msg = new Header();
msg.seq = 0;
msg.stamp.sec = 1234;
msg.stamp.nsec = 5678;
msg.frame_id = 'Hello, world!';

console.log("Original: ");
print_header(msg);

const msg2 = Header.decode(msg.encode());

console.log("Decoded: ");
print_header(msg2);
