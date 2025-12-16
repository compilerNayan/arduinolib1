#!/usr/bin/env python3
"""
00 Process Serializable Classes Script

Orchestrator script that processes all classes with Serializable macro in client files.
Uses 05_list_client_files.py to get the list of client files.
"""

import os
import sys
import importlib.util

print("Executing NayanSerializer/scripts/serializer/00_process_serializable_classes.py")

# Import the serializer scripts
# Determine script_dir - where this script and other serializer scripts are located
try:
    script_file = os.path.abspath(__file__)
    script_dir = os.path.dirname(script_file)
except NameError:
    # __file__ not available (exec() context) - try to find script directory
    script_dir = None
    
    # Method 1: If we have script_dir pointing to scripts/core/, go up and into serializer/
    # This is the most reliable method since script_dir is set by 02_find_library.py
    if 'script_dir' in globals() and globals()['script_dir']:
        # script_dir is scripts/core/, so go up one level to scripts/, then to serializer/
        scripts_parent = os.path.dirname(globals()['script_dir'])
        candidate = os.path.join(scripts_parent, 'serializer')
        print(f"DEBUG: Method 1 - script_dir={globals()['script_dir']}, scripts_parent={scripts_parent}, candidate={candidate}, exists={os.path.exists(candidate)}")
        if os.path.exists(candidate):
            script_dir = candidate
    
    # Method 2: Try initial_script_dir (from execute_scripts.py) - this is scripts/
    if (not script_dir or not os.path.exists(script_dir)) and 'initial_script_dir' in globals() and globals()['initial_script_dir']:
        candidate = os.path.join(globals()['initial_script_dir'], 'serializer')
        if os.path.exists(candidate):
            script_dir = candidate
    
    # Method 3: Try _pre_build_script_dir (from pre_build.py) - this is scripts/
    if (not script_dir or not os.path.exists(script_dir)) and '_pre_build_script_dir' in globals():
        candidate = os.path.join(globals()['_pre_build_script_dir'], 'serializer')
        if os.path.exists(candidate):
            script_dir = candidate
    
    # Method 4: Try script_dir (from 02_find_library.py) - this is scripts/core/
    # (This is already handled in Method 1, but keeping as fallback)
    if (not script_dir or not os.path.exists(script_dir)) and 'script_dir' in globals() and globals()['script_dir']:
        # script_dir is scripts/core/, so go up one level to scripts/, then to serializer/
        scripts_parent = os.path.dirname(globals()['script_dir'])
        candidate = os.path.join(scripts_parent, 'serializer')
        if os.path.exists(candidate):
            script_dir = candidate
    
    # Method 4: Try to find from lib_dir (from 02_find_library.py)
    if (not script_dir or not os.path.exists(script_dir)) and 'lib_dir' in globals() and globals()['lib_dir']:
        candidate = os.path.join(globals()['lib_dir'], 'scripts', 'serializer')
        if os.path.exists(candidate):
            script_dir = candidate
    
    # Method 5: Fallback - search from current directory
    if not script_dir or not os.path.exists(script_dir):
        cwd = os.getcwd()
        possible_dirs = [
            os.path.join(cwd, 'scripts', 'serializer'),
            os.path.join(os.path.dirname(cwd), 'scripts', 'serializer'),
        ]
        for dir_path in possible_dirs:
            if os.path.exists(dir_path):
                script_dir = dir_path
                break
        
        # Final fallback - try to find from known library location or lib_dir
        if not script_dir or not os.path.exists(script_dir):
            # Try lib_dir first if available
            if 'lib_dir' in globals() and globals()['lib_dir']:
                candidate = os.path.join(globals()['lib_dir'], 'scripts', 'serializer')
                if os.path.exists(candidate):
                    script_dir = candidate
            
            # If still not found, try common library locations
            if not script_dir or not os.path.exists(script_dir):
                known_lib_paths = [
                    '/Users/nkurude/CLionProjects/Experiments/mylibs/NayanSerializer',
                ]
                for lib_path in known_lib_paths:
                    candidate = os.path.join(lib_path, 'scripts', 'serializer')
                    if os.path.exists(candidate):
                        script_dir = candidate
                        break

# Verify script_dir exists and contains the serializer scripts
# If script_dir doesn't exist or doesn't contain serializer scripts, try to fix it
if not os.path.exists(script_dir) or not os.path.exists(os.path.join(script_dir, "S1_check_dto_macro.py")):
    # If script_dir points to scripts/ instead of scripts/serializer/, fix it
    if script_dir.endswith('scripts') and os.path.exists(os.path.join(script_dir, 'serializer')):
        script_dir = os.path.join(script_dir, 'serializer')
    
    # If still not found, try lib_dir
    if (not os.path.exists(script_dir) or not os.path.exists(os.path.join(script_dir, "S1_check_dto_macro.py"))) and 'lib_dir' in globals() and globals()['lib_dir']:
        candidate = os.path.join(globals()['lib_dir'], 'scripts', 'serializer')
        if os.path.exists(candidate) and os.path.exists(os.path.join(candidate, "S1_check_dto_macro.py")):
            script_dir = candidate
    
    # Final check
    if not os.path.exists(script_dir) or not os.path.exists(os.path.join(script_dir, "S1_check_dto_macro.py")):
        print(f"Error: Could not find serializer directory at {script_dir}")
        print(f"  Available globals: {[k for k in globals().keys() if 'dir' in k.lower() or 'script' in k.lower()]}")
        if 'initial_script_dir' in globals():
            print(f"  initial_script_dir: {globals()['initial_script_dir']}")
        if 'script_dir' in globals():
            print(f"  script_dir: {globals()['script_dir']}")
        if 'lib_dir' in globals():
            print(f"  lib_dir: {globals()['lib_dir']}")
        raise FileNotFoundError(f"Serializer directory not found: {script_dir}")

sys.path.insert(0, script_dir)

# Import serializer modules
s1_path = os.path.join(script_dir, "S1_check_dto_macro.py")
if not os.path.exists(s1_path):
    print(f"Error: Could not find S1_check_dto_macro.py at {s1_path}")
    print(f"  script_dir: {script_dir}")
    print(f"  Files in script_dir: {os.listdir(script_dir) if os.path.exists(script_dir) else 'directory does not exist'}")
    raise FileNotFoundError(f"S1_check_dto_macro.py not found at {s1_path}")

spec_s1 = importlib.util.spec_from_file_location("S1_check_dto_macro", s1_path)
S1_check_dto_macro = importlib.util.module_from_spec(spec_s1)
spec_s1.loader.exec_module(S1_check_dto_macro)

spec_s3 = importlib.util.spec_from_file_location("S3_inject_serialization", os.path.join(script_dir, "S3_inject_serialization.py"))
S3_inject_serialization = importlib.util.module_from_spec(spec_s3)
spec_s3.loader.exec_module(S3_inject_serialization)


def process_all_serializable_classes(dry_run=False):
    """
    Process all client files that contain classes with Serializable macro.
    
    Args:
        dry_run: If True, show what would be processed without modifying files
        
    Returns:
        Number of files processed
    """
    # Check if client_files is available (from 05_list_client_files.py)
    if 'client_files' not in globals() and 'get_client_files' not in globals():
        print("Error: client_files not available. Make sure 05_list_client_files.py has run before this script.")
        return 0
    
    # Get client files - filter to only header files
    if 'client_files' in globals():
        header_files = [f for f in globals()['client_files'] if f.endswith(('.h', '.hpp'))]
    elif 'get_client_files' in globals():
        header_files = globals()['get_client_files'](['.h', '.hpp'])
    else:
        header_files = []
    
    if not header_files:
        print("ℹ️  No client header files found")
        return 0
    
    print(f"🔍 Scanning {len(header_files)} header file(s) for Serializable classes...")
    
    processed_count = 0
    
    # Process each header file
    for file_path in header_files:
        if not os.path.exists(file_path):
            continue
        
        # Check if file has Serializable macro
        dto_info = S1_check_dto_macro.check_dto_macro(file_path)
        
        if not dto_info or not dto_info.get('has_dto'):
            continue
        
        class_name = dto_info['class_name']
        print(f"\n📝 Processing {os.path.basename(file_path)}: {class_name}")
        
        # Extract fields
        import S2_extract_dto_fields
        spec_s2 = importlib.util.spec_from_file_location("S2_extract_dto_fields", os.path.join(script_dir, "S2_extract_dto_fields.py"))
        S2_extract_dto_fields = importlib.util.module_from_spec(spec_s2)
        spec_s2.loader.exec_module(S2_extract_dto_fields)
        
        fields = S2_extract_dto_fields.extract_all_fields(file_path, class_name)
        
        if not fields:
            print(f"⚠️  Warning: No fields found in {class_name}")
            continue
        
        # Separate optional and non-optional fields
        optional_fields = [field for field in fields if S3_inject_serialization.is_optional_type(field['type'].strip())]
        non_optional_fields = [field for field in fields if not S3_inject_serialization.is_optional_type(field['type'].strip())]
        
        print(f"   Found {len(fields)} field(s): {len(optional_fields)} optional, {len(non_optional_fields)} non-optional")
        
        # Discover validation macros
        import S6_discover_validation_macros
        spec_s6 = importlib.util.spec_from_file_location("S6_discover_validation_macros", os.path.join(script_dir, "S6_discover_validation_macros.py"))
        S6_discover_validation_macros = importlib.util.module_from_spec(spec_s6)
        spec_s6.loader.exec_module(S6_discover_validation_macros)
        
        validation_macros = S6_discover_validation_macros.find_validation_macro_definitions(None)
        
        if validation_macros:
            print(f"   Discovered {len(validation_macros)} validation macro(s)")
        
        # Extract validation fields
        import S7_extract_validation_fields
        spec_s7 = importlib.util.spec_from_file_location("S7_extract_validation_fields", os.path.join(script_dir, "S7_extract_validation_fields.py"))
        S7_extract_validation_fields = importlib.util.module_from_spec(spec_s7)
        spec_s7.loader.exec_module(S7_extract_validation_fields)
        
        validation_fields_by_macro = S7_extract_validation_fields.extract_validation_fields(
            file_path, class_name, validation_macros
        )
        
        if validation_fields_by_macro:
            total_validated = sum(len(fields) for fields in validation_fields_by_macro.values())
            print(f"   {total_validated} field(s) with validation macros")
        
        # Generate and inject methods
        methods_code = S3_inject_serialization.generate_serialization_methods(class_name, fields, validation_fields_by_macro)
        
        # Add includes if needed
        if not dry_run:
            S3_inject_serialization.add_include_if_needed(file_path, "<ArduinoJson.h>")
            if optional_fields:
                S3_inject_serialization.add_include_if_needed(file_path, "<optional>")
        
        # Inject methods
        success = S3_inject_serialization.inject_methods_into_class(file_path, class_name, methods_code, dry_run=dry_run)
        
        if success:
            # Comment out Serializable macro
            if not dry_run:
                S3_inject_serialization.comment_dto_macro(file_path, dry_run=False)
            processed_count += 1
            print(f"   ✅ Successfully processed {class_name}")
        else:
            print(f"   ❌ Failed to process {class_name}")
    
    return processed_count


def main():
    """Main function to process all Serializable classes."""
    processed_count = process_all_serializable_classes(dry_run=False)
    
    if processed_count > 0:
        print(f"\n✅ Successfully processed {processed_count} file(s) with Serializable classes")
    else:
        print("\nℹ️  No files with Serializable classes found")
    
    return 0


if __name__ == "__main__":
    exit(main())
