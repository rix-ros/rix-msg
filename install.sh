#!/bin/bash

# Install the required packages
pip install pyinstaller

# Create the executable
pyinstaller -p=rix-msg/python/ --onedir --strip --noupx -y rix-msg/python/rixmsg.py

# Check if the executable was created
if [ ! -f "dist/rixmsg/rixmsg" ]; then
    echo "Error: rixmsg executable not found in dist/rixmsg/"
    exit 1
fi

# Copy the required files
mkdir -p "$HOME/.rix/rix-msg/"
cp -r dist/rixmsg "$HOME/.rix/rix-msg/"

# Verify the copied executable
if [ ! -f "$HOME/.rix/rix-msg/rixmsg/rixmsg" ]; then
    echo "Error: rixmsg executable not found in $HOME/.rix/rix-msg/rixmsg/"
    exit 1
fi

# Create the symbolic link
ln -sf "$HOME/.rix/rix-msg/rixmsg/rixmsg" /usr/local/bin/rixmsg

# Verify the symbolic link
if [ ! -L "/usr/local/bin/rixmsg" ]; then
    echo "Error: symbolic link not created in /usr/local/bin/"
    exit 1
fi

# Clean up
rm -rf build/ dist/

# Create node_modules and python directories
mkdir -p "$HOME/.rix/node_modules/rix-msg"
mkdir -p "$HOME/.rix/python/rixmsg"

# Copy include to rix-msg directory
cp -r rix-msg/include /usr/local/include/rix/msg/

# Run CMake for rix-msg
mkdir -p rix-msg/build
cd rix-msg/build
cmake ..
make install
cd ../..

echo "Installation completed successfully"
echo "Creating default rix message implementation files"

rixmsg create rix-msg/defs/standard
rixmsg create rix-msg/defs/sensor
rixmsg create rix-msg/defs/geometry
rixmsg create rix-msg/defs/navigation

echo "Default rix message implementation files created successfully"

exit 0