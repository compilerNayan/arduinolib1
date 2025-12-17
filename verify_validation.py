#!/usr/bin/env python3
"""
Simple verification script to test validation macro discovery.
Run this from the arduinolib1 directory after building the client project.
"""

import os
import sys

# This simulates what happens during CMake build
project_dir = '/Users/nkurude/CLionProjects/Experiments/arduinolibclient'
library_dir = '/Users/nkurude/src/personal/springbootexps/arduinolib1/arduinolib1'

# Set environment variables
os.environ['PROJECT_DIR'] = project_dir
os.environ['CMAKE_PROJECT_DIR'] = project_dir  
os.environ['LIBRARY_DIR'] = library_dir

# Add paths
scripts_dir = os.path.join(library_dir, 'arduinolib1_scripts')
sys.path.insert(0, os.path.join(scripts_dir, 'arduinolib1_core'))
sys.path.insert(0, os.path.join(scripts_dir, 'arduinolib1_serializer'))

print("Testing validation macro discovery...")
print(f"Project: {project_dir}")
print(f"Library: {library_dir}")
print()

try:
    import S6_discover_validation_macros
    macros = S6_discover_validation_macros.find_validation_macro_definitions(None)
    
    if macros:
        print(f"✓ SUCCESS: Found {len(macros)} validation macro(s):")
        for name, func in sorted(macros.items()):
            print(f"  - {name} -> {func}")
        print("\n✓ Validation macros are being discovered correctly!")
        return 0
    else:
        print("✗ FAILED: No validation macros discovered")
        return 1
except Exception as e:
    print(f"✗ ERROR: {e}")
    import traceback
    traceback.print_exc()
    return 1

if __name__ == '__main__':
    sys.exit(main() if 'main' in dir() else 0)

