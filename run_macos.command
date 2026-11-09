#!/bin/bash
cd "$(dirname "$0")"
python3 app.py
status=$?
if [ "$status" -ne 0 ]; then
  read -r -p "Press Enter to close..."
fi
exit "$status"
