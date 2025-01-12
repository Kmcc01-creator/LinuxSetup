#!/bin/bash

# Source required utilities
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/colors.sh"
source "$SCRIPT_DIR/logging.sh"

# Terminal capability detection
declare -A TERM_CAPABILITIES

# ANSI escape sequences
ESC=$'\033'
CSI="${ESC}["
OSC="${ESC}]"
BEL=$'\007'

# Initialize terminal capabilities
init_terminal_detection() {
    log_debug "Initializing terminal detection"
    
    # Basic terminal info
    TERM_CAPABILITIES[TERM]=$TERM
    TERM_CAPABILITIES[TERM_PROGRAM]=$TERM_PROGRAM
    TERM_CAPABILITIES[COLORTERM]=$COLORTERM
    
    # Detect color support
    if [ "$(tput colors 2>/dev/null)" -ge 256 ]; then
        TERM_CAPABILITIES[256_COLORS]=true
    else
        TERM_CAPABILITIES[256_COLORS]=false
    fi
    
    # True color support
    if check_true_color; then
        TERM_CAPABILITIES[TRUE_COLOR]=true
    else
        TERM_CAPABILITIES[TRUE_COLOR]=false
    fi
    
    # Unicode support
    if echo -e '\u2713' > /dev/null 2>&1; then
        TERM_CAPABILITIES[UNICODE]=true
    else
        TERM_CAPABILITIES[UNICODE]=false
    fi
    
    # Detect common terminals with extended features
    case "$TERM_PROGRAM" in
        iTerm.app)
            TERM_CAPABILITIES[IMAGES]=true
            TERM_CAPABILITIES[FAVICONS]=true
            TERM_CAPABILITIES[HYPERLINKS]=true
            ;;
        WezTerm)
            TERM_CAPABILITIES[IMAGES]=true
            TERM_CAPABILITIES[FAVICONS]=true
            TERM_CAPABILITIES[HYPERLINKS]=true
            ;;
        kitty)
            TERM_CAPABILITIES[IMAGES]=true
            TERM_CAPABILITIES[FAVICONS]=true
            TERM_CAPABILITIES[HYPERLINKS]=true
            ;;
        *)
            TERM_CAPABILITIES[IMAGES]=false
            TERM_CAPABILITIES[FAVICONS]=false
            TERM_CAPABILITIES[HYPERLINKS]=false
            ;;
    esac
}

# Fancy text effects
fancy_text() {
    local text=$1
    local style=$2
    
    case $style in
        "rainbow")
            local output=""
            local colors=(196 208 226 46 21 201)  # Rainbow colors
            local i=0
            for (( j=0; j<${#text}; j++ )); do
                local char="${text:$j:1}"
                output+="${CSI}38;5;${colors[$((i % 6))]}m$char"
                ((i++))
            done
            echo -e "${output}${CSI}0m"
            ;;
        "pulse")
            echo -e "${CSI}5m$text${CSI}0m"
            ;;
        "bold-pulse")
            echo -e "${CSI}1;5m$text${CSI}0m"
            ;;
        "gradient")
            local output=""
            for (( i=0; i<${#text}; i++ )); do
                local char="${text:$i:1}"
                local intensity=$((255 - (i * 255 / ${#text})))
                output+="${CSI}38;2;${intensity};0;${intensity}m$char"
            done
            echo -e "${output}${CSI}0m"
            ;;
    esac
}

# Set terminal title
set_terminal_title() {
    echo -e "${OSC}0;$1${BEL}"
}

# Set terminal favicon (works in supported terminals)
set_terminal_icon() {
    local icon_file=$1
    if [ "${TERM_CAPABILITIES[FAVICONS]}" = true ] && [ -f "$icon_file" ]; then
        # Convert icon to base64
        local icon_base64
        icon_base64=$(base64 -w 0 "$icon_file")
        echo -e "${OSC}1;icon=data:image/png;base64,${icon_base64}${BEL}"
    else
        log_warning "Terminal doesn't support favicons or icon file not found"
    fi
}

# Hyperlinks in terminal (works in supported terminals)
terminal_link() {
    local url=$1
    local text=${2:-$url}
    
    if [ "${TERM_CAPABILITIES[HYPERLINKS]}" = true ]; then
        echo -e "${OSC}8;;${url}${BEL}${text}${OSC}8;;${BEL}"
    else
        echo "$text ($url)"
    fi
}

# Progress bar with gradient colors
gradient_progress_bar() {
    local current=$1
    local total=$2
    local width=${3:-50}
    
    local percentage=$((current * 100 / total))
    local filled=$((width * current / total))
    local empty=$((width - filled))
    
    # Start with carriage return to overwrite previous line
    echo -n -e "\r["
    
    # Filled portion with gradient
    for (( i=0; i<filled; i++ )); do
        local r=$((255 - (i * 255 / width)))
        local b=$((i * 255 / width))
        echo -n -e "${CSI}38;2;${r};0;${b}m▓"
    done
    
    # Empty portion
    for (( i=0; i<empty; i++ )); do
        echo -n -e "${CSI}38;2;100;100;100m░"
    done
    
    echo -n -e "${CSI}0m] ${percentage}%"
    
    # Print newline if complete
    if [ "$current" -eq "$total" ]; then
        echo
    fi
}

# Show cursor position
show_cursor_position() {
    local pos
    echo -en "${CSI}6n"
    read -sdR pos
    echo "${pos#*[}"
}

# Terminal dimensions
get_terminal_dimensions() {
    echo "Rows: $(tput lines), Columns: $(tput cols)"
}

# Save cursor position
save_cursor_position() {
    echo -en "${CSI}s"
}

# Restore cursor position
restore_cursor_position() {
    echo -en "${CSI}u"
}

# Move cursor
move_cursor() {
    local row=$1
    local col=$2
    echo -en "${CSI}${row};${col}H"
}

# Example usage function
demo_terminal_features() {
    clear
    set_terminal_title "Terminal Features Demo"
    
    echo "Terminal Capabilities:"
    for cap in "${!TERM_CAPABILITIES[@]}"; do
        echo "  $cap: ${TERM_CAPABILITIES[$cap]}"
    done
    
    echo -e "\nFancy Text Examples:"
    fancy_text "Rainbow Text Example" "rainbow"
    fancy_text "Pulsing Text Example" "pulse"
    fancy_text "Bold Pulsing Text Example" "bold-pulse"
    fancy_text "Gradient Text Example" "gradient"
    
    echo -e "\nHyperlink Example:"
    terminal_link "https://github.com" "GitHub"
    
    echo -e "\nProgress Bar Example:"
    for i in {0..10}; do
        gradient_progress_bar "$i" 10
        sleep 0.2
    done
    
    echo -e "\nTerminal Information:"
    get_terminal_dimensions
    
    echo -e "\nCursor Position Test:"
    save_cursor_position
    echo "Current cursor position: $(show_cursor_position)"
    restore_cursor_position
}

# Initialize terminal detection when sourced
init_terminal_detection
