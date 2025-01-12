#!/bin/bash

# Source required modules
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/colors.sh"
source "$SCRIPT_DIR/palettes.sh"
source "$SCRIPT_DIR/logging.sh"

# Set up example configuration
LOG_LEVEL="DEBUG"
set_log_level "$LOG_LEVEL"

log_info "Starting color system integration example"

# Function to display color in terminal
display_color() {
    local r=$1
    local g=$2
    local b=$3
    local text=${4:-"    "}  # Default to spaces for color block
    
    local color_code=$(rgb_to_terminal $r $g $b)
    local bg_code=$(rgb_to_terminal_bg $r $g $b)
    echo -e "${bg_code}${color_code}${text}\033[0m"
}

# Function to display HSL color
display_hsl_color() {
    local h=$1
    local s=$2
    local l=$3
    local text=${4:-"    "}
    
    # Convert HSL to RGB
    local rgb_values
    rgb_values=$(hsl_to_rgb $h $s $l)
    read -r r g b <<< "$rgb_values"
    
    display_color $r $g $b "$text"
    log_debug "Displayed HSL($h, $s, $l) as RGB($r, $g, $b)"
}

# Test palette generation
test_palette_generation() {
    local palette_name=$1
    local h=$2
    local s=$3
    local l=$4
    
    log_info "Generating $palette_name palette (H:$h, S:$s, L:$l)"
    
    # Generate palette
    case $palette_name in
        "monochromatic")
            eval "$(generate_monochromatic_palette $h $s $l)"
            log_info "Generated monochromatic palette"
            
            # Display palette
            echo "Monochromatic Palette:"
            for key in "${!palette[@]}"; do
                read -r r g b <<< "${palette[$key]}"
                display_color $r $g $b "  $key  "
            done
            ;;
            
        "complementary")
            eval "$(generate_complementary_palette $h $s $l)"
            log_info "Generated complementary palette"
            
            # Display palette
            echo "Complementary Palette:"
            for key in "${!palette[@]}"; do
                read -r r g b <<< "${palette[$key]}"
                display_color $r $g $b "  $key  "
            done
            ;;
            
        "triadic")
            eval "$(generate_triadic_palette $h $s $l)"
            log_info "Generated triadic palette"
            
            # Display palette
            echo "Triadic Palette:"
            for key in "${!palette[@]}"; do
                read -r r g b <<< "${palette[$key]}"
                display_color $r $g $b "  $key  "
            done
            ;;
    esac
}

# Example usage of color transformations
log_info "Testing color transformations"

echo -e "\nColor Space Transformations:"
echo "-----------------------------"

# Test RGB to HSL conversion
test_rgb=(255 128 0)  # Orange color
log_debug "Converting RGB(${test_rgb[0]}, ${test_rgb[1]}, ${test_rgb[2]}) to HSL"
hsl_values=$(rgb_to_hsl ${test_rgb[@]})
read -r h s l <<< "$hsl_values"
display_color ${test_rgb[@]} " RGB "
display_hsl_color $h $s $l " HSL "

# Test predefined palettes
echo -e "\nPredefined Palettes:"
echo "--------------------"

log_info "Testing predefined palettes"

# Ocean Palette
echo "Ocean Theme:"
eval "$PALETTE_OCEAN"
for key in "${!palette[@]}"; do
    read -r r g b <<< "${palette[$key]}"
    display_color $r $g $b "  $key  "
done

# Generate custom palettes
echo -e "\nCustom Palette Generation:"
echo "------------------------"

# Test monochromatic palette
test_palette_generation "monochromatic" 180 0.6 0.5

# Test complementary palette
test_palette_generation "complementary" 30 0.7 0.5

# Test triadic palette
test_palette_generation "triadic" 120 0.6 0.4

# Error handling example
echo -e "\nError Handling Example:"
echo "----------------------"

log_info "Testing error handling"

# Simulate some errors
track_error "COLOR_CONVERSION" "Invalid RGB value: 300"
track_error "PALETTE_GENERATION" "Invalid hue value: -30"
track_error "COLOR_DISPLAY" "Terminal doesn't support true color"

# Display error summary
echo -e "\nError Summary:"
echo "--------------"
get_error_summary

log_info "Color system integration example completed"

# Rotate log if needed
rotate_log

exit 0
