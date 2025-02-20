import os
import shutil
import argparse


DEFAULT_EXCLUDES = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv", ".pyc", ".pyo"]


def flatten_dir(source_dir, destination_dir, include_init=False, exclude=None):
    """
    Flattens the folder structure by copying all .py files into a single destination directory.
    Files are prefixed with their parent directory names separated by double underscores.

    :param source_dir: Path to the source directory
    :param destination_dir: Path to the destination directory
    :param include_init: Whether to include __init__.py files (default: False)
    :param exclude: List of directory names to exclude (default: DEFAULT_EXCLUDES)
    """

    # Set default values for exclude if not provided
    exclude = exclude or DEFAULT_EXCLUDES

    # Clear the destination directory if it exists
    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)
    os.makedirs(destination_dir)

    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    for root, dirs, files in os.walk(source_dir):
        # Exclude specified directories
        dirs[:] = [d for d in dirs if d not in exclude]

        for file in files:
            # Filter Python files based on include_init parameter and exclude specified extensions
            if file.endswith(".py") and file not in exclude:
                if not include_init and file == "__init__.py":
                    continue

                source_file = os.path.join(root, file)

                # Get the relative path components after the source directory
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]

                # Create the new filename with directory prefixes
                if path_parts:
                    new_filename = "__".join(path_parts + [file])
                else:
                    new_filename = file

                destination_file = os.path.join(destination_dir, new_filename)

                # Rename the file if it already exists in the destination
                counter = 1
                original_dest_file = destination_file
                while os.path.exists(destination_file):
                    name, ext = os.path.splitext(original_dest_file)
                    destination_file = f"{name}_{counter}{ext}"
                    counter += 1

                shutil.copy2(source_file, destination_file)
                print(f"Copied: {source_file} -> {destination_file}")


def deflatten_dir(flattened_dir, destination_dir):
    """
    Reverts the flattening process by recreating the original directory structure
    based on the file names in the flattened directory.

    :param flattened_dir: Path to the flattened directory
    :param destination_dir: Path to the destination directory
    """

    # Clear the destination directory if it exists
    if os.path.exists(destination_dir):
        shutil.rmtree(destination_dir)
    os.makedirs(destination_dir)

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
            shutil.copy2(flattened_file, destination_file)
            print(f"Copied: {flattened_file} -> {destination_file}")


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
    parser.add_argument("--include-init",
                        action="store_true",
                        help="Include __init__.py files in the flattening process (default: False)")
    parser.add_argument("--exclude",
                        nargs="+",
                        default=[".idea", ".venv", ".vscode"],
                        help="Directory names to exclude (default: \"__pycache__\", \".git\", \".idea\", \".vscode\", "
                             "\".venv\", \"venv\", \".pyc\", \".pyo\")")
    parser.add_argument("--deflatten",
                        action="store_true",
                        help="Deflatten the directory instead of flattening (default: False)")

    args = parser.parse_args()

    try:
        if args.deflatten:
            deflatten_dir(args.src, args.dest)
        else:
            flatten_dir(args.src, args.dest, args.include_init, args.exclude)
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 1
    return 0


if __name__ == "__main__":
    main()
