#!/usr/bin/env python3
"""
Unit tests for formatting improvements in display.py module.
Tests the three specific formatting requirements:
1. No blank line after etymology
2. Alternative forms on same line as head word
3. Examples on same line as definitions
"""

import unittest
import sys
import json
import sqlite3
from unittest.mock import patch, MagicMock

# Add src directory to path for testing
sys.path.insert(0, 'src')

from ordb.display import format_result
from ordb.config import Colors


class TestFormattingImprovements(unittest.TestCase):
    """Test the specific formatting improvements required."""
    
    def setUp(self):
        """Set up test database with proper schema matching real functions."""
        self.conn = sqlite3.connect(':memory:')
        cursor = self.conn.cursor()
        
        # Create test tables matching the real schema
        cursor.execute('''
            CREATE TABLE definitions (
                id INTEGER PRIMARY KEY,
                definition_id INTEGER,
                article_id INTEGER,
                parent_id INTEGER,
                level INTEGER,
                content TEXT,
                order_num INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE examples (
                id INTEGER PRIMARY KEY,
                definition_id INTEGER,
                article_id INTEGER,
                quote TEXT,
                explanation TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE expression_links (
                expression_article_id INTEGER,
                target_lemma TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE articles (
                article_id INTEGER PRIMARY KEY,
                lemma TEXT,
                word_class TEXT
            )
        ''')
        
        # Insert test data for real testing
        cursor.execute('''
            INSERT INTO definitions (id, definition_id, article_id, parent_id, level, content, order_num)
            VALUES (1, 1, 1, NULL, 1, 'a building where people live', 1)
        ''')
        
        cursor.execute('''
            INSERT INTO examples (id, definition_id, article_id, quote, explanation)
            VALUES (1, 1, 1, 'det er et stort hus', NULL)
        ''')
        
        self.conn.commit()
    
    def tearDown(self):
        """Close test database."""
        self.conn.close()
    
    def test_no_blank_line_after_etymology(self):
        """Test that there is no blank line after etymology."""
        result_data = (1, "hus", "hus", "NOUN", "Neuter", "", "{}", "norr. hús", None)
        
        # Use real database functions - no mocking!
        result = format_result(self.conn, result_data)
        
        # Check that etymology is present
        self.assertIn("Etymology:", result)
        self.assertIn("norr. hús", result)
        
        # Find the etymology line and check what follows
        lines = result.split('\n')
        etymology_line_index = None
        for i, line in enumerate(lines):
            if "Etymology:" in line:
                etymology_line_index = i
                break
        
        self.assertIsNotNone(etymology_line_index)
        
        # The line immediately after etymology should NOT be empty (requirement implemented)
        if etymology_line_index + 1 < len(lines):
            next_line = lines[etymology_line_index + 1]
            self.assertNotEqual(next_line.strip(), "", 
                              "There should be no blank line after etymology")
    
    def test_alternative_forms_on_same_line(self):
        """Test that alternative forms appear on the same line as the head word."""
        # Result with alternative forms
        result_data = (1, "syk", "syk | sjuk", "ADJ", None, "", "{}", "norr. sjúkr", None)
        
        # Use real database functions - no mocking!
        result = format_result(self.conn, result_data)
        
        # Check that both the lemma and alternative forms are present
        self.assertIn("syk", result)
        
        # Find the header line (with the emoji and lemma)
        lines = result.split('\n')
        header_line = None
        for line in lines:
            if "📖" in line and "syk" in line:
                header_line = line
                break
        
        self.assertIsNotNone(header_line)
        
        # The alternative forms should be on the SAME line as the header (requirement implemented)
        self.assertIn("Alternative forms:", header_line,
                     "Alternative forms should be on the same line as the head word")
    
    def test_examples_on_same_line_as_definition(self):
        """Test that examples appear on the same line as definitions."""
        result_data = (1, "hus", "hus", "NOUN", "Neuter", "", "{}", None, None)
        
        # Use real database functions - no mocking!
        result = format_result(self.conn, result_data)
        
        # Find the definition line
        lines = result.split('\n')
        definition_line_index = None
        for i, line in enumerate(lines):
            if "a building where people live" in line:
                definition_line_index = i
                break
        
        self.assertIsNotNone(definition_line_index, "Should find the test definition")
        
        # The examples should be on the SAME line as the definition (requirement implemented)
        definition_line = lines[definition_line_index]
        self.assertIn("det er et stort hus", definition_line,
                     "Examples should be on the same line as the definition")
    
    def test_all_formatting_combined(self):
        """Test all three formatting requirements together."""
        # Result with all features - use article_id 1 which has test data
        result_data = (1, "hus", "hus | house", "NOUN", "Neuter", "", "{}", "norr. hús", None)
        
        # Use real database functions - no mocking!
        result = format_result(self.conn, result_data)
        lines = result.split('\n')
        
        # Test 1: Alternative forms on header line
        header_line = None
        for line in lines:
            if "📖" in line and "hus" in line:
                header_line = line
                break
        self.assertIsNotNone(header_line, "Should find header line")
        self.assertIn("Alternative forms:", header_line, "Alternative forms should be on header line")
        
        # Test 2: Examples on definition line
        definition_line = None
        for line in lines:
            if "a building where people live" in line:
                definition_line = line
                break
        self.assertIsNotNone(definition_line, "Should find definition line")
        self.assertIn("det er et stort hus", definition_line, "Examples should be on definition line")
        
        # Test 3: No blank line after etymology
        etymology_index = None
        for i, line in enumerate(lines):
            if "Etymology:" in line:
                etymology_index = i
                break
        if etymology_index is not None and etymology_index + 1 < len(lines):
            self.assertNotEqual(lines[etymology_index + 1].strip(), "")


if __name__ == '__main__':
    unittest.main(verbosity=2)