import os
import shutil
import argparse
import sys
import time

DEFAULT_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv"]
DEFAULT_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]


def get_unique_filename(destination_file):
    counter = 2
    name, ext = os.path.splitext(destination_file)
    unique_destination_file = destination_file

    while os.path.exists(unique_destination_file):
        unique_destination_file = f"{name}_{counter}{ext}"
        counter += 1

    return unique_destination_file


def get_relative_path(path, base_path):
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        return path


def flatten_dir(source_dir, dest_dir, exclude_dirs=None, exclude_exts=None, clear_dest_dir=False, silent=False):
    # Set default values
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_exts = exclude_exts or DEFAULT_EXCLUDE_EXTENSIONS

    # Convert to absolute paths
    source_dir = os.path.abspath(source_dir)
    dest_dir = os.path.abspath(dest_dir)

    # Stats tracking
    stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_copied": 0,
        "bytes_copied": 0,
        "skipped_files": 0,
        "max_nesting_level": 0
    }

    if clear_dest_dir and os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    os.makedirs(dest_dir, exist_ok=True)

    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))
    start_time = time.time()

    if not silent:
        print(f"Source: {source_dir}")
        print(f"Destination: {dest_dir}\n")

    for root, dirs, files in os.walk(source_dir):
        stats["dirs_traversed"] += 1

        # Calculate nesting level
        current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
        stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

        # Exclude directories
        dirs[:] = [
            d for d in dirs
            if d not in exclude_dirs and os.path.abspath(os.path.join(root, d)) != dest_dir
        ]

        for file in files:
            stats["total_files_processed"] += 1

            # Filter Python files
            if file.endswith(".py") and not any(file.endswith(ext) for ext in exclude_exts):
                source_file = os.path.join(root, file)

                # Get path components
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]

                # Create new filename
                if path_parts:
                    new_filename = "___".join(path_parts + [file])
                else:
                    new_filename = file

                destination_file = os.path.join(dest_dir, new_filename)
                unique_destination_file = get_unique_filename(destination_file)

                # Copy file
                shutil.copy2(source_file, unique_destination_file)
                stats["files_copied"] += 1
                stats["bytes_copied"] += os.path.getsize(source_file)

                # Print relative paths with arrow
                rel_source = get_relative_path(source_file, os.getcwd())
                rel_dest = get_relative_path(unique_destination_file, os.getcwd())
                if not silent:
                    print(f"{rel_source} → {rel_dest}")
            else:
                stats["skipped_files"] += 1

    end_time = time.time()
    duration = end_time - start_time

    if not silent:
        print("\n" + "=" * 50)
        print("FLATTENING COMPLETE")
        print("=" * 50)
        print(f"Time taken: {duration:.6f} seconds")
        print(f"Directories traversed: {stats['dirs_traversed']}")
        print(f"Maximum nesting level: {stats['max_nesting_level']}")
        print(f"Total files scanned: {stats['total_files_processed']}")
        print(f"Files copied: {stats['files_copied']}")
        print(f"Files skipped: {stats['skipped_files']}")
        print(f"Total data copied: {stats['bytes_copied'] / 1024:.2f} KB")
        print(f"Files per second: {stats['files_copied'] / max(duration, 0.1):.2f}")
        print("=" * 50)

    return stats


def deflatten_dir(flattened_dir, dest_dir, clear_dest_dir=False, silent=False):
    # Convert to absolute paths
    flattened_dir = os.path.abspath(flattened_dir)
    dest_dir = os.path.abspath(dest_dir)

    # Stats tracking
    stats = {
        "total_files_processed": 0,
        "dirs_created": 0,
        "files_copied": 0,
        "bytes_copied": 0,
        "skipped_files": 0
    }

    if clear_dest_dir and os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    os.makedirs(dest_dir, exist_ok=True)
    stats["dirs_created"] += 1

    start_time = time.time()

    if not silent:
        print(f"Source: {flattened_dir}")
        print(f"Destination: {dest_dir}")

    for file in os.listdir(flattened_dir):
        stats["total_files_processed"] += 1

        if file.endswith(".py"):
            flattened_file = os.path.join(flattened_dir, file)

            # Get original structure from filename
            path_parts = file.split("___")
            original_file = path_parts[-1]
            original_dir = os.path.join(dest_dir, *path_parts[:-1])

            # Skip if destination would overwrite source
            if os.path.abspath(original_dir).startswith(flattened_dir):
                print(f"Skipping to avoid overwriting source: {get_relative_path(flattened_file, os.getcwd())}")
                stats["skipped_files"] += 1
                continue

            # Create directory structure
            if not os.path.exists(original_dir):
                os.makedirs(original_dir, exist_ok=True)
                stats["dirs_created"] += 1

            destination_file = os.path.join(original_dir, original_file)
            unique_destination_file = get_unique_filename(destination_file)

            # Copy file
            shutil.copy2(flattened_file, unique_destination_file)
            stats["files_copied"] += 1
            stats["bytes_copied"] += os.path.getsize(flattened_file)

            # Print relative paths with arrow
            rel_source = get_relative_path(flattened_file, os.getcwd())
            rel_dest = get_relative_path(unique_destination_file, os.getcwd())
            if not silent:
                print(f"{rel_source} → {rel_dest}")
        else:
            stats["skipped_files"] += 1

    end_time = time.time()
    duration = end_time - start_time

    if not silent:
        print("\n" + "=" * 50)
        print("DEFLATTEN COMPLETE")
        print("=" * 50)
        print(f"Time taken: {duration:.6f} seconds")
        print(f"Directories created: {stats['dirs_created']}")
        print(f"Total files scanned: {stats['total_files_processed']}")
        print(f"Files copied: {stats['files_copied']}")
        print(f"Files skipped: {stats['skipped_files']}")
        print(f"Total data copied: {stats['bytes_copied'] / 1024:.2f} KB")
        print(f"Files per second: {stats['files_copied'] / max(duration, 0.1):.2f}")
        print("=" * 50)

    return stats


def main():
    parser = argparse.ArgumentParser(
        description="Flatten or deflatten a directory of Python files."
    )

    # Support both positional and named arguments
    src_group = parser.add_argument_group('source')
    src_group.add_argument("src_pos", nargs="?", help="Source directory path (positional)")
    src_group.add_argument("--src", dest="src_named", help="Source directory path (named)")

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument("dest_pos", nargs="?", help="Destination directory path (positional)")
    dest_group.add_argument("--dest", dest="dest_named", help="Destination directory path (named)")

    parser.add_argument("--exclude-dirs",
                        nargs="+",
                        default=DEFAULT_EXCLUDE_DIRS,
                        help="Directory names to exclude (default: \"__pycache__\", \".git\", "
                             "\".idea\", \".vscode\", \".venv\", \"venv\")")
    parser.add_argument("--exclude-extensions",
                        nargs="+",
                        default=DEFAULT_EXCLUDE_EXTENSIONS,
                        help="File extensions to exclude (default: \".pyc\", \".pyo\", \"__init__.py\")")
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

    try:
        if args.deflatten:
            stats = deflatten_dir(source_dir, dest_dir, args.clear_dest_dir)
        else:
            stats = flatten_dir(source_dir, dest_dir, args.exclude_dirs, args.exclude_extensions, args.clear_dest_dir)

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
