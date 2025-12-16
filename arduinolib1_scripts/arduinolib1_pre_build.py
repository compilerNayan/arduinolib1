# Print message immediately when script is loaded
print("Hello cool dudes normal")

# Import PlatformIO environment first
Import("env")

import sys
import os
from pathlib import Path

# Get the scripts directory without using __file__
# In PlatformIO, we can get the library path from the library builder
get_client_files = None

try:
    # Method 1: Get library path from library builder
    # When extraScript runs, the library builder is available in the environment
    lib_builder = env.GetLibBuilder()
    if lib_builder and hasattr(lib_builder, 'path'):
        lib_path = Path(lib_builder.path)
        scripts_dir = lib_path / "arduinolib1_scripts"
        if scripts_dir.exists() and (scripts_dir / "get_client_files.py").exists():
            sys.path.insert(0, str(scripts_dir))
            from get_client_files import get_client_files
            print(f"✓ Method 1: Found library path from library builder: {scripts_dir}")
except Exception as e:
    pass

# Method 2: If library builder didn't work, try to find scripts directory
# by searching from current working directory
if get_client_files is None:
    try:
        cwd = Path(os.getcwd())
        # Try arduinolib1_scripts/ subdirectory first (most common case)
        potential_scripts = cwd / "arduinolib1_scripts"
        if potential_scripts.exists() and (potential_scripts / "get_client_files.py").exists():
            sys.path.insert(0, str(potential_scripts))
            from get_client_files import get_client_files
            print(f"✓ Method 2: Found library path from current directory subdirectory: {potential_scripts}")
        else:
            # Search up the directory tree for arduinolib1_scripts/get_client_files.py
            current = cwd
            for _ in range(10):  # Search up to 10 levels
                potential = current / "arduinolib1_scripts" / "get_client_files.py"
                if potential.exists():
                    scripts_dir = potential.parent
                    sys.path.insert(0, str(scripts_dir))
                    from get_client_files import get_client_files
                    print(f"✓ Method 2: Found library path by searching up directory tree: {scripts_dir}")
                    break
                parent = current.parent
                if parent == current:  # Reached filesystem root
                    break
                current = parent
            else:
                raise ImportError("Could not find get_client_files.py")
    except ImportError as e:
        print(f"Warning: Could not import get_client_files: {e}")
        print("Using fallback function (returns empty list)")
        # Define a fallback function
        def get_client_files(project_dir):
            return []

# Get the project directory from PlatformIO environment
# The PROJECT_DIR is available in the environment
project_dir = env.get("PROJECT_DIR", None)

if project_dir:
    print(f"\nClient project directory: {project_dir}")
    client_files = get_client_files(project_dir)
    print(f"\nFound {len(client_files)} files in client project:")
    print("=" * 60)
    for file in client_files:
        print(file)
    print("=" * 60)
else:
    print("Warning: Could not determine PROJECT_DIR from environment")
