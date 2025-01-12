#!/bin/bash

# Source terminal utilities
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/terminal-utils.sh"

# Function to check if file exists and is readable
check_icon_file() {
    local icon_path=$1
    if [[ ! -f "$icon_path" ]]; then
        log_error "Icon file not found: $icon_path"
        return 1
    elif [[ ! -r "$icon_path" ]]; then
        log_error "Icon file not readable: $icon_path"
        return 1
    fi
    return 0
}

# Function to validate icon file type
validate_icon_file() {
    local icon_path=$1
    local mime_type
    
    # Check if 'file' command exists
    if command -v file >/dev/null 2>&1; then
        mime_type=$(file --mime-type -b "$icon_path")
        case "$mime_type" in
            image/png|image/jpeg|image/gif|image/x-icon)
                return 0
                ;;
            *)
                log_error "Unsupported icon file type: $mime_type"
                return 1
                ;;
        esac
    else
        # Fallback to extension check if 'file' command is not available
        case "${icon_path,,}" in
            *.png|*.jpg|*.jpeg|*.gif|*.ico)
                return 0
                ;;
            *)
                log_warning "Cannot verify icon file type, 'file' command not available"
                return 0
                ;;
        esac
    fi
}

# Icon setup function
setup_icon() {
    local icon_path="${SCRIPT_DIR}/example_icon.png"
    
    if check_icon_file "$icon_path" && validate_icon_file "$icon_path"; then
        log_info "Setting terminal icon from: $icon_path"
        set_terminal_icon "$icon_path"
    else
        log_warning "Skipping icon setup due to file issues"
    fi
}

# Run the demo
clear
echo "=== Terminal Features Demo ==="
echo

# Set terminal title and icon
set_terminal_title "Feature Demo"
setup_icon

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
echo "------------------"
terminal_link "https://github.com" "Visit GitHub"
terminal_link "https://www.kernel.org" "Linux Kernel"

# Demonstrate progress bar
echo -e "\nProgress Bar Example:"
echo "--------------------"
for i in {0..20}; do
    gradient_progress_bar "$i" 20 40
    sleep 0.1
done

# Show terminal dimensions
echo -e "\nTerminal Size:"
echo "--------------"
get_terminal_dimensions

# Cursor position demo
echo -e "\nCursor Position Demo:"
echo "--------------------"
echo "Current position before save: $(show_cursor_position)"
save_cursor_position
echo "Position saved!"

# Move cursor to a new position
move_cursor 15 10
echo "Moved cursor to row 15, column 10"
sleep 1

# Show current position
echo "Current position after move: $(show_cursor_position)"
sleep 1

# Restore original position
restore_cursor_position
echo "Cursor restored to original position"
echo "Final position: $(show_cursor_position)"

# Cleanup
rm -f "$SCRIPT_DIR/test_icon.png" 2>/dev/null
