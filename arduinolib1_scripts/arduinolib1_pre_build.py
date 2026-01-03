# Import PlatformIO environment first (if available)
env = None
try:
    Import("env")
except NameError:
    # Not running in PlatformIO environment (e.g., running from CMake)
    class MockEnv:
        def get(self, key, default=None):
            return default
    env = MockEnv()

import sys
import os
from pathlib import Path

# Import logging utility
try:
    # Try to find and import pre_build_logger
    script_dir = Path(__file__).parent if '__file__' in globals() else Path(os.getcwd())
    # Search for arduinolib0_scripts
    for parent in [script_dir] + list(script_dir.parents)[:10]:
        logger_path = parent / "arduinolib0" / "arduinolib0_scripts" / "pre_build_logger.py"
        if logger_path.exists():
            sys.path.insert(0, str(logger_path.parent))
            from pre_build_logger import print_banner, log_processing_start
            print_banner()
            log_processing_start("Serialization Processing")
            break
    else:
        # Fallback: create minimal logger functions
        def print_banner():
            pass
        def log_processing_start(name):
            pass
except Exception:
    # Fallback: create minimal logger functions
    def print_banner():
        pass
    def log_processing_start(name):
        pass


def get_library_dir():
    """
    Find the arduinolib1_scripts directory by searching up the directory tree.
    
    Returns:
        Path: Path to the arduinolib1_scripts directory
        
    Raises:
        ImportError: If the directory cannot be found
    """
    cwd = Path(os.getcwd())
    current = cwd
    for _ in range(10):  # Search up to 10 levels
        potential = current / "arduinolib1_scripts"
        if potential.exists() and potential.is_dir():
            # print(f"✓ Found library path by searching up directory tree: {potential}")
            # print(f"✓ Found library path by searching up directory tree: {potential}")
            return potential
        parent = current.parent
        if parent == current:  # Reached filesystem root
            break
        current = parent
    raise ImportError("Could not find arduinolib1_scripts directory")


def get_project_dir():
    """
    Get the project directory from PlatformIO environment or CMake environment.
    
    Returns:
        str: Path to the project directory, or None if not found
    """
    # Try PlatformIO environment first
    project_dir = None
    if env:
        project_dir = env.get("PROJECT_DIR", None)
    
    # If not found, try CMake environment variable
    if not project_dir:
        project_dir = os.environ.get("CMAKE_PROJECT_DIR", None)
    
    if project_dir:
        # print(f"\nClient project directory: {project_dir}")
        pass
    else:
        # print("Warning: Could not determine PROJECT_DIR from environment")
        # print("Warning: Could not determine PROJECT_DIR from environment")
        pass
    return project_dir
# Get library scripts directory and add it to Python path
library_scripts_dir = get_library_dir()
sys.path.insert(0, str(library_scripts_dir))

# Get library root directory (parent of arduinolib1_scripts)
library_dir = library_scripts_dir.parent

# Get project directory
project_dir = get_project_dir()

# Get serializable macro name from environment or use default
serializable_macro = os.environ.get("SERIALIZABLE_MACRO", "Serializable")

# Import and execute scripts
from arduinolib1_execute_scripts import execute_scripts
execute_scripts(project_dir, library_dir, serializable_macro=serializable_macro)
