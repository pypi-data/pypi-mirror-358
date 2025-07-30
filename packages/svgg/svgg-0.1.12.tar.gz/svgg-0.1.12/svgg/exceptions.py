"""
SVGG Exceptions Module

This module defines custom exceptions used throughout the SVGG package.
"""

class SVGGError(Exception):
    """Base exception for all SVGG-related errors."""
    pass


class FileNotFoundError(SVGGError):
    """Raised when a file cannot be found."""
    pass


class InvalidSVGError(SVGGError):
    """Raised when an SVG file is invalid or malformed."""
    pass


class ImportError(SVGGError):
    """Raised when there is an error importing data."""
    pass


class ExportError(SVGGError):
    """Raised when there is an error exporting data."""
    pass


class MetadataError(SVGGError):
    """Raised when there is an error with metadata operations."""
    pass


class StructureError(SVGGError):
    """Raised when there is an error with the SVG structure."""
    pass


class CompressionError(SVGGError):
    """Raised when there is an error with compression operations."""
    pass


class ValidationError(SVGGError):
    """Raised when validation of data fails."""
    pass
