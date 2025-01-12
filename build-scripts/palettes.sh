#!/bin/bash

# Source color utilities
source "$(dirname "${BASH_SOURCE[0]}")/colors.sh"

# Palette Generators
generate_monochromatic_palette() {
    local base_h=$1
    local base_s=${2:-0.5}
    local base_l=${3:-0.5}
    
    declare -A palette
    
    # Generate 5 shades
    palette[primary]=$(hsl_to_rgb "$base_h" "$base_s" "$base_l")
    palette[light]=$(hsl_to_rgb "$base_h" "$base_s" $(echo "scale=6; $base_l + 0.2" | bc))
    palette[lighter]=$(hsl_to_rgb "$base_h" "$base_s" $(echo "scale=6; $base_l + 0.4" | bc))
    palette[dark]=$(hsl_to_rgb "$base_h" "$base_s" $(echo "scale=6; $base_l - 0.2" | bc))
    palette[darker]=$(hsl_to_rgb "$base_h" "$base_s" $(echo "scale=6; $base_l - 0.4" | bc))
    
    declare -p palette
}

generate_complementary_palette() {
    local base_h=$1
    local base_s=${2:-0.5}
    local base_l=${3:-0.5}
    
    declare -A palette
    
    # Primary colors
    palette[primary]=$(hsl_to_rgb "$base_h" "$base_s" "$base_l")
    palette[primary_light]=$(hsl_to_rgb "$base_h" "$base_s" $(echo "scale=6; $base_l + 0.2" | bc))
    palette[primary_dark]=$(hsl_to_rgb "$base_h" "$base_s" $(echo "scale=6; $base_l - 0.2" | bc))
    
    # Complementary colors
    local comp_h
    comp_h=$(echo "scale=0; ($base_h + 180) % 360" | bc)
    palette[complement]=$(hsl_to_rgb "$comp_h" "$base_s" "$base_l")
    palette[complement_light]=$(hsl_to_rgb "$comp_h" "$base_s" $(echo "scale=6; $base_l + 0.2" | bc))
    palette[complement_dark]=$(hsl_to_rgb "$comp_h" "$base_s" $(echo "scale=6; $base_l - 0.2" | bc))
    
    declare -p palette
}

generate_triadic_palette() {
    local base_h=$1
    local base_s=${2:-0.5}
    local base_l=${3:-0.5}
    
    declare -A palette
    
    # Primary colors
    palette[primary]=$(hsl_to_rgb "$base_h" "$base_s" "$base_l")
    
    # Triadic colors
    local triad1_h triad2_h
    triad1_h=$(echo "scale=0; ($base_h + 120) % 360" | bc)
    triad2_h=$(echo "scale=0; ($base_h + 240) % 360" | bc)
    
    palette[triad1]=$(hsl_to_rgb "$triad1_h" "$base_s" "$base_l")
    palette[triad2]=$(hsl_to_rgb "$triad2_h" "$base_s" "$base_l")
    
    declare -p palette
}

# Predefined Palettes
PALETTE_OCEAN=$(generate_complementary_palette 200 0.7 0.5)
PALETTE_FOREST=$(generate_complementary_palette 120 0.6 0.4)
PALETTE_SUNSET=$(generate_triadic_palette 30 0.8 0.5)
PALETTE_BERRY=$(generate_complementary_palette 330 0.7 0.4)
PALETTE_MONO_BLUE=$(generate_monochromatic_palette 210 0.6 0.5)
