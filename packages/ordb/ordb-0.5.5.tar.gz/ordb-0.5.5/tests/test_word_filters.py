"""Test word type filters: --adj, --verb, --noun, --adv."""
import unittest
import subprocess
import sys
from pathlib import Path
import os

# Add src to path for importing utils
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.utils import clean_ansi_codes


class TestWordFilters(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use user database location (default for ordb)
        self.db_path = os.path.expanduser('~/.ordb/articles.db')
    
    def run_search(self, query, *args, input_text=None):
        """Run search command and return output."""
        cmd = self.search_cmd + ['--no-paginate'] + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True, input=input_text)
        return result.stdout, result.stderr, result.returncode
    
    def test_adj_filter(self):
        """Test --adj filter returns only adjectives."""
        stdout, stderr, returncode = self.run_search('stor', '--adj', '--limit', '3')
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should contain adjective markers
        self.assertIn('[adj]', clean_output)
        
        # Should NOT contain other word types in results
        self.assertNotIn('[noun]', clean_output)
        self.assertNotIn('[verb]', clean_output)
        self.assertNotIn('[adv]', clean_output)
    
    def test_verb_filter(self):
        """Test --verb filter returns only verbs."""
        stdout, stderr, returncode = self.run_search('gå', '--verb', '--limit', '3')
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should contain verb markers
        self.assertIn('[verb]', clean_output)
        
        # Should NOT contain other word types in results
        self.assertNotIn('[noun]', clean_output)
        self.assertNotIn('[adj]', clean_output)
        self.assertNotIn('[adv]', clean_output)
    
    def test_noun_filter(self):
        """Test --noun filter returns only nouns."""
        stdout, stderr, returncode = self.run_search('hus', '--noun', '--limit', '3')
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should contain noun markers
        self.assertIn('[noun]', clean_output)
        
        # Should NOT contain other word types in results
        self.assertNotIn('[verb]', clean_output)
        self.assertNotIn('[adj]', clean_output)
        self.assertNotIn('[adv]', clean_output)
    
    def test_adv_filter(self):
        """Test --adv filter returns only adverbs."""
        stdout, stderr, returncode = self.run_search('fort', '--adv', '--limit', '3')
        
        clean_output = clean_ansi_codes(stdout)
        
        # If no adverb results found, skip the detailed assertions
        if 'No results found' in clean_output:
            self.assertEqual(returncode, 0)
            return
        
        self.assertEqual(returncode, 0)
        
        # Should contain adverb markers
        self.assertIn('[adv]', clean_output)
        
        # Should NOT contain other word types in results  
        self.assertNotIn('[noun]', clean_output)
        self.assertNotIn('[verb]', clean_output)
        self.assertNotIn('[adj]', clean_output)


if __name__ == '__main__':
    unittest.main()