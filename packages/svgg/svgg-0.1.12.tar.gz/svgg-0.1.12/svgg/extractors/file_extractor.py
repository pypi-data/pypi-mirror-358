"""
File Extractor Module

This module provides functionality to extract embedded files and content from SVG files.
"""

import base64
from pathlib import Path
from typing import Dict, List, Union
from xml.etree import ElementTree as ET

from ..exceptions import SVGGError

# For type hints only
try:
    from lxml.etree import _Element as Element  # type: ignore
    from lxml.etree import _ElementTree as ElementTree  # type: ignore
except ImportError:
    from xml.etree.ElementTree import Element, ElementTree  # type: ignore

class FileExtractor:
    """A class to handle extraction of embedded files and content from SVG files.
    
    This class provides methods to:
    - Extract embedded files from SVG metadata
    - Reconstruct file structures from embedded data
    - Handle different embedding methods (base64, gzip, etc.)
    """
    
    def __init__(self, svg_content: Union[str, bytes, ET.Element]) -> None:
        """Initialize the FileExtractor with SVG content.
        
        Args:
            svg_content: SVG content as string, bytes, or ElementTree Element
        """
        self.svg_content = svg_content
        self.root = self._parse_svg()
    
    def _parse_svg(self) -> ET.Element:
        """Parse the SVG content into an ElementTree Element.
        
        Returns:
            The root element of the SVG document
            
        Raises:
            SVGGError: If the SVG content cannot be parsed
        """
        try:
            if isinstance(self.svg_content, (str, bytes)):
                return ET.fromstring(self.svg_content)
            elif isinstance(self.svg_content, ET.Element):
                return self.svg_content
            else:
                raise SVGGError("Unsupported SVG content type. Expected str, bytes, or Element.")
        except ET.ParseError as e:
            raise SVGGError(f"Failed to parse SVG content: {str(e)}")
    
    def extract_embedded_files(self) -> Dict[str, bytes]:
        """Extract all embedded files from the SVG.
        
        Returns:
            Dictionary mapping filenames to their content as bytes
            
        Raises:
            SVGGError: If extraction fails
        """
        try:
            # Look for embedded files in metadata
            embedded_files = {}
            
            # Check for files embedded in custom metadata elements
            for elem in self.root.findall(".//*[@data-filename]"):
                if 'data-content' in elem.attrib:
                    filename = elem.get('data-filename', 'unnamed.bin')
                    content_b64 = elem.get('data-content', '')
                    try:
                        content = base64.b64decode(content_b64)
                        embedded_files[filename] = content
                    except Exception as e:
                        print(f"Warning: Failed to decode embedded file {filename}: {str(e)}")
            
            # Check for files embedded in comments (common pattern)
            for comment in self.root.xpath('//comment()'):
                text = comment.text.strip() if comment.text else ''
                if text.startswith('FILE:'):
                    try:
                        parts = text.split('\n', 1)
                        if len(parts) == 2:
                            filename = parts[0][5:].strip()
                            content = base64.b64decode(parts[1].strip())
                            embedded_files[filename] = content
                    except Exception as e:
                        print(f"Warning: Failed to extract file from comment: {str(e)}")
            
            return embedded_files
            
        except Exception as e:
            raise SVGGError(f"Failed to extract embedded files: {str(e)}")
    
    def extract_to_directory(self, output_dir: Union[str, Path], overwrite: bool = False) -> List[Path]:
        """Extract all embedded files to a directory.
        
        Args:
            output_dir: Directory to extract files to
            overwrite: Whether to overwrite existing files
            
        Returns:
            List of Path objects to the extracted files
            
        Raises:
            SVGGError: If extraction fails
            FileExistsError: If a file already exists and overwrite is False
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_files = []
        
        try:
            embedded_files = self.extract_embedded_files()
            
            for filename, content in embedded_files.items():
                output_path = output_dir / filename
                
                if output_path.exists() and not overwrite:
                    raise FileExistsError(f"File {output_path} already exists and overwrite is False")
                
                with open(output_path, 'wb') as f:
                    f.write(content)
                
                extracted_files.append(output_path)
            
            return extracted_files
            
        except Exception as e:
            # Clean up any partially extracted files
            for path in extracted_files:
                try:
                    path.unlink()
                except OSError:
                    # Ignore errors during cleanup
                    pass
            raise SVGGError(f"Failed to extract files to directory: {str(e)}")


