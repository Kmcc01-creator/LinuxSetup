#!/bin/bash

# Update package lists
echo "Updating package lists..."
sudo apt-get update

# Install Python development files
echo "Installing Python development files..."
sudo apt-get install -y python3-dev python3-pip

# Install OpenGL dependencies
echo "Installing OpenGL dependencies..."
sudo apt-get install -y \
    libgl1-mesa-dev \
    libgles2-mesa-dev \
    libglfw3-dev \
    libglew-dev

# Install SDL2 dependencies
echo "Installing SDL2 dependencies..."
sudo apt-get install -y \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-ttf-dev

# Install FreeType and text-related dependencies
echo "Installing FreeType and text dependencies..."
sudo apt-get install -y \
    libfreetype6-dev \
    libharfbuzz-dev \
    libfribidi-dev

# Install Python packages
echo "Installing Python packages..."
pip3 install --upgrade pip
pip3 install \
    numpy \
    pysdl2 \
    pyopengl \
    freetype-py \
    pillow \
    pygame

# Verify installations
echo "Verifying installations..."
python3 -c "import OpenGL; import sdl2; import freetype; print('All core packages installed successfully!')"

echo "Installation complete! Your system is ready for graphics development."
