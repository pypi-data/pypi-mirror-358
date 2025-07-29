# src/diagram_to_iac/core/config_loader.py
"""
Central configuration loader for diagram-to-iac project.
Handles loading and merging configuration from multiple sources with environment variable overrides.
"""

import os
import yaml
import logging
from pathlib import Path
from typing import Dict, Any, Optional, Union
from functools import lru_cache

logger = logging.getLogger(__name__)

class ConfigLoader:
    """
    Central configuration management for the diagram-to-iac project.
    Loads configuration from YAML files and provides environment variable override capability.
    """
    
    def __init__(self, app_config_path: Optional[str] = None, system_config_path: Optional[str] = None):
        """
        Initialize ConfigLoader with optional custom config paths.
        
        Args:
            app_config_path: Path to application config file (default: src/diagram_to_iac/config.yaml)
            system_config_path: Path to system config file (default: config/system.yaml)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        
        # Set default paths
        self.base_path = Path(__file__).parent.parent.parent.parent  # diagram-to-iac root
        self.app_config_path = Path(app_config_path) if app_config_path else self.base_path / "src" / "diagram_to_iac" / "config.yaml"
        self.system_config_path = Path(system_config_path) if system_config_path else self.base_path / "config" / "system.yaml"
        
        # Cache for loaded configs
        self._app_config = None
        self._system_config = None
        self._merged_config = None
    
    @lru_cache(maxsize=1)
    def get_config(self) -> Dict[str, Any]:
        """
        Get the complete merged configuration with environment variable overrides.
        
        Returns:
            Merged configuration dictionary
        """
        if self._merged_config is None:
            self._merged_config = self._load_and_merge_configs()
        return self._merged_config
    
    def _load_and_merge_configs(self) -> Dict[str, Any]:
        """
        Load and merge all configuration sources.
        
        Returns:
            Merged configuration dictionary
        """
        # Load base configs
        app_config = self._load_app_config()
        system_config = self._load_system_config()
        
        # Start with system config as base, overlay app config
        merged = self._deep_merge(system_config, app_config)
        
        # Apply environment variable overrides
        merged = self._apply_env_overrides(merged)
        
        self.logger.debug("Configuration loaded and merged successfully")
        return merged
    
    def _load_app_config(self) -> Dict[str, Any]:
        """Load application configuration from YAML file."""
        if self._app_config is None:
            try:
                if self.app_config_path.exists():
                    with open(self.app_config_path, 'r') as f:
                        self._app_config = yaml.safe_load(f) or {}
                    self.logger.debug(f"Loaded app config from {self.app_config_path}")
                else:
                    self.logger.warning(f"App config file not found: {self.app_config_path}")
                    self._app_config = {}
            except Exception as e:
                self.logger.error(f"Failed to load app config: {e}")
                self._app_config = {}
        return self._app_config
    
    def _load_system_config(self) -> Dict[str, Any]:
        """Load system configuration from YAML file."""
        if self._system_config is None:
            try:
                if self.system_config_path.exists():
                    with open(self.system_config_path, 'r') as f:
                        self._system_config = yaml.safe_load(f) or {}
                    self.logger.debug(f"Loaded system config from {self.system_config_path}")
                else:
                    self.logger.warning(f"System config file not found: {self.system_config_path}")
                    self._system_config = {}
            except Exception as e:
                self.logger.error(f"Failed to load system config: {e}")
                self._system_config = {}
        return self._system_config
    
    def _deep_merge(self, base: Dict[str, Any], overlay: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries, with overlay taking precedence.
        
        Args:
            base: Base dictionary
            overlay: Dictionary to overlay on base
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in overlay.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Apply environment variable overrides to configuration.
        Environment variables should be in the format: DIAGRAM_TO_IAC_<SECTION>_<KEY>
        
        Args:
            config: Base configuration dictionary
            
        Returns:
            Configuration with environment overrides applied
        """
        result = config.copy()
        env_prefix = "DIAGRAM_TO_IAC_"
        
        # Get list of allowed overrides from config
        allowed_overrides = config.get("environment_overrides", {}).get("allowed_overrides", [])
        
        for env_var, env_value in os.environ.items():
            if not env_var.startswith(env_prefix):
                continue
                
            # Parse environment variable name
            # e.g., DIAGRAM_TO_IAC_NETWORK_API_TIMEOUT -> network.api_timeout
            var_path = env_var[len(env_prefix):].lower().replace('_', '.')
            
            # Check if override is allowed
            if var_path not in allowed_overrides:
                self.logger.debug(f"Environment override not allowed: {var_path}")
                continue
            
            # Convert string value to appropriate type
            converted_value = self._convert_env_value(env_value)
            
            # Apply override to config
            self._set_nested_value(result, var_path, converted_value)
            self.logger.debug(f"Applied environment override: {var_path} = {converted_value}")
        
        return result
    
    def _convert_env_value(self, value: str) -> Union[str, int, float, bool]:
        """
        Convert environment variable string value to appropriate type.
        
        Args:
            value: String value from environment variable
            
        Returns:
            Converted value
        """
        # Handle boolean values
        if value.lower() in ("true", "yes", "1", "on"):
            return True
        elif value.lower() in ("false", "no", "0", "off"):
            return False
        
        # Handle numeric values
        try:
            if '.' in value:
                return float(value)
            else:
                return int(value)
        except ValueError:
            pass
        
        # Return as string
        return value
    
    def _set_nested_value(self, config: Dict[str, Any], path: str, value: Any) -> None:
        """
        Set a nested value in configuration using dot notation.
        
        Args:
            config: Configuration dictionary to modify
            path: Dot-separated path (e.g., "network.api_timeout")
            value: Value to set
        """
        keys = path.split('.')
        current = config
        
        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        
        # Set the final value
        current[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get a specific configuration section.
        
        Args:
            section: Section name (e.g., "network", "ai", "routing")
            
        Returns:
            Configuration section dictionary
        """
        return self.get_config().get(section, {})
    
    def get_value(self, path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation.
        
        Args:
            path: Dot-separated path (e.g., "network.api_timeout")
            default: Default value if path not found
            
        Returns:
            Configuration value or default
        """
        keys = path.split('.')
        current = self.get_config()
        
        try:
            for key in keys:
                current = current[key]
            return current
        except (KeyError, TypeError):
            return default
    
    def reload(self) -> None:
        """Reload configuration from files (clears cache)."""
        self._app_config = None
        self._system_config = None
        self._merged_config = None
        self.get_config.cache_clear()
        self.logger.debug("Configuration cache cleared, will reload on next access")


# Global configuration loader instance
_config_loader = None

def get_config_loader() -> ConfigLoader:
    """Get the global configuration loader instance."""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigLoader()
    return _config_loader

def get_config() -> Dict[str, Any]:
    """Get the complete merged configuration."""
    return get_config_loader().get_config()

def get_config_section(section: str) -> Dict[str, Any]:
    """Get a specific configuration section."""
    return get_config_loader().get_section(section)

def get_config_value(path: str, default: Any = None) -> Any:
    """Get a configuration value using dot notation."""
    return get_config_loader().get_value(path, default)

def reload_config() -> None:
    """Reload configuration from files."""
    get_config_loader().reload()
