"""Test etymology display flags: -e, --only-etymology."""
import unittest
import subprocess
import sys
from pathlib import Path
import os

# Add src to path for importing utils
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.utils import clean_ansi_codes


class TestEtymologyFlags(unittest.TestCase):
    
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
    
    def test_only_etymology_flag(self):
        """Test -e, --only-etymology flag shows only etymology."""
        stdout, stderr, returncode = self.run_search('hus', '-e', '--limit', '1')
        if returncode != 0:
            print(f"DEBUG: stdout={stdout}")
            print(f"DEBUG: stderr={stderr}")
            print(f"DEBUG: returncode={returncode}")
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should include etymology
        self.assertIn('Etymology:', clean_output)
        self.assertIn('norr. hús', clean_output)
        
        # Should NOT include definitions, examples, or inflections
        self.assertNotIn('bygning (med tak og vegger)', clean_output)
        self.assertNotIn('bygge hus', clean_output)
        self.assertNotIn('Inflections:', clean_output)
        self.assertNotIn('Faste uttrykk:', clean_output)
    
    def test_only_etymology_long_form(self):
        """Test --only-etymology long form flag."""
        stdout, stderr, returncode = self.run_search('stein', '--only-etymology', '--limit', '1')
        self.assertEqual(returncode, 0)
        
        clean_output = clean_ansi_codes(stdout)
        
        # Should include etymology
        self.assertIn('Etymology:', clean_output)
        self.assertIn('norr. steinn', clean_output)
        
        # Should NOT include other content
        self.assertNotIn('fast og hardt mineralsk', clean_output)
        self.assertNotIn('kaste stein', clean_output)


if __name__ == '__main__':
    unittest.main()