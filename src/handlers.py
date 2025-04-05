import os
import shutil
import time
import datetime

from constants import *
from utils import (
    get_unique_filename, print_stats, should_process_file,
    get_relative_path, is_timestamp_dir, minify_code, format_path
)


class FileExtHandler:
    def __init__(self, extensions, exclude_dirs, exclude_extensions, exclude_filenames):
        self.extensions = extensions
        self.default_exclude_dirs = exclude_dirs
        self.default_exclude_extensions = exclude_extensions
        self.default_exclude_filenames = exclude_filenames

    def flatten_dir(self, source_dir, dest_dir, exclude_dirs=None, exclude_exts=None,
                    exclude_files=None, include_dirs=None, include_exts=None, include_files=None,
                    clear_dest_dir=False, silent=False):
        source_dir = os.path.abspath(source_dir)
        dest_dir = os.path.abspath(dest_dir)

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
            print(f"Source: {format_path(source_dir)}")
            print(f"Destination: {format_path(dest_dir)}\n")
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

                    try:
                        shutil.copy2(source_file, unique_destination_file)
                        stats["files_copied"] += 1
                        stats["bytes_copied"] += os.path.getsize(source_file)

                        if not silent:
                            rel_source = get_relative_path(source_file)
                            rel_dest = get_relative_path(unique_destination_file)
                            print(f"{rel_source} → {rel_dest}")
                    except Exception as e:
                        error_msg = f"Error copying {file}: {str(e)}"
                        print(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    stats["skipped_files"] += 1

        if stats["files_copied"] == 0 and not silent:
            print(f"No files found to process in {source_dir}.")
            print(f"No files were copied to {dest_dir}.")
            print("\nNothing to do for this file type.")

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_FLATTEN, duration)

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
            print(f"Source: {format_path(flattened_dir)}")
            print(f"Destination: {format_path(dest_dir)}\n")
            print(f"Processing files: {', '.join(self.extensions)}...")
            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        if not os.path.exists(flattened_dir) or not os.listdir(flattened_dir):
            if not silent:
                print(f"Source directory {flattened_dir} does not exist or is empty.")
                print(f"No files to deflatten to {dest_dir}.")
                print("\nNothing to do for this file type.")

            end_time = time.time()
            duration = end_time - start_time

            if not silent:
                print_stats(stats, OPERATION_DEFLATTEN, duration)

            return stats

        for file in os.listdir(flattened_dir):
            stats["total_files_processed"] += 1
            original_filename = file.split("___")[-1]

            # Check if it's a file type this handler processes
            is_target_ext = any(file.lower().endswith(ext) for ext in self.extensions)
            if not is_target_ext:
                stats["skipped_files"] += 1
                continue

            should_include = True
            if include_exts:
                is_included_ext = any(original_filename.lower().endswith(ext) for ext in include_exts)
                if not is_included_ext:
                    should_include = False
            if exclude_files and original_filename in exclude_files:
                should_include = False
            if include_dirs:
                path_parts = file.split("___")[:-1]  # Get directory parts
                if not any(part in include_dirs for part in path_parts):
                    should_include = False
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
                print(f"Skipping to avoid overwriting source: {flattened_file}")
                stats["skipped_files"] += 1
                continue

            if not os.path.exists(original_dir):
                try:
                    os.makedirs(original_dir, exist_ok=True)
                    stats["dirs_created"] += 1
                except Exception as e:
                    error_msg = f"Error creating directory {original_dir}: {str(e)}"
                    print(error_msg)
                    raise RuntimeError(error_msg)

            destination_file = os.path.join(original_dir, original_file)
            unique_destination_file = get_unique_filename(destination_file)

            try:
                shutil.copy2(flattened_file, unique_destination_file)
                stats["files_copied"] += 1
                stats["bytes_copied"] += os.path.getsize(flattened_file)

                if not silent:
                    rel_source = get_relative_path(flattened_file)
                    rel_dest = get_relative_path(unique_destination_file)
                    print(f"{rel_source} → {rel_dest}")
            except Exception as e:
                error_msg = f"Error copying {file}: {str(e)}"
                print(error_msg)
                raise RuntimeError(error_msg)

        if stats["files_copied"] == 0 and not silent:
            print(f"No files found to process in {flattened_dir}.")
            print(f"No files were copied to {dest_dir}.")
            print("\nNothing to do for this file type.")

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_DEFLATTEN, duration)

        return stats

    def minify_dir(self, source_dir, dest_dir, exclude_dirs=None, exclude_exts=None,
                   exclude_files=None, include_dirs=None, include_exts=None, include_files=None,
                   clear_dest_dir=False, silent=False):
        source_dir = os.path.abspath(source_dir)
        dest_dir = os.path.abspath(dest_dir)

        # Make sure base output directory isn't included in directory exclusion
        base_dir = os.path.abspath(os.path.join(os.getcwd(), "codebundle"))
        if base_dir not in exclude_dirs and exclude_dirs is not None:
            exclude_dirs.append(base_dir)

        # Stats tracking
        stats = {
            "total_files_processed": 0,
            "dirs_traversed": 0,
            "files_copied": 0,
            "files_minified": 0,
            "bytes_original": 0,
            "bytes_minified": 0,
            "skipped_files": 0,
            "max_nesting_level": 0
        }

        if clear_dest_dir and os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

        start_time = time.time()

        if not silent:
            print(f"Source: {format_path(source_dir)}")
            print(f"Destination: {format_path(dest_dir)}\n")
            print(f"Processing files: {', '.join(self.extensions)}...")
            print(f"Minification: Using python-minifier for Python files and JSON compression for JSON files")

            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        # Flag to track if any files were found
        files_found = False

        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level for stats
            current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            # Process directory inclusion/exclusion
            if include_dirs:
                rel_dir = os.path.relpath(root, source_dir)
                rel_dir_parts = rel_dir.split(os.sep)
                if not any(part in include_dirs for part in rel_dir_parts) and rel_dir != '.':
                    dirs[:] = []  # Skip this branch
                    continue

            # Skip the codebundle directory and timestamp directories
            dirs[:] = [
                d for d in dirs
                if not (d == "codebundle" or is_timestamp_dir(d)) and
                   d not in exclude_dirs and
                   os.path.abspath(os.path.join(root, d)) != dest_dir
            ]

            # Create corresponding directory in destination
            rel_path = os.path.relpath(root, source_dir)
            target_dir = os.path.join(dest_dir, rel_path) if rel_path != '.' else dest_dir
            os.makedirs(target_dir, exist_ok=True)

            for file in files:
                stats["total_files_processed"] += 1

                # Use centralized file filtering logic
                should_include = should_process_file(file, self.extensions, exclude_exts, exclude_files, include_exts, include_files)

                if should_include:
                    files_found = True
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)

                    # Get file extension
                    _, file_ext = os.path.splitext(file)

                    try:
                        # For text files that can be minified
                        with open(source_file, 'r', encoding='utf-8') as f:
                            content = f.read()
                            original_size = len(content)
                            stats["bytes_original"] += original_size

                        # Apply minification based on file type
                        if file_ext.lower() in ['.py', '.json', '.jsonl', '.geojson', '.json5', '.ndjson']:
                            minified_content = minify_code(content, file_ext)
                            minified_size = len(minified_content)

                            with open(target_file, 'w', encoding='utf-8') as f:
                                f.write(minified_content)

                            stats["files_minified"] += 1
                            stats["bytes_minified"] += minified_size
                            stats["files_copied"] += 1

                            if not silent:
                                rel_source = get_relative_path(source_file)
                                rel_dest = get_relative_path(target_file)
                                reduction = (1 - minified_size / max(original_size, 1)) * 100
                                print(f"{rel_source} → {rel_dest} (Size reduction: {reduction:.2f}%)")
                        else:
                            # Just copy non-minifiable files
                            shutil.copy2(source_file, target_file)
                            stats["files_copied"] += 1
                            stats["bytes_minified"] += original_size  # No reduction

                            if not silent:
                                rel_source = get_relative_path(source_file)
                                rel_dest = get_relative_path(target_file)
                                print(f"{rel_source} → {rel_dest}")

                    except UnicodeDecodeError:
                        # Handle binary files
                        shutil.copy2(source_file, target_file)
                        file_size = os.path.getsize(source_file)
                        stats["files_copied"] += 1
                        stats["bytes_original"] += file_size
                        stats["bytes_minified"] += file_size  # No reduction for binary files

                        if not silent:
                            rel_source = get_relative_path(source_file)
                            rel_dest = get_relative_path(target_file)
                            print(f"{rel_source} → {rel_dest} (binary file)")
                    except Exception as e:
                        # Report error to user
                        error_msg = f"Error processing {file}: {str(e)}"
                        print(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    stats["skipped_files"] += 1

        if not files_found and not silent:
            print(f"No files found to minify in {source_dir}.")
            print(f"No files were copied to {dest_dir}.")

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_MINIFY, duration)

        return stats

    def bundle_files(self, source_dir, output_file, exclude_dirs=None, exclude_exts=None,
                     exclude_files=None, include_dirs=None, include_exts=None, include_files=None, silent=False,
                     minify=False):
        source_dir = os.path.abspath(source_dir)
        output_file = os.path.abspath(output_file)
        output_filename = os.path.basename(output_file)
        if output_filename not in exclude_files and exclude_files is not None:
            exclude_files.append(output_filename)
        source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

        stats = {
            "total_files_processed": 0,
            "dirs_traversed": 0,
            "files_bundled": 0,
            "bytes_bundled": 0,
            "skipped_files": 0,
            "max_nesting_level": 0,
            "original_size": 0,
            "minified_size": 0
        }

        start_time = time.time()
        if not silent:
            print(f"Source: {format_path(source_dir)}")
            print(f"Destination: {format_path(output_file)}")
            if minify:
                print(f"Minification: Using python-minifier for Python files and JSON compression for JSON files")

        # Gather files to bundle
        files_to_bundle = []
        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1
            # Calculate nesting level
            current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)
            if include_dirs:
                # Only process specified directories
                rel_dir = os.path.relpath(root, source_dir)
                rel_dir_parts = rel_dir.split(os.sep)
                # Check if any part of the path is in include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_dir != '.':
                    dirs[:] = []  # Clear dirs to skip this branch
                    continue

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            for file in files:
                stats["total_files_processed"] += 1
                file_path = os.path.join(root, file)
                if os.path.abspath(file_path) == output_file:
                    stats["skipped_files"] += 1
                    continue

                should_include = should_process_file(file, self.extensions, exclude_exts, exclude_files, include_exts,
                                                     include_files)
                if should_include:
                    path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                    if path_parts:
                        formatted_path = "___".join(path_parts + [file])
                    else:
                        formatted_path = file

                    # Get file extension for language hint
                    _, file_ext = os.path.splitext(file)
                    if file_ext:
                        file_ext = file_ext[1:]  # Remove the dot

                    files_to_bundle.append({
                        'file_path': file_path,
                        'formatted_path': formatted_path,
                        'rel_path': os.path.relpath(file_path, source_dir),
                        'extension': file_ext,
                        'full_extension': file_ext
                    })
                else:
                    stats["skipped_files"] += 1

        # If no files were found to bundle
        if not files_to_bundle:
            if not silent:
                print(f"No files found to bundle in {source_dir}.")

            end_time = time.time()
            duration = end_time - start_time

            if not silent:
                print_stats(stats, OPERATION_BUNDLE if not minify else OPERATION_MINIFY_BUNDLE, duration)

            return stats

        # Sort files to group similar types together
        files_to_bundle.sort(key=lambda x: (x['extension'], x['formatted_path']))
        stats["original_size"] = sum(
            os.path.getsize(f['file_path']) for f in files_to_bundle if os.path.exists(f['file_path']))

        # Group files by extension for more efficient processing
        extension_groups = {}
        for file_info in files_to_bundle:
            ext = file_info['extension']
            if ext not in extension_groups:
                extension_groups[ext] = []

            extension_groups[ext].append(file_info)
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(f"# {os.path.basename(source_dir)} ({len(files_to_bundle)} files)\n")
            outfile.write(f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            if minify:
                outfile.write(
                    f"# Minification: Enabled (using python-minifier for Python files and JSON compression for JSON files)\n")
            outfile.write("\n")

            for ext, group_files in extension_groups.items():
                if group_files:
                    outfile.write(f"## {ext.upper() or 'UNKNOWN'} FILES ({len(group_files)})\n\n")
                for file_info in group_files:
                    file_path = file_info['file_path']
                    formatted_path = file_info['formatted_path']
                    file_extension = '.' + file_info['full_extension'] if file_info['full_extension'] else ''

                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            original_content_size = len(content)

                        if not content.strip():
                            if not silent:
                                print(f"Skipped empty file: {formatted_path}")
                            stats["skipped_files"] += 1
                            continue

                        if minify:
                            minified_content = minify_code(content, file_extension)
                            stats["minified_size"] += len(minified_content)
                            content = minified_content

                        else:
                            stats["minified_size"] = 0  # Not using minification

                        outfile.write(f"`{formatted_path}`\n```\n")
                        outfile.write(content.rstrip())
                        outfile.write("\n```\n\n")
                        stats["files_bundled"] += 1
                        stats["bytes_bundled"] += len(content)

                        if not silent:
                            if minify and file_extension.lower() in ['.py', '.json', '.jsonl', '.geojson', '.json5', '.ndjson']:
                                reduction = (1 - len(content) / max(original_content_size, 1)) * 100
                                print(f"Bundled: {formatted_path} (Size reduction: {reduction:.2f}%)")
                            else:
                                print(f"Bundled: {formatted_path}")
                    except UnicodeDecodeError:
                        if not silent:
                            print(f"Skipped binary file: {formatted_path}")
                        stats["skipped_files"] += 1
                    except Exception as e:
                        error_msg = f"Error bundling {formatted_path}: {str(e)}"
                        print(error_msg)
                        raise RuntimeError(error_msg)

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_BUNDLE if not minify else OPERATION_MINIFY_BUNDLE, duration)

        return stats


class JavaScriptTypescriptHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=JSTS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSTS_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSTS_EXCLUDE_FILENAMES
        )


class MarkdownTextHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=MDTXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=MDTXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=MDTXT_EXCLUDE_FILENAMES
        )


class NotebookHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=NOTEBOOK_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOTEBOOK_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOTEBOOK_EXCLUDE_FILENAMES
        )


class PythonHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=PYTHON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PYTHON_EXCLUDE_EXTENSIONS,
            exclude_filenames=PYTHON_EXCLUDE_FILENAMES
        )


class YamlHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=YML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=YML_EXCLUDE_EXTENSIONS,
            exclude_filenames=YML_EXCLUDE_FILENAMES
        )


class ShellHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=SHELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SHELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=SHELL_EXCLUDE_FILENAMES
        )


class JsonHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=JSON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSON_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSON_EXCLUDE_FILENAMES
        )


HANDLERS = {
    "py": PythonHandler(),
    "ipynb": NotebookHandler(),
    "jsts": JavaScriptTypescriptHandler(),
    "mdtxt": MarkdownTextHandler(),
    "yml": YamlHandler(),
    "shell": ShellHandler(),
    "json": JsonHandler(),
}
