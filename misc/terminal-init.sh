#!/bin/bash

# Function to get screen dimensions
get_screen_dimensions() {
    local screen_width=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f1)
    local screen_height=$(xrandr --current | grep '*' | uniq | awk '{print $1}' | cut -d 'x' -f2)
    echo "$screen_width $screen_height"
}

# Function to calculate window dimensions (half of screen)
get_window_dimensions() {
    read screen_width screen_height <<< $(get_screen_dimensions)
    local window_width=$((screen_width / 2 - 20))  # Subtract some pixels for borders
    local window_height=$((screen_height / 2 - 20))
    echo "$window_width $window_height"
}

# Function to position a window
position_window() {
    local window_id=$1
    local x_pos=$2
    local y_pos=$3
    local width=$4
    local height=$5
    
    # Wait for window to be ready
    sleep 0.5
    
    # Unmaximize and remove fullscreen
    xdotool windowstate --remove MAXIMIZED_VERT --remove MAXIMIZED_HORZ "$window_id"
    xdotool windowstate --remove FULLSCREEN "$window_id"
    
    # Force window size and position
    xdotool windowsize --sync "$window_id" "$width" "$height"
    xdotool windowmove --sync "$window_id" "$x_pos" "$y_pos"
    
    # Ensure window is active and properly sized
    xdotool windowactivate "$window_id"
    xdotool windowsize --sync "$window_id" "$width" "$height"
}

# Function to open and position a terminal
setup_terminal() {
    local x_pos=$1
    local y_pos=$2
    local width=$3
    local height=$4
    
    # Open terminal with default size
    gnome-terminal --geometry=80x24 &
    sleep 0.5
    
    # Get the window ID of the most recently opened terminal
    local window_id=$(xdotool search --sync --pid $! --class "gnome-terminal" | tail -n1)
    
    # Position and size the window
    position_window "$window_id" "$x_pos" "$y_pos" "$width" "$height"
}

main() {
    # Check for required tools
    if ! command -v xdotool &> /dev/null || ! command -v gnome-terminal &> /dev/null; then
        echo "Error: Required tools not found. Please install xdotool and gnome-terminal:"
        echo "sudo apt-get install xdotool gnome-terminal"
        exit 1
    fi
    
    # Get dimensions
    read window_width window_height <<< $(get_window_dimensions)
    read screen_width screen_height <<< $(get_screen_dimensions)
    
    # Calculate positions (add small gaps)
    local right_x=$((screen_width - window_width - 10))
    local bottom_y=$((screen_height - window_height - 10))
    
    # Setup terminals in each corner
    setup_terminal 10 10 "$window_width" "$window_height"                # Top-left
    setup_terminal "$right_x" 10 "$window_width" "$window_height"       # Top-right
    setup_terminal 10 "$bottom_y" "$window_width" "$window_height"      # Bottom-left
    setup_terminal "$right_x" "$bottom_y" "$window_width" "$window_height" # Bottom-right
}

# Run main function
main
