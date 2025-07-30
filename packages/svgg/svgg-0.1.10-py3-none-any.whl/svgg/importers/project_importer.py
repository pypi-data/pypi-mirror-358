"""
Project Importer Module

This module provides functionality to import and manage project structures,
including directory hierarchies and file collections, for embedding into SVGs.
"""

import os
import json
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Union, Any, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ProjectFile:
    """Represents a file in a project with metadata and content."""
    path: str
    name: str
    size: int
    mime_type: str
    last_modified: float
    is_binary: bool
    content: Optional[bytes] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def from_path(cls, file_path: Union[str, Path], load_content: bool = True) -> 'ProjectFile':
        """Create a ProjectFile from a file path.
        
        Args:
            file_path: Path to the file
            load_content: Whether to load file content into memory
            
        Returns:
            Initialized ProjectFile instance
        """
        file_path = Path(file_path)
        if not file_path.exists() or not file_path.is_file():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        stat = file_path.stat()
        content = None
        is_binary = True
        
        if load_content:
            try:
                with open(file_path, 'rb') as f:
                    content = f.read()
                # Try to decode as text to check if it's binary
                content.decode('utf-8')
                is_binary = False
            except UnicodeDecodeError:
                # File is binary
                pass
                
        return cls(
            path=str(file_path),
            name=file_path.name,
            size=stat.st_size,
            mime_type=cls._guess_mime_type(file_path),
            last_modified=stat.st_mtime,
            is_binary=is_binary,
            content=content
        )
    
    @staticmethod
    def _guess_mime_type(file_path: Path) -> str:
        """Guess the MIME type of a file based on its extension."""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

class ProjectImporter:
    """
    A class to handle importing and managing project structures.
    
    This class provides methods to:
    - Import entire directory structures
    - Filter files by type, size, or other criteria
    - Maintain directory hierarchies
    - Generate project manifests
    - Export project structures
    """
    
    def __init__(self, root_path: Optional[Union[str, Path]] = None):
        """Initialize the ProjectImporter with an optional root path.
        
        Args:
            root_path: Optional root directory of the project
        """
        self.root_path = Path(root_path).resolve() if root_path else None
        self.files: Dict[str, ProjectFile] = {}
        self.ignored_patterns: Set[str] = {
            '__pycache__', '.git', '.svn', '.hg', '.DS_Store',
            '*.pyc', '*.pyo', '*.pyd', '*.so', '*.dll', '*.exe',
            '*.egg-info', 'dist', 'build', '*.egg', '*.whl',
            'node_modules', 'venv', 'env', '.env', '.venv',
            '*.log', '*.tmp', '*.bak', '*.swp', '*.swo', '*.swn'
        }
    
    def add_ignored_pattern(self, pattern: str) -> None:
        """Add a pattern to the ignore list.
        
        Args:
            pattern: Glob-style pattern to ignore (e.g., '*.tmp', '__pycache__')
        """
        self.ignored_patterns.add(pattern)
    
    def is_ignored(self, path: Union[str, Path]) -> bool:
        """Check if a path should be ignored based on ignore patterns.
        
        Args:
            path: Path to check
            
        Returns:
            True if the path should be ignored, False otherwise
        """
        path = Path(path)
        
        # Check if any part of the path matches an ignore pattern
        for part in path.parts:
            for pattern in self.ignored_patterns:
                if part == pattern or part.startswith(pattern.rstrip('*')):
                    return True
                
                # Handle glob patterns
                if pattern.startswith('*'):
                    if part.endswith(pattern[1:]) or part == pattern[1:]:
                        return True
                        
        return False
    
    def scan_directory(self, directory: Optional[Union[str, Path]] = None, 
                      recursive: bool = True) -> List[ProjectFile]:
        """Scan a directory and collect file information.
        
        Args:
            directory: Directory to scan (defaults to root_path)
            recursive: Whether to scan subdirectories
            
        Returns:
            List of ProjectFile objects
        """
        if directory is None:
            if self.root_path is None:
                raise ValueError("No directory specified and no root_path set")
            directory = self.root_path
            
        directory = Path(directory).resolve()
        if not directory.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")
            
        files = []
        pattern = '**/*' if recursive else '*'
        
        for file_path in directory.glob(pattern):
            if file_path.is_file() and not self.is_ignored(file_path):
                try:
                    project_file = ProjectFile.from_path(file_path)
                    # Store relative path as key
                    rel_path = str(file_path.relative_to(directory))
                    self.files[rel_path] = project_file
                    files.append(project_file)
                except (PermissionError, OSError) as e:
                    # Skip files that can't be accessed
                    continue
                    
        return files
    
    def import_project(self, project_path: Union[str, Path], 
                       recursive: bool = True) -> Dict[str, ProjectFile]:
        """Import a project from a directory.
        
        Args:
            project_path: Path to the project directory
            recursive: Whether to import files recursively
            
        Returns:
            Dictionary mapping relative paths to ProjectFile objects
        """
        self.root_path = Path(project_path).resolve()
        self.scan_directory(recursive=recursive)
        return self.files
    
    def export_manifest(self, output_file: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
        """Generate a manifest of the project files.
        
        Args:
            output_file: Optional path to save the manifest as JSON
            
        Returns:
            Dictionary containing the project manifest
        """
        manifest = {
            'root_path': str(self.root_path) if self.root_path else None,
            'file_count': len(self.files),
            'total_size': sum(f.size for f in self.files.values()),
            'files': {}
        }
        
        for rel_path, file_info in self.files.items():
            manifest['files'][rel_path] = {
                'name': file_info.name,
                'size': file_info.size,
                'mime_type': file_info.mime_type,
                'last_modified': datetime.fromtimestamp(file_info.last_modified).isoformat(),
                'is_binary': file_info.is_binary,
                'metadata': file_info.metadata
            }
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(manifest, f, indent=2, ensure_ascii=False)
                
        return manifest
    
    def filter_files(self, **criteria) -> List[ProjectFile]:
        """Filter files based on criteria.
        
        Args:
            **criteria: Keyword arguments for filtering. Supported criteria:
                - min_size: Minimum file size in bytes
                - max_size: Maximum file size in bytes
                - mime_type: MIME type or list of MIME types to include
                - extension: File extension or list of extensions to include
                - exclude_binary: If True, exclude binary files
                - exclude_text: If True, exclude text files
                
        Returns:
            List of filtered ProjectFile objects
        """
        filtered = []
        
        for file_info in self.files.values():
            include = True
            
            if 'min_size' in criteria and file_info.size < criteria['min_size']:
                include = False
            elif 'max_size' in criteria and file_info.size > criteria['max_size']:
                include = False
            elif 'mime_type' in criteria:
                mime_types = [criteria['mime_type']] if isinstance(criteria['mime_type'], str) else criteria['mime_type']
                if file_info.mime_type not in mime_types:
                    include = False
            elif 'extension' in criteria:
                extensions = [criteria['extension']] if isinstance(criteria['extension'], str) else criteria['extension']
                if not any(file_info.name.lower().endswith(ext.lower().lstrip('*')) for ext in extensions):
                    include = False
            
            if 'exclude_binary' in criteria and criteria['exclude_binary'] and file_info.is_binary:
                include = False
            elif 'exclude_text' in criteria and criteria['exclude_text'] and not file_info.is_binary:
                include = False
                
            if include:
                filtered.append(file_info)
                
        return filtered
    
    def export_files(self, output_dir: Union[str, Path], files: Optional[List[ProjectFile]] = None) -> List[Path]:
        """Export files to a directory.
        
        Args:
            output_dir: Directory to export files to
            files: List of ProjectFile objects to export (defaults to all files)
            
        Returns:
            List of paths to exported files
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        files_to_export = files if files is not None else list(self.files.values())
        exported = []
        
        for file_info in files_to_export:
            rel_path = file_info.path
            if self.root_path:
                try:
                    rel_path = str(Path(file_info.path).relative_to(self.root_path))
                except ValueError:
                    # File is outside the root directory, use its name
                    rel_path = file_info.name
            
            dest_path = output_dir / rel_path
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if file_info.content is not None:
                mode = 'wb' if file_info.is_binary else 'w'
                with open(dest_path, mode) as f:
                    f.write(file_info.content)
            else:
                shutil.copy2(file_info.path, dest_path)
                
            exported.append(dest_path)
            
        return exported
