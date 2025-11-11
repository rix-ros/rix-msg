# RIX-MSG: Robotics Interprocess eXchange Message Library

## Fast, Modular Message Serialization for Robotics

**RIX-MSG** is a high-performance, cross-language message definition and serialization library for robotics and distributed systems. It provides a robust foundation for defining, generating, and serializing messages in C++ and Python—empowering you to build scalable, reliable robot software architectures.

- 🌐 **Multi-Language:** Automatically generates C++ and Python implementations from a single message definition.
- ⚡ **Zero-Copy Serialization:** Optimized for low-latency communication with vectored I/O support.
- 🧩 **Flexible Schema:** Supports arithmetic types, strings, arrays, vectors, and nested messages for complex data structures.
- 🔒 **Type-Safe:** Enforces strict type checking and schema validation across all supported languages.
- 📝 **Human-Readable Definitions:** Message formats are defined in clear, versioned JSON files.

RIX-MSG makes it easy to define and use complex message types, offering a clean schema and powerful tools for code generation and validation.

---

## Get Started: Define and Serialize Messages with RIX-MSG

### Installation

Run the install script to set up RIX-MSG and its dependencies:

```bash
bash install.sh
```

This will:
- Build and install the `rixmsg` CLI tool to `$HOME/.rix/bin/rixmsg`
- Generate default message serialization files for C++ and Python in:
  - `$HOME/.rix/include/rix/msg/`
  - `$HOME/.rix/python/rixmsg/`

---

## Environment Setup

Before using the `rixmsg` CLI or generated code, ensure your environment is set up:

```bash
source ~/.rix/setup.bash
```

You can add this to your `.bashrc` for convenience:

```bash
echo 'source ~/.rix/setup.bash' >> ~/.bashrc
```

---

## Usage

The `rixmsg` executable provides several functions:

- `rixmsg packages` — List all installed message packages.
- `rixmsg package <package>` — List all message types in a package.
- `rixmsg show <package>/<name>` — Print the JSON definition of a message.
- `rixmsg create <path>` — Generate implementation files from message definition files in `<path>`.
- `rixmsg index` — Index all message definitions by hash.
- `rixmsg validate <path>` — Validate a message definition file against the schema.

Example usage:

```bash
rixmsg packages
rixmsg package geometry
rixmsg show std_msgs/Header
rixmsg create defs/example_msgs/
rixmsg validate defs/geometry_msgs/Point.json
```

---

## Message Definition Format

Message definitions use a simple JSON schema. Supported types include:

- Base types: `char`, `int8`, `int16`, `int32`, `int64`, `uint8`, `uint16`, `uint32`, `uint64`, `float`, `double`, `bool`, `string`, `pointer`
- Arrays: `type[]` (dynamic), `type[N]` (fixed-size)
- Nested messages: `{ "type": "<name>", "package": "<package>" }`

Example (`std_msgs/Header.json`):

```json
{
  "version": "1.0.0",
  "package": "std_msgs",
  "name": "Header",
  "fields": [
    { "name": "seq", "type": "uint32" },
    { "name": "stamp", "type": "Time", "package": "std_msgs" },
    { "name": "frame_id", "type": "string" }
  ]
}
```

---

## Code Generation

After defining your messages, generate code for all supported languages:

```bash
rixmsg create defs/example_msgs/
```

Generated files will be placed in:

- C++: `~/.rix/include/rix/msg/<package>/<Message>.hpp`
- Python: `~/.rix/python/rixmsg/rixmsg/<package>/<Message>.py`

---

## C++ Example

Include generated message headers in your C++ project:

```cpp
#include "rix/std_msgs/Header.hpp"

using rix::std_msgs::Header;

int main() {
    Header msg;
    msg.seq = 42;
    msg.frame_id = "robot_1";
    return 0;
}
```

---

## Python Example

Import generated message classes in Python:

```python
from rix.std_msgs import Header

msg = Header()
msg.seq = 42
msg.frame_id = "robot_1"
```

---

## More Information

- [RIX C++ Documentation](https://github.com/rix-ros/rix-cpp)
- [RIX Python Documentation](https://github.com/rix-ros/rix-py)

---

## License

See [LICENSE.md](LICENSE.md) for details.

---