"""
Module to load project configurations
"""
import json
import os


def load_config(config_path="config.json"):
    """
    Load JSON configuration file
    
    Args:
        config_path (str): Path to configuration file
        
    Returns:
        dict: Loaded configurations
        
    Raises:
        FileNotFoundError: If file does not exist
        json.JSONDecodeError: If JSON is invalid
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return config


def validate_config(config):
    """
    Validate if required configurations are present
    
    Args:
        config (dict): Configurations to validate
        
    Returns:
        bool: True if valid
        
    Raises:
        ValueError: If required configuration is missing
    """
    required_keys = ["model", "video_input_directory", "video_output_directory", "video_extensions", "image_input_directory", "image_output_directory"]
    
    for key in required_keys:
        if key not in config:
            raise ValueError(f"Required configuration missing: {key}")
    
    return True
