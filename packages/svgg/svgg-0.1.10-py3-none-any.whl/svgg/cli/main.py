"""SVGG - SVG Generator Command Line Interface.

This module provides the main entry point for the SVGG CLI.
"""

import click
from typing import Optional

@click.group()
@click.version_option()
@click.help_option('-h', '--help')
def main() -> None:
    """SVGG - Universal tool for creating enhanced SVG files with embedded content.
    
    Examples:
        # Embed files into an SVG
        svgg embed file1.pdf file2.png --into template.svg --output result.svg
        
        # Create an SVG bundle from multiple files
        svgg create --files "*.pdf,*.png" --output bundle.svg
        
        # Extract embedded files from an SVG
        svgg extract result.svg --output-dir ./extracted/
        
        # Show information about embedded files
        svgg info result.svg
    """
    pass

@main.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--into', '-i', 'svg_file', required=True, help='Target SVG file to embed files into')
@click.option('--output', '-o', required=True, help='Output SVG file')
@click.option('--compression/--no-compression', default=False, help='Enable/disable compression')
@click.option('--metadata', '-m', help='JSON string with metadata')
def embed(files: tuple[str, ...], svg_file: str, output: str, compression: bool, metadata: Optional[str]) -> None:
    """Embed files into an SVG.
    
    FILES: One or more files to embed into the SVG
    """
    click.echo(f"Embedding {len(files)} files into {svg_file} -> {output}")
    click.echo(f"Compression: {'enabled' if compression else 'disabled'}")
    if metadata:
        click.echo(f"Metadata: {metadata}")

@main.command()
@click.option('--files', '-f', help='Comma-separated list of file patterns')
@click.option('--directory', '-d', help='Directory to scan for files')
@click.option('--output', '-o', required=True, help='Output SVG file')
@click.option('--template', '-t', help='Template SVG file')
def create(files: Optional[str], directory: Optional[str], output: str, template: Optional[str]) -> None:
    """Create an SVG bundle from multiple files."""
    if not files and not directory:
        raise click.UsageError("Either --files or --directory must be specified")
    
    click.echo(f"Creating SVG bundle: {output}")
    if files:
        click.echo(f"Including files: {files}")
    if directory:
        click.echo(f"Scanning directory: {directory}")
    if template:
        click.echo(f"Using template: {template}")

@main.command()
@click.argument('svg_file', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='.', help='Output directory for extracted files')
def extract(svg_file: str, output_dir: str) -> None:
    """Extract embedded files from an SVG.
    
    SVG_FILE: The SVG file containing embedded content
    """
    click.echo(f"Extracting files from {svg_file} to {output_dir}")

@main.command()
@click.argument('svg_file', type=click.Path(exists=True))
@click.option('--json', '-j', is_flag=True, help='Output as JSON')
def info(svg_file: str, json: bool) -> None:
    """Show information about embedded files in an SVG.
    
    SVG_FILE: The SVG file to inspect
    """
    if json:
        click.echo('{"status": "info", "file": "' + svg_file + '", "message": "Info command not yet implemented"}')
    else:
        click.echo(f"Information for {svg_file}:")
        click.echo("This command is not yet fully implemented.")

if __name__ == '__main__':
    main()
