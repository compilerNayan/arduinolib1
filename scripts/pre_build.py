# Print message immediately when script is loaded
print("Hello cool dudes normal")

# Import PlatformIO environment first
Import("env")

# Import the get_client_files function
import sys
import os
from pathlib import Path

# Add scripts directory to path to import get_client_files
scripts_dir = Path(__file__).parent
sys.path.insert(0, str(scripts_dir))

from get_client_files import get_client_files

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
