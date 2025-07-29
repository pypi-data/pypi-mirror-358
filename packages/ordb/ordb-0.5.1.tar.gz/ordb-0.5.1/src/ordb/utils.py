"""Utility functions for ordb."""

import re
import sys


def get_terminal_size():
    """Get terminal size, with fallback to default values."""
    try:
        import shutil
        columns, rows = shutil.get_terminal_size()
        return rows, columns
    except:
        return 24, 80  # Default fallback


def get_single_keypress():
    """Get a single keypress from the user without requiring Enter.
    
    Cross-platform implementation supporting Unix/Linux/macOS (termios) 
    and Windows (msvcrt) with fallback to standard input().
    """
    try:
        import sys
        import tty
        import termios
        
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            char = sys.stdin.read(1)
            return char
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    except:
        # Fallback for systems without termios (Windows)
        try:
            import msvcrt
            return msvcrt.getch().decode('utf-8')
        except:
            # Final fallback - use input()
            return input()


def clean_ansi_codes(text):
    """Remove ANSI color codes from text.
    
    Useful for testing, text processing, and terminal compatibility.
    """
    return re.sub(r'\x1b\[[0-9;]*m', '', text)


def find_entry_start(lines, from_line):
    """Find the start of the dictionary entry that contains the given line.
    
    Searches backwards and forwards from the given line to find the nearest
    dictionary entry header (indicated by 📖 emoji).
    """
    # Look backwards from the current line to find an entry header (📖)
    for i in range(from_line, -1, -1):
        # Remove ANSI codes to check for entry header
        clean_line = clean_ansi_codes(lines[i])
        if clean_line.strip().startswith('📖'):
            return i
    
    # If no entry header found going backwards, look forwards
    for i in range(from_line + 1, len(lines)):
        clean_line = clean_ansi_codes(lines[i])
        if clean_line.strip().startswith('📖'):
            return i
    
    return 0  # If no entry header found anywhere, return start of document


def truncate_text(text, max_length, suffix="..."):
    """Truncate text to maximum length, adding suffix if truncated."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def format_percentage(value, total, decimal_places=1):
    """Format a percentage with proper handling of zero division."""
    if total == 0:
        return "0.0%"
    return f"{(value / total * 100):.{decimal_places}f}%"