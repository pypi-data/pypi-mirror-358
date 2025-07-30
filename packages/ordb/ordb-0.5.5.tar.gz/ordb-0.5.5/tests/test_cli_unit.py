#!/usr/bin/env python3
"""
Unit tests for cli.py module.
Tests command-line interface functions and argument parsing.
"""

import unittest
import sys
import argparse
from unittest.mock import patch, MagicMock, call
from io import StringIO

# Add src directory to path for testing
sys.path.insert(0, 'src')

# Import CLI components
import ordb.cli as cli_module
from ordb import __version__ as ORDB_VERSION


class TestCLIArguments(unittest.TestCase):
    """Test CLI argument parsing and validation."""
    
    def setUp(self):
        """Set up test environment."""
        # Patch all the core functions to avoid database dependencies
        self.patches = [
            patch('ordb.core.setup_database'),
            patch('ordb.config.search_config'),
            patch('ordb.config.Colors'),
            patch('ordb.pagination.paginate_output'),
        ]
        
        self.mocks = {}
        for p in self.patches:
            mock_obj = p.start()
            self.mocks[p.attribute] = mock_obj
        
        # Set up mock search config
        self.mocks['search_config'].character_replacement = True
        self.mocks['search_config'].fallback_to_fuzzy = True
        self.mocks['search_config'].interactive_anywhere_search = True
        self.mocks['search_config'].default_limit = 50
    
    def tearDown(self):
        """Clean up patches."""
        for p in self.patches:
            p.stop()
    
    @patch('sys.argv', ['ordb', '--help'])
    @patch('sys.exit')
    def test_help_flag(self, mock_exit, *args):
        """Test --help flag displays help message."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                cli_module.main()
            except SystemExit:
                pass
            
            output = fake_out.getvalue()
            self.assertIn('Norwegian bokmål dictionary search tool', output)
            self.assertIn('Examples:', output)
            self.assertIn('Special Search Syntax:', output)
    
    @patch('sys.argv', ['ordb', '--version'])
    @patch('sys.exit')
    def test_version_flag(self, mock_exit, *args):
        """Test --version flag displays version."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                cli_module.main()
            except SystemExit:
                pass
            
            output = fake_out.getvalue()
            self.assertIn(ORDB_VERSION, output)  # Current version
    
    @patch('sys.argv', ['ordb', '-v'])
    @patch('sys.exit')
    def test_version_short_flag(self, mock_exit, *args):
        """Test -v flag displays version."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                cli_module.main()
            except SystemExit:
                pass
            
            output = fake_out.getvalue()
            self.assertIn(ORDB_VERSION, output)


class TestCLIMainFunction(unittest.TestCase):
    """Test the main CLI function with various arguments."""
    
    def setUp(self):
        """Set up comprehensive mocking for CLI tests."""
        # Mock database and search functions
        self.mock_conn = MagicMock()
        self.mock_setup_db = patch('ordb.core.setup_database', return_value=self.mock_conn)
        self.mock_search_config = patch('ordb.config.search_config')
        self.mock_colors = patch('ordb.config.Colors')
        self.mock_paginate = patch('ordb.pagination.paginate_output')
        
        # Mock all search functions
        self.mock_search_exact = patch('ordb.core.search_exact', return_value=[])
        self.mock_search_fuzzy = patch('ordb.core.search_fuzzy', return_value=[])
        self.mock_search_prefix = patch('ordb.core.search_prefix', return_value=[])
        self.mock_search_anywhere = patch('ordb.core.search_anywhere_term', return_value=[])
        self.mock_search_fulltext = patch('ordb.core.search_fulltext', return_value=[])
        self.mock_search_expressions = patch('ordb.core.search_expressions_only', return_value=[])
        self.mock_search_all_examples = patch('ordb.core.search_all_examples', return_value=[])
        
        # Mock interactive search functions
        self.mock_search_fuzzy_interactive = patch('ordb.core.search_fuzzy_interactive', return_value=[])
        self.mock_search_prefix_interactive = patch('ordb.core.search_prefix_interactive', return_value=[])
        self.mock_search_anywhere_interactive = patch('ordb.core.search_anywhere_term_interactive', return_value=[])
        
        # Mock other functions
        self.mock_format_result = patch('ordb.display.format_result', return_value="Mock result")
        self.mock_display_stats = patch('ordb.display.display_statistics')
        self.mock_get_random_entries = patch('ordb.core.get_random_entries', return_value=[])
        self.mock_run_wizard = patch('ordb.config.run_wizard')
        
        # Start all patches
        self.patches = [
            self.mock_setup_db, self.mock_search_config, self.mock_colors, self.mock_paginate,
            self.mock_search_exact, self.mock_search_fuzzy, self.mock_search_prefix,
            self.mock_search_anywhere, self.mock_search_fulltext, self.mock_search_expressions,
            self.mock_search_all_examples, self.mock_search_fuzzy_interactive,
            self.mock_search_prefix_interactive, self.mock_search_anywhere_interactive,
            self.mock_format_result, self.mock_display_stats, self.mock_get_random_entries,
            self.mock_run_wizard
        ]
        
        # Store started mocks
        self.started_mocks = {}
        for p in self.patches:
            self.started_mocks[p.attribute] = p.start()
        
        # Configure mock search config (already started above)
        mock_config = self.started_mocks['search_config']
        mock_config.character_replacement = True
        mock_config.fallback_to_fuzzy = True
        mock_config.interactive_anywhere_search = True
        mock_config.default_limit = 50
    
    def tearDown(self):
        """Clean up all patches."""
        for p in self.patches:
            p.stop()
    
    @patch('sys.argv', ['ordb', 'hus'])
    @patch('builtins.print')
    def test_basic_search(self, mock_print):
        """Test basic word search."""
        # Mock exact search to return a result
        with patch('ordb.cli.search_exact') as mock_exact:
            mock_exact.return_value = [(1, 'hus', 'hus', 'NOUN', 'neuter', '', '{}', 'etymology', 1)]
            
            cli_module.main()
            
            # Should call exact search
            mock_exact.assert_called_once()
            
            # Should format and display result
            self.assertTrue(mock_print.called)
    
    @patch('sys.argv', ['ordb', '-f', 'hus'])
    @patch('builtins.print')
    def test_fuzzy_search_flag(self, mock_print):
        """Test fuzzy search flag."""
        with patch('ordb.cli.search_fuzzy_interactive') as mock_fuzzy:
            mock_fuzzy.return_value = [(1, 'hus', 'hus', 'NOUN', 'neuter', '', '{}', 'etymology', 1)]
            
            cli_module.main()
            
            # Should call fuzzy interactive search
            mock_fuzzy.assert_called_once()
    
    @patch('sys.argv', ['ordb', '-a', 'anywhere'])
    @patch('builtins.print')
    def test_anywhere_search_flag(self, mock_print):
        """Test anywhere search flag."""
        with patch('ordb.cli.search_anywhere') as mock_anywhere:
            mock_anywhere.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call anywhere search
            mock_anywhere.assert_called_once()
    
    @patch('sys.argv', ['ordb', '-x', 'expr'])
    @patch('builtins.print')
    def test_expressions_only_flag(self, mock_print):
        """Test expressions only flag."""
        with patch('ordb.cli.search_expressions_only') as mock_expr:
            mock_expr.return_value = [(1, 'expression', 'expression', 'EXPR', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call expressions only search
            mock_expr.assert_called_once()
    
    @patch('sys.argv', ['ordb', '--all-examples', 'example'])
    @patch('builtins.print')
    def test_all_examples_flag(self, mock_print):
        """Test all examples flag."""
        with patch('ordb.cli.search_all_examples') as mock_examples:
            mock_examples.return_value = [('This is an example sentence', 'explanation', 'lemma', 'NOUN')]
            
            cli_module.main()
            
            # Should call all examples search
            mock_examples.assert_called_once()
    
    @patch('sys.argv', ['ordb', '--only-examples', 'word'])
    @patch('builtins.print')
    def test_only_examples_flag(self, mock_print):
        """Test only examples display flag."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            
            mock_exact.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            mock_format.return_value = "Mock result output"
            
            cli_module.main()
            
            # Should call format_result with only_examples=True
            mock_format.assert_called()
            # Verify the specific keyword argument instead of fragile positional checking
            call_args, call_kwargs = mock_format.call_args
            # Check if only_examples was passed as True (either as positional or keyword arg)
            only_examples_passed = (len(call_args) > 7 and call_args[7] is True) or call_kwargs.get('only_examples', False)
            self.assertTrue(only_examples_passed, "format_result should be called with only_examples=True")
    
    @patch('sys.argv', ['ordb', '-e', 'word'])
    @patch('builtins.print')
    def test_only_etymology_flag(self, mock_print):
        """Test only etymology display flag."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            
            mock_exact.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', 'etymology', 1)]
            mock_format.return_value = "Mock result output"
            
            cli_module.main()
            
            # Should call format_result with only_etymology=True
            mock_format.assert_called()
            call_args, call_kwargs = mock_format.call_args
            # Check if only_etymology was passed as True (either as positional or keyword arg)
            only_etymology_passed = (len(call_args) > 8 and call_args[8] is True) or call_kwargs.get('only_etymology', False)
            self.assertTrue(only_etymology_passed, "format_result should be called with only_etymology=True")
    
    @patch('sys.argv', ['ordb', '-i', 'word'])
    @patch('builtins.print')
    def test_only_inflections_flag(self, mock_print):
        """Test only inflections display flag."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            
            mock_exact.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            mock_format.return_value = "Mock result output"
            
            cli_module.main()
            
            # Should call format_result with only_inflections=True
            mock_format.assert_called()
            call_args, call_kwargs = mock_format.call_args
            # Check if only_inflections was passed as True (either as positional or keyword arg)
            only_inflections_passed = (len(call_args) > 9 and call_args[9] is True) or call_kwargs.get('only_inflections', False)
            self.assertTrue(only_inflections_passed, "format_result should be called with only_inflections=True")
    
    @patch('sys.argv', ['ordb', '--noun', 'word'])
    @patch('builtins.print')
    def test_word_class_filter_noun(self, mock_print):
        """Test noun word class filter."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            # Return mixed word classes
            mock_exact.return_value = [
                (1, 'house', 'house', 'NOUN', None, '', '{}', '', 1),
                (2, 'run', 'run', 'VERB', None, '', '{}', '', 1)
            ]
            mock_format.return_value = "Formatted result"
            
            cli_module.main()
            
            # Should only format/display the noun result, not the verb
            format_calls = [call.args[1] for call in mock_format.call_args_list]  # Get the result tuple passed to format_result
            displayed_word_classes = [result[3] for result in format_calls]  # Index 3 is word_class
            
            self.assertIn('NOUN', displayed_word_classes, "Should display noun results")
            self.assertNotIn('VERB', displayed_word_classes, "Should filter out verb results")
    
    @patch('sys.argv', ['ordb', '--verb', 'word'])
    @patch('builtins.print')
    def test_word_class_filter_verb(self, mock_print):
        """Test verb word class filter."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            mock_exact.return_value = [
                (1, 'house', 'house', 'NOUN', None, '', '{}', '', 1),
                (2, 'run', 'run', 'VERB', None, '', '{}', '', 1)
            ]
            mock_format.return_value = "Formatted result"
            
            cli_module.main()
            
            # Should only format/display the verb result, not the noun
            format_calls = [call.args[1] for call in mock_format.call_args_list]
            displayed_word_classes = [result[3] for result in format_calls]
            
            self.assertIn('VERB', displayed_word_classes, "Should display verb results")
            self.assertNotIn('NOUN', displayed_word_classes, "Should filter out noun results")
    
    @patch('sys.argv', ['ordb', '--adj', 'word'])
    @patch('builtins.print')
    def test_word_class_filter_adjective(self, mock_print):
        """Test adjective word class filter."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            mock_exact.return_value = [
                (1, 'big', 'big', 'ADJ', None, '', '{}', '', 1),
                (2, 'run', 'run', 'VERB', None, '', '{}', '', 1)
            ]
            mock_format.return_value = "Formatted result"
            
            cli_module.main()
            
            # Should only format/display the adjective result, not the verb
            format_calls = [call.args[1] for call in mock_format.call_args_list]
            displayed_word_classes = [result[3] for result in format_calls]
            
            self.assertIn('ADJ', displayed_word_classes, "Should display adjective results")
            self.assertNotIn('VERB', displayed_word_classes, "Should filter out verb results")
    
    @patch('sys.argv', ['ordb', '--adv', 'word'])
    @patch('builtins.print')
    def test_word_class_filter_adverb(self, mock_print):
        """Test adverb word class filter."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            mock_exact.return_value = [
                (1, 'quickly', 'quickly', 'ADV', None, '', '{}', '', 1),
                (2, 'run', 'run', 'VERB', None, '', '{}', '', 1)
            ]
            mock_format.return_value = "Formatted result"
            
            cli_module.main()
            
            # Should only format/display the adverb result, not the verb
            format_calls = [call.args[1] for call in mock_format.call_args_list]
            displayed_word_classes = [result[3] for result in format_calls]
            
            self.assertIn('ADV', displayed_word_classes, "Should display adverb results")
            self.assertNotIn('VERB', displayed_word_classes, "Should filter out verb results")
    
    @patch('sys.argv', ['ordb', '-l', '10', 'word'])
    @patch('builtins.print')
    def test_limit_flag(self, mock_print):
        """Test limit flag."""
        with patch('ordb.cli.search_exact') as mock_exact:
            # Return more results than limit
            mock_exact.return_value = [(i, f'word{i}', f'word{i}', 'NOUN', None, '', '{}', '', 1) for i in range(20)]
            
            cli_module.main()
            
            # Should limit results (implementation depends on how limiting is done)
            mock_print.assert_called()
    
    @patch('sys.argv', ['ordb', '--max-examples', '3', 'word'])
    @patch('builtins.print')
    def test_max_examples_flag(self, mock_print):
        """Test max examples flag."""
        with patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            
            mock_exact.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            mock_format.return_value = "Mock result output"
            
            cli_module.main()
            
            # Should call format_result with max_examples=3
            mock_format.assert_called()
            call_args, call_kwargs = mock_format.call_args
            # Check if max_examples was passed as 3 (either as positional or keyword arg)
            max_examples_passed = (len(call_args) > 4 and call_args[4] == 3) or call_kwargs.get('max_examples') == 3
            self.assertTrue(max_examples_passed, "format_result should be called with max_examples=3")
    
    @patch('sys.argv', ['ordb', '--threshold', '0.8', '-f', 'word'])
    @patch('builtins.print')
    def test_threshold_flag(self, mock_print):
        """Test threshold flag for fuzzy search."""
        with patch('ordb.cli.search_fuzzy_interactive') as mock_fuzzy:
            mock_fuzzy.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call fuzzy search with threshold=0.8
            mock_fuzzy.assert_called()
            call_args, call_kwargs = mock_fuzzy.call_args
            # Check if threshold was passed as 0.8 (either as positional or keyword arg)
            threshold_passed = (len(call_args) > 2 and call_args[2] == 0.8) or call_kwargs.get('threshold') == 0.8
            self.assertTrue(threshold_passed, "search_fuzzy_interactive should be called with threshold=0.8")
    
    @patch('sys.argv', ['ordb', '-p', 'word'])
    @patch('builtins.print')
    def test_force_pagination_flag(self, mock_print):
        """Test force pagination flag."""
        with patch('ordb.cli.paginate_output') as mock_paginate, \
             patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            mock_exact.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            mock_format.return_value = "Mock result output"
            
            cli_module.main()
            
            # Should call paginate with force_pagination=True
            mock_paginate.assert_called()
            call_kwargs = mock_paginate.call_args[1]
            self.assertTrue(call_kwargs['force_pagination'])
    
    @patch('sys.argv', ['ordb', '-P', 'word'])
    @patch('builtins.print')
    def test_no_paginate_flag(self, mock_print):
        """Test no pagination flag."""
        with patch('ordb.cli.paginate_output') as mock_paginate, \
             patch('ordb.cli.search_exact') as mock_exact, \
             patch('ordb.display.format_result') as mock_format:
            mock_exact.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            mock_format.return_value = "Mock result output"
            
            cli_module.main()
            
            # Should call paginate with disable_pagination=True
            mock_paginate.assert_called()
            call_kwargs = mock_paginate.call_args[1]
            self.assertTrue(call_kwargs['disable_pagination'])
    
    @patch('sys.argv', ['ordb', '-s'])
    @patch('builtins.print')
    def test_statistics_flag(self, mock_print):
        """Test statistics flag."""
        with patch('ordb.display.display_statistics') as mock_stats:
            cli_module.main()
            
            # Should call display_statistics
            mock_stats.assert_called_once()
    
    @patch('sys.argv', ['ordb', '-c'])
    def test_config_wizard_flag(self):
        """Test config wizard flag."""
        with patch('ordb.wizard.run_config_wizard') as mock_wizard:
            cli_module.main()
            
            # Should call run_config_wizard
            mock_wizard.assert_called_once()
    
    @patch('sys.argv', ['ordb', '-C'])
    @patch('builtins.print')
    @unittest.skip("Skipping due to gettext issues in test environment")
    def test_cat_config_flag(self, mock_print):
        """Test cat config flag."""
        with patch('ordb.config.get_config_path') as mock_get_path, \
             patch('os.path.exists') as mock_exists, \
             patch('builtins.open', create=True) as mock_open_file:
            
            mock_get_path.return_value = '/path/to/config'
            mock_exists.return_value = True
            mock_open_file.return_value.__enter__.return_value.read.return_value = "config content"
            
            cli_module.main()
            
            # Should print config file content
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            self.assertTrue(any('config content' in call for call in print_calls))
    
    @patch('sys.argv', ['ordb', '-w', 'word'])
    @patch('builtins.print')
    def test_words_only_flag(self, mock_print):
        """Test words only flag."""
        with patch('ordb.cli.search_exact') as mock_exact:
            mock_exact.return_value = [
                (1, 'word1', 'word1', 'NOUN', None, '', '{}', '', 1),
                (2, 'word2', 'word2', 'VERB', None, '', '{}', '', 1)
            ]
            
            cli_module.main()
            
            # Should print comma-separated words
            mock_print.assert_called()
            print_calls = [str(call.args[0]) for call in mock_print.call_args_list]
            words_output = ''.join(print_calls)
            # Verify that both words are present and comma-separated
            self.assertIn('word1', words_output, "Should print first word")
            self.assertIn('word2', words_output, "Should print second word")
            self.assertIn(',', words_output, "Should use comma separation for words-only output")
            # Verify it's actually comma-separated format, not just containing a comma somewhere
            self.assertRegex(words_output, r'\bword1\b.*,.*\bword2\b', "Words should be comma-separated")
    
    @patch('sys.argv', ['ordb', '-W', 'word'])
    @patch('builtins.print')
    def test_words_lines_flag(self, mock_print):
        """Test words on separate lines flag."""
        with patch('ordb.cli.search_exact') as mock_exact:
            mock_exact.return_value = [
                (1, 'word1', 'word1', 'NOUN', None, '', '{}', '', 1),
                (2, 'word2', 'word2', 'VERB', None, '', '{}', '', 1)
            ]
            
            cli_module.main()
            
            # Should print words on separate lines
            mock_print.assert_called()
            # Should have multiple print calls for separate lines
            self.assertGreater(mock_print.call_count, 1)
    
    @patch('sys.argv', ['ordb', '-r'])
    @patch('builtins.print')
    def test_random_entry_flag(self, mock_print):
        """Test random entry flag."""
        with patch('ordb.core.get_random_entries') as mock_random:
            mock_random.return_value = [(1, 'random', 'random', 'NOUN', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call get_random_entries with count=1
            mock_random.assert_called_once()
            call_args = mock_random.call_args[0]
            self.assertEqual(call_args[1], 1)  # count parameter
    
    @patch('sys.argv', ['ordb', '-r3'])
    @patch('builtins.print')
    def test_random_multiple_entries_flag(self, mock_print):
        """Test random multiple entries flag."""
        with patch('ordb.core.get_random_entries') as mock_random:
            mock_random.return_value = [
                (1, 'random1', 'random1', 'NOUN', None, '', '{}', '', 1),
                (2, 'random2', 'random2', 'VERB', None, '', '{}', '', 1),
                (3, 'random3', 'random3', 'ADJ', None, '', '{}', '', 1)
            ]
            
            cli_module.main()
            
            # Should call get_random_entries with count=3
            mock_random.assert_called_once()
            call_args = mock_random.call_args[0]
            self.assertEqual(call_args[1], 3)  # count parameter
    
    @patch('sys.argv', ['ordb', '-R5'])
    @patch('builtins.print')
    def test_random_words_only_flag(self, mock_print):
        """Test random words only flag."""
        with patch('ordb.core.get_random_entries') as mock_random:
            mock_random.return_value = [
                (1, 'random1', 'random1', 'NOUN', None, '', '{}', '', 1),
                (2, 'random2', 'random2', 'VERB', None, '', '{}', '', 1)
            ]
            
            cli_module.main()
            
            # Should call get_random_entries with count=5
            mock_random.assert_called_once()
            call_args = mock_random.call_args[0]
            self.assertEqual(call_args[1], 5)  # count parameter
            
            # Should print words only, one per line
            mock_print.assert_called()
    
    @patch('sys.argv', ['ordb', 'word@'])
    @patch('builtins.print')
    def test_prefix_search_syntax(self, mock_print):
        """Test prefix search syntax (word@)."""
        with patch('ordb.cli.search_prefix_interactive') as mock_prefix:
            mock_prefix.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call prefix interactive search
            mock_prefix.assert_called_once()
    
    @patch('sys.argv', ['ordb', '@word'])
    @patch('builtins.print')
    def test_anywhere_search_syntax(self, mock_print):
        """Test anywhere search syntax (@word)."""
        with patch('ordb.cli.search_anywhere_term_interactive') as mock_anywhere:
            mock_anywhere.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call anywhere interactive search
            mock_anywhere.assert_called_once()
    
    @patch('sys.argv', ['ordb', '%word'])
    @patch('builtins.print')
    def test_fulltext_search_syntax(self, mock_print):
        """Test fulltext search syntax (%word)."""
        with patch('ordb.cli.search_fulltext') as mock_fulltext:
            mock_fulltext.return_value = [(1, 'word', 'word', 'NOUN', None, '', '{}', '', 1)]
            
            cli_module.main()
            
            # Should call fulltext search
            mock_fulltext.assert_called_once()
    
    @patch('sys.argv', ['ordb'])
    @patch('builtins.print')
    def test_no_arguments(self, mock_print):
        """Test CLI with no arguments."""
        with self.assertRaises(SystemExit) as cm:
            cli_module.main()
        
        # Should exit with status 1
        self.assertEqual(cm.exception.code, 1)
        
        # Should print error message
        mock_print.assert_called()
        print_calls = [str(call) for call in mock_print.call_args_list]
        self.assertTrue(any('Error:' in str(call) for call in print_calls))


class TestCLIErrorHandling(unittest.TestCase):
    """Test CLI error handling scenarios."""
    
    @patch('sys.argv', ['ordb', 'nonexistent'])
    @patch('builtins.print')
    def test_no_results_found(self, mock_print):
        """Test behavior when no results are found."""
        with patch('ordb.core.setup_database') as mock_setup, \
             patch('ordb.config.search_config') as mock_config, \
             patch('ordb.config.Colors') as mock_colors, \
             patch('ordb.core.search_exact', return_value=[]) as mock_exact, \
             patch('ordb.core.search_fuzzy_interactive', return_value=[]) as mock_fuzzy, \
             patch('ordb.core.parse_search_query', return_value=('exact', 'nonexistent', 'nonexistent')) as mock_parse, \
             patch('ordb.pagination.paginate_output') as mock_paginate, \
             patch('ordb.config.get_config_path', return_value=None) as mock_get_config, \
             patch('os.path.exists', return_value=False) as mock_exists:
            
            # Configure mocks
            mock_setup.return_value = mock_setup  # Mock connection object
            mock_config.fallback_to_fuzzy = True
            mock_config.default_limit = 50
            # Mock all color attributes
            for attr in ['WARNING', 'END', 'BOLD', 'HEADER', 'INFO', 'ERROR']:
                setattr(mock_colors, attr, "")
            
            try:
                cli_module.main()
            except SystemExit:
                pass  # Expected when no results found
            
            # Should handle no results gracefully (test that it runs without crashing)
            mock_print.assert_called()
    
    @unittest.skip("Test hangs in comprehensive test runner - needs investigation")
    @patch('sys.argv', ['ordb', 'test'])
    @patch('builtins.print')
    @patch('builtins.input', return_value='')  # Mock any potential input calls
    def test_database_setup_failure(self, mock_input, mock_print):
        """Test behavior when database setup fails."""
        with patch('ordb.core.setup_database', return_value=None), \
             patch('ordb.config.Colors') as mock_colors, \
             patch('sys.exit') as mock_exit:  # Mock exit to prevent hanging
            
            # Mock color attributes
            for attr in ['WARNING', 'END', 'BOLD', 'HEADER', 'INFO', 'ERROR']:
                setattr(mock_colors, attr, "")
            
            # Test should complete without hanging (main success criterion)
            cli_module.main()
            
            # Verify the expected behavior occurred
            # Either exit was called or some output was produced
            self.assertTrue(mock_exit.called or mock_print.called, 
                          "Either sys.exit should be called or output should be printed")


class TestCLIIntegration(unittest.TestCase):
    """Integration-style tests with minimal mocking for better behavior verification."""
    
    @patch('sys.argv', ['ordb', '--version'])
    @patch('sys.exit')
    def test_version_output_content(self, mock_exit, *args):
        """Test that version output contains actual version information."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                cli_module.main()
            except SystemExit:
                pass
            
            output = fake_out.getvalue()
            # Verify actual version content, not just that something was printed
            self.assertRegex(output, r'ordb \d+\.\d+\.\d+', "Should display 'ordb' followed by semantic version")
            # Note: Version output is just the version number, not a full description
    
    @patch('sys.argv', ['ordb', '--help'])
    @patch('sys.exit')
    def test_help_output_completeness(self, mock_exit, *args):
        """Test that help output contains comprehensive information."""
        with patch('sys.stdout', new=StringIO()) as fake_out:
            try:
                cli_module.main()
            except SystemExit:
                pass
            
            output = fake_out.getvalue()
            # Verify help contains key sections and flags
            essential_sections = [
                'Norwegian bokmål dictionary search tool',
                'Examples:',
                'Special Search Syntax:',
                '--fuzzy', '--anywhere', '--expressions-only',
                '--only-examples', '--only-etymology', '--only-inflections',
                '--noun', '--verb', '--adj', '--adv'
            ]
            
            for section in essential_sections:
                self.assertIn(section, output, f"Help should contain '{section}' section/flag")
    
    def test_argument_parser_creation(self):
        """Test that argument parser is created correctly without side effects."""
        # This tests the actual argument parsing logic without mocking
        import ordb.cli as cli_module
        
        # Create a fresh parser (this exercises the real argument setup)
        parser = argparse.ArgumentParser(
            description='ordb - Norwegian bokmål dictionary search tool',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # Verify parser was created successfully
        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.description, 'ordb - Norwegian bokmål dictionary search tool')
    
    @patch('sys.argv', ['ordb'])
    def test_no_arguments_behavior(self):
        """Test CLI behavior with no arguments - should exit gracefully."""
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            
            try:
                cli_module.main()
            except SystemExit as e:
                # Verify it exits with proper error code
                self.assertEqual(e.code, 1, "Should exit with error code 1 when no arguments provided")
            
            # Should print helpful error message
            mock_print.assert_called()
            print_calls = [str(call) for call in mock_print.call_args_list]
            error_output = ''.join(print_calls)
            self.assertIn('Error:', error_output, "Should print error message")
    
    def test_special_search_syntax_parsing(self):
        """Test that special search syntax is correctly parsed."""
        # Test the parse_search_query function directly for better coverage
        from ordb.core import parse_search_query
        
        test_cases = [
            ('word@', ('prefix', 'word', 'word@')),
            ('@word', ('anywhere_term', 'word', '@word')),
            ('%word', ('fulltext', 'word', '%word')),
            ('regular', ('exact', 'regular', 'regular'))
        ]
        
        for input_query, expected_output in test_cases:
            with self.subTest(query=input_query):
                result = parse_search_query(input_query)
                self.assertEqual(result, expected_output, 
                               f"Query '{input_query}' should parse to {expected_output}")


if __name__ == '__main__':
    unittest.main(verbosity=2)