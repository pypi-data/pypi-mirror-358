"""Command-line interface for ordb."""

import argparse
import os
import sys
from . import __version__
from .config import Colors, search_config
from .core import (
    setup_database, parse_search_query, search_exact, search_fuzzy, 
    search_prefix, search_anywhere_term, search_fulltext, search_anywhere,
    search_expressions_only, search_all_examples, search_fuzzy_interactive,
    search_prefix_interactive, search_anywhere_term_interactive
)
from .pagination import paginate_output


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='ordb - Norwegian bokmål dictionary search tool',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=f'''\
{Colors.BOLD}Examples:{Colors.END}
  %(prog)s gå                   # Exact match for "gå" (fallback based on config)
  %(prog)s -f huse              # Interactive fuzzy match: press letter key for immediate selection
  %(prog)s -a "til fots"        # Search anywhere for "til fots"
  %(prog)s -x hus               # Search only expressions containing "hus"
  %(prog)s --only-examples hus  # Show only examples for "hus"
  %(prog)s -e hus               # Show only etymology for "hus"
  %(prog)s -i hus               # Show only inflections for "hus"
  %(prog)s --adj stor           # Find only adjectives matching "stor"
  %(prog)s --verb gå            # Find only verbs matching "gå"
  %(prog)s --noun hus           # Find only nouns matching "hus"
  %(prog)s --adv fort           # Find only adverbs matching "fort"
  %(prog)s -s                   # Show comprehensive dictionary statistics

{Colors.BOLD}Special Search Syntax:{Colors.END}
  %(prog)s ære@                 # Prefix: terms starting with "ære" (interactive lettered list)
  %(prog)s @ære                 # Anywhere in term: terms containing "ære" (interactive lettered list)
  %(prog)s @ære@                # Same as @ære
  %(prog)s %%nasjonal           # Full-text: search all content for "nasjonal"
  %(prog)s -l 10 ære@           # Override interactive mode: show 10 prefix results directly
  %(prog)s -P ære@              # Disable interactive lists and pagination

{Colors.BOLD}Character Replacement:{Colors.END}
  %(prog)s gaar                 # Automatically tries "gå" (aa→å replacement)
  %(prog)s hoer                 # Automatically tries "hør" (oe→ø replacement)
  %(prog)s laere                # Automatically tries "lære" (ae→æ replacement)
  Note: Character replacement can be turned off in the configuration file (use -c flag)

{Colors.BOLD}Configuration:{Colors.END}
  Colors, character replacement, and default limits can be customized.
  Use -c flag to launch configuration wizard.

{Colors.BOLD}Auto-fallback:{Colors.END}
  If no exact matches are found:
  - With fallback_to_fuzzy=True: Shows interactive fuzzy search list
  - With fallback_to_fuzzy=False: Tries prefix search (original behavior)
        '''
    )
    
    parser.add_argument('query', nargs='?', help='Search term')
    
    # Single-letter options (alphabetical, with -h shown first by argparse)
    parser.add_argument('-a', '--anywhere', action='store_true',
                       help='Search anywhere in definitions and examples')
    parser.add_argument('-c', '--config', action='store_true',
                       help='Launch interactive configuration wizard')
    parser.add_argument('-C', '--cat-config', action='store_true',
                       help='Display raw configuration file contents')
    parser.add_argument('-e', '--only-etymology', action='store_true',
                       help='Show only etymology for hits')
    parser.add_argument('-f', '--fuzzy', action='store_true', 
                       help='Interactive fuzzy search: shows lettered list of similar words')
    parser.add_argument('-i', '--only-inflections', action='store_true',
                       help='Show only inflections, with each category on separate line')
    parser.add_argument('-l', '--limit', type=int, default=None,
                       help=f'Maximum number of results to show (default: {search_config.default_limit}). When used, overrides interactive lists and shows all results up to limit.')
    parser.add_argument('-p', '--paginate', action='store_true',
                       help='Force pagination even when config pagination=False')
    parser.add_argument('-P', '--no-paginate', action='store_true',
                       help='Force pagination off and disable interactive lists')
    parser.add_argument('-r', nargs='?', const=1, type=int, metavar='N', dest='random_entries',
                       help='Get N random words with their definitions (default: 1)')
    parser.add_argument('-R', nargs='?', const=1, type=int, metavar='N', dest='random_words',
                       help='Get N random words only, one per line (default: 1)')
    parser.add_argument('-s', '--stats', action='store_true',
                       help='Show comprehensive dictionary statistics')
    parser.add_argument('-t', '--threshold', type=float, default=0.6,
                       help='Similarity threshold for fuzzy matching (0.0-1.0, default: 0.6)')
    parser.add_argument('-v', '--version', action='version', version=f'ordb {__version__}',
                       help='Show version information')
    parser.add_argument('-w', '--words-only', action='store_true',
                       help='Return only matching words as comma-separated list (no limit)')
    parser.add_argument('-W', action='store_true', dest='words_only_lines',
                       help='Return only matching words, one per line (no limit, no other text)')
    parser.add_argument('-x', '--expressions-only', action='store_true',
                       help='Search only expressions ([expr] word class)')
    
    # Long-only options (alphabetical)
    parser.add_argument('--adj', action='store_true',
                       help='Return only hits of word type [adj]')
    parser.add_argument('--adv', action='store_true',
                       help='Return only hits of word type [adv]')
    parser.add_argument('--all-examples', action='store_true',
                       help='Find exact matches of target word in all examples across dictionary')
    from .config import get_data_dir
    default_db_path = str(get_data_dir() / 'articles.db')
    parser.add_argument('--db', default=default_db_path,
                       help=f'Database file path (default: {default_db_path})')
    parser.add_argument('--max-examples', type=int, default=None,
                       help='Maximum examples per definition (default: show all)')
    parser.add_argument('--no-definitions', action='store_true',
                       help='Hide definitions in output')
    parser.add_argument('--no-examples', action='store_true',
                       help='Hide examples in output')
    parser.add_argument('--noun', action='store_true',
                       help='Return only hits of word type [noun]')
    parser.add_argument('--only-examples', action='store_true',
                       help='Show only examples (including faste uttrykk examples)')
    parser.add_argument('--test', action='store_true',
                       help='Run test searches with predefined words')
    parser.add_argument('--verb', action='store_true',
                       help='Return only hits of word type [verb]')
    
    args = parser.parse_args()
    
    # Ensure config file exists - create default if none found
    try:
        from .config import get_config_path
        config_path = get_config_path()
        if not config_path or not os.path.exists(config_path):
            # Silently create default config file
            from .wizard import save_config
            import configparser
            config = configparser.ConfigParser()
            config.add_section('colors')
            config.add_section('search')
            save_config(config)
    except Exception as e:
        # If config creation fails, continue with defaults but warn user
        print(f"{Colors.WARNING}Warning: Could not create configuration file: {e}{Colors.END}")
    
    # Handle config wizard
    if args.config:
        try:
            from .wizard import run_config_wizard
            run_config_wizard()
            return
        except Exception as e:
            print(f"{Colors.ERROR}Error launching configuration wizard: {e}{Colors.END}")
            sys.exit(1)
    
    # Handle cat config
    if args.cat_config:
        try:
            from .config import get_config_path
            config_path = get_config_path()
            if config_path and os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    print(f.read())
            else:
                print(f"{Colors.WARNING}No configuration file found, creating new default configuration file.{Colors.END}")
                # Create default config file
                from .wizard import save_config
                import configparser
                config = configparser.ConfigParser()
                config.add_section('colors')
                config.add_section('search')
                save_config(config)
                
                # Now read and display the newly created config
                config_path = get_config_path()
                if config_path and os.path.exists(config_path):
                    with open(config_path, 'r') as f:
                        print(f.read())
                else:
                    print(f"{Colors.ERROR}Failed to create configuration file.{Colors.END}")
            return
        except Exception as e:
            print(f"{Colors.ERROR}Error reading configuration file: {e}{Colors.END}")
            sys.exit(1)
    
    # Validate arguments
    if not args.test and not args.query and not args.stats and not args.random_entries and not args.random_words:
        print(f"{Colors.ERROR}Error: Either provide a search term, use --test flag, --stats flag, --config flag, or -r/-R flag{Colors.END}")
        sys.exit(1)
    
    if not 0.0 <= args.threshold <= 1.0:
        print(f"{Colors.ERROR}Error: Threshold must be between 0.0 and 1.0{Colors.END}")
        sys.exit(1)
    
    # Adjust limit when pagination is enabled and user didn't specify custom limit
    if (search_config.pagination or args.paginate) and args.limit == search_config.default_limit:
        # Use limit_with_pagination, with 0 meaning no limit (set to very large number)
        if search_config.limit_with_pagination == 0:
            args.limit = 999999  # Effectively no limit
        else:
            args.limit = search_config.limit_with_pagination
    
    # Connect to database
    conn = setup_database(args.db)
    if conn is None:
        print(f"{Colors.ERROR}Failed to setup database. Exiting.{Colors.END}")
        sys.exit(1)
    
    # Handle test mode
    if args.test:
        from .display import run_test_searches
        run_test_searches(conn, args)
        return
    
    # Handle statistics mode
    if args.stats:
        from .display import display_statistics
        display_statistics(conn)
        conn.close()
        return
    
    # Handle random entries
    if args.random_entries or args.random_words:
        from .core import get_random_entries
        
        count = args.random_entries if args.random_entries else args.random_words
        results = get_random_entries(conn, count, include_expr=False)
        
        if args.random_words:
            # Just print the words, one per line
            for result in results:
                print(result[1])  # lemma
        else:
            # Display full entries
            from .display import format_result
            
            # Collect output for pagination
            output_parts = []
            
            if count > 1:
                output_parts.append(f"{Colors.HEADER}🎲 {count} random dictionary entries:{Colors.END}")
            else:
                output_parts.append(f"{Colors.HEADER}🎲 Random dictionary entry:{Colors.END}")
            
            # Format results with all the display flags
            show_definitions = not args.no_definitions
            show_examples = not args.no_examples
            only_examples = args.only_examples
            only_etymology = args.only_etymology
            only_inflections = args.only_inflections
            
            for i, result in enumerate(results):
                show_expressions = (i == 0)  # Show expressions only for first result
                result_output = format_result(conn, result, show_definitions, show_examples, 
                                            args.max_examples, '', show_expressions, 
                                            only_examples, only_etymology, only_inflections)
                output_parts.append(result_output)
                if i < len(results) - 1:
                    output_parts.append(f"{Colors.INFO}{'-' * 80}{Colors.END}")
            
            # Join and paginate
            full_output = '\n'.join(output_parts)
            paginate_output(full_output, force_pagination=args.paginate, disable_pagination=args.no_paginate)
        
        conn.close()
        return
    
    try:
        # Parse search query for special syntax
        search_type, clean_query, original_query = parse_search_query(args.query)
        
        # Override with command line flags if present
        if args.all_examples:
            # Special case: search all examples across dictionary
            print(f"{Colors.HEADER}🔍 Searching all examples for exact matches of '{Colors.BOLD}{args.query}{Colors.END}{Colors.HEADER}'{Colors.END}")
            examples = search_all_examples(conn, args.query)
            
            if not examples:
                print(f"{Colors.WARNING}No examples found containing '{args.query}'.{Colors.END}")
                return
            
            # Collect all output for pagination
            output_parts = []
            output_parts.append(f"\n{Colors.BOLD}Found {len(examples)} example(s) containing '{args.query}':{Colors.END}")
            output_parts.append(f"{Colors.INFO}{'=' * 80}{Colors.END}")
            
            # Display examples in semicolon-separated format
            example_texts = []
            # Handle None limit case - use default limit from config
            limit_to_use = args.limit if args.limit is not None else search_config.default_limit
            for quote, explanation, lemma, word_class in examples[:limit_to_use]:
                from .display import highlight_search_term
                highlighted_quote = highlight_search_term(quote, args.query, Colors.EXAMPLE)
                example_text = highlighted_quote
                if explanation:
                    example_text += f" ({explanation})"
                example_texts.append(example_text)
            
            if example_texts:
                output_parts.append(f"  {'; '.join(example_texts)}")
            
            if len(examples) > limit_to_use:
                output_parts.append(f"{Colors.INFO}... and {len(examples) - limit_to_use} more example(s){Colors.END}")
                output_parts.append(f"{Colors.INFO}Use --limit {len(examples)} to see all examples{Colors.END}")
            
            # Join all output and paginate
            full_output = '\n'.join(output_parts)
            paginate_output(full_output, force_pagination=args.paginate, disable_pagination=args.no_paginate)
            
            return
        elif args.expressions_only:
            search_type = 'expressions_only'
            clean_query = args.query
        elif args.fuzzy:
            search_type = 'fuzzy'
            clean_query = args.query
        elif args.anywhere:
            search_type = 'anywhere'
            clean_query = args.query
        
        # Check if user provided explicit limit or --no-paginate or words-only (override interactive mode)
        limit_overrides_interactive = args.limit is not None or args.no_paginate or args.words_only or args.words_only_lines
        
        # Set the actual limit value to use
        if args.limit is None:
            args.limit = search_config.default_limit
        
        # Perform search based on type
        if search_type == 'expressions_only':
            results = search_expressions_only(conn, clean_query)
        elif search_type == 'fuzzy':
            if limit_overrides_interactive:
                # Use non-interactive fuzzy search when limit is specified
                results = search_fuzzy(conn, clean_query, args.threshold, include_expr=False)
            else:
                # Use interactive fuzzy search
                result = search_fuzzy_interactive(conn, clean_query, args.threshold, include_expr=False)
                if result == 'CANCELLED':
                    return  # User cancelled, exit silently
                elif result:
                    results = [result]
                else:
                    results = []
        elif search_type == 'anywhere':
            results = search_anywhere(conn, clean_query, include_expr=False)
        elif search_type == 'prefix':
            if limit_overrides_interactive or not search_config.interactive_anywhere_search:
                # Use non-interactive prefix search when limit specified or interactive disabled
                results = search_prefix(conn, clean_query, include_expr=False)
            else:
                # Use interactive prefix search
                result = search_prefix_interactive(conn, clean_query, include_expr=False)
                if result == 'CANCELLED':
                    return  # User cancelled, exit silently
                elif result:
                    results = [result]
                else:
                    results = []
        elif search_type == 'anywhere_term':
            if limit_overrides_interactive or not search_config.interactive_anywhere_search:
                # Use non-interactive anywhere term search when limit specified or interactive disabled
                results = search_anywhere_term(conn, clean_query, include_expr=False)
            else:
                # Use interactive anywhere term search
                result = search_anywhere_term_interactive(conn, clean_query, include_expr=False)
                if result == 'CANCELLED':
                    return  # User cancelled, exit silently
                elif result:
                    results = [result]
                else:
                    results = []
        elif search_type == 'fulltext':
            results = search_fulltext(conn, clean_query, include_expr=False)
        else:
            results = search_exact(conn, clean_query, include_expr=True)
            
            # If no exact matches found, fallback based on config
            if not results and search_type == 'exact':
                if search_config.fallback_to_fuzzy and not limit_overrides_interactive:
                    # Use interactive fuzzy search as fallback (unless limit overrides)
                    print(f"{Colors.WARNING}No exact matches found. Trying fuzzy search...{Colors.END}")
                    print()
                    result = search_fuzzy_interactive(conn, clean_query, 0.6, include_expr=True)
                    if result == 'CANCELLED':
                        return  # User cancelled, exit silently
                    elif result:
                        results = [result]
                elif search_config.fallback_to_fuzzy and limit_overrides_interactive:
                    # Use non-interactive fuzzy search when limit is specified
                    print(f"{Colors.WARNING}No exact matches found. Trying fuzzy search...{Colors.END}")
                    print()
                    results = search_fuzzy(conn, clean_query, 0.6, include_expr=True)
                else:
                    # Original behavior: fallback to prefix search
                    results = search_prefix(conn, clean_query, include_expr=True)
        
        # Apply word class filtering if specified before displaying count
        if args.adj:
            results = [result for result in results if result[3] and 'ADJ' in result[3]]
        elif args.verb:
            results = [result for result in results if result[3] and 'VERB' in result[3]]
        elif args.noun:
            results = [result for result in results if result[3] and 'NOUN' in result[3]]
        elif args.adv:
            results = [result for result in results if result[3] and 'ADV' in result[3]]
        
        # Display results
        if not results:
            if not (args.words_only or args.words_only_lines):
                print(f"{Colors.WARNING}No results found.{Colors.END}")
            return
        
        # Handle words-only output
        if args.words_only or args.words_only_lines:
            # Extract unique lemmas from results (no limit)
            unique_words = []
            seen_words = set()
            for result in results:
                lemma = result[1]
                if lemma not in seen_words:
                    unique_words.append(lemma)
                    seen_words.add(lemma)
            
            if args.words_only:
                # Comma-separated output
                print(', '.join(unique_words))
            else:  # args.words_only_lines
                # One word per line
                for word in unique_words:
                    print(word)
            return
        
        # Display results using the display module
        from .display import format_result
        
        # Handle display flags
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
        
        # Collect all output for pagination
        output_parts = []
        
        # Add search header
        if search_type == 'expressions_only':
            output_parts.append(f"{Colors.HEADER}🔍 Expression search for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (expressions only){Colors.END}")
        elif search_type == 'fuzzy' and results:
            # Don't show header for fuzzy search - already shown in interactive mode
            pass
        elif search_type == 'anywhere':
            output_parts.append(f"{Colors.HEADER}🔍 Searching anywhere for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}'{Colors.END}")
        elif search_type == 'prefix':
            output_parts.append(f"{Colors.HEADER}🔍 Prefix search for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}@' (terms starting with '{clean_query}'){Colors.END}")
        elif search_type == 'anywhere_term':
            output_parts.append(f"{Colors.HEADER}🔍 Term search for '@{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (terms containing '{clean_query}'){Colors.END}")
        elif search_type == 'fulltext':
            output_parts.append(f"{Colors.HEADER}🔍 Full-text search for '%{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}' (all content){Colors.END}")
        else:
            output_parts.append(f"{Colors.HEADER}🔍 Exact search for '{Colors.BOLD}{clean_query}{Colors.END}{Colors.HEADER}'{Colors.END}")
        
        # Format results
        for i, result in enumerate(results[:args.limit]):
            show_expressions = (i == 0)  # Show expressions only for first result
            result_output = format_result(conn, result, show_definitions, show_examples, args.max_examples, clean_query, show_expressions, only_examples, only_etymology, only_inflections)
            output_parts.append(result_output)
            if i < min(len(results), args.limit) - 1:
                output_parts.append(f"{Colors.INFO}{'-' * 80}{Colors.END}")
        
        # Add result count if more than 1 result
        if len(results) > 1:
            if len(results) > args.limit:
                output_parts.append(f"{Colors.INFO}Found {len(results)} results (showing {args.limit}). Use --limit {len(results)} to see all.{Colors.END}")
            else:
                output_parts.append(f"{Colors.INFO}Found {len(results)} results.{Colors.END}")
        
        # Join all output and paginate
        full_output = '\n'.join(output_parts)
        paginate_output(full_output, force_pagination=args.paginate, disable_pagination=args.no_paginate)
    
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Search interrupted.{Colors.END}")
    except Exception as e:
        print(f"{Colors.ERROR}Error: {e}{Colors.END}")
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()