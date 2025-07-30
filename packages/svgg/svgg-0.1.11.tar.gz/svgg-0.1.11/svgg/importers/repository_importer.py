"""
Git Repository Importer Module

This module provides functionality to import files from Git repositories,
supporting both local and remote repositories, with options to filter by
file type, size, and commit history.
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Union, Any
from datetime import datetime

class RepositoryImporter:
    """
    A class to handle importing files from Git repositories.
    
    This class provides methods to:
    - Clone remote repositories
    - Import files from local repositories
    - Filter files by type, size, or commit history
    - Handle repository metadata and history
    - Export repository contents
    """
    
    def __init__(self, repo_url: Optional[str] = None, local_path: Optional[Union[str, Path]] = None):
        """Initialize the RepositoryImporter with a repository URL or local path.
        
        Args:
            repo_url: URL of the remote Git repository (e.g., 'https://github.com/user/repo.git')
            local_path: Local path to a Git repository or where to clone the remote repository
        """
        self.repo_url = repo_url
        self.local_path = Path(local_path) if local_path else None
        self.temp_dir = None
        self.repo = None
        
        # If only URL is provided, clone to a temporary directory
        if repo_url and not local_path:
            self.temp_dir = tempfile.mkdtemp(prefix='svgg_repo_')
            self.local_path = Path(self.temp_dir) / Path(repo_url).stem
    
    def clone_repository(self) -> bool:
        """Clone the remote repository to the local path.
        
        Returns:
            bool: True if cloning was successful, False otherwise
            
        Raises:
            ImportError: If GitPython is not installed
            ValueError: If no repository URL is provided
        """
        if not self.repo_url:
            raise ValueError("No repository URL provided")
            
        try:
            from git import Repo
        except ImportError:
            raise ImportError(
                "GitPython is required for repository operations. "
                "Install it with: pip install gitpython"
            )
            
        try:
            self.repo = Repo.clone_from(self.repo_url, self.local_path)
            return True
        except Exception as e:
            print(f"Error cloning repository: {e}")
            return False
    
    def load_local_repository(self) -> bool:
        """Load an existing local Git repository.
        
        Returns:
            bool: True if the repository was loaded successfully, False otherwise
            
        Raises:
            ImportError: If GitPython is not installed
            ValueError: If no local path is provided
        """
        if not self.local_path:
            raise ValueError("No local repository path provided")
            
        try:
            from git import Repo, InvalidGitRepositoryError
        except ImportError:
            raise ImportError(
                "GitPython is required for repository operations. "
                "Install it with: pip install gitpython"
            )
            
        try:
            self.repo = Repo(self.local_path)
            return True
        except InvalidGitRepositoryError:
            print(f"Not a valid Git repository: {self.local_path}")
            return False
    
    def get_file_history(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """Get the commit history for a specific file.
        
        Args:
            file_path: Path to the file relative to the repository root
            
        Returns:
            List of dictionaries containing commit information
            
        Raises:
            RuntimeError: If no repository is loaded
        """
        if not self.repo:
            raise RuntimeError("No repository loaded. Call clone_repository() or load_local_repository() first.")
            
        history = []
        try:
            for commit in self.repo.iter_commits(paths=str(file_path)):
                history.append({
                    'hexsha': commit.hexsha,
                    'author': str(commit.author),
                    'authored_date': datetime.fromtimestamp(commit.authored_date).isoformat(),
                    'message': commit.message.strip(),
                    'committed_date': datetime.fromtimestamp(commit.committed_date).isoformat(),
                    'committer': str(commit.committer),
                })
        except Exception as e:
            print(f"Error getting file history: {e}")
            
        return history
    
    def list_files(self, ref: str = 'HEAD', recursive: bool = True) -> List[Dict[str, Any]]:
        """List all files in the repository at a specific reference.
        
        Args:
            ref: Git reference (branch, tag, or commit hash)
            recursive: Whether to list files recursively
            
        Returns:
            List of dictionaries containing file information
            
        Raises:
            RuntimeError: If no repository is loaded
        """
        if not self.repo:
            raise RuntimeError("No repository loaded. Call clone_repository() or load_local_repository() first.")
            
        files = []
        try:
            tree = self.repo.commit(ref).tree
            for item in tree.traverse():
                if item.type == 'blob':  # Regular file
                    files.append({
                        'path': item.path,
                        'name': os.path.basename(item.path),
                        'size': item.size,
                        'type': 'file',
                        'mode': item.mode,
                        'hexsha': item.hexsha
                    })
                elif item.type == 'tree' and not recursive:
                    files.append({
                        'path': item.path,
                        'name': os.path.basename(item.path),
                        'type': 'directory',
                        'mode': item.mode,
                        'hexsha': item.hexsha
                    })
        except Exception as e:
            print(f"Error listing repository files: {e}")
            
        return files
    
    def get_file_content(self, file_path: Union[str, Path], ref: str = 'HEAD') -> Optional[bytes]:
        """Get the content of a file at a specific reference.
        
        Args:
            file_path: Path to the file relative to the repository root
            ref: Git reference (branch, tag, or commit hash)
            
        Returns:
            File content as bytes, or None if the file doesn't exist
            
        Raises:
            RuntimeError: If no repository is loaded
        """
        if not self.repo:
            raise RuntimeError("No repository loaded. Call clone_repository() or load_local_repository() first.")
            
        try:
            commit = self.repo.commit(ref)
            blob = next((b for b in commit.tree.traverse() if b.path == str(file_path) and b.type == 'blob'), None)
            if blob:
                return blob.data_stream.read()
        except Exception as e:
            print(f"Error getting file content: {e}")
            
        return None
    
    def export_files(self, output_dir: Union[str, Path], 
                     file_patterns: Optional[List[str]] = None,
                     ref: str = 'HEAD') -> List[Path]:
        """Export files from the repository matching the given patterns.
        
        Args:
            output_dir: Directory to export files to
            file_patterns: List of file patterns to include (e.g., ['*.py', '*.md'])
            ref: Git reference (branch, tag, or commit hash)
            
        Returns:
            List of paths to exported files
            
        Raises:
            RuntimeError: If no repository is loaded
        """
        if not self.repo:
            raise RuntimeError("No repository loaded. Call clone_repository() or load_local_repository() first.")
            
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        exported = []
        
        try:
            files = self.list_files(ref=ref)
            for file_info in files:
                if file_info['type'] != 'file':
                    continue
                    
                # Check if file matches any of the patterns
                if file_patterns:
                    import fnmatch
                    if not any(fnmatch.fnmatch(file_info['path'], pattern) for pattern in file_patterns):
                        continue
                
                # Get file content and write to output directory
                content = self.get_file_content(file_info['path'], ref=ref)
                if content is not None:
                    dest_path = output_dir / file_info['path']
                    dest_path.parent.mkdir(parents=True, exist_ok=True)
                    with open(dest_path, 'wb') as f:
                        f.write(content)
                    exported.append(dest_path)
                    
        except Exception as e:
            print(f"Error exporting files: {e}")
            
        return exported
    
    def cleanup(self) -> None:
        """Clean up any temporary directories created by this importer."""
        if self.temp_dir and os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
            self.temp_dir = None
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - ensure resources are cleaned up."""
        self.cleanup()
    
    def __del__(self):
        """Destructor - ensure resources are cleaned up."""
        self.cleanup()
