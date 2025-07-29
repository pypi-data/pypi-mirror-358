#!/usr/bin/env python3
"""
Interactive configuration wizard for Norwegian dictionary search (ordb).
This wizard helps users configure their ordb settings, saving to ~/.ordb/config.
"""

import os
import sys
import configparser
from pathlib import Path
from .config import get_config_dir

# Color codes for the wizard interface
class WizardColors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    END = '\033[0m'
    GRAY = '\033[90m'

def load_current_config():
    """Load the current configuration file."""
    # Check locations in same order as SearchConfig
    config_dirs = [
        get_config_dir() / 'config',
        Path.home() / '.config-ordb',
        Path.home() / '.config-bm'
    ]
    
    config = configparser.ConfigParser()
    
    # Try to load existing config
    for config_path in config_dirs:
        if config_path.exists():
            config.read(config_path)
            break
    
    # Set defaults if sections don't exist
    if 'colors' not in config:
        config.add_section('colors')
    if 'search' not in config:
        config.add_section('search')
    
    return config

def save_config(config):
    """Save configuration to the appropriate location with all defaults and comments."""
    config_dir = get_config_dir()
    config_dir.mkdir(parents=True, exist_ok=True)
    config_path = config_dir / 'config'
    
    # Create a comprehensive config file with defaults and comments
    config_content = f"""# ordb Configuration File
# This file configures the Norwegian dictionary search tool (ordb)
# Edit these settings to customize your search experience

[colors]
# Terminal colors for different elements
# Available colors: black, red, green, yellow, blue, magenta, cyan, white,
#                  bright_red, bright_green, bright_yellow, bright_blue,
#                  bright_magenta, bright_cyan, bright_white
# Use 'none' for no color

# Main word entries
lemma = {config.get('colors', 'lemma', fallback='cyan')}

# Word type labels ([noun], [verb], etc.)
word_class = {config.get('colors', 'word_class', fallback='yellow')}

# Definition text
definition = {config.get('colors', 'definition', fallback='none')}

# Example sentences
example = {config.get('colors', 'example', fallback='cyan')}

# Etymology information
etymology = {config.get('colors', 'etymology', fallback='gray')}

# Gender colors
masculine = {config.get('colors', 'masculine', fallback='blue')}
feminine = {config.get('colors', 'feminine', fallback='red')}
neuter = {config.get('colors', 'neuter', fallback='green')}

# Highlight color for fuzzy search matches
highlight = {config.get('colors', 'highlight', fallback='green')}

[search]
# Character replacement settings
# Convert aa→å, oe→ø, ae→æ automatically in searches
character_replacement = {config.get('search', 'character_replacement', fallback='true')}

# Default maximum number of results to show
default_limit = {config.get('search', 'default_limit', fallback='50')}

# Display settings
# Show inflection tables in entries
show_inflections = {config.get('search', 'show_inflections', fallback='true')}

# Show etymology information in entries
show_etymology = {config.get('search', 'show_etymology', fallback='true')}

# Pagination settings
# Enable pagination for long outputs
pagination = {config.get('search', 'pagination', fallback='true')}

# Lines per page (0 = auto-detect based on terminal size)
page_size = {config.get('search', 'page_size', fallback='20')}

# Maximum results when pagination is enabled (0 = no limit)
limit_with_pagination = {config.get('search', 'limit_with_pagination', fallback='500')}

# Clear screen when showing paginated results
clear_screen = {config.get('search', 'clear_screen', fallback='true')}

# Interactive search settings
# Maximum results in interactive lettered lists (fuzzy, prefix, anywhere searches)
interactive_results_limit = {config.get('search', 'interactive_results_limit', fallback='15')}

# Use fuzzy search as fallback when no exact matches found
fallback_to_fuzzy = {config.get('search', 'fallback_to_fuzzy', fallback='true')}

# Use interactive menus for @ searches (prefix and anywhere term searches)
interactive_anywhere_search = {config.get('search', 'interactive_anywhere_search', fallback='true')}
"""
    
    with open(config_path, 'w') as f:
        f.write(config_content)

def show_welcome():
    """Display welcome message and ASCII art."""
    print(f"""
{WizardColors.CYAN}{WizardColors.BOLD}
╔═══════════════════════════════════════════════════════════╗
║                                                           ║
║          📖 ordb Configuration Wizard 📖                  ║
║                                                           ║
║       Norwegian bokmål Dictionary Search Tool             ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
{WizardColors.END}

{WizardColors.GRAY}This wizard will help you configure ordb settings including:
• Terminal colors for different word types
• Search behavior and limits
• Display preferences{WizardColors.END}

Press {WizardColors.BOLD}Enter{WizardColors.END} to continue, or {WizardColors.BOLD}Ctrl+C{WizardColors.END} to cancel...
""")
    input()

def configure_colors(config):
    """Configure color settings."""
    print(f"\n{WizardColors.HEADER}{WizardColors.BOLD}🎨 Color Configuration{WizardColors.END}")
    print(f"{WizardColors.GRAY}Configure terminal colors for different elements.{WizardColors.END}")
    
    color_options = {
        '1': ('black', '30'),
        '2': ('red', '31'),
        '3': ('green', '32'),
        '4': ('yellow', '33'),
        '5': ('blue', '34'),
        '6': ('magenta', '35'),
        '7': ('cyan', '36'),
        '8': ('white', '37'),
        '9': ('bright_red', '91'),
        '10': ('bright_green', '92'),
        '11': ('bright_yellow', '93'),
        '12': ('bright_blue', '94'),
        '13': ('bright_magenta', '95'),
        '14': ('bright_cyan', '96'),
        '15': ('bright_white', '97'),
        '0': ('default', '')
    }
    
    def show_colors():
        print(f"\n{WizardColors.BOLD}Available colors:{WizardColors.END}")
        
        # Group colors into rows for compact display
        row1 = [(k, v) for k, v in color_options.items() if k in ['1', '2', '3', '4', '5', '6', '7', '8']]
        row2 = [(k, v) for k, v in color_options.items() if k in ['9', '10', '11', '12', '13', '14', '15', '0']]
        
        # Display first row (basic colors)
        print("  ", end="")
        for key, (name, code) in row1:
            if code:
                print(f"{key}:\033[{code}m{name.title():>8}\033[0m", end="  ")
            else:
                print(f"{key}:{name.title():>8}", end="  ")
        print()  # New line
        
        # Display second row (bright colors + default)
        print("  ", end="")
        for key, (name, code) in row2:
            name_display = name.replace('bright_', '').replace('_', ' ').title()
            if key == '0':
                name_display = 'Default'
            if code:
                print(f"{key}:\033[{code}m{name_display:>8}\033[0m", end="  ")
            else:
                print(f"{key}:{name_display:>8}", end="  ")
        print()  # New line
    
    elements = [
        ('lemma', 'Main dictionary entries (words)'),
        ('word_class', 'Word type labels [noun], [verb], etc.'),
        ('definition', 'Definition text'),
        ('example', 'Example sentences'),
        ('etymology', 'Etymology information'),
        ('masculine', 'Masculine gender'),
        ('feminine', 'Feminine gender'),
        ('neuter', 'Neuter gender')
    ]
    
    print(f"\n{WizardColors.CYAN}Configure colors for different text elements:{WizardColors.END}")
    
    for element, description in elements:
        show_colors()
        
        current = config.get('colors', element, fallback='')
        current_name = next((name for code, (name, _) in color_options.items() if _ == current), 'default')
        
        print(f"\n{WizardColors.BOLD}{description}{WizardColors.END}")
        print(f"Current: {current_name}")
        
        while True:
            choice = input(f"Enter color number (0-15, or Enter to keep current): ").strip()
            
            if choice == '':
                break
            elif choice in color_options:
                color_name, color_code = color_options[choice]
                config.set('colors', element, color_code)
                print(f"Set to: \033[{color_code}m{color_name.replace('_', ' ').title()}\033[0m")
                break
            else:
                print(f"{WizardColors.RED}Invalid choice. Please enter a number 0-15.{WizardColors.END}")

def configure_search(config):
    """Configure search settings."""
    print(f"\n{WizardColors.HEADER}{WizardColors.BOLD}🔍 Search Configuration{WizardColors.END}")
    print(f"{WizardColors.GRAY}Configure search behavior and display options.{WizardColors.END}")
    
    settings = [
        ('character_replacement', 'Enable automatic character replacement (aa→å, oe→ø, ae→æ)', 'boolean', True),
        ('default_limit', 'Default maximum results to show', 'integer', 20),
        ('pagination', 'Enable pagination for long results', 'boolean', True),
        ('page_size', 'Lines per page (0 = auto-detect)', 'integer', 0),
        ('limit_with_pagination', 'Max results with pagination (0 = no limit)', 'integer', 100),
        ('show_inflections', 'Show inflection tables by default', 'boolean', True),
        ('show_etymology', 'Show etymology information by default', 'boolean', True),
        ('interactive_results_limit', 'Maximum results in interactive lists', 'integer', 15),
        ('fallback_to_fuzzy', 'Use fuzzy search when no exact matches found', 'boolean', True),
        ('interactive_anywhere_search', 'Use interactive menus for @ searches', 'boolean', True),
        ('clear_screen', 'Clear screen when showing paginated results', 'boolean', True)
    ]
    
    print(f"\n{WizardColors.CYAN}Configure search settings:{WizardColors.END}")
    
    for setting, description, setting_type, default in settings:
        current = config.get('search', setting, fallback=str(default))
        
        print(f"\n{WizardColors.BOLD}{description}{WizardColors.END}")
        print(f"Current: {current}")
        
        if setting_type == 'boolean':
            while True:
                choice = input(f"Enable? [y/n] (Enter to keep current): ").strip().lower()
                if choice == '':
                    break
                elif choice in ('y', 'yes', 'true', '1'):
                    config.set('search', setting, 'True')
                    print("Set to: True")
                    break
                elif choice in ('n', 'no', 'false', '0'):
                    config.set('search', setting, 'False')
                    print("Set to: False")
                    break
                else:
                    print(f"{WizardColors.RED}Please enter y/n{WizardColors.END}")
        
        elif setting_type == 'integer':
            while True:
                choice = input(f"Enter value (Enter to keep current): ").strip()
                if choice == '':
                    break
                try:
                    value = int(choice)
                    if value >= 0:
                        config.set('search', setting, str(value))
                        print(f"Set to: {value}")
                        break
                    else:
                        print(f"{WizardColors.RED}Please enter a non-negative number{WizardColors.END}")
                except ValueError:
                    print(f"{WizardColors.RED}Please enter a valid number{WizardColors.END}")

def run_config_wizard():
    """Main configuration wizard function."""
    show_welcome()
    
    # Load current configuration
    config = load_current_config()
    
    # Configure each section
    try:
        configure_colors(config)
        configure_search(config)
        
        # Confirm and save
        print(f"\n{WizardColors.BOLD}Configuration Summary:{WizardColors.END}")
        print("Your configuration is ready to be saved.")
        
        save_choice = input(f"\nSave configuration? [Y/n]: ").strip().lower()
        if save_choice in ('', 'y', 'yes'):
            save_config(config)
            config_path = get_config_dir() / 'config'
            print(f"{WizardColors.GREEN}✓ Configuration saved to {config_path}{WizardColors.END}")
            print("You can now use ordb with your new settings!")
        else:
            print(f"{WizardColors.YELLOW}Configuration not saved.{WizardColors.END}")
    
    except KeyboardInterrupt:
        print(f"\n{WizardColors.YELLOW}Configuration wizard cancelled.{WizardColors.END}")
        sys.exit(1)
    except Exception as e:
        print(f"{WizardColors.RED}Error: {e}{WizardColors.END}")
        sys.exit(1)

def main():
    """Entry point for standalone execution."""
    run_config_wizard()

if __name__ == "__main__":
    main()