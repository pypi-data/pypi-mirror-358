"""Display and formatting functions for ordb."""

import re
import json
import os
from pathlib import Path
from collections import Counter
from .config import Colors, search_config
from .core import get_definitions_and_examples, get_related_expressions

# Test words for the -t flag
TEST_WORDS = ['stein', 'gå', 'hus']


def _load_irregular_verbs():
    """Load irregular verbs from data file and convert to regex patterns."""
    try:
        # Find the db directory relative to this file
        current_dir = Path(__file__).parent
        project_root = current_dir.parent.parent
        irregular_verbs_file = project_root / 'db' / 'irregular_verbs.json'
        
        if not irregular_verbs_file.exists():
            # Fallback to basic irregular verbs if file not found
            return {
                'gå': r'\b(gå|går|gikk|gått)\b',
                'være': r'\b(være|er|var|vært)\b', 
                'ha': r'\b(ha|har|hadde|hatt)\b',
            }
        
        with open(irregular_verbs_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert the verb forms to regex patterns
        irregular_verbs = {}
        for infinitive, forms in data['irregular_verbs'].items():
            # Create regex pattern from all forms
            escaped_forms = [re.escape(form) for form in forms]
            pattern = r'\b(' + '|'.join(escaped_forms) + r')\b'
            irregular_verbs[infinitive] = pattern
        
        return irregular_verbs
    except Exception:
        # Fallback to basic irregular verbs if loading fails
        return {
            'gå': r'\b(gå|går|gikk|gått)\b',
            'være': r'\b(være|er|var|vært)\b', 
            'ha': r'\b(ha|har|hadde|hatt)\b',
        }


def format_word_class(word_class):
    """Format word class with colors."""
    if not word_class:
        return ""
    
    # Split by spaces or pipes to handle multiple classes
    classes = re.split(r'[ |]+', word_class)
    
    # Define color mapping
    class_colors = {
        'NOUN': f"{Colors.WORD_CLASS}noun{Colors.END}",
        'VERB': f"{Colors.WORD_CLASS}verb{Colors.END}",
        'ADJ': f"{Colors.WORD_CLASS}adj{Colors.END}",
        'ADV': f"{Colors.WORD_CLASS}adv{Colors.END}",
        'PRON': f"{Colors.WORD_CLASS}pron{Colors.END}",
        'DET': f"{Colors.WORD_CLASS}det{Colors.END}",
        'PREP': f"{Colors.WORD_CLASS}prep{Colors.END}",
        'CONJ': f"{Colors.WORD_CLASS}conj{Colors.END}",
        'INTJ': f"{Colors.WORD_CLASS}intj{Colors.END}",
        'NUM': f"{Colors.WORD_CLASS}num{Colors.END}",
        'EXPR': f"{Colors.WORD_CLASS}expr{Colors.END}",
        'SYMB': f"{Colors.WORD_CLASS}symb{Colors.END}",
        'ABBR': f"{Colors.WORD_CLASS}abbr{Colors.END}",
        'PROPN': f"{Colors.WORD_CLASS}propn{Colors.END}",
        'SUBST': f"{Colors.WORD_CLASS}subst{Colors.END}",
        'PART': f"{Colors.WORD_CLASS}part{Colors.END}",
        'AUX': f"{Colors.WORD_CLASS}aux{Colors.END}",
        'FOREIGN': f"{Colors.WORD_CLASS}foreign{Colors.END}",
        'UNKNOWN': f"{Colors.WORD_CLASS}unknown{Colors.END}"
    }
    
    colored_classes = []
    for cls in classes:
        if cls in class_colors:
            colored_classes.append(class_colors[cls])
        else:
            colored_classes.append(f"{Colors.WORD_CLASS}{cls.lower()}{Colors.END}")
    
    return f"[{', '.join(colored_classes)}]"


def format_gender(gender):
    """Format gender with colors."""
    if not gender:
        return ""
    
    color_map = {
        'Masc': f"{Colors.MASCULINE}masculine{Colors.END}",
        'Fem': f"{Colors.FEMININE}feminine{Colors.END}",
        'Neuter': f"{Colors.NEUTER}neuter{Colors.END}"
    }
    
    genders = gender.split(' | ')
    return ', '.join(color_map.get(g, g) for g in genders)


def extract_homonym_number(raw_data):
    """Extract homonym number from raw_data JSON."""
    if not raw_data:
        return None
    
    try:
        data = json.loads(raw_data)
        lemmas = data.get('lemmas', [])
        if lemmas and isinstance(lemmas, list):
            hgno = lemmas[0].get('hgno')
            return hgno if hgno and hgno > 1 else None
    except:
        return None


def extract_compound_words(definition_text):
    """Extract compound word lists from definition text, returning main definition and compound part separately."""
    if not definition_text:
        return definition_text, None
    
    # Look for compound word patterns
    compound_patterns = [
        r'(.*?);\s*(som etterledd i ord som:\s*.+)$',
        r'(.*?);\s*(som førsteledd i .*?:\s*.+)$',
        r'(.*?);\s*(brukt som førsteledd i .*?:\s*.+)$',
        r'(.*?);\s*(i ord som:\s*.+)$',
        # Handle cases where compound info is the entire definition
        r'^(brukt som førsteledd i .*?:\s*.+)$',
        r'^(som førsteledd i .*?:\s*.+)$'
    ]
    
    for pattern in compound_patterns:
        match = re.match(pattern, definition_text, re.IGNORECASE)
        if match:
            if len(match.groups()) == 2:
                # Pattern with main definition and compound part
                main_def = match.group(1).strip()
                compound_part = match.group(2).strip()
                return main_def, compound_part
            elif len(match.groups()) == 1:
                # Standalone compound pattern - no main definition
                compound_part = match.group(1).strip()
                return "", compound_part
    
    return definition_text, None


def highlight_search_term(text, search_term, base_color=Colors.EXAMPLE):
    """Highlight search term in text with green color, preserving base color for rest.
    
    This function highlights both exact matches and words that contain the search term
    as a stem (for conjugated/inflected forms).
    """
    if not search_term or not text:
        return f"{base_color}{text}{Colors.END}"
    
    # Common Norwegian verb inflection patterns
    # This is a simplified approach - a full solution would require a Norwegian stemmer
    inflection_patterns = []
    
    # Load Norwegian irregular verbs from data file
    irregular_verbs = _load_irregular_verbs()
    
    search_lower = search_term.lower()
    if search_lower in irregular_verbs:
        inflection_patterns = [irregular_verbs[search_lower]]
    else:
        # For regular words, try words that start with the search term
        inflection_patterns = [rf'\b({re.escape(search_term)}\w*)\b']
    
    highlighted = text
    
    # Apply inflection-based highlighting
    for pattern in inflection_patterns:
        inflection_re = re.compile(pattern, re.IGNORECASE)
        
        def replace_inflection_func(match):
            return f"{Colors.END}{Colors.HIGHLIGHT}{match.group(1)}{Colors.END}{base_color}"
        
        highlighted = inflection_re.sub(replace_inflection_func, highlighted)
    
    # Then apply exact match highlighting for any remaining instances
    # (in case the search term appears in the middle of words or wasn't caught above)
    exact_pattern = re.compile(re.escape(search_term), re.IGNORECASE)
    
    def replace_exact_func(match):
        # Only highlight if not already highlighted
        if f"{Colors.HIGHLIGHT}" not in match.string[max(0, match.start()-10):match.start()]:
            return f"{Colors.END}{Colors.HIGHLIGHT}{match.group()}{Colors.END}{base_color}"
        return match.group()
    
    highlighted = exact_pattern.sub(replace_exact_func, highlighted)
    
    return f"{base_color}{highlighted}{Colors.END}"


def format_inflection_table(inflection_table_json, word_class=None, lemma=None):
    """Format inflection table as a proper table, deduplicating entries and filtering redundant forms."""
    if not inflection_table_json:
        return ""
    
    try:
        tables = json.loads(inflection_table_json)
        if not tables:
            return ""
        
        # Combine all inflections from all tables and deduplicate
        all_grouped = {}
        
        for table in tables:
            word_class = table.get('word_class', '')
            inflections = table.get('inflections', [])
            
            if not inflections:
                continue
            
            # Group by grammatical categories
            for infl in inflections:
                form = infl['form']
                tags = infl['tags']
                
                if word_class == 'VERB':
                    if 'Inf' in tags:
                        key = 'Infinitive'
                    elif 'Pres' in tags:
                        key = 'Present'
                    elif 'Past' in tags:
                        key = 'Past'
                    elif 'PastPart' in tags:
                        key = 'Past Participle'
                    elif 'PresPart' in tags:
                        key = 'Present Participle'
                    else:
                        key = 'Other'
                elif word_class == 'NOUN':
                    if 'Sing' in tags and 'Ind' in tags:
                        key = 'Singular'
                    elif 'Sing' in tags and 'Def' in tags:
                        key = 'Singular Definite'
                    elif 'Plur' in tags and 'Ind' in tags:
                        key = 'Plural'
                    elif 'Plur' in tags and 'Def' in tags:
                        key = 'Plural Definite'
                    else:
                        key = 'Other'
                elif word_class == 'ADJ':
                    if 'Pos' in tags:
                        if 'Neuter' in tags:
                            key = 'Neuter'
                        elif 'Def' in tags or 'Plur' in tags:
                            key = 'Definite/Plural'
                        else:
                            key = 'Basic'
                    else:
                        key = 'Other'
                else:
                    key = ' '.join(tags) if tags else 'Other'
                
                if key not in all_grouped:
                    all_grouped[key] = set()
                all_grouped[key].add(form)
        
        # Format as single compact line with all inflection categories
        if all_grouped:
            # For EXPR word class, don't show the expressions section since it's redundant
            # (the expression is already shown as the lemma)
            if word_class == "EXPR":
                return ""
            
            header_text = "Inflections"
            inflection_parts = []
            
            # Special handling for nouns - combine singular forms and plural forms
            if 'Singular' in all_grouped or 'Singular Definite' in all_grouped:
                sing_forms = sorted(list(all_grouped.get('Singular', set())))
                sing_def_forms = sorted(list(all_grouped.get('Singular Definite', set())))
                combined_sing = sing_forms + sing_def_forms
                if combined_sing:
                    inflection_parts.append(f"{Colors.INFLECTION_LABEL}Singular:{Colors.END} {', '.join(combined_sing)}")
                # Remove these from further processing
                all_grouped.pop('Singular', None)
                all_grouped.pop('Singular Definite', None)
            
            if 'Plural' in all_grouped or 'Plural Definite' in all_grouped:
                plur_forms = sorted(list(all_grouped.get('Plural', set())))
                plur_def_forms = sorted(list(all_grouped.get('Plural Definite', set())))
                combined_plur = plur_forms + plur_def_forms
                if combined_plur:
                    inflection_parts.append(f"{Colors.INFLECTION_LABEL}Plural:{Colors.END} {', '.join(combined_plur)}")
                # Remove these from further processing
                all_grouped.pop('Plural', None)
                all_grouped.pop('Plural Definite', None)
            
            # Define order for remaining categories
            category_order = ['Infinitive', 'Present', 'Past', 'Past Participle', 'Present Participle', 
                            'Basic', 'Neuter', 'Definite/Plural', 'Other']
            
            # Sort categories by defined order
            sorted_categories = []
            for cat in category_order:
                if cat in all_grouped:
                    sorted_categories.append(cat)
            
            # Add any remaining categories
            for cat in all_grouped:
                if cat not in sorted_categories:
                    sorted_categories.append(cat)
            
            for category in sorted_categories:
                forms = sorted(list(all_grouped[category]))
                
                # Filter out forms that are identical to the lemma (avoid redundancy)
                if lemma:
                    forms = [form for form in forms if form.lower() != lemma.lower()]
                
                # Only add category if it has remaining forms
                if forms:
                    forms_str = ', '.join(forms)
                    inflection_parts.append(f"{Colors.INFLECTION_LABEL}{category}:{Colors.END} {forms_str}")
            
            # Join all parts with spaces instead of newlines to make it compact
            if inflection_parts:
                compact_inflections = ' '.join(inflection_parts)
                return f"  {Colors.BOLD}{header_text}:{Colors.END} {compact_inflections}"
            
            return ""
        
        return ""
    except:
        return ""


def format_inflection_table_multiline(inflection_table_json, word_class=None, lemma=None):
    """Format inflection table with each category on a separate line (for --only-inflections)."""
    if not inflection_table_json:
        return ""
    
    try:
        inflection_tables = json.loads(inflection_table_json)
        if not inflection_tables:
            return ""
        
        # Take the first inflection table
        table = inflection_tables[0]
        if 'inflections' not in table:
            return ""
        
        all_grouped = {}
        word_class = table.get('word_class', word_class)
        
        for inflection in table['inflections']:
            form = inflection['form']
            tags = inflection['tags']
            if word_class == 'NOUN':
                if 'Indef' in tags and 'Sing' in tags:
                    key = 'Singular'
                elif 'Def' in tags and 'Sing' in tags:
                    key = 'Singular Definite'
                elif 'Indef' in tags and 'Plur' in tags:
                    key = 'Plural'
                elif 'Def' in tags and 'Plur' in tags:
                    key = 'Plural Definite'
                else:
                    key = 'Other'
            elif word_class == 'VERB':
                if 'Inf' in tags:
                    key = 'Infinitive'
                elif 'Pres' in tags:
                    key = 'Present'
                elif 'Past' in tags:
                    key = 'Past'
                elif 'PastPart' in tags:
                    key = 'Past Participle'
                elif 'PresPart' in tags:
                    key = 'Present Participle'
                else:
                    key = 'Other'
            elif word_class == 'ADJ':
                if 'Pos' in tags:
                    if 'Neuter' in tags:
                        key = 'Neuter'
                    elif 'Def' in tags or 'Plur' in tags:
                        key = 'Definite/Plural'
                    else:
                        key = 'Basic'
                elif 'Cmp' in tags:
                    key = 'Comparative'
                elif 'Sup' in tags:
                    key = 'Superlative'
                else:
                    key = 'Other'
            else:
                key = ' '.join(tags) if tags else 'Other'
            
            if key not in all_grouped:
                all_grouped[key] = set()
            all_grouped[key].add(form)
        
        if all_grouped:
            # For EXPR word class, don't show the expressions section since it's redundant
            if word_class == "EXPR":
                return ""
            
            header_text = "Inflections"
            inflection_lines = []
            
            # Special handling for nouns - combine singular forms and plural forms
            if 'Singular' in all_grouped or 'Singular Definite' in all_grouped:
                sing_forms = sorted(list(all_grouped.get('Singular', set())))
                sing_def_forms = sorted(list(all_grouped.get('Singular Definite', set())))
                combined_sing = sing_forms + sing_def_forms
                if combined_sing:
                    inflection_lines.append(f"  {Colors.INFLECTION_LABEL}Singular:{Colors.END} {', '.join(combined_sing)}")
                # Remove these from further processing
                all_grouped.pop('Singular', None)
                all_grouped.pop('Singular Definite', None)
            
            if 'Plural' in all_grouped or 'Plural Definite' in all_grouped:
                plur_forms = sorted(list(all_grouped.get('Plural', set())))
                plur_def_forms = sorted(list(all_grouped.get('Plural Definite', set())))
                combined_plur = plur_forms + plur_def_forms
                if combined_plur:
                    inflection_lines.append(f"  {Colors.INFLECTION_LABEL}Plural:{Colors.END} {', '.join(combined_plur)}")
                # Remove these from further processing
                all_grouped.pop('Plural', None)
                all_grouped.pop('Plural Definite', None)
            
            # Define order for remaining categories
            category_order = ['Infinitive', 'Present', 'Past', 'Past Participle', 'Present Participle', 
                            'Basic', 'Neuter', 'Definite/Plural', 'Comparative', 'Superlative', 'Other']
            
            # Sort categories by defined order
            sorted_categories = []
            for cat in category_order:
                if cat in all_grouped:
                    sorted_categories.append(cat)
            
            # Add any remaining categories
            for cat in all_grouped:
                if cat not in sorted_categories:
                    sorted_categories.append(cat)
            
            for category in sorted_categories:
                forms = sorted(list(all_grouped[category]))
                
                # Filter out forms that are identical to the lemma (avoid redundancy)
                if lemma:
                    forms = [form for form in forms if form.lower() != lemma.lower()]
                
                # Only add category if it has remaining forms
                if forms:
                    forms_str = ', '.join(forms)
                    inflection_lines.append(f"  {Colors.INFLECTION_LABEL}{category}:{Colors.END} {forms_str}")
            
            # Join all parts with newlines for multiline mode
            if inflection_lines:
                header_line = f"  {Colors.BOLD}{header_text}:{Colors.END}"
                return header_line + "\n" + "\n".join(inflection_lines)
            
            return ""
        
        return ""
    except Exception as e:
        return ""


def format_result(conn, result, show_definitions=True, show_examples=True, max_examples=None, search_term="", show_expressions=False, only_examples=False, only_etymology=False, only_inflections=False):
    """Format a search result with proper structure and colors."""
    article_id, lemma, all_lemmas, word_class, gender, inflections, inflection_table, etymology, homonym_number = result
    
    output = []
    
    # Header with lemma and grammatical info
    highlighted_lemma = highlight_search_term(lemma, search_term)
    if homonym_number:
        highlighted_lemma = f"{highlighted_lemma} ({homonym_number})"
    header = f"{Colors.BOLD}{Colors.LEMMA}📖 {highlighted_lemma}{Colors.END}"
    if word_class:
        header += f" {format_word_class(word_class)}"
    if gender:
        header += f" ({format_gender(gender)})"
    
    # Add alternative forms to header line
    if all_lemmas and all_lemmas != lemma:
        other_lemmas = [l for l in all_lemmas.split(' | ') if l != lemma]
        if other_lemmas:
            highlighted_lemmas = [highlight_search_term(l, search_term) for l in other_lemmas]
            header += f" {Colors.INFO}Alternative forms: {Colors.END}{', '.join(highlighted_lemmas)}"
    
    output.append(header)
    
    # If only_examples is True, skip all other info and just show examples
    if only_examples:
        # Get examples from definitions
        cursor = conn.cursor()
        cursor.execute('''
            SELECT DISTINCT e.quote, e.explanation
            FROM examples e
            WHERE e.article_id = ? AND e.quote IS NOT NULL AND e.quote != ''
            ORDER BY e.id
        ''', (article_id,))
        
        examples = cursor.fetchall()
        if examples:
            example_texts = []
            for quote, explanation in examples:
                if quote:
                    highlighted_quote = highlight_search_term(quote, search_term, Colors.EXAMPLE)
                    example_text = highlighted_quote
                    if explanation:
                        example_text += f" ({explanation})"
                    example_texts.append(example_text)
            
            if example_texts:
                output.append(f"  {'; '.join(example_texts)}")
        
        # Get examples from related expressions (faste uttrykk)
        # Always include expressions for --only-examples mode
        expressions = get_related_expressions(conn, lemma)
        if expressions:
            expr_examples = []
            for expr_lemma, expr_data in expressions.items():
                # Include the expression name itself as an example
                clean_expr = expr_lemma.replace('[', '').replace(']', '').replace('|', '/')
                highlighted_expr = highlight_search_term(clean_expr, search_term, Colors.EXAMPLE)
                expr_examples.append(highlighted_expr)
                
                # Include any actual examples from the expression definitions
                for def_data in expr_data['definitions']:
                    for quote, explanation in def_data['examples']:
                        if quote:
                            highlighted_quote = highlight_search_term(quote, search_term, Colors.EXAMPLE)
                            example_text = highlighted_quote
                            if explanation:
                                example_text += f" ({explanation})"
                            expr_examples.append(example_text)
            
            if expr_examples:
                if examples:  # If we already have examples, add a separator
                    output.append(f"  {'; '.join(expr_examples)}")
                else:
                    output.append(f"  {'; '.join(expr_examples)}")
        
        return '\n'.join(output)
    
    # If only_etymology is True, skip all other info and just show etymology
    if only_etymology:
        if etymology:
            output.append(f"  {Colors.ETYMOLOGY}Etymology: {Colors.END}{etymology}")
        else:
            output.append(f"  {Colors.INFO}No etymology available{Colors.END}")
        return '\n'.join(output)
    
    # If only_inflections is True, skip all other info and just show inflections
    if only_inflections:
        if inflection_table:
            # Format inflections on separate lines for this mode
            inflection_output = format_inflection_table_multiline(inflection_table, word_class, lemma)
            if inflection_output:
                output.append(inflection_output)
            else:
                output.append(f"  {Colors.INFO}No inflections available{Colors.END}")
        else:
            output.append(f"  {Colors.INFO}No inflections available{Colors.END}")
        return '\n'.join(output)
    
    # Blank line after header (unless in special modes)
    if not (only_examples or only_etymology or only_inflections):
        output.append("")
    
    # Get definitions and examples
    definitions, examples_by_def = get_definitions_and_examples(conn, article_id)
    
    # Display definitions if requested
    if show_definitions:
        
        if definitions:
            pass
            
            # Find the minimum level (top level) for numbering
            min_level = min(d[3] for d in definitions) if definitions else 0
            definition_counter = 1
            
            for def_row_id, def_id, parent_id, level, content, order_num in definitions:
                # Indent based on level (adjust for minimum level)
                indent = "  " + "  " * (level - min_level)
                
                # Extract compound words from definition content
                main_def, compound_part = extract_compound_words(content)
                
                # Check if this is a standalone compound definition (no main definition)
                is_standalone_compound = (main_def == "" and compound_part)
                
                if is_standalone_compound and output:
                    # This is compound info that should be attached to the previous definition
                    # Just add the compound part without numbering, no extra blank line
                    output.append(f"{indent}    {compound_part}")
                    # Skip adding the blank line at the end for standalone compounds
                    continue
                else:
                    # Regular definition with numbering
                    if level == min_level:
                        bullet = f"{Colors.BOLD}{definition_counter}.{Colors.END}"
                        definition_counter += 1
                    else:
                        bullet = f"{Colors.YELLOW}•{Colors.END}"
                    
                    # Make main definition content bold but not colored
                    colored_content = f"{Colors.BOLD}{main_def}{Colors.END}"
                    
                    # Prepare examples for this definition if they exist
                    examples_text = ""
                    if show_examples and def_row_id in examples_by_def:
                        examples = examples_by_def[def_row_id]
                        if max_examples:
                            examples = examples[:max_examples]
                        
                        if examples:
                            example_texts = []
                            for quote, explanation in examples:
                                highlighted_quote = highlight_search_term(quote, search_term, Colors.EXAMPLE)
                                example_text = f'"{highlighted_quote}"'
                                if explanation:
                                    example_text += f" ({explanation})"
                                example_texts.append(example_text)
                            
                            # Join examples with semicolon and space
                            examples_text = f" {'; '.join(example_texts)}"
                            
                            if max_examples and len(examples_by_def[def_row_id]) > max_examples:
                                remaining = len(examples_by_def[def_row_id]) - max_examples
                                examples_text += f" {Colors.INFO}... and {remaining} more example(s){Colors.END}"
                    
                    # Combine definition and examples on same line
                    output.append(f"{indent}{bullet} {colored_content}{examples_text}")
                    
                    # Add compound words on separate line if present
                    if compound_part:
                        output.append(f"{indent}    {compound_part}")
    
    # If definitions weren't shown but examples should be, show them separately
    elif show_examples and examples_by_def:
        for def_row_id, examples in examples_by_def.items():
            if examples:
                example_texts = []
                for quote, explanation in examples:
                    highlighted_quote = highlight_search_term(quote, search_term, Colors.EXAMPLE)
                    example_text = f'"{highlighted_quote}"'
                    if explanation:
                        example_text += f" ({explanation})"
                    example_texts.append(example_text)
                
                examples_line = "; ".join(example_texts)
                output.append(f"  {examples_line}")
    
    # Etymology (after definitions)
    if search_config.show_etymology and etymology:
        output.append(f"  {Colors.ETYMOLOGY}Etymology: {Colors.END}{etymology}")
    
    # Inflection table (after etymology)
    if search_config.show_inflections:
        table_output = format_inflection_table(inflection_table, word_class, lemma)
        if table_output:
            output.append(table_output)
    
    # Fixed expressions (only for main entries, not for expressions themselves, and only if explicitly requested)
    if word_class != 'EXPR' and show_expressions:
        expressions = get_related_expressions(conn, lemma)
        if expressions:
            output.append(f"  {Colors.BOLD}Faste uttrykk:{Colors.END}")
            for expr_lemma, expr_data in expressions.items():
                # Clean up the expression lemma (remove brackets)
                clean_expr = expr_lemma.replace('[', '').replace(']', '').replace('|', '/')
                # Highlight search term in expression name
                highlighted_expr = highlight_search_term(clean_expr, search_term, Colors.BOLD)
                output.append(f"    • {highlighted_expr}")
                
                # Handle multiple definitions for the same expression
                for i, def_data in enumerate(expr_data['definitions']):
                    # Add definition if it's not just "Se: ..." or "Sjå: ..." AND show_definitions is True
                    if show_definitions and def_data['content'] and not (def_data['content'].startswith('Se:') or def_data['content'].startswith('Sjå:')):
                        # Highlight search term in definition
                        highlighted_def = highlight_search_term(def_data['content'], search_term, '')
                        # Number definitions if there are multiple
                        if len(expr_data['definitions']) > 1:
                            output.append(f"      {i+1}. {highlighted_def}")
                        else:
                            output.append(f"      {highlighted_def}")
                    
                    # Add examples in italics (cyan color to simulate italics) only if show_examples is True
                    if show_examples:
                        for quote, explanation in def_data['examples']:
                            if quote:
                                # Highlight search term in example quote
                                highlighted_quote = highlight_search_term(quote, search_term, Colors.EXAMPLE)
                                example_text = f"{highlighted_quote}"
                                if explanation:
                                    example_text += f" ({explanation})"
                                # Indent examples appropriately
                                if len(expr_data['definitions']) > 1:
                                    output.append(f"          {example_text}")
                                else:
                                    output.append(f"        {example_text}")
    
    return '\n'.join(output)


def run_test_searches(conn, args):
    """Run test searches with predefined words."""
    from .core import search_exact, search_prefix
    
    print(f"{Colors.BOLD}Running test searches...{Colors.END}")
    print(f"{Colors.INFO}{'=' * 80}{Colors.END}")
    
    for i, test_word in enumerate(TEST_WORDS):
        print(f"{Colors.HEADER}Test {i+1}: Searching for '{Colors.BOLD}{test_word}{Colors.END}{Colors.HEADER}'{Colors.END}")
        
        # Perform exact search (with fallback to prefix if no exact match)
        results = search_exact(conn, test_word)
        if not results:
            print(f"{Colors.WARNING}No exact matches found. Trying prefix search...{Colors.END}")
            results = search_prefix(conn, test_word)
        
        if results:
            
            # Show all results for test mode
            if args.only_examples:
                show_definitions = False
                show_examples = True
                only_examples = True
                only_etymology = False
                only_inflections = False
            elif args.only_etymology:
                show_definitions = False
                show_examples = False
                only_examples = False
                only_etymology = True
                only_inflections = False
            elif args.only_inflections:
                show_definitions = False
                show_examples = False
                only_examples = False
                only_etymology = False
                only_inflections = True
            else:
                show_definitions = not args.no_definitions
                show_examples = not args.no_examples
                only_examples = False
                only_etymology = False
                only_inflections = False
            
            for j, result in enumerate(results):
                show_expressions = (j == 0)  # Show expressions only for first exact match
                print(format_result(conn, result, show_definitions, show_examples, args.max_examples, test_word, show_expressions, only_examples, only_etymology, only_inflections))
                if j < len(results) - 1:
                    print(f"{Colors.INFO}{'-' * 80}{Colors.END}")
        else:
            print(f"{Colors.WARNING}No results found.{Colors.END}")
        
        if i < len(TEST_WORDS) - 1:
            print(f"{Colors.INFO}{'=' * 80}{Colors.END}")
    
    print(f"{Colors.BOLD}Test searches completed.{Colors.END}")


def display_statistics(conn):
    """Display comprehensive dictionary statistics."""
    cursor = conn.cursor()
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}📊 Dictionary Statistics{Colors.END}")
    print(f"{Colors.INFO}{'=' * 80}{Colors.END}\n")
    
    # Total entries
    cursor.execute("SELECT COUNT(*) FROM articles")
    total_entries = cursor.fetchone()[0]
    
    # Entries by word class
    cursor.execute("""
        SELECT word_class, COUNT(*) as count 
        FROM articles 
        WHERE word_class IS NOT NULL AND word_class != ''
        GROUP BY word_class 
        ORDER BY count DESC
    """)
    word_class_stats = cursor.fetchall()
    
    # Total words with identified type
    cursor.execute("SELECT COUNT(*) FROM articles WHERE word_class IS NOT NULL AND word_class != ''")
    words_with_type = cursor.fetchone()[0]
    
    # Gender statistics for nouns
    cursor.execute("""
        SELECT gender, COUNT(*) as count 
        FROM articles 
        WHERE word_class LIKE '%NOUN%' AND gender IS NOT NULL AND gender != ''
        GROUP BY gender
    """)
    gender_stats = cursor.fetchall()
    
    # Etymology statistics
    cursor.execute("SELECT COUNT(*) FROM articles WHERE etymology IS NOT NULL AND etymology != ''")
    with_etymology = cursor.fetchone()[0]
    
    # Inflection statistics
    cursor.execute("SELECT COUNT(*) FROM articles WHERE inflection_table IS NOT NULL AND inflection_table != '[]'")
    with_inflections = cursor.fetchone()[0]
    
    # Definition and example statistics
    cursor.execute("SELECT COUNT(DISTINCT article_id) FROM definitions")
    with_definitions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT article_id) FROM examples")
    with_examples = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM definitions")
    total_definitions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM examples")
    total_examples = cursor.fetchone()[0]
    
    # Expression statistics
    cursor.execute("SELECT COUNT(*) FROM articles WHERE word_class = 'EXPR'")
    expressions = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(DISTINCT target_lemma) FROM expression_links")
    words_with_expressions = cursor.fetchone()[0]
    
    # Display main statistics
    print(f"{Colors.BOLD}Total Entries:{Colors.END} {total_entries:,}")
    print(f"{Colors.BOLD}Total Definitions:{Colors.END} {total_definitions:,}")
    print(f"{Colors.BOLD}Total Examples:{Colors.END} {total_examples:,}")
    print(f"{Colors.BOLD}Total Expressions:{Colors.END} {expressions:,}\n")
    
    # Word type distribution
    print(f"{Colors.BOLD}{Colors.HEADER}Word Type Distribution{Colors.END}")
    print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
    print(f"Words with identified type: {words_with_type:,} ({words_with_type/total_entries*100:.1f}% of entries)\n")
    
    word_class_colors = {
        'NOUN': Colors.MASCULINE,
        'VERB': Colors.FEMININE,
        'ADJ': Colors.NEUTER,
        'ADV': Colors.YELLOW,
        'EXPR': Colors.PURPLE
    }
    
    for word_class, count in word_class_stats:
        percentage = count / total_entries * 100
        color = word_class_colors.get(word_class, Colors.INFO)
        bar_length = int(percentage / 2)  # Scale to max 50 chars
        bar = '█' * bar_length
        print(f"{color}{word_class:10}{Colors.END}: {count:6,} ({percentage:4.1f}%) {color}{bar}{Colors.END}")
    
    # Gender distribution for nouns
    noun_count = sum(count for wc, count in word_class_stats if 'NOUN' in wc)
    if noun_count > 0:
        print(f"\n{Colors.BOLD}{Colors.HEADER}Noun Gender Distribution{Colors.END}")
        print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
        
        gender_colors = {
            'Masc': Colors.MASCULINE,
            'Fem': Colors.FEMININE,
            'Neuter': Colors.NEUTER,
            'Fem | Masc': Colors.PURPLE,
            'Masc | Neuter': Colors.CYAN,
            'Fem | Masc | Neuter': Colors.YELLOW
        }
        
        # Sort gender stats in desired order
        gender_order = ['Masc', 'Fem | Masc', 'Neuter', 'Fem', 'Masc | Neuter', 'Fem | Masc | Neuter']
        sorted_gender_stats = []
        gender_dict = dict(gender_stats)
        
        for gender in gender_order:
            if gender in gender_dict:
                sorted_gender_stats.append((gender, gender_dict[gender]))
        
        # Add any remaining genders not in the predefined order
        for gender, count in gender_stats:
            if gender not in gender_order:
                sorted_gender_stats.append((gender, count))
        
        for gender, count in sorted_gender_stats:
            percentage = count / noun_count * 100
            color = gender_colors.get(gender, Colors.INFO)
            bar_length = int(percentage / 2)
            bar = '█' * bar_length
            print(f"{color}{gender:20}{Colors.END}: {count:6,} ({percentage:4.1f}%) {color}{bar}{Colors.END}")
    
    # Coverage statistics
    print(f"\n{Colors.BOLD}{Colors.HEADER}Coverage Analysis{Colors.END}")
    print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
    
    coverage_items = [
        ("With etymology", with_etymology, Colors.ETYMOLOGY),
        ("With inflections", with_inflections, Colors.CYAN),
        ("With definitions", with_definitions, Colors.GREEN),
        ("With examples", with_examples, Colors.EXAMPLE),
        ("Linked to expressions", words_with_expressions, Colors.PURPLE)
    ]
    
    for label, count, color in coverage_items:
        percentage = count / total_entries * 100
        bar_length = int(percentage / 2)
        bar = '▓' * bar_length
        print(f"{label:20}: {count:6,} ({percentage:4.1f}%) {color}{bar}{Colors.END}")
    
    # Word length distribution
    print(f"\n{Colors.BOLD}{Colors.HEADER}Word Length Distribution{Colors.END}")
    print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
    
    cursor.execute("""
        SELECT LENGTH(lemma) as len, COUNT(*) as count
        FROM articles
        GROUP BY LENGTH(lemma)
        ORDER BY LENGTH(lemma)
    """)
    
    length_stats = cursor.fetchall()
    max_count = max(count for _, count in length_stats)
    
    for length, count in length_stats:
        if length > 0 and length <= 20:  # Only show reasonable lengths
            percentage = count / total_entries * 100
            bar_length = int(count / max_count * 30)  # Scale to max 30 chars
            bar = '▓' * bar_length
            print(f"{length:2} chars: {count:6,} ({percentage:4.1f}%) {Colors.INFO}{bar}{Colors.END}")
    
    # Starting letter distribution
    print(f"\n{Colors.BOLD}{Colors.HEADER}Starting Letter Distribution (Excluding Expressions){Colors.END}")
    print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
    
    # Get lemmas excluding expressions and handle special characters
    cursor.execute("""
        SELECT lemma, COUNT(*) as count
        FROM articles
        WHERE lemma IS NOT NULL AND lemma != ''
        AND word_class != 'EXPR'  -- Exclude expressions
        GROUP BY lemma
    """)
    
    letter_counts = {}
    for (lemma, count) in cursor.fetchall():
        # Find the first actual letter (A-Z, Æ, Ø, Å), skipping -, ., [, etc.
        first_letter = None
        for char in lemma.upper():
            if char.isalpha():
                first_letter = char
                break
        
        if first_letter:
            if first_letter not in letter_counts:
                letter_counts[first_letter] = 0
            letter_counts[first_letter] += count
    
    # Sort by count descending
    letter_stats = sorted(letter_counts.items(), key=lambda x: x[1], reverse=True)
    
    # Calculate total non-expression entries for percentage calculation
    total_non_expr_entries = sum(letter_counts.values())
    
    for letter, count in letter_stats:
        percentage = count / total_non_expr_entries * 100
        bar_length = int(percentage)  # Scale to percentage
        bar = '■' * bar_length
        print(f"{Colors.BOLD}{letter}{Colors.END}: {count:6,} ({percentage:4.1f}%) {Colors.HEADER}{bar}{Colors.END}")
    
    # Top mentioned words in examples
    print(f"\n{Colors.BOLD}{Colors.HEADER}Top 200 Most Mentioned Words in Examples{Colors.END}")
    print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
    
    # Get all examples
    cursor.execute("""
        SELECT quote FROM examples 
        WHERE quote IS NOT NULL AND quote != ''
    """)
    
    word_counter = Counter()
    stop_words = {'det', 'som', 'for', 'med', 'til', 'fra', 'han', 'hun', 'den', 
                  'var', 'har', 'kan', 'vil', 'skal', 'ble', 'blir', 'ikke', 'men', 
                  'eller', 'også', 'jeg', 'meg', 'deg', 'seg', 'sin', 'sitt', 'sine',
                  'min', 'din', 'vår', 'deres', 'enn', 'når', 'hvor', 'hva', 'hvem',
                  'noe', 'noen', 'der', 'her', 'om', 'opp', 'ned', 'inn', 'mot'}
    
    for (quote,) in cursor.fetchall():
        # Extract words (letters only, convert to lowercase)
        words = re.findall(r'\b[a-zæøå]+\b', quote.lower())
        for word in words:
            if len(word) > 2 and word not in stop_words:
                word_counter[word] += 1
    
    top_words = word_counter.most_common(200)
    if top_words:
        max_word_count = top_words[0][1]
        for i, (word, count) in enumerate(top_words):
            bar_length = int(count / max_word_count * 20)
            bar = '▓' * bar_length
            print(f"{i+1:3}. {word:15}: {count:6,} {Colors.SUCCESS}{bar}{Colors.END}")
    
    # Homonym statistics
    cursor.execute("SELECT COUNT(*) FROM articles WHERE homonym_number > 1")
    homonyms = cursor.fetchone()[0]
    
    print(f"\n{Colors.BOLD}{Colors.HEADER}Additional Statistics{Colors.END}")
    print(f"{Colors.INFO}{'-' * 40}{Colors.END}")
    print(f"Homonyms (words with multiple entries): {homonyms:,}")
    
    # Average definitions and examples per word
    if with_definitions > 0:
        avg_definitions = total_definitions / with_definitions
        print(f"Average definitions per word: {avg_definitions:.1f}")
    
    if with_examples > 0:
        avg_examples = total_examples / with_examples
        print(f"Average examples per word: {avg_examples:.1f}")
    
    print(f"\n{Colors.INFO}{'=' * 80}{Colors.END}")