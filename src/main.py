import os
import shutil
import argparse
import sys


DEFAULT_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv"]
DEFAULT_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]


def get_unique_filename(destination_file):
    """
    Generates a unique filename by appending a counter if the file already exists.

    :param destination_file: The original destination file path
    :return: The unique file path
    """
    counter = 2
    name, ext = os.path.splitext(destination_file)
    unique_destination_file = destination_file

    while os.path.exists(unique_destination_file):
        unique_destination_file = f"{name}_{counter}{ext}"
        counter += 1

    return unique_destination_file


def flatten_dir(source_dir, dest_dir, exclude_dirs=None, exclude_exts=None, clear_dest_dir=False):
    """
    Flattens the folder structure by copying all .py files into a single destination directory.
    Files are prefixed with their parent directory names separated by double underscores.

    :param source_dir: Path to the source directory
    :param dest_dir: Path to the destination directory
    :param exclude_dirs: List of directory names to exclude (default: DEFAULT_EXCLUDE_DIRS)
    :param exclude_exts: List of file extensions to exclude (default: DEFAULT_EXCLUDE_EXTENSIONS)
    :param clear_dest_dir: Whether to clear the destination directory before copying (default: False)
    """

    # Set default values for exclude_dirs and exclude_extensions if not provided
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_exts = exclude_exts or DEFAULT_EXCLUDE_EXTENSIONS

    # Convert to absolute paths to avoid issues with relative paths
    source_dir = os.path.abspath(source_dir)
    dest_dir = os.path.abspath(dest_dir)

    if clear_dest_dir:
        # Clear the destination directory if it exists
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

    os.makedirs(dest_dir, exist_ok=True)

    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    for root, dirs, files in os.walk(source_dir):
        # Exclude specified directories and the destination directory itself
        dirs[:] = [
            d for d in dirs
            if d not in exclude_dirs and os.path.abspath(os.path.join(root, d)) != dest_dir
        ]

        for file in files:
            # Filter Python files based on exclude_extensions
            if file.endswith(".py") and not any(file.endswith(ext) for ext in exclude_exts):
                source_file = os.path.join(root, file)

                # Get the relative path components after the source directory
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]

                # Create the new filename with directory prefixes
                if path_parts:
                    new_filename = "___".join(path_parts + [file])
                else:
                    new_filename = file

                destination_file = os.path.join(dest_dir, new_filename)

                # Generate a unique filename if the file already exists in the destination
                unique_destination_file = get_unique_filename(destination_file)

                shutil.copy2(source_file, unique_destination_file)
                print(f"Copied: {source_file} -> {unique_destination_file}")


def deflatten_dir(flattened_dir, dest_dir, clear_dest_dir=False):
    """
    Reverts the flattening process by recreating the original directory structure
    based on the file names in the flattened directory.

    :param flattened_dir: Path to the flattened directory
    :param dest_dir: Path to the destination directory
    :param clear_dest_dir: Whether to clear the destination directory before copying (default: False)
    """
    # Convert to absolute paths to avoid issues with relative paths
    flattened_dir = os.path.abspath(flattened_dir)
    dest_dir = os.path.abspath(dest_dir)

    if clear_dest_dir:
        # Clear the destination directory if it exists
        if os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

    os.makedirs(dest_dir, exist_ok=True)

    for file in os.listdir(flattened_dir):
        if file.endswith(".py"):
            flattened_file = os.path.join(flattened_dir, file)

            # Get the original directory structure from the file name
            path_parts = file.split("___")
            original_file = path_parts[-1]
            original_dir = os.path.join(dest_dir, *path_parts[:-1])

            # Skip if the destination would be the source itself to avoid overwriting
            if os.path.abspath(original_dir).startswith(flattened_dir):
                print(f"Skipping to avoid overwriting source: {flattened_file}")
                continue

            # Create the original directory structure if it doesn't exist
            os.makedirs(original_dir, exist_ok=True)

            destination_file = os.path.join(original_dir, original_file)

            # Generate a unique filename if the file already exists in the destination
            unique_destination_file = get_unique_filename(destination_file)

            shutil.copy2(flattened_file, unique_destination_file)
            print(f"Copied: {flattened_file} -> {unique_destination_file}")


def main():
    parser = argparse.ArgumentParser(
        description="Flatten or deflatten a directory of Python files."
    )

    # Make both positional and named arguments accept the same parameters
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

    args = parser.parse_args()

    # Determine source and destination directories
    source_dir = args.src_named if args.src_named else args.src_pos
    dest_dir = args.dest_named if args.dest_named else args.dest_pos

    if not source_dir or not dest_dir:
        parser.print_help()
        print("\nError: Both source and destination directories are required.")
        return 1

    try:
        if args.deflatten:
            deflatten_dir(source_dir, dest_dir, args.clear_dest_dir)
        else:
            flatten_dir(source_dir, dest_dir, args.exclude_dirs, args.exclude_extensions, args.clear_dest_dir)
        print("Operation completed successfully.")
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
