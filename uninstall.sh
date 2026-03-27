#!/bin/bash
# Uninstall Clingy for the current user.
#
# This script:
#   1. Stops and disables the systemd user service
#   2. Removes the service file
#   3. Removes the installed application from ~/.local/share/clingy/
#
# Note: Your saved notes in ~/.local/share/clingy/ are preserved by default.
#       Use --purge to also remove saved notes.

set -euo pipefail

INSTALL_DIR="$HOME/.local/share/clingy"
SERVICE_DIR="$HOME/.config/systemd/user"
SERVICE_FILE="clingy.service"
PURGE=false

for arg in "$@"; do
    case "$arg" in
        --purge) PURGE=true ;;
        *) echo "Unknown option: $arg"; exit 1 ;;
    esac
done

echo "Uninstalling Clingy..."

# -- 1. Stop and disable the service -----------------------------------------
if systemctl --user is-active --quiet clingy 2>/dev/null; then
    systemctl --user stop clingy
    echo "  Service stopped"
fi

if systemctl --user is-enabled --quiet clingy 2>/dev/null; then
    systemctl --user disable clingy
    echo "  Service disabled"
fi

# -- 2. Remove service file --------------------------------------------------
if [ -f "$SERVICE_DIR/$SERVICE_FILE" ]; then
    rm "$SERVICE_DIR/$SERVICE_FILE"
    systemctl --user daemon-reload
    echo "  Service file removed"
fi

# -- 3. Remove installed application -----------------------------------------
if [ -d "$INSTALL_DIR" ]; then
    # Always remove the application code and venv
    rm -rf "$INSTALL_DIR/clingy"
    rm -rf "$INSTALL_DIR/venv"
    rm -f  "$INSTALL_DIR/requirements.txt"

    if [ "$PURGE" = true ]; then
        # Remove everything including saved notes
        rm -rf "$INSTALL_DIR"
        echo "  Application and saved notes removed from $INSTALL_DIR"
    else
        echo "  Application removed from $INSTALL_DIR"
        # Check if there are remaining files (i.e. saved notes)
        if [ -d "$INSTALL_DIR" ] && [ "$(ls -A "$INSTALL_DIR" 2>/dev/null)" ]; then
            echo "  Note: Saved notes preserved in $INSTALL_DIR"
            echo "        Run with --purge to also remove saved notes"
        else
            # Nothing left, clean up the empty directory
            rmdir "$INSTALL_DIR" 2>/dev/null || true
        fi
    fi
fi

echo ""
echo "Clingy has been uninstalled."
