"""Configuration management for SVGG.

This module provides the ConfigManager class which handles loading, validating,
and managing configuration settings for the SVGG package.
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional, Union


class ConfigManager:
    """Manages configuration settings for the SVGG package.
    
    This class handles loading configuration from various sources, validating
    the configuration, and providing access to configuration values.
    """
    
    DEFAULT_CONFIG = {
        "output_dir": "output",
        "compression": False,
        "max_file_size": 10485760,  # 10MB
        "allowed_extensions": ["pdf", "png", "jpg", "jpeg", "txt"],
        "default_template": "default.svg",
        "debug": False,
    }
    
    def __init__(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Initialize the ConfigManager.
        
        Args:
            config_path: Optional path to a configuration file.
                If not provided, uses default configuration.
        """
        self._config = self.DEFAULT_CONFIG.copy()
        self.config_path = Path(config_path) if config_path else None
        
        if self.config_path and self.config_path.exists():
            self.load_config()
    
    def load_config(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Load configuration from a file.
        
        Args:
            config_path: Path to the configuration file.
                If not provided, uses the path from initialization.
                
        Raises:
            FileNotFoundError: If the config file does not exist.
            json.JSONDecodeError: If the config file is not valid JSON.
        """
        if config_path:
            self.config_path = Path(config_path)
            
        if not self.config_path or not self.config_path.exists():
            msg = f"Config file not found: {self.config_path}"
            raise FileNotFoundError(msg)
            
        with open(self.config_path, 'r', encoding='utf-8') as f:
            user_config = json.load(f)
            
        # Update default config with user-provided values
        self._config.update(user_config)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key.
        
        Args:
            key: The configuration key to retrieve.
            default: Default value to return if key is not found.
            
        Returns:
            The configuration value, or the default if key is not found.
        """
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: The configuration key to set.
            value: The value to set.
        """
        self._config[key] = value
    
    def save(self, config_path: Optional[Union[str, Path]] = None) -> None:
        """Save the current configuration to a file.
        
        Args:
            config_path: Path to save the configuration. If not provided, uses
                the current config_path.
        """
        if config_path:
            self.config_path = Path(config_path)
            
        if not self.config_path:
            raise ValueError("No config path specified")
            
        # Ensure the directory exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self._config, f, indent=2)
    
    def __getitem__(self, key: str) -> Any:
        """Get a configuration value using dict-style access."""
        return self._config[key]
    
    def __setitem__(self, key: str, value: Any) -> None:
        """Set a configuration value using dict-style access."""
        self._config[key] = value
    
    def __contains__(self, key: str) -> bool:
        """Check if a configuration key exists."""
        return key in self._config
    
    def to_dict(self) -> Dict[str, Any]:
        """Return the current configuration as a dictionary."""
        return self._config.copy()
