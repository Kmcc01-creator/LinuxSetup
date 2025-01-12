"""
Dependency analysis and management tool for the project.
"""
from pathlib import Path
from typing import Dict, Set, List, Optional
import ast
import tomli
import networkx as nx
from dataclasses import dataclass

@dataclass
class Dependency:
    """Represents a module dependency."""
    name: str
    version: Optional[str] = None
    optional: bool = False
    build_only: bool = False

class DependencyAnalyzer:
    """Analyzes project dependencies and their relationships."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.graph = nx.DiGraph()
    
    def analyze_project(self) -> nx.DiGraph:
        """Analyze entire project dependency structure."""
        # Scan source files
        for py_file in self.src_path.rglob("*.py"):
            if self._should_skip_file(py_file):
                continue
            
            module_name = self._get_module_name(py_file)
            self._analyze_file_dependencies(py_file, module_name)
        
        # Add build dependencies from pyproject.toml
        self._analyze_build_dependencies()
        
        return self.graph
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if file should be skipped in analysis."""
        return (
            "__pycache__" in str(file_path)
            or "tests" in str(file_path)
            or file_path.name.startswith(".")
        )
    
    def _get_module_name(self, file_path: Path) -> str:
        """Get module name from file path."""
        rel_path = file_path.relative_to(self.src_path)
        return ".".join(rel_path.parent.parts + (rel_path.stem,))
    
    def _analyze_file_dependencies(self, file_path: Path, module_name: str) -> None:
        """Analyze dependencies in a single file."""
        try:
            with open(file_path) as f:
                tree = ast.parse(f.read())
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        self._add_dependency(module_name, name.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        self._add_dependency(module_name, node.module)
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
    
    def _analyze_build_dependencies(self) -> None:
        """Analyze build dependencies from pyproject.toml."""
        pyproject_path = self.project_root / "pyproject.toml"
        if not pyproject_path.exists():
            return
        
        with open(pyproject_path, "rb") as f:
            config = tomli.load(f)
        
        # Add build system dependencies
        if "build-system" in config:
            for dep in config["build-system"].get("requires", []):
                self._add_dependency("build", dep, build_only=True)
        
        # Add project dependencies
        if "project" in config:
            for dep in config["project"].get("dependencies", []):
                self._add_dependency("runtime", dep)
    
    def _add_dependency(self, from_module: str, to_module: str, 
                       optional: bool = False, build_only: bool = False) -> None:
        """Add dependency to the graph."""
        # Clean up module names
        to_module = to_module.split('.')[0]
        
        # Add nodes and edge
        self.graph.add_node(from_module)
        self.graph.add_node(to_module)
        self.graph.add_edge(
            from_module, 
            to_module, 
            optional=optional,
            build_only=build_only
        )
    
    def find_cycles(self) -> List[List[str]]:
        """Find dependency cycles in the project."""
        return list(nx.simple_cycles(self.graph))
    
    def get_dependency_order(self) -> List[str]:
        """Get proper build/import order of modules."""
        try:
            return list(nx.topological_sort(self.graph))
        except nx.NetworkXUnfeasible:
            print("Warning: Dependency graph contains cycles!")
            return []
    
    def get_module_dependencies(self, module: str) -> Set[str]:
        """Get all dependencies for a specific module."""
        if module not in self.graph:
            return set()
        
        # Get all reachable nodes from this module
        return set(nx.descendants(self.graph, module))
    
    def export_graph(self, output_path: Path) -> None:
        """Export dependency graph to various formats."""
        # Mermaid format
        mermaid_content = ["graph TD"]
        for from_node, to_node, data in self.graph.edges(data=True):
            edge_style = "-.>" if data.get("optional") else "-->"
            if data.get("build_only"):
                edge_style = "==>"
            mermaid_content.append(f"    {from_node} {edge_style} {to_node}")
        
        with open(output_path / "dependencies.mmd", "w") as f:
            f.write("\n".join(mermaid_content))
        
        # DOT format for Graphviz
        nx.drawing.nx_pydot.write_dot(self.graph, output_path / "dependencies.dot")

def main():
    """CLI interface for dependency analysis."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze project dependencies")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--output", type=Path, default=Path.cwd() / "docs" / "dependencies")
    parser.add_argument("--check-cycles", action="store_true", 
                       help="Check for dependency cycles")
    
    args = parser.parse_args()
    
    analyzer = DependencyAnalyzer(args.project_root)
    graph = analyzer.analyze_project()
    
    # Create output directory
    args.output.mkdir(parents=True, exist_ok=True)
    
    # Export graph
    analyzer.export_graph(args.output)
    print(f"Dependency graph exported to {args.output}")
    
    # Check for cycles if requested
    if args.check_cycles:
        cycles = analyzer.find_cycles()
        if cycles:
            print("\nWarning: Dependency cycles found:")
            for cycle in cycles:
                print(" -> ".join(cycle))
        else:
            print("\nNo dependency cycles found.")
    
    # Print build order
    build_order = analyzer.get_dependency_order()
    if build_order:
        print("\nSuggested build order:")
        for module in build_order:
            print(f"  - {module}")

if __name__ == "__main__":
    main()