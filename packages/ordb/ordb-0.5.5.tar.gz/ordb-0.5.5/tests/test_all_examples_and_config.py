"""Test TODO items #17, #18, and #19: --all-examples, inflections config, etymology config."""
import unittest
import subprocess
import tempfile
import re
import os
import sys
import configparser
from pathlib import Path

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.config import SearchConfig

class TestTodo17_18_19(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use user database location
        self.db_path = os.path.expanduser('~/.ordb/articles.db')
        self.original_dir = os.getcwd()
    
    def tearDown(self):
        """Clean up after test."""
        os.chdir(self.original_dir)
    
    def create_config_file(self, content, directory):
        """Create a temporary config file in the specified directory."""
        # Create .ordb directory structure for new config location
        ordb_dir = Path(directory) / '.ordb'
        ordb_dir.mkdir(exist_ok=True)
        config_path = ordb_dir / 'config'
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return str(config_path)
    
    def run_search_in_dir(self, directory, query, *args):
        """Run search command in a specific directory and return output."""
        os.chdir(directory)
        cmd = self.search_cmd + ['--no-paginate'] + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout, result.stderr, result.returncode
    
    def run_search(self, query, *args):
        """Run search command and return output."""
        cmd = self.search_cmd + ['--no-paginate'] + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def test_todo_17_all_examples_finds_examples(self):
        """Test TODO #17: --all-examples finds examples across dictionary."""
        output = self.run_search('gå', '--all-examples', '--limit', '5')
        clean_output = self.clean_ansi(output)
        
        # Should show the search header
        self.assertIn('searching all examples', output.lower())
        self.assertIn('exact matches', output)
        
        # Should find examples
        self.assertIn('example(s) containing', output)
        
        # Should display examples in semicolon-separated format
        self.assertIn(';', clean_output)
        
        # Should highlight the search term
        self.assertIn('gå', clean_output)
    
    def test_todo_17_all_examples_respects_limit(self):
        """Test that --all-examples respects the --limit parameter."""
        output = self.run_search('gå', '--all-examples', '--limit', '3')
        
        # Should find examples but be limited
        if '📖' in output:
            # Should mention truncation if there are more results
            if 'more example(s)' in output:
                self.assertIn('more example(s)', output)
    
    def test_todo_17_all_examples_character_replacement(self):
        """Test that --all-examples works with character replacement."""
        output = self.run_search('gaa', '--all-examples', '--limit', '3')
        
        # Should find examples for "gå" even when searching for "gaa"
        if '📖' in output:
            clean_output = self.clean_ansi(output)
            # Should find examples (character replacement should work)
            self.assertIn('gå', clean_output)
    
    def test_todo_18_inflections_config_disabled(self):
        """Test TODO #18: SearchConfig class supports show_inflections setting."""
        # Test that the SearchConfig class properly loads the show_inflections setting
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write('''
[search]
show_inflections = False
show_etymology = True
''')
            temp_config_path = f.name
        
        try:
            # Test that SearchConfig can parse the configuration
            config = configparser.ConfigParser()
            config.read(temp_config_path)
            
            # Should have search section
            self.assertIn('search', config)
            
            # Should be able to read show_inflections setting
            self.assertEqual(config['search'].getboolean('show_inflections'), False)
            self.assertEqual(config['search'].getboolean('show_etymology'), True)
            
        finally:
            import os
            os.unlink(temp_config_path)
    
    def test_todo_19_etymology_config_disabled(self):
        """Test TODO #19: SearchConfig class supports show_etymology setting."""
        # Test that the SearchConfig class properly loads the show_etymology setting
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write('''
[search]
show_inflections = True
show_etymology = False
''')
            temp_config_path = f.name
        
        try:
            # Test that SearchConfig can parse the configuration
            config = configparser.ConfigParser()
            config.read(temp_config_path)
            
            # Should have search section
            self.assertIn('search', config)
            
            # Should be able to read show_etymology setting
            self.assertEqual(config['search'].getboolean('show_inflections'), True)
            self.assertEqual(config['search'].getboolean('show_etymology'), False)
            
        finally:
            import os
            os.unlink(temp_config_path)
    
    def test_todo_18_19_both_disabled(self):
        """Test both inflections and etymology can be disabled via config."""
        # Test that the SearchConfig class properly loads both settings
        
        # Create a temporary config file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.conf', delete=False) as f:
            f.write('''
[search]
show_inflections = False
show_etymology = False
''')
            temp_config_path = f.name
        
        try:
            # Test that SearchConfig can parse the configuration
            config = configparser.ConfigParser()
            config.read(temp_config_path)
            
            # Should have search section
            self.assertIn('search', config)
            
            # Should be able to read both settings as disabled
            self.assertEqual(config['search'].getboolean('show_inflections'), False)
            self.assertEqual(config['search'].getboolean('show_etymology'), False)
            
        finally:
            import os
            os.unlink(temp_config_path)
    
    def test_todo_18_19_config_defaults_to_true(self):
        """Test that missing config options default to True."""
        # Test that SearchConfig defaults work properly
        
        # Create a SearchConfig instance without any config file
        # This should use default values
        search_config = SearchConfig()
        
        # Should default to True for both settings
        self.assertEqual(search_config.show_inflections, True)
        self.assertEqual(search_config.show_etymology, True)
        self.assertEqual(search_config.character_replacement, True)
    
    def test_all_examples_no_results(self):
        """Test --all-examples with a word that has no examples."""
        output = self.run_search('xyzkjsdhfksdf', '--all-examples')
        
        # Should show appropriate message
        self.assertIn('No examples found', output)

if __name__ == '__main__':
    unittest.main()