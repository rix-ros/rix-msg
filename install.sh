#!/bin/bash

chmod +x rixmsg-gen.py
chmod +x rixmsg

touch /usr/local/bin/rixmsg-gen
touch /usr/local/bin/rixmsg
cp -p rixmsg-gen.py /usr/local/bin/rixmsg-gen
cp -p rixmsg /usr/local/bin/rixmsg
cp include/error.hpp /usr/local/include/rix/msgs/error.hpp