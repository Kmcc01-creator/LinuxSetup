"""
Enhanced dependency validation system with rules enforcement.
"""
from pathlib import Path
from typing import Dict, List, Set, Optional
import networkx as nx
from dataclasses import dataclass
from enum import Enum
import tomli
import ast
import re

class ValidationLevel(Enum):
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

@dataclass
class ValidationRule:
    """Represents a dependency validation rule."""
    name: str
    description: str
    level: ValidationLevel
    
    def validate(self, graph: nx.DiGraph) -> List['ValidationIssue']:
        """Implement in subclasses."""
        raise NotImplementedError

@dataclass
class ValidationIssue:
    """Represents a validation issue found."""
    rule: str
    message: str
    level: ValidationLevel
    affected_modules: List[str]

class CircularDependencyRule(ValidationRule):
    """Detects circular dependencies in the module graph."""
    
    def __init__(self):
        super().__init__(
            name="no-circular-deps",
            description="Detects circular dependencies between modules",
            level=ValidationLevel.ERROR
        )
    
    def validate(self, graph: nx.DiGraph) -> List[ValidationIssue]:
        issues = []
        cycles = list(nx.simple_cycles(graph))
        
        for cycle in cycles:
            issues.append(ValidationIssue(
                rule=self.name,
                message=f"Circular dependency detected: {' -> '.join(cycle)}",
                level=self.level,
                affected_modules=cycle
            ))
        
        return issues

class LayerViolationRule(ValidationRule):
    """Enforces layered architecture rules."""
    
    LAYERS = {
        "graphics": 3,
        "math": 2,
        "utils": 1
    }
    
    def __init__(self):
        super().__init__(
            name="layer-violation",
            description="Enforces layered architecture dependencies",
            level=ValidationLevel.ERROR
        )
    
    def validate(self, graph: nx.DiGraph) -> List[ValidationIssue]:
        issues = []
        
        for from_node, to_node in graph.edges():
            from_layer = self._get_layer(from_node)
            to_layer = self._get_layer(to_node)
            
            if from_layer and to_layer and from_layer < to_layer:
                issues.append(ValidationIssue(
                    rule=self.name,
                    message=f"Layer violation: {from_node} (layer {from_layer}) "
                           f"depends on {to_node} (layer {to_layer})",
                    level=self.level,
                    affected_modules=[from_node, to_node]
                ))
        
        return issues
    
    def _get_layer(self, module: str) -> Optional[int]:
        module_base = module.split('.')[0]
        return self.LAYERS.get(module_base)

class DirectDependencyRule(ValidationRule):
    """Enforces rules about direct dependencies between modules."""
    
    ALLOWED_DIRECT_DEPS = {
        "graphics.renderers": {"math.linear", "math.geometry"},
        "graphics.shaders": {"math.linear"},
        "graphics.scene": {"math.geometry", "math.algorithms"},
        "graphics.primitives": {"math.geometry"}
    }
    
    def __init__(self):
        super().__init__(
            name="direct-deps",
            description="Enforces allowed direct dependencies",
            level=ValidationLevel.ERROR
        )
    
    def validate(self, graph: nx.DiGraph) -> List[ValidationIssue]:
        issues = []
        
        for from_module, to_module in graph.edges():
            if from_module in self.ALLOWED_DIRECT_DEPS:
                if to_module not in self.ALLOWED_DIRECT_DEPS[from_module]:
                    issues.append(ValidationIssue(
                        rule=self.name,
                        message=f"Unauthorized direct dependency: {from_module} -> {to_module}",
                        level=self.level,
                        affected_modules=[from_module, to_module]
                    ))
        
        return issues

class ExternalDependencyRule(ValidationRule):
    """Validates external dependency usage."""
    
    ALLOWED_EXTERNAL = {
        "graphics": {"PyOpenGL", "vulkan", "numpy"},
        "math": {"numpy", "scipy"},
        "utils": {"pydantic", "typing-extensions"}
    }
    
    def __init__(self):
        super().__init__(
            name="external-deps",
            description="Validates external dependency usage",
            level=ValidationLevel.WARNING
        )
    
    def validate(self, graph: nx.DiGraph) -> List[ValidationIssue]:
        issues = []
        
        for node in graph.nodes():
            module_base = node.split('.')[0]
            if module_base in self.ALLOWED_EXTERNAL:
                external_deps = self._get_external_deps(graph, node)
                invalid_deps = external_deps - self.ALLOWED_EXTERNAL[module_base]
                
                if invalid_deps:
                    issues.append(ValidationIssue(
                        rule=self.name,
                        message=f"Unauthorized external dependencies in {node}: {invalid_deps}",
                        level=self.level,
                        affected_modules=[node]
                    ))
        
        return issues
    
    def _get_external_deps(self, graph: nx.DiGraph, node: str) -> Set[str]:
        return {n for n in graph.successors(node) 
                if not any(n.startswith(f"{base}.") 
                          for base in self.ALLOWED_EXTERNAL.keys())}

class DependencyValidator:
    """Main dependency validation system."""
    
    def __init__(self):
        self.rules: List[ValidationRule] = [
            CircularDependencyRule(),
            LayerViolationRule(),
            DirectDependencyRule(),
            ExternalDependencyRule()
        ]
    
    def validate(self, graph: nx.DiGraph) -> List[ValidationIssue]:
        """Run all validation rules on the dependency graph."""
        all_issues = []
        
        for rule in self.rules:
            try:
                issues = rule.validate(graph)
                all_issues.extend(issues)
            except Exception as e:
                print(f"Error running rule {rule.name}: {e}")
        
        return all_issues
    
    def print_validation_report(self, issues: List[ValidationIssue]) -> None:
        """Print a formatted validation report."""
        if not issues:
            print("No dependency issues found!")
            return
        
        print("\nDependency Validation Report")
        print("===========================")
        
        for level in ValidationLevel:
            level_issues = [i for i in issues if i.level == level]
            if level_issues:
                print(f"\n{level.value.upper()}:")
                for issue in level_issues:
                    print(f"\n  Rule: {issue.rule}")
                    print(f"  Message: {issue.message}")
                    print(f"  Affected modules: {', '.join(issue.affected_modules)}")

def main():
    """CLI interface for dependency validation."""
    import argparse
    from .analyzer import DependencyAnalyzer
    
    parser = argparse.ArgumentParser(description="Validate project dependencies")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--fail-on", choices=["error", "warning", "info"], 
                       default="error",
                       help="Exit with error on this validation level")
    
    args = parser.parse_args()
    
    # Analyze dependencies
    analyzer = DependencyAnalyzer(args.project_root)
    graph = analyzer.analyze_project()
    
    # Validate dependencies
    validator = DependencyValidator()
    issues = validator.validate(graph)
    
    # Print report
    validator.print_validation_report(issues)
    
    # Check if we should fail
    fail_level = ValidationLevel(args.fail_on)
    if any(issue.level.value <= fail_level.value for issue in issues):
        exit(1)

if __name__ == "__main__":
    main()