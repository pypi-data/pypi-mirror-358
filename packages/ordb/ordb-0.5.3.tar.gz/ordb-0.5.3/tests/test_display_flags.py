"""Test TODO items #14, #15, and #16: --no-definitions, --no-examples, and --only-examples consistency."""
import unittest
import subprocess
import re
import os

class TestTodo14_15_16(unittest.TestCase):
    
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
    
    def test_todo_14_no_definitions_excludes_faste_uttrykk_definitions(self):
        """Test TODO #14: --no-definitions should exclude definitions from faste uttrykk."""
        output = self.run_search('hus', '--no-definitions')
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('search for', output.lower())
        
        # Should show "Faste uttrykk:" header
        self.assertIn('Faste uttrykk:', clean_output)
        
        # Should NOT show definition text for expressions
        # These are definition texts that should be hidden
        self.assertNotIn('sal, rom eller lignende med alle plasser opptatt', clean_output)
        self.assertNotIn('ikke bli lagt merke til, ikke bli oppfattet', clean_output)
        self.assertNotIn('på arbeidsplassen; internt', clean_output)
        
        # Should still show expression names
        self.assertIn('fullt hus', clean_output)
        self.assertIn('gå hus forbi', clean_output)
        self.assertIn('på huset', clean_output)
        
        # Should still show examples (since --no-examples not used)
        self.assertIn('spille for fullt hus', clean_output)
    
    def test_todo_15_no_examples_excludes_faste_uttrykk_examples(self):
        """Test TODO #15: --no-examples should exclude examples from faste uttrykk."""
        output = self.run_search('hus', '--no-examples')
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('search for', output.lower())
        
        # Should show "Faste uttrykk:" header
        self.assertIn('Faste uttrykk:', clean_output)
        
        # Should show expression names and definitions
        self.assertIn('fullt hus', clean_output)
        self.assertIn('sal, rom eller lignende med alle plasser opptatt', clean_output)
        self.assertIn('gå hus forbi', clean_output)
        self.assertIn('ikke bli lagt merke til, ikke bli oppfattet', clean_output)
        
        # Should NOT show examples from faste uttrykk
        self.assertNotIn('spille for fullt hus', clean_output)
        self.assertNotIn('jentenes prestasjoner har gått hus forbi', clean_output)
        self.assertNotIn('navnet gikk meg hus forbi', clean_output)
        
        # Should also not show main examples
        self.assertNotIn('bygge hus', clean_output)
        self.assertNotIn('ha både hus og hytte', clean_output)
    
    def test_todo_16_only_examples_shows_only_examples(self):
        """Test TODO #16: --only-examples should show only examples."""
        output = self.run_search('hus', '--only-examples')
        clean_output = self.clean_ansi(output)
        
        # Should find results
        self.assertIn('search for', output.lower())
        
        # Should show lemma header
        self.assertIn('hus', clean_output)
        self.assertIn('[noun]', clean_output)
        
        # Should NOT show definitions
        self.assertNotIn('bygning (med tak og vegger)', clean_output)
        self.assertNotIn('bosted, hjem, heim', clean_output)
        
        # Should NOT show etymology
        self.assertNotIn('Etymology:', clean_output)
        self.assertNotIn('norr. hús', clean_output)
        
        # Should NOT show inflections
        self.assertNotIn('Inflections:', clean_output)
        self.assertNotIn('Singular:', clean_output)
        self.assertNotIn('Plural:', clean_output)
        
        # Should NOT show "Faste uttrykk:" header
        self.assertNotIn('Faste uttrykk:', clean_output)
        
        # Should show examples from main word
        self.assertIn('bygge hus', clean_output)
        self.assertIn('ha både hus og hytte', clean_output)
        
        # Should show examples from faste uttrykk (without the header)
        self.assertIn('spille for fullt hus', clean_output)
        self.assertIn('på huset', clean_output)
        
        # Examples should be semicolon-separated on one line
        lines = clean_output.split('\n')
        example_lines = [line for line in lines if 'bygge hus' in line or 'spille for fullt hus' in line]
        self.assertGreater(len(example_lines), 0, "Should find example lines")
        
        # Check that examples are separated by semicolons
        for line in example_lines:
            if 'bygge hus' in line:
                self.assertIn(';', line, "Examples should be semicolon-separated")
    
    def test_todo_16_only_examples_works_with_multiple_words(self):
        """Test that --only-examples works with words that have multiple results."""
        output = self.run_search('stein', '--only-examples')
        clean_output = self.clean_ansi(output)
        
        # Should find multiple results (stein has several homonyms)
        self.assertIn('search for', output.lower())
        
        # Should show examples for different word types
        self.assertIn('kaste stein', clean_output)  # From noun
        self.assertIn('steinet til døde', clean_output)  # From verb
        
        # Should NOT show definitions for any of them
        self.assertNotIn('hard naturlig mineralmasse', clean_output)
        self.assertNotIn('drepe ved steining', clean_output)
    
    def test_todo_16_only_examples_no_examples_shows_only_headers(self):
        """Test that --only-examples on words without examples shows only headers."""
        # Use a word that might not have many examples
        output = self.run_search('xyz', '--only-examples')
        
        # Should run without error - either show search results or "no results found"
        self.assertTrue('search for' in output.lower() or 'no results found' in output.lower())
        
        # If no results, should show "no results found"
        if 'no results found' in output.lower():
            self.assertIn('no results found', output.lower())
        # If results found, should only show headers
        elif '📖' in output:
            clean_output = self.clean_ansi(output)
            # Should not show non-example content
            self.assertNotIn('Etymology:', clean_output)
            self.assertNotIn('Inflections:', clean_output)

if __name__ == '__main__':
    unittest.main()