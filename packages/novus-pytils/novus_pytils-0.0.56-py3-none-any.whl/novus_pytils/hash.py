import hashlib
def get_file_md5_hash(file_path):
    """
    Calculate the MD5 hash of a file.

    Args:
        file_path (str): The path to the file for which the MD5 hash is to be calculated.

    Returns:
        str: The MD5 hash of the file in hexadecimal format.
    """

    with open(file_path, 'rb') as file:
        md5_hash = hashlib.md5(file.read()).hexdigest()
    return md5_hash

def get_str_md5_hash(string):
    """
    Calculate the MD5 hash of a given string.

    Args:
        string (str): The input string to hash.

    Returns:
        str: The MD5 hash of the string in hexadecimal format.
    """

    return hashlib.md5(string.encode()).hexdigest()

def get_str_sha256_hash(string):
    """
    Calculate the SHA-256 hash of a given string.

    Args:
        string (str): The input string to hash.

    Returns:
        str: The SHA-256 hash of the string in hexadecimal format.
    """
    return hashlib.sha256(string.encode()).hexdigest()

def get_file_sha256_hash(file_path):
    """
    Calculate the SHA-256 hash of a file.

    Args:
        file_path (str): The path to the file for which the SHA-256 hash is to be calculated.

    Returns:
        str: The SHA-256 hash of the file in hexadecimal format.
    """

    with open(file_path, 'rb') as file:
        sha256_hash = hashlib.sha256(file.read()).hexdigest()
    return sha256_hash

