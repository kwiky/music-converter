#!/bin/bash
#
# FLAC to Opus Converter Wrapper Script
# Usage: ./convert_flac_to_opus.sh
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_SCRIPT="$SCRIPT_DIR/flac_to_opus_converter.py"

# Check if Python script exists
if [[ ! -f "$PYTHON_SCRIPT" ]]; then
    echo "Error: Python script not found at $PYTHON_SCRIPT"
    exit 1
fi

# Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not found"
    echo "Please install Python 3"
    exit 1
fi

# Run the Python script
echo "Starting FLAC to Opus conversion tool..."
echo "Music directory: $(dirname "$SCRIPT_DIR")"
echo ""

python3 "$PYTHON_SCRIPT" "$@"