"""Core search engine for ordb."""

import sqlite3
import sys
import re
import gzip
import urllib.request
import urllib.error
from pathlib import Path
from difflib import SequenceMatcher
from .config import apply_character_replacement


def download_database(url, db_path):
    """Download and decompress the database from the given URL."""
    from .config import Colors
    
    print(f"{Colors.BOLD}Downloading dictionary database from:")
    print(f"{url}{Colors.END}")
    print()
    
    try:
        # Create user data directory if it doesn't exist
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Download compressed database
        temp_gz_path = db_path.with_suffix('.db.gz')
        
        print("Downloading compressed database...")
        with urllib.request.urlopen(url) as response:
            total_size = int(response.headers.get('Content-Length', 0))
            downloaded = 0
            
            with open(temp_gz_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    if total_size > 0:
                        progress = (downloaded / total_size) * 100
                        print(f"\rProgress: {progress:.1f}% ({downloaded // 1024} KB / {total_size // 1024} KB)", end='', flush=True)
        
        print(f"\n{Colors.SUCCESS}Download complete!{Colors.END}")
        
        # Decompress the database
        print("Decompressing database...")
        with gzip.open(temp_gz_path, 'rb') as gz_file:
            with open(db_path, 'wb') as db_file:
                db_file.write(gz_file.read())
        
        # Clean up compressed file
        temp_gz_path.unlink()
        
        print(f"{Colors.SUCCESS}Database ready at: {db_path}{Colors.END}")
        return True
        
    except urllib.error.HTTPError as e:
        print(f"{Colors.ERROR}HTTP Error {e.code}: {e.reason}{Colors.END}")
        return False
    except urllib.error.URLError as e:
        print(f"{Colors.ERROR}URL Error: {e.reason}{Colors.END}")
        return False
    except Exception as e:
        print(f"{Colors.ERROR}Error downloading database: {e}{Colors.END}")
        return False


def extract_bundled_database():
    """Extract the bundled compressed database to user directory."""
    from .config import Colors
    import io
    import os
    
    from .config import get_data_dir
    user_db_path = get_data_dir() / 'articles.db'
    
    try:
        # Try to find bundled database - look for it relative to package installation
        bundled_db_data = None
        
        # Method 1: Look in the package directory (for wheel installations)
        try:
            import ordb
            package_dir = Path(ordb.__file__).parent
            package_db_path = package_dir / 'articles.db.gz'
            if package_db_path.exists():
                bundled_db_data = package_db_path.read_bytes()
        except Exception:
            pass
                
        # Method 2: Look relative to the current package location (development layouts)
        if bundled_db_data is None:
            try:
                import ordb
                package_dir = Path(ordb.__file__).parent
                possible_paths = [
                    package_dir / '../db/articles.db.gz',  # Development layout
                    package_dir / 'db/articles.db.gz',    # If moved to package
                    package_dir / '../../db/articles.db.gz'  # Another possible layout
                ]
                for path in possible_paths:
                    abs_path = path.resolve()
                    if abs_path.exists():
                        bundled_db_data = abs_path.read_bytes()
                        break
            except Exception:
                pass
                
        # Method 3: Look relative to this source file (for development)
        if bundled_db_data is None:
            try:
                # Get the directory of this core.py file
                current_file = Path(__file__).parent
                possible_paths = [
                    current_file / '../../db/articles.db.gz',  # From src/ordb to db
                    current_file / '../../../db/articles.db.gz',  # Just in case
                ]
                for path in possible_paths:
                    abs_path = path.resolve()
                    if abs_path.exists():
                        bundled_db_data = abs_path.read_bytes()
                        break
            except Exception:
                pass
        
        if bundled_db_data is None:
            # No bundled database found
            return None
        
        print(f"{Colors.BOLD}Welcome to ordb.{Colors.END}")
        print(f"No installed dictionary found. May I now install the included dictionary database to {get_data_dir()}?")
        print()
        print(f"   • Compressed size: ~21 MB")
        print(f"   • Uncompressed size: ~90 MB")
        print(f"   • Contains 90,000+ Norwegian dictionary entries")
        print()
        
        try:
            response = input("Continue with database setup? [Y/n]: ").strip().lower()
            if response and response not in ['y', 'yes']:
                print("Database setup cancelled.")
                return None
        except EOFError:
            # No interactive input available (e.g., piped input) - default to yes
            print("y")
            print("Proceeding with database setup...")
        
        # Create user data directory
        user_db_path.parent.mkdir(parents=True, exist_ok=True)
        
        print("Extracting database... (this may take a moment)")
        
        # Decompress and save
        with gzip.open(io.BytesIO(bundled_db_data), 'rb') as gz_file:
            with open(user_db_path, 'wb') as db_file:
                # Write in chunks to show progress for large file
                chunk_size = 1024 * 1024  # 1MB chunks
                while True:
                    chunk = gz_file.read(chunk_size)
                    if not chunk:
                        break
                    db_file.write(chunk)
                    print(".", end="", flush=True)
        
        print()  # New line after progress dots
        print(f"{Colors.SUCCESS}✅ Database ready at: {user_db_path}{Colors.END}")
        return user_db_path
        
    except Exception as e:
        print(f"{Colors.ERROR}Error extracting bundled database: {e}{Colors.END}")
        return None


def setup_database(db_path):
    """Connect to the SQLite database, extracting or downloading if necessary."""
    db_path = Path(db_path)
    
    # If database exists, just connect
    if db_path.exists():
        return sqlite3.connect(db_path)
    
    # Database not found - trigger first-run setup
    from .config import Colors
    
    print(f"{Colors.WARNING}Dictionary database not found at: {db_path}{Colors.END}")
    print()
    
    # First try to extract bundled database
    print(f"{Colors.INFO}Attempting to extract bundled database...{Colors.END}")
    extracted_path = extract_bundled_database()
    if extracted_path and extracted_path.exists():
        print(f"{Colors.SUCCESS}Bundled database extracted successfully!{Colors.END}")
        return sqlite3.connect(extracted_path)
    else:
        print(f"{Colors.WARNING}Bundled database extraction failed or returned None.{Colors.END}")
    
    # Fallback to downloading
    print()
    print(f"{Colors.WARNING}Bundled database not available. Attempting download...{Colors.END}")
    print("This is a one-time setup that will download about 20-30 MB.")
    print()
    
    # Default GitHub URL - can be overridden
    default_url = "https://github.com/kmlawson/ordb/releases/latest/download/articles.db.gz"
    
    print(f"Download URL: {default_url}")
    print()
    response = input("Press Enter to download, or paste alternative URL: ").strip()
    
    download_url = response if response else default_url
    
    if download_database(download_url, db_path):
        return sqlite3.connect(db_path)
    else:
        print(f"{Colors.ERROR}Failed to download database. Please check your internet connection or try again later.{Colors.END}")
        print()
        print("Alternative method - generate database from source:")
        print("1. Visit https://ord.uib.no/")
        print("2. Click 'Ordlister' and download article.json")
        print("3. Get ordb source: git clone https://github.com/kmlawson/ordb.git")
        print("4. Place article.json in the ordb directory")
        print("5. Run: cd ordb && python db/json-to-db.py")
        print(f"6. Copy generated articles.db to {get_data_dir()}/articles.db")
        print()
        print("Note: This requires ~200 MB disk space and may take several minutes")
        sys.exit(1)


def similarity(a, b):
    """Calculate similarity ratio between two strings."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def parse_search_query(query):
    """Parse search query to determine search type and clean query."""
    original_query = query
    search_type = 'exact'
    
    # Full text search: %term
    if query.startswith('%'):
        search_type = 'fulltext'
        query = query[1:]
    # Prefix match: term@
    elif query.endswith('@') and not query.startswith('@'):
        search_type = 'prefix'
        query = query[:-1]
    # Match anywhere: @term or @term@
    elif query.startswith('@'):
        search_type = 'anywhere_term'
        query = query[1:]
        if query.endswith('@'):
            query = query[:-1]
    
    return search_type, query, original_query


def search_exact(conn, query, include_expr=True):
    """Search for exact matches in lemmas and inflections."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        # Search in primary lemma
        expr_filter = "" if include_expr else "AND word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE lemma = ? COLLATE NOCASE {expr_filter}
        ''', (variant,))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
        
        # Search in all lemmas and inflections for exact matches
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE (all_lemmas LIKE ? COLLATE NOCASE 
            OR inflections LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%'))
        
        # Add results, avoiding duplicates
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                # Check if it's actually an exact match (word boundaries)
                all_lemmas = result[2].split(' | ') if result[2] else []
                inflections = result[5].split(' | ') if result[5] else []
                if (variant.lower() in [lemma.lower() for lemma in all_lemmas] or
                    variant.lower() in [infl.lower() for infl in inflections]):
                    results.append(result)
                    seen_ids.add(result[0])
    
    # Sort by: 1) homonym number (NULL treated as 1), 2) word class priority (NOUN first), 3) lemma length
    def sort_key(x):
        homonym = x[8] if x[8] is not None else 1
        word_class_priority = 0 if x[3] == 'NOUN' else 1 if x[3] == 'VERB' else 2 if x[3] == 'ADJ' else 3 if x[3] == 'ADV' else 4
        return (homonym, word_class_priority, len(x[1]))
    
    results.sort(key=sort_key)
    
    # Don't include expressions as separate entries - they will be grouped under main entries
    return results


def search_prefix(conn, query, include_expr=False):
    """Search for terms that start with the query."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE (lemma LIKE ? COLLATE NOCASE
            OR all_lemmas LIKE ? COLLATE NOCASE 
            OR inflections LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number = result
                
                # Check if any term actually starts with the variant
                all_lemmas_list = all_lemmas.split(' | ') if all_lemmas else []
                inflections_list = inflections.split(' | ') if inflections else []
                all_terms = [lemma] + all_lemmas_list + inflections_list
                
                if any(term.lower().startswith(variant.lower()) for term in all_terms if term):
                    results.append(result)
                    seen_ids.add(result[0])
    
    # Sort by lemma length first (shortest first), then alphabetically
    results.sort(key=lambda x: (len(x[1]), x[1].lower()))
    return results


def search_anywhere_term(conn, query, include_expr=False):
    """Search for terms that contain the query anywhere."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE (lemma LIKE ? COLLATE NOCASE
            OR all_lemmas LIKE ? COLLATE NOCASE 
            OR inflections LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length first (shortest first), then alphabetically
    results.sort(key=lambda x: (len(x[1]), x[1].lower()))
    return results


def search_fulltext(conn, query, include_expr=False):
    """Search in all content including definitions and examples."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND a.word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT DISTINCT a.article_id, a.lemma, a.all_lemmas, a.word_class, a.gender, a.inflections, a.inflection_table, a.etymology, a.homonym_number
            FROM articles a
            LEFT JOIN definitions d ON a.article_id = d.article_id
            LEFT JOIN examples e ON a.article_id = e.article_id
            WHERE (a.lemma LIKE ? COLLATE NOCASE
            OR a.all_lemmas LIKE ? COLLATE NOCASE
            OR a.inflections LIKE ? COLLATE NOCASE
            OR d.content LIKE ? COLLATE NOCASE 
            OR e.quote LIKE ? COLLATE NOCASE
            OR a.etymology LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%', f'%{variant}%', f'%{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length first (shortest first), then alphabetically
    results.sort(key=lambda x: (len(x[1]), x[1].lower()))
    return results


def search_fuzzy(conn, query, threshold=0.6, include_expr=False):
    """Search for fuzzy matches."""
    cursor = conn.cursor()
    
    expr_filter = "" if include_expr else "WHERE word_class != 'EXPR'"
    cursor.execute(f'SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number FROM articles {expr_filter}')
    all_articles = cursor.fetchall()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    fuzzy_matches = []
    seen_ids = set()
    
    for variant in query_variants:
        for article in all_articles:
            article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number = article
            
            # Skip if already added
            if article_id in seen_ids:
                continue
            
            # Check similarity with primary lemma
            if similarity(variant, lemma) >= threshold:
                fuzzy_matches.append((article, similarity(variant, lemma)))
                seen_ids.add(article_id)
                continue
            
            # Check similarity with all lemmas
            lemmas = all_lemmas.split(' | ') if all_lemmas else []
            max_similarity = 0
            for lem in lemmas:
                sim = similarity(variant, lem)
                if sim > max_similarity:
                    max_similarity = sim
            
            if max_similarity >= threshold:
                fuzzy_matches.append((article, max_similarity))
                seen_ids.add(article_id)
    
    # Sort by similarity score (descending), then by lemma length (ascending), then alphabetically
    fuzzy_matches.sort(key=lambda x: (-x[1], len(x[0][1]), x[0][1].lower()))
    
    return [match[0] for match in fuzzy_matches]


def _highlight_fuzzy_differences(query, lemma, colors):
    """Highlight differences between query and lemma for fuzzy search display.
    
    Uses different colors for matching and non-matching characters.
    Uses a simple longest common subsequence approach for better matching.
    """
    query_lower = query.lower()
    lemma_lower = lemma.lower()
    
    # Find positions of matching characters using a greedy approach
    matching_positions = set()
    query_idx = 0
    
    for i, char in enumerate(lemma_lower):
        if query_idx < len(query_lower) and char == query_lower[query_idx]:
            matching_positions.add(i)
            query_idx += 1
    
    # Build highlighted string
    highlighted = ""
    for i, char in enumerate(lemma):
        if i in matching_positions:
            # Matching character - use bright highlight color
            highlighted += f"{colors.HIGHLIGHT}{char}{colors.END}"
        else:
            # Non-matching character - use dimmed lemma color
            highlighted += f"{colors.LEMMA}{char}{colors.END}"
    
    return highlighted


def _highlight_prefix_match(query, lemma, colors):
    """Highlight prefix match for prefix search display."""
    query_lower = query.lower()
    lemma_lower = lemma.lower()
    
    if lemma_lower.startswith(query_lower):
        # Highlight the matching prefix in bright color, rest in lemma color
        prefix_len = len(query)
        highlighted = f"{colors.HIGHLIGHT}{lemma[:prefix_len]}{colors.END}"
        if len(lemma) > prefix_len:
            highlighted += f"{colors.LEMMA}{lemma[prefix_len:]}{colors.END}"
        return highlighted
    else:
        # No prefix match found, use regular lemma color
        return f"{colors.LEMMA}{lemma}{colors.END}"


def _highlight_anywhere_match(query, lemma, colors):
    """Highlight anywhere match for anywhere term search display."""
    query_lower = query.lower()
    lemma_lower = lemma.lower()
    
    # Find the first occurrence of the query in the lemma
    pos = lemma_lower.find(query_lower)
    if pos != -1:
        # Highlight the matching substring
        before = lemma[:pos]
        match = lemma[pos:pos + len(query)]
        after = lemma[pos + len(query):]
        
        highlighted = ""
        if before:
            highlighted += f"{colors.LEMMA}{before}{colors.END}"
        highlighted += f"{colors.HIGHLIGHT}{match}{colors.END}"
        if after:
            highlighted += f"{colors.LEMMA}{after}{colors.END}"
        return highlighted
    else:
        # No match found, use regular lemma color
        return f"{colors.LEMMA}{lemma}{colors.END}"


def search_fuzzy_interactive(conn, query, threshold=0.6, include_expr=False, offset=0):
    """Interactive fuzzy search that presents results as a lettered list.
    
    Returns None if user cancels, or the selected result if chosen.
    """
    from .config import search_config, Colors
    from .utils import get_single_keypress
    
    # Get fuzzy matches
    all_matches = search_fuzzy(conn, query, threshold, include_expr)
    
    if not all_matches:
        return None
    
    # Use configured limit
    limit = search_config.interactive_results_limit
    
    # Calculate pagination
    start_idx = offset
    end_idx = offset + limit
    matches = all_matches[start_idx:end_idx]
    
    # Check if we have more results after this page
    has_more_results = end_idx < len(all_matches)
    
    # If no matches in this page (offset too high), return None
    if not matches:
        return None
    
    # Display the fuzzy search header with threshold
    print(f"{Colors.HEADER}🔍 Fuzzy search for '~{Colors.BOLD}{query}{Colors.END}{Colors.HEADER}' (threshold: {threshold}){Colors.END}")
    if offset == 0:
        # First page
        if has_more_results:
            print(f"{Colors.INFO}Found {len(all_matches)} similar matches (showing first {len(matches)}):{Colors.END}")
        else:
            print(f"{Colors.INFO}Found {len(matches)} similar matches:{Colors.END}")
    else:
        # Subsequent pages
        page_num = (offset // limit) + 1
        if has_more_results:
            print(f"{Colors.INFO}Found {len(all_matches)} similar matches (page {page_num}, showing {len(matches)} matches):{Colors.END}")
        else:
            print(f"{Colors.INFO}Found {len(all_matches)} similar matches (page {page_num}, showing {len(matches)} matches):{Colors.END}")
    print()
    
    # Generate letter labels for matches
    letters = []
    for i in range(len(matches)):
        if i < 26:
            letters.append(chr(ord('a') + i))
        else:
            # After z, use aa, ab, ac, etc.
            first_letter = chr(ord('a') + (i - 26) // 26)
            second_letter = chr(ord('a') + (i - 26) % 26)
            letters.append(first_letter + second_letter)
    
    # Add "more results" option if needed - always use "0" for consistency
    more_results_letter = None
    if has_more_results:
        more_results_letter = '0'
    
    # Display matches with letters
    for i, (article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number) in enumerate(matches):
        # Format word class
        word_class_display = f" [{word_class.lower()}]" if word_class else ""
        
        # Format gender
        gender_display = ""
        if gender:
            if gender == 'MASC':
                gender_display = f" {Colors.MASCULINE}(masculine){Colors.END}"
            elif gender == 'FEM':
                gender_display = f" {Colors.FEMININE}(feminine){Colors.END}"
            elif gender == 'NEUT':
                gender_display = f" {Colors.NEUTER}(neuter){Colors.END}"
        
        # Apply fuzzy highlighting to show matching vs non-matching characters
        highlighted_lemma = _highlight_fuzzy_differences(query, lemma, Colors)
        
        # Add homonym number if it exists and is greater than 1
        homonym_display = f" ({homonym_number})" if homonym_number and homonym_number > 1 else ""
        
        # Display entry
        print(f"  {Colors.BOLD}{letters[i]}){Colors.END} {highlighted_lemma}{homonym_display}{word_class_display}{gender_display}")
    
    # Display "more results" option if needed
    if has_more_results:
        remaining_count = len(all_matches) - len(matches)
        print(f"  {Colors.BOLD}{more_results_letter}){Colors.END} {Colors.INFO}...more results ({remaining_count} additional matches){Colors.END}")
    
    print()
    if has_more_results:
        print(f"{Colors.INFO}Press a letter to view the entry, 0 or spacebar for more results, or Enter to cancel: {Colors.END}", end='', flush=True)
    else:
        print(f"{Colors.INFO}Press a letter to view the entry, or Enter to cancel: {Colors.END}", end='', flush=True)
    
    try:
        choice = get_single_keypress().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        return 'CANCELLED'
    
    # Handle Enter key or Ctrl+C
    if choice in ['\r', '\n', '\x03']:  # Enter, newline, or Ctrl+C
        print()
        return 'CANCELLED'
    
    # Check if user selected "more results"
    if has_more_results and (choice == '0' or choice == ' '):
        # Show next page of results
        new_offset = offset + limit
        print(f"\n{Colors.INFO}Showing next page...{Colors.END}\n")
        return search_fuzzy_interactive(conn, query, threshold, include_expr, new_offset)
    
    # Find the selected entry
    for i, letter in enumerate(letters):
        if choice == letter and i < len(matches):
            print()  # Add newline before showing the entry
            return matches[i]
    
    print(f"\n{Colors.WARNING}Invalid selection.{Colors.END}")
    return 'CANCELLED'


def search_prefix_interactive(conn, query, include_expr=False, offset=0):
    """Interactive prefix search that presents results as a lettered list.
    
    Returns None if user cancels, or the selected result if chosen.
    """
    from .config import search_config, Colors
    from .utils import get_single_keypress
    
    # Get prefix matches
    all_matches = search_prefix(conn, query, include_expr)
    
    if not all_matches:
        return None
    
    # Use configured limit
    limit = search_config.interactive_results_limit
    
    # Calculate pagination
    start_idx = offset
    end_idx = offset + limit
    matches = all_matches[start_idx:end_idx]
    
    # Check if we have more results after this page
    has_more_results = end_idx < len(all_matches)
    
    # If no matches in this page (offset too high), return None
    if not matches:
        return None
    
    # Display the prefix search header
    print(f"{Colors.HEADER}🔍 Prefix search for '{Colors.BOLD}{query}@{Colors.END}{Colors.HEADER}'{Colors.END}")
    if offset == 0:
        # First page
        if has_more_results:
            print(f"{Colors.INFO}Found {len(all_matches)} prefix matches (showing first {len(matches)}):{Colors.END}")
        else:
            print(f"{Colors.INFO}Found {len(matches)} prefix matches:{Colors.END}")
    else:
        # Subsequent pages
        page_num = (offset // limit) + 1
        if has_more_results:
            print(f"{Colors.INFO}Found {len(all_matches)} prefix matches (page {page_num}, showing {len(matches)} matches):{Colors.END}")
        else:
            print(f"{Colors.INFO}Found {len(all_matches)} prefix matches (page {page_num}, showing {len(matches)} matches):{Colors.END}")
    print()
    
    # Generate letter labels for matches
    letters = []
    for i in range(len(matches)):
        if i < 26:
            letters.append(chr(ord('a') + i))
        else:
            # After z, use aa, ab, ac, etc.
            first_letter = chr(ord('a') + (i - 26) // 26)
            second_letter = chr(ord('a') + (i - 26) % 26)
            letters.append(first_letter + second_letter)
    
    # Add "more results" option if needed - always use "0" for consistency
    more_results_letter = None
    if has_more_results:
        more_results_letter = '0'
    
    # Display matches with letters
    for i, (article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number) in enumerate(matches):
        # Format word class
        word_class_display = f" [{word_class.lower()}]" if word_class else ""
        
        # Format gender
        gender_display = ""
        if gender:
            if gender == 'MASC':
                gender_display = f" {Colors.MASCULINE}(masculine){Colors.END}"
            elif gender == 'FEM':
                gender_display = f" {Colors.FEMININE}(feminine){Colors.END}"
            elif gender == 'NEUT':
                gender_display = f" {Colors.NEUTER}(neuter){Colors.END}"
        
        # Apply prefix highlighting to show the matching prefix
        highlighted_lemma = _highlight_prefix_match(query, lemma, Colors)
        
        # Add homonym number if it exists and is greater than 1
        homonym_display = f" ({homonym_number})" if homonym_number and homonym_number > 1 else ""
        
        # Display entry
        print(f"  {Colors.BOLD}{letters[i]}){Colors.END} {highlighted_lemma}{homonym_display}{word_class_display}{gender_display}")
    
    # Display "more results" option if needed
    if has_more_results:
        remaining_count = len(all_matches) - len(matches)
        print(f"  {Colors.BOLD}{more_results_letter}){Colors.END} {Colors.INFO}...more results ({remaining_count} additional matches){Colors.END}")
    
    print()
    if has_more_results:
        print(f"{Colors.INFO}Press a letter to view the entry, 0 or spacebar for more results, or Enter to cancel: {Colors.END}", end='', flush=True)
    else:
        print(f"{Colors.INFO}Press a letter to view the entry, or Enter to cancel: {Colors.END}", end='', flush=True)
    
    try:
        choice = get_single_keypress().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        return 'CANCELLED'
    
    # Handle Enter key or Ctrl+C
    if choice in ['\r', '\n', '\x03']:  # Enter, newline, or Ctrl+C
        print()
        return 'CANCELLED'
    
    # Check if user selected "more results"
    if has_more_results and (choice == '0' or choice == ' '):
        # Show next page of results
        new_offset = offset + limit
        print(f"\n{Colors.INFO}Showing next page...{Colors.END}\n")
        return search_prefix_interactive(conn, query, include_expr, new_offset)
    
    # Find the selected entry
    for i, letter in enumerate(letters):
        if choice == letter and i < len(matches):
            print()  # Add newline before showing the entry
            return matches[i]
    
    print(f"\n{Colors.WARNING}Invalid selection.{Colors.END}")
    return 'CANCELLED'


def search_anywhere_term_interactive(conn, query, include_expr=False, offset=0):
    """Interactive anywhere term search that presents results as a lettered list.
    
    Returns None if user cancels, or the selected result if chosen.
    """
    from .config import search_config, Colors
    from .utils import get_single_keypress
    
    # Get anywhere term matches
    all_matches = search_anywhere_term(conn, query, include_expr)
    
    if not all_matches:
        return None
    
    # Use configured limit
    limit = search_config.interactive_results_limit
    
    # Calculate pagination
    start_idx = offset
    end_idx = offset + limit
    matches = all_matches[start_idx:end_idx]
    
    # Check if we have more results after this page
    has_more_results = end_idx < len(all_matches)
    
    # If no matches in this page (offset too high), return None
    if not matches:
        return None
    
    # Display the anywhere term search header
    print(f"{Colors.HEADER}🔍 Anywhere term search for '{Colors.BOLD}@{query}{Colors.END}{Colors.HEADER}'{Colors.END}")
    if offset == 0:
        # First page
        if has_more_results:
            print(f"{Colors.INFO}Found {len(all_matches)} matches containing '{query}' (showing first {len(matches)}):{Colors.END}")
        else:
            print(f"{Colors.INFO}Found {len(matches)} matches containing '{query}':{Colors.END}")
    else:
        # Subsequent pages
        page_num = (offset // limit) + 1
        if has_more_results:
            print(f"{Colors.INFO}Found {len(all_matches)} matches containing '{query}' (page {page_num}, showing {len(matches)} matches):{Colors.END}")
        else:
            print(f"{Colors.INFO}Found {len(all_matches)} matches containing '{query}' (page {page_num}, showing {len(matches)} matches):{Colors.END}")
    print()
    
    # Generate letter labels for matches
    letters = []
    for i in range(len(matches)):
        if i < 26:
            letters.append(chr(ord('a') + i))
        else:
            # After z, use aa, ab, ac, etc.
            first_letter = chr(ord('a') + (i - 26) // 26)
            second_letter = chr(ord('a') + (i - 26) % 26)
            letters.append(first_letter + second_letter)
    
    # Add "more results" option if needed - always use "0" for consistency
    more_results_letter = None
    if has_more_results:
        more_results_letter = '0'
    
    # Display matches with letters
    for i, (article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number) in enumerate(matches):
        # Format word class
        word_class_display = f" [{word_class.lower()}]" if word_class else ""
        
        # Format gender
        gender_display = ""
        if gender:
            if gender == 'MASC':
                gender_display = f" {Colors.MASCULINE}(masculine){Colors.END}"
            elif gender == 'FEM':
                gender_display = f" {Colors.FEMININE}(feminine){Colors.END}"
            elif gender == 'NEUT':
                gender_display = f" {Colors.NEUTER}(neuter){Colors.END}"
        
        # Apply anywhere highlighting to show the matching substring
        highlighted_lemma = _highlight_anywhere_match(query, lemma, Colors)
        
        # Add homonym number if it exists and is greater than 1
        homonym_display = f" ({homonym_number})" if homonym_number and homonym_number > 1 else ""
        
        # Display entry
        print(f"  {Colors.BOLD}{letters[i]}){Colors.END} {highlighted_lemma}{homonym_display}{word_class_display}{gender_display}")
    
    # Display "more results" option if needed
    if has_more_results:
        remaining_count = len(all_matches) - len(matches)
        print(f"  {Colors.BOLD}{more_results_letter}){Colors.END} {Colors.INFO}...more results ({remaining_count} additional matches){Colors.END}")
    
    print()
    if has_more_results:
        print(f"{Colors.INFO}Press a letter to view the entry, 0 or spacebar for more results, or Enter to cancel: {Colors.END}", end='', flush=True)
    else:
        print(f"{Colors.INFO}Press a letter to view the entry, or Enter to cancel: {Colors.END}", end='', flush=True)
    
    try:
        choice = get_single_keypress().lower()
    except (KeyboardInterrupt, EOFError):
        print()
        return 'CANCELLED'
    
    # Handle Enter key or Ctrl+C
    if choice in ['\r', '\n', '\x03']:  # Enter, newline, or Ctrl+C
        print()
        return 'CANCELLED'
    
    # Check if user selected "more results"
    if has_more_results and (choice == '0' or choice == ' '):
        # Show next page of results
        new_offset = offset + limit
        print(f"\n{Colors.INFO}Showing next page...{Colors.END}\n")
        return search_anywhere_term_interactive(conn, query, include_expr, new_offset)
    
    # Find the selected entry
    for i, letter in enumerate(letters):
        if choice == letter and i < len(matches):
            print()  # Add newline before showing the entry
            return matches[i]
    
    print(f"\n{Colors.WARNING}Invalid selection.{Colors.END}")
    return 'CANCELLED'


def search_anywhere(conn, query, include_expr=False):
    """Search anywhere in definitions and examples."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        expr_filter = "" if include_expr else "AND a.word_class != 'EXPR'"
        cursor.execute(f'''
            SELECT DISTINCT a.article_id, a.lemma, a.all_lemmas, a.word_class, a.gender, a.inflections, a.inflection_table, a.etymology, a.homonym_number
            FROM articles a
            LEFT JOIN definitions d ON a.article_id = d.article_id
            LEFT JOIN examples e ON a.article_id = e.article_id
            WHERE (d.content LIKE ? COLLATE NOCASE 
            OR e.quote LIKE ? COLLATE NOCASE
            OR a.all_lemmas LIKE ? COLLATE NOCASE) {expr_filter}
        ''', (f'%{variant}%', f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length first (shortest first), then alphabetically
    results.sort(key=lambda x: (len(x[1]), x[1].lower()))
    return results


def search_expressions_only(conn, query):
    """Search only for expressions (word_class = 'EXPR')."""
    cursor = conn.cursor()
    results = []
    seen_ids = set()
    
    # Get all query variants with character replacements
    query_variants = apply_character_replacement(query)
    
    for variant in query_variants:
        cursor.execute('''
            SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
            FROM articles 
            WHERE word_class = 'EXPR' AND (
                lemma LIKE ? COLLATE NOCASE
                OR all_lemmas LIKE ? COLLATE NOCASE
            )
        ''', (f'%{variant}%', f'%{variant}%'))
        
        for result in cursor.fetchall():
            if result[0] not in seen_ids:
                results.append(result)
                seen_ids.add(result[0])
    
    # Sort by lemma length first (shortest first), then alphabetically
    results.sort(key=lambda x: (len(x[1]), x[1].lower()))
    return results


def search_all_examples(conn, query):
    """Find all examples across the dictionary that contain the exact target word."""
    cursor = conn.cursor()
    
    # Apply character replacement to the query
    query_variants = apply_character_replacement(query)
    
    all_examples = []
    seen_examples = set()  # To avoid duplicates
    
    for variant in query_variants:
        # Search in regular examples table
        cursor.execute('''
            SELECT DISTINCT e.quote, e.explanation, a.lemma, a.word_class
            FROM examples e
            JOIN articles a ON e.article_id = a.article_id
            WHERE e.quote IS NOT NULL AND e.quote != ''
            AND e.quote LIKE ? COLLATE NOCASE
            ORDER BY a.lemma, e.id
        ''', (f'%{variant}%',))
        
        for quote, explanation, lemma, word_class in cursor.fetchall():
            if quote and quote not in seen_examples:
                # Check if it's actually an exact word match (not part of another word)
                import re
                # Use word boundaries to ensure exact matches
                pattern = r'\\b' + re.escape(variant.lower()) + r'\\b'
                if re.search(pattern, quote.lower()):
                    all_examples.append((quote, explanation, lemma, word_class))
                    seen_examples.add(quote)
                else:
                    # Also try simple space-separated word matching as fallback
                    words = quote.lower().split()
                    if variant.lower() in words:
                        all_examples.append((quote, explanation, lemma, word_class))
                        seen_examples.add(quote)
    
    # Sort by lemma name for organized output
    all_examples.sort(key=lambda x: x[2])  # Sort by lemma
    return all_examples


def get_related_expressions(conn, search_term):
    """Get fixed expressions that are explicitly linked to the search term."""
    cursor = conn.cursor()
    
    # Get expressions that are explicitly linked to this search term via cross-references
    cursor.execute('''
        SELECT DISTINCT a.article_id, a.lemma, d.id as def_id, d.content, e.quote, e.explanation
        FROM expression_links el
        JOIN articles a ON el.expression_article_id = a.article_id
        LEFT JOIN definitions d ON a.article_id = d.article_id
        LEFT JOIN examples e ON d.id = e.definition_id
        WHERE el.target_lemma = ? AND a.word_class = 'EXPR'
        ORDER BY a.lemma, d.order_num, d.id
    ''', (search_term,))
    
    linked_expressions = cursor.fetchall()
    
    # Group by expression lemma and definition
    expr_dict = {}
    for article_id, lemma, def_id, content, quote, explanation in linked_expressions:
        if lemma not in expr_dict:
            expr_dict[lemma] = {'definitions': []}
        
        # Find if this definition already exists
        def_found = False
        for def_data in expr_dict[lemma]['definitions']:
            if def_data['id'] == def_id:
                if quote:
                    def_data['examples'].append((quote, explanation))
                def_found = True
                break
        
        # If definition not found, add it
        if not def_found and content:
            expr_dict[lemma]['definitions'].append({
                'id': def_id,
                'content': content,
                'examples': [(quote, explanation)] if quote else []
            })
    
    return expr_dict


def get_definitions_and_examples(conn, article_id):
    """Get structured definitions and examples for an article."""
    cursor = conn.cursor()
    
    # Get definitions ordered by level and order_num
    cursor.execute('''
        SELECT id, definition_id, parent_id, level, content, order_num
        FROM definitions 
        WHERE article_id = ? 
        ORDER BY level, order_num
    ''', (article_id,))
    definitions = cursor.fetchall()
    
    # Get examples
    cursor.execute('''
        SELECT definition_id, quote, explanation
        FROM examples 
        WHERE article_id = ?
    ''', (article_id,))
    examples = cursor.fetchall()
    
    # Group examples by definition
    examples_by_def = {}
    for def_id, quote, explanation in examples:
        if def_id not in examples_by_def:
            examples_by_def[def_id] = []
        examples_by_def[def_id].append((quote, explanation))
    
    return definitions, examples_by_def


def get_random_entries(conn, count=1, include_expr=False):
    """Get random dictionary entries.
    
    Args:
        conn: Database connection
        count: Number of random entries to get
        include_expr: Whether to include expressions in results
        
    Returns:
        List of article tuples in standard format
    """
    cursor = conn.cursor()
    expr_filter = "" if include_expr else "WHERE word_class != 'EXPR'"
    
    # SQLite's RANDOM() function for random selection
    cursor.execute(f'''
        SELECT article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number
        FROM articles 
        {expr_filter}
        ORDER BY RANDOM()
        LIMIT ?
    ''', (count,))
    
    return cursor.fetchall()