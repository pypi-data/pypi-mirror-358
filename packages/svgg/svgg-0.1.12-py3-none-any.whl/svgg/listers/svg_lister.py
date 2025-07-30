"""
SVG Lister Module

This module provides functionality to list and inspect SVG contents,
including embedded files, metadata, and structural elements.
"""

from typing import Dict, List, Optional, Union
from xml.etree import ElementTree as ET

from ..exceptions import SVGGError

class SVGLister:
    """A class to list and inspect SVG contents.
    
    This class provides methods to:
    - List embedded files in an SVG
    - Inspect SVG structure and metadata
    - Generate reports about SVG contents
    """
    
    def __init__(self, svg_content: Union[str, bytes, ET.Element]) -> None:
        """Initialize the SVGLister with SVG content.
        
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
    
    def list_embedded_files(self) -> List[Dict[str, object]]:
        """List all embedded files in the SVG.
        
        Returns:
            List of dictionaries containing information about embedded files.
            Each dictionary has string keys and values that can be strings or integers.
        """
        embedded_files = []
        
        # Check for files embedded in custom metadata elements
        for elem in self.root.findall(".//*[@data-filename]"):
            if 'data-content' in elem.attrib:
                filename = elem.get('data-filename', 'unnamed.bin')
                content_type = elem.get('data-type', 'application/octet-stream')
                size = len(elem.get('data-content', '')) * 3 // 4  # Approximate size
                
                embedded_files.append({
                    'filename': filename,
                    'type': content_type,
                    'size_bytes': size,
                    'location': 'metadata',
                    'element': elem.tag
                })
        
        # Check for files embedded in comments (common pattern)
        for i, comment in enumerate(self._find_comments(self.root)):
            text = comment.text.strip() if comment.text else ''
            if text.startswith('FILE:'):
                try:
                    parts = text.split('\n', 1)
                    if len(parts) == 2:
                        filename = parts[0][5:].strip()
                        size = len(parts[1].strip()) * 3 // 4  # Approximate size
                        
                        embedded_files.append({
                            'filename': filename,
                            'type': 'application/octet-stream',
                            'size_bytes': size,
                            'location': f'comment_{i}',
                            'element': 'comment'
                        })
                except Exception as e:
                    print(f"Warning: Failed to parse embedded file from comment: {str(e)}")
        
        return embedded_files
    
    def get_metadata(self) -> Dict[str, str]:
        """Extract metadata from the SVG.
        
        Returns:
            Dictionary containing SVG metadata
        """
        metadata = {}
        
        # Basic SVG metadata
        metadata['width'] = self.root.get('width', '100%')
        metadata['height'] = self.root.get('height', '100%')
        metadata['viewBox'] = self.root.get('viewBox', '')
        
        # Check for metadata elements
        metadata_elem = self.root.find('{http://www.w3.org/2000/svg}metadata')
        if metadata_elem is not None:
            for child in metadata_elem:
                if child.text and child.text.strip():
                    metadata[child.tag.split('}')[-1]] = child.text.strip()
        
        return metadata
    
    def list_elements(self, element_type: Optional[str] = None) -> List[Dict[str, str]]:
        """List all elements in the SVG, optionally filtered by type.
        
        Args:
            element_type: Optional element type to filter by (e.g., 'rect', 'circle')
            
        Returns:
            List of dictionaries containing element information
        """
        elements = []
        
        # If no specific type is provided, find all elements
        if element_type is None:
            for elem in self.root.iter():
                elements.append({
                    'tag': elem.tag.split('}')[-1],
                    'id': elem.get('id', ''),
                    'class': elem.get('class', '')
                })
        else:
            # Find elements of the specified type
            for elem in self.root.findall(f'.//{{*}}{element_type}'):
                elements.append({
                    'tag': elem.tag.split('}')[-1],
                    'id': elem.get('id', ''),
                    'class': elem.get('class', '')
                })
        
        return elements
    
    def _find_comments(self, element: ET.Element) -> List[ET.Element]:
        """Recursively find all comments in the element tree.
        
        Args:
            element: Root element to search from
            
        Returns:
            List of elements that are comments
        """
        comments: List[ET.Element] = []
        
        # Check if this element has a comment as a direct child
        if element.text and isinstance(element.text, str) and '<!--' in element.text:
            # This is a simplified approach; for full comment parsing, consider using lxml
            comment_text = element.text.strip()
            if comment_text.startswith('<!--') and comment_text.endswith('-->'):
                # Create a new element to represent the comment
                comment_elem = ET.Element('comment')
                comment_elem.text = comment_text[4:-3].strip()
                comments.append(comment_elem)
        
        # Recursively check child elements
        for child in element:
            comments.extend(self._find_comments(child))
        
        return comments
    
    def generate_report(self) -> str:
        """Generate a text report about the SVG contents.
        
        Returns:
            Formatted text report
        """
        report = []
        
        # Basic SVG info
        metadata = self.get_metadata()
        report.append("=== SVG Information ===")
        report.append(f"Dimensions: {metadata.get('width', '?')} x {metadata.get('height', '?')}")
        report.append(f"ViewBox: {metadata.get('viewBox', 'Not specified')}")
        
        # Embedded files
        embedded_files = self.list_embedded_files()
        report.append("\n=== Embedded Files ===")
        if embedded_files:
            for i, file_info in enumerate(embedded_files, 1):
                size_bytes = int(file_info.get('size_bytes', 0))  # Ensure it's an int
                size_kb = size_bytes / 1024.0
                report.append(
                    f"{i}. {file_info['filename']} ({size_kb:.2f} KB, "
                    f"{file_info['type']}) in {file_info['location']}"
                )
        else:
            report.append("No embedded files found.")
        
        # Element counts
        elements = self.list_elements()
        element_counts: Dict[str, int] = {}
        for elem in elements:
            tag = str(elem.get('tag', 'unknown'))
            element_counts[tag] = element_counts.get(tag, 0) + 1
        
        report.append("\n=== Elements ===")
        for tag, count in sorted(element_counts.items()):
            report.append(f"- {tag}: {count}")
        
        return "\n".join(report)


