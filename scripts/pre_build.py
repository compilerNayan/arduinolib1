# Print message immediately when script is loaded
print("Hello cool dudes normal")

# Import PlatformIO environment first
Import("env")

import os
from pathlib import Path


def get_client_files(project_dir):
    """
    Get all files in the client project, excluding library directories.
    
    Args:
        project_dir: Path to the client project root (where platformio.ini is)
    
    Returns:
        List of file paths relative to project_dir
    """
    project_path = Path(project_dir).resolve()
    client_files = []
    
    # Directories to exclude (PlatformIO library and build directories)
    exclude_dirs = {
        '.pio',           # PlatformIO build and library directory
        '.git',           # Git directory
        '.vscode',        # VS Code settings (optional, but common)
        '.idea',          # IDE settings
    }
    
    # Walk through the project directory
    for root, dirs, files in os.walk(project_path):
        # Convert to Path for easier manipulation
        root_path = Path(root)
        
        # Skip if this directory or any parent is in exclude_dirs
        should_skip = False
        for part in root_path.parts:
            if part in exclude_dirs:
                should_skip = True
                break
        
        if should_skip:
            # Remove excluded directories from dirs list to prevent walking into them
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            continue
        
        # Add all files in this directory
        for file in files:
            file_path = root_path / file
            # Get relative path from project root
            try:
                rel_path = file_path.relative_to(project_path)
                client_files.append(str(rel_path))
            except ValueError:
                # Skip if path is not relative (shouldn't happen, but safety check)
                continue
    
    return sorted(client_files)

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
