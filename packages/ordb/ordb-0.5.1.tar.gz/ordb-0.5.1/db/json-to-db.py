#!/usr/bin/env python3
"""
Convert article.json (Norwegian dictionary) to SQLite database.
Creates an indexed database with proper structured data extraction including fixed expressions and abbreviation expansion.
Fixed to handle nested definition structures correctly.
"""

import json
import sqlite3
import sys
import re
from pathlib import Path

def load_concepts():
    """Load abbreviation expansions from concepts.json."""
    try:
        with open('concepts.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data['concepts']
    except FileNotFoundError:
        print("Warning: concepts.json not found. Abbreviation expansion will be skipped.")
        return {}

def expand_abbreviations_comprehensive(text, abbreviations):
    """Expand abbreviations in text using the concepts.json data."""
    if not text or not abbreviations:
        return text
    
    result = text
    
    # Handle specific replacements first
    # Replace "e l" with "eller lignende"
    result = result.replace(' e l ', ' eller lignende ')
    result = result.replace(' e l,', ' eller lignende,')
    result = result.replace(' e l.', ' eller lignende.')
    result = result.replace(' e l;', ' eller lignende;')
    
    # Replace "t forsk f" with "til forskjell fra" (handle spaces vs underscores)
    result = result.replace(' t forsk f ', ' til forskjell fra ')
    result = result.replace(' t forsk f,', ' til forskjell fra,')
    result = result.replace(' t forsk f.', ' til forskjell fra.')
    result = result.replace(' t forsk f;', ' til forskjell fra;')
    result = result.replace('t forsk f ', 'til forskjell fra ')
    
    # Replace standalone "el" with "eller" (but be careful about context)
    result = re.sub(r'\bel\b(?=\s)', 'eller', result)
    
    # Expand other common abbreviations from concepts.json
    priority_abbrevs = {
        'norr.': 'norrønt',
        'lat.': 'latin', 
        'gr.': 'gresk',
        'fr.': 'fransk',
        'eng.': 'engelsk',
        'ty.': 'tysk',
        'da.': 'dansk',
        'sv.': 'svensk',
        'jf': 'jamfør',
        'bl_a': 'blant annet',
        'f_eks': 'for eksempel',
        'dvs': 'det vil si',
        'osv': 'og så videre',
        'o_l': 'og lignende',
        'e_l': 'eller lignende',
        'el': 'eller',
        't_forsk_f': 'til forskjell fra',
        'sj': 'sjelden',
        'tidl': 'tidligere',
        'overf': 'i overført betydning'
    }
    
    # Apply priority abbreviations
    for abbrev, expansion in priority_abbrevs.items():
        if abbrev in abbreviations and abbreviations[abbrev].get('expansion') == expansion:
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            result = re.sub(pattern, expansion, result)
    
    return result

def create_database(db_path):
    """Create SQLite database with proper schema and indexes."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Drop existing tables if they exist
    cursor.execute('DROP TABLE IF EXISTS articles')
    cursor.execute('DROP TABLE IF EXISTS definitions')
    cursor.execute('DROP TABLE IF EXISTS examples')
    cursor.execute('DROP TABLE IF EXISTS expression_links')
    
    # Create main articles table
    cursor.execute('''
        CREATE TABLE articles (
            article_id TEXT PRIMARY KEY,
            lemma TEXT NOT NULL,
            all_lemmas TEXT,
            word_class TEXT,
            gender TEXT,
            inflections TEXT,
            inflection_table JSON,
            etymology TEXT,
            pronunciation TEXT,
            status INTEGER,
            author TEXT,
            updated TEXT,
            edit_state TEXT,
            homonym_number INTEGER
        )
    ''')
    
    # Create definitions table (hierarchical)
    cursor.execute('''
        CREATE TABLE definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT,
            definition_id INTEGER,
            parent_id INTEGER,
            level INTEGER,
            content TEXT,
            order_num INTEGER,
            FOREIGN KEY (article_id) REFERENCES articles (article_id)
        )
    ''')
    
    # Create examples table
    cursor.execute('''
        CREATE TABLE examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            article_id TEXT,
            definition_id INTEGER,
            quote TEXT,
            explanation TEXT,
            FOREIGN KEY (article_id) REFERENCES articles (article_id)
        )
    ''')
    
    # Create expression_links table to store cross-references
    cursor.execute('''
        CREATE TABLE expression_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            expression_article_id TEXT,
            target_lemma TEXT,
            target_article_id TEXT,
            FOREIGN KEY (expression_article_id) REFERENCES articles (article_id)
        )
    ''')
    
    # Create indexes
    cursor.execute('CREATE INDEX idx_lemma ON articles(lemma)')
    cursor.execute('CREATE INDEX idx_all_lemmas ON articles(all_lemmas)')
    cursor.execute('CREATE INDEX idx_word_class ON articles(word_class)')
    cursor.execute('CREATE INDEX idx_definitions_article ON definitions(article_id)')
    cursor.execute('CREATE INDEX idx_examples_article ON examples(article_id)')
    cursor.execute('CREATE INDEX idx_expression_links_target ON expression_links(target_lemma)')
    cursor.execute('CREATE INDEX idx_expression_links_expression ON expression_links(expression_article_id)')
    
    return conn

def extract_etymology(etymology_list, abbreviations):
    """Extract etymology information with abbreviation expansion."""
    if not etymology_list:
        return ''
    etymology_parts = []
    for etym in etymology_list:
        if 'content' in etym:
            content = str(etym['content'])
            items = etym.get('items', [])
            content, _ = replace_placeholders(content, items)
            if content:
                # Expand abbreviations in etymology
                content = expand_abbreviations_comprehensive(content, abbreviations)
                etymology_parts.append(content)
    return ' | '.join(etymology_parts)

def replace_placeholders(content, items):
    """Replace $ placeholders with actual content from items."""
    if not content or not items:
        return content, []
    
    result = content
    referenced_lemmas = []
    
    for item in items:
        if isinstance(item, dict):
            # Handle article references
            if item.get('type_') == 'article_ref' and 'lemmas' in item:
                lemmas = [lemma.get('lemma', '') for lemma in item['lemmas']]
                lemma_text = ', '.join(lemmas)
                result = result.replace('$', lemma_text, 1)
                # Store referenced lemmas for cross-reference tracking
                referenced_lemmas.extend(lemmas)
            # Handle entity references
            elif item.get('type_') == 'entity' and 'id' in item:
                entity_text = item['id'].replace('_', ' ')
                result = result.replace('$', entity_text, 1)
            # Handle usage references
            elif item.get('type_') == 'usage' and 'text' in item:
                result = result.replace('$', item['text'], 1)
    
    # Remove any remaining $ symbols
    result = result.replace('$', '').strip()
    # Clean up extra spaces and commas
    result = ' '.join(result.split())
    result = result.replace(' ,', ',').replace(',,', ',')
    
    return result, referenced_lemmas

def extract_cross_references(content, items):
    """Extract cross-reference information from Se:/Sjå: references."""
    referenced_lemmas = []
    
    if content and (content.startswith('Se:') or content.startswith('Sjå:')):
        # Extract referenced lemmas from items
        for item in items or []:
            if isinstance(item, dict) and item.get('type_') == 'article_ref' and 'lemmas' in item:
                for lemma_info in item['lemmas']:
                    if 'lemma' in lemma_info:
                        referenced_lemmas.append(lemma_info['lemma'])
    
    return referenced_lemmas

def find_all_cross_references(element):
    """Recursively find all cross-references in any part of a definition structure."""
    cross_references = []
    
    if isinstance(element, dict):
        if element.get('type_') == 'explanation':
            content = element.get('content', '')
            items = element.get('items', [])
            if content and (content.startswith('Se:') or content.startswith('Sjå:')):
                refs = extract_cross_references(content, items)
                cross_references.extend(refs)
        
        # Recursively check all dict values
        for key, value in element.items():
            sub_refs = find_all_cross_references(value)
            cross_references.extend(sub_refs)
    
    elif isinstance(element, list):
        for item in element:
            sub_refs = find_all_cross_references(item)
            cross_references.extend(sub_refs)
    
    return cross_references

def extract_compound_words_from_element(element):
    """Extract compound words from compound_list elements."""
    if isinstance(element, dict):
        if element.get('type_') == 'compound_list':
            intro = element.get('intro', {}).get('content', '')
            compounds = []
            for elem in element.get('elements', []):
                if elem.get('type_') == 'article_ref' and 'lemmas' in elem:
                    lemmas = [lemma.get('lemma', '') for lemma in elem['lemmas']]
                    compounds.extend(lemmas)
            if compounds:
                return f"{intro}: {', '.join(compounds)}"
        elif 'elements' in element:
            for sub_elem in element['elements']:
                result = extract_compound_words_from_element(sub_elem)
                if result:
                    return result
    elif isinstance(element, list):
        for item in element:
            result = extract_compound_words_from_element(item)
            if result:
                return result
    return None

def process_definition_element(element, article_id, cursor, main_lemma, abbreviations, parent_db_id=None, level=0):
    """Process a single definition element and return its database ID."""
    if not isinstance(element, dict) or element.get('type_') != 'definition':
        return None
    
    
    definition_content_parts = []
    examples = []
    compound_words = None
    has_nested_definitions = False
    cross_references = []
    
    # Find all cross-references in this definition structure (recursively)
    cross_references = find_all_cross_references(element)
    
    # Check if this definition has nested definitions
    if 'elements' in element:
        for sub_element in element['elements']:
            if isinstance(sub_element, dict) and sub_element.get('type_') == 'definition':
                has_nested_definitions = True
                break
    
    # If this definition has nested definitions, process both main content AND nested definitions
    if has_nested_definitions:
        # First, process the main explanation elements (before nested definitions)
        if 'elements' in element:
            for sub_element in element['elements']:
                if isinstance(sub_element, dict):
                    if sub_element.get('type_') == 'explanation':
                        content = sub_element.get('content', '')
                        items = sub_element.get('items', [])
                        if content:
                            # Skip cross-references as they're handled separately
                            if not (content.startswith('Se:') or content.startswith('Sjå:')):
                                # Regular content
                                processed_content, _ = replace_placeholders(content, items)
                                definition_content_parts.append(processed_content)
                                
                    elif sub_element.get('type_') == 'example':
                        quote = ''
                        explanation = ''
                        if 'quote' in sub_element:
                            quote = sub_element['quote'].get('content', '')
                            # Replace $ with the main lemma in examples
                            if quote and '$' in quote:
                                quote = quote.replace('$', main_lemma)
                        if 'explanation' in sub_element:
                            explanation = sub_element['explanation'].get('content', '')
                        if quote:
                            examples.append((quote, explanation))
        
        # Then process nested definitions separately
        for sub_element in element['elements']:
            if isinstance(sub_element, dict) and sub_element.get('type_') == 'definition':
                # Check if this is a sub-definition that should be included in parent content
                if sub_element.get('sub_definition', False):
                    # This is a sub-definition - include its content as part of the parent definition
                    sub_content_parts = []
                    sub_examples = []
                    
                    if 'elements' in sub_element:
                        for sub_sub_element in sub_element['elements']:
                            if isinstance(sub_sub_element, dict):
                                if sub_sub_element.get('type_') == 'explanation':
                                    sub_content = sub_sub_element.get('content', '')
                                    sub_items = sub_sub_element.get('items', [])
                                    if sub_content and not (sub_content.startswith('Se:') or sub_content.startswith('Sjå:')):
                                        processed_sub_content, _ = replace_placeholders(sub_content, sub_items)
                                        sub_content_parts.append(processed_sub_content)
                                
                                elif sub_sub_element.get('type_') == 'example':
                                    quote = ''
                                    explanation = ''
                                    if 'quote' in sub_sub_element:
                                        quote = sub_sub_element['quote'].get('content', '')
                                        if quote and '$' in quote:
                                            quote = quote.replace('$', main_lemma)
                                    if 'explanation' in sub_sub_element:
                                        explanation = sub_sub_element['explanation'].get('content', '')
                                    if quote:
                                        sub_examples.append((quote, explanation))
                    
                    # Add sub-definition content to the main definition content
                    if sub_content_parts:
                        sub_definition_text = '; '.join(sub_content_parts)
                        definition_content_parts.append(sub_definition_text)
                    
                    # Add sub-definition examples to main examples
                    examples.extend(sub_examples)
                else:
                    # This is a regular nested definition - process as separate definition
                    process_definition_element(sub_element, article_id, cursor, main_lemma, abbreviations, parent_db_id, level)
        
        # Store cross-references even if we have nested definitions
        if cross_references:
            for ref_lemma in cross_references:
                if ref_lemma.strip():
                    cursor.execute('''
                        INSERT INTO expression_links (expression_article_id, target_lemma, target_article_id)
                        VALUES (?, ?, NULL)
                    ''', (article_id, ref_lemma.strip()))
        
        # Continue to process the main definition content if any was found
        # Don't return None here - let it fall through to create the main definition entry
    
    # Process elements within this definition (only if no nested definitions)  
    if 'elements' in element and not has_nested_definitions:
        for sub_element in element['elements']:
            if isinstance(sub_element, dict):
                if sub_element.get('type_') == 'explanation':
                    content = sub_element.get('content', '')
                    items = sub_element.get('items', [])
                    if content:
                        # Skip cross-references as they're handled separately
                        if not (content.startswith('Se:') or content.startswith('Sjå:')):
                            # Regular content
                            processed_content, _ = replace_placeholders(content, items)
                            definition_content_parts.append(processed_content)
                            
                elif sub_element.get('type_') == 'example':
                    quote = ''
                    explanation = ''
                    if 'quote' in sub_element:
                        quote = sub_element['quote'].get('content', '')
                        # Replace $ with the main lemma in examples
                        if quote and '$' in quote:
                            quote = quote.replace('$', main_lemma)
                    if 'explanation' in sub_element:
                        explanation = sub_element['explanation'].get('content', '')
                    if quote:
                        examples.append((quote, explanation))
                        
                elif sub_element.get('type_') == 'compound_list':
                    # Extract compound words for this specific definition
                    compound_words = extract_compound_words_from_element(sub_element)
                
                elif sub_element.get('type_') == 'definition':
                    # This is handled by the nested definitions check above
                    continue
    
    # Combine definition content
    definition_content = '; '.join(definition_content_parts)
    
    # Add compound words to definition if present
    if compound_words:
        if definition_content:
            definition_content += '; ' + compound_words
        else:
            definition_content = compound_words
    
    # Expand abbreviations in the final definition content
    definition_content = expand_abbreviations_comprehensive(definition_content, abbreviations)
    
    # Store cross-references for expressions (even if no definition content)
    for ref_lemma in cross_references:
        if ref_lemma.strip():
            cursor.execute('''
                INSERT INTO expression_links (expression_article_id, target_lemma, target_article_id)
                VALUES (?, ?, NULL)
            ''', (article_id, ref_lemma.strip()))
    
    # Insert this definition only if it has meaningful content
    if definition_content and definition_content.strip() and definition_content.strip() != '$':
        cursor.execute('''
            INSERT INTO definitions (article_id, definition_id, parent_id, level, content, order_num)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (article_id, element.get('id'), parent_db_id, level, definition_content, 0))
        
        definition_db_id = cursor.lastrowid
        
        # Insert examples for this definition
        for quote, explanation in examples:
            cursor.execute('''
                INSERT INTO examples (article_id, definition_id, quote, explanation)
                VALUES (?, ?, ?, ?)
            ''', (article_id, definition_db_id, quote, explanation))
        
        return definition_db_id
    
    return None


def extract_definitions_recursive(element, article_id, cursor, main_lemma, abbreviations, parent_db_id=None, level=0):
    """Recursively extract definitions from nested structures."""
    if isinstance(element, dict) and element.get('type_') == 'definition':
        # Check if this definition has nested definitions
        nested_definitions = []
        if 'elements' in element:
            for sub_element in element['elements']:
                if isinstance(sub_element, dict) and sub_element.get('type_') == 'definition':
                    nested_definitions.append(sub_element)
        
        # Always process the main definition - let process_definition_element handle nested logic
        process_definition_element(element, article_id, cursor, main_lemma, abbreviations, parent_db_id, level)
    
    elif isinstance(element, list):
        for item in element:
            extract_definitions_recursive(item, article_id, cursor, main_lemma, abbreviations, parent_db_id, level)

def resolve_expression_links(cursor):
    """Resolve target_article_id for expression links after all articles are processed."""
    print("Resolving expression cross-reference links...")
    
    cursor.execute('''
        UPDATE expression_links 
        SET target_article_id = (
            SELECT article_id 
            FROM articles 
            WHERE lemma = expression_links.target_lemma 
            AND word_class != 'EXPR'
            LIMIT 1
        )
        WHERE target_article_id IS NULL
    ''')
    
    # Get statistics
    cursor.execute('SELECT COUNT(*) FROM expression_links WHERE target_article_id IS NOT NULL')
    resolved_count = cursor.fetchone()[0]
    cursor.execute('SELECT COUNT(*) FROM expression_links')
    total_count = cursor.fetchone()[0]
    
    print(f"  - Resolved {resolved_count}/{total_count} expression links")
    
    # Clean up unresolved links
    cursor.execute('DELETE FROM expression_links WHERE target_article_id IS NULL')
    
    return resolved_count

def process_article(article_id, article_data, cursor, abbreviations):
    """Process a single article and extract all structured data."""
    lemmas = []
    word_classes = []
    genders = []
    inflections = []
    inflection_tables = []
    
    # Extract lemmas and grammatical information
    if 'lemmas' in article_data:
        for lemma_data in article_data['lemmas']:
            if 'lemma' in lemma_data:
                lemmas.append(lemma_data['lemma'])
            
            # Extract grammatical info and inflection tables
            if 'paradigm_info' in lemma_data:
                for paradigm in lemma_data['paradigm_info']:
                    if 'tags' in paradigm:
                        for tag in paradigm['tags']:
                            if tag in ['NOUN', 'VERB', 'ADJ', 'ADV', 'EXPR']:
                                word_classes.append(tag)
                            elif tag in ['Masc', 'Fem', 'Neuter']:
                                genders.append(tag)
                    
                    # Extract inflection table with tags
                    if 'inflection' in paradigm:
                        table = []
                        for infl in paradigm['inflection']:
                            if 'word_form' in infl and infl['word_form']:
                                inflections.append(infl['word_form'])
                                tags = infl.get('tags', [])
                                table.append({
                                    'form': infl['word_form'],
                                    'tags': tags
                                })
                        if table:
                            inflection_tables.append({
                                'word_class': paradigm.get('tags', [''])[0] if paradigm.get('tags') else '',
                                'inflections': table
                            })
    
    # Extract etymology with abbreviation expansion
    etymology = ''
    if 'body' in article_data and 'etymology' in article_data['body']:
        etymology = extract_etymology(article_data['body']['etymology'], abbreviations)
    
    # Extract homonym number
    homonym_number = None
    if 'lemmas' in article_data and article_data['lemmas']:
        first_lemma = article_data['lemmas'][0]
        if 'hgno' in first_lemma and first_lemma['hgno'] > 1:
            homonym_number = first_lemma['hgno']
    
    # Get primary lemma
    primary_lemma = lemmas[0] if lemmas else ''
    
    # Insert main article
    cursor.execute('''
        INSERT INTO articles 
        (article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, status, author, updated, edit_state, homonym_number)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        article_id,
        primary_lemma,
        ' | '.join(lemmas),
        ' | '.join(set(word_classes)),
        ' | '.join(set(genders)),
        ' | '.join(set(inflections)),
        json.dumps(inflection_tables, ensure_ascii=False),
        etymology,
        article_data.get('status', 0),
        article_data.get('author', ''),
        article_data.get('updated', ''),
        article_data.get('edit_state', ''),
        homonym_number
    ))
    
    # Extract definitions and examples
    if 'body' in article_data and 'definitions' in article_data['body']:
        for definition in article_data['body']['definitions']:
            extract_definitions_recursive(definition, article_id, cursor, primary_lemma, abbreviations)

def main():
    input_file = 'article.json'
    output_file = 'articles.db'
    
    if not Path(input_file).exists():
        print(f"Error: {input_file} not found")
        sys.exit(1)
    
    print(f"Converting {input_file} to {output_file}...")
    print("This may take a while for large files...")
    
    # Load abbreviations
    abbreviations = load_concepts()
    print(f"Loaded {len(abbreviations)} abbreviation expansions")
    
    # Create database
    conn = create_database(output_file)
    cursor = conn.cursor()
    
    # Process JSON file
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Processing {len(data)} articles...")
        
        batch_size = 1000
        articles_processed = 0
        
        for article_id, article_data in data.items():
            process_article(article_id, article_data, cursor, abbreviations)
            articles_processed += 1
            
            # Commit in batches for better performance
            if articles_processed % batch_size == 0:
                conn.commit()
                print(f"Processed {articles_processed} articles...")
        
        # Final commit
        conn.commit()
        
        # Resolve expression cross-reference links
        resolved_links = resolve_expression_links(cursor)
        conn.commit()
        
        print(f"Successfully converted {articles_processed} articles to {output_file}")
        
        # Show statistics
        cursor.execute("SELECT COUNT(*) FROM articles")
        article_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM definitions")
        def_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM examples")
        example_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM expression_links")
        link_count = cursor.fetchone()[0]
        
        print(f"Database contains:")
        print(f"  - {article_count} articles")
        print(f"  - {def_count} definitions")
        print(f"  - {example_count} examples")
        print(f"  - {link_count} expression cross-reference links")
        print(f"  - Abbreviations expanded automatically")
        print(f"  - Proper nested definition handling")
        print(f"  - Expression-to-main-entry relationships preserved")
        
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        conn.close()

if __name__ == '__main__':
    main()