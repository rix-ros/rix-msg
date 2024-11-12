/**
 * @description Read a 64-bit unsigned integer from a DataView
 * @param {DataView} view 
 * @param {number} offset
 * @param {boolean} littleEndian 
 * @returns {BigInt}
 */
function getUint64(view, offset, littleEndian) {
    let left, right;
    if (littleEndian) {
        left = view.getUint32(offset, true);
        right = view.getUint32(offset + 4, true);
    } else {
        left = view.getUint32(offset, false);
        right = view.getUint32(offset + 4, false);
    }
    return BigInt(left) + (BigInt(right) << BigInt(32));
}

/**
 * @description Read a 64-bit signed integer from a DataView
 * @param {DataView} view 
 * @param {number} offset 
 * @param {boolean} littleEndian 
 * @returns {BigInt}
 */
function getInt64(view, offset, littleEndian) {
    let left, right;
    if (littleEndian) {
        left = view.getUint32(offset, true);
        right = view.getInt32(offset + 4, true);
    } else {
        left = view.getInt32(offset, false);
        right = view.getUint32(offset + 4, false);
    }
    return BigInt(left) + (BigInt(right) << BigInt(32));
}

/**
 * @description Check if an object is a class
 * @param {any} func
 * @returns {boolean}
 */
function isClass(obj) {
    return typeof obj === 'function' && 
           typeof obj.prototype === 'object' && 
           obj.prototype !== null && 
           obj.prototype.constructor === obj;
}

/**
 * @description A class to represent a C structure
 */
export class Structure {
    #fields;
    #size;
    #packed;
    #view;

    /**
     * 
     * @param {Array} fields - An array of fields in the structure.
     * @param {boolean} packed - Whether the structure is packed or not. Default is false.
     * @param {*} buffer - An ArrayBuffer to use as the underlying data buffer. Default is null.
     */
    constructor(fields, packed=false, buffer=null) {
        // Set the fields
        this.#fields = fields;

        // Calculate the size of the structure
        this.#size = Structure.sizeof(this.#fields, packed);

        // Set the packed flag
        this.#packed = packed;

        // Create the buffer and view
        if (buffer) {
            if (buffer.byteLength < this.#size) {
                throw new Error('Buffer is too small! Expected ' + this.#size + ' bytes, got ' + buffer.byteLength + ' bytes.');
            }
            this.buffer = buffer;
        } else {
            this.buffer = new ArrayBuffer(this.#size);
        }
        this.#view = new DataView(this.buffer);
        
        // Define the fields as properties of this object
        this.#fields.forEach((field, index) => {
            field.offset = this.#calculateOffset(index);
            Object.defineProperty(this, field.name, {
                get: () => this.#getField(index),
                set: (value) => this.#setField(index, value)
            });
        });
    }

    /**
     * 
     * @param {string | function | Array<function>} format 
     * @returns {number} The size of the structure in bytes.
     */
    static alignof(format) {
        if (format instanceof Array) {
            // For an array, the alignment is the alignment of its elements
            return Structure.alignof(format[0]);
        } else if (isClass(format)) {
            // For a nested structure, the alignment is the maximum alignment of its fields
            return Math.max(...format.fields.map(field => Structure.alignof(field.format)));
        }
        // For a primitive type, the alignment is the same as the size
        return Structure.#getUnitSizeFromFormat(format);
    }

    /**
     * 
     * @param {Array<{name: string, format: string | function | Array<function>}>} fields 
     * @param {boolean} packed 
     * @returns {number} The size of the fields in bytes.
     */
    static sizeof(fields, packed=false) {
        let totalSize = 0;
        let max_align = 0;
        for (let i = 0; i < fields.length; i++) {

            let size;
            if (fields[i].format instanceof Array) {
                size = fields[i].format[0].size() * fields[i].format.length;
            } else if (isClass(fields[i].format)) {
                size = fields[i].format.size();
            } else {
                size = Structure.#getTotalSizeFromFormat(fields[i].format);
            }

            totalSize += size;

            // Add padding
            if (packed) {
                continue;
            }

            const alignment = Structure.alignof(fields[i].format);
            if (alignment > max_align) {
                max_align = alignment;
            }
            const padding = (alignment - (totalSize % alignment)) % alignment;
            totalSize += padding;
        }
        
        if (packed) {
            return totalSize;
        }

        // Add padding at the end of the structure to align the whole structure
        const padding = (max_align - (totalSize % max_align)) % max_align;
        totalSize += padding;

        return totalSize;
    }

    /**
     * 
     * @returns {number} The size of this structure in bytes.
     */
    size() {
        return this.#size;
    }

    /**
     * 
     * @returns {boolean} Whether the structure is packed or not.
     */
    isPacked() {
        return this.#packed;
    }

    /**
     * 
     * @param {number} index 
     * @returns {number} The byte offset of the field at the given index.
     */
    #calculateOffset(index) {
        let offset = 0;
        for (let i = 0; i < index; i++) {
            let size;
            if (this.#fields[i].format instanceof Array) {
                size = this.#fields[i].format[0].size() * this.#fields[i].format.length;
            } else if (isClass(this.#fields[i].format)) {
                size = this.#fields[i].format.size();
            } else {
                size = Structure.#getTotalSizeFromFormat(this.#fields[i].format);
            }
            offset += size;
            
            if (this.#packed) {
                continue;
            }

            // Add padding
            const alignment = Structure.alignof(this.#fields[i].format);
            const padding = (alignment - (offset % alignment)) % alignment;
            offset += padding;
        }

        if (this.#packed) {
            return offset;
        }

        // Add padding at the end of the structure to align the whole structure
        const alignment = Structure.alignof(this.#fields[index].format);
        const padding = (alignment - (offset % alignment)) % alignment;
        offset += padding;

        return offset;
    }

    /**
     * 
     * @param {string} format 
     * @returns {number} The unit size of the given format in bytes.
     */
    static #getUnitSizeFromFormat(format) {
        const match = format.match(/^(\d*)(.)/);
        const count = match[1] ? parseInt(match[1], 10) : 1;
        const type = match[2];
    
        let size;
        switch (type) {
            case 'c': // char
            case 'b': // signed char (int8_t)
            case 'B': // unsigned char (byte, uint8_t)
            case '?': // _Bool
                size = 1;
                break;
            case 'h': // short (int16_t)
            case 'H': // unsigned short (uint16_t)
                size = 2;
                break;
            case 'i': // int (int32_t)
            case 'I': // unsigned int (uint32_t)
            case 'l': // long (int32_t)
            case 'L': // unsigned long (uint32_t)
            case 'f': // float
                size = 4;
                break;
            case 'd': // double
            case 'q': // long long (int64_t)
            case 'Q': // unsigned long long (uint64_t)
                size = 8;
                break;
            default:
                throw new Error(`Unsupported format: ${format}`);
        }
    
        return size;
    }

    /**
     * 
     * @param {string} format 
     * @returns {number} The total size of the given format in bytes.
     */
    static #getTotalSizeFromFormat(format) {
        const match = format.match(/^(\d*)(.)/);
        const count = match[1] ? parseInt(match[1], 10) : 1;
        const type = match[2];
    
        let size;
        switch (type) {
            case 'c': // char
            case 'b': // signed char (int8_t)
            case 'B': // unsigned char (byte, uint8_t)
            case '?': // _Bool
                size = 1;
                break;
            case 'h': // short (int16_t)
            case 'H': // unsigned short (uint16_t)
                size = 2;
                break;
            case 'i': // int (int32_t)
            case 'I': // unsigned int (uint32_t)
            case 'l': // long (int32_t)
            case 'L': // unsigned long (uint32_t)
            case 'f': // float
                size = 4;
                break;
            case 'd': // double
            case 'q': // long long (int64_t)
            case 'Q': // unsigned long long (uint64_t)
                size = 8;
                break;
            default:
                throw new Error(`Unsupported format: ${format}`);
        }
    
        return size * count;
    }

    #getField(index) {
        const field = this.#fields[index];
        const offset = field.offset;
        if (field.format instanceof Array) {
            return field.format;
        }
        else if (isClass(field.format)) {
            let tmp = this.buffer.slice(offset, offset + field.format.size())
            return new field.format(tmp);
        }

        const match = field.format.match(/^(\d*)(.)/);
        const count = match[1] ? parseInt(match[1], 10) : 1;
        const type = match[2];

        switch (type) {
            case 'b':
                return (count > 1) ? new Int8Array(this.buffer, offset, count) : this.#view.getInt8(offset);
            case 'B':
                return (count > 1) ? new Uint8Array(this.buffer, offset, count) : this.#view.getUint8(offset);
            case '?':
                return (count > 1) ? new Uint8Array(this.buffer, offset, count).map((value) => value !== 0) : this.#view.getUint8(offset) !== 0;
            case 'h':
                return (count > 1) ? new Int16Array(this.buffer, offset, count) : this.#view.getInt16(offset, true);
            case 'H':
                return (count > 1) ? new Uint16Array(this.buffer, offset, count) : this.#view.getUint16(offset, true);
            case 'l':
            case 'i':
                return (count > 1) ? new Int32Array(this.buffer, offset, count) : this.#view.getInt32(offset, true);
            case 'L':
            case 'I':
                return (count > 1) ? new Uint32Array(this.buffer, offset, count) : this.#view.getUint32(offset, true);
            case 'f':
                return (count > 1) ? new Float32Array(this.buffer, offset, count) : this.#view.getFloat32(offset, true);
            case 'd':
                return (count > 1) ? new Float64Array(this.buffer, offset, count) : this.#view.getFloat64(offset, true);
            case 'q':
                return (count > 1) ? new BigInt64Array(this.buffer, offset, count) : getInt64(this.#view, offset, true);
            case 'Q':
                return (count > 1) ? new BigUint64Array(this.buffer, offset, count) : getUint64(this.#view, offset, true);
            case 'c':
                return (count > 1) ? new TextDecoder().decode(new Uint8Array(this.buffer, offset, count)).split('\0')[0] : this.#view.getInt8(offset);
            default:
                throw new Error(`Unsupported format: ${type}`);
        }
    }

    #setField(index, value) {
        const field = this.#fields[index];
        const offset = field.offset;

        if (isClass(field.format)) {
            const destination = new Uint8Array(this.buffer);
            const source = new Uint8Array(value.buffer);
            destination.set(source, offset);
            return;
        }

        const match = field.format.match(/^(\d*)(.)/);
        const count = match[1] ? parseInt(match[1], 10) : 1;
        const type = match[2];

        if (count == 1) {
            switch (type) {
                case 'b':
                    this.#view.setInt8(offset, value);
                    break;
                case 'B':
                    this.#view.setUint8(offset, value);
                    break;
                case '?':
                    this.#view.setUint8(offset, value ? 1 : 0);
                    break;
                case 'h':
                    this.#view.setInt16(offset, value, true);
                    break;
                case 'H':
                    this.#view.setUint16(offset, value, true);
                    break;
                case 'l':
                case 'i':
                    this.#view.setInt32(offset, value, true);
                    break;
                case 'L':
                case 'I':
                    this.#view.setUint32(offset, value, true);
                    break;
                case 'f':
                    this.#view.setFloat32(offset, value, true);
                    break;
                case 'd':
                    this.#view.setFloat64(offset, value, true);
                    break;
                case 'q':
                    this.#view.setBigInt64(offset, BigInt(value), true);
                    break;
                case 'Q':
                    this.#view.setBigUint64(offset, BigInt(value), true);
                    break;
                case 'c':
                    this.#view.setInt8(offset, value.charCodeAt(0));
                    break;
                default:
                    throw new Error(`Unsupported format: ${type}`);
            }
        } else {
            switch (type) {
                case 'b':
                    new Int8Array(this.buffer, offset, count).set(value);
                    break;
                case 'B':
                    new Uint8Array(this.buffer, offset, count).set(value);
                    break;
                case '?':
                    new Uint8Array(this.buffer, offset, count).set(value.map((v) => v ? 1 : 0));
                    break;
                case 'h':
                    new Int16Array(this.buffer, offset, count).set(value);
                    break;
                case 'H':
                    new Uint16Array(this.buffer, offset, count).set(value);
                    break;
                case 'l':
                case 'i':
                    new Int32Array(this.buffer, offset, count).set(value);
                    break;
                case 'L':
                case 'I':
                    new Uint32Array(this.buffer, offset, count).set(value);
                    break;
                case 'f':
                    new Float32Array(this.buffer, offset, count).set(value);
                    break;
                case 'd':
                    new Float64Array(this.buffer, offset, count).set(value);
                    break;
                case 'q':
                    new BigInt64Array(this.buffer, offset, count).set(value.map((v) => BigInt(v)));
                    break;
                case 'Q':
                    new BigUint64Array(this.buffer, offset, count).set(value.map((v) => BigInt(v)));
                    break;
                case 'c':
                    new Uint8Array(this.buffer, offset, count).set(new TextEncoder().encode(value));
                    break;
                default:
                    throw new Error(`Unsupported format: ${type}`);
            }
        }
    }
}