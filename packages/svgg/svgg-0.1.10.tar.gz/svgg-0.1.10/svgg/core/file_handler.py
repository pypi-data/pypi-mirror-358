"""
File Handler Module

This module provides file handling functionality for SVG files and their
embedded content, including reading, writing, and managing file operations.
"""

import os
import base64
import mimetypes
from typing import Union

class FileHandler:
    """
    A class to handle file operations for SVG files and their embedded content.
    
    This class provides methods for reading, writing, and managing files,
    including handling of binary and text content, MIME type detection,
    and file system operations.
    """
    
    @staticmethod
    def read_file(file_path: str, binary: bool = False) -> Union[str, bytes]:
        """Read the contents of a file.
        
        Args:
            file_path: Path to the file to read
            binary: Whether to read the file in binary mode
            
        Returns:
            File contents as string or bytes
            
        Raises:
            FileNotFoundError: If the file does not exist
            IOError: If there is an error reading the file
        """
        mode = 'rb' if binary else 'r'
        encoding = None if binary else 'utf-8'
        
        try:
            with open(file_path, mode, encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file {file_path}: {str(e)}")

    @staticmethod
    def write_file(file_path: str, content: Union[str, bytes], 
                  binary: bool = False) -> None:
        """Write content to a file.
        
        Args:
            file_path: Path to the file to write
            content: Content to write (string or bytes)
            binary: Whether to write in binary mode
            
        Raises:
            IOError: If there is an error writing the file
        """
        mode = 'wb' if binary or isinstance(content, bytes) else 'w'
        encoding = None if binary or isinstance(content, bytes) else 'utf-8'
        
        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(os.path.abspath(file_path)), exist_ok=True)
        
        try:
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Error writing to file {file_path}: {str(e)}")
    
    @staticmethod
    def get_mime_type(file_path: str) -> str:
        """Get the MIME type of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MIME type as string (defaults to 'application/octet-stream' if unknown)
        """
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def file_exists(file_path: str) -> bool:
        """Check if a file exists.
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if the file exists, False otherwise
        """
        return os.path.isfile(file_path)
    
    @staticmethod
    def directory_exists(directory: str) -> bool:
        """Check if a directory exists.
        
        Args:
            directory: Path to the directory
            
        Returns:
            True if the directory exists, False otherwise
        """
        return os.path.isdir(directory)
    
    @staticmethod
    def create_directory(directory: str) -> None:
        """Create a directory if it doesn't exist.
        
        Args:
            directory: Path to the directory to create
            
        Raises:
            OSError: If the directory cannot be created
        """
        os.makedirs(directory, exist_ok=True)
    
    @staticmethod
    def get_file_size(file_path: str) -> int:
        """Get the size of a file in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Size of the file in bytes
            
        Raises:
            FileNotFoundError: If the file does not exist
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        return os.path.getsize(file_path)
    
    @staticmethod
    def encode_file_to_base64(file_path: str) -> str:
        """Encode a file to base64.
        
        Args:
            file_path: Path to the file to encode
            
        Returns:
            Base64-encoded string of the file content
            
        Raises:
            IOError: If there is an error reading the file
        """
        try:
            with open(file_path, 'rb') as f:
                return base64.b64encode(f.read()).decode('utf-8')
        except Exception as e:
            raise IOError(
                f"Error encoding file {file_path} to base64: {str(e)}"
            )
    
    @staticmethod
    def decode_base64_to_file(encoded_data: str, output_path: str) -> None:
        """Decode base64 data and write to a file.
        
        Args:
            encoded_data: Base64-encoded data as string
            output_path: Path where to save the decoded file
            
        Raises:
            ValueError: If the encoded data is invalid
            IOError: If there is an error writing the file
        """
        try:
            decoded_data = base64.b64decode(encoded_data)
            with open(output_path, 'wb') as f:
                f.write(decoded_data)
        except base64.binascii.Error as e:
            raise ValueError(f"Invalid base64 data: {str(e)}")
        except Exception as e:
            raise IOError(
                f"Error writing decoded data to {output_path}: {str(e)}"
            )


# For backward compatibility
FileHandler = FileHandler
