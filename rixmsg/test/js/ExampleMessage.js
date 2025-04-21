import { MessageBase } from "../message_base.js";
import { OtherMessage } from "../example/OtherMessage.js";

export class ExampleMessage extends MessageBase {
    constructor() {
        super();
        this.number = 0;
        this.word = '';
        this.flag = false;
        this.object = new OtherMessage();
        this.array = [];
        this.static_array = Array.from({length: 3}, () => 0.0);
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
        size += MessageBase._size_vector_base(this.array, MessageBase._size_float());
        size += MessageBase._size_fixed_array_base(this.static_array, MessageBase._size_float());
        size += MessageBase._size_vector_string(this.array_of_words);
        size += MessageBase._size_fixed_array_string(this.static_array_of_words, 3);
        size += MessageBase._size_vector_custom(this.array_of_objects);
        size += MessageBase._size_fixed_array_custom(this.static_array_of_objects, 3);
        return size;
    }

    hash() {
        return [BigInt(0xd3b5843a81f422d9), BigInt(0x316fab08fd66c0d5)];
    }

    serialize(buffer) {
        buffer = MessageBase._serialize_uint32(this.number, buffer);
        buffer = MessageBase._serialize_string(this.word, buffer);
        buffer = MessageBase._serialize_bool(this.flag, buffer);
        buffer = MessageBase._serialize_custom(this.object, buffer);
        buffer = MessageBase._serialize_vector(this.array, buffer, MessageBase._serialize_float);
        buffer = MessageBase._serialize_fixed_array(this.static_array, buffer, MessageBase._serialize_float, 3);
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
        this.array = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_float);
        this.static_array = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_float, 3);
        this.array_of_words = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_string);
        this.static_array_of_words = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_string, 3);
        this.array_of_objects = MessageBase._deserialize_vector(buffer, context, MessageBase._deserialize_custom, OtherMessage);
        this.static_array_of_objects = MessageBase._deserialize_fixed_array(buffer, context, MessageBase._deserialize_custom, 3, OtherMessage);
    }
}