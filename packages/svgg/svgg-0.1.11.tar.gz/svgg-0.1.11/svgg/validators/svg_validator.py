"""
SVG Validator Module

This module provides functionality to validate SVG content against the SVG specification
and check for common issues and best practices.
"""

"""SVG Validator Module.

This module provides functionality to validate SVG content against the SVG
specification and check for common issues and best practices.
"""

import re
from typing import Dict, List, Union
from xml.etree import ElementTree as ET

from ..exceptions import SVGGError

class SVGValidator:
    """Validate SVG content against the SVG specification.
    
    This class provides methods to validate SVG structure and syntax,
    check for common issues and best practices, and generate validation reports.
    """
    
    def __init__(self, svg_content: Union[str, bytes, ET.Element]) -> None:
        """Initialize the SVGValidator with SVG content.
        
        Args:
            svg_content: SVG content as string, bytes, or ElementTree Element
        """
        self.svg_content = svg_content
        self.root = self._parse_svg()
        self.errors: List[Dict[str, str]] = []
        self.warnings: List[Dict[str, str]] = []
    
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
    
    def validate_structure(self) -> bool:
        """Validate the basic structure of the SVG.
        
        Returns:
            True if the SVG structure is valid, False otherwise
        """
        is_valid = True
        
        # Check root element is SVG
        if self.root.tag != '{http://www.w3.org/2000/svg}svg':
            self.errors.append({
                'code': 'INVALID_ROOT',
                'message': 'Root element must be an SVG element',
                'element': self.root.tag
            })
            is_valid = False
        
        # Check for required attributes
        required_attrs = ['width', 'height', 'viewBox']
        for attr in required_attrs:
            if attr not in self.root.attrib:
                self.warnings.append({
                    'code': f'MISSING_{attr.upper()}',
                    'message': f'SVG is missing recommended attribute: {attr}',
                    'element': 'svg'
                })
        
        return is_valid
    
    def validate_elements(self) -> bool:
        """Validate SVG elements and their attributes.
        
        Returns:
            True if all elements are valid, False otherwise
        """
        is_valid = True
        
        # Define valid SVG elements (simplified list)
        valid_elements = {
            'svg', 'g', 'path', 'rect', 'circle', 'ellipse', 'line', 'polyline',
            'polygon', 'text', 'tspan', 'image', 'use', 'defs', 'clipPath',
            'linearGradient', 'radialGradient', 'stop', 'style', 'script'
        }
        
        # Check all elements in the document
        for element in self.root.iter():
            # Remove namespace for validation
            tag = element.tag.split('}')[-1] if '}' in element.tag else element.tag
            
            # Check if this element has a comment as a direct child
            if element.text and isinstance(element.text, str) and '<!--' in element.text:
                # This is a simplified approach; for full comment parsing,
                # consider using lxml
                comment_text = element.text.strip()
                if comment_text.startswith('<!--') and comment_text.endswith('-->'):
                    # Create a new element to represent the comment
                    comment_elem = ET.Element('comment')
                    comment_elem.text = comment_text[4:-3].strip()
                    element.append(comment_elem)
            
            # Check if element is a valid SVG element
            if tag not in valid_elements:
                self.warnings.append({
                    'code': 'UNKNOWN_ELEMENT',
                    'message': f'Element <{tag}> is not a standard SVG element',
                    'element': tag
                })
            
            # Validate element attributes
            is_valid = self._validate_attributes(element, tag) and is_valid
        
        return is_valid
    
    def _validate_attributes(self, elem: ET.Element, tag: str) -> bool:
        """Validate attributes for a given element.
        
        Args:
            elem: The element to validate
            tag: The element's tag name (without namespace)
            
        Returns:
            True if all attributes are valid, False otherwise
        """
        is_valid = True
        
        # Define required attributes for common elements
        required_attrs = {
            'image': ['xlink:href', 'x', 'y', 'width', 'height'],
            'use': ['xlink:href', 'x', 'y'],
            'linearGradient': ['id', 'x1', 'y1', 'x2', 'y2'],
            'radialGradient': ['id', 'cx', 'cy', 'r', 'fx', 'fy'],
            'stop': ['offset', 'stop-color']
        }
        
        # Check required attributes
        for attr in required_attrs.get(tag, []):
            if attr not in elem.attrib:
                self.errors.append({
                    'code': 'MISSING_ATTR',
                    'message': f'Required attribute "{attr}" is missing',
                    'element': tag,
                    'attribute': attr
                })
                is_valid = False
        
        # Validate attribute values
        for attr, value in elem.attrib.items():
            if attr == 'id' and not self._is_valid_id(value):
                self.errors.append({
                    'code': 'INVALID_ID',
                    'message': f'Invalid ID: "{value}" (must start with a letter)'
                })
                is_valid = False
            
            # Add more attribute validations as needed
            
        return is_valid
    
    def _is_valid_id(self, id_str: str) -> bool:
        """Check if an ID is valid according to XML ID rules.
        
        Args:
            id_str: The ID to validate
            
        Returns:
            True if the ID is valid, False otherwise
        """
        if not id_str:
            return False
        
        # Must start with a letter or underscore
        if not (id_str[0].isalpha() or id_str[0] == '_'):
            return False
        
        # Can contain letters, digits, hyphens, underscores, colons, and periods
        return bool(re.match(r'^[a-zA-Z_][\w\-.:]*$', id_str))
    
    def validate(self) -> Dict[str, Union[bool, List[Dict[str, str]]]]:
        """Run all validation checks on the SVG.
        
        Returns:
            Dictionary containing validation results with 'is_valid' flag,
            'errors' and 'warnings' lists
        """
        self.errors = []
        self.warnings = []
        
        # Run validation checks
        self.validate_structure()
        self.validate_elements()
        
        return {
            'is_valid': len(self.errors) == 0,
            'errors': self.errors,
            'warnings': self.warnings
        }
    
    def get_validation_report(self) -> str:
        """Generate a human-readable validation report.
        
        Returns:
            Formatted validation report as a string
        """
        result = self.validate()
        
        report = ["=== SVG Validation Report ==="]
        
        # Add errors
        if result['errors']:
            report.append("\nErrors:")
            for i, error in enumerate(result['errors'], 1):
                report.append(f"{i}. [{error.get('code', 'UNKNOWN')}] {error['message']}")
                if 'element' in error:
                    report.append(f"   Element: {error['element']}")
                if 'attribute' in error:
                    report.append(f"   Attribute: {error['attribute']}")
        else:
            report.append("\nNo errors found!")
        
        # Add warnings
        if result['warnings']:
            report.append("\nWarnings:")
            for i, warning in enumerate(result['warnings'], 1):
                report.append(f"{i}. [{warning.get('code', 'UNKNOWN')}] {warning['message']}")
                if 'element' in warning:
                    report.append(f"   Element: {warning['element']}")
                if 'attribute' in warning:
                    report.append(f"   Attribute: {warning['attribute']}")
        else:
            report.append("\nNo warnings found!")
        
        # Add summary
        error_count = len(result['errors'])
        warning_count = len(result['warnings'])
        report.append(f"\nSummary: {error_count} errors, {warning_count} warnings")
        
        return "\n".join(report)
    
    @staticmethod
    def is_valid_svg(svg_content: Union[str, bytes]) -> bool:
        """Quickly check if the given content is valid SVG.
        
        Args:
            svg_content: SVG content as string or bytes
            
        Returns:
            True if the content is valid SVG, False otherwise
        """
        try:
            validator = SVGValidator(svg_content)
            result = validator.validate()
            return result['is_valid']
        except Exception:
            return False

