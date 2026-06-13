#!/usr/bin/env bash
set -euo pipefail

# Build Aircon Calculator executable for Unix-like systems
pyinstaller --onefile --console --name aircon-calculator main.py

echo
echo "Build complete. Check the dist folder for aircon-calculator executable."

