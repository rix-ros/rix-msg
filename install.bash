#!/bin/bash

set -e

python3 -m venv venv
source venv/bin/activate

# Install the required packages
pip install -r requirements.txt

# Create the executable
python3 -m PyInstaller --clean --strip --optimize 2 --paths rixmsg/src/ --hidden-import jsonschema --onedir --noupx --name rixmsg rixmsg/src/main.py

# Check if the executable was created
if [ ! -f "dist/rixmsg/rixmsg" ]; then
    echo "Error: rixmsg executable not found in dist/rixmsg/"
    exit 1
fi

# Copy the required files
cp -r dist/rixmsg "$HOME/.rix/"

# Create symbolic link to rixmsg
mkdir -p "$HOME/.rix/bin/"
ln -sf "$HOME/.rix/rixmsg/rixmsg" "$HOME/.rix/bin/rixmsg"

# Clean up
rm -r build/ dist/

# Create directories for rixmsg
mkdir -p "$HOME/.rix/js/rixmsg"
mkdir -p "$HOME/.rix/python/rixmsg/rixmsg"
mkdir -p "$HOME/.rix/include/rix/msg/"

# Copy files to rixmsg directories
cp -r cpp/* "$HOME/.rix/include/rix/msg/"
cp -r js/* "$HOME/.rix/js/rixmsg/"
cp python/setup.py "$HOME/.rix/python/rixmsg/"
touch "$HOME/.rix/python/rixmsg/rixmsg/__init__.py"
cp python/message.py "$HOME/.rix/python/rixmsg/rixmsg/"
cp rixmsg/schema.json "$HOME/.rix/rixmsg/schema.json"

echo "Installation completed successfully."
echo "Creating default rix message implementation files."

"$HOME/.rix/bin/rixmsg" create defs/mediator
"$HOME/.rix/bin/rixmsg" create defs/standard
"$HOME/.rix/bin/rixmsg" create defs/sensor
"$HOME/.rix/bin/rixmsg" create defs/geometry

echo "Default rix message implementation files created successfully."

deactivate
rm -r venv

exit 0
