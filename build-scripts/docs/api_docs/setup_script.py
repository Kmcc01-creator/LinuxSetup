#!/usr/bin/env python3
"""
Setup script for creating the project structure.
"""
from pathlib import Path
import os

def create_directory_structure():
    # Create main directories
    directories = [
        'src/api_docs',
        'tests',
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def create_files():
    # Create empty __init__.py files
    init_files = [
        'src/api_docs/__init__.py',
        'tests/__init__.py',
    ]
    
    for init_file in init_files:
        Path(init_file).touch()

    # Create pyproject.toml
    with open('pyproject.toml', 'w') as f:
        f.write('''[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "api_docs"
version = "0.1.0"
dependencies = [
    "pytest>=7.0",
]
''')

    # Create setup.cfg
    with open('setup.cfg', 'w') as f:
        f.write('''[metadata]
name = api_docs
version = 0.1.0

[options]
package_dir =
    = src
packages = find:

[options.packages.find]
where = src
''')

def main():
    create_directory_structure()
    create_files()
    print("Project structure created successfully!")

if __name__ == '__main__':
    main()
