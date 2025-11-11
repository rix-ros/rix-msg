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

# Copy rixmsg
cp -r rixmsg "$HOME/.rix/"

# Ensure main.py is executable
chmod +x "$HOME/.rix/rixmsg/src/main.py"

# Create symbolic link to rixmsg
mkdir -p "$HOME/.rix/bin/"
ln -sf "$HOME/.rix/rixmsg/src/main.py" "$HOME/.rix/bin/rixmsg"

# Create directories for rixmsg libraries
mkdir -p "$HOME/.rix/python/rix/rix/msg"
mkdir -p "$HOME/.rix/include/rix/msg/"

# Copy rixmsg setup files
cp -r cpp/* "$HOME/.rix/include/rix/msg/"
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
