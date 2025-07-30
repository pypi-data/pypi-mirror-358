import os

"""
Contains utility functions
"""

def load_api_key(name: str) -> str:
    """
    Loads the API key from multiple possible file locations.
    """
    
    possible_paths = [
        f"../secret/{name}.txt",
        f"secret/{name}.txt",
        f"../../secret/{name}.txt",
    ]

    for path in possible_paths:
        if os.path.isfile(path):
            with open(path, "r", encoding='utf-8') as f:
                return f.read().strip()

    raise FileNotFoundError(f"API key file for '{name}' not found in any of the expected locations: {possible_paths}")
