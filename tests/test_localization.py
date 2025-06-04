#!/usr/bin/env python3
"""
Test script to verify localization files.
"""

import os
import json
import sys

def load_localization_file(lang_code):
    """Load a localization file and return its contents."""
    file_path = f"../resources/localization/{lang_code}.json"
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: Localization file for '{lang_code}' not found.")
        return None
    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON in '{lang_code}.json': {e}")
        return None

def compare_keys(base_lang, test_lang, base_dict, test_dict, path=""):
    """Compare keys between two dictionaries recursively."""
    missing_keys = []
    
    for key in base_dict:
        new_path = f"{path}.{key}" if path else key
        
        if key not in test_dict:
            missing_keys.append(new_path)
        elif isinstance(base_dict[key], dict) and isinstance(test_dict[key], dict):
            missing_keys.extend(compare_keys(base_lang, test_lang, base_dict[key], test_dict[key], new_path))
    
    return missing_keys

def test_localization_files():
    """Test all localization files against the English base file."""
    # Available language codes
    lang_codes = ['en', 'es', 'de', 'sv', 'tr']
    
    # Load English as the base language
    base_lang = load_localization_file('en')
    if not base_lang:
        print("Failed to load base language (English).")
        return False
    
    all_valid = True
    
    # Test each language
    for lang_code in lang_codes:
        if lang_code == 'en':
            continue  # Skip English as it's the base
        
        print(f"Testing {lang_code}...")
        lang_data = load_localization_file(lang_code)
        
        if not lang_data:
            all_valid = False
            continue
        
        # Check for missing keys
        missing_keys = compare_keys('en', lang_code, base_lang, lang_data)
        if missing_keys:
            all_valid = False
            print(f"  Missing keys in {lang_code}:")
            for key in missing_keys:
                print(f"    - {key}")
        else:
            print(f"  {lang_code} has all required keys.")
    
    return all_valid

if __name__ == "__main__":
    print("Testing localization files...")
    if test_localization_files():
        print("\nAll localization files are valid!")
    else:
        print("\nSome localization files have issues. Please check the output above.")
