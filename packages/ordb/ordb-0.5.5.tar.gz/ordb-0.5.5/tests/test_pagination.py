"""Test pagination functionality: -p flag, config settings, navigation."""
import unittest
import subprocess
import sys
from pathlib import Path
import os

# Add src to path for importing utils
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.utils import clean_ansi_codes


class TestPagination(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['ordb']  # Use installed ordb command
        # Use the actual ordb database location (no --db needed)
        self.no_paginate_args = ['--no-paginate']  # For tests that need pagination disabled
        self.paginate_args = []  # For tests that need pagination enabled
        
        # Create temporary config for pagination tests
        self.original_config = None
        project_root = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.config_path = project_root / '.config-bm'
        if self.config_path.exists():
            # Backup original config
            self.original_config = self.config_path.read_text()
    
    def tearDown(self):
        """Clean up after tests."""
        # Restore original config if it existed
        if self.original_config is not None:
            self.config_path.write_text(self.original_config)
        elif self.config_path.exists():
            # Remove test config if original didn't exist
            self.config_path.unlink()
    
    def run_search(self, query, *args, input_text=None, allow_pagination=False):
        """Run search command and return output."""
        base_args = self.paginate_args if allow_pagination else self.no_paginate_args
        cmd = self.search_cmd + base_args + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True, input=input_text, timeout=30)
        return result.stdout, result.stderr, result.returncode
    
    def create_test_config(self, pagination=True, page_size=20):
        """Create a test configuration file."""
        config_content = f"""[search]
pagination = {pagination}
page_size = {page_size}
character_replacement = True
default_limit = 50
show_inflections = True
show_etymology = True
"""
        self.config_path.write_text(config_content)
    
    def test_pagination_enabled_by_default(self):
        """Test that pagination is enabled by default."""
        # Create config with pagination enabled
        self.create_test_config(pagination=True, page_size=10)
        
        # Search for something that will produce long output
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should contain pagination prompt
        self.assertIn('--More--', clean_output)
        self.assertIn('lines remaining', clean_output)
        self.assertIn('Space/Enter: next page', clean_output)
    
    def test_pagination_disabled_in_config(self):
        """Test that pagination can be disabled via config."""
        # Create config with pagination disabled
        self.create_test_config(pagination=False, page_size=10)
        
        # Search for something short to avoid timeout
        stdout, stderr, returncode = self.run_search('xyz', '--limit', '1')
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should NOT contain pagination prompt
        self.assertNotIn('--More--', clean_output)
        self.assertNotIn('lines remaining', clean_output)
    
    def test_pagination_force_flag(self):
        """Test -p flag forces pagination even when config is False."""
        # Create config with pagination disabled
        self.create_test_config(pagination=False, page_size=10)
        
        # Use -p flag to force pagination
        stdout, stderr, returncode = self.run_search('hus', '-p', '--limit', '1', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should contain pagination prompt despite config being False
        self.assertIn('--More--', clean_output)
        self.assertIn('lines remaining', clean_output)
    
    def test_pagination_quit_functionality(self):
        """Test that 'q' properly quits pagination."""
        # Create config with small page size
        self.create_test_config(pagination=True, page_size=5)
        
        # Search with 'q' input to quit pagination
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should show truncation message
        self.assertIn('Output truncated', clean_output)
    
    def test_pagination_short_output_no_prompt(self):
        """Test that short output doesn't trigger pagination."""
        # Create config with large page size
        self.create_test_config(pagination=True, page_size=100)
        
        # Search for something that won't produce much output
        stdout, stderr, returncode = self.run_search('xyz', '--limit', '1')
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should NOT contain pagination prompt for short output
        self.assertNotIn('--More--', clean_output)
    
    def test_pagination_preserves_colors(self):
        """Test that pagination preserves ANSI color codes."""
        # Create config with small page size
        self.create_test_config(pagination=True, page_size=5)
        
        # Search and quit immediately to get first page
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        # Should contain ANSI color codes (not cleaned)
        self.assertIn('\x1b[', stdout)  # Should have ANSI codes
        self.assertIn('[92m', stdout)   # Should have green color codes
        self.assertIn('[96m', stdout)   # Should have cyan color codes
    
    def test_pagination_entry_header_preservation(self):
        """Test that entry headers are preserved during pagination."""
        # Create config with very small page size to force entry splitting
        self.create_test_config(pagination=True, page_size=3)
        
        # Search for a word that produces long entries
        stdout, stderr, returncode = self.run_search('hus', '--limit', '1', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should include the entry header even with small page size
        self.assertIn('📖', clean_output)
        self.assertIn('[noun]', clean_output)
        self.assertIn('(neuter)', clean_output)
    
    # Combined feature tests
    def test_etymology_flag_with_pagination(self):
        """Test that -e flag works with pagination."""
        # Create config with small page size
        self.create_test_config(pagination=True, page_size=3)
        
        stdout, stderr, returncode = self.run_search('hus', '-e', '--limit', '1', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should show etymology and pagination if needed
        self.assertIn('Etymology:', clean_output)
    
    def test_word_filter_with_pagination(self):
        """Test that word type filters work with pagination."""
        # Create config with small page size  
        self.create_test_config(pagination=True, page_size=5)
        
        stdout, stderr, returncode = self.run_search('stor', '--adj', '--limit', '2', input_text='q\n', allow_pagination=True)
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should show only adjectives
        self.assertIn('[adj]', clean_output)
        self.assertNotIn('[noun]', clean_output)


if __name__ == '__main__':
    unittest.main()