# Package initialization
"""
SVGG - SVG Generator

Universal tool for creating enhanced SVG files with embedded content.
Supports import/export of files as base64 DATA URIs with metadata management.
"""

from .version import __version__, __author__, __email__

# Core functionality
from .core.svg_generator import SVGGenerator
from .core.metadata_manager import MetadataManager
from .core.file_handler import FileHandler

# Importers
from .importers.file_importer import SVGImporter
from .importers.multi_importer import MultiImporter
from .importers.zip_importer import ZipImporter
from .importers.project_importer import ProjectImporter
from .importers.repository_importer import RepositoryImporter
from .importers.smart_importer import SmartImporter

# Exporters
from .exporters.file_exporter import SVGExporter
from .exporters.web_exporter import WebExtractor
from .exporters.doc_exporter import DocExporter
from .exporters.batch_exporter import BatchProcessor

# Extractors
from .extractors.file_extractor import FileExtractor

# Listers
from .listers.svg_lister import SVGLister

# Validators
from .validators.svg_validator import SVGValidator

# Configuration
from .config.config_manager import ConfigManager

# Utilities
from .utils.logger import setup_logger
from .utils.file_utils import FileUtils

# Exceptions
from .exceptions import (
    SVGGError,
    FileNotFoundError,
    InvalidSVGError,
    ImportError,
    ExportError,
    MetadataError,
    StructureError,
    CompressionError,
    ValidationError,
)

# API Client
try:
    from .server.client import SVGGClient
except ImportError:
    SVGGClient = None

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",

    # Core classes
    "SVGGenerator",
    "MetadataManager",
    "FileHandler",

    # Importers
    "SVGImporter",
    "MultiImporter",
    "ZipImporter",
    "ProjectImporter",
    "RepositoryImporter",
    "SmartImporter",

    # Exporters
    "SVGExporter",
    "WebExtractor",
    "DocExporter",
    "BatchProcessor",

    # Extractors
    "FileExtractor",

    # Listers
    "SVGLister",

    # Validators
    "SVGValidator",

    # Configuration
    "ConfigManager",

    # Utilities
    "FileUtils",
    "setup_logger",
    ]