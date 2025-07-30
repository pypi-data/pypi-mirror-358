"""
Web Exporter Module

This module provides functionality to export web content to various formats,
including HTML, MHTML, and EML. It handles web page extraction, conversion,
and export operations.
"""

import mimetypes
import urllib.parse
from email.message import EmailMessage
from email.utils import formatdate, make_msgid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, cast

from bs4 import BeautifulSoup  # type: ignore
import requests  # type: ignore
from requests.adapters import HTTPAdapter  # type: ignore
from urllib3.util.retry import Retry  # type: ignore

class WebExtractor:
    """A class to handle web content extraction and export.

    This class provides methods to:
    - Download web pages and their resources
    - Convert web content to various formats (HTML, MHTML, EML)
    - Handle authentication and sessions
    - Process and clean HTML content
    - Export to different file formats
    """

    def __init__(self, output_dir: Optional[Union[str, Path]] = None) -> None:
        """Initialize the WebExtractor with an optional output directory.

        Args:
            output_dir: Directory to save exported files
                      (default: current directory)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create and configure a requests session with retry logic.

        Returns:
            Configured requests.Session object
        """
        session = requests.Session()
        retry = Retry(
            total=3,
            backoff_factor=0.5,
            status_forcelist=[500, 502, 503, 504],
        )
        adapter = HTTPAdapter(max_retries=retry)
        session.mount('http://', adapter)
        session.mount('https://', adapter)
        return session

    def fetch_url(
        self,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        auth: Optional[Tuple[str, str]] = None,
        timeout: int = 30,
    ) -> Tuple[Optional[str], Dict[str, Any]]:
        """Fetch content from a URL with error handling.

        Args:
            url: URL to fetch
            headers: Optional request headers
            auth: Optional (username, password) for basic auth
            timeout: Request timeout in seconds

        Returns:
            Tuple of (content, metadata) where content is the response text
            and metadata is a dict with status code, content type, etc.
        """
        try:
            response = self.session.get(
                url,
                headers=headers or {},
                auth=auth,
                timeout=timeout,
                allow_redirects=True,
            )
            response.raise_for_status()
            return response.text, {
                'status_code': response.status_code,
                'content_type': response.headers.get('content-type', ''),
                'url': response.url,
                'headers': dict(response.headers),
                'encoding': response.encoding,
            }
        except requests.RequestException as e:
            return None, {
                'error': str(e),
                'status_code': getattr(e.response, 'status_code', 0)
                if hasattr(e, 'response') else 0,
            }

    def export_html(
        self,
        url: str,
        output_file: Optional[Union[str, Path]] = None,
        include_resources: bool = True,
        clean_html: bool = True,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Export a web page to an HTML file.

        Args:
            url: URL of the web page to export
            output_file: Output file path (default: based on URL)
            include_resources: Whether to download and include linked resources
            clean_html: Whether to clean and format the HTML
            **kwargs: Additional arguments for fetch_url

        Returns:
            Dictionary with export results and metadata
        """
        if not output_file:
            parsed_url = urllib.parse.urlparse(url)
            filename = f"{parsed_url.netloc}{parsed_url.path or 'index'}.html"
            filename = filename.replace('/', '_').replace(':', '_')
            output_file = self.output_dir / filename
        else:
            output_file = Path(output_file)

        content, metadata = self.fetch_url(url, **kwargs)
        if not content:
            return {'success': False, 'error': 'Failed to fetch URL', **metadata}

        # Ensure content is a string
        html_content = str(content)

        if clean_html:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                html_content = soup.prettify()
            except Exception as e:
                return {'success': False, 
                        'error': f'HTML parsing error: {e}'}

        try:
            output_file.write_text(html_content, encoding='utf-8')
            result = {
                'success': True,
                'output_file': str(output_file),
                'size': output_file.stat().st_size,
                **metadata,
            }

            if include_resources:
                resources = self._download_resources(
                    html_content, output_file.parent
                )
                result['resources'] = resources

            return result
        except Exception as e:
            return {'success': False, 'error': str(e), **metadata}

    def _download_resources(
        self,
        html_content: str,
        output_dir: Union[str, Path],
    ) -> List[Dict[str, Any]]:
        """Download resources linked in HTML (images, CSS, JS, etc.).

        Args:
            html_content: HTML content to parse for resources
            output_dir: Directory to save downloaded resources

        Returns:
            List of downloaded resources with metadata
        """
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            resources: List[Dict[str, Any]] = []
            output_dir = Path(output_dir)
            (output_dir / 'resources').mkdir(exist_ok=True)

            # Define HTML tags and their attributes that contain resource URLs
            tags = {
                'img': 'src',
                'link': 'href',
                'script': 'src',
            }

            for tag_name, attr_name in tags.items():
                for element in soup.find_all(tag_name):
                    resource_url = element.get(attr_name)
                    if not resource_url:
                        continue

                    # Handle relative URLs
                    if not resource_url.startswith(('http://', 'https://')):
                        resource_url = urllib.parse.urljoin(
                            'http://example.com',  # Base URL will be replaced
                            resource_url
                        )

                    # Download the resource
                    try:
                        response = self.session.get(resource_url, stream=True)
                        response.raise_for_status()

                        # Determine file extension from content type or URL
                        content_type = response.headers.get('content-type', '')
                        ext = (
                            mimetypes.guess_extension(
                                content_type.split(';')[0]
                            ) or '.bin'
                        )
                        filename = f"resource_{len(resources)}{ext}"
                        filepath = output_dir / 'resources' / filename

                        with open(filepath, 'wb') as f:
                            for chunk in response.iter_content(chunk_size=8192):
                                f.write(chunk)

                        # Update the HTML to use the local resource
                        element[attr_name] = f"resources/{filename}"

                        resources.append({
                            'url': resource_url,
                            'local_path': str(filepath),
                            'size': filepath.stat().st_size,
                            'content_type': response.headers.get(
                                'content-type', ''
                            ),
                        })
                    except Exception:  # noqa: BLE001
                        # Skip failed resource downloads
                        continue

            # Save the updated HTML
            if resources:
                with open(output_dir / 'index.html', 'w', encoding='utf-8') as f:
                    f.write(str(soup))

            return resources
        except Exception as e:
            return [{'error': str(e)}]

    def export_mhtml(
        self,
        url: str,
        output_file: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Export a web page to MHTML format.

        Args:
            url: URL of the web page to export
            output_file: Output file path (default: based on URL)
            **kwargs: Additional arguments for fetch_url

        Returns:
            Dictionary with export results and metadata
        """
        if not output_file:
            parsed_url = urllib.parse.urlparse(url)
            filename = f"{parsed_url.netloc}{parsed_url.path or 'index'}.mhtml"
            filename = filename.replace('/', '_').replace(':', '_')
            output_file = self.output_dir / filename
        else:
            output_file = Path(output_file)

        try:
            # For MHTML, we'll use a simple approach of saving the raw response
            # A more complete implementation would properly encode all resources
            response = self.session.get(url, **kwargs)
            response.raise_for_status()

            with open(output_file, 'wb') as f:
                f.write(response.content)

            return {
                'success': True,
                'output_file': str(output_file),
                'size': output_file.stat().st_size,
                'content_type': response.headers.get('content-type', ''),
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def export_eml(
        self,
        url: str,
        subject: Optional[str] = None,
        from_addr: str = "webexport@example.com",
        to_addr: str = "export@example.com",
        output_file: Optional[Union[str, Path]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Export a web page to EML format.

        Args:
            url: URL of the web page to export
            subject: Email subject (default: based on page title or URL)
            from_addr: Sender email address
            to_addr: Recipient email address
            output_file: Output file path (default: based on URL)
            **kwargs: Additional arguments for fetch_url

        Returns:
            Dictionary with export results and metadata
        """
        if not output_file:
            parsed_url = urllib.parse.urlparse(url)
            filename = f"{parsed_url.netloc}{parsed_url.path or 'index'}.eml"
            filename = filename.replace('/', '_').replace(':', '_')
            output_file = self.output_dir / filename
        else:
            output_file = Path(output_file)

        content, metadata = self.fetch_url(url, **kwargs)
        if not content:
            return {'success': False, 'error': 'Failed to fetch URL', **metadata}

        # Ensure content is a string
        html_content = str(content)

        # Extract title for subject if not provided
        if not subject:
            try:
                soup = BeautifulSoup(html_content, 'html.parser')
                subject = soup.title.string if soup.title else url
            except Exception:  # noqa: BLE001
                subject = url

        # Create email message
        msg = EmailMessage()
        msg['From'] = from_addr
        msg['To'] = to_addr
        msg['Subject'] = subject
        msg['Date'] = formatdate()
        msg['Message-ID'] = make_msgid()
        msg['X-URL'] = url

        # Add HTML content
        msg.add_alternative(html_content, subtype='html')

        try:
            with open(output_file, 'wb') as f:
                f.write(msg.as_bytes())

            return {
                'success': True,
                'output_file': str(output_file),
                'size': output_file.stat().st_size,
                'subject': subject,
                'from': from_addr,
                'to': to_addr,
            }
        except Exception as e:  # noqa: BLE001
            return {'success': False, 'error': str(e)}

    def cleanup(self) -> None:
        """Clean up any temporary files or resources."""
        if hasattr(self, 'session'):
            self.session.close()

    def __enter__(self) -> 'WebExtractor':
        """Context manager entry."""
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Any,
    ) -> None:
        """Context manager exit - ensure resources are cleaned up.

        Args:
            exc_type: Exception type if an exception was raised
            exc_val: Exception value if an exception was raised
            exc_tb: Exception traceback if an exception was raised
        """
        self.cleanup()

    def __del__(self) -> None:
        """Destructor - ensure resources are cleaned up."""
        self.cleanup()
