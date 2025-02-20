import os
import shutil
import argparse


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


def flatten_dir(source_dir, destination_dir, exclude_dirs=None, exclude_extensions=None):
    """
    Flattens the folder structure by copying all .py files into a single destination directory.
    Files are prefixed with their parent directory names separated by double underscores.

    :param source_dir: Path to the source directory
    :param destination_dir: Path to the destination directory
    :param exclude_dirs: List of directory names to exclude (default: DEFAULT_EXCLUDE_DIRS)
    :param exclude_extensions: List of file extensions to exclude (default: DEFAULT_EXCLUDE_EXTENSIONS)
    """

    # Set default values for exclude_dirs and exclude_extensions if not provided
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_extensions = exclude_extensions or DEFAULT_EXCLUDE_EXTENSIONS

    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    for root, dirs, files in os.walk(source_dir):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            # Filter Python files based on exclude_extensions
            if file.endswith(".py") and not any(file.endswith(ext) for ext in exclude_extensions):
                source_file = os.path.join(root, file)

                # Get the relative path components after the source directory
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]

                # Create the new filename with directory prefixes
                if path_parts:
                    new_filename = "__".join(path_parts + [file])
                else:
                    new_filename = file

                destination_file = os.path.join(destination_dir, new_filename)

                # Generate a unique filename if the file already exists in the destination
                unique_destination_file = get_unique_filename(destination_file)

                shutil.copy2(source_file, unique_destination_file)
                print(f"Copied: {source_file} -> {unique_destination_file}")


def deflatten_dir(flattened_dir, destination_dir):
    """
    Reverts the flattening process by recreating the original directory structure
    based on the file names in the flattened directory.

    :param flattened_dir: Path to the flattened directory
    :param destination_dir: Path to the destination directory
    """

    for file in os.listdir(flattened_dir):
        if file.endswith(".py"):
            flattened_file = os.path.join(flattened_dir, file)

            # Get the original directory structure from the file name
            path_parts = file.split("__")
            original_file = path_parts[-1]
            original_dir = os.path.join(destination_dir, *path_parts[:-1])

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
    parser.add_argument("--src",
                        required=True,
                        help="Source directory path")
    parser.add_argument("--dest",
                        required=True,
                        help="Destination directory path")
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

    args = parser.parse_args()

    try:
        if args.deflatten:
            deflatten_dir(args.src, args.dest)
        else:
            flatten_dir(args.src, args.dest, args.exclude_dirs, args.exclude_extensions)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    main()
