# Import debug utility first
import sys
import os
from pathlib import Path

# Add current directory to path to import debug_utils
try:
    if '__file__' in globals():
        script_dir = Path(__file__).parent
    else:
        # In PlatformIO SCons context, search for arduinolib1_scripts directory
        script_dir = Path(os.getcwd())
        # Try to find arduinolib1_scripts directory
        for _ in range(10):
            potential = script_dir / "arduinolib1_scripts"
            if potential.exists() and potential.is_dir():
                script_dir = potential
                break
            parent = script_dir.parent
            if parent == script_dir:
                break
            script_dir = parent
    sys.path.insert(0, str(script_dir))
except Exception:
    # If anything fails, just use current directory
    sys.path.insert(0, os.getcwd())

try:
    from debug_utils import debug_print
except ImportError:
    # Fallback if debug_utils not found - create a no-op function
    def debug_print(*args, **kwargs):
        pass

# Print message immediately when script is loaded (debug only)
debug_print("Hello cool dudes normal")

# Import PlatformIO environment first (if available)
env = None
try:
    Import("env")
except NameError:
    # Not running in PlatformIO environment (e.g., running from CMake)
    debug_print("Note: Not running in PlatformIO environment - some features may be limited")
    # Create a mock env object for CMake builds
    class MockEnv:
        def get(self, key, default=None):
            return default
    env = MockEnv()


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
            debug_print(f"✓ Found library path by searching up directory tree: {potential}")
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
        debug_print(f"\nClient project directory: {project_dir}")
    else:
        debug_print("Warning: Could not determine PROJECT_DIR from environment")
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

# Import debug utility
try:
    from debug_utils import debug_print
except ImportError:
    # Fallback if debug_utils not found - create a no-op function
    def debug_print(*args, **kwargs):
        pass

execute_scripts(project_dir, library_dir, serializable_macro=serializable_macro)
