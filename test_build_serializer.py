#!/usr/bin/env python3
"""Test script to manually run the serializer and verify validation macro discovery."""

import os
import sys

# Set up paths
project_dir = '/Users/nkurude/CLionProjects/Experiments/arduinolibclient'
library_dir = '/Users/nkurude/src/personal/springbootexps/arduinolib1/arduinolib1'

# Set environment variables (as execute_scripts would)
os.environ['PROJECT_DIR'] = project_dir
os.environ['CMAKE_PROJECT_DIR'] = project_dir
os.environ['LIBRARY_DIR'] = library_dir

# Add script paths
library_scripts_dir = os.path.join(library_dir, 'arduinolib1_scripts')
sys.path.insert(0, library_scripts_dir)
sys.path.insert(0, os.path.join(library_scripts_dir, 'arduinolib1_core'))
sys.path.insert(0, os.path.join(library_scripts_dir, 'arduinolib1_serializer'))

print("=" * 60)
print("Testing Serializer with Validation Macro Discovery")
print("=" * 60)
print(f"Project dir: {project_dir}")
print(f"Library dir: {library_dir}")
print()

# Import execute_scripts
try:
    from arduinolib1_execute_scripts import execute_scripts
    print("✓ Successfully imported execute_scripts")
    print()
    
    # Run execute_scripts (this will trigger the serializer)
    print("Running execute_scripts...")
    print("-" * 60)
    execute_scripts(project_dir, library_dir)
    print("-" * 60)
    print()
    
    # Check if validation code was generated
    all_validations_file = os.path.join(project_dir, 'src', 'AllValidationsDto.h')
    if os.path.exists(all_validations_file):
        with open(all_validations_file, 'r') as f:
            content = f.read()
        
        if 'ValidateFields' in content:
            if 'No validation macros defined' in content:
                print("✗ FAILED: ValidateFields method exists but says 'No validation macros defined'")
                print("   This means validation macros were not discovered!")
                sys.exit(1)
            elif 'DtoValidationUtility::ValidateNotNull' in content or 'DtoValidationUtility::ValidateNotEmpty' in content or 'DtoValidationUtility::ValidateNotBlank' in content:
                print("✓ SUCCESS: ValidateFields method contains validation code!")
                print("   Validation macros were discovered and code was generated!")
            else:
                print("⚠ WARNING: ValidateFields method exists but validation code unclear")
                print("   Content snippet:")
                # Find ValidateFields section
                idx = content.find('ValidateFields')
                if idx != -1:
                    snippet = content[idx:idx+500]
                    print(f"   {snippet[:200]}...")
        else:
            print("✗ FAILED: ValidateFields method not found in generated code")
            print("   Serializer may not have run or failed")
            sys.exit(1)
    else:
        print(f"✗ FAILED: Could not find {all_validations_file}")
        sys.exit(1)
    
    print()
    print("=" * 60)
    print("✓ Test completed successfully!")
    print("=" * 60)
    
except Exception as e:
    print(f"\n✗ Test FAILED with error:")
    import traceback
    traceback.print_exc()
    sys.exit(1)

