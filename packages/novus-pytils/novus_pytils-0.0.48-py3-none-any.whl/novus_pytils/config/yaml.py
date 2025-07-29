import yaml
from novus_pytils.files import file_exists

def load_yaml(filepath : str) -> dict:
    """
    Load a yaml file and return the contents as a dictionary.

    Args:
        filepath (str): The path to the yaml file.

    Returns:
        dict: The contents of the yaml file as a dictionary.
    """

    if not file_exists(filepath):
        raise FileNotFoundError(f"File not found: {filepath}")
    with open(filepath, 'r') as f:
        return yaml.safe_load(f)
    
