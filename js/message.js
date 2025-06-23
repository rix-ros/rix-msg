export class Message {
    // Methods for derived classes to override
    size() {
      return null;
    }
    serialize() {
      return null;
    }
    deserialize() {
      return null;
    }
    hash() {
      return null;
    }
  
    static #append_to_buffer(buffer, data) {
      const newBuffer = new ArrayBuffer(buffer.byteLength + data.byteLength);
      const newView = new Uint8Array(newBuffer);
      newView.set(new Uint8Array(buffer), 0);
      newView.set(new Uint8Array(data), buffer.byteLength);
      return newBuffer;
    }
  
    /**
     *
     * @param {number} value
     * @param {DataView} buffer
     * @returns {void}
     * @description Serialize number types into to a buffer. Appends bytes
     *              to the end of the buffer.
     */
  
    static _serialize_int32(value, buffer) {
      if (typeof value == 'string') {
          value = parseInt(value, 10);
      }
      const data = new ArrayBuffer(4);
      const view = new DataView(data);
      view.setInt32(0, value, true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_uint32(value, buffer) {
      if (typeof value == 'string') {
          value = parseInt(value, 10);
      }
      const data = new ArrayBuffer(4);
      const view = new DataView(data);
      view.setUint32(0, value, true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_int16(value, buffer) {
      if (typeof value == 'string') {
          value = parseInt(value, 10);
      }
      const data = new ArrayBuffer(2);
      const view = new DataView(data);
      view.setInt16(0, value, true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_uint16(value, buffer) {
      if (typeof value == 'string') {
          value = parseInt(value, 10);
      }
      const data = new ArrayBuffer(2);
      const view = new DataView(data);
      view.setUint16(0, value, true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_int8(value, buffer) {
      if (typeof value == 'string') {
          value = parseInt(value, 10);
      }
      const data = new ArrayBuffer(1);
      const view = new DataView(data);
      view.setInt8(0, value);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_uint8(value, buffer) {
      if (typeof value == 'string') {
          value = parseInt(value, 10);
      }
      const data = new ArrayBuffer(1);
      const view = new DataView(data);
      view.setUint8(0, value);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_char(value, buffer) {
      if (typeof value == 'string') {
          value = value.charAt(0); // Ensure it's a single character
      }
      const data = new ArrayBuffer(1);
      const view = new DataView(data);
      view.setInt8(0, value);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_bool(value, buffer) {
      if (typeof value == 'string') {
          value = value.toLowerCase() === 'true'; // Convert string to boolean
      }
      const data = new ArrayBuffer(1);
      const view = new DataView(data);
      view.setUint8(0, value ? 1 : 0);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_float(value, buffer) {
      if (typeof value == 'string') {
          value = parseFloat(value); // Convert string to float
      }
      const data = new ArrayBuffer(4);
      const view = new DataView(data);
      view.setFloat32(0, value, true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_double(value, buffer) {
      if (typeof value == 'string') {
          value = parseFloat(value); // Convert string to double
      }
      const data = new ArrayBuffer(8);
      const view = new DataView(data);
      view.setFloat64(0, value, true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_int64(value, buffer) {
      const data = new ArrayBuffer(8);
      const view = new DataView(data);
      view.setBigInt64(0, BigInt(value), true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_uint64(value, buffer) {
      const data = new ArrayBuffer(8);
      const view = new DataView(data);
      view.setBigUint64(0, BigInt(value), true);
      return Message.#append_to_buffer(buffer, data);
    }
  
    static _serialize_string(value, buffer) {
      const encoder = new TextEncoder();
      const bytes = encoder.encode(value);
      const length = bytes.byteLength;
      let data = Message._serialize_uint32(length, buffer);
      data = Message.#append_to_buffer(data, bytes);
      return data;
    }
  
    static _serialize_message(value, buffer) {
      buffer = value.serialize(buffer);
      return buffer;
    }
  
    // Equivalent to std::vector<T> in C++
    static _serialize_vector(value, buffer, serialize) {
      buffer = Message._serialize_uint32(value.length, buffer);
      value.forEach((element) => {
        buffer = serialize(element, buffer);
      });
      return buffer;
    }
  
    // Equivalent to std::array<T, N> in C++
    static _serialize_array(value, buffer, serialize, size) {
      for (let i = 0; i < size; i++) {
        buffer = serialize(value[i], buffer);
      }
      return buffer;
    }
  
    // Equivalent to std::map<K, V> in C++
    static _serialize_map(value, buffer, serialize_key, serialize_value) {
      buffer = Message._serialize_vector(Object.keys(value), buffer, serialize_key);
      buffer = Message._serialize_vector(Object.values(value), buffer, serialize_value);
      return buffer;
    }
  
    /**
     *
     * @param {DataView} buffer
     * @param {object} context
     * @returns {number}
     * @description Deserialize bytes at the offset into a number type. Increments
     *              the offset member of context by the number of bytes read.
     */
  
    static _deserialize_int32(view, context) {
      let val = view.getInt32(context.offset, true);
      context.offset += 4;
      return val;
    }
  
    static _deserialize_uint32(view, context) {
      let val = view.getUint32(context.offset, true);
      context.offset += 4;
      return val;
    }
  
    static _deserialize_int16(view, context) {
      let val = view.getInt16(context.offset, true);
      context.offset += 2;
      return val;
    }
  
    static _deserialize_uint16(view, context) {
      let val = view.getUint16(context.offset, true);
      context.offset += 2;
      return val;
    }
  
    static _deserialize_int8(view, context) {
      let val = view.getInt8(context.offset);
      context.offset += 1;
      return val;
    }
  
    static _deserialize_uint8(view, context) {
      let val = view.getUint8(context.offset);
      context.offset += 1;
      return val;
    }
  
    static _deserialize_char(view, context) {
      let val = String.fromCharCode(view.getInt8(context.offset));
      context.offset += 1;
      return val;
    }
  
    static _deserialize_bool(view, context) {
      let val = view.getUint8(context.offset) === 1;
      context.offset += 1;
      return val;
    }
  
    static _deserialize_float(view, context) {
      let val = view.getFloat32(context.offset, true);
      context.offset += 4;
      return val;
    }
  
    static _deserialize_double(view, context) {
      let val = view.getFloat64(context.offset, true);
      context.offset += 8;
      return val;
    }
  
    static _deserialize_int64(view, context) {
      let val = Number(view.getBigInt64(context.offset, true));
      context.offset += 8;
      return val;
    }
  
    static _deserialize_uint64(view, context) {
      let val = Number(view.getBigUint64(context.offset, true));
      context.offset += 8;
      return val;
    }
  
    static _deserialize_string(view, context) {
      const length = Message._deserialize_uint32(view, context);
      const bytes = view.buffer.slice(context.offset, context.offset + length);
      const decoder = new TextDecoder();
      const str = decoder.decode(bytes);
      context.offset += length;
      return str;
    }
  
    static _deserialize_message(view, context, obj_type) {
      const obj = new obj_type();
      obj.deserialize(view, context);
      return obj;
    }
  
    static _deserialize_vector(view, context, deserialize, obj_type) {
      const length = Message._deserialize_uint32(view, context);
      const vector = [];
      for (let i = 0; i < length; i++) {
        vector.push(deserialize(view, context, obj_type));
      }
      return vector;
    }
  
    static _deserialize_array(view, context, deserialize, size, obj_type) {
      const array = [];
      for (let i = 0; i < size; i++) {
        array.push(deserialize(view, context, obj_type));
      }
      return array;
    }
  
    static _deserialize_map(
      view,
      context,
      deserialize_key,
      deserialize_value,
      obj_type
    ) {
      const keys = Message._deserialize_vector(view, context, deserialize_key);
      const values = Message._deserialize_vector(
        view,
        context,
        deserialize_value,
        obj_type
      );
      return Object.fromEntries(keys.map((key, index) => [key, values[index]]));
    }
  
    /**
     * Size methods
     */
  
    static _size_int32() {
      return 4;
    }
    static _size_uint32() {
      return 4;
    }
    static _size_int16() {
      return 2;
    }
    static _size_uint16() {
      return 2;
    }
    static _size_int8() {
      return 1;
    }
    static _size_uint8() {
      return 1;
    }
    static _size_char() {
      return 1;
    }
    static _size_bool() {
      return 1;
    }
    static _size_float() {
      return 4;
    }
    static _size_double() {
      return 8;
    }
    static _size_int64() {
      return 8;
    }
    static _size_uint64() {
      return 8;
    }
  
    static _size_string(value) {
      return 4 + value.length;
    }
  
    static _size_message(value) {
      return value.size();
    }
  
    static _size_vector_number(value, size) {
      return 4 + value.length * size;
    }
  
    static _size_vector_string(value) {
      return 4 + value.reduce((acc, str) => acc + 4 + str.length, 0);
    }
  
    static _size_vector_message(value) {
      return 4 + value.reduce((acc, obj) => acc + obj.size(), 0);
    }
  
    static _size_array_number(value, size) {
      return value.length * size;
    }
  
    static _size_array_string(value, size) {
      return value.slice(0, size).reduce((acc, str) => acc + str.length, 0);
    }
  
    static _size_array_message(value, size) {
      return value.slice(0, size).reduce((acc, obj) => acc + obj.size(), 0);
    }
  
    static _size_map_number_to_number(value, key_size, value_size) {
      return 8 + Object.keys(value).length * (key_size + value_size);
    }
  
    static _size_map_number_to_string(value, key_size) {
      let keys = Object.keys(value);
      return (
        8 +
        keys.length * key_size +
        keys.reduce((acc, str) => acc + 4 + value[str].length, 0)
      );
    }
  
    static _size_map_number_to_message(value, key_size) {
      let keys = Object.keys(value);
      return (
        8 +
        keys.length * key_size +
        keys.reduce((acc, str) => acc + value[str].size(), 0)
      );
    }
  
    static _size_map_string_to_number(value, value_size) {
      let keys = Object.keys(value);
      return (
        8 +
        keys.reduce((acc, str) => acc + 4 + str.length, 0) +
        keys.length * value_size
      );
    }
  
    static _size_map_string_to_string(value) {
      let keys = Object.keys(value);
      return (
        8 +
        keys.reduce((acc, str) => acc + 4 + str.length, 0) +
        keys.reduce((acc, str) => acc + 4 + value[str].length, 0)
      );
    }
  
    static _size_map_string_to_message(value) {
      let keys = Object.keys(value);
      return (
        8 +
        keys.reduce((acc, str) => acc + 4 + str.length, 0) +
        keys.reduce((acc, str) => acc + value[str].size(), 0)
      );
    }
  }
  