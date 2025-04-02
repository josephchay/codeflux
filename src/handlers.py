import os
import shutil
import time

from constants import *
from utils import get_relative_path, get_unique_filename, print_stats, should_process_file


class FileExtHandler:
    def __init__(self, extensions, exclude_dirs, exclude_extensions, exclude_filenames):
        self.extensions = extensions
        self.default_exclude_dirs = exclude_dirs
        self.default_exclude_extensions = exclude_extensions
        self.default_exclude_filenames = exclude_filenames

    def flatten_dir(self, source_dir, dest_dir, exclude_dirs=None, exclude_exts=None,
                    exclude_files=None, include_dirs=None, include_exts=None, include_files=None,
                    clear_dest_dir=False, silent=False):
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
            print(f"Processing files: {', '.join(self.extensions)}...")
            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            # Process directory inclusion/exclusion
            if include_dirs:
                # Check if any part of the current path matches the include dirs
                rel_dir = os.path.relpath(root, source_dir)
                rel_dir_parts = rel_dir.split(os.sep)
                # If none of the path parts are in include_dirs and we're not at root
                if not any(part in include_dirs for part in rel_dir_parts) and rel_dir != '.':
                    dirs[:] = []  # Skip this branch
                    continue

            # Exclude directories
            dirs[:] = [
                d for d in dirs
                if d not in exclude_dirs and os.path.abspath(os.path.join(root, d)) != dest_dir
            ]

            for file in files:
                stats["total_files_processed"] += 1

                if should_process_file(file, self.extensions, exclude_exts, exclude_files, include_exts, include_files):
                    source_file = os.path.join(root, file)
                    path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]

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
            print_stats("flatten", stats, duration)

        return stats

    def deflatten_dir(self, flattened_dir, dest_dir, exclude_files=None, include_dirs=None,
                      include_exts=None, include_files=None, clear_dest_dir=False, silent=False):
        flattened_dir = os.path.abspath(flattened_dir)
        dest_dir = os.path.abspath(dest_dir)

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
            print(f"Processing files: {', '.join(self.extensions)}...")
            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        for file in os.listdir(flattened_dir):
            stats["total_files_processed"] += 1
            original_filename = file.split("___")[-1]

            # Check if it's a file type this handler processes
            is_target_ext = any(file.lower().endswith(ext) for ext in self.extensions)
            if not is_target_ext:
                stats["skipped_files"] += 1
                continue

            # Check file inclusion/exclusion
            should_include = True

            # Check if the file extension should be included
            if include_exts:
                is_included_ext = any(original_filename.lower().endswith(ext) for ext in include_exts)
                if not is_included_ext:
                    should_include = False

            # Check if it should be excluded
            if exclude_files and original_filename in exclude_files:
                should_include = False

            # Check if the file is in an included directory
            if include_dirs:
                path_parts = file.split("___")[:-1]  # Get directory parts
                if not any(part in include_dirs for part in path_parts):
                    should_include = False

            # If include_files is specified, only include those files
            if include_files:
                should_include = original_filename in include_files

            if not should_include:
                stats["skipped_files"] += 1
                continue

            flattened_file = os.path.join(flattened_dir, file)
            path_parts = file.split("___")
            original_file = path_parts[-1]
            original_dir = os.path.join(dest_dir, *path_parts[:-1])

            if os.path.abspath(original_dir).startswith(flattened_dir):
                print(f"Skipping to avoid overwriting source: {get_relative_path(flattened_file, os.getcwd())}")
                stats["skipped_files"] += 1
                continue

            if not os.path.exists(original_dir):
                os.makedirs(original_dir, exist_ok=True)
                stats["dirs_created"] += 1

            destination_file = os.path.join(original_dir, original_file)
            unique_destination_file = get_unique_filename(destination_file)

            shutil.copy2(flattened_file, unique_destination_file)
            stats["files_copied"] += 1
            stats["bytes_copied"] += os.path.getsize(flattened_file)

            rel_source = get_relative_path(flattened_file, os.getcwd())
            rel_dest = get_relative_path(unique_destination_file, os.getcwd())
            if not silent:
                print(f"{rel_source} → {rel_dest}")

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats("deflatten", stats, duration)

        return stats


class JavaScriptTypescriptHandler(FileExtHandler):
    """Handler for JavaScript/TypeScript files"""
    def __init__(self):
        super().__init__(
            extensions=JSTS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSTS_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSTS_EXCLUDE_FILENAMES
        )


class MarkdownTextHandler(FileExtHandler):
    """Handler for Markdown files"""
    def __init__(self):
        super().__init__(
            extensions=MDTXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=MDTXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=MDTXT_EXCLUDE_FILENAMES
        )


class NotebookHandler(FileExtHandler):
    """Handler for Python Notebook files"""
    def __init__(self):
        super().__init__(
            extensions=NOTEBOOK_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOTEBOOK_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOTEBOOK_EXCLUDE_FILENAMES
        )


class PythonHandler(FileExtHandler):
    """Handler for Python files"""
    def __init__(self):
        super().__init__(
            extensions=PYTHON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PYTHON_EXCLUDE_EXTENSIONS,
            exclude_filenames=PYTHON_EXCLUDE_FILENAMES
        )


class YamlHandler(FileExtHandler):
    """Handler for YAML files"""
    def __init__(self):
        super().__init__(
            extensions=YML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=YML_EXCLUDE_EXTENSIONS,
            exclude_filenames=YML_EXCLUDE_FILENAMES
        )


class ShellHandler(FileExtHandler):
    """Handler for Shell script files"""
    def __init__(self):
        super().__init__(
            extensions=SHELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SHELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=SHELL_EXCLUDE_FILENAMES
        )


HANDLERS = {
    "py": PythonHandler(),
    "ipynb": NotebookHandler(),
    "jsts": JavaScriptTypescriptHandler(),
    "mdtxt": MarkdownTextHandler(),
    "yml": YamlHandler(),
    "shell": ShellHandler(),
}
