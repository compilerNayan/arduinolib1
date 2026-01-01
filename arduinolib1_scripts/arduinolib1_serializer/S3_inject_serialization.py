#!/usr/bin/env python3
"""
S3 Inject Serialization Script

This script injects Serialize() and Deserialize() methods into Dto classes.
"""

import argparse
import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Optional

print("Executing NayanSerializer/scripts/serializer/S3_inject_serialization.py")

# Add parent directory to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

try:
    import S1_check_dto_macro
    import S2_extract_dto_fields
    import S6_discover_validation_macros
    import S7_extract_validation_fields
except ImportError as e:
    print(f"Error: Could not import required modules: {e}")
    print("Make sure S1_check_dto_macro.py, S2_extract_dto_fields.py, S6_discover_validation_macros.py, and S7_extract_validation_fields.py are in the same directory.")
    sys.exit(1)


def check_include_exists(file_path: str, include_pattern: str) -> bool:
    """
    Check if an include statement already exists in the file.
    
    Args:
        file_path: Path to the C++ file
        include_pattern: Pattern to search for (e.g., "ArduinoJson.h")
        
    Returns:
        True if include exists, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            # Check if include pattern exists
            return include_pattern in content or f'<{include_pattern}>' in content or f'"{include_pattern}"' in content
    except Exception:
        return False


def add_include_if_needed(file_path: str, include_path: str) -> bool:
    """
    Add an include statement if it doesn't already exist.
    
    Args:
        file_path: Path to the C++ file
        include_path: Include path to add (e.g., "<ArduinoJson.h>" or '"some/header.h"')
        
    Returns:
        True if include was added or already exists, False on error
    """
    if check_include_exists(file_path, include_path.replace('<', '').replace('>', '').replace('"', '')):
        return True
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        # Find the last #include line
        last_include_idx = -1
        for i, line in enumerate(lines):
            if line.strip().startswith('#include'):
                last_include_idx = i
        
        # Insert after the last include
        if last_include_idx >= 0:
            lines.insert(last_include_idx + 1, f'#include {include_path}\n')
        else:
            # No includes found, add after header guard
            for i, line in enumerate(lines):
                if line.strip().startswith('#define') and '_H' in line:
                    lines.insert(i + 1, f'#include {include_path}\n')
                    break
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        
        return True
    except Exception as e:
        print(f"Error adding include: {e}")
        return False


def is_optional_type(field_type: str) -> bool:
    """
    Check if a field type is an optional type.
    
    Args:
        field_type: The type string to check
        
    Returns:
        True if the type is optional, False otherwise
    """
    field_type_clean = field_type.strip()
    # Check for patterns like: optional<...>, std::optional<...>
    return 'optional<' in field_type_clean or 'std::optional<' in field_type_clean


def extract_inner_type_from_optional(field_type: str) -> str:
    """
    Extract the inner type from an optional type.
    E.g., "optional<int>" -> "int", "std::optional<StdString>" -> "StdString"
    
    Args:
        field_type: The optional type string
        
    Returns:
        The inner type string
    """
    # Match optional<...> or std::optional<...>
    match = re.search(r'(?:std::)?optional<(.+)>', field_type)
    if match:
        return match.group(1).strip()
    return field_type


def generate_serialization_methods(class_name: str, fields: List[Dict[str, str]], validation_fields_by_macro: Dict[str, List[Dict[str, str]]] = None) -> str:
    """
    Generate Serialize() and Deserialize() methods for a Dto class.
    
    Args:
        class_name: Name of the class
        fields: List of field dictionaries with 'type' and 'name'
        validation_fields_by_macro: Dictionary mapping validation macro names to lists of fields
                                   Each field dict should have 'type', 'name', 'access', and 'function_name'
        
    Returns:
        Generated code as string
    """
    if validation_fields_by_macro is None:
        validation_fields_by_macro = {}
    code_lines = []
    
    # Generate Serialize() method
    code_lines.append("    // Serialization method")
    code_lines.append(f"    Public StdString Serialize() const {{")
    code_lines.append("        // Create JSON document")
    code_lines.append("        JsonDocument doc;")
    code_lines.append("")
    
    # Only serialize optional fields - skip non-optional fields
    # Primitive types that can be serialized directly
    primitive_types = ['int', 'Int', 'CInt', 'long', 'Long', 'CLong', 'float', 'Float', 'CFloat', 
                      'double', 'Double', 'CDouble', 'bool', 'Bool', 'CBool', 'char', 'Char', 'CChar',
                      'unsigned', 'UInt', 'CUInt', 'short', 'Short', 'CShort']
    
    # Filter to only optional fields
    optional_fields = [field for field in fields if is_optional_type(field['type'].strip())]
    
    if not optional_fields:
        code_lines.append("        // No optional fields to serialize")
    else:
        for field in optional_fields:
            field_type = field['type'].strip()
            field_name = field['name']
            
            # Extract inner type
            inner_type = extract_inner_type_from_optional(field_type)
            
            # Check inner type characteristics
            is_primitive = any(prim in inner_type for prim in primitive_types)
            is_string = 'StdString' in inner_type or 'CStdString' in inner_type or 'string' in inner_type.lower()
            
            # Generate code to check if optional has value
            code_lines.append(f"        // Serialize optional field: {field_name}")
            code_lines.append(f"        if ({field_name}.has_value()) {{")
            
            if is_string:
                code_lines.append(f"            doc[\"{field_name}\"] = {field_name}.value().c_str();")
            elif is_primitive:
                code_lines.append(f"            doc[\"{field_name}\"] = {field_name}.value();")
            else:
                # For nested object types in optional
                code_lines.append(f"            // Serialize nested object: {field_name}")
                code_lines.append(f"            StdString {field_name}_json = {field_name}.value().Serialize();")
                code_lines.append(f"            JsonDocument {field_name}_doc;")
                code_lines.append(f"            deserializeJson({field_name}_doc, {field_name}_json.c_str());")
                code_lines.append(f"            doc[\"{field_name}\"] = {field_name}_doc;")
            
            code_lines.append(f"        }} else {{")
            code_lines.append(f"            doc[\"{field_name}\"] = nullptr;")
            code_lines.append(f"        }}")
    
    code_lines.append("")
    code_lines.append("        // Serialize to string")
    code_lines.append("        StdString output;")
    code_lines.append("        serializeJson(doc, output);")
    code_lines.append("")
    code_lines.append("        return StdString(output.c_str());")
    code_lines.append("    }")
    code_lines.append("")
    
    # Always generate validation function (even if empty) so nested objects can call it
    code_lines.append("        // Validation method for all validation macros")
    code_lines.append(f"        Public template<typename DocType>")
    code_lines.append(f"        Static StdString ValidateFields(DocType& doc) {{")
    code_lines.append("        StdString validationErrors;")
    code_lines.append("")
    
    if validation_fields_by_macro:
        # Collect all fields to check for nested object validation
        all_fields_dict = {field['name']: field for field in fields}
        primitive_types = ['int', 'Int', 'CInt', 'long', 'Long', 'CLong', 'float', 'Float', 'CFloat', 
                          'double', 'Double', 'CDouble', 'bool', 'Bool', 'CBool', 'char', 'Char', 'CChar',
                          'unsigned', 'UInt', 'CUInt', 'short', 'Short', 'CShort']
        
        # Generate validation calls for each validation macro type
        for macro_name, fields_list in validation_fields_by_macro.items():
            for field in fields_list:
                field_name = field['name']
                field_type = field['type'].strip()
                function_name = field['function_name']
                
                # Check if this is a nested object type (optional<SomeClass>)
                is_nested_object = False
                nested_type = None
                if is_optional_type(field_type):
                    inner_type = extract_inner_type_from_optional(field_type)
                    is_primitive = any(prim in inner_type for prim in primitive_types)
                    is_string = 'StdString' in inner_type or 'CStdString' in inner_type or 'string' in inner_type.lower()
                    if not is_primitive and not is_string:
                        is_nested_object = True
                        nested_type = inner_type
                
                # If nested object, validate nested object first (before validating the field itself)
                if is_nested_object and nested_type:
                    code_lines.append(f"        // First validate nested object: {field_name}")
                    code_lines.append(f"        if (!doc[\"{field_name}\"].isNull()) {{")
                    code_lines.append(f"            // Extract nested object and convert to JsonDocument for validation")
                    code_lines.append(f"            JsonObject {field_name}_obj = doc[\"{field_name}\"].template as<JsonObject>();")
                    code_lines.append(f"            JsonDocument {field_name}_doc;")
                    code_lines.append(f"            // Copy the JsonObject into JsonDocument")
                    code_lines.append(f"            {field_name}_doc.set({field_name}_obj);")
                    code_lines.append(f"            // Validate nested object's fields")
                    code_lines.append(f"            StdString {field_name}_nested_errors = {nested_type}::ValidateFields({field_name}_doc);")
                    code_lines.append(f"            if (!{field_name}_nested_errors.empty()) {{")
                    code_lines.append(f"                if (!validationErrors.empty()) validationErrors += \",\\n\";")
                    code_lines.append(f"                validationErrors += \"Validation errors in nested object '{field_name}': \";")
                    code_lines.append(f"                validationErrors += {field_name}_nested_errors;")
                    code_lines.append(f"            }}")
                    code_lines.append(f"        }}")
                    code_lines.append(f"")
                
                # Now validate the field itself (e.g., NotNull)
                # Ensure function_name uses fully qualified namespace
                qualified_function_name = function_name
                if not qualified_function_name.startswith('nayan::'):
                    # If function_name is like "DtoValidationUtility::ValidateNotNull" (without namespace),
                    # prepend "nayan::validation::" to make it fully qualified
                    qualified_function_name = f"nayan::validation::{qualified_function_name}"
                
                code_lines.append(f"        // Validate {macro_name} field: {field_name}")
                code_lines.append(f"        {qualified_function_name}(doc, \"{field_name}\", validationErrors);")
    else:
        code_lines.append("        // No validation macros defined for this class")
    
    code_lines.append("")
    code_lines.append("        return validationErrors;")
    code_lines.append("    }")
    code_lines.append("")
    
    # Generate static Deserialize() method
    code_lines.append("    // Deserialization method")
    code_lines.append(f"    Public Static {class_name} Deserialize(CStdString& data) {{")
    code_lines.append("        // Create JSON document")
    code_lines.append("        JsonDocument doc;")
    code_lines.append("")
    code_lines.append("        // Deserialize JSON string")
    code_lines.append("        DeserializationError error = deserializeJson(doc, data.c_str());")
    code_lines.append("")
    code_lines.append("        if (error) {")
    code_lines.append("            StdString errorMsg = \"JSON parse error: \";")
    code_lines.append("            errorMsg += error.c_str();")
    code_lines.append("            throw std::runtime_error(errorMsg.c_str());")
    code_lines.append("        }")
    code_lines.append("")
    
    # Validate fields using the separate validation function (always call, even if empty)
    code_lines.append("        // Validate all fields with validation macros")
    code_lines.append("        StdString validationErrors = ValidateFields(doc);")
    code_lines.append("        if (!validationErrors.empty()) {")
    code_lines.append("            throw std::runtime_error(validationErrors.c_str());")
    code_lines.append("        }")
    code_lines.append("")
    
    # Create object with default constructor (only after validation passes)
    code_lines.append("        // Create object with default constructor")
    code_lines.append(f"        {class_name} obj;")
    code_lines.append("")
    
    # Only deserialize optional fields - skip non-optional fields
    code_lines.append("        // Assign values from JSON if present (only optional fields)")
    # Primitive types that can be deserialized directly
    primitive_types = ['int', 'Int', 'CInt', 'long', 'Long', 'CLong', 'float', 'Float', 'CFloat', 
                      'double', 'Double', 'CDouble', 'bool', 'Bool', 'CBool', 'char', 'Char', 'CChar',
                      'unsigned', 'UInt', 'CUInt', 'short', 'Short', 'CShort']
    
    # Filter to only optional fields
    optional_fields = [field for field in fields if is_optional_type(field['type'].strip())]
    
    # Create set of validated field names for quick lookup
    validated_field_names = set()
    for fields_list in validation_fields_by_macro.values():
        for field in fields_list:
            validated_field_names.add(field['name'])
    
    if not optional_fields:
        code_lines.append("        // No optional fields to deserialize")
    else:
        for field in optional_fields:
            field_type = field['type'].strip()
            field_name = field['name']
            is_validated = field_name in validated_field_names
            
            # Extract inner type
            inner_type = extract_inner_type_from_optional(field_type)
            
            # Check inner type characteristics
            is_primitive = any(prim in inner_type for prim in primitive_types)
            is_string = 'StdString' in inner_type or 'CStdString' in inner_type or 'string' in inner_type.lower()
            
            # For validated fields, directly assign (already validated above)
            # For optional fields, check if key exists and is not null
            if is_validated:
                # Find which validation macros apply to this field
                validation_macros = []
                for macro_name, fields_list in validation_fields_by_macro.items():
                    if any(f['name'] == field_name for f in fields_list):
                        validation_macros.append(macro_name)
                validation_desc = "+".join(validation_macros) if validation_macros else "validated"
                code_lines.append(f"        // Deserialize {validation_desc} field: {field_name} (already validated)")
                # Direct assignment for NotNull fields (no if check needed)
                if is_string:
                    code_lines.append(f"        obj.{field_name} = StdString(doc[\"{field_name}\"].as<const char*>());")
                elif is_primitive:
                    # Handle different primitive types
                    if 'bool' in inner_type.lower() or 'Bool' in inner_type:
                        code_lines.append(f"        obj.{field_name} = doc[\"{field_name}\"].as<bool>();")
                    elif 'int' in inner_type.lower() or 'Int' in inner_type:
                        code_lines.append(f"        obj.{field_name} = doc[\"{field_name}\"].as<int>();")
                    elif 'float' in inner_type.lower() or 'Float' in inner_type:
                        code_lines.append(f"        obj.{field_name} = doc[\"{field_name}\"].as<float>();")
                    elif 'double' in inner_type.lower() or 'Double' in inner_type:
                        code_lines.append(f"        obj.{field_name} = doc[\"{field_name}\"].as<double>();")
                    elif 'char' in inner_type.lower() or 'Char' in inner_type:
                        code_lines.append(f"        obj.{field_name} = doc[\"{field_name}\"].as<char>();")
                    else:
                        code_lines.append(f"        obj.{field_name} = doc[\"{field_name}\"].as<{inner_type}>();")
                else:
                    # For nested object types in optional
                    code_lines.append(f"        // Deserialize nested object: {field_name}")
                    code_lines.append(f"        JsonObject {field_name}_obj = doc[\"{field_name}\"].as<JsonObject>();")
                    code_lines.append(f"        StdString {field_name}_json;")
                    code_lines.append(f"        serializeJson({field_name}_obj, {field_name}_json);")
                    code_lines.append(f"        obj.{field_name} = {inner_type}::Deserialize({field_name}_json);")
            else:
                code_lines.append(f"        // Deserialize optional field: {field_name}")
                code_lines.append(f"        if (!doc[\"{field_name}\"].isNull()) {{")
                
                if is_string:
                    code_lines.append(f"            obj.{field_name} = StdString(doc[\"{field_name}\"].as<const char*>());")
                elif is_primitive:
                    # Handle different primitive types
                    if 'bool' in inner_type.lower() or 'Bool' in inner_type:
                        code_lines.append(f"            obj.{field_name} = doc[\"{field_name}\"].as<bool>();")
                    elif 'int' in inner_type.lower() or 'Int' in inner_type:
                        code_lines.append(f"            obj.{field_name} = doc[\"{field_name}\"].as<int>();")
                    elif 'float' in inner_type.lower() or 'Float' in inner_type:
                        code_lines.append(f"            obj.{field_name} = doc[\"{field_name}\"].as<float>();")
                    elif 'double' in inner_type.lower() or 'Double' in inner_type:
                        code_lines.append(f"            obj.{field_name} = doc[\"{field_name}\"].as<double>();")
                    elif 'char' in inner_type.lower() or 'Char' in inner_type:
                        code_lines.append(f"            obj.{field_name} = doc[\"{field_name}\"].as<char>();")
                    else:
                        code_lines.append(f"            obj.{field_name} = doc[\"{field_name}\"].as<{inner_type}>();")
                else:
                    # For nested object types in optional
                    code_lines.append(f"            // Deserialize nested object: {field_name}")
                    code_lines.append(f"            JsonObject {field_name}_obj = doc[\"{field_name}\"].as<JsonObject>();")
                    code_lines.append(f"            StdString {field_name}_json;")
                    code_lines.append(f"            serializeJson({field_name}_obj, {field_name}_json);")
                    code_lines.append(f"            obj.{field_name} = {inner_type}::Deserialize({field_name}_json);")
                
                code_lines.append(f"        }}")
                # Note: If key doesn't exist or is null, optional remains unset (default state)
    
    code_lines.append("")
    code_lines.append("        return obj;")
    
    code_lines.append("    }")
    
    return "\n".join(code_lines)


def convert_annotation_to_processed(file_path: str, dry_run: bool = False, annotation_name: str = "Serializable") -> bool:
    """
    Convert //@AnnotationName to /*@AnnotationName*/ in a C++ file.
    This marks the annotation as processed so it won't be processed again.
    
    Args:
        file_path: Path to the C++ file to modify
        dry_run: If True, only show what would be changed without making changes
        annotation_name: Name of the annotation to convert (default: "Serializable")
        
    Returns:
        True if file was modified successfully or would be modified, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        modified = False
        modified_lines = []
        
        # Pattern to match //@AnnotationName (case-sensitive)
        annotation_pattern = rf'^(\s*)//@({re.escape(annotation_name)})\s*$'
        
        for i, line in enumerate(lines):
            original_line = line
            stripped_line = line.strip()
            
            # Skip already processed annotations (/*@AnnotationName*/)
            if re.match(rf'^\s*/\*@{re.escape(annotation_name)}\*/\s*$', stripped_line):
                modified_lines.append(line)
                continue
            
            # Check if line contains //@AnnotationName annotation
            match = re.match(annotation_pattern, line)
            if match:
                indent = match.group(1)
                annotation = match.group(2)
                # Convert to /*@AnnotationName*/
                if not dry_run:
                    modified_lines.append(f'{indent}/*@{annotation}*/\n')
                else:
                    modified_lines.append(line)  # Keep original for dry run display
                modified = True
                if dry_run:
                    print(f"    Would convert: {stripped_line} -> /*@{annotation}*/")
            else:
                modified_lines.append(line)
        
        # Write back to file if modifications were made and not dry run
        if modified and not dry_run:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.writelines(modified_lines)
            print(f"✓ Converted //@{annotation_name} to /*@{annotation_name}*/ in: {file_path}")
        elif modified and dry_run:
            print(f"  Would convert //@{annotation_name} to /*@{annotation_name}*/ in: {file_path}")
        elif not modified:
            # No annotation found (this is fine, might already be processed)
            pass
        
        return True
        
    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found")
        return False
    except Exception as e:
        print(f"Error modifying file '{file_path}': {e}")
        return False


def inject_methods_into_class(file_path: str, class_name: str, methods_code: str, dry_run: bool = False) -> bool:
    """
    Inject serialization methods into a class before the closing brace.
    
    Args:
        file_path: Path to the C++ file
        class_name: Name of the class
        methods_code: Code to inject
        dry_run: If True, don't actually modify the file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()
    except Exception as e:
        print(f"Error reading file: {e}")
        return False
    
    # Find class boundaries
    boundaries = S2_extract_dto_fields.find_class_boundaries(file_path, class_name)
    if not boundaries:
        print(f"Error: Could not find class boundaries for {class_name}")
        return False
    
    start_line, end_line = boundaries
    
    # Find the closing brace line (should be end_line)
    # Look for the line with just "};" or "} ;"
    closing_line_idx = end_line - 1  # Convert to 0-indexed
    
    # Check if methods already exist
    class_content = ''.join(lines[start_line - 1:end_line])
    if 'Serialize()' in class_content and 'Deserialize(' in class_content:
        print(f"ℹ️  Serialization methods already exist in {class_name}")
        return True
    
    if dry_run:
        print(f"Would inject methods before line {end_line}:")
        print(methods_code)
        return True
    
    # Insert methods before the closing brace
    # Find the last non-empty, non-comment line before the closing brace
    insert_idx = closing_line_idx
    for i in range(closing_line_idx - 1, start_line - 2, -1):
        line = lines[i].strip()
        if line and not line.startswith('//') and not line.startswith('/*'):
            insert_idx = i + 1
            break
    
    # Insert the methods code
    methods_lines = methods_code.split('\n')
    # Add proper indentation to match class indentation
    indent = "    "  # Default 4 spaces
    if insert_idx > 0 and lines[insert_idx - 1]:
        # Detect indentation from previous line
        leading_spaces = len(lines[insert_idx - 1]) - len(lines[insert_idx - 1].lstrip())
        if leading_spaces > 0:
            indent = lines[insert_idx - 1][:leading_spaces]
    
    # Indent each line (except empty lines)
    indented_methods = []
    for line in methods_lines:
        if line.strip():  # Non-empty line
            indented_methods.append(indent + line + '\n')
        else:  # Empty line
            indented_methods.append('\n')
    
    # Insert with a blank line before
    lines[insert_idx:insert_idx] = ['\n'] + indented_methods
    
    # Write back to file
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            file.writelines(lines)
        print(f"✅ Injected serialization methods into {class_name}")
        return True
    except Exception as e:
        print(f"Error writing file: {e}")
        return False


def main():
    """Main function to handle command line arguments and inject serialization methods."""
    parser = argparse.ArgumentParser(
        description="Inject Serialize() and Deserialize() methods into Dto classes"
    )
    parser.add_argument(
        "file_path",
        help="Path to the C++ Dto class file"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be injected without modifying the file"
    )
    
    args = parser.parse_args()
    
    # Check if class has Serializable macro
    dto_info = S1_check_dto_macro.check_dto_macro(args.file_path)
    
    if not dto_info or not dto_info.get('has_dto'):
        print("❌ Error: Class does not have //@Serializable annotation")
        return 1
    
    class_name = dto_info['class_name']
    print(f"✅ Found //@Serializable class: {class_name}")
    
    # Extract fields (all access levels: public, private, protected, or no specifier)
    fields = S2_extract_dto_fields.extract_all_fields(args.file_path, class_name)
    
    if not fields:
        print("⚠️  Warning: No fields found in class")
        return 1
    
    # Separate optional and non-optional fields
    optional_fields = [field for field in fields if is_optional_type(field['type'].strip())]
    non_optional_fields = [field for field in fields if not is_optional_type(field['type'].strip())]
    
    print(f"📋 Found {len(fields)} field(s) total:")
    if optional_fields:
        print(f"   ✅ {len(optional_fields)} optional field(s) (will be serialized):")
        for field in optional_fields:
            print(f"      {field['type']} {field['name']}")
    if non_optional_fields:
        print(f"   ⏭️  {len(non_optional_fields)} non-optional field(s) (will be skipped):")
        for field in non_optional_fields:
            print(f"      {field['type']} {field['name']}")
    
    # Check if any fields are optional
    has_optional_fields = len(optional_fields) > 0
    
    if not has_optional_fields:
        print("⚠️  Warning: No optional fields found. Serialization methods will be empty.")
    
    # Discover validation macros from source files
    # Pass None to use client_files from 05_list_client_files.py
    validation_macros = S6_discover_validation_macros.find_validation_macro_definitions(None)
    
    if validation_macros:
        print(f"🔍 Discovered {len(validation_macros)} validation macro(s):")
        for macro_name, function_name in sorted(validation_macros.items()):
            print(f"   {macro_name} -> {function_name}")
    
    # Extract fields with validation macros (generic approach)
    validation_fields_by_macro = S7_extract_validation_fields.extract_validation_fields(
        args.file_path, class_name, validation_macros
    )
    
    if validation_fields_by_macro:
        total_validated = sum(len(fields) for fields in validation_fields_by_macro.values())
        print(f"   🔒 {total_validated} field(s) with validation macros (will be validated):")
        for macro_name, fields_list in sorted(validation_fields_by_macro.items()):
            print(f"      {macro_name} ({len(fields_list)} field(s)):")
            for field in fields_list:
                print(f"         {field['type']} {field['name']} (access: {field['access']})")
    
    # Generate methods code
    methods_code = generate_serialization_methods(class_name, fields, validation_fields_by_macro)
    
    # Add includes if needed
    if not args.dry_run:
        # Note: ArduinoJson.h is already included in NayanSerializer.h, so no need to add it here
        # Add optional include if any fields are optional
        if has_optional_fields:
            add_include_if_needed(args.file_path, "<optional>")
        # Note: DtoValidationUtility.h is included via DIDef.h -> SerializerIncludes.h, so no need to include it here
    
    # Inject methods into class
    success = inject_methods_into_class(args.file_path, class_name, methods_code, dry_run=args.dry_run)
    
    if not success:
        return 1
    
    # Convert //@Serializable to /*@Serializable*/ after successful injection
    # Get annotation name from environment or use default
    annotation_name = os.environ.get("SERIALIZABLE_MACRO", "Serializable")
    if not args.dry_run:
        print(f"  Converting //@{annotation_name} to /*@{annotation_name}*/ in: {args.file_path}")
    else:
        print(f"  Would convert //@{annotation_name} to /*@{annotation_name}*/ in: {args.file_path}")
    convert_annotation_to_processed(args.file_path, dry_run=args.dry_run, annotation_name=annotation_name)
    
    if args.dry_run:
        print("\n🔍 DRY RUN MODE - Generated methods code:")
        print("="*70)
        print(methods_code)
        print("="*70)
    
    return 0


# Export functions for other scripts to import
__all__ = [
    'check_include_exists',
    'add_include_if_needed',
    'is_optional_type',
    'extract_inner_type_from_optional',
    'generate_serialization_methods',
    'convert_annotation_to_processed',
    'inject_methods_into_class',
    'main'
]


if __name__ == "__main__":
    exit(main())

