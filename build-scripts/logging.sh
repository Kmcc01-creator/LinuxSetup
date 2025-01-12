#!/bin/bash

# Source the color utilities
source "$(dirname "${BASH_SOURCE[0]}")/colors.sh"

# Logging Configuration
declare -A LOG_LEVELS=(
    ["DEBUG"]=0
    ["INFO"]=1
    ["WARNING"]=2
    ["ERROR"]=3
    ["CRITICAL"]=4
)

# Default configuration
CURRENT_LOG_LEVEL=${LOG_LEVEL:-"INFO"}
LOG_FILE=${LOG_FILE:-"build_$(date +%Y%m%d_%H%M%S).log"}
LOG_TO_FILE=${LOG_TO_FILE:-true}
LOG_TO_STDOUT=${LOG_TO_STDOUT:-true}

# Check for true color support
check_true_color() {
    if [ "$COLORTERM" = "truecolor" ] || [ "$COLORTERM" = "24bit" ]; then
        return 0
    fi
    
    case "$TERM" in
        *-24bit|*-direct|*-truecolor)
            return 0
            ;;
    esac
    
    # Additional checks for specific terminals that support true color
    case "$TERM_PROGRAM" in
        iTerm.app|vscode|WezTerm|Alacritty|kitty)
            return 0
            ;;
    esac
    
    return 1
}

# Initialize logging system
init_logging() {
    # Check for true color support
    if ! check_true_color; then
        log_warning "Terminal does not support true color. Color output may be limited."
        track_error "COLOR_DISPLAY" "Terminal doesn't support true color"
    fi
    local log_dir
    log_dir=$(dirname "$LOG_FILE")
    
    # Create log directory if it doesn't exist
    if [[ ! -d "$log_dir" ]]; then
        mkdir -p "$log_dir"
    fi
    
    # Initialize log file with header
    if [[ "$LOG_TO_FILE" = true ]]; then
        {
            echo "=== Log Start ==="
            echo "Date: $(date)"
            echo "System: $(uname -a)"
            echo "================="
            echo
        } > "$LOG_FILE"
    fi
}

# Format timestamp for log entries
get_timestamp() {
    date "+%Y-%m-%d %H:%M:%S"
}

# Check if a log level should be processed
should_log() {
    local level=$1
    [[ ${LOG_LEVELS[$level]} -ge ${LOG_LEVELS[$CURRENT_LOG_LEVEL]} ]]
}

# Internal logging function
_log() {
    local level=$1
    local message=$2
    local timestamp
    local color_code
    local reset_code
    
    if ! should_log "$level"; then
        return 0
    fi
    
    timestamp=$(get_timestamp)
    
    # Set color based on log level
    case $level in
        "DEBUG")
            color_code=$(rgb_to_terminal 150 150 150)  # Gray
            ;;
        "INFO")
            color_code=$(rgb_to_terminal 0 150 255)    # Light Blue
            ;;
        "WARNING")
            color_code=$(rgb_to_terminal 255 150 0)    # Orange
            ;;
        "ERROR")
            color_code=$(rgb_to_terminal 255 50 50)    # Red
            ;;
        "CRITICAL")
            # Background color for critical
            color_code=$(rgb_to_terminal_bg 255 0 0)$(rgb_to_terminal 255 255 255)
            ;;
    esac
    
    reset_code='\033[0m'
    
    # Format the log message
    local formatted_message="[$timestamp] ${color_code}${level}${reset_code}: $message"
    local file_message="[$timestamp] ${level}: $message"
    
    # Write to stdout if enabled
    if [[ "$LOG_TO_STDOUT" = true ]]; then
        echo -e "$formatted_message"
    fi
    
    # Write to file if enabled
    if [[ "$LOG_TO_FILE" = true ]]; then
        echo "$file_message" >> "$LOG_FILE"
    fi
}

# Public logging functions
log_debug() {
    _log "DEBUG" "$*"
}

log_info() {
    _log "INFO" "$*"
}

log_warning() {
    _log "WARNING" "$*"
}

log_error() {
    _log "ERROR" "$*"
}

log_critical() {
    _log "CRITICAL" "$*"
}

# Function to change log level
set_log_level() {
    local new_level=$1
    if [[ -n "${LOG_LEVELS[$new_level]}" ]]; then
        CURRENT_LOG_LEVEL=$new_level
        log_info "Log level changed to: $new_level"
    else
        log_error "Invalid log level: $new_level"
        return 1
    fi
}

# Function to rotate log file
rotate_log() {
    if [[ "$LOG_TO_FILE" != true ]]; then
        return 0
    fi
    
    local max_size=${1:-$((10 * 1024 * 1024))}  # Default 10MB
    local current_size
    
    if [[ -f "$LOG_FILE" ]]; then
        current_size=$(stat -f%z "$LOG_FILE" 2>/dev/null || stat -c%s "$LOG_FILE")
        
        if ((current_size > max_size)); then
            local timestamp
            timestamp=$(date +%Y%m%d_%H%M%S)
            local rotated_file="${LOG_FILE%.*}_${timestamp}.log"
            
            mv "$LOG_FILE" "$rotated_file"
            gzip "$rotated_file" &  # Compress in background
            
            init_logging
            log_info "Log file rotated to: $rotated_file"
        fi
    fi
}

# Error tracking functions
declare -A ERROR_COUNTS
declare -A LAST_ERRORS

track_error() {
    local error_type=$1
    local error_message=$2
    
    # Increment error count
    ERROR_COUNTS[$error_type]=$((${ERROR_COUNTS[$error_type]:-0} + 1))
    
    # Store last error message
    LAST_ERRORS[$error_type]=$error_message
    
    # Log the error
    log_error "[$error_type] $error_message"
}

get_error_summary() {
    local output=""
    
    for error_type in "${!ERROR_COUNTS[@]}"; do
        local count=${ERROR_COUNTS[$error_type]}
        local last_message=${LAST_ERRORS[$error_type]}
        output+="$error_type: $count occurrences (Last: $last_message)"$'\n'
    done
    
    echo "$output"
}

# Initialize logging when the script is sourced
init_logging
