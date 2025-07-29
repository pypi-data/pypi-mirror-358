"""Configuration management for ordb."""

import configparser
import os
from pathlib import Path

def get_config_dir():
    """Get the platform-appropriate config directory."""
    if os.name == 'nt':  # Windows
        # Use APPDATA environment variable, fallback to USERPROFILE
        config_base = os.environ.get('APPDATA')
        if not config_base:
            config_base = os.environ.get('USERPROFILE')
        if not config_base:
            config_base = Path.home()
        else:
            config_base = Path(config_base)
        return config_base / 'ordb'
    else:  # Unix-like (Linux, macOS, etc.)
        return Path.home() / '.ordb'


def get_data_dir():
    """Get the platform-appropriate data directory."""
    if os.name == 'nt':  # Windows
        # Use LOCALAPPDATA for data files
        data_base = os.environ.get('LOCALAPPDATA')
        if not data_base:
            data_base = os.environ.get('APPDATA')
        if not data_base:
            data_base = os.environ.get('USERPROFILE')
        if not data_base:
            data_base = Path.home()
        else:
            data_base = Path(data_base)
        return data_base / 'ordb'
    else:  # Unix-like (Linux, macOS, etc.)
        return Path.home() / '.ordb'


def get_config_path():
    """Get the path to the configuration file."""
    # Primary location (platform-appropriate)
    primary_config = get_config_dir() / 'config'
    
    # Check if config exists
    if primary_config.exists():
        return primary_config
    
    return None


# Default ANSI color codes
DEFAULT_COLORS = {
    'HEADER': '\033[95m',
    'BLUE': '\033[94m',
    'CYAN': '\033[96m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'RED': '\033[91m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'END': '\033[0m',
    'GRAY': '\033[90m',
    'PURPLE': '\033[35m',
    'BLACK': '\033[30m',
    'WHITE': '\033[97m',
    'DEFAULT': ''
}

# Color mapping from config names to ANSI codes
COLOR_MAP = {
    'BLACK': '\033[30m',
    'RED': '\033[91m',
    'GREEN': '\033[92m',
    'YELLOW': '\033[93m',
    'BLUE': '\033[94m',
    'PURPLE': '\033[95m',
    'CYAN': '\033[96m',
    'WHITE': '\033[97m',
    'GRAY': '\033[90m',
    'BOLD': '\033[1m',
    'UNDERLINE': '\033[4m',
    'DEFAULT': '',
    'BOLD_RED': '\033[1m\033[91m',
    'BOLD_GREEN': '\033[1m\033[92m',
    'BOLD_YELLOW': '\033[1m\033[93m',
    'BOLD_BLUE': '\033[1m\033[94m',
    'BOLD_PURPLE': '\033[1m\033[95m',
    'BOLD_CYAN': '\033[1m\033[96m',
    'UNDERLINE_RED': '\033[4m\033[91m',
    'UNDERLINE_GREEN': '\033[4m\033[92m',
    'UNDERLINE_BLUE': '\033[4m\033[94m'
}

class Colors:
    """Color codes for terminal output. Can be customized via .config-bm file."""
    def __init__(self):
        # Set defaults
        for key, value in DEFAULT_COLORS.items():
            setattr(self, key, value)
        
        # Add semantic color attributes with defaults
        self.LEMMA = self.CYAN
        self.WORD_CLASS = self.YELLOW
        self.MASCULINE = self.BLUE
        self.FEMININE = self.RED
        self.NEUTER = self.GREEN
        self.DEFINITION = ''  # No color
        self.EXAMPLE = self.CYAN
        self.HIGHLIGHT = self.GREEN
        self.ETYMOLOGY = self.GRAY
        self.INFLECTION_LABEL = self.GRAY
        self.ERROR = self.RED
        self.WARNING = self.YELLOW
        self.INFO = self.GRAY
        self.SUCCESS = self.GREEN
        
        # Load custom colors from config
        self.load_config()
    
    def load_config(self):
        """Load color configuration from config file."""
        # Get config file path
        config_path = get_config_path()
        
        if not config_path:
            return
        
        config = configparser.ConfigParser()
        try:
            config.read(config_path)
            
            if 'colors' not in config:
                return
            
            color_settings = config['colors']
            
            # Map config color names to our color attributes
            mapping = {
                'header': 'HEADER',
                'lemma': 'LEMMA',
                'bold': 'BOLD',
                'word_class': 'WORD_CLASS',
                'masculine': 'MASCULINE',
                'feminine': 'FEMININE',
                'neuter': 'NEUTER',
                'definition': 'DEFINITION',
                'example': 'EXAMPLE',
                'highlight': 'HIGHLIGHT',
                'etymology': 'ETYMOLOGY',
                'inflection_label': 'INFLECTION_LABEL',
                'error': 'ERROR',
                'warning': 'WARNING',
                'info': 'INFO',
                'success': 'SUCCESS'
            }
            
            for config_name, attr_name in mapping.items():
                if config_name in color_settings:
                    color_value = color_settings[config_name].strip().upper()
                    if color_value in COLOR_MAP:
                        setattr(self, attr_name, COLOR_MAP[color_value])
        
        except Exception:
            # Silently ignore config errors and use defaults
            pass

class SearchConfig:
    """Manage search configuration settings."""
    def __init__(self):
        # Default values
        self.character_replacement = True
        self.default_limit = 50
        self.show_inflections = True
        self.show_etymology = True
        self.pagination = True
        self.page_size = 20
        self.limit_with_pagination = 500
        self.clear_screen = True
        self.interactive_results_limit = 15
        self.fallback_to_fuzzy = True
        self.interactive_anywhere_search = True
        
        # Load from config
        self.load_config()
    
    def load_config(self):
        """Load search settings from config file."""
        try:
            # Get config file path
            config_path = get_config_path()
            
            if not config_path:
                return
                
            config = configparser.ConfigParser()
            config.read(config_path)
            
            if 'search' in config:
                # Character replacement setting
                if 'character_replacement' in config['search']:
                    self.character_replacement = config['search'].getboolean('character_replacement', True)
                
                # Default limit setting
                if 'default_limit' in config['search']:
                    try:
                        value = config['search']['default_limit'].split('#')[0].strip()
                        self.default_limit = int(value)
                    except ValueError:
                        pass
                
                # Display options
                if 'show_inflections' in config['search']:
                    self.show_inflections = config['search'].getboolean('show_inflections', True)
                
                if 'show_etymology' in config['search']:
                    self.show_etymology = config['search'].getboolean('show_etymology', True)
                
                # Pagination settings
                if 'pagination' in config['search']:
                    self.pagination = config['search'].getboolean('pagination', True)
                
                if 'page_size' in config['search']:
                    try:
                        value = config['search']['page_size'].split('#')[0].strip()
                        self.page_size = int(value)
                    except ValueError:
                        pass
                
                if 'limit_with_pagination' in config['search']:
                    try:
                        value = config['search']['limit_with_pagination'].split('#')[0].strip()
                        self.limit_with_pagination = int(value)
                    except ValueError:
                        pass
                
                if 'clear_screen' in config['search']:
                    self.clear_screen = config['search'].getboolean('clear_screen', True)
                
                # Interactive results limit (with backward compatibility)
                if 'interactive_results_limit' in config['search']:
                    try:
                        value = config['search']['interactive_results_limit'].split('#')[0].strip()
                        self.interactive_results_limit = int(value)
                    except ValueError:
                        pass
                elif 'fuzzy_results_limit' in config['search']:
                    # Backward compatibility
                    try:
                        value = config['search']['fuzzy_results_limit'].split('#')[0].strip()
                        self.interactive_results_limit = int(value)
                    except ValueError:
                        pass
                
                if 'fallback_to_fuzzy' in config['search']:
                    self.fallback_to_fuzzy = config['search'].getboolean('fallback_to_fuzzy', True)
                
                if 'interactive_anywhere_search' in config['search']:
                    self.interactive_anywhere_search = config['search'].getboolean('interactive_anywhere_search', True)
        except:
            # If anything goes wrong, just use defaults
            pass

def apply_character_replacement(query):
    """Apply character replacements if enabled in config.
    
    Replaces:
    - aa → å
    - oe → ø  
    - ae → æ
    
    Returns a list of query variants to try.
    """
    if not search_config.character_replacement:
        return [query]
    
    variants = [query]
    
    # Create variants with replacements
    replacements = [
        ('aa', 'å'),
        ('oe', 'ø'),
        ('ae', 'æ'),
        # Also try uppercase versions
        ('AA', 'Å'),
        ('Aa', 'Å'),
        ('OE', 'Ø'),
        ('Oe', 'Ø'),
        ('AE', 'Æ'),
        ('Ae', 'Æ')
    ]
    
    for old, new in replacements:
        if old in query:
            variant = query.replace(old, new)
            if variant not in variants:
                variants.append(variant)
    
    return variants

def run_wizard():
    """Run the configuration wizard."""
    import subprocess
    import sys
    subprocess.run([sys.executable, 'config-wizard.py'])

# Initialize singletons
Colors = Colors()
search_config = SearchConfig()