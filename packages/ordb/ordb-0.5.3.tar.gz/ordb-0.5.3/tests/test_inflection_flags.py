"""Test inflection display flags: -i, --only-inflections."""
import unittest
import subprocess
import sys
from pathlib import Path
import os

# Add src to path for importing utils
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.utils import clean_ansi_codes


class TestInflectionFlags(unittest.TestCase):
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['ordb']  # Use installed ordb command
        # Use the actual ordb database location (no --db needed)
        self.common_args = ['--no-paginate']  # Prevent pagination hanging
    
    def run_search(self, query, *args, input_text=None):
        """Run search command and return output."""
        cmd = self.search_cmd + self.common_args + list(args) + [query]
        result = subprocess.run(cmd, capture_output=True, text=True, input=input_text, timeout=30)
        return result.stdout, result.stderr, result.returncode
    
    def test_only_inflections_flag(self):
        """Test -i, --only-inflections flag shows only inflections."""
        stdout, stderr, returncode = self.run_search('hus', '-i', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should include inflections on separate lines
        self.assertIn('Inflections:', clean_output)
        self.assertIn('Singular:', clean_output)
        self.assertIn('Plural:', clean_output)
        # Check for the actual inflection values (format may vary)
        self.assertIn('huset', clean_output)  # singular definite
        self.assertIn('husa', clean_output)   # plural indefinite
        
        # Should NOT include definitions, examples, or etymology
        self.assertNotIn('bygning (med tak og vegger)', clean_output)
        self.assertNotIn('bygge hus', clean_output)
        self.assertNotIn('Etymology:', clean_output)
        self.assertNotIn('Faste uttrykk:', clean_output)
    
    def test_only_inflections_multiline_format(self):
        """Test that -i flag shows inflections on separate lines."""
        stdout, stderr, returncode = self.run_search('gå', '-i', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should show each inflection category on its own line
        lines = clean_output.split('\n')
        inflection_lines = [line for line in lines if 'Infinitive:' in line or 'Present:' in line or 'Past:' in line]
        
        # Should have multiple inflection category lines
        self.assertGreater(len(inflection_lines), 1)


if __name__ == '__main__':
    unittest.main()