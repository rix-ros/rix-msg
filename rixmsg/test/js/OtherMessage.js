import { MessageBase } from "../message_base.js";

export class OtherMessage extends MessageBase {
    constructor() {
        super();
        this.number = 0.0;
        this.flag = false;
    }

    size() {
        let size = 0;
        size += MessageBase._size_double();
        size += MessageBase._size_bool();
        return size;
    }

    hash() {
        return [BigInt(0x309c08666f8285b7), BigInt(0xe5ca3cc56cb0fbec)];
    }

    serialize(buffer) {
        buffer = MessageBase._serialize_double(this.number, buffer);
        buffer = MessageBase._serialize_bool(this.flag, buffer);
        return buffer;
    }

    deserialize(buffer, context) {
        this.number = MessageBase._deserialize_double(buffer, context);
        this.flag = MessageBase._deserialize_bool(buffer, context);
    }
}