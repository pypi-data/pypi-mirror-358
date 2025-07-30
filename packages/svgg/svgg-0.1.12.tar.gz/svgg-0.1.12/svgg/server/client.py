"""Client for interacting with the SVGG server.

This module provides a client class for communicating with the SVGG server.
It handles authentication, request/response serialization, and error handling.
"""

import json
import logging
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter, Retry

from svgg.utils.logger import get_logger


class SVGGClient:
    """Client for interacting with the SVGG server.
    
    This class provides methods to communicate with the SVGG server,
    handling authentication, request/response serialization, and error handling.
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:5000",
        api_key: Optional[str] = None,
        timeout: int = 30,
        max_retries: int = 3,
        backoff_factor: float = 0.5,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        """Initialize the SVGG client.
        
        Args:
            base_url: Base URL of the SVGG server.
            api_key: API key for authentication (if required).
            timeout: Request timeout in seconds.
            max_retries: Maximum number of retries for failed requests.
            backoff_factor: Backoff factor for retries.
            logger: Logger instance to use. If None, a default logger will be created.
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.timeout = timeout
        self.logger = logger or get_logger('svgg.client')
        
        # Configure session with retry strategy
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=backoff_factor,
            status_forcelist=[408, 429, 500, 502, 503, 504],
            allowed_methods=["GET", "POST", "PUT", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
        
        # Set up default headers
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        })
        
        if self.api_key:
            self.session.headers['Authorization'] = f'Bearer {self.api_key}'
    
    def _request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        files: Optional[Dict] = None,
    ) -> Dict[str, Any]:
        """Send an HTTP request to the server.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.).
            endpoint: API endpoint (e.g., '/api/svgs').
            data: Request body as a dictionary.
            params: Query parameters.
            files: Files to upload (for multipart/form-data).
            
        Returns:
            Parsed JSON response as a dictionary.
            
        Raises:
            requests.HTTPError: If the request fails.
            ValueError: If the response is not valid JSON.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        self.logger.debug(
            "Sending %s request to %s with params=%s, data=%s",
            method, url, params, data
        )
        
        try:
            if files:
                # For file uploads, don't use json=, use data= and files=
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    data=data,
                    files=files,
                    timeout=self.timeout,
                )
            else:
                # For JSON data, use json= which handles serialization
                response = self.session.request(
                    method,
                    url,
                    params=params,
                    json=data,
                    timeout=self.timeout,
                )
            
            response.raise_for_status()
            
            # Handle empty responses
            if not response.content:
                return {}
                
            return response.json()
            
        except requests.exceptions.JSONDecodeError as e:
            self.logger.error("Failed to parse JSON response: %s", str(e))
            raise ValueError(f"Invalid JSON response: {response.text}") from e
            
        except requests.exceptions.RequestException as e:
            self.logger.error("Request failed: %s", str(e))
            raise
    
    # Example API methods - these should be updated based on actual API endpoints
    
    def get_svg(self, svg_id: str) -> Dict[str, Any]:
        """Get an SVG by its ID.
        
        Args:
            svg_id: ID of the SVG to retrieve.
            
        Returns:
            SVG data as a dictionary.
        """
        return self._request('GET', f'/api/svgs/{svg_id}')
    
    def create_svg(self, svg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new SVG.
        
        Args:
            svg_data: SVG data to create.
            
        Returns:
            Created SVG data.
        """
        return self._request('POST', '/api/svgs', data=svg_data)
    
    def update_svg(self, svg_id: str, svg_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing SVG.
        
        Args:
            svg_id: ID of the SVG to update.
            svg_data: Updated SVG data.
            
        Returns:
            Updated SVG data.
        """
        return self._request('PUT', f'/api/svgs/{svg_id}', data=svg_data)
    
    def delete_svg(self, svg_id: str) -> None:
        """Delete an SVG.
        
        Args:
            svg_id: ID of the SVG to delete.
        """
        self._request('DELETE', f'/api/svgs/{svg_id}')
    
    def upload_svg_file(self, file_path: str) -> Dict[str, Any]:
        """Upload an SVG file to the server.
        
        Args:
            file_path: Path to the SVG file to upload.
            
        Returns:
            Uploaded SVG data.
        """
        with open(file_path, 'rb') as f:
            return self._request(
                'POST',
                '/api/svgs/upload',
                files={'file': (Path(file_path).name, f, 'image/svg+xml')}
            )
    
    def health_check(self) -> Dict[str, Any]:
        """Check the health of the SVGG server.
        
        Returns:
            Health status information.
        """
        return self._request('GET', '/health')


# Example usage
if __name__ == "__main__":
    # Initialize client
    client = SVGGClient(base_url="http://localhost:5000")
    
    try:
        # Check server health
        health = client.health_check()
        print(f"Server health: {health}")
        
        # Example: Upload an SVG file
        # response = client.upload_svg_file("example.svg")
        # print(f"Uploaded SVG: {response}")
        
    except Exception as e:
        print(f"Error: {e}")
