"""
Automated fixes for common dependency issues.
"""
from pathlib import Path
from typing import Dict, List, Set, Optional
import networkx as nx
import tomli
import tomli_w
import ast
import astor
from dataclasses import dataclass, field

@dataclass
class FixerConfig:
    """Configuration for dependency fixes."""
    allowed_moves: Dict[str, List[str]] = field(default_factory=lambda: {
        "graphics": ["renderers", "shaders", "scene", "primitives"],
        "math": ["linear", "geometry", "algorithms"],
        "utils": ["logging", "errors", "config"]
    })
    
    module_aliases: Dict[str, str] = field(default_factory=lambda: {
        "np": "numpy",
        "plt": "matplotlib.pyplot",
        "gl": "OpenGL.GL"
    })
    
    preferred_imports: Dict[str, str] = field(default_factory=lambda: {
        "matplotlib.pyplot": "import matplotlib.pyplot as plt",
        "numpy": "import numpy as np",
        "OpenGL.GL": "from OpenGL import GL as gl"
    })

class DependencyFixer:
    """Fixes common dependency issues."""
    
    def __init__(self, project_root: Path, config: Optional[FixerConfig] = None):
        self.project_root = project_root
        self.config = config or FixerConfig()
    
    def fix_circular_dependencies(self, graph: nx.DiGraph) -> List[str]:
        """Fix circular dependencies by suggesting module moves."""
        fixes = []
        cycles = list(nx.simple_cycles(graph))
        
        for cycle in cycles:
            fix = self._suggest_module_move(cycle)
            if fix:
                fixes.append(fix)
        
        return fixes
    
    def _suggest_module_move(self, cycle: List[str]) -> Optional[str]:
        """Suggest moving functionality to break cycle."""
        for module in cycle:
            module_parts = module.split('.')
            if len(module_parts) > 1:
                base_module, submodule = module_parts[0], module_parts[1]
                if base_module in self.config.allowed_moves:
                    allowed = self.config.allowed_moves[base_module]
                    for target in cycle:
                        if target.split('.')[0] != base_module:
                            return (
                                f"Move shared functionality from {module} to "
                                f"utils.shared.{submodule}_common to break dependency cycle"
                            )
        return None
    
    def fix_import_style(self, file_path: Path) -> bool:
        """Fix import style to match preferred patterns."""
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            
            modified = False
            new_tree = ast.Module(body=[], type_ignores=[])
            
            for node in tree.body:
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    new_node = self._fix_import_node(node)
                    if new_node != node:
                        modified = True
                        new_tree.body.append(new_node)
                    else:
                        new_tree.body.append(node)
                else:
                    new_tree.body.append(node)
            
            if modified:
                with open(file_path, 'w') as f:
                    f.write(astor.to_source(new_tree))
                return True
                
            return False
            
        except Exception as e:
            print(f"Error fixing imports in {file_path}: {e}")
            return False
    
    def _fix_import_node(self, node: ast.AST) -> ast.AST:
        """Fix individual import node."""
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.config.preferred_imports:
                    return ast.parse(self.config.preferred_imports[alias.name]).body[0]
        elif isinstance(node, ast.ImportFrom):
            module_name = f"{node.module}.{node.names[0].name}" if node.module else node.names[0].name
            if module_name in self.config.preferred_imports:
                return ast.parse(self.config.preferred_imports[module_name]).body[0]
        return node
    
    def apply_fixes(self, issues: List['ValidationIssue']) -> List[str]:
        """Apply automated fixes for validation issues."""
        fixes_applied = []
        
        for issue in issues:
            if issue.rule == "no-circular-deps":
                fixes = self.fix_circular_dependencies(issue.graph)
                fixes_applied.extend(fixes)
            
            elif issue.rule == "import-style":
                for module in issue.affected_modules:
                    file_path = self.project_root / "src" / module.replace(".", "/") / "__init__.py"
                    if self.fix_import_style(file_path):
                        fixes_applied.append(f"Fixed import style in {module}")
        
        return fixes_applied

class ConfigurationManager:
    """Manages dependency validation configuration."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.config_path = project_root / "dependency_config.toml"
    
    def load_config(self) -> FixerConfig:
        """Load configuration from file."""
        if not self.config_path.exists():
            return FixerConfig()
        
        with open(self.config_path, "rb") as f:
            data = tomli.load(f)
        
        return FixerConfig(
            allowed_moves=data.get("allowed_moves", {}),
            module_aliases=data.get("module_aliases", {}),
            preferred_imports=data.get("preferred_imports", {})
        )
    
    def save_config(self, config: FixerConfig) -> None:
        """Save configuration to file."""
        data = {
            "allowed_moves": config.allowed_moves,
            "module_aliases": config.module_aliases,
            "preferred_imports": config.preferred_imports
        }
        
        with open(self.config_path, "wb") as f:
            tomli_w.dump(data, f)

def main():
    """CLI interface for dependency fixing."""
    import argparse
    from .validator import DependencyValidator
    from .analyzer import DependencyAnalyzer
    
    parser = argparse.ArgumentParser(description="Fix dependency issues")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--apply", action="store_true", help="Apply suggested fixes")
    
    args = parser.parse_args()
    
    # Load configuration
    config_manager = ConfigurationManager(args.project_root)
    config = config_manager.load_config()
    
    # Analyze and validate
    analyzer = DependencyAnalyzer(args.project_root)
    graph = analyzer.analyze_project()
    
    validator = DependencyValidator()
    issues = validator.validate(graph)
    
    if not issues:
        print("No issues to fix!")
        return
    
    # Create fixer and get suggestions
    fixer = DependencyFixer(args.project_root, config)
    fixes = fixer.apply_fixes(issues)
    
    if args.apply:
        print("\nApplied fixes:")
        for fix in fixes:
            print(f"  - {fix}")
    else:
        print("\nSuggested fixes:")
        for fix in fixes:
            print(f"  - {fix}")
        print("\nRun with --apply to apply these fixes")

if __name__ == "__main__":
    main()