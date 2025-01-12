"""
Build system integration for documentation and error handling.
"""
from pathlib import Path
import tomli
import tomli_w

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
    config = {
        'build-system': {
            'requires': [
                'hatchling',
                'scikit-build-core',
                'meson-python',
            ],
            'build-backend': 'hatchling.build'
        },
        'project': {
            'name': 'api-docs',
            'version': '0.1.0',
            'description': 'API documentation and error handling system',
            'requires-python': '>=3.8',
            'dependencies': [
                'sphinx',
                'sphinx-autodoc-typehints',
                'myst-parser',
                'tomli',
                'tomli-w',
            ],
        },
        'tool': {
            'hatch': {
                'build': {
                    'hooks': {
                        'post': [
                            'python -m sphinx.cmd.build docs/source docs/build/html'
                        ]
                    }
                }
            },
            'scikit-build': {
                'wheel': {
                    'packages': ['src/api_docs']
                },
                'cmake': {
                    'build-type': 'Release'
                }
            }
        }
    }
    
    with open(project_root / 'pyproject.toml', 'w') as f:
        tomli_w.dump(config, f)

def setup_sphinx(project_root: Path) -> None:
    """Setup Sphinx documentation configuration."""
    sphinx_config = """
project = 'API Documentation'
copyright = '2024, Your Name'
author = 'Your Name'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'sphinx_autodoc_typehints',
    'myst_parser',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'furo'
html_static_path = ['_static']

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
}

autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_numpy_docstring = True
"""
    
    docs_path = project_root / 'docs' / 'source'
    docs_path.mkdir(parents=True, exist_ok=True)
    
    with open(docs_path / 'conf.py', 'w') as f:
        f.write(sphinx_config)

def create_documentation_structure(project_root: Path) -> None:
    """Create initial documentation structure."""
    docs_structure = {
        'api': {'index.md': '# API Reference\n'},
        'errors': {'index.md': '# Error Reference\n'},
        'guides': {
            'index.md': '# Developer Guides\n',
            'error_handling.md': '# Error Handling Guide\n',
            'logging.md': '# Logging Guide\n'
        }
    }
    
    docs_root = project_root / 'docs' / 'source'
    
    for category, files in docs_structure.items():
        category_path = docs_root / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        for filename, content in files.items():
            with open(category_path / filename, 'w') as f:
                f.write(content)

def initialize_project(root_dir: str = '.') -> None:
    """Initialize project with documentation and build system setup."""
    project_root = Path(root_dir)
    
    # Create project structure
    (project_root / 'src' / 'api_docs').mkdir(parents=True, exist_ok=True)
    
    # Generate build files
    generate_meson_build(project_root)
    update_pyproject_toml(project_root)
    setup_sphinx(project_root)
    create_documentation_structure(project_root)
    
    # Create initial README
    readme_content = """# API Documentation System

A comprehensive system for API documentation, error handling, and logging.

## Features

- Automatic API documentation generation
- Error handling with documentation
- Logging system
- Multiple build system support (meson, hatch, scikit-build)

## Building

```bash
# Using meson
meson setup builddir
meson compile -C builddir

# Using hatch
hatch build

# Using pip with scikit-build
pip install .
```

## Documentation

Documentation is available in the `docs/` directory and can be built using:

```bash
sphinx-build docs/source docs/build/html
```
"""
    
    with open(project_root / 'README.md', 'w') as f:
        f.write(readme_content)

if __name__ == '__main__':
    initialize_project()
