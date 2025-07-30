#!/usr/bin/env python3
"""
Comprehensive test suite for Norwegian Dictionary database integrity and search functionality.
Tests the json-to-db.py conversion and ordb functionality.
"""

import unittest
import sqlite3
import subprocess
import sys
import os
import tempfile
import re
from collections import defaultdict

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestDatabaseIntegrity(unittest.TestCase):
    """Test database integrity and search functionality."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures - connect to database and prepare search command."""
        import os
        # Use user database location
        cls.db_path = os.path.expanduser('~/.ordb/articles.db')
        cls.search_cmd = ['python', '-m', 'src.ordb']
        
        # Verify database exists
        if not os.path.exists(cls.db_path):
            raise FileNotFoundError(f"Database {cls.db_path} not found. Run ordb once to set up database first.")
    
    def setUp(self):
        """Set up each test."""
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def tearDown(self):
        """Clean up after each test."""
        self.conn.close()
    
    def clean_ansi(self, text):
        """Remove ANSI color codes from text."""
        return re.sub(r'\x1b\[[0-9;]*m', '', text)
    
    def _run_search(self, query, capture_output=True):
        """Run search script and return output."""
        try:
            cmd = self.search_cmd + ['--no-paginate', query]
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            self.fail(f"Failed to run search script: {e}")
    
    def test_no_duplicate_definitions(self):
        """Test that there are no duplicate definitions in the database."""
        print("\n🔍 Testing for duplicate definitions...")
        
        # Find articles with duplicate definitions
        self.cursor.execute('''
            SELECT article_id, definition_id, content, COUNT(*) as count
            FROM definitions 
            GROUP BY article_id, definition_id, content
            HAVING COUNT(*) > 1
        ''')
        
        duplicates = self.cursor.fetchall()
        
        if duplicates:
            print(f"❌ Found {len(duplicates)} sets of duplicate definitions:")
            for article_id, def_id, content, count in duplicates[:5]:  # Show first 5
                # Get lemma for this article
                self.cursor.execute('SELECT lemma FROM articles WHERE article_id = ?', (article_id,))
                lemma = self.cursor.fetchone()[0] if self.cursor.fetchone() else "Unknown"
                print(f"  - Article {article_id} ({lemma}): definition_id {def_id} appears {count} times")
                print(f"    Content: {content[:100]}...")
        
        self.assertEqual(len(duplicates), 0, 
                        f"Found {len(duplicates)} duplicate definitions in database")
        print("✅ No duplicate definitions found")
    
    def test_stein_expressions_count(self):
        """Test that 'stein' returns exactly 15 expressions."""
        print("\n🔍 Testing 'stein' expressions count...")
        
        stdout, stderr, returncode = self._run_search("stein")
        
        self.assertEqual(returncode, 0, f"Search script failed: {stderr}")
        
        # Count expressions in output (lines starting with "• ")
        expression_lines = [line for line in stdout.split('\n') if line.strip().startswith('• ')]
        expression_count = len(expression_lines)
        
        print(f"Found {expression_count} expressions for 'stein'")
        if expression_count != 15:
            print("First few expressions found:")
            for i, line in enumerate(expression_lines[:5]):
                print(f"  {i+1}. {line.strip()}")
        
        self.assertEqual(expression_count, 15,
                        f"Expected 15 expressions for 'stein', but found {expression_count}")
        print("✅ 'stein' returns exactly 15 expressions")
    
    def test_cross_reference_links_count(self):
        """Test that database has expected number of cross-reference links."""
        print("\n🔍 Testing cross-reference links count...")
        
        # Count total expression links
        self.cursor.execute('SELECT COUNT(*) FROM expression_links')
        total_links = self.cursor.fetchone()[0]
        
        # We expect at least 9000 links (more than before the fix)
        expected_minimum = 9000
        
        print(f"Found {total_links} expression cross-reference links")
        
        self.assertGreaterEqual(total_links, expected_minimum,
                               f"Expected at least {expected_minimum} expression links, but found {total_links}")
        print(f"✅ Database has {total_links} cross-reference links (>= {expected_minimum})")
    
    def test_specific_cross_references(self):
        """Test that specific cross-references we fixed are present."""
        print("\n🔍 Testing specific cross-references...")
        
        test_cases = [
            ("på huset", "hus"),
            ("fullt hus", "hus"),
            ("fullt hus", "full"),
        ]
        
        for expression, target in test_cases:
            self.cursor.execute('''
                SELECT el.* FROM expression_links el
                JOIN articles a ON el.expression_article_id = a.article_id
                WHERE a.lemma = ? AND el.target_lemma = ?
            ''', (expression, target))
            
            link = self.cursor.fetchone()
            self.assertIsNotNone(link, 
                               f"Cross-reference from '{expression}' to '{target}' not found")
            print(f"✅ Found cross-reference: '{expression}' → '{target}'")
    
    def test_database_structure(self):
        """Test that database has expected tables and structure."""
        print("\n🔍 Testing database structure...")
        
        # Check required tables exist
        required_tables = ['articles', 'definitions', 'examples', 'expression_links']
        
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in self.cursor.fetchall()]
        
        for table in required_tables:
            self.assertIn(table, existing_tables, f"Required table '{table}' not found")
            print(f"✅ Table '{table}' exists")
        
        # Check table record counts
        for table in required_tables:
            self.cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = self.cursor.fetchone()[0]
            self.assertGreater(count, 0, f"Table '{table}' is empty")
            print(f"✅ Table '{table}' has {count:,} records")
    
    def test_articles_basic_integrity(self):
        """Test basic integrity of articles table."""
        print("\n🔍 Testing articles table integrity...")
        
        # Check for articles without lemmas (allow a small number as artifacts)
        self.cursor.execute("SELECT COUNT(*) FROM articles WHERE lemma IS NULL OR lemma = ''")
        empty_lemmas = self.cursor.fetchone()[0]
        total_articles = 90841  # Known total from database
        empty_percentage = (empty_lemmas / total_articles) * 100
        
        self.assertLess(empty_percentage, 0.1, f"Too many articles with empty lemmas: {empty_lemmas} ({empty_percentage:.3f}%)")
        print(f"✅ Articles with empty lemmas: {empty_lemmas} ({empty_percentage:.3f}% - acceptable)")
        
        # Check for proper word classes
        self.cursor.execute("SELECT DISTINCT word_class FROM articles WHERE word_class IS NOT NULL AND word_class != ''")
        word_classes = [row[0] for row in self.cursor.fetchall()]
        expected_classes = ['SUBST', 'VERB', 'ADJ', 'ADV', 'EXPR']
        
        for wc in word_classes:
            # Handle compound word classes like "ADJ | NOUN"
            if ' | ' in wc:
                parts = [part.strip() for part in wc.split(' | ')]
                for part in parts:
                    # Map some alternative forms
                    if part == 'NOUN':
                        part = 'SUBST'
                    self.assertIn(part, expected_classes, f"Unexpected word class part: {part} in {wc}")
            else:
                # Map some alternative forms
                mapped_wc = wc
                if wc == 'NOUN':
                    mapped_wc = 'SUBST'
                self.assertIn(mapped_wc, expected_classes, f"Unexpected word class: {wc}")
        print(f"✅ Found word classes (including compounds): {len(word_classes)} types")
        
        # Check for expression word class count
        self.cursor.execute("SELECT COUNT(*) FROM articles WHERE word_class = 'EXPR'")
        expr_count = self.cursor.fetchone()[0]
        self.assertGreater(expr_count, 1000, "Too few expressions found")
        print(f"✅ Found {expr_count:,} expressions (EXPR word class)")
    
    def test_search_script_basic_functionality(self):
        """Test that search script runs without errors for common queries."""
        print("\n🔍 Testing search script basic functionality...")
        
        test_queries = ["hus", "gå", "være", "og"]
        
        for query in test_queries:
            stdout, stderr, returncode = self._run_search(query)
            
            self.assertEqual(returncode, 0, f"Search failed for '{query}': {stderr}")
            clean_output = self.clean_ansi(stdout)
            # Should have results (either "Found" text or entry markers)
            self.assertTrue("Found" in clean_output or "📖" in stdout, f"No results found for '{query}'")
            self.assertTrue("result" in clean_output or "📖" in stdout, f"Invalid output format for '{query}'")
            print(f"✅ Search for '{query}' successful")
    
    def test_previously_problematic_words(self):
        """Test words that previously had duplicate definitions."""
        print("\n🔍 Testing previously problematic words...")
        
        test_words = ["husmor", "drivhuseffekt"]
        
        for word in test_words:
            stdout, stderr, returncode = self._run_search(word)
            
            self.assertEqual(returncode, 0, f"Search failed for '{word}': {stderr}")
            
            # Count definitions (lines with pattern "  [1m1.[0m", "  [1m2.[0m", etc.)
            definition_lines = []
            for line in stdout.split('\n'):
                # Remove ANSI color codes and check for definition pattern
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
                if re.match(r'^\d+\.', clean_line):
                    definition_lines.append(clean_line)
            
            # Should have 2 definitions, not 4 (no duplicates)
            definition_count = len(definition_lines)
            expected_count = 2
            
            print(f"'{word}' has {definition_count} definitions")
            self.assertEqual(definition_count, expected_count,
                           f"'{word}' should have {expected_count} definitions, not {definition_count}")
            print(f"✅ '{word}' has correct number of definitions (no duplicates)")
    
    def test_hjerte_expressions_count(self):
        """Test that 'hjerte' has improved expression count (should be ~25)."""
        print("\n🔍 Testing 'hjerte' expressions count...")
        
        stdout, stderr, returncode = self._run_search("hjerte")
        
        self.assertEqual(returncode, 0, f"Search script failed: {stderr}")
        
        # Count expressions in output
        expression_lines = [line for line in stdout.split('\n') if line.strip().startswith('• ')]
        expression_count = len(expression_lines)
        
        print(f"Found {expression_count} expressions for 'hjerte'")
        
        # Should be around 25 (matching web version)
        expected_min = 20
        expected_max = 30
        
        self.assertGreaterEqual(expression_count, expected_min,
                               f"'hjerte' should have at least {expected_min} expressions, found {expression_count}")
        self.assertLessEqual(expression_count, expected_max,
                            f"'hjerte' should have at most {expected_max} expressions, found {expression_count}")
        print(f"✅ 'hjerte' has {expression_count} expressions (within expected range {expected_min}-{expected_max})")
    
    def test_expression_examples_integrity(self):
        """Test that expressions have proper examples and cross-references."""
        print("\n🔍 Testing expression examples integrity...")
        
        # Test a few specific expressions we know should work
        test_expressions = ["på huset", "fullt hus"]
        
        for expr in test_expressions:
            stdout, stderr, returncode = self._run_search(expr)
            
            self.assertEqual(returncode, 0, f"Search failed for '{expr}': {stderr}")
            self.assertIn(expr, stdout, f"Expression '{expr}' not found in output")
            
            # Should have examples (lines with quotes)
            example_lines = [line for line in stdout.split('\n') 
                           if '"' in line and line.strip().startswith('"')]
            
            self.assertGreater(len(example_lines), 0, 
                             f"Expression '{expr}' should have examples")
            print(f"✅ Expression '{expr}' has {len(example_lines)} examples")

    def test_sub_definition_integration(self):
        """Test that sub-definitions are properly integrated into parent definitions."""
        print("\n🔍 Testing sub-definition integration...")
        
        # Test words that previously had incorrect sub-definition handling
        test_cases = [
            ("rar", 1, "should have 1 definition with adverb usage integrated"),
            ("egentlig", 3, "should have 3 definitions with adverb usage integrated"),
        ]
        
        for word, expected_count, description in test_cases:
            stdout, stderr, returncode = self._run_search(word)
            
            self.assertEqual(returncode, 0, f"Search failed for '{word}': {stderr}")
            
            # Count definitions (lines with pattern "  [1m1.[0m", "  [1m2.[0m", etc.)
            definition_lines = []
            for line in stdout.split('\n'):
                # Remove ANSI color codes and check for definition pattern
                clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
                if re.match(r'^\d+\.', clean_line):
                    definition_lines.append(clean_line)
            
            definition_count = len(definition_lines)
            
            print(f"'{word}' has {definition_count} definitions")
            self.assertEqual(definition_count, expected_count,
                           f"'{word}' {description}, not {definition_count}")
            
            # Additional check for "rar": ensure "brukt som adv" is integrated, not separate  
            if word == "rar":
                # For "rar", check that "brukt som adv" appears integrated in content, not as separate definition
                has_brukt_som_content = False
                brukt_som_as_only_definition = False
                
                for line in stdout.split('\n'):
                    clean_line = re.sub(r'\x1b\[[0-9;]*m', '', line).strip()
                    if "brukt som adv" in clean_line:
                        if re.match(r'^\d+\.\s*brukt som adv[:\s]*$', clean_line):
                            brukt_som_as_only_definition = True
                        elif not clean_line.startswith('•'):  # Not in expressions section
                            has_brukt_som_content = True
                
                self.assertTrue(has_brukt_som_content, 
                              f"'{word}' should contain 'brukt som adv' in definition content")
                self.assertFalse(brukt_som_as_only_definition, 
                               f"'{word}' should not have 'brukt som adv' as standalone definition")
            
            print(f"✅ '{word}' has correct definition structure ({description})")


class TestSearchFeatures(unittest.TestCase):
    """Test specific search features and output formatting."""
    
    def setUp(self):
        """Set up each test."""
        self.search_cmd = ['python', '-m', 'src.ordb']
    
    def _run_search(self, query, capture_output=True):
        """Run search script and return output."""
        try:
            cmd = self.search_cmd + ['--no-paginate', query]
            result = subprocess.run(
                cmd,
                capture_output=capture_output,
                text=True,
                timeout=30
            )
            return result.stdout, result.stderr, result.returncode
        except Exception as e:
            self.fail(f"Failed to run search script: {e}")
    
    def test_output_formatting(self):
        """Test that output formatting is correct."""
        print("\n🔍 Testing output formatting...")
        
        stdout, stderr, returncode = self._run_search("hus")
        
        self.assertEqual(returncode, 0, f"Search failed: {stderr}")
        
        # Check for proper formatting elements
        formatting_checks = [
            ("📖", "Article emoji present"),
            ("Faste uttrykk:", "Fixed expressions section present"),
            ("Inflections:", "Inflections section present"),
            ("Etymology:", "Etymology section present"),
        ]
        
        for pattern, description in formatting_checks:
            self.assertIn(pattern, stdout, f"Missing formatting: {description}")
            print(f"✅ {description}")
    
    def test_no_malformed_output(self):
        """Test that output doesn't contain malformed elements."""
        print("\n🔍 Testing for malformed output...")
        
        stdout, stderr, returncode = self._run_search("stein")
        
        self.assertEqual(returncode, 0, f"Search failed: {stderr}")
        
        # Check for potential issues
        issues = [
            ("$", "Unresolved placeholders"),
            ("None", "None values in output"),
            ("null", "Null values in output"),
            ("\x00", "Null bytes in output"),
        ]
        
        for pattern, description in issues:
            self.assertNotIn(pattern, stdout, f"Found {description} in output")
            print(f"✅ No {description}")


def run_all_tests():
    """Run all tests and provide summary."""
    print("=" * 80)
    print("🧪 NORWEGIAN DICTIONARY DATABASE INTEGRITY TESTS")
    print("=" * 80)
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDatabaseIntegrity))
    suite.addTests(loader.loadTestsFromTestCase(TestSearchFeatures))
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}")
    
    if result.errors:
        print(f"\n💥 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}")
    
    if result.wasSuccessful():
        print("\n🎉 ALL TESTS PASSED!")
        return 0
    else:
        print("\n❌ SOME TESTS FAILED")
        return 1


if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)