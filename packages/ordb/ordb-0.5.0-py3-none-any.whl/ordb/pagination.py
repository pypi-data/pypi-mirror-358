"""Pagination and terminal UI for ordb."""

import re
import sys
from .utils import get_terminal_size, get_single_keypress, find_entry_start


def paginate_output(text, page_size=None, force_pagination=False, disable_pagination=False):
    """Advanced pagination with scrolling support, preserving ANSI color codes."""
    from .config import search_config, Colors
    
    # Check if pagination should be used
    if disable_pagination:
        use_pagination = False
    else:
        use_pagination = force_pagination or search_config.pagination
    
    if not use_pagination:
        print(text)
        return
    
    lines = text.strip().split('\n')
    config_page_size = page_size  # Store the original configured page size
    current_line = 0
    
    while current_line < len(lines):
        # Recalculate terminal size and page size on each iteration
        # to handle terminal resizing during pagination
        terminal_rows, terminal_cols = get_terminal_size()
        
        if config_page_size is None or config_page_size == 0:
            # Use terminal height minus 2 lines for the status/prompt
            effective_page_size = max(3, terminal_rows - 2)  # Minimum 3 lines of content
        else:
            # Use configured page size but still respect terminal size if smaller
            # Allow very small terminals but ensure at least 3 lines of content
            effective_page_size = min(config_page_size, max(3, terminal_rows - 2))
        
        # If output is short enough for current terminal size, don't paginate
        if len(lines) <= effective_page_size and current_line == 0:
            print(text)
            return
        
        # Ensure current_line is within valid bounds after potential terminal resize
        max_start_line = max(0, len(lines) - effective_page_size)
        current_line = min(current_line, max_start_line)
        
        # Clear screen and move cursor to top (if enabled)
        if search_config.clear_screen:
            print('\033[2J\033[H', end='')
        else:
            # Just add some separation without clearing
            if current_line > 0:  # Not the first page
                print('\n' + '='*50 + ' PAGE ' + '='*50)
        
        # Calculate which lines to show using current effective page size
        # Reserve 7 lines for the status prompt to prevent auto-scrolling, but only on the first page
        if current_line == 0:
            # First page - reserve space to prevent auto-scrolling
            display_lines = max(3, effective_page_size - 7)
        else:
            # All other pages - use full page size
            display_lines = effective_page_size
        end_line = min(current_line + display_lines, len(lines))
        
        # Simply show the current page without complex context logic for line navigation
        page_lines = lines[current_line:end_line]
        
        # Display the current page
        print('\n'.join(page_lines))
        
        # Show status line if not at the end
        if end_line < len(lines):
            remaining_lines = len(lines) - end_line
            percentage = int((end_line / len(lines)) * 100)
            # Show terminal size info if it's being auto-detected
            size_info = f" (terminal: {terminal_rows}x{terminal_cols})" if config_page_size == 0 or config_page_size is None else ""
            status = f"{Colors.INFO}--More-- ({percentage}%, {remaining_lines} lines remaining{size_info}) [Space/Enter: next page, b: previous page, j/k/↑↓: line up/down, q: quit]{Colors.END}"
            print(f"\n{status}", end='', flush=True)
            
            # Get user input
            try:
                key = get_single_keypress()
                
                if key in ['q', 'Q']:
                    print(f"\n{Colors.INFO}Output truncated by user.{Colors.END}")
                    break
                elif key in [' ', '\r', '\n']:  # Space, Enter
                    # Move to next page - the overlap will be handled in the next iteration
                    current_line = end_line
                elif key == 'b':  # b key - scroll back one page
                    current_line = max(current_line - effective_page_size, 0)
                elif key == 'j':  # j key - scroll down one line
                    current_line = min(current_line + 1, max(0, len(lines) - 1))
                elif key == 'k':  # k key - scroll up one line  
                    current_line = max(current_line - 1, 0)
                elif key == '\x1b':  # Escape sequence (arrow keys)
                    # Read the remaining part of the arrow key sequence
                    try:
                        next_char = get_single_keypress()
                        if next_char == '[':
                            direction = get_single_keypress()
                            if direction == 'B':  # Down arrow
                                current_line = min(current_line + 1, max(0, len(lines) - 1))
                            elif direction == 'A':  # Up arrow
                                current_line = max(current_line - 1, 0)
                    except:
                        pass
                else:
                    # Any other key moves to next page
                    current_line = end_line
                    
            except (KeyboardInterrupt, EOFError):
                print(f"\n{Colors.INFO}Output truncated.{Colors.END}")
                break
        else:
            # At the end of the document - still allow navigation
            print(f"\n{Colors.INFO}(END) [q: quit, b/k/↑: scroll up]{Colors.END}", end='', flush=True)
            try:
                key = get_single_keypress()
                
                if key in ['q', 'Q']:
                    break
                elif key == 'b':  # b key - scroll back one page
                    current_line = max(current_line - effective_page_size, 0)
                elif key == 'k':  # k key - scroll up one line
                    current_line = max(current_line - 1, 0)
                elif key == '\x1b':  # Escape sequence (arrow keys)
                    # Read the remaining part of the arrow key sequence
                    try:
                        next_char = get_single_keypress()
                        if next_char == '[':
                            direction = get_single_keypress()
                            if direction == 'A':  # Up arrow
                                current_line = max(current_line - 1, 0)
                    except:
                        pass
                elif key in [' ', '\r', '\n']:  # Space, Enter - exit at end
                    break
                # Any other key - continue loop (no action)
            except (KeyboardInterrupt, EOFError):
                break
    
    # Clear the status line and restore normal output
    print('\033[K')  # Clear current line