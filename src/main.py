import os
import argparse
import sys
import time

from constants import DEFAULT_EXCLUDE_DIRS, ALL_EXCLUDE_EXTENSIONS, ALL_EXCLUDE_FILENAMES, ALL_EXTENSIONS
from handlers import HANDLERS
from utils import get_relative_path, print_stats


def bundle_files(source_dir, output_file, file_types=None, exclude_dirs=None, exclude_exts=None,
                 exclude_files=None, include_files=None, silent=False):
    file_types = file_types or ["py", "ipynb", "js", "md", "yaml"]
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_exts = exclude_exts or ALL_EXCLUDE_EXTENSIONS
    exclude_files = exclude_files or ALL_EXCLUDE_FILENAMES

    if isinstance(exclude_files, list):
        exclude_files = list(exclude_files)
    else:
        exclude_files = []

    source_dir = os.path.abspath(source_dir)
    output_file = os.path.abspath(output_file)
    output_filename = os.path.basename(output_file)
    if output_filename not in exclude_files:
        exclude_files.append(output_filename)
    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_bundled": 0,
        "bytes_bundled": 0,
        "skipped_files": 0,
        "max_nesting_level": 0
    }

    # Get all file extensions based on selected file types
    included_extensions = []
    for file_type in file_types:
        if file_type in HANDLERS:
            included_extensions.extend(HANDLERS[file_type].extensions)

    start_time = time.time()

    if not silent:
        print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
        print(f"Output file: {get_relative_path(output_file, os.getcwd())}\n")
        print(f"Bundling files into a single text file...")

    files_to_bundle = []
    for root, dirs, files in os.walk(source_dir):
        stats["dirs_traversed"] += 1

        # Calculate nesting level
        current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
        stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            stats["total_files_processed"] += 1
            file_path = os.path.join(root, file)
            if os.path.abspath(file_path) == output_file:
                stats["skipped_files"] += 1
                continue

            file_ext = os.path.splitext(file)[1].lower()

            # Check if file should be included
            is_included_ext = any(file.lower().endswith(ext) for ext in included_extensions)
            is_excluded_ext = any(file.endswith(ext) for ext in exclude_exts)
            is_excluded_file = file in exclude_files

            # If include_files is specified, only include those files
            if include_files:
                should_include = file in include_files
            else:
                should_include = is_included_ext and not is_excluded_ext and not is_excluded_file

            if should_include:
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                if path_parts:
                    formatted_path = "___".join(path_parts + [file])
                else:
                    formatted_path = file

                files_to_bundle.append({
                    'file_path': file_path,
                    'formatted_path': formatted_path,
                    'rel_path': os.path.relpath(file_path, source_dir)
                })
            else:
                stats["skipped_files"] += 1

    if not files_to_bundle:
        if not silent:
            print("No files found to bundle.")
        end_time = time.time()
        duration = end_time - start_time
        if not silent:
            print_stats("bundling", stats, duration)
        return stats

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write("=" * 80 + "\n")
        outfile.write(f"BUNDLED FILES FROM: {source_dir}\n")
        outfile.write(f"CREATED: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write("=" * 80 + "\n\n")

        for file_info in files_to_bundle:
            file_path = file_info['file_path']
            formatted_path = file_info['formatted_path']
            rel_path = file_info['rel_path']

            try:
                # Read file content
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                # Write file separator
                outfile.write("\n" + "=" * 80 + "\n")
                outfile.write(f"FILE: {formatted_path}\n")
                outfile.write("=" * 80 + "\n\n")

                # Write file content
                outfile.write(content)
                outfile.write("\n")

                # Update stats
                stats["files_bundled"] += 1
                stats["bytes_bundled"] += os.path.getsize(file_path)

                if not silent:
                    print(f"Bundled: {rel_path}")

            except UnicodeDecodeError:
                if not silent:
                    print(f"Skipped binary file: {rel_path}")
                stats["skipped_files"] += 1
            except Exception as e:
                if not silent:
                    print(f"Error bundling {rel_path}: {str(e)}")
                stats["skipped_files"] += 1

        # Write footer
        outfile.write("\n" + "=" * 80 + "\n")
        outfile.write(f"END OF BUNDLED FILES ({stats['files_bundled']} files)\n")
        outfile.write("=" * 80 + "\n")

    end_time = time.time()
    duration = end_time - start_time

    if not silent:
        print_stats("bundle", stats, duration)

    return stats


def merge_stats(stats_list):
    """Merge multiple statistics dictionaries into one"""
    merged_stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_copied": 0,
        "bytes_copied": 0,
        "skipped_files": 0,
        "max_nesting_level": 0,
        "dirs_created": 0,
        "files_bundled": 0,
        "bytes_bundled": 0
    }

    for stats in stats_list:
        for key, value in stats.items():
            if key in merged_stats:
                merged_stats[key] += value
                # For max_nesting_level, keep the maximum value
                if key == "max_nesting_level":
                    merged_stats[key] = max(merged_stats[key], value)

    return merged_stats


def flatten_dir(source_dir, dest_dir, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                include_files=None, clear_dest_dir=False, silent=False):
    file_types = file_types or ["py", "ipynb", "js", "md", "yaml"]
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_exts = exclude_exts or ALL_EXCLUDE_EXTENSIONS
    exclude_files = exclude_files or ALL_EXCLUDE_FILENAMES

    all_stats = []
    start_time = time.time()

    for file_type in file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            file_dest_dir = os.path.join(dest_dir, file_type)

            if not silent:
                print(f"\n================ {file_type.upper()} FILES ================\n")

            file_stats = handler.flatten_dir(source_dir, file_dest_dir, exclude_dirs, exclude_exts, exclude_files, include_files, clear_dest_dir, silent)

            if file_stats["files_copied"] > 0:
                all_stats.append(file_stats)
            elif os.path.exists(file_dest_dir) and not os.listdir(file_dest_dir):
                try:
                    os.rmdir(file_dest_dir)
                    if not silent:
                        print(f"Removed empty directory: {file_dest_dir}")
                except OSError:
                    pass

    merged_stats = merge_stats(all_stats)
    end_time = time.time()
    duration = end_time - start_time

    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("flatten", merged_stats, duration)

    return merged_stats


def deflatten_dir(flattened_dir, dest_dir, file_types=None, exclude_files=None, include_files=None, clear_dest_dir=False,
                  silent=False):
    file_types = file_types or ["py", "ipynb", "js", "md", "yaml"]
    exclude_files = exclude_files or ALL_EXCLUDE_FILENAMES

    all_stats = []
    start_time = time.time()

    for file_type in file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            source_dir = os.path.join(flattened_dir, file_type)

            if os.path.exists(source_dir) and os.listdir(source_dir):
                if not silent:
                    print(f"\n================ {file_type.upper()} FILES ================\n")

                file_stats = handler.deflatten_dir(source_dir, dest_dir, exclude_files, include_files, clear_dest_dir, silent)
                all_stats.append(file_stats)

    merged_stats = merge_stats(all_stats)
    end_time = time.time()
    duration = end_time - start_time

    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("deflatten", merged_stats, duration)

    return merged_stats


def main():
    parser = argparse.ArgumentParser(description="Flatten, deflatten, or bundle a directory of Python, JavaScript, TypeScript, Markdown, and YAML files.")

    # Support both positional and named arguments
    src_group = parser.add_argument_group('source')
    src_group.add_argument("src_pos", nargs="?", help="Source directory path (positional)")
    src_group.add_argument("--src", dest="src_named", help="Source directory path (named)")

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument("dest_pos", nargs="?", help="Destination directory or file path (positional)")
    dest_group.add_argument("--dest", dest="dest_named", help="Destination directory or file path (named)")

    parser.add_argument("--file-types",
                        nargs="+",
                        choices=["py", "ipynb", "js", "md", "yaml"],
                        default=["py", "ipynb", "js", "md", "yaml"],
                        help="File types to process: 'py' for Python, 'ipynb' for Python Notebooks, 'js' for JavaScript/TypeScript, 'md' for Markdown, 'yaml' for YAML (default: all)")

    parser.add_argument("--exclude-dirs",
                        nargs="+",
                        help="Directory names to exclude")
    parser.add_argument("--exclude-extensions",
                        nargs="+",
                        help="File extensions to exclude")
    parser.add_argument("--exclude-files",
                        nargs="+",
                        help="Specific filenames to exclude")

    parser.add_argument("--include-files",
                        nargs="+",
                        help="Specific filenames to include (only these will be processed)")

    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument("--deflatten",
                                 action="store_true",
                                 help="Deflatten the directory instead of flattening (default: False)")
    operation_group.add_argument("--bundle", "-b",
                                 action="store_true",
                                 help="Bundle files into a single text file (default: False)")

    parser.add_argument("--clear-dest-dir",
                        action="store_true",
                        help="Clear the destination directory before copying (default: False)")
    parser.add_argument('--no-log',
                        action='store_true',
                        help="Suppress all output logs.")

    args = parser.parse_args()

    source_dir = args.src_named if args.src_named else args.src_pos
    dest_path = args.dest_named if args.dest_named else args.dest_pos

    if not source_dir or not dest_path:
        parser.print_help()
        print("\nError: Both source and destination are required.")
        return 1

    try:
        if args.deflatten:
            stats = deflatten_dir(source_dir, dest_path, args.file_types, args.exclude_files, args.include_files, args.clear_dest_dir, args.no_log)
        elif args.bundle:
            stats = bundle_files(source_dir, dest_path, args.file_types, args.exclude_dirs, args.exclude_extensions, args.exclude_files, args.include_files, args.no_log)
        else:
            stats = flatten_dir(source_dir, dest_path, args.file_types, args.exclude_dirs, args.exclude_extensions, args.exclude_files, args.include_files, args.clear_dest_dir, args.no_log)

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
