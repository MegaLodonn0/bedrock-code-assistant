"""Configuration loading and management"""

import json
import os
from pathlib import Path


class ConfigError(Exception):
    """Configuration loading error"""
    pass


class Config:
    """Load and manage configuration from JSON file"""
    
    def __init__(self, config_path: str = None):
        """
        Initialize configuration loader.
        
        Args:
            config_path: Path to config.json file. If None, uses default location.
        """
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config.json"
        
        self.config_path = Path(config_path)
        self._config = None
        self._load_config()
    
    def _load_config(self):
        """Load configuration from JSON file"""
        if not self.config_path.exists():
            raise ConfigError(
                f"Configuration file not found: {self.config_path}\n"
                f"Please copy config.example.json to config.json and fill in your credentials."
            )
        
        try:
            with open(self.config_path, 'r') as f:
                self._config = json.load(f)
        except json.JSONDecodeError as e:
            raise ConfigError(f"Invalid JSON in config file: {e}")
        except Exception as e:
            raise ConfigError(f"Failed to load config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value using dot notation"""
        keys = key.split('.')
        value = self._config
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    @property
    def aws(self):
        """Get AWS configuration"""
        return self._config.get('aws', {})
    
    @property
    def bedrock(self):
        """Get Bedrock configuration"""
        return self._config.get('bedrock', {})
    
    @property
    def assistant(self):
        """Get Assistant configuration"""
        return self._config.get('assistant', {})


# Global config instance
_config = None


def get_config(config_path: str = None) -> Config:
    """Get or create global config instance"""
    global _config
    if _config is None:
        _config = Config(config_path)
    return _config
