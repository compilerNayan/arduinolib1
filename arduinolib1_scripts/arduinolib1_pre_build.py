# Print message immediately when script is loaded
print("Hello cool dudes normal")

# Import PlatformIO environment first
Import("env")

import sys
import os
from pathlib import Path

# Find scripts directory by searching up the directory tree
cwd = Path(os.getcwd())
current = cwd
for _ in range(10):  # Search up to 10 levels
    potential = current / "arduinolib1_scripts"
    if potential.exists() and potential.is_dir():
        scripts_dir = potential
        sys.path.insert(0, str(scripts_dir))
        from get_client_files import get_client_files
        print(f"✓ Found library path by searching up directory tree: {scripts_dir}")
        break
    parent = current.parent
    if parent == current:  # Reached filesystem root
        break
    current = parent
else:
    raise ImportError("Could not find arduinolib1_scripts directory")

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
