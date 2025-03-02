import os
import shutil
import time
from src.utils import get_unique_filename, get_relative_path, print_stats


# Default exclusions for Python files
DEFAULT_PYTHON_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv"]
DEFAULT_PYTHON_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]


def flatten_python_dir(source_dir, dest_dir, exclude_dirs=None, exclude_exts=None, clear_dest_dir=False, silent=False):
    """
    Flatten a directory structure of Python files into a single directory
    """
    # Set default values
    exclude_dirs = exclude_dirs or DEFAULT_PYTHON_EXCLUDE_DIRS
    exclude_exts = exclude_exts or DEFAULT_PYTHON_EXCLUDE_EXTENSIONS

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
        print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
        print(f"Destination: {get_relative_path(dest_dir, os.getcwd())}\n")
        print(f"Processing Python files (.py)...")

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
        print_stats("flattening", stats, duration)

    return stats


def deflatten_python_dir(flattened_dir, dest_dir, clear_dest_dir=False, silent=False):
    """
    Deflatten a directory of Python files back into a hierarchical structure
    """
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
        print(f"Source: {get_relative_path(flattened_dir, os.getcwd())}")
        print(f"Destination: {get_relative_path(dest_dir, os.getcwd())}\n")
        print(f"Processing Python files (.py)...")

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
        print_stats("deflatten", stats, duration)

    return stats
