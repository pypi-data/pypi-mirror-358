#!/usr/bin/env python3
"""
Unit tests for config.py module.
Tests configuration management functions.
"""

import unittest
import sys
import tempfile
import configparser
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src directory to path for testing
sys.path.insert(0, 'src')

from ordb.config import (
    get_config_dir, get_data_dir, get_config_path,
    apply_character_replacement, run_wizard, SearchConfig
)


class TestConfigFunctions(unittest.TestCase):
    """Test configuration management functions."""
    
    @patch('os.name', 'posix')
    @patch.dict('os.environ', {}, clear=True)
    def test_get_config_dir_unix(self):
        """Test get_config_dir on Unix systems."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/home/user')
            result = get_config_dir()
            self.assertEqual(result, Path('/home/user/.ordb'))
    
    @patch('os.name', 'nt')
    @patch.dict('os.environ', {'APPDATA': 'C:\\Users\\User\\AppData\\Roaming'})
    def test_get_config_dir_windows(self):
        """Test get_config_dir on Windows."""
        # Mock Path in the config module to avoid WindowsPath on Unix system
        with patch('ordb.config.Path') as mock_path:
            mock_config_base = MagicMock()
            mock_config_base.__truediv__ = MagicMock(return_value='C:\\Users\\User\\AppData\\Roaming\\ordb')
            mock_path.return_value = mock_config_base
            
            result = get_config_dir()
            
            # Should have called Path with the APPDATA value
            mock_path.assert_called_with('C:\\Users\\User\\AppData\\Roaming')
            # Should have done path / 'ordb'
            mock_config_base.__truediv__.assert_called_with('ordb')
    
    @patch('os.name', 'nt')
    @patch.dict('os.environ', {}, clear=True)
    def test_get_config_dir_windows_fallback(self):
        """Test get_config_dir on Windows without APPDATA."""
        with patch('ordb.config.Path') as mock_path:
            mock_home_result = MagicMock()
            mock_home_result.__truediv__ = MagicMock(return_value='C:\\Users\\User/ordb')
            mock_path.home.return_value = mock_home_result
            
            result = get_config_dir()
            
            # Should have called Path.home()
            mock_path.home.assert_called_once()
            # Should have done home_path / 'ordb'
            mock_home_result.__truediv__.assert_called_with('ordb')
    
    @patch('os.name', 'posix')
    @patch.dict('os.environ', {}, clear=True)
    def test_get_data_dir_unix(self):
        """Test get_data_dir on Unix systems."""
        with patch('pathlib.Path.home') as mock_home:
            mock_home.return_value = Path('/home/user')
            result = get_data_dir()
            self.assertEqual(result, Path('/home/user/.ordb'))
    
    @patch('os.name', 'nt')
    @patch.dict('os.environ', {'LOCALAPPDATA': 'C:\\Users\\User\\AppData\\Local'})
    def test_get_data_dir_windows(self):
        """Test get_data_dir on Windows."""
        # Mock Path in the config module to avoid WindowsPath on Unix system
        with patch('ordb.config.Path') as mock_path:
            mock_data_base = MagicMock()
            mock_data_base.__truediv__ = MagicMock(return_value='C:\\Users\\User\\AppData\\Local\\ordb')
            mock_path.return_value = mock_data_base
            
            result = get_data_dir()
            
            # Should have called Path with the LOCALAPPDATA value
            mock_path.assert_called_with('C:\\Users\\User\\AppData\\Local')
            # Should have done path / 'ordb'
            mock_data_base.__truediv__.assert_called_with('ordb')
    
    @patch('os.name', 'nt')
    @patch.dict('os.environ', {}, clear=True)
    def test_get_data_dir_windows_fallback(self):
        """Test get_data_dir on Windows without LOCALAPPDATA."""
        with patch('ordb.config.Path') as mock_path:
            mock_home_result = MagicMock()
            mock_home_result.__truediv__ = MagicMock(return_value='C:\\Users\\User/ordb')
            mock_path.home.return_value = mock_home_result
            
            result = get_data_dir()
            
            # Should have called Path.home()
            mock_path.home.assert_called_once()
            # Should have done home_path / 'ordb'
            mock_home_result.__truediv__.assert_called_with('ordb')
    
    def test_get_config_path_primary_exists(self):
        """Test get_config_path when primary config exists."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            primary_config = temp_path / 'config'
            primary_config.touch()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                mock_get_config_dir.return_value = temp_path
                result = get_config_path()
                self.assertEqual(result, primary_config)
    
    def test_get_config_path_not_exists(self):
        """Test get_config_path when config doesn't exist."""
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                mock_get_config_dir.return_value = temp_path / 'nonexistent'
                result = get_config_path()
                self.assertIsNone(result)


class TestCharacterReplacementFunctions(unittest.TestCase):
    """Test character replacement functions."""
    
    def test_apply_character_replacement_aa_to_a(self):
        """Test aa to å replacement."""
        result = apply_character_replacement("baade")
        self.assertIn("både", result)
        self.assertIsInstance(result, list)
    
    def test_apply_character_replacement_oe_to_o(self):
        """Test oe to ø replacement."""
        result = apply_character_replacement("kjoere")
        self.assertIn("kjøre", result)
        self.assertIsInstance(result, list)
    
    def test_apply_character_replacement_ae_to_ae(self):
        """Test ae to æ replacement."""
        result = apply_character_replacement("laere")
        self.assertIn("lære", result)
        self.assertIsInstance(result, list)
    
    def test_apply_character_replacement_multiple(self):
        """Test multiple replacements in one string."""
        result = apply_character_replacement("baade kjoere laere")
        # Should contain variants with different combinations
        self.assertIsInstance(result, list)
        self.assertIn("baade kjoere laere", result)  # Original
        # Should have variants with replacements
        variants_with_aa = [v for v in result if "både" in v]
        self.assertTrue(len(variants_with_aa) > 0)
    
    def test_apply_character_replacement_uppercase(self):
        """Test uppercase replacements."""
        result = apply_character_replacement("BAADE KJOERE LAERE")
        self.assertIsInstance(result, list)
        # Should have variants with uppercase replacements
        variants_with_aa = [v for v in result if "BÅDE" in v]
        self.assertTrue(len(variants_with_aa) > 0)
    
    def test_apply_character_replacement_mixed_case(self):
        """Test mixed case replacements."""
        result = apply_character_replacement("Baade Kjoere Laere")
        self.assertIsInstance(result, list)
        # Should have variants with mixed case replacements
        variants_with_aa = [v for v in result if "Både" in v]
        self.assertTrue(len(variants_with_aa) > 0)
    
    def test_apply_character_replacement_no_change(self):
        """Test string with no replacements needed."""
        original = "ingen endringer her"
        result = apply_character_replacement(original)
        self.assertEqual(result, [original])
    
    def test_apply_character_replacement_empty_string(self):
        """Test empty string."""
        result = apply_character_replacement("")
        self.assertEqual(result, [""])
    
    @patch('subprocess.run')
    def test_run_wizard(self, mock_run):
        """Test run_wizard calls the external script."""
        run_wizard()
        mock_run.assert_called_once()


class TestSearchConfig(unittest.TestCase):
    """Test SearchConfig class."""
    
    def test_searchconfig_init_defaults(self):
        """Test SearchConfig initialization with defaults."""
        config = SearchConfig()
        
        # Test default values
        self.assertTrue(config.character_replacement)
        self.assertEqual(config.default_limit, 50)
        self.assertTrue(config.show_inflections)
        self.assertTrue(config.show_etymology)
        self.assertTrue(config.pagination)
        self.assertEqual(config.page_size, 20)
        self.assertEqual(config.limit_with_pagination, 500)
        self.assertTrue(config.clear_screen)
        self.assertEqual(config.interactive_results_limit, 15)
        self.assertTrue(config.fallback_to_fuzzy)
        self.assertTrue(config.interactive_anywhere_search)
    
    def test_searchconfig_load_config_file_not_exists(self):
        """Test load_config when config file doesn't exist."""
        config = SearchConfig()
        
        with patch('ordb.config.get_config_path') as mock_get_path:
            mock_get_path.return_value = None
            config.load_config()
            
            # Should still have defaults
            self.assertTrue(config.character_replacement)
            self.assertEqual(config.default_limit, 50)
    
    def test_searchconfig_load_config_with_custom_values(self):
        """Test load_config with custom configuration values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""[search]
character_replacement = false
default_limit = 25
show_inflections = false
show_etymology = false
pagination = false
page_size = 30
limit_with_pagination = 200
clear_screen = false
interactive_results_limit = 10
fallback_to_fuzzy = false
interactive_anywhere_search = false
""")
            f.flush()
            
            config = SearchConfig()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                # Set up mocking so that config_dir/config points to our temp file
                temp_dir = Path(f.name).parent
                mock_get_config_dir.return_value = temp_dir
                # Rename our temp file to 'config' in temp dir
                config_file = temp_dir / 'config'
                Path(f.name).rename(config_file)
                
                config.load_config()
                
                # Test custom values
                self.assertFalse(config.character_replacement)
                self.assertEqual(config.default_limit, 25)
                self.assertFalse(config.show_inflections)
                self.assertFalse(config.show_etymology)
                self.assertFalse(config.pagination)
                self.assertEqual(config.page_size, 30)
                self.assertEqual(config.limit_with_pagination, 200)
                self.assertFalse(config.clear_screen)
                self.assertEqual(config.interactive_results_limit, 10)
                self.assertFalse(config.fallback_to_fuzzy)
                self.assertFalse(config.interactive_anywhere_search)
        
        # Clean up
        try:
            Path(f.name).unlink()
        except FileNotFoundError:
            pass  # Already cleaned up by rename
    
    def test_searchconfig_load_config_partial_values(self):
        """Test load_config with partial configuration values."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""[search]
default_limit = 75
show_inflections = false
""")
            f.flush()
            
            config = SearchConfig()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                # Set up mocking so that config_dir/config points to our temp file
                temp_dir = Path(f.name).parent
                mock_get_config_dir.return_value = temp_dir
                # Rename our temp file to 'config' in temp dir
                config_file = temp_dir / 'config'
                Path(f.name).rename(config_file)
                
                config.load_config()
                
                # Test partial values (some custom, some default)
                self.assertTrue(config.character_replacement)  # default
                self.assertEqual(config.default_limit, 75)  # custom
                self.assertFalse(config.show_inflections)  # custom
                self.assertTrue(config.show_etymology)  # default
        
        # Clean up
        try:
            Path(f.name).unlink()
        except FileNotFoundError:
            pass  # Already cleaned up by rename
    
    def test_searchconfig_load_config_invalid_file(self):
        """Test load_config with invalid/corrupted config file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("invalid config content [[[")
            f.flush()
            
            config = SearchConfig()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                # Set up mocking so that config_dir/config points to our temp file
                temp_dir = Path(f.name).parent
                mock_get_config_dir.return_value = temp_dir
                # Rename our temp file to 'config' in temp dir
                config_file = temp_dir / 'config'
                Path(f.name).rename(config_file)
                
                config.load_config()
                
                # Should fall back to defaults
                self.assertTrue(config.character_replacement)
                self.assertEqual(config.default_limit, 50)
        
        # Clean up
        try:
            Path(f.name).unlink()
        except FileNotFoundError:
            pass  # Already cleaned up by rename
    
    def test_searchconfig_invalid_integer_values(self):
        """Test SearchConfig with invalid integer values (exception handling)."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""[search]
default_limit = invalid_number
page_size = not_a_number
limit_with_pagination = abc123
interactive_results_limit = xyz
""")
            f.flush()
            
            config = SearchConfig()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                temp_dir = Path(f.name).parent
                mock_get_config_dir.return_value = temp_dir
                config_file = temp_dir / 'config'
                Path(f.name).rename(config_file)
                
                config.load_config()
                
                # Should use defaults due to ValueError exceptions
                self.assertEqual(config.default_limit, 50)  # default
                self.assertEqual(config.page_size, 20)  # default
                self.assertEqual(config.limit_with_pagination, 500)  # default
                self.assertEqual(config.interactive_results_limit, 15)  # default
        
        # Clean up
        try:
            Path(f.name).unlink()
        except FileNotFoundError:
            pass
    
    def test_searchconfig_general_exception_handling(self):
        """Test SearchConfig with general exception handling."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("completely invalid config content")
            f.flush()
            
            config = SearchConfig()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                temp_dir = Path(f.name).parent
                mock_get_config_dir.return_value = temp_dir
                config_file = temp_dir / 'config'
                Path(f.name).rename(config_file)
                
                config.load_config()
                
                # Should use all defaults due to exception
                self.assertTrue(config.character_replacement)  # default
                self.assertEqual(config.default_limit, 50)  # default
        
        # Clean up
        try:
            Path(f.name).unlink()
        except FileNotFoundError:
            pass
    
    def test_searchconfig_backward_compatibility(self):
        """Test backward compatibility with old config key names."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write("""[search]
fuzzy_results_limit = 25
""")
            f.flush()
            
            config = SearchConfig()
            
            with patch('ordb.config.get_config_dir') as mock_get_config_dir:
                # Set up mocking so that config_dir/config points to our temp file
                temp_dir = Path(f.name).parent
                mock_get_config_dir.return_value = temp_dir
                # Rename our temp file to 'config' in temp dir
                config_file = temp_dir / 'config'
                Path(f.name).rename(config_file)
                
                config.load_config()
                
                # Should use old key name value for new attribute
                self.assertEqual(config.interactive_results_limit, 25)
        
        # Clean up
        try:
            Path(f.name).unlink()
        except FileNotFoundError:
            pass  # Already cleaned up by rename


if __name__ == '__main__':
    unittest.main()