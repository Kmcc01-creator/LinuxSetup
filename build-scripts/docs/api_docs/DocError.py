"""
Core system for documentation generation and error handling.
Integrates with meson, hatch, and scikit-build.
"""
import enum
import functools
import inspect
import logging
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, Union

class DocFormat(enum.Enum):
    """Documentation format types."""
    RST = "rst"
    MARKDOWN = "md"
    NUMPY = "numpy"
    GOOGLE = "google"

@dataclass
class APIError:
    """Base class for API errors with documentation integration."""
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None
    doc_ref: Optional[str] = None  # Reference to error documentation

class ErrorRegistry:
    """Registry for API errors with documentation generation."""
    _errors: Dict[int, Type[APIError]] = {}
    
    @classmethod
    def register(cls, error_code: int) -> Callable:
        """Register an error class with documentation."""
        def wrapper(error_cls: Type[APIError]) -> Type[APIError]:
            cls._errors[error_code] = error_cls
            # Generate error documentation
            cls._generate_error_doc(error_cls)
            return error_cls
        return wrapper
    
    @classmethod
    def _generate_error_doc(cls, error_cls: Type[APIError]) -> None:
        """Generate documentation for error class."""
        doc_path = Path("docs/errors")
        doc_path.mkdir(parents=True, exist_ok=True)
        
        with open(doc_path / f"{error_cls.__name__.lower()}.md", "w") as f:
            f.write(f"# {error_cls.__name__}\n\n")
            f.write(f"Error Code: {error_cls.code}\n\n")
            f.write(f"Description: {error_cls.__doc__}\n\n")
            f.write("## Usage\n\n")
            f.write("```python\n")
            f.write(f"raise {error_cls.__name__}(message='Example error')\n")
            f.write("```\n")

class DocGenerator:
    """Documentation generator with build system integration."""
    
    def __init__(self, format: DocFormat = DocFormat.RST):
        self.format = format
        self.logger = logging.getLogger(__name__)
    
    def generate_api_docs(self, module: Any) -> str:
        """Generate API documentation for a module."""
        doc_content = []
        
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) or inspect.isfunction(obj):
                doc = self._generate_doc(obj)
                doc_content.append(doc)
        
        return "\n\n".join(doc_content)
    
    def _generate_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate documentation for a class or function."""
        if self.format == DocFormat.RST:
            return self._generate_rst_doc(obj)
        elif self.format == DocFormat.MARKDOWN:
            return self._generate_md_doc(obj)
        else:
            raise ValueError(f"Unsupported format: {self.format}")
    
    def _generate_rst_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate RST documentation."""
        doc = [f"{obj.__name__}\n{'=' * len(obj.__name__)}\n"]
        
        if obj.__doc__:
            doc.append(obj.__doc__.strip())
        
        if inspect.isclass(obj):
            # Document methods
            for name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    sig = inspect.signature(method)
                    doc.append(f"\n.. method:: {name}{sig}\n")
                    if method.__doc__:
                        doc.append(f"   {method.__doc__.strip()}\n")
        
        return "\n".join(doc)
    
    def _generate_md_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate Markdown documentation."""
        doc = [f"# {obj.__name__}\n"]
        
        if obj.__doc__:
            doc.append(obj.__doc__.strip())
        
        if inspect.isclass(obj):
            doc.append("\n## Methods\n")
            for name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    sig = inspect.signature(method)
                    doc.append(f"\n### `{name}{sig}`\n")
                    if method.__doc__:
                        doc.append(method.__doc__.strip())
        
        return "\n".join(doc)

def api_logger(func: Callable) -> Callable:
    """Decorator for API function logging."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger(func.__module__)
        try:
            logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    return wrapper

# Example usage
@ErrorRegistry.register(404)
class NotFoundError(APIError):
    """Resource not found error."""
    code = 404

@api_logger
def example_api_function(param: str) -> str:
    """Example API function with logging and error handling.
    
    Args:
        param: Input parameter
        
    Returns:
        Processed string
        
    Raises:
        NotFoundError: If resource not found
    """
    if not param:
        raise NotFoundError(message="Resource not found")
    return f"Processed: {param}"
