#!/bin/bash

# Install the required packages
pip install -r requirements.txt

# Check if Node.js is installed
if ! [ -x "$(command -v node)" ]; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Create the executable
pyinstaller --clean -p=rixmsg/python/ --onedir --strip --noupx -y rixmsg/python/rixmsg.py

# Check if the executable was created
if [ ! -f "dist/rixmsg/rixmsg" ]; then
    echo "Error: rixmsg executable not found in dist/rixmsg/"
    exit 1
fi

# Copy the required files
mkdir -p "$HOME/.rix/rixmsg/"
cp -r dist/rixmsg "$HOME/.rix/rixmsg/"

# Create symbolic link to rixmsg
ln -sf "$HOME/.rix/rixmsg/rixmsg/rixmsg" "$HOME/.rix/bin/rixmsg"

# Clean up
rm -rf build/ dist/

# Create node_modules and python directories
mkdir -p "$HOME/.rix/node_modules/rixmsg"
mkdir -p "$HOME/.rix/python/rixmsg"

# Copy include to rixmsg directory
mkdir -p "$HOME/.rix/include/rix/msg/"
cp -r rixmsg/include/* "$HOME/.rix/include/rix/msg/"

# Run CMake for rixmsg
mkdir -p rixmsg/build
cd rixmsg/build
cmake ..
make install
cd ../..

echo "Installation completed successfully"
echo "Creating default rix message implementation files"

rixmsg create rixmsg/defs/component
rixmsg create rixmsg/defs/standard
rixmsg create rixmsg/defs/sensor
rixmsg create rixmsg/defs/geometry

echo "Default rix message implementation files created successfully"

echo "Installing Node.JS packages"
cd cstructjs
npm install
echo "Linking cstructjs"
npm link
cd ..

# Store the current directory
DIR=$(pwd)

cd "$HOME/.rix/node_modules/rixmsg/"
echo "Linking cstructjs to rixmsg"
npm link cstructjs
npm install

# Return to the original directory
cd $DIR

exit 0
