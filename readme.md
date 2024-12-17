# RIX-MSG

The `rix-msg` library contains definitions for the base message types used in `rix` and the `rixmsg` executable.

## Install

To install `rixmsg`, run the following commands:

```bash
chmod +x install.sh
./install.sh
```

This will install the `rixmsg` executable into `/usr/local/bin` and create the default message serialization files for C++, Python, and JavaScript in `~/.rix/include/rix/msg/`, `~/.rix/python/rixmsg/`, and `~/.rix/node_modules/rixmsg/` respectively. 

## Usage

The `rixmsg` executable uses five functions: `packages`,`show`, `package`, and `create`.
* `rixmsg packages`: List all of the `rixmsg` packages that are installed.
* `rixmsg package <package>`: List the names of each message in a package.
* `rixmsg show <package>/<name>`: Print the `.rixmsg` file of the specified message.
* `rixmsg create <path>`: Generate implementation files from `.rixmsg` files and install them globally. `<path>` should specify a path to a directory containing `.rixmsg` files.

After the default installation, `rixmsg packages` should output:
```txt
component
standard
sensor
geometry
```

Additionally `rixmsg package geometry` should output:
```txt
TF
Pose
Vector3
Vector3Stamped
PointStamped
Twist
TwistStamped
QuaternionStamped
Quaternion
Transform
PoseStamped
Point
TransformStamped
```

RIX packages are designed to be easy to include in your existing CMake projects. For example:
```cmake
cmake_minimum_required(VERSION 3.10)
project(msgs_test)
set(CMAKE_CXX_STANDARD 20)
list(APPEND CMAKE_PREFIX_PATH "~/.rix")

find_package(rixmsg REQUIRED)

add_executable(test test.cpp)
```

## Tests
`rix-msg` supports three languages: C++, Python, and JavaScript. There are tests for each of these languages in the `tests` directory.

C++
```bash
mkdir tests/cpp/build
cd tests/cpp/build
cmake ..
make
./test
```
Python
```bash
cd tests/python/
python3 -m venv venv
source venv/bin/activate
pip install ~/.rix/python/rixmsg/
python3 test.py
```
JavaScript
```bash
cd tests/js/
npm link ~/.rix/node_modules/rixmsg/
npm install
node test.js
```
Note: When running the Python or JavaScript examples, there may be an error with the permissions to edit the `~/.rix/` directory. To fix this, run:
```bash
sudo chown -R [USER] ~/.rix/
```

## The `.rixmsg` Format

Every `.rixmsg` must have the following format:
```txt
version: <version>;
package: <package>;

<msg type> {
    <type> <name>;
    <package name>::<msg type> <name>;
    <type> <name>[<size>];
}
```

An example of this format is `standard/header`:
```txt
version: 1.0.0;
package: standard;

Header {
    uint32_t seq;
    standard::Time stamp;
    char frameID[32];
}
```

To define a type with variable size, use the template argument.
```txt
version: <version>;
package: <package>;

template: <template type> <template name>[, ...]
<msg type> {
    <type> <name>[<template name>];
}
```
An example of this format is `standard/string`
```txt
version: 1.0.0;
package: standard;

template: uint32_t N;
String {
    char data[N];
}
```
Supported types include: `char`, `int8_t`, `int16_t`, `int32_t`, `int64_t`, `uint8_t`, `uint16_t`, `uint32_t`, `uint64_t`, `float`, `double`, and `bool`. You can also nest message types by specifying the package and name of the message as demonstrated above in `standard/header`.

The `.rixmsg` format requires all messages to be statically allocated. This is necessary to enforce zero-copy memory transfer used throughout `rix-core`. Unforunately, this means that there is no support for dynamically allocated member variables within messages.

To create your own `rixmsg` package, create a folder to contain the message definitions and create a separate `.rixmsg` file for each message. Then, run `rixmsg create <path/to/directory>` to generator the header files from the definitions. 
