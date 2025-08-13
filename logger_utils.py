import logging
import configparser
import os

def setup_logging_from_config(config_file="config.ini"):
    """
    Configure logging based on settings in config file.
    
    Args:
        config_file (str): Path to the configuration file.
    """
    # Set default values
    log_level = "INFO"
    
    # Try to read from config file
    if os.path.exists(config_file):
        config = configparser.ConfigParser()
        config.read(config_file)
        
        if config.has_section('logging'):
            log_level = config.get('logging', 'level', fallback=log_level)
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    
    # Configure logging with a simple format
    logging.basicConfig(
        level=numeric_level,
        format='%(levelname)s: %(message)s'
    )