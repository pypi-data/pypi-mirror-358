import os
import json


def load_all_errors():
    """Load all error codes from the specified error files."""
    # Get the directory where the current script (manager.py) is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # The errors directory is assumed to be parallel to manager.py
    errors_dir = os.path.join(current_dir, "errors")

    # Load the main error codes JSON file
    main_errors_path = os.path.join(errors_dir, "error-codes.json")
    main_errors = load_json(main_errors_path)

    error_codes = {}
    for category, file_name in main_errors.items():
        file_path = os.path.join(errors_dir, file_name)
        error_codes[category.lower()] = load_json(file_path)
    return error_codes

def load_json(file_path):
    """Load a JSON file from the given file path."""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
        return {}
    
def get_all_error_codes():
    """Return all error codes as a flat structure."""
    error_codes = load_all_errors()
    all_error_codes = {}
    for category in error_codes.values():
        all_error_codes.update(category)
    return all_error_codes

def get_categories():
    """Load the category-to-file mappings from the JSON file."""
    # Get the current directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Path to the 'errors' directory where 'error-codes.json' is located
    errors_dir = os.path.join(current_dir, "errors")
    
    # The error-codes.json file is now inside the 'errors' folder
    mapping_file = os.path.join(errors_dir, "error-codes.json")
    category_mapping = load_json(mapping_file)
    
    return list(category_mapping.keys())
  
def load_category_mapping():
    """Load the category-to-file mappings from the JSON file."""
    # Get the current directory where the script is located
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the 'errors' directory where 'error-codes.json' is located
    errors_dir = os.path.join(current_dir, "errors")
    
    # The error-codes.json file is now inside the 'errors' folder
    mapping_file = os.path.join(errors_dir, "error-codes.json")
    
    return load_json(mapping_file)

def get_error_codes_by_category(category):
    """Return error codes for a specific category using the category-to-file mapping."""
    # Load the category-to-file mapping
    category_mapping = load_category_mapping()
    
    # Fetch the file path for the given category
    error_file_path = category_mapping.get(category)
    if not error_file_path:
        print(f"Error: No mapping found for category {category}.")
        return {}
    
    # Adjust the file path if it's relative
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_file_path = os.path.join(current_dir, "errors", error_file_path.lstrip("./"))
    
    # Load and return the error codes from the specific file
    return load_json(full_file_path)

