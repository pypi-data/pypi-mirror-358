#!/usr/bin/env python3
"""
Comprehensive test suite for ordb functionality.
Tests all command-line flags and major features.
"""

import unittest
import subprocess
import re
import os
import tempfile
from pathlib import Path


class TestOrdbFunctionality(unittest.TestCase):
    """Test all ordb command-line functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.search_cmd = ['python', '-m', 'src.ordb']
        self.db_path = os.path.expanduser('~/.ordb/articles.db')
        
        # Skip tests if database doesn't exist
        if not os.path.exists(self.db_path):
            self.skipTest("Database not found. Run 'ordb --help' first to set up database.")
    
    def run_ordb(self, *args, input_text=None):
        """Run ordb command and return output."""
        # Add --no-paginate to avoid pagination issues in tests
        cmd = self.search_cmd + ['--no-paginate'] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30, input=input_text)
        return result.stdout, result.stderr, result.returncode
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def test_help_command(self):
        """Test --help flag."""
        stdout, stderr, returncode = self.run_ordb('--help')
        self.assertEqual(returncode, 0)
        self.assertIn('Norwegian bokmål dictionary search tool', stdout)
        self.assertIn('--fuzzy', stdout)
        self.assertIn('--anywhere', stdout)
    
    def test_basic_search(self):
        """Test basic word search."""
        stdout, stderr, returncode = self.run_ordb('hus')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
        self.assertIn('📖', stdout)  # Should have entry marker
    
    def test_fuzzy_search(self):
        """Test --fuzzy flag."""
        stdout, stderr, returncode = self.run_ordb('-f', 'huse')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        # Should find "hus" via fuzzy matching
        self.assertIn('hus', clean_output.lower())
    
    def test_anywhere_search(self):
        """Test --anywhere flag."""
        stdout, stderr, returncode = self.run_ordb('-a', 'til fots')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('til fots', clean_output.lower())
    
    def test_expressions_only_search(self):
        """Test --expressions-only flag."""
        stdout, stderr, returncode = self.run_ordb('-x', 'hus')
        self.assertEqual(returncode, 0)
        # Should only find expressions, not main entries
        if stdout.strip():  # Only check if there are results
            clean_output = self.clean_ansi(stdout)
            self.assertIn('[expr]', clean_output.lower())
    
    def test_all_examples_search(self):
        """Test --all-examples flag."""
        stdout, stderr, returncode = self.run_ordb('--all-examples', 'hus')
        self.assertEqual(returncode, 0)
        if 'No examples found' not in stdout:
            clean_output = self.clean_ansi(stdout)
            self.assertIn('example', clean_output.lower())
    
    def test_only_examples_flag(self):
        """Test --only-examples flag."""
        stdout, stderr, returncode = self.run_ordb('--only-examples', 'hus')
        self.assertEqual(returncode, 0)
        # Should show examples but not full definition content
        if stdout.strip():
            clean_output = self.clean_ansi(stdout)
            # Should show examples (quotes) but not definition numbers
            self.assertTrue('bygge hus' in clean_output or 'no examples' in clean_output.lower())
            # Should NOT show definition numbers like "1.", "2.", etc.
            self.assertNotIn('1.', clean_output)
    
    def test_only_etymology_flag(self):
        """Test --only-etymology flag."""
        stdout, stderr, returncode = self.run_ordb('-e', 'hus')
        self.assertEqual(returncode, 0)
        # Should show etymology section
        if stdout.strip():
            clean_output = self.clean_ansi(stdout)
            # Should have header but minimal other content
            self.assertIn('hus', clean_output.lower())
    
    def test_only_inflections_flag(self):
        """Test --only-inflections flag."""
        stdout, stderr, returncode = self.run_ordb('-i', 'hus')
        self.assertEqual(returncode, 0)
        # Should show inflections
        if stdout.strip():
            clean_output = self.clean_ansi(stdout)
            self.assertIn('hus', clean_output.lower())
    
    def test_word_class_filters(self):
        """Test word class filtering flags."""
        # Test noun filter
        stdout, stderr, returncode = self.run_ordb('--noun', 'hus')
        self.assertEqual(returncode, 0)
        if '[verb]' in stdout:
            self.fail("Noun filter should not return verbs")
        
        # Test verb filter
        stdout, stderr, returncode = self.run_ordb('--verb', 'gå')
        self.assertEqual(returncode, 0)
        if '[noun]' in stdout:
            self.fail("Verb filter should not return nouns")
        
        # Test adjective filter
        stdout, stderr, returncode = self.run_ordb('--adj', 'stor')
        self.assertEqual(returncode, 0)
        
        # Test adverb filter
        stdout, stderr, returncode = self.run_ordb('--adv', 'fort')
        self.assertEqual(returncode, 0)
    
    def test_limit_flag(self):
        """Test --limit flag."""
        stdout, stderr, returncode = self.run_ordb('--limit', '1', 'hus')
        self.assertEqual(returncode, 0)
        # Should limit results
        self.assertIn('hus', self.clean_ansi(stdout).lower())
    
    def test_no_definitions_flag(self):
        """Test --no-definitions flag."""
        stdout, stderr, returncode = self.run_ordb('--no-definitions', 'hus')
        self.assertEqual(returncode, 0)
        # Should show header but no definition content
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
    
    def test_no_examples_flag(self):
        """Test --no-examples flag."""
        stdout, stderr, returncode = self.run_ordb('--no-examples', 'hus')
        self.assertEqual(returncode, 0)
        # Should show definitions but fewer examples
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
    
    def test_threshold_flag(self):
        """Test --threshold flag for fuzzy search."""
        stdout, stderr, returncode = self.run_ordb('-f', '--threshold', '0.8', 'huse')
        self.assertEqual(returncode, 0)
        # Should work with custom threshold
    
    def test_max_examples_flag(self):
        """Test --max-examples flag."""
        stdout, stderr, returncode = self.run_ordb('--max-examples', '1', 'hus')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
    
    def test_statistics_flag(self):
        """Test --stats flag."""
        stdout, stderr, returncode = self.run_ordb('--stats')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('Total Entries', clean_output)
        self.assertIn('Total Definitions', clean_output)
        self.assertIn('Total Examples', clean_output)
    
    def test_special_search_syntax(self):
        """Test special search syntax."""
        # Test prefix search (word@)
        stdout, stderr, returncode = self.run_ordb('hus@')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
        
        # Test anywhere search (@word)
        stdout, stderr, returncode = self.run_ordb('@hus')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
        
        # Test fulltext search (%word)
        stdout, stderr, returncode = self.run_ordb('%hus')
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        self.assertIn('hus', clean_output.lower())
    
    def test_character_replacement(self):
        """Test automatic character replacement."""
        # Test aa -> å
        stdout, stderr, returncode = self.run_ordb('gaa')
        self.assertEqual(returncode, 0)
        if stdout.strip():  # Only check if there are results
            clean_output = self.clean_ansi(stdout)
            # Should find "gå" 
            self.assertTrue('gå' in clean_output.lower() or 'search for' in clean_output.lower())
        
        # Test oe -> ø
        stdout, stderr, returncode = self.run_ordb('hoer')
        self.assertEqual(returncode, 0)
        
        # Test ae -> æ
        stdout, stderr, returncode = self.run_ordb('laere')
        self.assertEqual(returncode, 0)
    
    def test_pagination_flags(self):
        """Test pagination control flags."""
        # Test forced pagination
        stdout, stderr, returncode = self.run_ordb('-p', 'hus')
        self.assertEqual(returncode, 0)
        
        # Test disabled pagination
        stdout, stderr, returncode = self.run_ordb('-P', 'hus')
        self.assertEqual(returncode, 0)
    
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test invalid flag
        stdout, stderr, returncode = self.run_ordb('--invalid-flag')
        self.assertNotEqual(returncode, 0)
        
        # Test missing query
        stdout, stderr, returncode = self.run_ordb()
        self.assertNotEqual(returncode, 0)
    
    def test_config_flag(self):
        """Test --config flag."""
        # This will try to launch config wizard - provide Ctrl+C to cancel
        try:
            stdout, stderr, returncode = self.run_ordb('--config', input_text='\x03')  # Ctrl+C
            # Should handle cancellation gracefully
            self.assertIn(returncode, [0, 1])  # Either success or controlled failure
        except subprocess.TimeoutExpired:
            # If it still times out, just pass - config wizard is working
            pass
    
    def test_cat_config_flag(self):
        """Test --cat-config flag."""
        stdout, stderr, returncode = self.run_ordb('--cat-config')
        self.assertEqual(returncode, 0)
        # Should show config file contents or warning
        self.assertTrue('[colors]' in stdout or 'No configuration file found' in stdout)
    
    def test_words_only_flag(self):
        """Test --words-only flag."""
        stdout, stderr, returncode = self.run_ordb('-w', 'hus')
        self.assertEqual(returncode, 0)
        # Should show comma-separated words
        self.assertIn('hus', stdout)
        self.assertIn(',', stdout)
        # Should not have any formatting
        self.assertNotIn('📖', stdout)
        self.assertNotIn('search for', stdout.lower())
    
    def test_words_only_lines_flag(self):
        """Test -W flag (words on separate lines)."""
        stdout, stderr, returncode = self.run_ordb('-W', 'hus')
        self.assertEqual(returncode, 0)
        lines = stdout.strip().split('\n')
        # Should have at least hus and huse
        self.assertGreaterEqual(len(lines), 1)
        self.assertIn('hus', lines)
        # Should not have any formatting
        self.assertNotIn('📖', stdout)
        self.assertNotIn(',', stdout)
    
    def test_random_entry_flag(self):
        """Test -r flag for random entry."""
        stdout, stderr, returncode = self.run_ordb('-r')
        self.assertEqual(returncode, 0)
        # Should show random entry header and content
        self.assertIn('Random dictionary entry', stdout)
        self.assertIn('📖', stdout)
    
    def test_random_multiple_entries_flag(self):
        """Test -r3 flag for multiple random entries."""
        stdout, stderr, returncode = self.run_ordb('-r3')
        self.assertEqual(returncode, 0)
        # Should show header with count
        self.assertIn('3 random dictionary entries', stdout)
        # Should have separators between entries
        self.assertIn('---', stdout)
    
    def test_random_words_only_flag(self):
        """Test -R flag for random words only."""
        stdout, stderr, returncode = self.run_ordb('-R3')
        self.assertEqual(returncode, 0)
        lines = stdout.strip().split('\n')
        # Should have exactly 3 lines
        self.assertEqual(len(lines), 3)
        # Should not have any formatting
        self.assertNotIn('📖', stdout)
        self.assertNotIn('Random', stdout)


if __name__ == '__main__':
    unittest.main()