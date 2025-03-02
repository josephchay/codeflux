import os
import argparse
import sys
from handlers.py_handler import (
    flatten_python_dir,
    deflatten_python_dir,
    DEFAULT_PYTHON_EXCLUDE_DIRS,
    DEFAULT_PYTHON_EXCLUDE_EXTENSIONS
)
from handlers.jsts_handler import (
    flatten_js_dir,
    deflatten_js_dir,
    DEFAULT_JS_EXCLUDE_DIRS,
    DEFAULT_JS_EXCLUDE_EXTENSIONS,
    JS_EXTENSIONS
)
from utils import get_relative_path


def merge_stats(stats_list):
    """Merge multiple statistics dictionaries into one"""
    merged_stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_copied": 0,
        "bytes_copied": 0,
        "skipped_files": 0,
        "max_nesting_level": 0,
        "dirs_created": 0
    }

    for stats in stats_list:
        for key, value in stats.items():
            if key in merged_stats:
                merged_stats[key] += value
                # For max_nesting_level, keep the maximum value
                if key == "max_nesting_level":
                    merged_stats[key] = max(merged_stats[key], value)

    return merged_stats


def flatten_dir(source_dir, dest_dir, file_types=None, exclude_dirs=None, exclude_exts=None, clear_dest_dir=False,
                silent=False):
    """
    Flatten a directory structure for specified file types
    """
    if file_types is None:
        file_types = ["py", "js"]

    all_stats = []

    # Process Python files
    if "py" in file_types:
        py_dest_dir = os.path.join(dest_dir, "py")
        if not silent:
            print("\n================ PYTHON FILES ================\n")
        py_stats = flatten_python_dir(source_dir, py_dest_dir, exclude_dirs, exclude_exts, clear_dest_dir, silent)

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
        js_stats = flatten_js_dir(source_dir, js_dest_dir, exclude_dirs, exclude_exts, clear_dest_dir, silent)

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

    # Merge and return all stats
    return merge_stats(all_stats)


def deflatten_dir(flattened_dir, dest_dir, file_types=None, clear_dest_dir=False, silent=False):
    """
    Deflatten a directory for specified file types
    """
    if file_types is None:
        file_types = ["py", "js"]

    all_stats = []

    # Process Python files
    if "py" in file_types:
        py_source_dir = os.path.join(flattened_dir, "py")
        if os.path.exists(py_source_dir) and os.listdir(py_source_dir):
            if not silent:
                print("\n================ PYTHON FILES ================\n")
            py_stats = deflatten_python_dir(py_source_dir, dest_dir, clear_dest_dir, silent)
            all_stats.append(py_stats)

    # Process JavaScript/TypeScript files
    if "js" in file_types:
        js_source_dir = os.path.join(flattened_dir, "jsts")
        if os.path.exists(js_source_dir) and os.listdir(js_source_dir):
            if not silent:
                print("\n============= JAVASCRIPT FILES ==============\n")
            js_stats = deflatten_js_dir(js_source_dir, dest_dir, clear_dest_dir, silent)
            all_stats.append(js_stats)

    # Merge and return all stats
    return merge_stats(all_stats)


def main():
    parser = argparse.ArgumentParser(
        description="Flatten or deflatten a directory of Python, JavaScript, and TypeScript files."
    )

    # Support both positional and named arguments
    src_group = parser.add_argument_group('source')
    src_group.add_argument("src_pos", nargs="?", help="Source directory path (positional)")
    src_group.add_argument("--src", dest="src_named", help="Source directory path (named)")

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument("dest_pos", nargs="?", help="Destination directory path (positional)")
    dest_group.add_argument("--dest", dest="dest_named", help="Destination directory path (named)")

    # File type options
    parser.add_argument("--file-types",
                        nargs="+",
                        choices=["py", "js"],
                        default=["py", "js"],
                        help="File types to process: 'py' for Python, 'js' for JavaScript/TypeScript (default: both)")

    # Exclusion options
    parser.add_argument("--exclude-dirs",
                        nargs="+",
                        help="Directory names to exclude")
    parser.add_argument("--exclude-extensions",
                        nargs="+",
                        help="File extensions to exclude")

    # Operation options
    parser.add_argument("--deflatten",
                        action="store_true",
                        help="Deflatten the directory instead of flattening (default: False)")
    parser.add_argument("--clear-dest-dir",
                        action="store_true",
                        help="Clear the destination directory before copying (default: False)")
    parser.add_argument('--no-log',
                        action='store_true',
                        help="Suppress all output logs.")

    args = parser.parse_args()

    # Get source and destination
    source_dir = args.src_named if args.src_named else args.src_pos
    dest_dir = args.dest_named if args.dest_named else args.dest_pos

    if not source_dir or not dest_dir:
        parser.print_help()
        print("\nError: Both source and destination directories are required.")
        return 1

    # Set default exclude directories and extensions based on file types
    exclude_dirs = args.exclude_dirs
    exclude_exts = args.exclude_extensions

    # If no custom exclusions provided, use defaults from both handlers
    if exclude_dirs is None:
        exclude_dirs = list(set(DEFAULT_PYTHON_EXCLUDE_DIRS + DEFAULT_JS_EXCLUDE_DIRS))

    if exclude_exts is None:
        exclude_exts = list(set(DEFAULT_PYTHON_EXCLUDE_EXTENSIONS + DEFAULT_JS_EXCLUDE_EXTENSIONS))

    try:
        if args.deflatten:
            stats = deflatten_dir(source_dir, dest_dir, args.file_types, args.clear_dest_dir, args.no_log)
        else:
            stats = flatten_dir(source_dir, dest_dir, args.file_types, exclude_dirs, exclude_exts, args.clear_dest_dir, args.no_log)

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
