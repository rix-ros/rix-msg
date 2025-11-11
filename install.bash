#!/bin/bash

set -e

# Check if python3.12 is available
if ! command -v python3.12 &>/dev/null; then
    echo "Error: python3.12 is not installed or not in PATH."
    echo "Please install Python 3.12 and try again."
    exit 1
fi

python3.12 -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Create the executable
python3.12 -m PyInstaller --clean --strip --optimize 2 --paths rixmsg/src/ --hidden-import jsonschema --onedir --noupx --name rixmsg rixmsg/src/main.py

# Check if the executable was created
if [ ! -f "dist/rixmsg/rixmsg" ]; then
    echo "Error: rixmsg executable not found in dist/rixmsg/"
    exit 1
fi

# Copy the required files
mkdir -p "$HOME/.rix/"
cp -r dist/rixmsg "$HOME/.rix/"

# Create symbolic link to rixmsg
mkdir -p "$HOME/.rix/bin/"
ln -sf "$HOME/.rix/rixmsg/rixmsg" "$HOME/.rix/bin/rixmsg"

# Clean up
rm -r build/ dist/

# Create directories for rixmsg libraries
mkdir -p "$HOME/.rix/js/rixmsg"
mkdir -p "$HOME/.rix/python/rix/rix/msg"
mkdir -p "$HOME/.rix/include/rix/msg/"

# Copy schema to rixmsg directory
cp rixmsg/schema.json "$HOME/.rix/rixmsg/schema.json"

# Copy rixmsg setup files
cp -r cpp/* "$HOME/.rix/include/rix/msg/"
cp -r js/* "$HOME/.rix/js/rixmsg/"
cp python/* "$HOME/.rix/python/rix/rix/msg/"

echo "Installation completed successfully."
echo "Creating default rix message implementation files."

"$HOME/.rix/bin/rixmsg" create defs/sys_msgs
"$HOME/.rix/bin/rixmsg" create defs/std_msgs
"$HOME/.rix/bin/rixmsg" create defs/sensor_msgs
"$HOME/.rix/bin/rixmsg" create defs/geometry_msgs

echo "Default rix message implementation files created successfully."

deactivate
rm -r venv

exit 0
