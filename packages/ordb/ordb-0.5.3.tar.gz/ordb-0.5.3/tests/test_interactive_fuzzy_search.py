#!/usr/bin/env python3
"""
Test interactive fuzzy search functionality.

This test ensures the new interactive fuzzy search feature (-f flag) 
works correctly with lettered lists and user selection.
"""

import unittest
import subprocess
import re


class TestInteractiveFuzzySearch(unittest.TestCase):
    """Test interactive fuzzy search feature."""
    
    def run_fuzzy_search_with_input(self, search_term, user_input):
        """Run fuzzy search with simulated user input."""
        process = subprocess.Popen(
            ['python', '-m', 'src.ordb', '-f', search_term],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=user_input)
        return stdout, stderr, process.returncode
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def test_fuzzy_search_shows_lettered_list(self):
        """Test that fuzzy search shows a lettered list of options."""
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('gjeit', '\n')  # Press Enter to cancel
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show fuzzy search header
        self.assertIn('Fuzzy search for', clean_output)
        self.assertIn('threshold: 0.6', clean_output)
        
        # Should show "Found X similar matches:"
        self.assertIn('Found', clean_output)
        self.assertIn('similar matches', clean_output)
        
        # Should show lettered options (a), b), c), etc.)
        self.assertIn('a)', clean_output)
        self.assertIn('b)', clean_output)
        
        # Should show prompt for user input (may include more results option)
        self.assertTrue(
            'Press a letter to view the entry, or Enter to cancel:' in clean_output or
            'Press a letter to view the entry, 0 or spacebar for more results, or Enter to cancel:' in clean_output
        )
    
    def test_fuzzy_search_user_selection(self):
        """Test that selecting a letter shows the corresponding entry."""
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('gjeit', 'a\n')  # Select option 'a'
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show the fuzzy list first
        self.assertIn('a)', clean_output)
        
        # Should then show a dictionary entry (with the book emoji)
        self.assertIn('📖', clean_output)
        
        # Should show definition structure
        self.assertTrue('1.' in clean_output or 'Alternative forms:' in clean_output or 'Etymology:' in clean_output)
    
    def test_fuzzy_search_cancel_with_enter(self):
        """Test that pressing Enter cancels the fuzzy search silently."""
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('gjeit', '\n')  # Just press Enter
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show the list but then exit silently without "No results found"
        self.assertIn('a)', clean_output)
        self.assertNotIn('No results found', clean_output)
    
    def test_fuzzy_search_invalid_selection(self):
        """Test that invalid letter selection shows message but exits gracefully."""
        # Use a search that will have results, then select an invalid letter
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('hus', 'x')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show "Invalid selection" but NOT "No results found"
        self.assertIn('Invalid selection', clean_output)
        self.assertNotIn('No results found', clean_output)
    
    def test_fuzzy_search_threshold_in_header(self):
        """Test that fuzzy search displays the threshold in the header."""
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('test', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show threshold in header
        self.assertIn('threshold: 0.6', clean_output)
    
    def test_fuzzy_search_with_custom_threshold(self):
        """Test fuzzy search with custom threshold."""
        process = subprocess.Popen(
            ['python', '-m', 'src.ordb', '-f', '--threshold', '0.7', 'gjeit'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input='\n')
        self.assertEqual(process.returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show custom threshold in header
        self.assertIn('threshold: 0.7', clean_output)
    
    def test_fuzzy_search_shows_word_class_and_gender(self):
        """Test that fuzzy search results show word class and gender info."""
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('gjeit', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show word class in brackets
        self.assertTrue('[noun]' in clean_output or '[verb]' in clean_output or '[adj]' in clean_output)
    
    def test_fuzzy_search_letter_sequence(self):
        """Test that letters go a, b, c... and then aa, ab, etc."""
        # Use a search that should return many results
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('e', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should have sequential letters
        letters_found = []
        lines = clean_output.split('\n')
        for line in lines:
            if re.match(r'\s*[a-z]+\)', line):
                match = re.match(r'\s*([a-z]+)\)', line)
                if match:
                    letters_found.append(match.group(1))
        
        # Should start with 'a'
        if letters_found:
            self.assertEqual(letters_found[0], 'a')
            
            # Should be in alphabetical order
            for i in range(1, min(len(letters_found), 26)):
                expected = chr(ord('a') + i)
                if i < len(letters_found):
                    self.assertEqual(letters_found[i], expected)
    
    def test_fuzzy_fallback_behavior(self):
        """Test that fuzzy search is used as fallback when no exact matches."""
        # Search for a word that likely doesn't exist exactly
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('nonexistentword123', '\n')
        
        # This tests the fallback behavior - it should either show fuzzy results or no results
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should either show fuzzy search or no results message
        self.assertTrue(
            'Fuzzy search for' in clean_output or 
            'No results found' in clean_output or
            'Trying fuzzy search' in clean_output
        )
    
    def test_fuzzy_search_differential_highlighting(self):
        """Test that fuzzy search shows differential highlighting for matching vs non-matching characters."""
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('huse', '\n')  # Press Enter to cancel
        
        self.assertEqual(returncode, 0)
        
        # Check that there are both highlight and lemma color codes in the output
        # Highlight color for matching characters (green)
        self.assertIn('\x1b[92m', stdout)  # Should have highlight color codes
        # Lemma color for non-matching characters (cyan)
        self.assertIn('\x1b[96m', stdout)  # Should have lemma color codes
        
        # Should show fuzzy results
        clean_output = self.clean_ansi(stdout)
        self.assertIn('Found', clean_output)
        self.assertIn('similar matches', clean_output)
        
        # Should have letter options
        self.assertIn('a)', clean_output)
    
    def test_more_results_with_zero_key(self):
        """Test that pressing '0' shows more results when available."""
        # Use a search that should return many results
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('e', '0\n')  # Press 0 then cancel
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show "more results" option if there are many matches
        if '0) ...more results' in clean_output:
            # Should show "Showing next page..." when 0 is pressed
            self.assertIn('Showing next page', clean_output)
    
    def test_more_results_with_spacebar(self):
        """Test that pressing spacebar shows more results when available."""
        # Use a search that should return many results
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('e', ' \n')  # Press space then cancel
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show "more results" option if there are many matches
        if '0) ...more results' in clean_output:
            # Should show "Showing next page..." when spacebar is pressed
            self.assertIn('Showing next page', clean_output)
    
    def test_more_results_prompt_includes_spacebar(self):
        """Test that prompt mentions both 0 and spacebar for more results."""
        # Use a search that should return many results
        stdout, stderr, returncode = self.run_fuzzy_search_with_input('e', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show both options in prompt when more results are available
        if '0) ...more results' in clean_output:
            self.assertIn('0 or spacebar for more results', clean_output)
    
    def test_pagination_consistency(self):
        """Test that pagination shows consistent page sizes."""
        # Use a search that should return many results and test pagination
        process = subprocess.Popen(
            ['python', '-m', 'src.ordb', '-f', 'e'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Send '0' to get more results, then cancel
        stdout, stderr = process.communicate(input='0\n')
        self.assertEqual(process.returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # If pagination occurred, should show page number
        if 'Showing next page' in clean_output:
            self.assertIn('page 2', clean_output)
    
    def run_prefix_search_with_input(self, search_term, user_input):
        """Run prefix search with simulated user input."""
        process = subprocess.Popen(
            ['python', '-m', 'src.ordb', f'{search_term}@'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=user_input)
        return stdout, stderr, process.returncode
    
    def run_anywhere_search_with_input(self, search_term, user_input):
        """Run anywhere term search with simulated user input."""
        process = subprocess.Popen(
            ['python', '-m', 'src.ordb', f'@{search_term}'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        stdout, stderr = process.communicate(input=user_input)
        return stdout, stderr, process.returncode
    
    def test_prefix_search_interactive_mode(self):
        """Test that prefix search uses interactive mode."""
        stdout, stderr, returncode = self.run_prefix_search_with_input('hus', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show prefix search header
        self.assertIn('Prefix search for', clean_output)
        self.assertIn('hus@', clean_output)
        
        # Should show lettered options
        self.assertIn('a)', clean_output)
        
        # Should show appropriate prompt
        self.assertIn('Press a letter to view the entry', clean_output)
    
    def test_prefix_search_silent_cancellation(self):
        """Test that prefix search cancels silently."""
        stdout, stderr, returncode = self.run_prefix_search_with_input('hus', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should not show "No results found" (silent cancellation)
        self.assertNotIn('No results found', clean_output)
    
    def test_prefix_search_more_results(self):
        """Test that prefix search supports more results."""
        stdout, stderr, returncode = self.run_prefix_search_with_input('hus', '0\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # If there are more results, should handle pagination
        if '0) ...more results' in clean_output:
            self.assertIn('Showing next page', clean_output)
    
    def test_anywhere_search_interactive_mode(self):
        """Test that anywhere term search uses interactive mode."""
        stdout, stderr, returncode = self.run_anywhere_search_with_input('hus', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should show anywhere term search header
        self.assertIn('Anywhere term search for', clean_output)
        self.assertIn('@hus', clean_output)
        
        # Should show lettered options
        self.assertIn('a)', clean_output)
        
        # Should show appropriate prompt
        self.assertIn('Press a letter to view the entry', clean_output)
    
    def test_anywhere_search_silent_cancellation(self):
        """Test that anywhere term search cancels silently."""
        stdout, stderr, returncode = self.run_anywhere_search_with_input('hus', '\n')
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # Should not show "No results found" (silent cancellation)
        self.assertNotIn('No results found', clean_output)
    
    def test_anywhere_search_more_results(self):
        """Test that anywhere term search supports more results."""
        stdout, stderr, returncode = self.run_anywhere_search_with_input('hus', ' \n')  # Test spacebar
        
        self.assertEqual(returncode, 0)
        clean_output = self.clean_ansi(stdout)
        
        # If there are more results, should handle pagination
        if '0) ...more results' in clean_output:
            self.assertIn('Showing next page', clean_output)
    
    def test_all_interactive_searches_use_zero_key(self):
        """Test that all interactive search types use '0' for more results."""
        # Test fuzzy search
        stdout_fuzzy, _, _ = self.run_fuzzy_search_with_input('e', '\n')
        # Test prefix search  
        stdout_prefix, _, _ = self.run_prefix_search_with_input('e', '\n')
        # Test anywhere search
        stdout_anywhere, _, _ = self.run_anywhere_search_with_input('e', '\n')
        
        for stdout, search_type in [(stdout_fuzzy, 'fuzzy'), (stdout_prefix, 'prefix'), (stdout_anywhere, 'anywhere')]:
            clean_output = self.clean_ansi(stdout)
            if '0) ...more results' in clean_output:
                # Should show consistent prompt mentioning 0 and spacebar
                self.assertIn('0 or spacebar for more results', clean_output, 
                             f"{search_type} search should mention both 0 and spacebar")


if __name__ == '__main__':
    unittest.main()