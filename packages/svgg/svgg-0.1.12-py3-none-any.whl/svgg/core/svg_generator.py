"""
SVG Generator Module

This module provides functionality to generate and manipulate SVG files
with embedded content using base64-encoded data URIs.
"""

import base64
import json
import mimetypes
import os
from typing import Dict, List, Optional, Union, Any

class SVGGenerator:
    """
    Main class for generating and manipulating SVG files with embedded content.
    """
    
    def __init__(self):
        """Initialize the SVGGenerator with default settings."""
        self.metadata = {}
        self.compression = True
    
    def embed(
        self,
        svg_file: str,
        files: List[str],
        output: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Embed files into an SVG file as data URIs.
        
        Args:
            svg_file: Path to the source SVG file
            files: List of file paths to embed
            output: Path to save the output SVG file
            metadata: Optional metadata to include in the SVG
            
        Returns:
            Dictionary with status and information about embedded files
        """
        try:
            # Initialize metadata
            self.metadata = metadata or {}
            self.metadata['embedded_files'] = []
            
            # Read the SVG file
            with open(svg_file, 'r', encoding='utf-8') as f:
                svg_content = f.read()
                
            # Process each file to embed
            embedded_files = []
            for file_path in files:
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"File not found: {file_path}")
                
                # Get MIME type
                mime_type, _ = mimetypes.guess_type(file_path)
                
                # Read file as binary and encode as base64
                with open(file_path, 'rb') as bin_file:
                    file_data = bin_file.read()
                
                if not mime_type:
                    mime_type = 'application/octet-stream'
                    
                encoded_data = base64.b64encode(file_data).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{encoded_data}"
                
                # Store file info in metadata
                file_info = {
                    'path': file_path,
                    'mime_type': mime_type,
                    'size': len(file_data),
                    'data_uri': data_uri[:100] + '...'  # Store a preview
                }
                self.metadata['embedded_files'].append(file_info)
                embedded_files.append(file_info)
            
            # Format the embedded files for the SVG
            embedded_content = [{
                'path': f['path'],
                'mime_type': f['mime_type'],
                'size': f['size']
            } for f in embedded_files]
            
            # Create the final SVG content
            metadata_str = json.dumps(self.metadata, indent=2)
            script_content = f"""<script type="application/json" id="svgg-metadata">
{metadata_str}
</script>"""
            
            # Insert before the closing </svg> tag
            if '</svg>' in svg_content:
                svg_content = svg_content.replace('</svg>', f"\n{script_content}\n</svg>")
            else:
                svg_content += f"\n{script_content}"
            
            # Write the output file
            os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
            with open(output, 'w', encoding='utf-8') as f:
                f.write(svg_content)
            
            return {
                'success': True,
                'output': output,
                'embedded_files': embedded_content
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'embedded_files': []
            }

    def extract(self, svg_file: str, output_dir: str) -> List[Dict]:
        """
        Extract embedded files from an SVG.
        
        Args:
            svg_file: Path to the SVG file with embedded content
            output_dir: Directory to extract files to
            
        Returns:
            List of extracted file information
        """
        try:
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Read the SVG file - this is a placeholder for actual implementation
            with open(svg_file, 'r', encoding='utf-8') as svg_file_obj:
                svg_content = svg_file_obj.read()  # Read content for future implementation
                # This will be used when implementing the actual extraction logic
            
            # In a real implementation, you would:
            # 1. Parse the SVG XML properly
            # 2. Find all embedded data URIs
            # 3. Extract and decode them
            # 4. Save to the output directory
            
            # For now, we'll just return a placeholder
            return [{
                'status': 'not_implemented',
                'message': 'Extraction not yet implemented',
                'output_dir': output_dir
            }]
            
        except Exception as e:
            return [{
                'status': 'error',
                'message': str(e)
            }]


# For backward compatibility
SVGGenerator = SVGGenerator  # type: ignore
