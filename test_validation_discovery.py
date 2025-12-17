#!/usr/bin/env python3
"""Test script to verify validation macro discovery works correctly."""

import os
import sys

# Add paths
project_dir = '/Users/nkurude/CLionProjects/Experiments/arduinolibclient'
library_dir = '/Users/nkurude/CLionProjects/Experiments/arduinolibclient/build/_deps/arduinolib1-src'

# Set environment variables
os.environ['PROJECT_DIR'] = project_dir
os.environ['CMAKE_PROJECT_DIR'] = project_dir
os.environ['LIBRARY_DIR'] = library_dir

# Add script paths
sys.path.insert(0, os.path.join(library_dir, 'arduinolib1_scripts', 'arduinolib1_core'))
sys.path.insert(0, os.path.join(library_dir, 'arduinolib1_scripts', 'arduinolib1_serializer'))

print("=" * 60)
print("Testing Validation Macro Discovery")
print("=" * 60)

# Import and test
try:
    from arduinolib1_get_client_files import get_client_files
    print(f"✓ Successfully imported get_client_files")
    
    # Test getting files
    if os.path.exists(library_dir):
        library_files = get_client_files(library_dir, skip_exclusions=True)
        library_header_files = [f for f in library_files if f.endswith(('.h', '.hpp'))]
        print(f"✓ Found {len(library_header_files)} library header files")
        
        # Check if NayanSerializer.h is in the list
        nayan_serializer = [f for f in library_header_files if 'NayanSerializer.h' in f]
        if nayan_serializer:
            print(f"✓ Found NayanSerializer.h: {nayan_serializer[0]}")
        else:
            print(f"✗ NayanSerializer.h not found in library files")
    else:
        print(f"✗ Library directory does not exist: {library_dir}")
        sys.exit(1)
    
    # Now test S6
    import S6_discover_validation_macros
    print(f"\n✓ Successfully imported S6_discover_validation_macros")
    
    # Discover macros
    print(f"\nDiscovering validation macros...")
    validation_macros = S6_discover_validation_macros.find_validation_macro_definitions(None)
    
    print(f"\n" + "=" * 60)
    print(f"Results:")
    print(f"=" * 60)
    if validation_macros:
        print(f"✓ Successfully discovered {len(validation_macros)} validation macro(s):")
        for macro_name, function_name in sorted(validation_macros.items()):
            print(f"  - {macro_name} -> {function_name}")
    else:
        print(f"✗ No validation macros discovered!")
        print(f"\nDebugging info:")
        print(f"  - project_dir: {project_dir}")
        print(f"  - library_dir: {library_dir}")
        print(f"  - PROJECT_DIR env: {os.environ.get('PROJECT_DIR')}")
        print(f"  - LIBRARY_DIR env: {os.environ.get('LIBRARY_DIR')}")
        sys.exit(1)
    
    print(f"\n" + "=" * 60)
    print(f"✓ Test PASSED - Validation macros discovered correctly!")
    print(f"=" * 60)
    
except Exception as e:
    print(f"\n✗ Test FAILED with error:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

