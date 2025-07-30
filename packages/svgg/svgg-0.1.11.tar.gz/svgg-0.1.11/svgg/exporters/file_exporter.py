"""
SVG Exporter Module

This module provides functionality to export SVG files with embedded content,
including support for different export formats and configurations.
"""

import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from xml.etree import ElementTree as ET
from xml.dom import minidom

class SVGExporter:
    """A class to handle exporting SVG files with embedded content.

    This class provides methods to:
    - Export SVG files with embedded content
    - Handle different export formats (SVG, PNG, PDF, etc.)
    - Manage file system operations for exports
    - Preserve metadata and structure
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """Initialize the SVGExporter with an optional output directory.

        Args:
            output_dir: Directory to save exported files (default: current directory)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
    def export_svg(
        self,
        svg_content: Union[str, bytes, ET.Element],
        filename: str,
        embed_data: Optional[Dict[str, Any]] = None,
        pretty_print: bool = True,
    ) -> Path:
        """Export an SVG file with optional embedded data.

        Args:
            svg_content: SVG content as string, bytes, or ElementTree Element
            filename: Output filename (without .svg extension if not present)
            embed_data: Dictionary of data to embed in the SVG
            pretty_print: Whether to format the output with indentation

        Returns:
            Path to the exported SVG file

        Raises:
            ValueError: If svg_content is not a valid type
        """
        # Ensure filename has .svg extension
        if not filename.lower().endswith('.svg'):
            filename += '.svg'

        output_path = self.output_dir / filename

        # Convert input to ElementTree Element if needed
        if isinstance(svg_content, str):
            root = ET.fromstring(svg_content)
        elif isinstance(svg_content, bytes):
            root = ET.fromstring(svg_content.decode('utf-8'))
        elif isinstance(svg_content, ET.Element):
            root = svg_content
        else:
            raise ValueError(
                "svg_content must be str, bytes, or ElementTree.Element"
            )

        # Add XML declaration if not present
        if not hasattr(root, 'tag'):
            raise ValueError("Invalid SVG content")

        # Add namespace if not present
        if 'xmlns' not in root.attrib:
            root.attrib['xmlns'] = 'http://www.w3.org/2000/svg'

        # Add embedded data if provided
        if embed_data:
            self._add_embedded_data(root, embed_data)

        # Convert to string with pretty printing if requested
        xml_string = ET.tostring(root, encoding='unicode')

        if pretty_print:
            # Parse the XML with minidom for pretty printing
            parsed = minidom.parseString(xml_string)
            xml_string = parsed.toprettyxml(indent='  ')

            # Remove extra newlines added by minidom
            xml_string = '\n'.join(
                line for line in xml_string.split('\n')
                if line.strip()
            )

        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(xml_string)

        return output_path
    
    def export_png(
        self,
        svg_content: Union[str, bytes, ET.Element],
        filename: str,
        dpi: int = 96,
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Path:
        """Export an SVG to PNG format.

        Args:
            svg_content: SVG content as string, bytes, or ElementTree Element
            filename: Output filename (without .png extension if not present)
            dpi: Dots per inch for the output image
            width: Output width in pixels (maintains aspect ratio if only one dimension is specified)
            height: Output height in pixels

        Returns:
            Path to the exported PNG file

        Note:
            Requires cairosvg or svglib to be installed.
        """
        try:
            import cairosvg  # type: ignore
            use_cairo = True
        except ImportError:
            try:
                from svglib.svglib import svg2rlg  # type: ignore
                from reportlab.graphics import renderPM  # type: ignore
                use_cairo = False
            except ImportError as e:
                raise ImportError(
                    "Exporting to PNG requires either cairosvg or svglib+reportlab. "
                    "Install with: pip install cairosvg or pip install svglib reportlab"
                ) from e
        
        # Ensure filename has .png extension
        if not filename.lower().endswith('.png'):
            filename += '.png'

        output_path = self.output_dir / filename

        # If we have an Element, convert to string
        if isinstance(svg_content, ET.Element):
            svg_content = ET.tostring(svg_content, encoding='unicode')

        # Convert to bytes if needed
        if isinstance(svg_content, str):
            svg_content = svg_content.encode('utf-8')

        # Export using cairosvg or svglib
        if use_cairo:
            cairosvg.svg2png(
                bytestring=svg_content,
                write_to=str(output_path),
                dpi=dpi,
                output_width=width,
                output_height=height
            )
        else:
            # Fall back to svglib+reportlab
            drawing = svg2rlg(svg_content)
            scale_x = scale_y = 1.0

            if width is not None:
                scale_x = width / drawing.width
                if height is None:
                    scale_y = scale_x
            if height is not None:
                scale_y = height / drawing.height
                if width is None:
                    scale_x = scale_y

            if scale_x != 1.0 or scale_y != 1.0:
                drawing.scale(scale_x, scale_y)

            renderPM.drawToFile(
                drawing, str(output_path), fmt='PNG', dpi=dpi
            )

        return output_path
    
    def export_pdf(
        self,
        svg_content: Union[str, bytes, ET.Element],
        filename: str,
    ) -> Path:
        """Export an SVG to PDF format.

        Args:
            svg_content: SVG content as string, bytes, or ElementTree Element
            filename: Output filename (without .pdf extension if not present)

        Returns:
            Path to the exported PDF file

        Note:
            Requires cairosvg or svglib to be installed.
        """
        try:
            import cairosvg  # type: ignore
            use_cairo = True
        except ImportError:
            try:
                from svglib.svglib import svg2rlg  # type: ignore
                from reportlab.graphics import renderPDF  # type: ignore
                use_cairo = False
            except ImportError as e:
                raise ImportError(
                    "Exporting to PDF requires either cairosvg or svglib+reportlab. "
                    "Install with: pip install cairosvg or pip install svglib reportlab"
                ) from e
        
        # Ensure filename has .pdf extension
        if not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        output_path = self.output_dir / filename

        # If we have an Element, convert to string
        if isinstance(svg_content, ET.Element):
            svg_content = ET.tostring(svg_content, encoding='unicode')

        # Convert to bytes if needed
        if isinstance(svg_content, str):
            svg_content = svg_content.encode('utf-8')

        # Export using cairosvg or svglib
        if use_cairo:
            cairosvg.svg2pdf(
                bytestring=svg_content, write_to=str(output_path)
            )
        else:
            # Fall back to svglib+reportlab
            drawing = svg2rlg(svg_content)
            renderPDF.drawToFile(drawing, str(output_path))

        return output_path
    
    def _add_embedded_data(
        self,
        svg_element: ET.Element,
        data: Dict[str, Any],
        parent: Optional[ET.Element] = None,
    ) -> None:
        """Add embedded data to an SVG element.

        Args:
            svg_element: The root SVG element to add data to
            data: Dictionary of data to embed
            parent: Parent element to add data to (default: svg_element)
        """
        if parent is None:
            parent = svg_element

        # Add metadata element if it doesn't exist
        metadata = svg_element.find('{http://www.w3.org/2000/svg}metadata')
        if metadata is None:
            metadata = ET.SubElement(svg_element, 'metadata')

        # Create a data element
        data_element = ET.SubElement(metadata, 'data')

        # Add data as attributes or child elements
        for key, value in data.items():
            if isinstance(value, (str, int, float, bool)):
                data_element.set(key, str(value))
            elif isinstance(value, dict):
                child = ET.SubElement(data_element, key)
                for k, v in value.items():
                    child.set(k, str(v))
            else:
                # Try to serialize as JSON for complex types
                try:
                    json_str = json.dumps(value)
                    data_element.set(key, json_str)
                except (TypeError, ValueError):
                    # Fall back to string representation
                    data_element.set(key, str(value))
    
    def export_directory(
        self,
        svg_files: List[Union[str, Path, Dict[str, Any]]],
        output_dir: Optional[Union[str, Path]] = None,
        format: str = 'svg',
        **kwargs,
    ) -> List[Path]:
        """Export multiple SVG files at once.

        Args:
            svg_files: List of SVG files or dictionaries with 'content' and 'filename' keys
            output_dir: Directory to save exported files (overrides instance output_dir)
            format: Output format ('svg', 'png', or 'pdf')
            **kwargs: Additional arguments to pass to the export function

        Returns:
            List of paths to exported files
        """
        export_dir = Path(output_dir) if output_dir else self.output_dir
        export_dir.mkdir(parents=True, exist_ok=True)

        exported_files = []

        for item in svg_files:
            if isinstance(item, (str, Path)):
                # Simple case: item is a file path
                with open(item, 'rb') as f:
                    content = f.read()
                filename = Path(item).stem
            elif isinstance(item, dict) and 'content' in item and 'filename' in item:
                # Dictionary with content and filename
                content = item['content']
                filename = item['filename']
            else:
                raise ValueError(
                    "Items must be file paths or dictionaries with 'content' and 'filename' keys"
                )

            # Add format extension to filename if needed
            if not filename.lower().endswith(f'.{format}'):
                filename = f"{filename}.{format}"

            # Export based on format
            if format.lower() == 'svg':
                exported = self.export_svg(content, filename, **kwargs)
            elif format.lower() == 'png':
                exported = self.export_png(content, filename, **kwargs)
            elif format.lower() == 'pdf':
                exported = self.export_pdf(content, filename, **kwargs)
            else:
                raise ValueError(f"Unsupported export format: {format}")

            exported_files.append(exported)

        return exported_files
    
    def cleanup(self) -> None:
        """Clean up any temporary files or resources."""
        # This method can be overridden by subclasses to clean up resources
        pass

    def __enter__(self) -> 'SVGExporter':
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensure resources are cleaned up."""
        self.cleanup()

    def __del__(self) -> None:
        """Destructor - ensure resources are cleaned up."""
        self.cleanup()
