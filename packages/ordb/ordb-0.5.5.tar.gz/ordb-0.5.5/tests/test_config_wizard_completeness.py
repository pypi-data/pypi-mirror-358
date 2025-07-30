#!/usr/bin/env python3
"""
Test that config wizard covers all settings in SearchConfig.

This test ensures that the config wizard includes prompts for all settings
that are loaded by SearchConfig.load_config() method, preventing missing
configuration options in the wizard.
"""

import unittest
import configparser
import re
from pathlib import Path


class TestConfigWizardCompleteness(unittest.TestCase):
    """Test config wizard completeness against SearchConfig."""
    
    def setUp(self):
        """Set up test environment."""
        self.config_py_path = Path(__file__).parent.parent / 'src' / 'ordb' / 'config.py'
        self.wizard_py_path = Path(__file__).parent.parent / 'src' / 'ordb' / 'wizard.py'
    
    def extract_searchconfig_settings(self):
        """Extract all settings that SearchConfig reads from the config file."""
        settings = set()
        
        # Read the config.py file
        with open(self.config_py_path, 'r') as f:
            content = f.read()
        
        # Find all patterns where config['search'] is accessed
        # Pattern 1: if 'setting_name' in config['search']:
        pattern1 = re.findall(r"if\s+'(\w+)'\s+in\s+config\['search'\]", content)
        settings.update(pattern1)
        
        # Pattern 2: config['search'].getboolean('setting_name'
        pattern2 = re.findall(r"config\['search'\]\.getboolean\('(\w+)'", content)
        settings.update(pattern2)
        
        # Pattern 3: config['search']['setting_name']
        pattern3 = re.findall(r"config\['search'\]\['(\w+)'\]", content)
        settings.update(pattern3)
        
        # Also check default initialization in __init__
        # Pattern: self.setting_name = value
        init_section = re.search(r'class SearchConfig:.*?def load_config', content, re.DOTALL)
        if init_section:
            init_content = init_section.group(0)
            # Find self.setting_name assignments
            pattern4 = re.findall(r'self\.(\w+)\s*=\s*[^=]', init_content)
            # Filter out methods and internal attributes
            config_attrs = [attr for attr in pattern4 if not attr.startswith('_') and attr != 'load_config']
            settings.update(config_attrs)
        
        return settings
    
    def extract_wizard_settings(self):
        """Extract all settings that the config wizard prompts for."""
        settings = set()
        
        # Read the wizard.py file
        with open(self.wizard_py_path, 'r') as f:
            content = f.read()
        
        # Find settings list in configure_search function
        # The settings is a multi-line list that ends at the for loop
        search_section = re.search(r'settings\s*=\s*\[(.*?)\]\s*\n.*?for setting, description, setting_type, default in settings:', content, re.DOTALL)
        if search_section:
            settings_content = search_section.group(1)
            # Extract setting names from tuples - they appear as first element in each tuple
            pattern = re.findall(r"\(\s*['\"](\w+)['\"]", settings_content)
            settings.update(pattern)
        
        return settings
    
    def test_wizard_covers_all_settings(self):
        """Test that config wizard covers all SearchConfig settings."""
        config_settings = self.extract_searchconfig_settings()
        wizard_settings = self.extract_wizard_settings()
        
        # Remove any settings that are programmatically set or internal
        # Also remove deprecated settings that have been renamed but kept for backward compatibility
        internal_settings = {'fuzzy_results_limit'}  # Renamed to interactive_results_limit
        config_settings = config_settings - internal_settings
        
        # Check that wizard covers all config settings
        missing_in_wizard = config_settings - wizard_settings
        extra_in_wizard = wizard_settings - config_settings
        
        # Report findings
        if missing_in_wizard:
            self.fail(f"Config wizard is missing these settings: {sorted(missing_in_wizard)}")
        
        # It's OK to have extra settings in wizard (for future compatibility)
        # but we'll note them
        if extra_in_wizard:
            print(f"Note: Config wizard has extra settings (OK): {sorted(extra_in_wizard)}")
        
        # Ensure we found some settings (sanity check)
        self.assertGreater(len(config_settings), 5, "Should find at least 5 config settings")
        self.assertGreater(len(wizard_settings), 5, "Should find at least 5 wizard settings")
    
    def test_wizard_generates_all_settings(self):
        """Test that save_config function includes all settings."""
        # Read the wizard.py file
        with open(self.wizard_py_path, 'r') as f:
            content = f.read()
        
        # Find all config.get('search', 'setting') references in save_config function
        # Look for the pattern throughout the file since save_config is very long
        saved_settings = set()
        pattern = re.findall(r"\{config\.get\('search',\s*'(\w+)'", content)
        saved_settings.update(pattern)
        
        # Sanity check - should find at least some settings
        if not saved_settings:
            self.fail("Could not find any config.get('search', ...) patterns in wizard.py")
        
        # Get wizard settings
        wizard_settings = self.extract_wizard_settings()
        
        # Check that all wizard settings are saved
        missing_in_save = wizard_settings - saved_settings
        
        if missing_in_save:
            self.fail(f"save_config is missing these wizard settings: {sorted(missing_in_save)}")


if __name__ == '__main__':
    unittest.main()