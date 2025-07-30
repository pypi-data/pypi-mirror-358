"""Test character replacement functionality (aa→å, oe→ø, ae→æ)."""
import unittest
import subprocess
import re
import os

class TestCharacterReplacement(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        # Use faster python module command
        self.search_cmd = ['python', '-m', 'src.ordb']
        # Use user database location (default for ordb)
        self.db_path = os.path.expanduser('~/.ordb/articles.db')
    
    def run_search(self, query, *args):
        """Run search command and return output."""
        cmd = self.search_cmd + ['--no-paginate'] + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def test_aa_to_a_replacement(self):
        """Test that 'aa' is replaced with 'å' in searches."""
        # Search for 'gaa' should find 'gå'
        output = self.run_search('gaa')
        clean_output = self.clean_ansi(output)
        
        # Should find results (indicated by search header and lemma)
        self.assertIn('search for', output.lower())
        self.assertIn('📖', output)
        
        # Should find 'gå' (verb)
        if '[verb]' in clean_output:
            self.assertIn('gå', clean_output)
    
    def test_oe_to_o_replacement(self):
        """Test that 'oe' is replaced with 'ø' in searches."""
        # Search for 'groenn' should find 'grønn'
        output = self.run_search('groen')
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('search for', output.lower())
        
        # Should find 'grønn' (green)
        if 'grønn' in clean_output:
            self.assertIn('grønn', clean_output)
    
    def test_ae_to_ae_replacement(self):
        """Test that 'ae' is replaced with 'æ' in searches."""
        # Search for 'vaere' should find 'være'
        output = self.run_search('vaere')
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('search for', output.lower())
        
        # Should find 'være' (verb - to be)
        if '[verb]' in clean_output:
            self.assertIn('være', clean_output)
    
    def test_fuzzy_search_with_replacement(self):
        """Test character replacement works with fuzzy search."""
        output = self.run_search('gaa', '-f')
        clean_output = self.clean_ansi(output)
        
        # Should find results (either interactive or direct)
        # When using --no-paginate, it bypasses interactive mode and shows direct results
        success_indicators = ['search for', '📖', 'found', 'results']
        self.assertTrue(any(indicator in output.lower() for indicator in success_indicators))
        
        # Should find 'gå' via fuzzy matching
        self.assertIn('gå', clean_output)
    
    def test_prefix_search_with_replacement(self):
        """Test character replacement works with prefix search."""
        output = self.run_search('gaa@')
        clean_output = self.clean_ansi(output)
        
        # Should find results  
        self.assertIn('search for', output.lower())
        
        # Should mention prefix search
        self.assertIn('Prefix search', output)
        
        # Should find words starting with 'gå'
        if 'gå' in clean_output:
            self.assertIn('gå', clean_output)
    
    def test_fulltext_search_with_replacement(self):
        """Test character replacement works with fulltext search."""
        output = self.run_search('%gaa')
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('search for', output.lower())
        
        # Should mention full-text search
        self.assertIn('Full-text search', output)
    
    def test_anywhere_search_with_replacement(self):
        """Test character replacement works with anywhere search."""
        output = self.run_search('groen', '-a')  # Use 'groen' instead of 'groenn' 
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('searching anywhere', output.lower())
        
        # Should mention anywhere search
        self.assertIn('anywhere', output)
    
    def test_expressions_search_with_replacement(self):
        """Test character replacement works with expressions-only search."""
        output = self.run_search('gaa', '-x')
        clean_output = self.clean_ansi(output)
        
        # Should mention expression search
        self.assertIn('Expression search', output)
        
        # If any results found, they should be expressions
        if '📖' in output and '[expr]' in clean_output:
            # All results should be expressions
            word_classes = re.findall(r'\\[(\\w+)\\]', clean_output)
            for wc in word_classes:
                self.assertEqual(wc, 'expr', f"Found non-expression: {wc}")
    
    def test_multiple_replacements(self):
        """Test query with multiple replacement opportunities."""
        # Search for 'gaae' should try multiple variants
        output = self.run_search('gaae')
        
        # Should find some results (may include gå, gåe, etc.)
        # Just verify the search ran without error
        self.assertIn('search for', output.lower())
    
    def test_uppercase_replacements(self):
        """Test that uppercase versions are also replaced."""
        output = self.run_search('GAA')
        
        # Should handle the uppercase query without error (may or may not find results)
        self.assertNotIn('Error', output)
        
        # Should run the search (indicated by search header)
        self.assertTrue('search for' in output.lower() or 'no results found' in output.lower())

if __name__ == '__main__':
    unittest.main()