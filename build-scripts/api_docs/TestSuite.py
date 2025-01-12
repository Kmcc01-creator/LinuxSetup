"""
Test suite for the documentation and error handling system.
"""
import pytest
import logging
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from api_docs.core import (
    DocFormat,
    APIError,
    ErrorRegistry,
    DocGenerator,
    api_logger
)
from api_docs.build import (
    generate_meson_build,
    update_pyproject_toml,
    setup_sphinx,
    initialize_project
)

# Fixtures
@pytest.fixture
def temp_dir():
    """Provide a temporary directory for test files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def doc_generator():
    """Provide a DocGenerator instance."""
    return DocGenerator(format=DocFormat.RST)

@pytest.fixture
def sample_module():
    """Create a sample module for documentation testing."""
    class SampleClass:
        """Sample class docstring."""
        def sample_method(self, param: str) -> str:
            """Sample method docstring."""
            return param

    def sample_function(param: int) -> int:
        """Sample function docstring."""
        return param

    mock_module = Mock()
    mock_module.SampleClass = SampleClass
    mock_module.sample_function = sample_function
    return mock_module

# Error Handling Tests
class TestErrorHandling:
    def test_api_error_creation(self):
        """Test APIError instantiation."""
        error = APIError(code=404, message="Not Found")
        assert error.code == 404
        assert error.message == "Not Found"
        assert error.details is None

    def test_error_registry_registration(self):
        """Test error registration in ErrorRegistry."""
        @ErrorRegistry.register(404)
        class TestError(APIError):
            """Test error class."""
            code = 404

        assert ErrorRegistry._errors[404] == TestError

    def test_error_documentation_generation(self, temp_dir):
        """Test error documentation generation."""
        with patch('builtins.open') as mock_open:
            @ErrorRegistry.register(500)
            class ServerError(APIError):
                """Server error class."""
                code = 500

            mock_open.assert_called()
            # Verify documentation content would be written

# Documentation Generator Tests
class TestDocGenerator:
    def test_rst_doc_generation(self, doc_generator, sample_module):
        """Test RST documentation generation."""
        doc = doc_generator.generate_api_docs(sample_module)
        assert "SampleClass" in doc
        assert "sample_method" in doc
        assert "sample_function" in doc
        assert "Sample class docstring" in doc

    def test_markdown_doc_generation(self, sample_module):
        """Test Markdown documentation generation."""
        md_generator = DocGenerator(format=DocFormat.MARKDOWN)
        doc = md_generator.generate_api_docs(sample_module)
        assert "# SampleClass" in doc
        assert "### `sample_method" in doc
        assert "Sample class docstring" in doc

    def test_invalid_format(self):
        """Test invalid documentation format handling."""
        with pytest.raises(ValueError):
            DocGenerator(format="invalid")

# Logging Tests
def test_api_logger():
    """Test API logging decorator."""
    test_logger = logging.getLogger("test")
    test_logger.addHandler(logging.NullHandler())

    @api_logger
    def test_function(param):
        return f"Test: {param}"

    with patch.object(test_logger, 'info') as mock_info:
        result = test_function("test_param")
        assert result == "Test: test_param"
        mock_info.assert_called()

def test_api_logger_error():
    """Test API logging decorator error handling."""
    test_logger = logging.getLogger("test")
    test_logger.addHandler(logging.NullHandler())

    @api_logger
    def error_function():
        raise ValueError("Test error")

    with patch.object(test_logger, 'error') as mock_error:
        with pytest.raises(ValueError):
            error_function()
        mock_error.assert_called()

# Build System Tests
class TestBuildSystem:
    def test_meson_build_generation(self, temp_dir):
        """Test meson.build file generation."""
        generate_meson_build(temp_dir)
        assert (temp_dir / 'meson.build').exists()
        with open(temp_dir / 'meson.build') as f:
            content = f.read()
            assert "project('api-docs'" in content
            assert "sphinx" in content

    def test_pyproject_toml_generation(self, temp_dir):
        """Test pyproject.toml generation."""
        update_pyproject_toml(temp_dir)
        assert (temp_dir / 'pyproject.toml').exists()
        # Verify content with tomli

    def test_sphinx_setup(self, temp_dir):
        """Test Sphinx configuration setup."""
        setup_sphinx(temp_dir)
        assert (temp_dir / 'docs' / 'source' / 'conf.py').exists()

    def test_project_initialization(self, temp_dir):
        """Test complete project initialization."""
        initialize_project(temp_dir)
        assert (temp_dir / 'src' / 'api_docs').exists()
        assert (temp_dir / 'docs' / 'source').exists()
        assert (temp_dir / 'pyproject.toml').exists()
        assert (temp_dir / 'meson.build').exists()
        assert (temp_dir / 'README.md').exists()

# Integration Tests
class TestIntegration:
    def test_full_documentation_workflow(self, temp_dir, sample_module):
        """Test complete documentation workflow."""
        # Initialize project
        initialize_project(temp_dir)

        # Generate documentation
        doc_generator = DocGenerator(format=DocFormat.RST)
        docs = doc_generator.generate_api_docs(sample_module)

        # Verify documentation files
        docs_path = temp_dir / 'docs' / 'source' / 'api'
        assert docs_path.exists()

    def test_error_handling_with_docs(self, temp_dir):
        """Test error handling with documentation integration."""
        initialize_project(temp_dir)

        @ErrorRegistry.register(400)
        class BadRequestError(APIError):
            """Bad request error."""
            code = 400

        # Verify error documentation was generated
        error_docs_path = temp_dir / 'docs' / 'source' / 'errors'
        assert error_docs_path.exists()

if __name__ == '__main__':
    pytest.main([__file__])
