# RIX-MSG

The `rix-msg` library contains definitions for the base message types used in `rix` and the `rixmsg` executable.

## Install

To install `rixmsg`, run the following command:

```bash
cd rix-msg
mkdir build
cd build
cmake ..
make install
```

The default installation will generate header files for the message definitions in `include/rix/msg/defs/`. If you do not want these files generated, toggle the `GEN_MSGS` flag off.
```bash
cd rix-msg
mkdir build
cd build
cmake -DGEN_MSGS=OFF ..
make install
```

This will install the `rixmsg` executable into `/usr/local/bin`. 

## Usage

`rixmsg` contains five functions: `help`, `packages`,`show`, `package`, and `create`.

* `rixmsg help`: This will print a help message with the `rixmsg` usage.
* `rixmsg packages`: This will list all of the `rixmsg` packages that you have installed.
* `rixmsg package <package>`: This will list the names of each message in a package
* `rixmsg show <package>/<name>`: This will print the `.rixmsg` file of the specified message.
* `rixmsg create <path>`: This will generate C++ header files from `.rixmsg` files and install them into `/usr/local/include/rix/msgs/<package>/<name>.hpp`. `<path>` should specify a path to a directory containing `.rixmsg` files.


After the default installation, `rixmsg packages` should output:
```txt
core
geometry
sensor
standard
```

Additionally `rixmsg package geometry` should output:
```txt
point
pointstamped
quaternion
quaternionstamped
tf
transform
transformstamped
twist
twiststamped
vector3
vector3stamped
```

RIX packages are designed to be easy to include in your existing CMake projects. For example:
```cmake
cmake_minimum_required(VERSION 3.5)

project(msg_test)

set(CMAKE_CXX_STANDARD 11)

find_package(rix_msg REQUIRED)

add_executable(test test.cpp)
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