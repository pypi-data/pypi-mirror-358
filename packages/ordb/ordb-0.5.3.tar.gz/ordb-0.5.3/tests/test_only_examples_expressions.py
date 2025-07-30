"""Test TODO item #26: --only-examples should include mentions of expressions."""
import unittest
import subprocess
import re
import os

class TestTodo26(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use user database location
        self.db_path = os.path.expanduser('~/.ordb/articles.db')
    
    def run_search(self, query, *args):
        """Run search command and return output."""
        cmd = self.search_cmd + ['--no-paginate'] + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.stdout
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def test_todo_26_only_examples_includes_expressions(self):
        """Test TODO #26: --only-examples includes expression names and examples."""
        output = self.run_search('hus', '--only-examples', '--limit', '1')
        clean_output = self.clean_ansi(output)
        
        # Should include examples from definitions
        self.assertIn('bygge hus', clean_output)
        
        # Should include expression names
        self.assertIn('fullt hus', clean_output)
        self.assertIn('gå hus forbi', clean_output)
        self.assertIn('gå mann av huse', clean_output)
        self.assertIn('holde åpent hus', clean_output)
        self.assertIn('hus under hver busk', clean_output)
        self.assertIn('i hus', clean_output)
        self.assertIn('på huset', clean_output)
        
        # Should include examples from expressions
        self.assertIn('spille for fullt hus', clean_output)
        self.assertIn('jentenes prestasjoner har gått hus forbi', clean_output)
        self.assertIn('få avlingen i hus', clean_output)
        self.assertIn('vi håper vodkaen er på huset', clean_output)
        
        # Should NOT include definitions text
        self.assertNotIn('bygning (med tak og vegger)', clean_output)
        self.assertNotIn('Etymology:', clean_output)
        self.assertNotIn('Inflections:', clean_output)
    
    def test_todo_26_comparison_with_regular_search(self):
        """Test that --only-examples includes expressions that are in regular search."""
        regular_output = self.run_search('hus', '--limit', '1')
        only_examples_output = self.run_search('hus', '--only-examples', '--limit', '1')
        
        clean_regular = self.clean_ansi(regular_output)
        clean_examples = self.clean_ansi(only_examples_output)
        
        # Examples should be present in both
        self.assertIn('bygge hus', clean_regular)
        self.assertIn('bygge hus', clean_examples)
        
        # Expression names should be present in both
        self.assertIn('fullt hus', clean_regular)
        self.assertIn('fullt hus', clean_examples)
        
        # But definitions should only be in regular
        self.assertIn('bygning (med tak og vegger)', clean_regular)
        self.assertNotIn('bygning (med tak og vegger)', clean_examples)
    
    def test_todo_26_expressions_without_examples(self):
        """Test that expressions without examples are still included."""
        output = self.run_search('hus', '--only-examples', '--limit', '1')
        clean_output = self.clean_ansi(output)
        
        # Some expressions don't have examples but should still be listed
        self.assertIn('gå mann av huse', clean_output)
        self.assertIn('holde åpent hus', clean_output)
        self.assertIn('hus under hver busk', clean_output)
        
        # These are expression names that appear even without examples

if __name__ == '__main__':
    unittest.main()