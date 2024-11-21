#!/bin/bash

# Install the required packages
# pip install pyinstaller

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
sudo ln -sf "$HOME/.rix/rix-msg/rixmsg/rixmsg" /usr/local/bin/rixmsg

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
sudo mkdir -p /usr/local/include/rix/msg/
sudo cp -r rix-msg/include/* /usr/local/include/rix/msg/

# Run CMake for rix-msg
mkdir -p rix-msg/build
cd rix-msg/build
cmake ..
sudo make install
cd ../..

echo "Installation completed successfully"
echo "Creating default rix message implementation files"

sudo -E rixmsg create rix-msg/defs/standard
sudo -E rixmsg create rix-msg/defs/sensor
sudo -E rixmsg create rix-msg/defs/geometry

echo "Default rix message implementation files created successfully"

echo "Installing Node.JS packages"
cd rix-structjs
npm install
echo "Linking rix-structjs"
npm link
cd ..

# Store the current directory
DIR=$(pwd)

cd "$HOME/.rix/node_modules/rix-msg/"
echo "Linking rix-structjs to rix-msg"
npm link rix-structjs
npm install

# Return to the original directory
cd $DIR

exit 0
