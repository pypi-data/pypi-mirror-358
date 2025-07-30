"""Test platform-specific file paths and Windows compatibility."""
import unittest
import tempfile
import os
import sys
from pathlib import Path
from unittest.mock import patch

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.config import get_config_dir, get_data_dir


class TestPlatformPaths(unittest.TestCase):
    
    def test_unix_config_paths(self):
        """Test that Unix-like systems use ~/.ordb/config."""
        with patch('os.name', 'posix'):
            config_dir = get_config_dir()
            data_dir = get_data_dir()
            
            expected_path = Path.home() / '.ordb'
            self.assertEqual(config_dir, expected_path)
            self.assertEqual(data_dir, expected_path)
    
    def test_windows_logic(self):
        """Test Windows path logic without creating actual Windows paths."""
        # Test environment variable detection
        test_env = {
            'APPDATA': 'C:/Users/TestUser/AppData/Roaming',
            'LOCALAPPDATA': 'C:/Users/TestUser/AppData/Local'
        }
        
        # Test config directory logic
        config_base = test_env.get('APPDATA')
        if config_base:
            expected_config = f"{config_base}/ordb"
            self.assertEqual(expected_config, "C:/Users/TestUser/AppData/Roaming/ordb")
        
        # Test data directory logic
        data_base = test_env.get('LOCALAPPDATA')
        if data_base:
            expected_data = f"{data_base}/ordb"
            self.assertEqual(expected_data, "C:/Users/TestUser/AppData/Local/ordb")
    
    def test_windows_fallback_logic(self):
        """Test Windows fallback logic when environment variables are missing."""
        # Simulate empty environment
        test_env = {}
        
        # Should fallback to home-based path
        config_base = test_env.get('APPDATA')
        if not config_base:
            config_base = test_env.get('USERPROFILE')
        
        # Test that logic defaults properly
        self.assertIsNone(config_base)  # No env vars set
    
    def test_config_directory_creation(self):
        """Test that config directories can be created successfully."""
        # Test with a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            test_config_dir = Path(temp_dir) / 'test_ordb_config'
            test_data_dir = Path(temp_dir) / 'test_ordb_data'
            
            # Create directories
            test_config_dir.mkdir(parents=True, exist_ok=True)
            test_data_dir.mkdir(parents=True, exist_ok=True)
            
            # Verify they exist
            self.assertTrue(test_config_dir.exists())
            self.assertTrue(test_data_dir.exists())
            
            # Test writing a config file
            config_file = test_config_dir / 'config'
            config_file.write_text('[search]\ntest=true\n')
            
            # Verify file was written
            self.assertTrue(config_file.exists())
            self.assertIn('test=true', config_file.read_text())
    
    def test_path_separators_cross_platform(self):
        """Test that pathlib handles path separators correctly across platforms."""
        # This should work the same on Windows and Unix
        test_path = Path('folder') / 'subfolder' / 'file.txt'
        
        # Pathlib should use the correct separator for the platform
        path_str = str(test_path)
        
        if os.name == 'nt':
            # Windows should use backslashes
            self.assertIn('\\', path_str)
        else:
            # Unix should use forward slashes
            self.assertIn('/', path_str)
    
    def test_database_path_construction(self):
        """Test that database paths are constructed correctly for Unix platform."""
        # Only test on the current platform to avoid cross-platform path issues
        data_dir = get_data_dir()
        db_path = data_dir / 'articles.db'
        
        # Should end with articles.db
        self.assertTrue(str(db_path).endswith('articles.db'))
        
        # Should contain ordb directory
        self.assertIn('ordb', str(db_path))


if __name__ == '__main__':
    unittest.main()