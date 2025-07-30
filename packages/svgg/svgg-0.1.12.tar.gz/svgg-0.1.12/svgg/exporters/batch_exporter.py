"""
Batch Exporter Module

This module provides functionality for batch processing of SVG files,
including exporting to multiple formats and applying operations in bulk.
"""

from pathlib import Path
from typing import List, Optional, Union, Any, Dict
from tqdm import tqdm
from xml.etree import ElementTree as ET

from ..core.svg_generator import SVGGenerator
from ..exceptions import SVGGError, ExportError
from .file_exporter import SVGExporter

class BatchProcessor:
    """A class to handle batch processing of SVG files.
    
    This class provides methods to:
    - Process multiple SVG files in batch
    - Apply transformations or exports to multiple files
    - Handle batch operations with progress tracking
    - Manage output directories and file naming
    """
    
    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """Initialize the BatchProcessor.
        
        Args:
            output_dir: Base directory for batch outputs (default: 'batch_output')
        """
        self.output_dir = Path(output_dir) if output_dir else Path('batch_output')
        self.exporter = SVGExporter(self.output_dir)
        self.svg_generator = SVGGenerator()
    
    def process_files(
        self,
        input_files: Union[str, List[Union[str, Path]]],
        output_format: str = 'svg',
        **export_kwargs: Any
    ) -> List[Path]:
        """Process multiple SVG files with the specified export format.
        
        Args:
            input_files: Single file path or list of file paths to process
            output_format: Output format (svg, png, pdf, etc.)
            **export_kwargs: Additional arguments to pass to the exporter
            
        Returns:
            List of Path objects to the exported files
            
        Raises:
            SVGGError: If processing fails
        """
        if isinstance(input_files, (str, Path)):
            input_files = [input_files]
            
        output_files: List[Path] = []
        
        for file_path in tqdm(input_files, desc="Processing files"):
            try:
                # Convert to Path if it's a string
                input_path = Path(str(file_path))
                if not input_path.exists():
                    raise FileNotFoundError(f"File not found: {input_path}")
                    
                output_filename = f"{input_path.stem}_export"
                
                # Read the file content
                with open(input_path, 'rb') as f:
                    file_content = f.read()
                
                # Process the file
                if output_format.lower() == 'svg':
                    # Try to parse as XML first
                    try:
                        etree = ET.fromstring(file_content)
                        output_path = self.exporter.export_svg(
                            etree,
                            output_filename,
                            **export_kwargs
                        )
                    except ET.ParseError:
                        # If not valid XML, pass as bytes
                        output_path = self.exporter.export_svg(
                            file_content,
                            output_filename,
                            **export_kwargs
                        )
                else:
                    raise ExportError(f"Unsupported output format: {output_format}")
                    
                output_files.append(Path(output_path))
                
            except Exception as e:
                raise SVGGError(f"Failed to process {file_path}: {str(e)}")
        
        return output_files
    
    def batch_export(
        self,
        input_dir: Union[str, Path],
        output_dir: Optional[Union[str, Path]] = None,
        file_pattern: str = "*.svg",
        output_format: str = 'svg',
        **export_kwargs
    ) -> List[Path]:
        """Batch export all matching files from a directory.
        
        Args:
            input_dir: Directory containing SVG files to process
            output_dir: Output directory (default: input_dir/exported)
            file_pattern: File pattern to match (e.g., '*.svg')
            output_format: Output format (svg, png, pdf, etc.)
            **export_kwargs: Additional arguments for the exporter
            
        Returns:
            List of Path objects to the exported files
        """
        input_dir = Path(input_dir)
        if not output_dir:
            output_dir = input_dir / 'exported'
        else:
            output_dir = Path(output_dir)
            
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all matching files
        input_files = list(input_dir.glob(file_pattern))
        if not input_files:
            raise SVGGError(f"No files matching pattern '{file_pattern}' found in {input_dir}")
            
        return self.process_files(input_files, output_format, **export_kwargs)
