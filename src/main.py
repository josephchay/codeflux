"""
CodeFlux: A comprehensive codebase management and transformation tool.

This application provides utilities for code flattening, minification, bundling, and analysis.
"""

import argparse
import datetime
import os
import sys

# Import core modules
from file_handler import FileHandler
from handlers import HANDLERS
from operations.bundle import BundleOperation
from operations.deflatten import DeflattenOperation
from operations.flatten import FlattenOperation
from operations.minify import MinifyOperation
from utils.logging import Logger

# Define constants
OPERATION_FLATTEN = "flatten"
OPERATION_DEFLATTEN = "deflatten"
OPERATION_MINIFY = "minify"
OPERATION_BUNDLE = "bundle"
OPERATION_MINIFY_BUNDLE = "minify_bundle"
OPERATION_ACROSCAN = "acroscan"
OPERATION_SEARCH = "search"
OPERATION_PROPERTIES = "properties"
OPERATION_TREE = "tree"
OPERATION_ROOT_TREE = "root_tree"
OPERATION_BIBDEDUP = "bibdedup"

DEFAULT_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv",
                        "node_modules", "dist", "build", ".next", "codeflux.egg-info",
                        "codeflux"]

# Default output paths
DEFAULT_FLATTEN_OUTPUT_PATH = "flattened"
DEFAULT_DEFLATTEN_OUTPUT_PATH = "deflattened"
DEFAULT_MINIFY_OUTPUT_PATH = "minified"
DEFAULT_BUNDLE_OUTPUT_PATH = "bundled.txt"
DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH = "minified_bundle.txt"
DEFAULT_TREE_OUTPUT_PATH = "processed_directory_tree.txt"
DEFAULT_ROOT_TREE_OUTPUT_PATH = "root_directory_tree.txt"
DEFAULT_SUMMARY_OUTPUT_PATH = "summary.txt"


def run_processed_tree_operation(source_dir, timestamp_dir, args, logger):
    """Run the processed directory tree visualization."""
    from ui.tree import visualize_dir_tree

    try:
        output_file = os.path.join(timestamp_dir, DEFAULT_TREE_OUTPUT_PATH)
        if not args.no_log:
            logger.info("\n\n:::::::::::::::::::::::::::::: PROCESSED DIRECTORY TREE ::::::::::::::::::::::::::::::")
            logger.info(f"Destination: \"{DEFAULT_TREE_OUTPUT_PATH}\"")

        visualize_dir_tree(
            source_dir,
            output_file,
            exclude_dirs=args.exclude_dirs or DEFAULT_EXCLUDE_DIRS,
            exclude_exts=args.exclude_extensions,
            exclude_files=args.exclude_files,
            print_to_console=not args.no_log,
            truncate_output=args.truncate
        )

        if not args.no_log:
            logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    except Exception as e:
        if not args.no_log:
            logger.error(f"Error generating processed directory tree: {str(e)}")


def run_root_tree_operation(source_dir, timestamp_dir, args, logger):
    """Run the root directory tree visualization."""
    from ui.tree import visualize_root_dir_tree

    try:
        output_file = os.path.join(timestamp_dir, DEFAULT_ROOT_TREE_OUTPUT_PATH)
        if not args.no_log:
            logger.info("\n\n:::::::::::::::::::::::::::::: ROOT DIRECTORY TREE ::::::::::::::::::::::::::::::")
            logger.info(f"Destination: \"{DEFAULT_ROOT_TREE_OUTPUT_PATH}\"")

        visualize_root_dir_tree(
            source_dir,
            output_file,
            print_to_console=not args.no_log,
            truncate_output=args.truncate,
            show_processing_status=True,
            user_exclude_dirs=args.exclude_dirs,
            user_exclude_exts=args.exclude_extensions,
            user_exclude_files=args.exclude_files
        )

        if not args.no_log:
            logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    except Exception as e:
        if not args.no_log:
            logger.error(f"Error generating root directory tree: {str(e)}")


def make_parser():
    """Create and configure the argument parser for the CLI."""
    parser = argparse.ArgumentParser(description="CodeFlux: A comprehensive codebase management and transformation tool.")

    # Source and destination arguments
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

    # Operation arguments
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
    operation_group.add_argument(
        "--acroscan", "-as",
        action="store_true",
        help="Scan for and optionally replace acronyms in documents"
    )
    operation_group.add_argument(
        "--properties", "-p",
        action="store_true",
        help="Display detailed file properties without modifying anything"
    )
    operation_group.add_argument(
        "--exclude-hash", "-xh",
        action="store_true",
        help="Exclude MD5 hash calculation from properties analysis (faster for large files)"
    )
    operation_group.add_argument(
        "--tree", "-tr",
        action="store_true",
        help="Generate a text-based visualization of the processed directory structure (default: True if no other operation specified)"
    )
    operation_group.add_argument(
        "--root-tree", "-rtr",
        action="store_true",
        help="Generate a complete text-based visualization of the root directory tree (with operation status)"
    )

    # BibTeX deduplication
    parser.add_argument(
        '--bibdedup', "-bd",
        action='store_true',
        help="Check for similar titles across multiple `.bib` files"
    )
    parser.add_argument(
        '--similarity-threshold', "-st",
        type=float,
        default=0.9,
        help="Similarity threshold for BibTeX duplicate detection (0.0-1.0, default: 0.9)"
    )

    # File type selection
    parser.add_argument(
        "--file-types", "-t",
        nargs="+",
        default=list(HANDLERS.keys()),
        help="File types to process (default: all)"
    )

    # Exclusion options
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

    # Inclusion options
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

    # Default handling
    defaults_group = parser.add_argument_group('defaults handling')
    defaults_group.add_argument(
        "--ignore-defaults", "-i",
        action="store_true",
        help="Ignore all default exclusion lists and only use the provided options"
    )

    # Acroscan options
    acroscan_group = parser.add_argument_group('acroscan options')
    acroscan_group.add_argument(
        "--acronym-list", "-al",
        help="Path to the CSV file containing acronyms (default: codeflux/src/templates/acronyms.csv)"
    )
    acroscan_group.add_argument(
        "--acronym-output", "-ao",
        help="Path to output the acronyms file (default: acronyms.txt or acronyms.tex for LaTeX)"
    )
    acroscan_group.add_argument(
        "--latex-mode", "-lm",
        action="store_true",
        default=True,
        help="Process files in LaTeX mode (uses \\ac{...} syntax)"
    )
    acroscan_group.add_argument(
        "--find-potential", "-fp",
        action="store_true",
        help="Find potential acronyms not in the list (words with multiple uppercase letters)"
    )
    acroscan_group.add_argument(
        "--replace-acronyms", "-ra",
        action="store_true",
        default=True,
        help="Replace found acronyms in the processed files (default: True)"
    )
    acroscan_group.add_argument(
        "--no-recursive-acroscan", "-nras",
        action="store_true",
        help="Do not recursively process subdirectories for acroscan"
    )

    # Search operations
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

    # Snippet options
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

    # General options
    parser.add_argument(
        "--clear-dest-dir", "-c",
        action="store_true",
        help="Clear the destination directory before copying (default: False)"
    )
    parser.add_argument(
        '--truncate', "-trc",
        action='store_true',
        help="Truncate long tree output in console."
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


def merge_with_defaults(user_values, defaults, ignore_defaults=False):
    """Merge user-provided values with default values."""
    if user_values is None:
        return [] if ignore_defaults else defaults
    if ignore_defaults:
        return user_values

    return list(set(user_values + defaults))


def mkdir_output(operation=None):
    """Create output directories and return paths."""
    base_dir = os.path.join(os.getcwd(), "codeflux")
    os.makedirs(base_dir, exist_ok=True)

    if operation:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp_dir = os.path.join(base_dir, timestamp)
        os.makedirs(timestamp_dir, exist_ok=True)
        return timestamp_dir, operation

    return base_dir, None


def process_flatten_operation(source_dir, output_dir, args, exclude_dirs, exclude_exts, exclude_files, logger):
    """Process the flatten operation for all selected file types."""
    results = []

    for file_type in args.file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]

            if args.no_filetype_dirs:
                file_dest_dir = output_dir
            else:
                file_dest_dir = os.path.join(output_dir, file_type)

            if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                continue

            if not args.no_log:
                logger.info(f"----- {file_type.upper()} FILES -----")

            operation = FlattenOperation(handler, logger)
            stats = operation.execute(
                source_dir,
                file_dest_dir,
                exclude_dirs=exclude_dirs,
                exclude_exts=exclude_exts,
                exclude_files=exclude_files,
                include_dirs=args.include_dirs,
                include_exts=args.include_extensions,
                include_files=args.include_files,
                clear_dest_dir=args.clear_dest_dir
            )
            results.append(stats)

            # Clean up empty directories
            if stats.files_copied == 0 and os.path.exists(file_dest_dir) and not os.listdir(file_dest_dir):
                try:
                    os.rmdir(file_dest_dir)
                    if not args.no_log:
                        logger.info(f"Removed empty directory: {os.path.relpath(file_dest_dir)}")
                except OSError:
                    pass

            if not args.no_log:
                logger.info("--------------------\n")

    return results


def process_deflatten_operation(source_dir, output_dir, args, exclude_files, logger):
    """Process the deflatten operation for all selected file types."""
    results = []
    has_files_to_process = False

    # Check if there are any files to process
    for file_type in args.file_types:
        if file_type in HANDLERS:
            file_source_dir = os.path.join(source_dir, file_type)
            if os.path.exists(file_source_dir) and os.listdir(file_source_dir):
                has_files_to_process = True
                break

    if not has_files_to_process and not args.no_log:
        logger.info("No files found to deflatten.")
        logger.info("No operations performed.")
        return results

    if not args.no_log:
        logger.info(f"Destination: \"{DEFAULT_DEFLATTEN_OUTPUT_PATH}/\"\n")

    for file_type in args.file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            file_source_dir = os.path.join(source_dir, file_type)

            if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                continue

            if os.path.exists(file_source_dir) and os.listdir(file_source_dir):
                if not args.no_log:
                    logger.info(f"---------- {file_type.upper()} FILES ----------")

                operation = DeflattenOperation(handler, logger)
                stats = operation.execute(
                    file_source_dir,
                    output_dir,
                    exclude_files=exclude_files,
                    include_dirs=args.include_dirs,
                    include_exts=args.include_extensions,
                    include_files=args.include_files,
                    clear_dest_dir=args.clear_dest_dir
                )
                results.append(stats)

                if not args.no_log:
                    logger.info("--------------------\n")

    return results


def process_minify_operation(source_dir, output_dir, args, exclude_dirs, exclude_exts, exclude_files, logger):
    """Process the minify operation for all selected file types."""
    results = []

    for file_type in args.file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]

            if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                continue

            if not args.no_log:
                logger.info(f"----- {file_type.upper()} FILES -----")

            operation = MinifyOperation(handler, logger)
            stats = operation.execute(
                source_dir,
                output_dir,
                exclude_dirs=exclude_dirs,
                exclude_exts=exclude_exts,
                exclude_files=exclude_files,
                include_dirs=args.include_dirs,
                include_exts=args.include_extensions,
                include_files=args.include_files,
                clear_dest_dir=args.clear_dest_dir,
                continue_on_error=args.continue_on_error
            )
            results.append(stats)

            if not args.no_log:
                logger.info("--------------------\n")

    return results


def process_bundle_operation(source_dir: str, output_file: str, args, exclude_dirs, exclude_exts, exclude_files, is_minified, logger):
    """Process the bundle operation with combined file handlers."""
    results = []

    # Create a combined bundle of all file types
    if args.file_types and HANDLERS:
        combined_extensions = []
        for file_type in args.file_types:
            if file_type in HANDLERS:
                combined_extensions.extend(HANDLERS[file_type].extensions)

        # Create a combined handler with all extensions
        combined_handler = FileHandler(
            extensions=combined_extensions,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=exclude_exts,
            exclude_filenames=exclude_files
        )

        operation = BundleOperation(combined_handler, logger)
        stats = operation.execute(
            source_dir,
            output_file,
            exclude_dirs=exclude_dirs,
            exclude_exts=exclude_exts,
            exclude_files=exclude_files,
            include_dirs=args.include_dirs,
            include_exts=args.include_extensions,
            include_files=args.include_files,
            minify=is_minified,
            snippet=args.snippet,
            snippet_lines=args.snippet_lines,
            snippet_start=args.snippet_start,
            snippet_context=args.snippet_context,
            search_pattern=args.search_pattern if hasattr(args, 'search_pattern') else None,
            continue_on_error=args.continue_on_error
        )

        # Fix for minify-bundle statistics - ensure bytes_original is properly set
        if is_minified and stats.bytes_original == 0:
            # If original bytes are not set but bundled bytes are, use bundled bytes
            stats.bytes_original = stats.bytes_bundled

        results.append(stats)

    return results


def main():
    """Main entry point for the application."""
    args = make_parser().parse_args()

    # Determine source directory
    source_dir = args.src_named if args.src_named else args.src_pos
    if not source_dir:
        source_dir = os.getcwd()

    if not os.path.isdir(source_dir):
        print(f"Error: Source directory '{source_dir}' does not exist or is not a directory")
        return 1

    # Create output directories
    base_dir, _ = mkdir_output()
    timestamp_dir, _ = mkdir_output("multiple")

    # Set up logger
    logger = Logger(silent=args.no_log)

    if not args.no_log:
        logger.info(f"Source directory (absolute): {os.path.abspath(source_dir)}")
        logger.info(f"Destination directory (absolute): {timestamp_dir}")

    # Determine which operations to run
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
    if args.acroscan:
        operations.append(OPERATION_ACROSCAN)
    if args.search_ext or args.search_pattern or args.search_size:
        operations.append(OPERATION_SEARCH)
    if args.properties:
        operations.append(OPERATION_PROPERTIES)
    if args.tree:
        operations.append(OPERATION_TREE)
    if args.root_tree:
        operations.append(OPERATION_ROOT_TREE)
    if args.bibdedup:
        operations.append(OPERATION_BIBDEDUP)

    # If no operations specified, default to all
    if not operations:
        operations = [
            OPERATION_FLATTEN, OPERATION_DEFLATTEN, OPERATION_MINIFY,
            OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE, OPERATION_ACROSCAN,
            OPERATION_BIBDEDUP
        ]

    # Combine exclusion lists
    exclude_dirs = merge_with_defaults(args.exclude_dirs, DEFAULT_EXCLUDE_DIRS, args.ignore_defaults)
    exclude_exts = merge_with_defaults(args.exclude_extensions, [], args.ignore_defaults)
    exclude_files = merge_with_defaults(args.exclude_files, [], args.ignore_defaults)

    if exclude_files:
        exclude_files = [path.replace('\\', '/') for path in exclude_files]

    # Track output paths for summary
    output_paths = {}

    try:
        for operation in operations:
            if operation == OPERATION_FLATTEN:
                flatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not flatten_dest:
                    flatten_dest = os.path.join(timestamp_dir, DEFAULT_FLATTEN_OUTPUT_PATH)
                output_paths[operation] = flatten_dest

                if not args.no_log:
                    logger.info("\n\n:::::::::::::::::::::::::::::: FLATTEN ::::::::::::::::::::::::::::::")
                    logger.info(f"Destination: \"{DEFAULT_FLATTEN_OUTPUT_PATH}/\"\n")

                results = process_flatten_operation(source_dir, flatten_dest, args, exclude_dirs, exclude_exts, exclude_files, logger)

                if not args.no_log:
                    if results:
                        total_files = sum(result.files_copied for result in results)
                        if total_files > 0:
                            logger.info("----- OPERATION SUMMARY -----")
                            logger.info(f"Total files flattened: {total_files}")
                            total_bytes = sum(result.bytes_copied for result in results)
                            logger.info(f"Total data processed: {total_bytes / 1024:.2f} KB")
                        else:
                            logger.info("----- OPERATION SUMMARY -----")
                            logger.info(f"No files were flattened.")
                    logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

            elif operation == OPERATION_DEFLATTEN:
                deflatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not deflatten_dest:
                    deflatten_dest = os.path.join(timestamp_dir, DEFAULT_DEFLATTEN_OUTPUT_PATH)
                output_paths[operation] = deflatten_dest

                if not args.no_log:
                    logger.info("\n\n:::::::::::::::::::::::::::::: DEFLATTEN ::::::::::::::::::::::::::::::")
                    logger.info(f"Destination: \"{DEFAULT_DEFLATTEN_OUTPUT_PATH}/\"\n")

                results = process_deflatten_operation(source_dir, deflatten_dest, args, exclude_files, logger)

                if not args.no_log:
                    if results:
                        total_files = sum(result.files_copied for result in results)
                        if total_files > 0:
                            logger.info("----- OPERATION SUMMARY -----")
                            logger.info(f"Total files deflattened: {total_files}")
                            total_dirs = sum(result.dirs_created for result in results)
                            logger.info(f"Total directories created: {total_dirs}")
                            total_bytes = sum(result.bytes_copied for result in results)
                            logger.info(f"Total data processed: {total_bytes / 1024:.2f} KB")
                        else:
                            logger.info("----- OPERATION SUMMARY -----")
                            logger.info(f"No files were deflattened.")
                    logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

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
                        logger.info("\n\n:::::::::::::::::::::::::::::: BUNDLE ::::::::::::::::::::::::::::::")
                        logger.info(f"Destination: \"{DEFAULT_BUNDLE_OUTPUT_PATH}\"\n")
                    else:
                        logger.info("\n\n:::::::::::::::::::::::::::::: MINIFY-BUNDLE ::::::::::::::::::::::::::::::")
                        logger.info(f"Destination: \"{DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH}\"")
                        logger.info("Minification: Enabled")
                        if args.continue_on_error:
                            logger.info("Note: Continuing on minification errors (--continue-on-error flag is set)")
                        logger.info("")

                is_minified = (operation == OPERATION_MINIFY_BUNDLE)
                results = process_bundle_operation(
                    source_dir, bundle_dest, args, exclude_dirs, exclude_exts, exclude_files, is_minified, logger
                )

                if not args.no_log:
                    logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

            elif operation == OPERATION_MINIFY:
                minify_dest = args.dest_named if args.dest_named else args.dest_pos
                if not minify_dest:
                    minify_dest = os.path.join(timestamp_dir, DEFAULT_MINIFY_OUTPUT_PATH)
                output_paths[operation] = minify_dest

                if not args.no_log:
                    logger.info("\n\n:::::::::::::::::::::::::::::: MINIFY ::::::::::::::::::::::::::::::")
                    logger.info(f"Destination: \"{DEFAULT_MINIFY_OUTPUT_PATH}/\"")
                    logger.info("Minification: Enabled")
                    if args.continue_on_error:
                        logger.info("Note: Continuing on minification errors (--continue-on-error flag is set)")
                    logger.info("")

                results = process_minify_operation(
                    source_dir, minify_dest, args, exclude_dirs, exclude_exts, exclude_files, logger
                )

                if not args.no_log:
                    if results:
                        total_files_copied = sum(result.files_copied for result in results)
                        total_files_minified = sum(result.files_minified for result in results)
                        if total_files_copied > 0:
                            logger.info("----- OPERATION SUMMARY -----")
                            logger.info(f"Total files minified: {total_files_minified}")
                            logger.info(f"Total files processed: {total_files_copied}")

                            total_original = sum(result.bytes_original for result in results)
                            total_minified = sum(result.bytes_minified for result in results)
                            if total_original > 0 and total_minified > 0:
                                orig_kb = total_original / 1024
                                mini_kb = total_minified / 1024
                                reduction = (1 - total_minified / max(total_original, 1)) * 100
                                logger.info(f"Original size: {orig_kb:.2f} KB")
                                logger.info(f"Minified size: {mini_kb:.2f} KB")
                                logger.info(f"Overall reduction: {reduction:.2f}%")
                        else:
                            logger.info("----- OPERATION SUMMARY -----")
                            logger.info(f"No files were minified.")
                    logger.info("::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")

        run_processed_tree_operation(source_dir, timestamp_dir, args, logger)
        run_root_tree_operation(source_dir, timestamp_dir, args, logger)

        # Write summary file
        summary_path = os.path.join(timestamp_dir, DEFAULT_SUMMARY_OUTPUT_PATH)
        with open(summary_path, 'w', encoding='utf-8') as summary_file:
            summary_file.write(f"CodeFlux Operations Summary\n\n")
            summary_file.write(f"Timestamp: {os.path.basename(timestamp_dir)}\n")
            local_timezone = datetime.datetime.now().astimezone().tzinfo
            summary_file.write(f"Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} [{local_timezone}]\n")
            summary_file.write(f"Source: {os.path.abspath(source_dir)}\n")
            summary_file.write(f"Destination: {os.path.abspath(timestamp_dir)}\n\n")

            # Record command for reference
            raw_command = ' '.join([sys.argv[0]] + [f'"{arg}"' if ' ' in arg else arg for arg in sys.argv[1:]])
            command = ' '.join([os.path.basename(sys.argv[0])] + sys.argv[1:])
            summary_file.write(f"Command (Raw): {raw_command}\n")
            summary_file.write(f"Command: {command}\n")

            # Add information about each operation
            for op in operations:
                if op in output_paths:
                    dest_path = output_paths[op]
                    rel_dest_path = os.path.relpath(dest_path, timestamp_dir)
                    summary_file.write(f"\n{op.upper()}\n")
                    summary_file.write(f"Destination: {rel_dest_path}\n")

        if not args.no_log:
            logger.info(f"\nSummary of operations written to \"{os.path.relpath(summary_path, timestamp_dir)}\"")

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
