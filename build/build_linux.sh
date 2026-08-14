#!/usr/bin/env bash
# Build the Linux one-file executable: ./build/build_linux.sh
# Output: dist/Attendly  (requires bash, Python 3.10+, venv with deps)
set -e
cd "$(dirname "$0")/.."

if [ ! -d venv ]; then
  python3 -m venv venv
  venv/bin/pip install -r requirements.txt
fi
venv/bin/pip install -q pyinstaller

venv/bin/pyinstaller --noconfirm --clean --onefile --windowed --name Attendly \
  --hidden-import cv2.face \
  --add-data "assets:assets" \
  --add-data "data/haarcascade_frontalface_default.xml:data" \
  main.py

echo "Done: dist/Attendly"
