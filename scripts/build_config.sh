#!/bin/bash

# Initialize variables before setting options
current_command=""
last_command=""

# Exit on error and undefined variables
set -eu

# Setup logging
LOG_FILE="setup_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE")
exec 2> >(tee -a "$LOG_FILE" >&2)

# Color output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() { echo -e "${BLUE}[INFO]${NC} $*" ;}
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $*" ;}
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $*" ;}
log_error() { echo -e "${RED}[ERROR]${NC} $*" ;}

# Error handler
trap 'last_command=$current_command; current_command=$BASH_COMMAND' DEBUG
trap 'if [ $? -ne 0 ]; then log_error "Command \"${last_command}\" failed with exit code $?. Check ${LOG_FILE} for details."; fi' EXIT

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to get Python version
get_python_version() {
    python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")' 2>/dev/null || echo "0.0"
}

# Function to install system packages
install_system_packages() {
    log_info "Detecting Linux Mint/Ubuntu-based system"
    
    # Update package lists
    log_info "Updating package lists..."
    sudo apt-get update -qq || {
        log_error "Failed to update package lists"
        return 1
    }
    
    # Install required packages
    log_info "Installing system packages..."
    sudo apt-get install -y \
        python3-dev \
        python3-pip \
        python3-venv \
        python3-full \
        git \
        build-essential \
        ninja-build \
        pkg-config \
        libblas-dev \
        liblapack-dev \
        libopenblas-dev \
        gfortran \
        libatlas-base-dev \
        libffi-dev \
        zlib1g-dev \
        liblzma-dev \
        libbz2-dev \
        libssl-dev \
        libsqlite3-dev \
        libreadline-dev \
        libncurses5-dev \
        libncursesw5-dev \
        xz-utils \
        tk-dev || {
        log_error "Failed to install system packages"
        return 1
    }
}

# Main setup function
main() {
    log_info "Starting scientific Python build environment setup..."
    
    # Check Python version
    PYTHON_VERSION=$(get_python_version)
    log_info "Found Python version: $PYTHON_VERSION"
    if [ "$(echo "$PYTHON_VERSION" | cut -d. -f1)" -lt 3 ] || [ "$(echo "$PYTHON_VERSION" | cut -d. -f2)" -lt 8 ]; then
        log_error "Python 3.8 or higher is required"
        exit 1
    fi
    
    # Install system packages
    install_system_packages
    
    # Create project structure
    PROJECT_NAME="scientific-project"
    log_info "Creating project structure: $PROJECT_NAME"
    mkdir -p "$PROJECT_NAME"
    cd "$PROJECT_NAME" || exit 1
    
    # Create and activate virtual environment
    log_info "Creating virtual environment..."
    python3 -m venv .venv || {
        log_error "Failed to create virtual environment"
        exit 1
    }
    
    # shellcheck disable=SC1091
    source .venv/bin/activate || {
        log_error "Failed to activate virtual environment"
        exit 1
    }
    
    # Verify virtual environment activation
    if [ -z "${VIRTUAL_ENV:-}" ]; then
        log_error "Virtual environment not activated"
        exit 1
    fi
    
    # Upgrade pip and install build tools
    log_info "Upgrading pip and installing build tools..."
    python3 -m pip install --upgrade pip || log_error "Failed to upgrade pip"
    
    python3 -m pip install -v \
        pdm \
        meson \
        meson-python \
        scikit-build \
        scikit-build-core \
        ninja \
        wheel \
        build \
        setuptools || {
        log_error "Failed to install build tools"
        exit 1
    }
    
    # Initialize PDM project
    log_info "Initializing PDM project..."
    VENV_PYTHON="$VIRTUAL_ENV/bin/python"
    pdm init --python "$VENV_PYTHON" -n || {
        log_error "Failed to initialize PDM project"
        exit 1
    }
    
    # Create pyproject.toml
    cat > pyproject.toml << 'EOL'
[build-system]
requires = [
    "pdm-backend",
    "meson-python",
    "scikit-build-core",
    "numpy",
]
build-backend = "pdm.backend"

[project]
name = "scientific-project"
version = "0.1.0"
description = "Scientific computing project with hybrid build system"
requires-python = ">=3.8"
dependencies = [
    "numpy>=1.24.0",
    "scipy>=1.9.0",
    "pandas>=2.0.0",
]

[tool.pdm]
build = {includes = ["src", "lib"]}

[tool.pdm.dev-dependencies]
test = [
    "pytest>=7.0",
    "pytest-cov>=3.0",
]
lint = [
    "ruff>=0.1.0",
    "black>=22.0",
]

[tool.scikit-build]
wheel.expand-macos-universal-tags = true
build-dir = "build/{wheel_tag}"
EOL
    
    # Setup environment for compilation
    export CFLAGS="-I/usr/include/atlas -I$(pwd)/.venv/include"
    export CPPFLAGS="$CFLAGS"
    export LDFLAGS="-L/usr/lib/atlas-base -L$(pwd)/.venv/lib"
    export ATLAS=/usr/lib/atlas-base/libatlas.so
    export BLAS=/usr/lib/atlas-base/libblas.so
    export LAPACK=/usr/lib/atlas-base/liblapack.so
    
    # Install dependencies with PDM
    log_info "Installing project dependencies..."
    
    # Install numpy first
    log_info "Installing numpy..."
    pdm add --verbose "numpy>=1.24.0" || log_error "Failed to install numpy"
    
    # Install scipy
    log_info "Installing scipy..."
    pdm add --verbose "scipy>=1.9.0" || log_error "Failed to install scipy"
    
    # Install pandas
    log_info "Installing pandas..."
    pdm add --verbose "pandas>=2.0.0" || log_error "Failed to install pandas"
    
    # Setup source and test directories
    mkdir -p src tests
    
    # Create initial Python module
    cat > src/__init__.py << 'EOL'
"""Scientific project main module."""
__version__ = "0.1.0"
EOL
    
    # Create test directory
    cat > tests/__init__.py << 'EOL'
"""Test suite for scientific project."""
EOL
    
    # Initialize git repository
    git init
    cat > .gitignore << 'EOL'
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.pdm.toml
.pdm-python
.venv/
.env
.log
EOL
    
    log_success "Build environment setup complete!"
    log_info "Project created at: $(pwd)"
    log_info "Log file: $LOG_FILE"
    echo
    log_info "To activate the environment:"
    echo "source .venv/bin/activate"
    echo
    log_info "Next steps:"
    echo "1. cd $PROJECT_NAME"
    echo "2. Add your source code to src/"
    echo "3. Add tests to tests/"
    echo "4. Build with: pdm build"
    echo "5. Run tests with: pdm run pytest"
}

# Run main function
main "$@"
