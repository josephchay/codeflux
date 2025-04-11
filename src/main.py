import os
import argparse
import sys
import datetime

from constants import (
    DEFAULT_EXCLUDE_DIRS, ALL_EXCLUDE_EXTENSIONS, ALL_EXCLUDE_FILENAMES,
    DEFAULT_FLATTEN_OUTPUT_PATH, DEFAULT_DEFLATTEN_OUTPUT_PATH, DEFAULT_BUNDLE_OUTPUT_PATH,
    DEFAULT_MINIFY_OUTPUT_PATH, DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH,
    OPERATION_FLATTEN, OPERATION_DEFLATTEN, OPERATION_BUNDLE, OPERATION_MINIFY, OPERATION_MINIFY_BUNDLE,
    OPERATION_SEARCH, MINIFICATION_DESCRIPTION
)
from handlers import HANDLERS, FileExtHandler
from search import Searcher
from ui.table import get_table_formatter
from utils import merge_with_defaults, merge_stats, mkdir_output, format_path, get_relative_path


def make_parser():
    parser = argparse.ArgumentParser(description="A plugin that gives you full control and deep insight into any project's codebase structure.")

    src_group = parser.add_argument_group('source')
    src_group.add_argument(
        "src_pos",
        nargs="?",
        help="Source directory path (positional, default: current directory)"
    )
    src_group.add_argument(
        "--src", "-s",
        dest="src_named",
        help="Source directory path (named)"
    )

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument(
        "dest_pos",
        nargs="?",
        help="Destination directory or file path (positional, defaults based on operation)"
    )
    dest_group.add_argument(
        "--dest", "-d",
        dest="dest_named",
        help="Destination directory or file path (named)"
    )

    operation_group = parser.add_argument_group('operations')
    operation_group.add_argument(
        "--flatten", "-f",
        action="store_true",
        help="Flatten the directory structure (default: True if no other operation specified)"
    )
    operation_group.add_argument(
        "--no-filetype-dirs", "-nfd",
        action="store_true",
        help="When flattening, place all files directly in the output directory without filetype subdirectories"
    )
    operation_group.add_argument(
        "--deflatten", "-df",
        action="store_true",
        help="Deflatten the directory - restore original structure (default: True if no other operation specified)"
    )
    operation_group.add_argument(
        "--minify", "-m",
        action="store_true",
        help="Create a minified copy of the directory while preserving structure (default: True if no other operation specified)"
    )
    operation_group.add_argument(
        "--bundle", "-b",
        action="store_true",
        help="Bundle files into a single document file (default: True if no other operation specified)"
    )
    operation_group.add_argument(
        "--minify-bundle", "-mb",
        action="store_true",
        help="Minify files and bundle them into a single document file (default: True if no other operation specified)"
    )

    parser.add_argument(
        "--file-types", "-t",
        nargs="+",
        choices=["py", "ipynb", "jsts", "html", "css", "php", "ruby", "swift", "kotlin", "java", "csharp", "shell",
                 "mdtxt", "yml", "json", "go", "ini", "db", "bat", "scp"],
        default=["py", "ipynb", "jsts", "html", "css", "php", "ruby", "swift", "kotlin", "java", "csharp", "shell",
                 "mdtxt", "yml", "json", "go", "ini", "db", "bat", "scp"],
        help="File types to process (default: all)"
    )

    exclusion_group = parser.add_argument_group('exclusion options')
    exclusion_group.add_argument(
        "--exclude-dirs", "-xd",
        nargs="+",
        help="Directory names to exclude"
    )
    exclusion_group.add_argument(
        "--exclude-extensions", "-xe",
        nargs="+",
        help="File extensions to exclude"
    )
    exclusion_group.add_argument(
        "--exclude-files", "-xf",
        nargs="+",
        help="Specific file paths to exclude (requires full path relative to source dir, e.g. 'path/to/file.py')"
    )

    inclusion_group = parser.add_argument_group('inclusion options')
    inclusion_group.add_argument(
        "--include-dirs", "-id",
        nargs="+",
        help="Directory names to include (only these will be processed)"
    )
    inclusion_group.add_argument(
        "--include-extensions", "-ie",
        nargs="+",
        help="File extensions to include (only these will be processed)"
    )
    inclusion_group.add_argument(
        "--include-files", "-if",
        nargs="+",
        help="Specific filenames to include (only these will be processed)"
    )

    defaults_group = parser.add_argument_group('defaults handling')
    defaults_group.add_argument(
        "--ignore-defaults", "-i",
        action="store_true",
        help="Ignore all default exclusion lists and only use the provided options"
    )

    search_group = parser.add_argument_group('search operations')
    search_group.add_argument(
        "--search-ext", "-se",
        nargs="+",
        help="Search for files with specific extensions"
    )
    search_group.add_argument(
        "--search-pattern", "-sp",
        help="Search for files containing a specific regex pattern"
    )
    search_group.add_argument(
        "--search-size", "-ss",
        nargs=2,
        metavar=('MIN_KB', 'MAX_KB'),
        help="Search for files within a size range (in KB, use 'none' for no limit)"
    )
    search_group.add_argument(
        "--search-date", "-sd",
        nargs='+',
        metavar=('START_DATE', 'END_DATE'),
        help="Search for files modified between dates (YYYY-MM-DD format, end date optional)"
    )
    search_group.add_argument(
        "--search-imports", "-si",
        help="Find files that import a specific module"
    )
    search_group.add_argument(
        "--search-duplicates", "-sdu",
        nargs='?',
        const=5,
        type=int,
        metavar='MIN_LINES',
        help="Find duplicate code blocks (optional: minimum lines, default 5)"
    )

    snippet_group = parser.add_argument_group('snippet options (for bundle and minify-bundle operations)')
    snippet_group.add_argument(
        "--snippet", "-sn",
        action="store_true",
        help="Enable snippet mode for bundling operations (only includes a portion of each file)"
    )
    snippet_group.add_argument(
        "--snippet-lines", "-snl",
        type=int,
        default=50,
        help="Maximum number of lines to include per file in snippet mode (default: 50)"
    )
    snippet_group.add_argument(
        "--snippet-start", "-sns",
        choices=["top", "middle", "bottom"],
        default="top",
        help="Where to take the snippet from: top, middle, or bottom of the file (default: top)"
    )
    snippet_group.add_argument(
        "--snippet-context", "-snc",
        type=int,
        default=5,
        help="Number of context lines to include around matches when using with search-pattern (default: 5)"
    )

    parser.add_argument(
        "--clear-dest-dir", "-c",
        action="store_true",
        help="Clear the destination directory before copying (default: False)"
    )
    parser.add_argument(
        '--no-log', "-nl",
        action='store_true',
        help="Suppress all output logs."
    )

    parser.add_argument(
        '--continue-on-error', "-coe",
        action='store_true',
        help="Continue processing when minification errors occur (using original content for failed files)"
    )

    return parser


def main():
    args = make_parser().parse_args()

    source_dir = args.src_named if args.src_named else args.src_pos
    if not source_dir:
        source_dir = os.getcwd()
    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory")
        return 1

    base_dir, _ = mkdir_output()
    timestamp_dir, _ = mkdir_output("multiple")

    if not args.no_log:
        # print(f"Base output directory: {base_dir}")
        print(f"Source directory (absolute): {os.path.abspath(source_dir)}")
        print(f"Destination directory (absolute): {timestamp_dir}")
        if not get_table_formatter()[1]:
            print("Notice: 'tabulate' module is not available. Reverting to default output formatting.")

    operations = []
    if args.flatten:
        operations.append(OPERATION_FLATTEN)
    if args.deflatten:
        operations.append(OPERATION_DEFLATTEN)
    if args.minify:
        operations.append(OPERATION_MINIFY)
    if args.bundle:
        operations.append(OPERATION_BUNDLE)
    if args.minify_bundle:
        operations.append(OPERATION_MINIFY_BUNDLE)
    if args.search_ext or args.search_pattern or args.search_size:
        operations.append(OPERATION_SEARCH)
    if not operations:
        operations = [OPERATION_FLATTEN, OPERATION_DEFLATTEN, OPERATION_MINIFY, OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE]

    output_paths = {}
    exclude_dirs = merge_with_defaults(args.exclude_dirs, DEFAULT_EXCLUDE_DIRS, args.ignore_defaults)
    exclude_exts = merge_with_defaults(args.exclude_extensions, ALL_EXCLUDE_EXTENSIONS, args.ignore_defaults)
    exclude_files = merge_with_defaults(args.exclude_files, ALL_EXCLUDE_FILENAMES, args.ignore_defaults)
    if exclude_files:
        exclude_files = [path.replace('\\', '/') for path in exclude_files]
    try:
        for operation in operations:
            handler_results = []
            if operation == OPERATION_FLATTEN:
                flatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not flatten_dest:
                    flatten_dest = os.path.join(timestamp_dir, DEFAULT_FLATTEN_OUTPUT_PATH)
                output_paths[operation] = flatten_dest

                if not args.no_log:
                    print("\n\n:::::::::::::::::::::::::::::: EXECUTING FLATTEN ::::::::::::::::::::::::::::::")
                    print(f"Destination: {get_relative_path(flatten_dest)}\n")

                for file_type in args.file_types:
                    if file_type in HANDLERS:
                        handler = HANDLERS[file_type]

                        if args.no_filetype_dirs:
                            file_dest_dir = flatten_dest
                        else:
                            file_dest_dir = os.path.join(flatten_dest, file_type)

                        if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                            continue

                        if not args.no_log:
                            print(f"----- {file_type.upper()} FILES -----")

                        stats = handler.flatten_dir(
                            source_dir, file_dest_dir, exclude_dirs, exclude_exts, exclude_files,
                            args.include_dirs, args.include_extensions, args.include_files,
                            args.clear_dest_dir, args.no_log
                        )
                        handler_results.append(stats)

                        # Clean up empty directories
                        if stats["files_copied"] == 0 and os.path.exists(file_dest_dir) and not os.listdir(file_dest_dir):
                            try:
                                os.rmdir(file_dest_dir)
                                if not args.no_log:
                                    print(f"Removed empty directory: {get_relative_path(file_dest_dir)}")
                            except OSError:
                                pass
                        if not args.no_log:
                            print("--------------------\n")

                merged_stats = merge_stats(handler_results)
                if not args.no_log:
                    if handler_results:
                        if merged_stats["files_copied"] > 0:
                            print("----- OVERALL SUMMARY -----")
                            print(f"Total files flattened: {merged_stats['files_copied']}")
                            print(f"Total data processed: {merged_stats['bytes_copied'] / 1024:.2f} KB")
                        else:
                            print("----- OVERALL SUMMARY -----")
                            print(f"No files were flattened.")
                    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

            elif operation == OPERATION_DEFLATTEN:
                deflatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not deflatten_dest:
                    deflatten_dest = os.path.join(timestamp_dir, DEFAULT_DEFLATTEN_OUTPUT_PATH)
                output_paths[operation] = deflatten_dest

                if not args.no_log:
                    print("\n\n:::::::::::::::::::::::::::::: EXECUTING DEFLATTEN ::::::::::::::::::::::::::::::")
                    print(f"Destination: {get_relative_path(deflatten_dest, timestamp_dir)}\n")

                # Check if there are any files to process
                has_files_to_process = False
                for file_type in args.file_types:
                    if file_type in HANDLERS:
                        file_source_dir = os.path.join(source_dir, file_type)
                        if os.path.exists(file_source_dir) and os.listdir(file_source_dir):
                            has_files_to_process = True
                            break

                if not has_files_to_process and not args.no_log:
                    print("No files found to deflatten.")
                    print("No operations performed.")

                else:
                    if not args.no_log:
                        print(f"Destination: {get_relative_path(deflatten_dest)}\n")

                    for file_type in args.file_types:
                        if file_type in HANDLERS:
                            handler = HANDLERS[file_type]
                            file_source_dir = os.path.join(source_dir, file_type)

                            if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                                continue

                            if os.path.exists(file_source_dir) and os.listdir(file_source_dir):
                                if not args.no_log:
                                    print(f"---------- {file_type.upper()} FILES ----------")

                                stats = handler.deflatten_dir(
                                    file_source_dir, deflatten_dest, exclude_files,
                                    args.include_dirs, args.include_extensions, args.include_files,
                                    args.clear_dest_dir, args.no_log
                                )

                                handler_results.append(stats)

                                if not args.no_log:
                                    print("--------------------\n")

                merged_stats = merge_stats(handler_results)
                if not args.no_log:
                    if handler_results:
                        if merged_stats["files_copied"] > 0:
                            print("----- OVERALL SUMMARY -----")
                            print(f"Total files deflattened: {merged_stats['files_copied']}")
                            print(f"Total directories created: {merged_stats['dirs_created']}")
                            print(f"Total data processed: {merged_stats['bytes_copied'] / 1024:.2f} KB")
                        else:
                            print("----- OVERALL SUMMARY -----")
                            print(f"No files were deflattened.")
                    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

            elif operation in [OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE]:
                bundle_dest = args.dest_named if args.dest_named else args.dest_pos
                if not bundle_dest:
                    if operation == OPERATION_BUNDLE:
                        bundle_dest = os.path.join(timestamp_dir, DEFAULT_BUNDLE_OUTPUT_PATH)
                    else:  # OPERATION_MINIFY_BUNDLE
                        bundle_dest = os.path.join(timestamp_dir, DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH)
                output_paths[operation] = bundle_dest

                if not args.no_log:
                    if operation == OPERATION_BUNDLE:
                        print("\n\n:::::::::::::::::::::::::::::: EXECUTING BUNDLE ::::::::::::::::::::::::::::::")
                        print(f"Destination: {get_relative_path(bundle_dest, timestamp_dir)}\n")
                    else:
                        print("\n\n:::::::::::::::::::::::::::::: EXECUTING MINIFY-BUNDLE ::::::::::::::::::::::::::::::")
                        print(f"Destination: {get_relative_path(bundle_dest, timestamp_dir)}")
                        print(f"Minification: {MINIFICATION_DESCRIPTION}")
                        if args.continue_on_error:
                            print("Note: Continuing on minification errors (--continue-on-error flag is set)")
                        print()

                # Create a combined bundle of all file types
                if args.file_types and HANDLERS:
                    combined_extensions = []
                    for file_type in args.file_types:
                        if file_type in HANDLERS:
                            combined_extensions.extend(HANDLERS[file_type].extensions)
                    combined_handler = FileExtHandler(extensions=combined_extensions, exclude_dirs=DEFAULT_EXCLUDE_DIRS,
                                                      exclude_extensions=ALL_EXCLUDE_EXTENSIONS,
                                                      exclude_filenames=ALL_EXCLUDE_FILENAMES)
                    stats = combined_handler.bundle_files(
                        source_dir, bundle_dest, exclude_dirs, exclude_exts, exclude_files,
                        args.include_dirs, args.include_extensions, args.include_files,
                        args.no_log, operation == OPERATION_MINIFY_BUNDLE,
                        args.snippet, args.snippet_lines, args.snippet_start, args.snippet_context,
                        args.search_pattern if hasattr(args, 'search_pattern') else None,
                        args.continue_on_error if hasattr(args, 'continue_on_error') else False
                    )
                    handler_results.append(stats)

                if not args.no_log:
                    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

            elif operation == OPERATION_MINIFY:
                minify_dest = args.dest_named if args.dest_named else args.dest_pos
                if not minify_dest:
                    minify_dest = os.path.join(timestamp_dir, DEFAULT_MINIFY_OUTPUT_PATH)
                output_paths[operation] = minify_dest

                if not args.no_log:
                    print("\n\n:::::::::::::::::::::::::::::: EXECUTING MINIFY ::::::::::::::::::::::::::::::")
                    print(f"Destination: {get_relative_path(minify_dest, timestamp_dir)}")
                    print(f"Minification: ({MINIFICATION_DESCRIPTION})")
                    if args.continue_on_error:
                        print("Note: Continuing on minification errors (--continue-on-error flag is set)")
                    print()

                processed_files = set()
                file_type_map = {}
                if args.include_files:
                    for include_file in args.include_files:
                        file_ext = os.path.splitext(include_file)[1].lower()
                        matched_handler = None
                        for handler_type, handler in HANDLERS.items():
                            if any(file_ext == ext.lower() for ext in handler.extensions):
                                if handler_type not in file_type_map:
                                    file_type_map[handler_type] = []
                                file_type_map[handler_type].append(include_file)
                                break

                for file_type in args.file_types:
                    if file_type in HANDLERS:
                        handler = HANDLERS[file_type]

                        if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                            continue
                        if args.include_files and file_type not in file_type_map:
                            continue

                        if not args.no_log:
                            print(f"----- {file_type.upper()} FILES -----")

                        handler_include_files = file_type_map.get(file_type, []) if args.include_files else args.include_files
                        stats = handler.minify_dir(
                            source_dir, minify_dest, exclude_dirs, exclude_exts, exclude_files,
                            args.include_dirs, args.include_extensions, handler_include_files,
                            args.clear_dest_dir, args.no_log, args.continue_on_error
                        )
                        handler_results.append(stats)

                        # Clean up empty directories
                        type_dir = os.path.join(minify_dest, file_type)
                        if stats["files_copied"] == 0 and os.path.exists(type_dir) and not os.listdir(type_dir):
                            try:
                                os.rmdir(type_dir)
                                if not args.no_log:
                                    print(f"Removed empty directory: {get_relative_path(type_dir)}")
                            except OSError:
                                pass
                        if not args.no_log:
                            print("--------------------\n")

                merged_stats = merge_stats(handler_results)
                if not args.no_log:
                    if handler_results:
                        if merged_stats["files_copied"] > 0:
                            print("----- OVERALL SUMMARY -----")
                            print(f"Total files minified: {merged_stats['files_minified']}")
                            print(f"Total files processed: {merged_stats['files_copied']}")
                            if merged_stats["bytes_original"] > 0 and merged_stats["bytes_minified"] > 0:
                                orig_kb = merged_stats["bytes_original"] / 1024
                                mini_kb = merged_stats["bytes_minified"] / 1024
                                reduction = (1 - merged_stats["bytes_minified"] / max(merged_stats["bytes_original"], 1)) * 100
                                print(f"Original size: {orig_kb:.2f} KB")
                                print(f"Minified size: {mini_kb:.2f} KB")
                                print(f"Overall reduction: {reduction:.2f}%")
                        else:
                            print("----- OVERALL SUMMARY -----")
                            print(f"No files were minified.")
                    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

            elif operation == OPERATION_SEARCH:
                if not args.no_log:
                    print("\n\n:::::::::::::::::::::::::::::: EXECUTING SEARCH ::::::::::::::::::::::::::::::")

                search_handler = Searcher(exclude_dirs=exclude_dirs, exclude_exts=exclude_exts, exclude_files=exclude_files)
                if args.search_ext:
                    print(f"\nSearching for files with extensions: {', '.join(args.search_ext)}")
                    search_handler.search_by_extension(source_dir, args.search_ext, args.no_log)

                if args.search_pattern:
                    target_exts = args.include_extensions or None
                    print(f"\nSearching for pattern: '{args.search_pattern}'")
                    if target_exts:
                        print(f"In files with extensions: {', '.join(target_exts)}")
                    search_handler.search_by_pattern(source_dir, args.search_pattern, target_exts, args.no_log)

                if args.search_size:
                    min_size = None if args.search_size[0].lower() == 'none' else float(args.search_size[0])
                    max_size = None if args.search_size[1].lower() == 'none' else float(args.search_size[1])
                    target_exts = args.include_extensions or None

                    size_range = []
                    if min_size is not None:
                        size_range.append(f">= {min_size} KB")
                    if max_size is not None:
                        size_range.append(f"<= {max_size} KB")

                    print(f"\nSearching for files with size {' and '.join(size_range)}")
                    if target_exts:
                        print(f"In files with extensions: {', '.join(target_exts)}")
                    search_handler.search_by_size(source_dir, min_size, max_size, target_exts, args.no_log)

                if args.search_date:
                    start_date = args.search_date[0]
                    end_date = args.search_date[1] if len(args.search_date) > 1 else None
                    target_exts = args.include_extensions or None
                    print(f"\nSearching for files modified since {start_date} until {end_date}" if end_date else "")
                    if target_exts:
                        print(f"In files with extensions: {', '.join(target_exts)}")
                    search_handler.search_by_date(source_dir, start_date, end_date, target_exts, args.no_log)

                if args.search_imports:
                    target_exts = args.include_extensions or ['.py']
                    print(f"\nSearching for imports of '{args.search_imports}'")
                    if target_exts:
                        print(f"In files with extensions: {', '.join(target_exts)}")
                    search_handler.search_imports(source_dir, args.search_imports, target_exts, args.no_log)

                if args.search_duplicates is not None:
                    target_exts = args.include_extensions or None
                    min_lines = args.search_duplicates
                    print(f"\nSearching for duplicate code blocks (min {min_lines} lines)")
                    if target_exts:
                        print(f"In files with extensions: {', '.join(target_exts)}")
                    search_handler.search_duplicates(source_dir, min_lines, extensions=target_exts, silent=args.no_log)

                if not args.no_log:
                    print("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

        summary_path = os.path.join(timestamp_dir, "summary.txt")
        with open(summary_path, 'w') as summary_file:
            summary_file.write(f"# Codebundle Operations Summary\n")
            summary_file.write(f"# Timestamp: {os.path.basename(timestamp_dir)}\n")
            summary_file.write(f"# Source: {os.path.abspath(source_dir)}\n")
            summary_file.write(f"# Destination: {os.path.abspath(timestamp_dir)}\n")
            local_timezone = datetime.datetime.now().astimezone().tzinfo
            summary_file.write(
                f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{local_timezone}]\n\n")

            for op in operations:
                if op in output_paths:
                    dest_path = output_paths[op]
                    # Use get_display_path for the summary file as well
                    rel_dest_path = get_relative_path(dest_path, timestamp_dir)
                    summary_file.write(f"## {op.upper()}\n")
                    summary_file.write(f"Destination: {rel_dest_path}\n\n")

        if not args.no_log:
            print(f"\nSummary of operations written to {get_relative_path(summary_path, timestamp_dir)}")
        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
