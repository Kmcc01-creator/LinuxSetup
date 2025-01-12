"""
Build system integration for graphics and math core modules.
"""
from pathlib import Path
import subprocess
from typing import Dict, List, Optional
import tomli
import tomli_w

class CoreBuildManager:
    """Manages build process for core modules."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_path = project_root / "src"
        self.build_path = project_root / "build"
        
    def setup_module(self, module_name: str, config: Dict) -> None:
        """Set up a core module with its build configuration."""
        module_path = self.src_path / module_name
        module_path.mkdir(parents=True, exist_ok=True)
        
        # Create module-specific build configuration
        build_config = {
            "module": {
                "name": module_name,
                "build_requires": config["build_requires"],
                "optional_features": config["optional_features"]
            }
        }
        
        with open(module_path / "build_config.toml", "wb") as f:
            tomli_w.dump(build_config, f)
    
    def build_module(self, module_name: str, features: List[str] = None) -> None:
        """Build a specific module with optional features."""
        module_path = self.src_path / module_name
        build_config_path = module_path / "build_config.toml"
        
        if not build_config_path.exists():
            raise FileNotFoundError(f"No build configuration found for {module_name}")
        
        # Load module build configuration
        with open(build_config_path, "rb") as f:
            config = tomli.load(f)
        
        # Prepare build environment
        env_vars = self._prepare_build_env(config["module"], features)
        
        # Run Cython compilation if needed
        if self._needs_cython_build(module_path):
            self._run_cython_build(module_path, env_vars)
        
        # Run PDM build
        subprocess.run(
            ["pdm", "build", "--no-isolation"],
            env=env_vars,
            cwd=self.project_root,
            check=True
        )
    
    def _prepare_build_env(self, config: Dict, features: List[str] = None) -> Dict:
        """Prepare build environment variables."""
        env = dict(os.environ)
        
        # Add build requirements to PYTHONPATH
        if "build_requires" in config:
            self._ensure_dependencies(config["build_requires"])
        
        # Add optional features
        if features and "optional_features" in config:
            for feature in features:
                if feature in config["optional_features"]:
                    self._ensure_dependencies(config["optional_features"][feature])
        
        return env
    
    def _needs_cython_build(self, module_path: Path) -> bool:
        """Check if module needs Cython compilation."""
        return any(module_path.rglob("*.pyx"))
    
    def _run_cython_build(self, module_path: Path, env: Dict) -> None:
        """Run Cython compilation for a module."""
        # Create a temporary setup.py for Cython
        setup_content = f'''
from setuptools import setup
from Cython.Build import cythonize
import numpy

setup(
    ext_modules=cythonize("{module_path}/*.pyx"),
    include_dirs=[numpy.get_include()]
)
'''
        setup_path = self.project_root / "setup.py"
        setup_path.write_text(setup_content)
        
        try:
            subprocess.run(
                ["python", "setup.py", "build_ext", "--inplace"],
                env=env,
                cwd=self.project_root,
                check=True
            )
        finally:
            setup_path.unlink()
    
    def _ensure_dependencies(self, dependencies: List[str]) -> None:
        """Ensure build dependencies are installed."""
        subprocess.run(
            ["pdm", "add", "--dev"] + dependencies,
            cwd=self.project_root,
            check=True
        )

def main():
    """Main entry point for build system."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Core Build System")
    parser.add_argument("module", choices=["graphics", "math", "all"])
    parser.add_argument("--features", nargs="+", help="Optional features to build")
    
    args = parser.parse_args()
    project_root = Path.cwd()
    
    builder = CoreBuildManager(project_root)
    
    if args.module == "all":
        modules = ["graphics", "math"]
    else:
        modules = [args.module]
    
    for module in modules:
        print(f"Building {module} module...")
        builder.build_module(module, args.features)
        print(f"{module} module built successfully!")

if __name__ == "__main__":
    main()