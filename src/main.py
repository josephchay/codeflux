import os
import argparse
import sys
import time

from handlers.py_handler import (
    flatten_python_dir,
    deflatten_python_dir,
    DEFAULT_PYTHON_EXCLUDE_DIRS,
    DEFAULT_PYTHON_EXCLUDE_EXTENSIONS,
    DEFAULT_PYTHON_EXCLUDE_FILENAMES
)
from handlers.jsts_handler import (
    flatten_js_dir,
    deflatten_js_dir,
    DEFAULT_JS_EXCLUDE_DIRS,
    DEFAULT_JS_EXCLUDE_EXTENSIONS,
    DEFAULT_JS_EXCLUDE_FILENAMES,
    JS_EXTENSIONS
)
from handlers.md_handler import (
    flatten_md_dir,
    deflatten_md_dir,
    DEFAULT_MD_EXCLUDE_DIRS,
    DEFAULT_MD_EXCLUDE_EXTENSIONS,
    DEFAULT_MD_EXCLUDE_FILENAMES,
    MD_EXTENSIONS
)
from utils import get_relative_path, print_stats


def bundle_files(source_dir, output_file, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None, silent=False):
    """
    Bundle files from source_dir into a single text file with organized formatting
    """
    # Combine default exclusions from all handlers
    if exclude_dirs is None:
        exclude_dirs = list(set(DEFAULT_PYTHON_EXCLUDE_DIRS + DEFAULT_JS_EXCLUDE_DIRS + DEFAULT_MD_EXCLUDE_DIRS))

    if exclude_exts is None:
        exclude_exts = list(set(DEFAULT_PYTHON_EXCLUDE_EXTENSIONS + DEFAULT_JS_EXCLUDE_EXTENSIONS + DEFAULT_MD_EXCLUDE_EXTENSIONS))

    if exclude_files is None:
        exclude_files = list(set(DEFAULT_PYTHON_EXCLUDE_FILENAMES + DEFAULT_JS_EXCLUDE_FILENAMES + DEFAULT_MD_EXCLUDE_FILENAMES))

    if file_types is None:
        file_types = ["py", "js", "md"]

    # Convert to absolute path
    source_dir = os.path.abspath(source_dir)
    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    # Stats tracking
    stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_bundled": 0,
        "bytes_bundled": 0,
        "skipped_files": 0,
        "max_nesting_level": 0
    }

    # Extensions to include based on file_types
    included_extensions = []
    if "py" in file_types:
        included_extensions.append(".py")
    if "js" in file_types:
        included_extensions.extend(JS_EXTENSIONS)
    if "md" in file_types:
        included_extensions.extend(MD_EXTENSIONS)

    start_time = time.time()

    if not silent:
        print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
        print(f"Output file: {get_relative_path(output_file, os.getcwd())}\n")
        print(f"Bundling files into a single text file...")

    with open(output_file, 'w', encoding='utf-8') as outfile:
        # Write header
        outfile.write("=" * 80 + "\n")
        outfile.write(f"BUNDLED FILES FROM: {source_dir}\n")
        outfile.write(f"CREATED: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        outfile.write("=" * 80 + "\n\n")

        # Walk through the directory structure
        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Process files
            for file in files:
                stats["total_files_processed"] += 1
                file_path = os.path.join(root, file)
                file_ext = os.path.splitext(file)[1].lower()

                # Check if file should be included
                is_included = any(file.lower().endswith(ext) for ext in included_extensions)
                is_excluded_ext = any(file.endswith(ext) for ext in exclude_exts)
                is_excluded_file = file in exclude_files

                if is_included and not is_excluded_ext and not is_excluded_file:
                    # Format path with ___ separator (similar to flatten function)
                    path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                    if path_parts:
                        formatted_path = "___".join(path_parts + [file])
                    else:
                        formatted_path = file

                    # Get relative path for display in console
                    rel_path = os.path.relpath(file_path, source_dir)

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
                else:
                    stats["skipped_files"] += 1

    # Write footer
    with open(output_file, 'a', encoding='utf-8') as outfile:
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


def flatten_dir(source_dir, dest_dir, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None, clear_dest_dir=False, silent=False):
    """
    Flatten a directory structure for specified file types
    """
    if file_types is None:
        file_types = ["py", "js", "md"]

    # Combine default exclusions for files
    if exclude_files is None:
        exclude_files = list(set(DEFAULT_PYTHON_EXCLUDE_FILENAMES + DEFAULT_JS_EXCLUDE_FILENAMES + DEFAULT_MD_EXCLUDE_FILENAMES))

    all_stats = []
    start_time = time.time()

    # Process Python files
    if "py" in file_types:
        py_dest_dir = os.path.join(dest_dir, "py")
        if not silent:
            print("\n================ PYTHON FILES ================\n")
        py_stats = flatten_python_dir(source_dir, py_dest_dir, exclude_dirs, exclude_exts, exclude_files, clear_dest_dir, silent)

        # Only keep the stats if files were actually copied
        if py_stats["files_copied"] > 0:
            all_stats.append(py_stats)
        # Remove the directory if no files were copied
        elif os.path.exists(py_dest_dir) and not os.listdir(py_dest_dir):
            try:
                os.rmdir(py_dest_dir)
                if not silent:
                    print(f"Removed empty directory: {py_dest_dir}")
            except OSError:
                pass

    # Process JavaScript/TypeScript files
    if "js" in file_types:
        js_dest_dir = os.path.join(dest_dir, "jsts")
        if not silent:
            print("\n============= JAVASCRIPT FILES ==============\n")
        js_stats = flatten_js_dir(source_dir, js_dest_dir, exclude_dirs, exclude_exts, exclude_files, clear_dest_dir, silent)

        # Only keep the stats if files were actually copied
        if js_stats["files_copied"] > 0:
            all_stats.append(js_stats)
        # Remove the directory if no files were copied
        elif os.path.exists(js_dest_dir) and not os.listdir(js_dest_dir):
            try:
                os.rmdir(js_dest_dir)
                if not silent:
                    print(f"Removed empty directory: {js_dest_dir}")
            except OSError:
                pass

    # Process Markdown files
    if "md" in file_types:
        md_dest_dir = os.path.join(dest_dir, "md")
        if not silent:
            print("\n================ MARKDOWN FILES ================\n")
        md_stats = flatten_md_dir(source_dir, md_dest_dir, exclude_dirs, exclude_exts, exclude_files, clear_dest_dir, silent)

        # Only keep the stats if files were actually copied
        if md_stats["files_copied"] > 0:
            all_stats.append(md_stats)
        # Remove the directory if no files were copied
        elif os.path.exists(md_dest_dir) and not os.listdir(md_dest_dir):
            try:
                os.rmdir(md_dest_dir)
                if not silent:
                    print(f"Removed empty directory: {md_dest_dir}")
            except OSError:
                pass

    # Merge stats and print overall summary
    merged_stats = merge_stats(all_stats)

    end_time = time.time()
    duration = end_time - start_time

    # Print overall summary if we have files and not in silent mode
    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("flattening", merged_stats, duration)

    return merged_stats


def deflatten_dir(flattened_dir, dest_dir, file_types=None, exclude_files=None, clear_dest_dir=False, silent=False):
    """
    Deflatten a directory for specified file types
    """
    if file_types is None:
        file_types = ["py", "js", "md"]

    # Combine default exclusions for files
    if exclude_files is None:
        exclude_files = list(set(DEFAULT_PYTHON_EXCLUDE_FILENAMES + DEFAULT_JS_EXCLUDE_FILENAMES + DEFAULT_MD_EXCLUDE_FILENAMES))

    all_stats = []
    start_time = time.time()

    # Process Python files
    if "py" in file_types:
        py_source_dir = os.path.join(flattened_dir, "py")
        if os.path.exists(py_source_dir) and os.listdir(py_source_dir):
            if not silent:
                print("\n================ PYTHON FILES ================\n")
            py_stats = deflatten_python_dir(py_source_dir, dest_dir, exclude_files, clear_dest_dir, silent)
            all_stats.append(py_stats)

    # Process JavaScript/TypeScript files
    if "js" in file_types:
        js_source_dir = os.path.join(flattened_dir, "jsts")
        if os.path.exists(js_source_dir) and os.listdir(js_source_dir):
            if not silent:
                print("\n============= JAVASCRIPT FILES ==============\n")
            js_stats = deflatten_js_dir(js_source_dir, dest_dir, exclude_files, clear_dest_dir, silent)
            all_stats.append(js_stats)

    # Process Markdown files
    if "md" in file_types:
        md_source_dir = os.path.join(flattened_dir, "md")
        if os.path.exists(md_source_dir) and os.listdir(md_source_dir):
            if not silent:
                print("\n================ MARKDOWN FILES ================\n")
            md_stats = deflatten_md_dir(md_source_dir, dest_dir, exclude_files, clear_dest_dir, silent)
            all_stats.append(md_stats)

    # Merge stats and print overall summary
    merged_stats = merge_stats(all_stats)

    end_time = time.time()
    duration = end_time - start_time

    # Print overall summary if we have files and not in silent mode
    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("deflatten", merged_stats, duration)

    return merged_stats


def main():
    parser = argparse.ArgumentParser(description="Flatten, deflatten, or bundle a directory of Python, JavaScript, TypeScript, and Markdown files.")

    # Support both positional and named arguments
    src_group = parser.add_argument_group('source')
    src_group.add_argument("src_pos", nargs="?", help="Source directory path (positional)")
    src_group.add_argument("--src", dest="src_named", help="Source directory path (named)")

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument("dest_pos", nargs="?", help="Destination directory or file path (positional)")
    dest_group.add_argument("--dest", dest="dest_named", help="Destination directory or file path (named)")

    # File type options
    parser.add_argument("--file-types",
                        nargs="+",
                        choices=["py", "js", "md"],
                        default=["py", "js", "md"],
                        help="File types to process: 'py' for Python, 'js' for JavaScript/TypeScript, 'md' for Markdown (default: all)")

    # Exclusion options
    parser.add_argument("--exclude-dirs",
                        nargs="+",
                        help="Directory names to exclude")
    parser.add_argument("--exclude-extensions",
                        nargs="+",
                        help="File extensions to exclude")
    parser.add_argument("--exclude-files",
                        nargs="+",
                        help="Specific filenames to exclude")

    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument("--deflatten",
                                 action="store_true",
                                 help="Deflatten the directory instead of flattening (default: False)")
    operation_group.add_argument("--bundle",
                                 action="store_true",
                                 help="Bundle files into a single text file (default: False)")

    parser.add_argument("--clear-dest-dir",
                        action="store_true",
                        help="Clear the destination directory before copying (default: False)")
    parser.add_argument('--no-log',
                        action='store_true',
                        help="Suppress all output logs.")

    args = parser.parse_args()

    # Get source and destination
    source_dir = args.src_named if args.src_named else args.src_pos
    dest_path = args.dest_named if args.dest_named else args.dest_pos

    if not source_dir or not dest_path:
        parser.print_help()
        print("\nError: Both source and destination are required.")
        return 1

    # Set default exclude directories and extensions based on file types
    exclude_dirs = args.exclude_dirs
    exclude_exts = args.exclude_extensions
    exclude_files = args.exclude_files

    # If no custom exclusions provided, use defaults from all handlers
    if exclude_dirs is None:
        exclude_dirs = list(set(DEFAULT_PYTHON_EXCLUDE_DIRS + DEFAULT_JS_EXCLUDE_DIRS + DEFAULT_MD_EXCLUDE_DIRS))

    if exclude_exts is None:
        exclude_exts = list(set(DEFAULT_PYTHON_EXCLUDE_EXTENSIONS + DEFAULT_JS_EXCLUDE_EXTENSIONS + DEFAULT_MD_EXCLUDE_EXTENSIONS))

    if exclude_files is None:
        exclude_files = list(set(DEFAULT_PYTHON_EXCLUDE_FILENAMES + DEFAULT_JS_EXCLUDE_FILENAMES + DEFAULT_MD_EXCLUDE_FILENAMES))

    try:
        if args.deflatten:
            stats = deflatten_dir(source_dir, dest_path, args.file_types, exclude_files, args.clear_dest_dir, args.no_log)
        elif args.bundle:
            stats = bundle_files(source_dir, dest_path, args.file_types, exclude_dirs, exclude_exts, exclude_files, args.no_log)
        else:
            stats = flatten_dir(source_dir, dest_path, args.file_types, exclude_dirs, exclude_exts, exclude_files, args.clear_dest_dir, args.no_log)

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
