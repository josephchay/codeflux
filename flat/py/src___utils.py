import os


def get_unique_filename(destination_file):
    """
    Generate a unique filename if the destination file already exists
    by appending an incrementing counter
    """
    counter = 2
    name, ext = os.path.splitext(destination_file)
    unique_destination_file = destination_file

    while os.path.exists(unique_destination_file):
        unique_destination_file = f"{name}_{counter}{ext}"
        counter += 1

    return unique_destination_file


def get_relative_path(path, base_path):
    """Get the relative path from base_path to path"""
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        return path


def print_stats(operation_type, stats, duration):
    """Print statistics about the flattening/deflattening operation"""
    print(f"Time taken: {duration:.6f} seconds")

    # Processing stats section
    print("\n[INPUT PROCESSING]")
    if operation_type == "flattening":
        print(f"Directories scanned: {stats['dirs_traversed']}")
        print(f"Maximum nesting level: {stats['max_nesting_level']}")
    print(f"Total files scanned: {stats['total_files_processed']}")
    print(f"Files skipped: {stats['skipped_files']} (non-target or excluded)")

    # Output stats section
    print("\n[OUTPUT RESULT]")
    if operation_type == "deflatten":
        print(f"Directories created: {stats['dirs_created']}")
    print(f"Files in {operation_type} output: {stats['files_copied']}")
    print(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")
    print(f"Processing rate: {stats['files_copied'] / max(duration, 0.1):.2f} files/second")
    print("=" * 50)
