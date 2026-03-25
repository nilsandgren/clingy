#!/bin/bash
# Create a virtual environment and install dependencies for Clingy.
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
python3 -m venv "$SCRIPT_DIR/venv"
source "$SCRIPT_DIR/venv/bin/activate"
pip install -r "$SCRIPT_DIR/requirements.txt"
echo ""
echo "Setup complete. Run the app with: ./run.sh"
