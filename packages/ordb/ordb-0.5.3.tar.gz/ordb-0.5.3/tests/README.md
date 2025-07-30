# Test Suite Documentation

This directory contains comprehensive tests for the ordb Norwegian dictionary search tool. The test suite includes both unit tests and integration tests covering all major functionality.

## Test Files Overview

### Core Functionality Tests

**`test_comprehensive_functionality.py`** - Main integration test suite (21 tests)
- Tests all command-line flags and options
- Validates search modes: exact, fuzzy (`-f`), prefix (`word@`), anywhere (`@word`, `-a`), fulltext (`%word`), expressions (`-x`)
- Tests word type filters: `--noun`, `--verb`, `--adj`, `--adv`
- Validates output modes: `--only-examples`, `--only-etymology`, `--only-inflections`, `--no-definitions`, `--no-examples`
- Tests pagination controls: `-p` (force), `-P` (disable)
- Validates configuration wizard (`-c`), statistics (`-s`), and version (`-v`) commands
- Tests Norwegian character replacement and search limits

**`test_database_integrity.py`** - Database validation and health checks (13 tests)
- Validates database schema: articles, definitions, examples, expression_links tables
- Tests data integrity: no duplicate definitions, proper cross-references
- Validates record counts: 90,841+ articles, 111,425+ definitions, 83,849+ examples
- Tests specific word expressions: 'stein' (15 expressions), 'hjerte' (25 expressions)
- Validates cross-reference links: "på huset" → "hus", "fullt hus" → "hus"/"full"
- Tests word class distribution and sub-definition integration
- Ensures no malformed output in search results

**`test_interactive_fuzzy_search.py`** - Interactive search functionality (21 tests)
- Tests fuzzy search interactive lettered lists (`-f`)
- Validates prefix search interactive mode (`word@`)
- Tests anywhere term search interactive mode (`@word`)
- Tests "more results" pagination with '0' key and spacebar
- Validates differential highlighting for fuzzy matches
- Tests silent cancellation (Enter key) and graceful invalid selection handling
- Tests letter sequence generation (a-z, aa-ab, etc.)
- Validates user selection and entry display functionality

### Feature-Specific Tests

**`test_character_replacement.py`** - Norwegian character substitution (9 tests)
- Tests 'aa' → 'å' replacement in searches (e.g., 'gaa' finds 'gå')
- Tests 'oe' → 'ø' replacement (e.g., 'groen' finds 'grønn')
- Tests 'ae' → 'æ' replacement (e.g., 'vaere' finds 'være')
- Validates replacement works across all search modes
- Tests multiple replacements and uppercase handling

**`test_word_filters.py`** - Grammatical category filtering (4 tests)
- Tests `--adj` filter returns only adjectives
- Tests `--verb` filter returns only verbs
- Tests `--noun` filter returns only nouns
- Tests `--adv` filter returns only adverbs

**`test_pagination.py`** - Terminal pagination system (10 tests)
- Tests pagination enabled/disabled by configuration
- Validates force pagination with `-p` flag
- Tests pagination quit functionality with 'q' key
- Validates color preservation during pagination
- Tests entry header preservation with small page sizes
- Validates interaction with etymology and word filter flags

**`test_etymology_flags.py`** - Etymology display options (9 tests)
- Tests etymology-only flag (`-e`, `--only-etymology`)
- Validates etymology display format and content
- Tests etymology with different search modes
- Ensures proper header formatting for etymology-only output

**`test_inflection_flags.py`** - Inflection display options (9 tests)
- Tests inflections-only flag (`-i`, `--only-inflections`)
- Validates multiline inflection formatting
- Tests inflection display with different word types
- Ensures proper formatting for complex inflection tables

**`test_display_flags.py`** - Output control flags (4 tests)
- Tests `--no-definitions` excludes definition text
- Tests `--no-examples` excludes example sentences
- Validates `--only-examples` shows examples only
- Tests interaction between different display flags

### Configuration and Platform Tests

**`test_config_wizard_completeness.py`** - Configuration system validation (2 tests)
- Dynamically verifies wizard covers all SearchConfig settings
- Tests that save_config includes all settings
- Ensures no configuration drift between loader and wizard

**`test_platform_paths.py`** - Cross-platform compatibility (6 tests)
- Tests Unix/Linux path handling (`~/.ordb/`)
- Validates Windows path logic (APPDATA/LOCALAPPDATA)
- Tests path fallback behavior
- Validates directory creation and file operations

**`test_all_examples_and_config.py`** - Examples search and config integration (8 tests)
- Tests `--all-examples` flag across dictionary
- Validates configuration file settings for inflections/etymology
- Tests config defaults and file handling

### Specialized Tests

**`test_only_examples_expressions.py`** - Expression handling in examples mode (3 tests)
- Tests `--only-examples` includes fixed expressions
- Validates expression formatting in examples-only output

**`test_compact_inflections.py`** - Inflection formatting (2 tests)
- Tests compact, single-line inflection display
- Validates proper formatting without unwanted line breaks

**`test_general_fixes.py`** - General bug fixes and improvements (3 tests)
- Tests specific bug fixes and edge cases
- Validates regression prevention

## Test Suite Organization

The test suite is organized into two main categories:

### Unit Tests (255 tests)
- **test_cli_unit.py** - Command-line interface unit tests
- **test_config_unit.py** - Configuration system unit tests  
- **test_core_unit.py** - Core search functionality unit tests
- **test_display_unit.py** - Display formatting unit tests
- **test_pagination_unit.py** - Pagination system unit tests
- **test_utils_unit.py** - Utility functions unit tests
- **test_wizard_unit.py** - Configuration wizard unit tests

### Integration Tests (114 tests)
- **test_comprehensive_functionality.py** - Complete CLI workflow tests
- **test_database_integrity.py** - Database validation and health checks
- **test_interactive_fuzzy_search.py** - Interactive search functionality
- **test_character_replacement.py** - Norwegian character substitution
- **test_word_filters.py** - Grammatical category filtering
- **test_pagination.py** - Terminal pagination system
- **test_etymology_flags.py** - Etymology display options
- **test_inflection_flags.py** - Inflection display options
- **test_display_flags.py** - Output control flags
- **test_config_wizard_completeness.py** - Configuration system validation
- **test_platform_paths.py** - Cross-platform compatibility
- **test_all_examples_and_config.py** - Examples search and config integration
- **test_only_examples_expressions.py** - Expression handling
- **test_compact_inflections.py** - Inflection formatting

### Test Coverage Areas:
- **Interactive functionality**: Fuzzy search, pagination, user interaction
- **Core functionality**: Search modes, flags, basic operations  
- **Database integrity**: Data validation, schema, cross-references
- **Configuration system**: Wizard, platform paths, file handling
- **Display features**: Etymology flags, pagination, formatting
- **Language features**: Character replacement, Norwegian-specific functionality
- **Platform support**: Windows/Unix compatibility

## Running Tests

### Run Unit Tests (Fast, No Database Required)
```bash
# Run all unit tests
./tests/run_unit_tests.sh

# Or manually with unittest
python -m unittest discover tests/ -p "test_*_unit.py" -v
```

### Run Integration Tests (Requires Database)
```bash
# First ensure database is installed
ordb --help  # This will prompt to install database if needed

# Run integration tests (bypasses @unittest.skip decorators)
./tests/run_integration_tests.sh

# Or manually (will respect @unittest.skip decorators)
python -m unittest discover tests/ -v
```

**Important**: The `run_integration_tests.sh` script temporarily removes `@unittest.skip` decorators to actually run the integration tests. If you run tests manually with `unittest`, they will be skipped due to the decorators.

### Run Specific Test Files
```bash
# Unit tests
python -m unittest tests.test_cli_unit
python -m unittest tests.test_core_unit

# Integration tests  
python -m unittest tests.test_comprehensive_functionality
python -m unittest tests.test_database_integrity
```

### Test Runner Scripts
The project includes convenient test runner scripts:
- **run_unit_tests.sh** - Runs only unit tests (fast, isolated)
- **run_integration_tests.sh** - Runs integration tests (requires database)

## Test Requirements

### Unit Tests
- **No external dependencies**: Run without database or configuration files
- **Fast execution**: Isolated tests with mocked dependencies
- **Python 3.8+**: Compatible with all supported Python versions

### Integration Tests  
- **Database required**: Integration tests need the ordb database at `~/.ordb/articles.db`
- **Full application**: Tests use complete ordb installation (`python -m ordb`)
- **Interactive components**: Some tests simulate user input and keypress interactions
- **Temporary files**: Tests may create temporary configuration files
- **Anti-pagination**: Tests include `--no-paginate` flag to prevent pagination interference

### Important Notes
- **Test framework**: Uses Python `unittest` module (not pytest)
- **Skipped integration tests**: Most integration tests are currently marked with `@unittest.skip("Integration test - requires full app setup and may freeze")` due to hanging/freezing issues in automated test environments
- **Active integration tests**: Only a few integration tests currently run (like `test_platform_paths.py`)
- **Database initialization**: Run `ordb --help` first to install database if needed for integration tests
- **Test output**: When running integration tests, you'll see `OK (skipped=X)` for most test files due to skip decorators

## Test Coverage Areas

The test suite provides comprehensive coverage of:

### Search Functionality
- **All search modes**: exact, fuzzy, prefix, anywhere, fulltext, expressions-only
- **Interactive features**: lettered lists, more results pagination, keypress handling
- **Special syntax**: `word@`, `@word`, `%word` search patterns
- **Character replacement**: aa→å, oe→ø, ae→æ automatic substitution

### Display and Output
- **Output modes**: full entries, examples-only, etymology-only, inflections-only
- **Display controls**: hide definitions, hide examples, show only specific sections
- **Pagination**: terminal-aware pagination with navigation controls
- **Formatting**: ANSI color codes, compact inflections, proper headers

### Configuration System
- **Cross-platform paths**: Windows (%APPDATA%) and Unix (~/.ordb/) support
- **Configuration wizard**: interactive setup, all setting coverage
- **File handling**: creation, migration, default values
- **Backward compatibility**: legacy config file support

### Database and Content
- **Schema integrity**: proper table structure and relationships
- **Content validation**: no duplicates, proper cross-references
- **Language features**: Norwegian irregular verbs, word class classification
- **Expression system**: fixed expressions, cross-reference links

### User Experience
- **Error handling**: graceful failures, informative messages
- **Interactive features**: immediate keypress, silent cancellation
- **Command-line interface**: all flags, help text, version display
- **Platform compatibility**: Windows, macOS, Linux support

## Adding New Tests

When adding new tests, follow these patterns:

```python
import unittest
import subprocess
import sys
from pathlib import Path

# Add src to path for importing
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from ordb.utils import clean_ansi_codes

class TestNewFeature(unittest.TestCase):
    
    def run_ordb(self, *args, input_text=None):
        """Run ordb command and return stdout, stderr, returncode."""
        cmd = ['python', '-m', 'ordb'] + list(args)
        result = subprocess.run(cmd, capture_output=True, text=True, input=input_text)
        return result.stdout, result.stderr, result.returncode
    
    def test_new_functionality(self):
        """Test description of what this validates."""
        stdout, stderr, returncode = self.run_ordb('--new-flag', 'test_word')
        self.assertEqual(returncode, 0)
        clean_output = clean_ansi_codes(stdout)
        self.assertIn('expected_content', clean_output)

if __name__ == '__main__':
    unittest.main()
```

### Naming Conventions
- Test files: `test_<feature_name>.py`
- Test classes: `Test<FeatureName>`
- Test methods: `test_<specific_functionality>`
- Include comprehensive docstrings for all tests

### Best Practices
- Use `clean_ansi_codes()` to remove color codes before assertions
- Include `--no-paginate` flag to prevent pagination interference
- Test both success and failure cases
- Validate return codes, stdout content, and proper error handling
- Keep tests focused and independent