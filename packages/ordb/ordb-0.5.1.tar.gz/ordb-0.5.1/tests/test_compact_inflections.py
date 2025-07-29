#!/usr/bin/env python3
"""
Test script to verify compact inflection display works correctly.
Inflections should now be on a single line instead of separate lines.
"""

import subprocess
import re
import sys

def test_compact_inflections():
    """Test that inflections are displayed on a single compact line."""
    
    # Test with a noun (hus)
    result = subprocess.run(['python', '-m', 'src.ordb', 'hus', '--limit', '1', '--no-paginate'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Find the inflections section
    lines = output.split('\n')
    inflection_line = None
    for line in lines:
        if 'Inflections:' in line:
            inflection_line = line
            break
    
    assert inflection_line is not None, "Could not find 'Inflections:' line"
    
    # Check that the inflections are on the same line as the header
    assert 'Singular:' in inflection_line and 'Plural:' in inflection_line, "Noun inflections not compact"
    
    # Test with a verb (gå)
    result = subprocess.run(['python', '-m', 'src.ordb', 'gå', '--limit', '1', '--no-paginate'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    # Find the inflections section
    lines = output.split('\n')
    inflection_line = None
    for line in lines:
        if 'Inflections:' in line:
            inflection_line = line
            break
    
    assert inflection_line is not None, "Could not find 'Inflections:' line for verb"
    
    # Check that the verb inflections are on the same line
    assert ('Infinitive:' in inflection_line and 'Present:' in inflection_line and 'Past:' in inflection_line), "Verb inflections not compact"

def test_no_multiline_inflections():
    """Test that inflections no longer span multiple lines."""
    
    result = subprocess.run(['python', '-m', 'src.ordb', 'hus', '--limit', '1', '--no-paginate'], 
                          capture_output=True, text=True)
    output = result.stdout
    
    lines = output.split('\n')
    
    # Find the inflections line
    inflection_line_index = None
    for i, line in enumerate(lines):
        if 'Inflections:' in line:
            inflection_line_index = i
            break
    
    assert inflection_line_index is not None, "Could not find inflections line"
    
    # Check the next few lines to ensure they don't contain inflection categories
    next_lines = lines[inflection_line_index + 1:inflection_line_index + 4]
    
    for line in next_lines:
        # Skip empty lines and lines that are clearly not inflection categories
        if line.strip() == '' or 'Faste uttrykk:' in line or '•' in line:
            continue
        
        # Check if this line contains inflection categories that should now be on the main line
        assert not any(cat in line for cat in ['Singular:', 'Plural:', 'Infinitive:', 'Present:', 'Past:']), f"Found inflection category on separate line: {line.strip()}"

if __name__ == '__main__':
    print("Testing compact inflections...")
    print("=" * 60)
    
    tests = [
        test_compact_inflections,
        test_no_multiline_inflections
    ]
    
    passed = 0
    total = len(tests)
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
            print(f"✅ {test_func.__name__} passed")
        except Exception as e:
            print(f"❌ {test_func.__name__} failed with error: {e}")
    
    print("=" * 60)
    if passed == total:
        print(f"✅ All {total} tests passed!")
    else:
        print(f"❌ {passed}/{total} tests passed")
        sys.exit(1)