"""
Script to execute client file processing.
This script imports get_client_files and processes the client project files.
"""

import os
import sys
import importlib.util
from arduinolib1_core.arduinolib1_get_client_files import get_client_files


def execute_scripts(project_dir, library_dir):
    """
    Execute the scripts to process client files.
    
    Args:
        project_dir: Path to the client project root (where platformio.ini is)
        library_dir: Path to the library directory
    """
    # Set project_dir in globals so serializer scripts can access it
    globals()['project_dir'] = project_dir
    globals()['library_dir'] = library_dir
    
    print(f"\nproject_dir: {project_dir}")
    print(f"library_dir: {library_dir}")
    
    if project_dir:
        client_files = get_client_files(project_dir, file_extensions=['.h', '.cpp'])
        print(f"\nFound {len(client_files)} files in client project:")
        print("=" * 60)
        for file in client_files:
            print(file)
        print("=" * 60)
    
    if library_dir:
        library_files = get_client_files(library_dir, skip_exclusions=True)
        print(f"\nFound {len(library_files)} files in library:")
        print("=" * 60)
        for file in library_files:
            print(file)
        print("=" * 60)
    
    # Run the master serializer script (00_process_serializable_classes.py)
    # Find the serializer directory
    try:
        # Get the directory of this script
        current_file = os.path.abspath(__file__)
        current_dir = os.path.dirname(current_file)
        # current_dir is arduinolib1_scripts/, so serializer is in arduinolib1_serializer/
        serializer_dir = os.path.join(current_dir, 'arduinolib1_serializer')
    except NameError:
        # __file__ not available, try to find from library_dir
        if library_dir:
            serializer_dir = os.path.join(library_dir, 'arduinolib1_scripts', 'arduinolib1_serializer')
        else:
            serializer_dir = None
    
    if serializer_dir and os.path.exists(serializer_dir):
        serializer_script_path = os.path.join(serializer_dir, '00_process_serializable_classes.py')
        if os.path.exists(serializer_script_path):
            print(f"\n{'=' * 60}")
            print("Running serializer master script: 00_process_serializable_classes.py")
            print(f"{'=' * 60}\n")
            
            try:
    # Set environment variables so serializer script can access project_dir and library_dir
    if project_dir:
        os.environ['PROJECT_DIR'] = project_dir
        os.environ['CMAKE_PROJECT_DIR'] = project_dir
    if library_dir:
        os.environ['LIBRARY_DIR'] = str(library_dir)
                
                # Load and execute the serializer script
                spec = importlib.util.spec_from_file_location("process_serializable_classes", serializer_script_path)
                serializer_module = importlib.util.module_from_spec(spec)
                
                # Add serializer directory to path for imports
                sys.path.insert(0, serializer_dir)
                
                # Set globals in the module's namespace before execution
                # This ensures the serializer script can access project_dir and library_dir
                serializer_module.__dict__['project_dir'] = project_dir
                serializer_module.__dict__['library_dir'] = library_dir
                
                # Execute the module (this will run the top-level code)
                spec.loader.exec_module(serializer_module)
                
                # Call the main function if it exists
                if hasattr(serializer_module, 'main'):
                    serializer_module.main()
                elif hasattr(serializer_module, 'process_all_serializable_classes'):
                    serializer_module.process_all_serializable_classes(dry_run=False)
            except Exception as e:
                print(f"Error running serializer script: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"Warning: Serializer script not found at {serializer_script_path}")
    else:
        print(f"Warning: Serializer directory not found at {serializer_dir}")

