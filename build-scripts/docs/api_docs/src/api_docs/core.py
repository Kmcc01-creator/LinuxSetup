# src/api_docs/core.py
"""
Core module for API documentation and error handling system.
"""
import enum
import functools
import inspect
import logging
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, Optional, Type, Union, List

class DocFormat(enum.Enum):
    """Documentation format types."""
    RST = "rst"
    MARKDOWN = "md"
    NUMPY = "numpy"
    GOOGLE = "google"

@dataclass
class APIError(Exception):
    """Base class for API errors with documentation integration."""
    code: int
    message: str
    details: Optional[Dict[str, Any]] = None
    doc_ref: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())

    def __post_init__(self):
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert error to dictionary format."""
        return {
            'code': self.code,
            'message': self.message,
            'details': self.details,
            'doc_ref': self.doc_ref,
            'timestamp': self.timestamp
        }

class ErrorRegistry:
    """Registry for API errors with documentation generation."""
    _errors: Dict[int, Type[APIError]] = {}
    _doc_path: Path = Path("docs/errors")
    
    @classmethod
    def register(cls, error_code: int) -> Callable:
        """Register an error class with documentation."""
        def wrapper(error_cls: Type[APIError]) -> Type[APIError]:
            if error_code in cls._errors:
                raise ValueError(f"Error code {error_code} is already registered")
            cls._errors[error_code] = error_cls
            cls._generate_error_doc(error_cls)
            return error_cls
        return wrapper
    
    @classmethod
    def get_error(cls, error_code: int) -> Optional[Type[APIError]]:
        """Get error class by error code."""
        return cls._errors.get(error_code)
    
    @classmethod
    def _generate_error_doc(cls, error_cls: Type[APIError]) -> None:
        """Generate documentation for error class."""
        cls._doc_path.mkdir(parents=True, exist_ok=True)
        
        doc_file = cls._doc_path / f"{error_cls.__name__.lower()}.md"
        with open(doc_file, "w") as f:
            f.write(f"# {error_cls.__name__}\n\n")
            f.write(f"Error Code: {error_cls.code}\n\n")
            f.write(f"Description: {error_cls.__doc__}\n\n")
            f.write("## Usage\n\n")
            f.write("```python\n")
            f.write(f"raise {error_cls.__name__}(message='Example error')\n")
            f.write("```\n\n")
            f.write("## Error Details\n\n")
            f.write("When this error occurs, check:\n\n")
            f.write("1. Input validation\n")
            f.write("2. System state\n")
            f.write("3. External dependencies\n")

class DocGenerator:
    """Documentation generator with build system integration."""
    
    def __init__(self, format: Union[DocFormat, str] = DocFormat.RST):
        if isinstance(format, str):
            try:
                self.format = DocFormat[format.upper()]
            except KeyError:
                raise ValueError(f"Invalid documentation format: {format}")
        elif isinstance(format, DocFormat):
            self.format = format
        else:
            raise ValueError(f"Invalid format type: {type(format)}")
        
        self.logger = logging.getLogger(__name__)
    
    def generate_api_docs(self, module: Any) -> str:
        """Generate API documentation for a module."""
        self.logger.info(f"Generating documentation for module: {module.__name__}")
        doc_content = []
        
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) or inspect.isfunction(obj):
                try:
                    doc = self._generate_doc(obj)
                    doc_content.append(doc)
                except Exception as e:
                    self.logger.error(f"Error generating docs for {name}: {str(e)}")
        
        return "\n\n".join(doc_content)
    
    def _generate_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate documentation for a class or function."""
        if self.format == DocFormat.RST:
            return self._generate_rst_doc(obj)
        elif self.format == DocFormat.MARKDOWN:
            return self._generate_md_doc(obj)
        elif self.format == DocFormat.NUMPY:
            return self._generate_numpy_doc(obj)
        else:
            return self._generate_google_doc(obj)
    
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
                    doc.append(f"\n{name}\n{'-' * len(name)}")
                    if method.__doc__:
                        doc.append(method.__doc__.strip())
        
        return "\n".join(doc)
    
    def _generate_md_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate Markdown documentation."""
        doc = [f"# {obj.__name__}"]
        
        if obj.__doc__:
            doc.append(obj.__doc__.strip())
        
        if inspect.isclass(obj):
            # Document methods
            for name, method in inspect.getmembers(obj, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    sig = inspect.signature(method)
                    doc.append(f"\n### `{name}{sig}`")
                    if method.__doc__:
                        doc.append(method.__doc__.strip())
        
        return "\n".join(doc)
    
    def _generate_numpy_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate NumPy style documentation."""
        # Add implementation as needed
        return self._generate_rst_doc(obj)
    
    def _generate_google_doc(self, obj: Union[Type, Callable]) -> str:
        """Generate Google style documentation."""
        # Add implementation as needed
        return self._generate_rst_doc(obj)

def api_logger(func: Callable) -> Callable:
    """Decorator for API function logging."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Get the logger for the module where the decorated function is defined
        logger_name = func.__module__ or "test"  # Use "test" for our test cases
        logger = logging.getLogger(logger_name)
        
        try:
            # Log before function execution
            logger.info(f"Calling {func.__name__} with args={args}, kwargs={kwargs}")
            
            # Execute the function
            result = func(*args, **kwargs)
            
            # Log successful completion
            logger.info(f"{func.__name__} completed successfully")
            return result
        except Exception as e:
            # Log error with full stack trace
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            raise
    
    return wrapper

class MetricsCollector:
    """Collect metrics about API usage and documentation."""
    
    def __init__(self):
        self.doc_coverage = {}
        self.error_counts = {}
        self.api_calls = {}
    
    def update_doc_coverage(self, module: Any) -> float:
        """Calculate documentation coverage for a module."""
        total_items = 0
        documented_items = 0
        
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) or inspect.isfunction(obj):
                total_items += 1
                if obj.__doc__:
                    documented_items += 1
        
        coverage = documented_items / total_items if total_items > 0 else 0
        self.doc_coverage[module.__name__] = coverage
        return coverage
    
    def record_error(self, error: APIError) -> None:
        """Record occurrence of an API error."""
        error_type = type(error).__name__
        self.error_counts[error_type] = self.error_counts.get(error_type, 0) + 1
    
    def record_api_call(self, func_name: str) -> None:
        """Record an API function call."""
        self.api_calls[func_name] = self.api_calls.get(func_name, 0) + 1
    
    def get_metrics_report(self) -> Dict[str, Any]:
        """Generate a metrics report."""
        return {
            'doc_coverage': self.doc_coverage,
            'error_counts': self.error_counts,
            'api_calls': self.api_calls
        }

# Initialize global metrics collector
metrics = MetricsCollector()

# Common error classes
@ErrorRegistry.register(400)
class BadRequestError(APIError):
    """Bad request error due to invalid input."""
    code = 400

@ErrorRegistry.register(404)
class NotFoundError(APIError):
    """Resource not found error."""
    code = 404

@ErrorRegistry.register(500)
class ServerError(APIError):
    """Internal server error."""
    code = 500
