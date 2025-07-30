"""
ZIP Archive Importer Module

This module provides functionality to import and extract files from ZIP archives,
including nested archives, with support for various compression methods.
"""

import os
import zipfile
import io
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, BinaryIO, Any, Tuple, Iterator
from typing_extensions import TypedDict

class FileInfo(TypedDict):
    """Type definition for file information dictionary."""
    filename: str
    file_size: int
    compress_size: int
    is_dir: bool
    is_encrypted: bool
    create_system: int
    extract_version: int
    create_version: int
    flag_bits: int
    compress_type: int
    reserved: int
    volume: int
    internal_attr: int
    external_attr: int
    header_offset: int
    CRC: int
    comment: bytes

class ZipImporter:
    """
    A class to handle importing files from ZIP archives.
    
    This class provides methods to:
    - List contents of ZIP archives
    - Extract specific files or all files
    - Handle nested ZIP archives
    - Validate ZIP file integrity
    - Get detailed information about archive contents
    """
    
    def __init__(self, zip_path: Union[str, os.PathLike]):
        """Initialize the ZipImporter with a path to a ZIP file.
        
        Args:
            zip_path: Path to the ZIP file to work with
            
        Raises:
            FileNotFoundError: If the ZIP file doesn't exist
            zipfile.BadZipFile: If the file is not a valid ZIP archive
        """
        self.zip_path = Path(zip_path)
        if not self.zip_path.exists():
            raise FileNotFoundError(f"ZIP file not found: {zip_path}")
            
        self._zip_ref = None
        self._file_list = []
        self._open_zip()
    
    def _open_zip(self) -> None:
        """Open the ZIP file and read its contents."""
        try:
            self._zip_ref = zipfile.ZipFile(self.zip_path, 'r')
            self._file_list = self._zip_ref.filelist
        except zipfile.BadZipFile as e:
            raise zipfile.BadZipFile(f"Invalid or corrupted ZIP file: {self.zip_path}") from e
    
    def list_files(self) -> List[str]:
        """List all files in the ZIP archive.
        
        Returns:
            List of filenames in the archive
        """
        return [f.filename for f in self._file_list]
    
    def get_file_info(self, filename: str) -> Optional[FileInfo]:
        """Get detailed information about a file in the archive.
        
        Args:
            filename: Name of the file in the archive
            
        Returns:
            Dictionary with file information, or None if file not found
        """
        try:
            info = self._zip_ref.getinfo(filename)
            return {
                'filename': info.filename,
                'file_size': info.file_size,
                'compress_size': info.compress_size,
                'is_dir': info.is_dir(),
                'is_encrypted': info.flag_bits & 0x1 == 1,
                'create_system': info.create_system,
                'extract_version': info.extract_version,
                'create_version': info.create_version,
                'flag_bits': info.flag_bits,
                'compress_type': info.compress_type,
                'reserved': info.reserved,
                'volume': info.volume,
                'internal_attr': info.internal_attr,
                'external_attr': info.external_attr,
                'header_offset': info.header_offset,
                'CRC': info.CRC,
                'comment': info.comment
            }
        except KeyError:
            return None
    
    def extract_file(self, filename: str, output_path: Union[str, os.PathLike] = None) -> str:
        """Extract a single file from the archive.
        
        Args:
            filename: Name of the file to extract
            output_path: Directory to extract to (defaults to current directory)
            
        Returns:
            Path to the extracted file
            
        Raises:
            KeyError: If the file is not found in the archive
            RuntimeError: If there's an error during extraction
        """
        if output_path is None:
            output_path = Path.cwd()
        else:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            return self._zip_ref.extract(filename, path=output_path)
        except Exception as e:
            raise RuntimeError(f"Error extracting {filename}: {str(e)}")
    
    def extract_all(self, output_path: Union[str, os.PathLike] = None) -> List[str]:
        """Extract all files from the archive.
        
        Args:
            output_path: Directory to extract to (defaults to current directory)
            
        Returns:
            List of paths to extracted files
            
        Raises:
            RuntimeError: If there's an error during extraction
        """
        if output_path is None:
            output_path = Path.cwd()
        else:
            output_path = Path(output_path)
            output_path.mkdir(parents=True, exist_ok=True)
        
        try:
            extracted = self._zip_ref.extractall(path=output_path)
            return [str(Path(output_path) / f.filename) for f in self._file_list if not f.is_dir()]
        except Exception as e:
            raise RuntimeError(f"Error extracting files: {str(e)}")
    
    def read_file(self, filename: str) -> bytes:
        """Read the contents of a file in the archive without extracting it.
        
        Args:
            filename: Name of the file to read
            
        Returns:
            File contents as bytes
            
        Raises:
            KeyError: If the file is not found in the archive
            RuntimeError: If there's an error reading the file
        """
        try:
            with self._zip_ref.open(filename, 'r') as f:
                return f.read()
        except Exception as e:
            raise RuntimeError(f"Error reading {filename}: {str(e)}")
    
    def is_encrypted(self, filename: str) -> bool:
        """Check if a file in the archive is encrypted.
        
        Args:
            filename: Name of the file to check
            
        Returns:
            True if the file is encrypted, False otherwise
        """
        try:
            info = self._zip_ref.getinfo(filename)
            return info.flag_bits & 0x1 == 1
        except KeyError:
            return False
    
    def close(self) -> None:
        """Close the ZIP file and release resources."""
        if self._zip_ref:
            self._zip_ref.close()
            self._zip_ref = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure the ZIP file is closed."""
        self.close()
    
    def __del__(self):
        """Destructor - ensure the ZIP file is closed."""
        self.close()
