import os
import argparse
import sys
import datetime

from constants import (
    DEFAULT_EXCLUDE_DIRS, ALL_EXCLUDE_EXTENSIONS, ALL_EXCLUDE_FILENAMES,
    DEFAULT_FLATTEN_OUTPUT_PATH, DEFAULT_DEFLATTEN_OUTPUT_PATH, DEFAULT_BUNDLE_OUTPUT_PATH,
    DEFAULT_MINIFY_OUTPUT_PATH, DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH,
    OPERATION_FLATTEN, OPERATION_DEFLATTEN, OPERATION_BUNDLE, OPERATION_MINIFY, OPERATION_MINIFY_BUNDLE
)
from handlers import HANDLERS, FileExtHandler
from utils import merge_with_defaults, merge_stats, create_output_dir, format_path, get_relative_path


def main():
    parser = argparse.ArgumentParser(description="Flatten, deflatten, bundle, or minify a directory of files.")

    # [argument parsing code remains unchanged]
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

    parser.add_argument(
        "--file-types", "-t",
        nargs="+",
        choices=["py", "ipynb", "jsts", "mdtxt", "yml", "shell", "json", "go"],
        default=["py", "ipynb", "jsts", "mdtxt", "yml", "shell", "json", "go"],
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
        help="Specific filenames to exclude"
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

    operation_group = parser.add_argument_group('operations')
    operation_group.add_argument(
        "--flatten", "-f",
        action="store_true",
        help="Flatten the directory structure (default: True if no other operation specified)"
    )
    operation_group.add_argument(
        "--deflatten", "-df",
        action="store_true",
        help="Deflatten the directory (restore original structure)"
    )
    operation_group.add_argument(
        "--bundle", "-b",
        action="store_true",
        help="Bundle files into a single document file"
    )
    operation_group.add_argument(
        "--minify-bundle", "-mb",
        action="store_true",
        help="Minify files and bundle them into a single document file"
    )
    operation_group.add_argument(
        "--minify", "-m",
        action="store_true",
        help="Create a minified copy of the directory while preserving structure"
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

    args = parser.parse_args()

    source_dir = args.src_named if args.src_named else args.src_pos
    if not source_dir:
        source_dir = os.getcwd()
    base_dir, _ = create_output_dir()
    # print(f"Base output directory: {base_dir}")

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
    if not operations:
        operations = [
            OPERATION_FLATTEN,
            OPERATION_DEFLATTEN,
            OPERATION_MINIFY,
            OPERATION_BUNDLE,
            OPERATION_MINIFY_BUNDLE,
        ]

    timestamp_dir, _ = create_output_dir("multiple")
    print(f"Source directory (absolute): {os.path.abspath(source_dir)}")
    print(f"Destination directory (absolute): {timestamp_dir}")

    output_paths = {}

    exclude_dirs = merge_with_defaults(args.exclude_dirs, DEFAULT_EXCLUDE_DIRS, args.ignore_defaults)
    exclude_exts = merge_with_defaults(args.exclude_extensions, ALL_EXCLUDE_EXTENSIONS, args.ignore_defaults)
    exclude_files = merge_with_defaults(args.exclude_files, ALL_EXCLUDE_FILENAMES, args.ignore_defaults)

    try:
        for operation in operations:
            handler_results = []
            if operation == OPERATION_FLATTEN:
                flatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not flatten_dest:
                    flatten_dest = os.path.join(timestamp_dir, DEFAULT_FLATTEN_OUTPUT_PATH)
                output_paths[operation] = flatten_dest

                print("\n\n========== EXECUTING FLATTEN ==========")

                for file_type in args.file_types:
                    if file_type in HANDLERS:
                        handler = HANDLERS[file_type]
                        file_dest_dir = os.path.join(flatten_dest, file_type)

                        if args.include_extensions and not any(
                                ext in args.include_extensions for ext in handler.extensions):
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
                                    print(f"Removed empty directory: {file_dest_dir}")
                            except OSError:
                                pass

                        print("--------------------\n")

                merged_stats = merge_stats(handler_results)
                if not args.no_log and handler_results:
                    if merged_stats["files_copied"] > 0:
                        print("----- OVERALL SUMMARY -----")
                        print(f"Total files flattened: {merged_stats['files_copied']}")
                        print(f"Total data processed: {merged_stats['bytes_copied'] / 1024:.2f} KB")
                    else:
                        print("----- OVERALL SUMMARY -----")
                        print(f"No files were flattened.")

                print("==============================")

            elif operation == OPERATION_DEFLATTEN:
                deflatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not deflatten_dest:
                    deflatten_dest = os.path.join(timestamp_dir, DEFAULT_DEFLATTEN_OUTPUT_PATH)
                output_paths[operation] = deflatten_dest

                print("\n\n========== EXECUTING DEFLATTEN ==========")

                if not args.no_log:
                    print(f"Destination: {get_relative_path(deflatten_dest)}")

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
                            print("--------------------\n")

                merged_stats = merge_stats(handler_results)
                if not args.no_log and handler_results:
                    if merged_stats["files_copied"] > 0:
                        print("----- OVERALL SUMMARY -----")
                        print(f"Total files deflattened: {merged_stats['files_copied']}")
                        print(f"Total directories created: {merged_stats['dirs_created']}")
                        print(f"Total data processed: {merged_stats['bytes_copied'] / 1024:.2f} KB")
                    else:
                        print("----- OVERALL SUMMARY -----")
                        print(f"No files were deflattened.")

                print("==============================")

            elif operation in [OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE]:
                bundle_dest = args.dest_named if args.dest_named else args.dest_pos
                if not bundle_dest:
                    if operation == OPERATION_BUNDLE:
                        bundle_dest = os.path.join(timestamp_dir, DEFAULT_BUNDLE_OUTPUT_PATH)
                    else:  # OPERATION_MINIFY_BUNDLE
                        bundle_dest = os.path.join(timestamp_dir, DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH)
                output_paths[operation] = bundle_dest

                if operation == OPERATION_BUNDLE:
                    print("\n\n========== EXECUTING BUNDLE ==========")
                else:
                    print("\n\n========== EXECUTING MINIFY-BUNDLE ==========")

                # Create a combined bundle of all file types
                if args.file_types and HANDLERS:
                    combined_extensions = []
                    for file_type in args.file_types:
                        if file_type in HANDLERS:
                            combined_extensions.extend(HANDLERS[file_type].extensions)

                    # Create a new combined handler with all extensions
                    combined_handler = FileExtHandler(
                        extensions=combined_extensions,
                        exclude_dirs=DEFAULT_EXCLUDE_DIRS,
                        exclude_extensions=ALL_EXCLUDE_EXTENSIONS,
                        exclude_filenames=ALL_EXCLUDE_FILENAMES
                    )

                    stats = combined_handler.bundle_files(
                        source_dir, bundle_dest, exclude_dirs, exclude_exts, exclude_files,
                        args.include_dirs, args.include_extensions, args.include_files,
                        args.no_log, operation == OPERATION_MINIFY_BUNDLE
                    )
                    handler_results.append(stats)

                print("==============================")

            elif operation == OPERATION_MINIFY:
                minify_dest = args.dest_named if args.dest_named else args.dest_pos
                if not minify_dest:
                    minify_dest = os.path.join(timestamp_dir, DEFAULT_MINIFY_OUTPUT_PATH)
                output_paths[operation] = minify_dest

                print("\n\n========== EXECUTING MINIFY ==========")

                for file_type in args.file_types:
                    if file_type in HANDLERS:
                        handler = HANDLERS[file_type]

                        if args.include_extensions and not any(ext in args.include_extensions for ext in handler.extensions):
                            continue

                        if not args.no_log:
                            print(f"----- {file_type.upper()} FILES -----")

                        stats = handler.minify_dir(
                            source_dir, minify_dest, exclude_dirs, exclude_exts, exclude_files,
                            args.include_dirs, args.include_extensions, args.include_files,
                            args.clear_dest_dir, args.no_log
                        )

                        handler_results.append(stats)
                        print("--------------------\n")

                merged_stats = merge_stats(handler_results)
                if not args.no_log and handler_results:
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

                print("==============================")

        summary_path = os.path.join(timestamp_dir, "operations_summary.txt")
        with open(summary_path, 'w') as summary_file:
            summary_file.write(f"# Codebundle Operations Summary\n")
            summary_file.write(f"# Timestamp: {os.path.basename(timestamp_dir)}\n")
            summary_file.write(f"# Source: {os.path.abspath(source_dir)}\n")
            summary_file.write(f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

            for op in operations:
                if op in output_paths:
                    dest_path = output_paths[op]
                    summary_file.write(f"## {op.upper()}\n")
                    summary_file.write(f"Destination: {format_path(dest_path)}\n\n")

        print(f"\nSummary written to {get_relative_path(summary_path)}")
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
