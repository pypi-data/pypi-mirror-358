"""
Multi-Format Importer Module

This module provides functionality to import and process multiple files
of different formats, including PDFs, images, and other document types.
"""

import os
import mimetypes
from typing import Dict, List, Optional, Any, Union, Tuple
from pathlib import Path

class MultiImporter:
    """
    A class to handle importing multiple files of different formats.
    
    This class provides methods to discover, validate, and process
    multiple files of various formats for embedding into SVGs.
    """
    
    # Supported file extensions and their MIME types
    SUPPORTED_FORMATS = {
        # Document formats
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        '.odt': 'application/vnd.oasis.opendocument.text',
        
        # Image formats
        '.png': 'image/png',
        '.jpg': 'image/jpeg',
        '.jpeg': 'image/jpeg',
        '.gif': 'image/gif',
        '.svg': 'image/svg+xml',
        '.webp': 'image/webp',
        
        # Data formats
        '.json': 'application/json',
        '.csv': 'text/csv',
        '.txt': 'text/plain',
        
        # Archive formats
        '.zip': 'application/zip',
        '.tar': 'application/x-tar',
        '.gz': 'application/gzip',
        '.7z': 'application/x-7z-compressed',
    }
    
    def __init__(self):
        """Initialize the MultiImporter with default settings."""
        self.supported_extensions = list(self.SUPPORTED_FORMATS.keys())
    
    def is_supported_file(self, file_path: Union[str, Path]) -> bool:
        """Check if a file is supported based on its extension.
        
        Args:
            file_path: Path to the file to check
            
        Returns:
            bool: True if the file format is supported, False otherwise
        """
        file_path = str(file_path)
        ext = os.path.splitext(file_path)[1].lower()
        return ext in self.supported_extensions
    
    def get_file_info(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """Get information about a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary containing file information including:
            - path: Full path to the file
            - name: File name with extension
            - extension: File extension (lowercase)
            - mime_type: Detected MIME type
            - size: File size in bytes
            - supported: Whether the file format is supported
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        ext = file_path.suffix.lower()
        mime_type = self.SUPPORTED_FORMATS.get(ext, mimetypes.guess_type(file_path)[0])
        
        return {
            'path': str(file_path.absolute()),
            'name': file_path.name,
            'extension': ext,
            'mime_type': mime_type or 'application/octet-stream',
            'size': file_path.stat().st_size,
            'supported': ext in self.supported_extensions
        }
    
    def discover_files(self, path: Union[str, Path], recursive: bool = False) -> List[Dict[str, Any]]:
        """Discover files in a directory.
        
        Args:
            path: Directory path or file path
            recursive: Whether to search recursively in subdirectories
            
        Returns:
            List of dictionaries containing information about discovered files
        """
        path = Path(path)
        files = []
        
        if path.is_file():
            return [self.get_file_info(path)]
            
        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {path}")
            
        glob_pattern = '**/*' if recursive else '*'
        
        for file_path in path.glob(glob_pattern):
            if file_path.is_file():
                try:
                    files.append(self.get_file_info(file_path))
                except (PermissionError, OSError) as e:
                    # Skip files that can't be accessed
                    continue
                    
        return files
    
    def filter_files(self, files: List[Dict[str, Any]], 
                     supported_only: bool = True, 
                     min_size: int = 0,
                     max_size: Optional[int] = None) -> List[Dict[str, Any]]:
        """Filter a list of files based on criteria.
        
        Args:
            files: List of file information dictionaries
            supported_only: Whether to include only supported file formats
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes (None for no limit)
            
        Returns:
            Filtered list of file information dictionaries
        """
        filtered = []
        
        for file_info in files:
            if supported_only and not file_info.get('supported', False):
                continue
                
            if file_info.get('size', 0) < min_size:
                continue
                
            if max_size is not None and file_info.get('size', 0) > max_size:
                continue
                
            filtered.append(file_info)
            
        return filtered
    
    def group_files_by_type(self, files: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group files by their MIME type.
        
        Args:
            files: List of file information dictionaries
            
        Returns:
            Dictionary mapping MIME types to lists of file information
        """
        groups = {}
        
        for file_info in files:
            mime_type = file_info.get('mime_type', 'application/octet-stream')
            if mime_type not in groups:
                groups[mime_type] = []
            groups[mime_type].append(file_info)
            
        return groups
