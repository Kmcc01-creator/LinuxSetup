#!/bin/bash

# Color conversion and generation utilities

# Convert RGB to HSL
# Usage: rgb_to_hsl 255 128 0
rgb_to_hsl() {
    local r=$1
    local g=$2
    local b=$3
    
    # Normalize RGB values to 0-1
    r=$(echo "scale=6; $r/255" | bc)
    g=$(echo "scale=6; $g/255" | bc)
    b=$(echo "scale=6; $b/255" | bc)
    
    # Find min and max values
    local max min
    max=$(echo "$r $g $b" | tr ' ' '\n' | sort -nr | head -n1)
    min=$(echo "$r $g $b" | tr ' ' '\n' | sort -n | head -n1)
    
    # Calculate lightness
    local l
    l=$(echo "scale=6; ($max + $min)/2" | bc)
    
    # If max equals min, we have a shade of gray
    if (( $(echo "$max == $min" | bc -l) )); then
        echo "0 0 $l"
        return
    fi
    
    # Calculate saturation
    local s
    if (( $(echo "$l <= 0.5" | bc -l) )); then
        s=$(echo "scale=6; ($max - $min)/($max + $min)" | bc)
    else
        s=$(echo "scale=6; ($max - $min)/(2 - $max - $min)" | bc)
    fi
    
    # Calculate hue
    local h
    if (( $(echo "$r == $max" | bc -l) )); then
        h=$(echo "scale=6; ($g - $b)/($max - $min)" | bc)
    elif (( $(echo "$g == $max" | bc -l) )); then
        h=$(echo "scale=6; 2 + ($b - $r)/($max - $min)" | bc)
    else
        h=$(echo "scale=6; 4 + ($r - $g)/($max - $min)" | bc)
    fi
    
    h=$(echo "scale=6; $h * 60" | bc)
    if (( $(echo "$h < 0" | bc -l) )); then
        h=$(echo "scale=6; $h + 360" | bc)
    fi
    
    echo "$h $s $l"
}

# Convert HSL to RGB
# Usage: hsl_to_rgb 180 0.5 0.5
hsl_to_rgb() {
    local h=$1
    local s=$2
    local l=$3
    
    # If saturation is 0, it's a shade of gray
    if (( $(echo "$s == 0" | bc -l) )); then
        local gray
        gray=$(echo "scale=0; $l * 255" | bc)
        echo "$gray $gray $gray"
        return
    fi
    
    # Helper function for hue to RGB
    hue_to_rgb() {
        local p=$1
        local q=$2
        local t=$3
        
        if (( $(echo "$t < 0" | bc -l) )); then
            t=$(echo "scale=6; $t + 1" | bc)
        fi
        if (( $(echo "$t > 1" | bc -l) )); then
            t=$(echo "scale=6; $t - 1" | bc)
        fi
        
        if (( $(echo "$t < 1/6" | bc -l) )); then
            echo "scale=6; $p + ($q - $p) * 6 * $t" | bc
            return
        fi
        if (( $(echo "$t < 1/2" | bc -l) )); then
            echo "$q"
            return
        fi
        if (( $(echo "$t < 2/3" | bc -l) )); then
            echo "scale=6; $p + ($q - $p) * (2/3 - $t) * 6" | bc
            return
        fi
        echo "$p"
    }
    
    local q
    if (( $(echo "$l < 0.5" | bc -l) )); then
        q=$(echo "scale=6; $l * (1 + $s)" | bc)
    else
        q=$(echo "scale=6; $l + $s - $l * $s" | bc)
    fi
    local p
    p=$(echo "scale=6; 2 * $l - $q" | bc)
    
    local h_norm
    h_norm=$(echo "scale=6; $h/360" | bc)
    
    local r g b
    r=$(hue_to_rgb "$p" "$q" $(echo "scale=6; $h_norm + 1/3" | bc))
    g=$(hue_to_rgb "$p" "$q" "$h_norm")
    b=$(hue_to_rgb "$p" "$q" $(echo "scale=6; $h_norm - 1/3" | bc))
    
    # Convert to 0-255 range
    r=$(echo "scale=0; $r * 255" | bc)
    g=$(echo "scale=0; $g * 255" | bc)
    b=$(echo "scale=0; $b * 255" | bc)
    
    echo "$r $g $b"
}

# Generate complementary color
# Usage: get_complementary_color 180 0.5 0.5
get_complementary_color() {
    local h=$1
    local s=$2
    local l=$3
    
    local comp_h
    comp_h=$(echo "scale=0; ($h + 180) % 360" | bc)
    echo "$comp_h $s $l"
}

# Generate analogous colors
# Usage: get_analogous_colors 180 0.5 0.5
get_analogous_colors() {
    local h=$1
    local s=$2
    local l=$3
    
    local left_h right_h
    left_h=$(echo "scale=0; ($h - 30 + 360) % 360" | bc)
    right_h=$(echo "scale=0; ($h + 30) % 360" | bc)
    echo "$left_h $s $l"
    echo "$right_h $s $l"
}

# Convert RGB to terminal color code
# Usage: rgb_to_terminal 255 128 0
rgb_to_terminal() {
    local r=$1
    local g=$2
    local b=$3
    echo -e "\033[38;2;${r};${g};${b}m"
}

# Convert RGB to terminal background color code
# Usage: rgb_to_terminal_bg 255 128 0
rgb_to_terminal_bg() {
    local r=$1
    local g=$2
    local b=$3
    echo -e "\033[48;2;${r};${g};${b}m"
}
