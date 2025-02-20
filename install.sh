#!/bin/bash

python3 -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Check if Node.js is installed
if ! [ -x "$(command -v node)" ]; then
    echo "Error: Node.js is not installed"
    exit 1
fi

# Create the executable
# python3 -m PyInstaller --clean --strip --optimize 2 --paths rixmsg/python/ --hidden-import jsonschema --onedir --noupx --specpath . --name rixmsg rixmsg/python/main.py
python3 -m PyInstaller rixmsg.spec

# Check if the executable was created
if [ ! -f "dist/rixmsg/rixmsg" ]; then
    echo "Error: rixmsg executable not found in dist/rixmsg/"
    exit 1
fi

# Copy the required files
mkdir -p "$HOME/.rix/rixmsg/"
cp -r dist/rixmsg "$HOME/.rix/rixmsg/"

# Create symbolic link to rixmsg
mkdir -p "$HOME/.rix/bin/"
ln -sf "$HOME/.rix/rixmsg/rixmsg/rixmsg" "$HOME/.rix/bin/rixmsg"

# Clean up
rm -r build/ dist/

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

"$HOME/.rix/bin/rixmsg" create rixmsg/defs/component
"$HOME/.rix/bin/rixmsg" create rixmsg/defs/standard
"$HOME/.rix/bin/rixmsg" create rixmsg/defs/sensor
"$HOME/.rix/bin/rixmsg" create rixmsg/defs/geometry

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

deactivate
rm -r venv

exit 0
