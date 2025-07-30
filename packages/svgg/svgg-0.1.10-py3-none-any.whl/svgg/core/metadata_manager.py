"""
Metadata Manager Module

This module provides functionality to manage metadata for SVG files,
including storing, retrieving, and manipulating embedded file metadata.
"""

import json
from typing import Any, Dict, Optional

class MetadataManager:
    """
    A class to manage metadata for SVG files with embedded content.
    
    This class handles the storage and retrieval of metadata related to
    files embedded within SVG documents.
    """
    
    def __init__(self, metadata: Optional[Dict[str, Any]] = None):
        """
        Initialize the MetadataManager with optional initial metadata.
        
        Args:
            metadata: Optional initial metadata dictionary
        """
        self.metadata = metadata or {}
        self.metadata.setdefault('embedded_files', [])
    
    def add_file_metadata(
        self,
        file_path: str,
        mime_type: str,
        size: int,
        data_uri: Optional[str] = None
    ) -> None:
        """
        Add metadata for an embedded file.
        
        Args:
            file_path: Path to the original file
            mime_type: MIME type of the file
            size: Size of the file in bytes
            data_uri: Optional data URI if the file is embedded
        """
        file_metadata = {
            'path': file_path,
            'mime_type': mime_type,
            'size': size
        }
        if data_uri:
            # Store a preview of the data URI
            file_metadata['data_uri'] = data_uri[:100] + '...'
            
        self.metadata['embedded_files'].append(file_metadata)
    
    def get_file_metadata(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific embedded file.
        
        Args:
            file_path: Path to the file to get metadata for
            
        Returns:
            Dictionary with file metadata, or None if not found
        """
        for file_meta in self.metadata.get('embedded_files', []):
            if file_meta.get('path') == file_path:
                return file_meta
        return None
    
    def get_all_metadata(self) -> Dict[str, Any]:
        """
        Get all metadata.
        
        Returns:
            Dictionary containing all metadata
        """
        return self.metadata
    
    def to_json(self, indent: Optional[int] = 2) -> str:
        """
        Convert metadata to JSON string.
        
        Args:
            indent: Number of spaces to indent the JSON output
            
        Returns:
            JSON string representation of the metadata
        """
        return json.dumps(self.metadata, indent=indent)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MetadataManager':
        """
        Create a MetadataManager instance from a JSON string.
        
        Args:
            json_str: JSON string containing metadata
            
        Returns:
            New MetadataManager instance with the parsed metadata
        """
        try:
            metadata = json.loads(json_str)
            return cls(metadata)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}") from e
    
    def clear(self) -> None:
        """Clear all metadata."""
        self.metadata = {'embedded_files': []}


# For backward compatibility
MetadataManager = MetadataManager
