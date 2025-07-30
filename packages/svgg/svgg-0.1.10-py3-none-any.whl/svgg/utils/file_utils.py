"""File handling utilities for the SVGG package.

This module provides a FileUtils class with static methods for common file operations
like reading, writing, and manipulating files and directories.
"""

import hashlib
import mimetypes
import shutil
from pathlib import Path
from typing import List, Union


class FileUtils:
    """Utility class for file operations.
    
    This class provides static methods for common file operations like reading,
    writing, and manipulating files and directories.
    """
    
    @staticmethod
    def read_file(file_path: Union[str, Path], binary: bool = False) -> Union[str, bytes]:
        """Read the contents of a file.

        Args:
            file_path: Path to the file to read.
            binary: If True, read file in binary mode.

        Returns:
            The file contents as a string (text mode) or bytes (binary mode).

        Raises:
            FileNotFoundError: If the file does not exist.
            IOError: If there's an error reading the file.
        """
        path = Path(file_path)
        mode = 'rb' if binary else 'r'

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        try:
            with open(path, mode) as f:
                return f.read()
        except Exception as e:
            raise IOError(f"Error reading file {path}: {str(e)}")
    
    @staticmethod
    def write_file(
        file_path: Union[str, Path],
        content: Union[str, bytes],
        binary: bool = False,
        overwrite: bool = False
    ) -> None:
        """Write content to a file.
        
        Args:
            file_path: Path to the file to write.
            content: Content to write to the file.
            binary: If True, write in binary mode.
            overwrite: If True, overwrite existing file.
            
        Raises:
            FileExistsError: If file exists and overwrite is False.
            IOError: If there's an error writing the file.
        """
        path = Path(file_path)
        mode = 'wb' if binary else 'w'
        
        if path.exists() and not overwrite:
            raise FileExistsError(f"File already exists: {path}")
            
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, mode) as f:
                f.write(content)
        except Exception as e:
            raise IOError(f"Error writing to file {path}: {str(e)}")
    
    @staticmethod
    def get_file_hash(file_path: Union[str, Path], algorithm: str = 'sha256') -> str:
        """Calculate the hash of a file.
        
        Args:
            file_path: Path to the file.
            algorithm: Hash algorithm to use (default: 'sha256').
            
        Returns:
            The hexadecimal digest of the file's hash.
            
        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If the algorithm is not available.
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        if algorithm not in hashlib.algorithms_available:
            raise ValueError(f"Unsupported hash algorithm: {algorithm}")
            
        hash_obj = hashlib.new(algorithm)
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hash_obj.update(chunk)
                
        return hash_obj.hexdigest()
    
    @staticmethod
    def get_mime_type(file_path: Union[str, Path]) -> str:
        """Get the MIME type of a file.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            The MIME type as a string (e.g., 'text/plain', 'image/png').
            Returns 'application/octet-stream' if type cannot be determined.
        """
        path = Path(file_path)
        mime_type, _ = mimetypes.guess_type(path)
        return mime_type or 'application/octet-stream'
    
    @staticmethod
    def ensure_directory(directory: Union[str, Path]) -> Path:
        """Ensure that a directory exists, creating it if necessary.
        
        Args:
            directory: Path to the directory.
            
        Returns:
            Path object of the directory.
        """
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    @staticmethod
    def list_files(
        directory: Union[str, Path],
        pattern: str = '*',
        recursive: bool = False
    ) -> List[Path]:
        """List files in a directory matching a pattern.
        
        Args:
            directory: Directory to search in.
            pattern: File pattern to match (e.g., '*.txt').
            recursive: If True, search recursively in subdirectories.
            
        Returns:
            List of Path objects for matching files.
        """
        path = Path(directory)
        if recursive:
            return list(path.rglob(pattern))
        return list(path.glob(pattern))
    
    @staticmethod
    def copy_file(
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False
    ) -> Path:
        """Copy a file to a new location.
        
        Args:
            source: Path to the source file.
            destination: Path to the destination file or directory.
            overwrite: If True, overwrite existing destination.
            
        Returns:
            Path to the copied file.
            
        Raises:
            FileNotFoundError: If source file does not exist.
            FileExistsError: If destination exists and overwrite is False.
        """
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
            
        if dst.is_dir():
            dst = dst / src.name
            
        if dst.exists() and not overwrite:
            raise FileExistsError(f"Destination file exists: {dst}")
            
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        return dst
    
    @staticmethod
    def move_file(
        source: Union[str, Path],
        destination: Union[str, Path],
        overwrite: bool = False
    ) -> Path:
        """Move a file to a new location.
        
        Args:
            source: Path to the source file.
            destination: Path to the destination file or directory.
            overwrite: If True, overwrite existing destination.
            
        Returns:
            Path to the moved file.
            
        Raises:
            FileNotFoundError: If source file does not exist.
            FileExistsError: If destination exists and overwrite is False.
        """
        src = Path(source)
        dst = Path(destination)
        
        if not src.exists():
            raise FileNotFoundError(f"Source file not found: {src}")
            
        if dst.is_dir():
            dst = dst / src.name
            
        if dst.exists():
            if not overwrite:
                raise FileExistsError(f"Destination file exists: {dst}")
            dst.unlink()
            
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src), str(dst))
        return dst
    
    @staticmethod
    def delete_file(file_path: Union[str, Path], missing_ok: bool = True) -> None:
        """Delete a file.
        
        Args:
            file_path: Path to the file to delete.
            missing_ok: If True, no error is raised if the file doesn't exist.
            
        Raises:
            FileNotFoundError: If file doesn't exist and missing_ok is False.
        """
        path = Path(file_path)
        if path.exists():
            path.unlink()
        elif not missing_ok:
            raise FileNotFoundError(f"File not found: {path}")
    
    @staticmethod
    def get_file_size(file_path: Union[str, Path]) -> int:
        """Get the size of a file in bytes.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            Size of the file in bytes.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.stat().st_size
    
    @staticmethod
    def is_binary_file(file_path: Union[str, Path]) -> bool:
        """Check if a file is binary.
        
        This is a simple check that looks for null bytes in the first 1024 bytes.
        
        Args:
            file_path: Path to the file.
            
        Returns:
            True if the file appears to be binary, False otherwise.
            
        Raises:
            FileNotFoundError: If the file does not exist.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        try:
            with open(path, 'rb') as f:
                chunk = f.read(1024)
                return b'\0' in chunk or not chunk.isascii()
        except Exception:
            return True
