# src/api_docs/build.py
from pathlib import Path

def generate_meson_build(project_root: Path) -> None:
    """Generate meson.build file with documentation support."""
    meson_content = """
project('api-docs', 'python',
        version: '0.1.0',
        default_options: ['warning_level=3'])

python = import('python').find_installation()

# Documentation generation
sphinx = find_program('sphinx-build', required: false)
if sphinx.found()
    custom_target('docs',
                 output: 'html',
                 input: 'docs/source/conf.py',
                 command: [sphinx, '-b', 'html', 'docs/source', '@OUTPUT@'],
                 build_by_default: true)
endif
"""
    with open(project_root / 'meson.build', 'w') as f:
        f.write(meson_content)

def update_pyproject_toml(project_root: Path) -> None:
    """Update pyproject.toml with build system configurations."""
    content = """
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "api-docs"
version = "0.1.0"
dependencies = [
    "sphinx>=4.0",
    "myst-parser",
    "sphinx-rtd-theme"
]
"""
    with open(project_root / 'pyproject.toml', 'w') as f:
        f.write(content)

def setup_sphinx(project_root: Path) -> None:
    """Setup Sphinx documentation configuration."""
    docs_path = project_root / 'docs' / 'source'
    docs_path.mkdir(parents=True, exist_ok=True)
    
    sphinx_config = """
project = 'API Documentation'
copyright = '2024, Your Name'
author = 'Your Name'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'myst_parser'
]

templates_path = ['_templates']
exclude_patterns = []
html_theme = 'sphinx_rtd_theme'
"""
    
    with open(docs_path / 'conf.py', 'w') as f:
        f.write(sphinx_config)

def initialize_project(root_dir: str = '.') -> None:
    """Initialize project with documentation and build system setup."""
    project_root = Path(root_dir)
    
    # Create necessary directories
    (project_root / 'src' / 'api_docs').mkdir(parents=True, exist_ok=True)
    (project_root / 'docs' / 'source' / 'api').mkdir(parents=True, exist_ok=True)
    (project_root / 'docs' / 'source' / 'errors').mkdir(parents=True, exist_ok=True)
    
    # Generate build files
    generate_meson_build(project_root)
    update_pyproject_toml(project_root)
    setup_sphinx(project_root)
    
    # Create README
    with open(project_root / 'README.md', 'w') as f:
        f.write("# API Documentation System\n\nA comprehensive documentation system.")