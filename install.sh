#!/bin/bash
# Install Clingy for the current user.
#
# This script:
#   1. Copies the application to ~/.local/share/clingy/
#   2. Creates a Python virtual environment and installs dependencies
#   3. Installs the systemd user service
#
# After installation you can manage Clingy with:
#   systemctl --user start   clingy   # start now
#   systemctl --user stop    clingy   # stop now
#   systemctl --user enable  clingy   # auto-start on login
#   systemctl --user disable clingy   # disable auto-start
#   systemctl --user status  clingy   # check status

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INSTALL_DIR="$HOME/.local/share/clingy"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="clingy.service"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor/512x512/apps"

echo "Installing Clingy..."

# -- 1. Copy application files -----------------------------------------------
mkdir -p "$INSTALL_DIR"
cp -r "$SCRIPT_DIR/clingy" "$INSTALL_DIR/"
cp "$SCRIPT_DIR/requirements.txt" "$INSTALL_DIR/"

echo "  Application files copied to $INSTALL_DIR"

# -- 2. Create virtual environment -------------------------------------------
if [ ! -d "$INSTALL_DIR/venv" ]; then
    python3 -m venv "$INSTALL_DIR/venv"
fi
"$INSTALL_DIR/venv/bin/pip" install --quiet -r "$INSTALL_DIR/requirements.txt"

echo "  Virtual environment created and dependencies installed"

# -- 3. Install systemd user service -----------------------------------------
mkdir -p "$SERVICE_DIR"
cp "$SCRIPT_DIR/$SERVICE_FILE" "$SERVICE_DIR/$SERVICE_FILE"
systemctl --user daemon-reload

echo "  Systemd user service installed"

# -- 4. Install desktop entry and icon ---------------------------------------
mkdir -p "$ICON_DIR"
cp "$SCRIPT_DIR/logo/logo.png" "$ICON_DIR/clingy.png"

mkdir -p "$DESKTOP_DIR"
# Copy the template and inject the Exec / Path lines with the real $HOME.
cp "$SCRIPT_DIR/clingy.desktop" "$DESKTOP_DIR/clingy.desktop"
sed -i "/^\[Desktop Entry\]$/a Exec=$INSTALL_DIR/venv/bin/python -m clingy.main\nPath=$INSTALL_DIR" \
    "$DESKTOP_DIR/clingy.desktop"

# Refresh the desktop database so the launcher picks up the new entry.
if command -v update-desktop-database &>/dev/null; then
    update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true
fi

echo "  Desktop entry and icon installed"

echo ""
echo "Installation complete!"
echo ""
echo "Manage Clingy with:"
echo "  systemctl --user start   clingy   # start now"
echo "  systemctl --user stop    clingy   # stop now"
echo "  systemctl --user enable  clingy   # auto-start on login"
echo "  systemctl --user disable clingy   # disable auto-start"
echo "  systemctl --user status  clingy   # check status"
