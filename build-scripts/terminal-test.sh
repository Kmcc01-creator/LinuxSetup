#!/bin/bash

# Source terminal utilities
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/terminal-utils.sh"

# Create a small test icon (you can replace this with a real icon file)
cat > test_icon.png << 'EOL'
iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAYAAAAf8/9hAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJ
bWFnZVJlYWR5ccllPAAAAyJpVFh0WE1MOmNvbS5hZG9iZS54bXAAAAAAADw/eHBhY2tldCBiZWdp
bj0i77u/IiBpZD0iVzVNME1wQ2VoaUh6cmVTek5UY3prYzlkIj8+IDx4OnhtcG1ldGEgeG1sbnM6
eD0iYWRvYmU6bnM6bWV0YS8iIHg6eG1wdGs9IkFkb2JlIFhNUCBDb3JlIDUuMy1jMDExIDY2LjE0
NTY2MSwgMjAxMi8wMi8wNi0xNDo1NjoyNyAgICAgICAgIj4gPHJkZjpSREYgeG1sbnM6cmRmPSJo
dHRwOi8vd3d3LnczLm9yZy8xOTk5LzAyLzIyLXJkZi1zeW50YXgtbnMjIj4gPHJkZjpEZXNjcmlw
dGlvbiByZGY6YWJvdXQ9IiIgeG1sbnM6eG1wPSJodHRwOi8vbnMuYWRvYmUuY29tL3hhcC8xLjAv
IiB4bWxuczp4bXBNTT0iaHR0cDovL25zLmFkb2JlLmNvbS94YXAvMS4wL21tLyIgeG1sbnM6c3RS
ZWY9Imh0dHA6Ly9ucy5hZG9iZS5jb20veGFwLzEuMC9zVHlwZS9SZXNvdXJjZVJlZiMiIHhtcDpD
cmVhdG9yVG9vbD0iQWRvYmUgUGhvdG9zaG9wIENTNiAoV2luZG93cykiIHhtcE1NOkluc3RhbmNl
SUQ9InhtcC5paWQ6QjM3MUVBMTk5ODg0MTFFQjg2N0NBQTYyOERBMDg0MEIiIHhtcE1NOkRvY3Vt
ZW50SUQ9InhtcC5kaWQ6QjM3MUVBMUExMDg0MTFFQjg2N0NBQTYyOERBMDg0MEIiPiA8eG1wTU06
RGVyaXZlZEZyb20gc3RSZWY6aW5zdGFuY2VJRD0ieG1wLmlpZDpCMzcxRUExNzk4ODQxMUVCODY3
Q0FBNjI4REEwODQwQiIgc3RSZWY6ZG9jdW1lbnRJRD0ieG1wLmRpZDpCMzcxRUExODk4ODQxMUVC
ODY3Q0FBNjI4REEwODQwQiIvPiA8L3JkZjpEZXNjcmlwdGlvbj4gPC9yZGY6UkRGPiA8L3g6eG1w
bWV0YT4gPD94cGFja2V0IGVuZD0iciI/Pv/uAA5BZG9iZQBkwAAAAAH/2wCEAAYEBAQFBAYFBQYJ
BgUGCQsIBgYICwwKCgsKCgwQDAwMDAwMEAwODxAPDgwTExQUExMcGxsbHB8fHx8fHx8fHx8BBQUF
CAcIDwkJDxQODg4UFA4ODg4UEQwMDAwMEREMDAwMDAwRDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwM
DAwMDP/AABEIABAQAQMBIgACEQEDEQH/xABcAAEAAAAAAAAAAAAAAAAAAAAJAQEAAAAAAAAAAAAA
AAAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
AAAAAAAAAAAAAAAAAAEBAQAAAAAAAAAAAAAAAAAAAAERAQAAAAAAAAAAAAAAAAAAAAn/2gAMAwEA
AhEDEQA/AJ+gf//Z
EOL

# Run the demo
clear
echo "=== Terminal Features Demo ==="
echo

# Set terminal title and icon
set_terminal_title "Feature Demo"
set_terminal_icon "test_icon.png"

# Show terminal capabilities
echo "Terminal Information:"
echo "-------------------"
for cap in "${!TERM_CAPABILITIES[@]}"; do
    printf "%-15s: %s\n" "$cap" "${TERM_CAPABILITIES[$cap]}"
done

# Demonstrate fancy text
echo -e "\nFancy Text Examples:"
echo "-------------------"
fancy_text "♦ Rainbow Text Effect ♦" "rainbow"
fancy_text "♦ Pulsing Text Effect ♦" "pulse"
fancy_text "♦ Bold Pulsing Effect ♦" "bold-pulse"
fancy_text "♦ Gradient Text Effect ♦" "gradient"

# Demonstrate hyperlinks
echo -e "\nHyperlink Examples:"
echo "-
