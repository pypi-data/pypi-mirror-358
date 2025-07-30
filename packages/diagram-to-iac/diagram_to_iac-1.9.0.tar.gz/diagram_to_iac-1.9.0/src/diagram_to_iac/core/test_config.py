"""
Configuration loader for diagram-to-iac tests.

This module provides utilities to load test configuration from the main config.yaml file,
making test repository URLs and other test settings configurable and centralized.
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any


def load_test_config() -> Dict[str, Any]:
    """
    Load test configuration from the main config.yaml file.
    
    Returns:
        Dict containing test configuration settings
    """
    # Find the config file relative to this module
    # The config.yaml is at src/diagram_to_iac/config.yaml
    # This file is at src/diagram_to_iac/core/test_config.py
    # So we need to go up one directory
    current_dir = Path(__file__).parent
    config_path = current_dir.parent / "config.yaml"
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found at {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    return config.get('test', {})


def get_test_repo_url() -> str:
    """
    Get the test repository URL from configuration.
    
    Returns:
        The configured test repository URL
    """
    config = load_test_config()
    return config.get('github', {}).get('test_repo_url', 'https://github.com/amartyamandal/test_iac_agent_private.git')


def get_test_repo_owner() -> str:
    """
    Get the test repository owner from configuration.
    
    Returns:
        The configured test repository owner
    """
    config = load_test_config()
    return config.get('github', {}).get('test_repo_owner', 'amartyamandal')


def get_test_repo_name() -> str:
    """
    Get the test repository name from configuration.
    
    Returns:
        The configured test repository name
    """
    config = load_test_config()
    return config.get('github', {}).get('test_repo_name', 'test_iac_agent_private')


def get_public_test_repo_url() -> str:
    """
    Get the public test repository URL from configuration.
    
    Returns:
        The configured public test repository URL
    """
    config = load_test_config()
    return config.get('github', {}).get('public_test_repo_url', 'https://github.com/amartyamandal/test_iac_agent_public.git')


def should_skip_integration_tests() -> bool:
    """
    Check if integration tests should be skipped when no GitHub token is available.
    
    Returns:
        True if integration tests should be skipped without a token
    """
    config = load_test_config()
    return config.get('settings', {}).get('skip_integration_tests_without_token', True)


def should_use_real_github_api() -> bool:
    """
    Check if tests should use real GitHub API calls.
    
    Returns:
        True if real GitHub API calls should be used
    """
    config = load_test_config()
    return config.get('settings', {}).get('use_real_github_api', False)


def should_mock_network_calls() -> bool:
    """
    Check if network calls should be mocked by default.
    
    Returns:
        True if network calls should be mocked
    """
    config = load_test_config()
    return config.get('settings', {}).get('mock_network_calls', True)


# Convenience function for backwards compatibility
def get_test_github_repo() -> str:
    """
    Get the test GitHub repository URL.
    Alias for get_test_repo_url() for backwards compatibility.
    
    Returns:
        The configured test repository URL
    """
    return get_test_repo_url()
