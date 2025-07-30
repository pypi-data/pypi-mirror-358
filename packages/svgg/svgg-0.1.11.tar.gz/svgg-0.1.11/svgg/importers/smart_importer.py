"""
Smart Importer Module

This module provides intelligent file importing with filtering capabilities.
It can automatically detect file types, apply filters, and handle different
import strategies based on file content or metadata.
"""

import os
import mimetypes
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Callable, Set, Type, Tuple
from dataclasses import dataclass, field
import hashlib

# Import other importer classes that might be used
from .file_importer import SVGImporter
from .multi_importer import MultiImporter
from .project_importer import ProjectImporter
from .repository_importer import RepositoryImporter
from .zip_importer import ZipImporter

# Type aliases
FileFilter = Callable[[Dict[str, Any]], bool]
FileProcessor = Callable[[Union[str, Path]], Dict[str, Any]]

@dataclass
class ImportResult:
    """Result of an import operation."""
    success: bool
    files_processed: int = 0
    files_skipped: int = 0
    errors: List[Dict[str, Any]] = field(default_factory=list)
    imported_files: List[Dict[str, Any]] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

class SmartImporter:
    """
    A smart importer that can handle various file types with filtering.
    
    This class provides intelligent importing capabilities with features like:
    - Automatic file type detection
    - Content-based filtering
    - Metadata extraction
    - Batch processing
    - Progress tracking
    - Error handling and reporting
    """
    
    def __init__(self):
        """Initialize the SmartImporter with default settings."""
        self.file_processors: Dict[str, FileProcessor] = {}
        self.filters: List[FileFilter] = []
        self.importers = {
            'svg': SVGImporter(),
            'multi': MultiImporter(),
            'project': ProjectImporter(),
            'repository': RepositoryImporter(),
            'zip': ZipImporter(),
        }
        self._setup_default_processors()
    
    def _setup_default_processors(self) -> None:
        """Set up default file processors for common file types."""
        # Register default processors for common file types
        self.register_processor('image/svg+xml', self._process_svg)
        self.register_processor('application/zip', self._process_zip)
        self.register_processor('application/x-tar', self._process_archive)
        self.register_processor('application/x-gzip', self._process_archive)
        self.register_processor('application/x-bzip2', self._process_archive)
        self.register_processor('application/x-xz', self._process_archive)
        self.register_processor('text/plain', self._process_text)
        self.register_processor('application/json', self._process_json)
    
    def register_processor(self, mime_type: str, processor: FileProcessor) -> None:
        """Register a processor for a specific MIME type.
        
        Args:
            mime_type: The MIME type to register the processor for
            processor: A callable that processes files of this type
        """
        self.file_processors[mime_type] = processor
    
    def add_filter(self, filter_func: FileFilter) -> None:
        """Add a filter function to apply during import.
        
        Args:
            filter_func: A callable that takes file metadata and returns True to include the file
        """
        self.filters.append(filter_func)
    
    def clear_filters(self) -> None:
        """Remove all filters."""
        self.filters.clear()
    
    def import_file(self, file_path: Union[str, Path], **kwargs) -> ImportResult:
        """Import a single file with smart processing.
        
        Args:
            file_path: Path to the file to import
            **kwargs: Additional arguments for the processor
            
        Returns:
            ImportResult containing information about the import operation
        """
        file_path = Path(file_path)
        if not file_path.exists():
            return ImportResult(
                success=False,
                errors=[{'file': str(file_path), 'error': 'File does not exist'}]
            )
        
        # Get file metadata
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type is None:
            mime_type = 'application/octet-stream'
        
        file_info = {
            'path': str(file_path),
            'name': file_path.name,
            'size': file_path.stat().st_size,
            'mime_type': mime_type,
            'extension': file_path.suffix.lower(),
            'modified': file_path.stat().st_mtime,
            'metadata': {}
        }
        
        # Apply filters
        if not self._passes_filters(file_info):
            return ImportResult(
                success=True,
                files_skipped=1,
                metadata={'skipped': [file_info]}
            )
        
        # Process the file
        try:
            processor = self._get_processor(mime_type)
            result = processor(file_path, **kwargs)
            
            if isinstance(result, dict):
                file_info['metadata'].update(result)
            
            return ImportResult(
                success=True,
                files_processed=1,
                imported_files=[file_info],
                metadata=file_info['metadata']
            )
            
        except Exception as e:
            return ImportResult(
                success=False,
                errors=[{'file': str(file_path), 'error': str(e)}]
            )
    
    def import_directory(self, 
                       dir_path: Union[str, Path], 
                       recursive: bool = True, 
                       **kwargs) -> ImportResult:
        """Import all files in a directory.
        
        Args:
            dir_path: Path to the directory to import
            recursive: Whether to include subdirectories
            **kwargs: Additional arguments for the processor
            
        Returns:
            ImportResult containing information about the import operation
        """
        dir_path = Path(dir_path)
        if not dir_path.is_dir():
            return ImportResult(
                success=False,
                errors=[{'path': str(dir_path), 'error': 'Not a directory'}]
            )
        
        result = ImportResult()
        
        # Walk the directory
        for entry in dir_path.rglob('*') if recursive else dir_path.glob('*'):
            if entry.is_file():
                file_result = self.import_file(entry, **kwargs)
                self._merge_results(result, file_result)
        
        result.success = len(result.errors) == 0
        return result
    
    def _get_processor(self, mime_type: str) -> FileProcessor:
        """Get the appropriate processor for a MIME type.
        
        Args:
            mime_type: The MIME type to get a processor for
            
        Returns:
            A callable processor function
            
        Raises:
            ValueError: If no processor is found for the MIME type
        """
        # Try exact match first
        if mime_type in self.file_processors:
            return self.file_processors[mime_type]
        
        # Try type/* pattern
        main_type = mime_type.split('/')[0] + '/*'
        if main_type in self.file_processors:
            return self.file_processors[main_type]
        
        # Try to find a compatible importer
        for importer in self.importers.values():
            if hasattr(importer, 'can_import') and importer.can_import(mime_type):
                return importer.import_file
        
        # Default to binary processor
        return self._process_binary
    
    def _passes_filters(self, file_info: Dict[str, Any]) -> bool:
        """Check if a file passes all registered filters.
        
        Args:
            file_info: Dictionary containing file metadata
            
        Returns:
            bool: True if all filters pass, False otherwise
        """
        if not self.filters:
            return True
            
        return all(filter_func(file_info) for filter_func in self.filters)
    
    def _merge_results(self, result: ImportResult, other: ImportResult) -> None:
        """Merge another ImportResult into this one.
        
        Args:
            result: The result to merge into
            other: The result to merge from
        """
        result.files_processed += other.files_processed
        result.files_skipped += other.files_skipped
        result.errors.extend(other.errors)
        result.imported_files.extend(other.imported_files)
        result.metadata.update(other.metadata)
    
    # Default processor implementations
    def _process_svg(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process an SVG file."""
        return self.importers['svg'].import_file(str(file_path), **kwargs)
    
    def _process_zip(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process a ZIP archive."""
        return self.importers['zip'].import_file(str(file_path), **kwargs)
    
    def _process_archive(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process a generic archive file."""
        # Default implementation just returns basic info
        return {'type': 'archive', 'path': str(file_path)}
    
    def _process_text(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process a text file."""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return {'type': 'text', 'content': content, 'length': len(content)}
    
    def _process_json(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process a JSON file."""
        import json
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return {'type': 'json', 'data': data}
    
    def _process_binary(self, file_path: Union[str, Path], **kwargs) -> Dict[str, Any]:
        """Process a binary file."""
        # For binary files, just return basic info and a hash
        with open(file_path, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()
        return {
            'type': 'binary',
            'size': os.path.getsize(file_path),
            'md5': file_hash
        }
