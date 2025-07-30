"""
SVG Importer Module

This module provides functionality to import and process SVG files,
including parsing, validation, and extraction of SVG content.
"""

import os
import re
from typing import Optional, Dict, Any, List, Union
from lxml import etree

class SVGImporter:
    """
    A class to handle importing and processing SVG files.
    
    This class provides methods to load SVG files, validate their structure,
    and extract relevant information or transform them as needed.
    """
    
    def __init__(self):
        """Initialize the SVGImporter with default settings."""
        self.namespaces = {
            'svg': 'http://www.w3.org/2000/svg',
            'xlink': 'http://www.w3.org/1999/xlink'
        }
    
    def load_svg(self, file_path: str) -> Optional[etree._ElementTree]:
        """Load and parse an SVG file.
        
        Args:
            file_path: Path to the SVG file to load
            
        Returns:
            An lxml ElementTree representing the SVG document, or None if loading fails
            
        Raises:
            FileNotFoundError: If the file does not exist
            etree.XMLSyntaxError: If the file is not a valid XML/SVG document
        """
        if not os.path.isfile(file_path):
            raise FileNotFoundError(f"SVG file not found: {file_path}")
            
        try:
            parser = etree.XMLParser(remove_blank_text=True, recover=True)
            return etree.parse(file_path, parser=parser)
        except etree.XMLSyntaxError as e:
            raise etree.XMLSyntaxError(f"Invalid SVG/XML file {file_path}: {str(e)}")
    
    def validate_svg(self, svg_tree: etree._ElementTree) -> bool:
        """Validate that the parsed document is a valid SVG.
        
        Args:
            svg_tree: Parsed SVG document as lxml ElementTree
            
        Returns:
            bool: True if the document is a valid SVG, False otherwise
        """
        root = svg_tree.getroot()
        return root.tag.endswith('svg') or root.tag == '{http://www.w3.org/2000/svg}svg'
    
    def get_svg_dimensions(self, svg_tree: etree._ElementTree) -> Dict[str, Union[float, str]]:
        """Extract width and height from an SVG document.
        
        Args:
            svg_tree: Parsed SVG document as lxml ElementTree
            
        Returns:
            Dictionary with 'width' and 'height' as keys, with values as floats (if numeric)
            or strings (if using units like 'px', 'pt', etc.)
        """
        root = svg_tree.getroot()
        dimensions = {'width': '100%', 'height': '100%'}
        
        for dim in ['width', 'height']:
            value = root.get(dim)
            if value:
                # Try to convert to float if it's a number without units
                if value.replace('.', '').isdigit():
                    value = float(value)
                dimensions[dim] = value
                
        return dimensions
    
    def extract_embedded_content(self, svg_tree: etree._ElementTree) -> List[Dict[str, Any]]:
        """Extract any embedded content (like images) from the SVG.
        
        Args:
            svg_tree: Parsed SVG document as lxml ElementTree
            
        Returns:
            List of dictionaries containing information about embedded content
        """
        embedded = []
        root = svg_tree.getroot()
        
        # Find all image elements
        for img in root.xpath('//svg:image', namespaces=self.namespaces):
            href = img.get('{' + self.namespaces['xlink'] + '}href')
            if href and href.startswith('data:'):
                # Handle embedded base64 data
                mime_type = href.split(';')[0][5:]  # Extract MIME type from data URL
                embedded.append({
                    'type': 'embedded_image',
                    'mime_type': mime_type,
                    'element': img
                })
            elif href:
                # Handle linked images
                embedded.append({
                    'type': 'linked_image',
                    'href': href,
                    'element': img
                })
                
        return embedded
    
    def clean_svg(self, svg_tree: etree._ElementTree) -> etree._ElementTree:
        """Clean up an SVG document by removing unnecessary attributes and elements.
        
        Args:
            svg_tree: Parsed SVG document as lxml ElementTree
            
        Returns:
            Cleaned lxml ElementTree
        """
        # This is a placeholder for SVG cleaning logic
        # In a real implementation, this would remove unnecessary attributes,
        # optimize paths, etc.
        return svg_tree
