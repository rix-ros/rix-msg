import { MessageBase } from "rixmsg/message_base.js";

export class OtherMessage extends MessageBase {
    constructor() {
        super();
        this.number = 0;
        this.flag = false;
    }

    size() {
        let size = 0;
        size += MessageBase._size_int16();
        size += MessageBase._size_bool();
        return size;
    }

    hash() {
        return [BigInt(0x3ca3b57c64691de0), BigInt(0x33fa64726faff850)];
    }

    serialize(buffer) {
        buffer = MessageBase._serialize_int16(this.number, buffer);
        buffer = MessageBase._serialize_bool(this.flag, buffer);
        return buffer;
    }

    deserialize(buffer, context) {
        this.number = MessageBase._deserialize_int16(buffer, context);
        this.flag = MessageBase._deserialize_bool(buffer, context);
    }
}