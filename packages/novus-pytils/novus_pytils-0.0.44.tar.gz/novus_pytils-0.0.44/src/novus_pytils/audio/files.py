# Supported audio file extensions
SUPPORTED_EXTENSIONS = ['.wav', '.ogg', '.flac', '.mp3', '.mp4']
from .files import get_files_by_extension

def find_audio_files(input_dir):
    """
    Find all supported audio files in the input directory recursively.
    
    Args:
        input_dir (Path): Input directory path
    
    Returns:
        list: List of Path objects for audio files
    """
    # audio_files = []
    
    # for file_path in input_dir.rglob('*'):
    #     if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
    #         audio_files.append(file_path)

    audio_files = get_files_by_extension(input_dir, SUPPORTED_EXTENSIONS)
    
    return audio_files