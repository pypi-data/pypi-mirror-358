#!/usr/bin/env python3
"""
Unit tests for utils.py module.
Tests utility functions used throughout the ordb application.
"""

import unittest
import sys
import io
from unittest.mock import patch, MagicMock, call
import platform

# Add src directory to path for testing
sys.path.insert(0, 'src')

from ordb.utils import (
    get_terminal_size, get_single_keypress, clean_ansi_codes,
    find_entry_start, truncate_text, format_percentage
)


class TestUtilsFunctions(unittest.TestCase):
    """Test all utility functions."""
    
    def test_get_terminal_size_default(self):
        """Test get_terminal_size returns default values when no terminal."""
        with patch('shutil.get_terminal_size') as mock_get_size:
            mock_get_size.side_effect = OSError("No terminal")
            rows, columns = get_terminal_size()
            self.assertEqual(rows, 24)
            self.assertEqual(columns, 80)
    
    def test_get_terminal_size_actual(self):
        """Test get_terminal_size returns actual terminal size."""
        with patch('shutil.get_terminal_size') as mock_get_size:
            # Mock terminal size - the function unpacks with columns, rows = get_terminal_size()
            # So we need to return something that can be unpacked to (columns, rows)
            mock_terminal = MagicMock()
            mock_terminal.columns = 120
            mock_terminal.lines = 30
            # Make it iterable so it can be unpacked
            mock_terminal.__iter__ = lambda self: iter([120, 30])  # columns, rows
            mock_get_size.return_value = mock_terminal
            
            rows, columns = get_terminal_size()
            self.assertEqual(rows, 30)
            self.assertEqual(columns, 120)
            mock_get_size.assert_called_once()
    
    def test_get_single_keypress_windows(self):
        """Test get_single_keypress on Windows."""
        # Simulate termios failure to trigger Windows path
        with patch('termios.tcgetattr') as mock_tcgetattr, \
             patch('builtins.__import__') as mock_import:
            
            mock_tcgetattr.side_effect = Exception("No termios")
            
            # Mock msvcrt module import
            mock_msvcrt = MagicMock()
            mock_msvcrt.getch.return_value = b'a'
            
            def side_effect(name, *args):
                if name == 'msvcrt':
                    return mock_msvcrt
                return __import__(name, *args)
            
            mock_import.side_effect = side_effect
            
            result = get_single_keypress()
            self.assertEqual(result, 'a')
    
    def test_get_single_keypress_unix(self):
        """Test get_single_keypress on Unix-like systems."""
        with patch('sys.stdin.fileno', return_value=0), \
             patch('termios.tcgetattr') as mock_tcgetattr, \
             patch('termios.tcsetattr') as mock_tcsetattr, \
             patch('tty.setraw') as mock_setraw, \
             patch('sys.stdin.read') as mock_read:
            
            mock_tcgetattr.return_value = ['old_settings']
            mock_read.return_value = 'b'
            
            result = get_single_keypress()
            self.assertEqual(result, 'b')
            
            # Verify termios functions were called
            mock_tcgetattr.assert_called_once()
            mock_setraw.assert_called_once()
            mock_tcsetattr.assert_called_once()
    
    def test_get_single_keypress_unix_special_keys(self):
        """Test get_single_keypress with special keys on Unix."""
        special_keys = ['\x1b', '\r', '\n', '\t', ' ']
        
        for key in special_keys:
            with patch('sys.stdin.fileno', return_value=0) as mock_fileno, \
                 patch('termios.tcgetattr') as mock_tcgetattr, \
                 patch('termios.tcsetattr') as mock_tcsetattr, \
                 patch('tty.setraw') as mock_setraw, \
                 patch('sys.stdin.read') as mock_read:
                
                mock_tcgetattr.return_value = ['old_settings']
                mock_read.return_value = key
                
                result = get_single_keypress()
                self.assertEqual(result, key)
    
    def test_get_single_keypress_unix_termios_exception(self):
        """Test get_single_keypress when termios operations fail."""
        with patch('sys.stdin.fileno', return_value=0), \
             patch('termios.tcgetattr') as mock_tcgetattr, \
             patch('termios.tcsetattr') as mock_tcsetattr, \
             patch('tty.setraw') as mock_setraw, \
             patch('sys.stdin.read') as mock_read, \
             patch('builtins.input', return_value='fallback'):
            
            mock_tcgetattr.return_value = ['old_settings']
            mock_tcsetattr.side_effect = Exception("Terminal error")
            mock_read.return_value = 'x'
            
            # Should fall back to input() when termios operations fail
            result = get_single_keypress()
            self.assertEqual(result, 'fallback')
    
    def test_get_single_keypress_windows_decode_error(self):
        """Test get_single_keypress on Windows with decode error."""
        with patch('termios.tcgetattr') as mock_tcgetattr, \
             patch('builtins.__import__') as mock_import:
            
            mock_tcgetattr.side_effect = Exception("No termios")
            
            # Mock msvcrt module with decode error
            mock_msvcrt = MagicMock()
            mock_msvcrt.getch.return_value = b'\xff'  # Invalid UTF-8
            
            def side_effect(name, *args):
                if name == 'msvcrt':
                    return mock_msvcrt
                return __import__(name, *args)
            
            mock_import.side_effect = side_effect
            
            # Should fall back to input() when decode fails
            with patch('builtins.input', return_value='fallback'):
                result = get_single_keypress()
                self.assertEqual(result, 'fallback')
    
    def test_get_single_keypress_stdin_fileno_error(self):
        """Test get_single_keypress when stdin.fileno() fails."""
        with patch('sys.stdin.fileno') as mock_fileno, \
             patch('builtins.input', return_value='no_tty'):
            
            mock_fileno.side_effect = OSError("Not a TTY")
            
            result = get_single_keypress()
            self.assertEqual(result, 'no_tty')
    
    @unittest.skip("Test hangs due to complex stdin/termios mocking")
    def test_get_single_keypress_keyboard_interrupt(self):
        """Test get_single_keypress handles KeyboardInterrupt."""
        with patch('sys.stdin.fileno', return_value=0), \
             patch('termios.tcgetattr') as mock_tcgetattr, \
             patch('termios.tcsetattr') as mock_tcsetattr, \
             patch('tty.setraw') as mock_setraw, \
             patch('sys.stdin.read') as mock_read:
            
            mock_tcgetattr.return_value = ['old_settings']
            mock_read.side_effect = KeyboardInterrupt()
            
            # Should propagate KeyboardInterrupt
            with self.assertRaises(KeyboardInterrupt):
                get_single_keypress()
    
    def test_get_single_keypress_exception(self):
        """Test get_single_keypress handles exceptions gracefully."""
        # Mock both termios and msvcrt to fail, triggering input() fallback
        with patch('termios.tcgetattr') as mock_tcgetattr, \
             patch('builtins.__import__') as mock_import, \
             patch('builtins.input') as mock_input:
            
            mock_tcgetattr.side_effect = Exception("Terminal error")
            
            def side_effect(name, *args):
                if name == 'msvcrt':
                    raise ImportError("No msvcrt")
                return __import__(name, *args)
            
            mock_import.side_effect = side_effect
            mock_input.return_value = 'fallback'
            
            result = get_single_keypress()
            self.assertEqual(result, 'fallback')
    
    def test_clean_ansi_codes_removes_colors(self):
        """Test clean_ansi_codes removes ANSI color codes."""
        colored_text = "\033[91mRed text\033[0m and \033[92mgreen text\033[0m"
        clean_text = clean_ansi_codes(colored_text)
        self.assertEqual(clean_text, "Red text and green text")
    
    def test_clean_ansi_codes_no_codes(self):
        """Test clean_ansi_codes with text that has no ANSI codes."""
        plain_text = "This is plain text"
        clean_text = clean_ansi_codes(plain_text)
        self.assertEqual(clean_text, plain_text)
    
    def test_clean_ansi_codes_empty_string(self):
        """Test clean_ansi_codes with empty string."""
        clean_text = clean_ansi_codes("")
        self.assertEqual(clean_text, "")
    
    def test_find_entry_start_found(self):
        """Test find_entry_start finds entry header."""
        lines = [
            "Some content",
            "More content", 
            "📖 hus [noun] (masculine)",
            "Definition here",
            "Another line"
        ]
        
        result = find_entry_start(lines, 1)
        self.assertEqual(result, 2)  # Index of the entry header
    
    def test_find_entry_start_not_found(self):
        """Test find_entry_start when no entry header found."""
        lines = [
            "Some content",
            "More content",
            "No entry header here"
        ]
        
        result = find_entry_start(lines, 0)
        self.assertEqual(result, 0)  # Returns 0 when not found
    
    def test_find_entry_start_from_end(self):
        """Test find_entry_start when starting from end of list."""
        lines = [
            "📖 first [noun]",
            "Content",
            "📖 second [verb]",
            "More content"
        ]
        
        result = find_entry_start(lines, 3)
        self.assertEqual(result, 2)  # Should find the nearest entry header backwards
    
    def test_truncate_text_no_truncation_needed(self):
        """Test truncate_text when text is shorter than max_length."""
        text = "Short text"
        result = truncate_text(text, 20)
        self.assertEqual(result, "Short text")
    
    def test_truncate_text_truncation_needed(self):
        """Test truncate_text when text exceeds max_length."""
        text = "This is a very long text that needs truncation"
        result = truncate_text(text, 20)
        self.assertEqual(result, "This is a very lo...")
        self.assertEqual(len(result), 20)
    
    def test_truncate_text_custom_suffix(self):
        """Test truncate_text with custom suffix."""
        text = "Long text here"
        result = truncate_text(text, 10, suffix=" [more]")
        self.assertEqual(result, "Lon [more]")
        self.assertEqual(len(result), 10)
    
    def test_truncate_text_exact_length(self):
        """Test truncate_text when text is exactly max_length."""
        text = "Exactly20characters!"
        result = truncate_text(text, 20)
        self.assertEqual(result, "Exactly20characters!")
    
    def test_format_percentage_basic(self):
        """Test format_percentage with basic values."""
        result = format_percentage(25, 100)
        self.assertEqual(result, "25.0%")
    
    def test_format_percentage_zero_total(self):
        """Test format_percentage with zero total."""
        result = format_percentage(5, 0)
        self.assertEqual(result, "0.0%")
    
    def test_format_percentage_custom_decimal_places(self):
        """Test format_percentage with custom decimal places."""
        result = format_percentage(1, 3, decimal_places=2)
        self.assertEqual(result, "33.33%")
    
    def test_format_percentage_zero_decimal_places(self):
        """Test format_percentage with zero decimal places."""
        result = format_percentage(1, 3, decimal_places=0)
        self.assertEqual(result, "33%")
    
    def test_format_percentage_exact_division(self):
        """Test format_percentage with exact division."""
        result = format_percentage(50, 100, decimal_places=1)
        self.assertEqual(result, "50.0%")


if __name__ == '__main__':
    unittest.main()