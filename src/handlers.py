import csv
import difflib
import hashlib
import os
import re
import shutil
import stat
import subprocess
import time
import datetime

from constants import *
from helpers.latex import load_acronyms_csv, make_acronyms_tex_from_csv
from minify import minify_code
from snipping import apply_snippet_filter
from ui.table import format_file_table
from utils import get_unique_filename, print_stats, should_process_file, get_relpath


class FileExtHandler:
    def __init__(self, extensions, exclude_dirs, exclude_extensions, exclude_filenames):
        self.extensions = extensions
        self.default_exclude_dirs = exclude_dirs
        self.default_exclude_extensions = exclude_extensions
        self.default_exclude_filenames = exclude_filenames

    def handles_file(self, filename):
        """Check if this handler should process the given filename based on its extension."""
        return any(filename.lower().endswith(ext.lower()) for ext in self.extensions)

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

        files_info = []  # For table output

        if clear_dest_dir and os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        os.makedirs(dest_dir, exist_ok=True)

        source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))
        start_time = time.time()

        if not silent:
            if self.extensions == [""]:
                print("Processing files with no extension...\n")
            elif self.extensions:
                print(f"Processing files: {', '.join(self.extensions)}...\n")

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
                source_file = os.path.join(root, file)
                rel_path = os.path.relpath(source_file, source_dir)

                # Only process files that match this handler's extensions
                is_handler_file_type = self.handles_file(file)
                if not is_handler_file_type:
                    stats["skipped_files"] += 1
                    continue

                # Apply additional file filters
                if should_process_file(file, self.extensions, exclude_exts, exclude_files, include_exts, include_files,
                                       file_rel_path=rel_path):
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
                        file_size = os.path.getsize(source_file)
                        stats["bytes_copied"] += file_size

                        if not silent:
                            # Create a relative path from the destination file to be displayed in the status
                            # This creates a clean path without the full output directory structure
                            dest_rel_path = os.path.relpath(unique_destination_file, os.path.dirname(dest_dir))

                            file_info = {
                                "file": get_relpath(source_file, source_dir),
                                "size": file_size,
                                "status": "Success"
                            }
                            files_info.append(file_info)
                    except Exception as e:
                        error_msg = f"Error copying {file}: {str(e)}"
                        print(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    stats["skipped_files"] += 1

        if not silent:
            if stats["files_copied"] == 0:
                print(f"No files found to process.")
                print(f"No files were copied.")
                print("\nNothing to do for this file type.")
            elif files_info:
                print("[FILES PROCESSED]")
                file_table = format_file_table(files_info, OPERATION_FLATTEN)
                print(file_table)

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

        files_info = []  # For table output

        if clear_dest_dir and os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)
        os.makedirs(dest_dir, exist_ok=True)
        stats["dirs_created"] += 1
        start_time = time.time()

        if not silent:
            if self.extensions == [""]:
                print("Processing files with no extension...\n")
            elif self.extensions:
                print(f"Processing files: {', '.join(self.extensions)}...\n")

            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        if not os.path.exists(flattened_dir) or not os.listdir(flattened_dir):
            if not silent:
                print(f"Source directory {get_relpath(flattened_dir)} does not exist or is empty.")
                print(f"No files to deflatten.")
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
            if not self.handles_file(original_filename):
                stats["skipped_files"] += 1
                continue

            path_parts = file.split("___")
            original_path = '/'.join(path_parts[:-1] + [original_filename]) if len(
                path_parts) > 1 else original_filename
            should_include = True

            if include_exts:
                is_included_ext = any(original_filename.lower().endswith(ext.lower()) for ext in include_exts)
                if not is_included_ext:
                    should_include = False

            if exclude_files:
                for exclude_pattern in exclude_files:
                    norm_exclude = exclude_pattern.replace('\\', '/')
                    norm_path = original_path.replace('\\', '/')
                    if norm_path.lower() == norm_exclude.lower() or norm_path.lower().endswith('/' + norm_exclude.lower()) or original_filename.lower() == norm_exclude.lower():
                        should_include = False
                        break

            if include_dirs:
                path_parts = file.split("___")[:-1]  # Get directory parts
                if not any(part in include_dirs for part in path_parts):
                    should_include = False

            if include_files:
                file_matches = False
                for include_file in include_files:
                    if original_filename.lower() == include_file.lower() or original_path.lower().endswith(include_file.lower()):
                        file_matches = True
                        break
                should_include = file_matches

            if not should_include:
                stats["skipped_files"] += 1
                continue

            flattened_file = os.path.join(flattened_dir, file)
            path_parts = file.split("___")
            original_file = path_parts[-1]
            original_dir = os.path.join(dest_dir, *path_parts[:-1])
            if os.path.abspath(original_dir).startswith(flattened_dir):
                print(f"Skipping to avoid overwriting source: {get_relpath(flattened_file)}")
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
                file_size = os.path.getsize(flattened_file)
                stats["bytes_copied"] += file_size

                if not silent:
                    file_info = {
                        "file": get_relpath(flattened_file),
                        "size": file_size,
                        "status": "Success"
                    }
                    files_info.append(file_info)
            except Exception as e:
                error_msg = f"Error copying {file}: {str(e)}"
                print(error_msg)
                raise RuntimeError(error_msg)

        if not silent:
            if stats["files_copied"] == 0:
                print(f"No files found to process.")
                print(f"No files were copied.")
            elif files_info:
                print("[FILES PROCESSED]")
                file_table = format_file_table(files_info, OPERATION_DEFLATTEN)
                print(file_table)

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_DEFLATTEN, duration)

        return stats

    def minify_dir(self, source_dir, output_dir, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                   include_dirs=None, include_exts=None, include_files=None, clear_dest_dir=False, silent=False,
                   continue_on_error=False):
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(output_dir)
        source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

        if output_dir == source_dir:
            raise ValueError("Source and output directories cannot be the same for minify operations")
        if clear_dest_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir)

        os.makedirs(output_dir, exist_ok=True)

        stats = {
            "total_files_processed": 0,
            "dirs_traversed": 0,
            "files_copied": 0,
            "files_minified": 0,
            "bytes_copied": 0,
            "bytes_original": 0,
            "bytes_minified": 0,
            "skipped_files": 0,
            "empty_files": 0,
            "failed_minifications": 0,
            "max_nesting_level": 0
        }

        files_info = []  # For table output
        files_with_warnings = {}  # Track files with warnings
        start_time = time.time()
        files_found = False

        def is_text_markdown_file(filename):
            """Check if a file is a text or markdown file that shouldn't attempt minification."""
            text_markdown_exts = ['.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.mdwn', '.mdtxt', '.mdtext', '.txt', '.rst']
            return any(filename.lower().endswith(ext) for ext in text_markdown_exts)

        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            if include_dirs:
                # Only process specified directories
                rel_dir_parts = rel_path.split(os.sep)
                # Check if any part of the path is in include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []  # Clear dirs to skip this branch
                    continue

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Create corresponding output directory
            rel_output_path = os.path.relpath(root, source_dir)
            output_path = os.path.normpath(os.path.join(output_dir, rel_output_path))
            os.makedirs(output_path, exist_ok=True)

            for file in files:
                stats["total_files_processed"] += 1
                file_path = os.path.join(root, file)
                output_file_path = os.path.join(output_path, file)

                # Skip if source and destination are the same
                if os.path.abspath(file_path) == os.path.abspath(output_file_path):
                    stats["skipped_files"] += 1
                    continue

                # Skip files not handled by this handler
                if not self.handles_file(file):
                    stats["skipped_files"] += 1
                    continue

                # Apply additional filters
                rel_file_path = os.path.relpath(file_path, source_dir)
                should_include = should_process_file(file, self.extensions, exclude_exts, exclude_files, include_exts,
                                                     include_files, file_rel_path=rel_file_path)
                if should_include:
                    files_found = True

                    # Check if file exists and has size
                    if os.path.getsize(file_path) == 0:
                        # Handle empty file
                        shutil.copy2(file_path, output_file_path)
                        stats["files_copied"] += 1
                        stats["empty_files"] += 1

                        if not silent:
                            file_info = {
                                "file": rel_file_path,
                                "size": 0,
                                "status": f"Skipped (empty file)",
                                "original_size": 0,
                                "reduction": 0.0,
                                "warnings": ""
                            }
                            files_info.append(file_info)
                        continue

                    try:
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()

                            # Skip empty files with whitespace only
                            if not content.strip():
                                shutil.copy2(file_path, output_file_path)
                                stats["files_copied"] += 1
                                stats["empty_files"] += 1
                                file_size = len(content.encode('utf-8'))

                                if not silent:
                                    file_info = {
                                        "file": rel_file_path,
                                        "size": file_size,
                                        "status": f"Skipped (empty file)",
                                        "original_size": file_size,
                                        "reduction": 0.0,
                                        "warnings": ""
                                    }
                                    files_info.append(file_info)
                                continue

                            # Using byte count for consistent size measurement
                            original_size = len(content.encode('utf-8'))
                            stats["bytes_original"] += original_size

                        _, ext = os.path.splitext(file)
                        ext_lower = ext.lower()

                        # Determine if this is a file type we shouldn't try to minify
                        is_text_md = is_text_markdown_file(file)

                        # For text/markdown files, just copy without attempting minification
                        if is_text_md:
                            shutil.copy2(file_path, output_file_path)
                            stats["files_copied"] += 1
                            file_size = original_size
                            stats["bytes_copied"] += file_size
                            stats["bytes_minified"] += file_size  # Count as minified size too

                            if not silent:
                                output_rel_path = os.path.join(rel_output_path, file).replace('\\', '/')
                                if rel_output_path == '.':
                                    output_rel_path = file

                                file_info = {
                                    "file": rel_file_path,
                                    "size": file_size,
                                    "status": f"Copied as-is",
                                    "original_size": file_size,
                                    "reduction": 0.0,
                                    "warnings": ""
                                }
                                files_info.append(file_info)
                            continue

                        try:
                            warning_message = None
                            if ext_lower.endswith('.py'):
                                # Common invalid escape sequences that trigger SyntaxWarnings
                                invalid_escapes = {'\\s': 'invalid escape sequence \\s',
                                                   '\\d': 'invalid escape sequence \\d',
                                                   '\\w': 'invalid escape sequence \\w',
                                                   '\\.': 'invalid escape sequence \\.',
                                                   '\\-': 'invalid escape sequence \\-',
                                                   '\\_': 'invalid escape sequence \\_'}
                                for invalid_escape, warning_text in invalid_escapes.items():
                                    if invalid_escape in content:
                                        warning_message = f"SyntaxWarning: {warning_text}"
                                        files_with_warnings[rel_file_path] = warning_message
                                        break

                            minified_content, minify_warning = minify_code(content, ext, continue_on_error)
                            if minify_warning:
                                files_with_warnings[rel_file_path] = minify_warning

                            # Check if minification was successful (content changed and returned value is not None)
                            if minified_content is not None and minified_content != content:
                                # Also using byte count for minified content
                                minified_size = len(minified_content.encode('utf-8'))
                                stats["bytes_minified"] += minified_size
                                stats["files_minified"] += 1
                            else:
                                # If content is unchanged or minified_content is None, use original size
                                minified_size = original_size
                                stats["bytes_minified"] += minified_size

                                # Only count as a failed minification if continue_on_error is True
                                # and the content is unchanged (could be due to error handling)
                                if continue_on_error and len(content.strip()) > 0:
                                    stats["failed_minifications"] += 1

                            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                                outfile.write(minified_content)

                            stats["files_copied"] += 1
                            stats["bytes_copied"] += minified_size

                            if not silent:
                                reduction = (1 - minified_size / max(original_size, 1)) * 100
                                # Use relative path for consistent output display
                                output_rel_path = os.path.relpath(output_file_path, output_dir).replace('\\', '/')

                                status = "Success"
                                if minified_size == original_size:
                                    if continue_on_error:
                                        status = "Copied as-is (no minification)"
                                    else:
                                        status = "Copied as-is"

                                # Add warning indicator if we found potential syntax warnings
                                if rel_file_path in files_with_warnings:
                                    status += " (warn:escapes)"

                                file_info = {
                                    "file": rel_file_path,
                                    "size": minified_size,
                                    "status": status,
                                    "original_size": original_size,
                                    "reduction": reduction,
                                    "warnings": files_with_warnings.get(rel_file_path, "")
                                }
                                files_info.append(file_info)
                        except Exception as e:
                            if continue_on_error:
                                # If we're continuing on error, copy the original content
                                shutil.copy2(file_path, output_file_path)
                                stats["files_copied"] += 1
                                stats["failed_minifications"] += 1
                                file_size = os.path.getsize(file_path)
                                stats["bytes_copied"] += file_size
                                stats["bytes_minified"] += file_size  # Count original size in minified bytes

                                if not silent:
                                    file_info = {
                                        "file": rel_file_path,
                                        "size": file_size,
                                        "status": f"Copied as-is (error)",
                                        "original_size": file_size,
                                        "reduction": 0.0,
                                        "warnings": ""
                                    }
                                    files_info.append(file_info)
                            else:
                                error_msg = f"Error minifying {file}: {str(e)}"
                                print(error_msg)
                                raise RuntimeError(error_msg)
                    except UnicodeDecodeError:
                        # Binary file, just copy it
                        shutil.copy2(file_path, output_file_path)
                        stats["files_copied"] += 1
                        file_size = os.path.getsize(file_path)
                        stats["bytes_original"] += file_size
                        stats["bytes_minified"] += file_size
                        stats["bytes_copied"] += file_size

                        if not silent:
                            file_info = {
                                "file": rel_file_path,
                                "size": file_size,
                                "status": f"Copied as-is (binary)",
                                "original_size": file_size,
                                "reduction": 0.0,
                                "warnings": ""
                            }
                            files_info.append(file_info)
                else:
                    stats["skipped_files"] += 1

        if not silent:
            if not files_found:
                print(f"No files found to minify.")
                print(f"No files were copied.")
            elif files_info:
                print("[FILES PROCESSED]")
                file_table = format_file_table(files_info, OPERATION_MINIFY)
                print(file_table)

                if stats["failed_minifications"] > 0 and continue_on_error:
                    print(f"\nNote: {stats['failed_minifications']} file(s) could not be minified and were copied as-is.")

            # Display warning summary if any warnings were found
            if files_with_warnings:
                print(f"\nNote: {len(files_with_warnings)} Python file(s) contain patterns that may generate syntax warnings.")
                print("These files are marked with '(warn:escapes)' in the status column.")

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_MINIFY, duration)

        return stats

    def bundle_files(self, source_dir, output_file, exclude_dirs=None, exclude_exts=None,
                     exclude_files=None, include_dirs=None, include_exts=None, include_files=None, silent=False,
                     minify=False, snippet=False, snippet_lines=50, snippet_start="top", snippet_context=5,
                     search_pattern=None, continue_on_error=False):
        source_dir = os.path.abspath(source_dir)
        output_file = os.path.abspath(output_file)
        output_filename = os.path.basename(output_file)
        if output_filename not in exclude_files and exclude_files is not None:
            exclude_files.append(output_filename)
        source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))
        files_with_warnings = {}

        stats = {
            "total_files_processed": 0,
            "dirs_traversed": 0,
            "files_bundled": 0,
            "bytes_bundled": 0,
            "skipped_files": 0,
            "max_nesting_level": 0,
            "original_size": 0,
            "minified_size": 0,
            "files_with_snippets": 0,
            "failed_minifications": 0,
        }
        files_info = []  # For table output
        start_time = time.time()

        def format_path_for_display(path):
            if "___" in path:
                parts = path.split("___")
                return "/".join(parts)
            return path

        # Gather files to bundle
        files_to_bundle = []
        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            # Process directory inclusion/exclusion
            if include_dirs:
                # Only process specified directories
                rel_dir_parts = rel_path.split(os.sep)
                # Check if any part of the path is in include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []  # Clear dirs to skip this branch
                    continue

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                stats["total_files_processed"] += 1
                file_path = os.path.join(root, file)

                # Skip output file
                if os.path.abspath(file_path) == output_file:
                    stats["skipped_files"] += 1
                    continue

                # Skip non-handled file types
                if not self.handles_file(file):
                    stats["skipped_files"] += 1
                    continue

                # Check if file should be included based on filters
                rel_path = os.path.relpath(file_path, source_dir)
                should_include = should_process_file(
                    file, self.extensions, exclude_exts, exclude_files, include_exts,
                    include_files, file_rel_path=rel_path
                )

                if should_include:
                    # Create path parts for formatted path (used in output)
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
                        'rel_path': rel_path,
                        'extension': file_ext.lower(),
                        'full_extension': file_ext
                    })
                else:
                    stats["skipped_files"] += 1

        if not files_to_bundle:
            if not silent:
                print(f"No files found to bundle.")

            end_time = time.time()
            duration = end_time - start_time

            if not silent:
                print_stats(stats, OPERATION_BUNDLE if not minify else OPERATION_MINIFY_BUNDLE, duration)

            return stats

        files_to_bundle.sort(key=lambda x: (x['extension'], x['formatted_path']))
        total_original_bytes = 0
        for file_info in files_to_bundle:
            file_path = file_info['file_path']
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_original_bytes += file_size

        stats["original_size"] = total_original_bytes

        # Group files by extension for more efficient processing
        extension_groups = {}
        for file_info in files_to_bundle:
            ext = file_info['extension']
            if ext not in extension_groups:
                extension_groups[ext] = []
            extension_groups[ext].append(file_info)

        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        total_minified_bytes = 0
        with open(output_file, 'w', encoding='utf-8') as outfile:
            outfile.write(f"# {os.path.basename(source_dir)} ({len(files_to_bundle)} files)\n")
            outfile.write(f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if snippet:
                outfile.write(f"# Snippet mode: {snippet_start.capitalize()} {snippet_lines} lines")
                if search_pattern:
                    outfile.write(f" with {snippet_context} context lines around '{search_pattern}'")
                outfile.write("\n")

            if minify:
                outfile.write(f"# Minification: Enabled ({MINIFICATION_DESCRIPTION})\n")
                if continue_on_error:
                    outfile.write(f"# Note: Continuing on minification errors (original content used for failed files)\n")

            # Process each extension group
            for ext, group_files in extension_groups.items():
                if group_files:
                    outfile.write(f"## {ext.upper() or 'UNKNOWN'} FILES ({len(group_files)})\n\n")

                    for file_info in group_files:
                        file_path = file_info['file_path']
                        formatted_path = file_info['formatted_path']
                        file_extension = '.' + file_info['full_extension'] if file_info['full_extension'] else ''
                        display_path = format_path_for_display(formatted_path)

                        try:
                            # First check if the file is a binary file
                            is_binary = False
                            try:
                                with open(file_path, 'r', encoding='utf-8') as test_file:
                                    test_file.read(1024)  # Try to read as text
                            except UnicodeDecodeError:
                                is_binary = True

                            if is_binary:
                                # Handle binary file - skip it with a message
                                stats["skipped_files"] += 1
                                if not silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": os.path.getsize(file_path),
                                        "status": "Skipped (binary file)"
                                    })
                                continue

                            # Proceed with text file
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                original_content_bytes = len(content.encode('utf-8'))

                            # Skip empty files
                            if not content.strip():
                                stats["skipped_files"] += 1
                                if not silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": 0,
                                        "status": "Skipped (empty file)"
                                    })
                                continue

                            # Handle snippets if enabled
                            is_truncated = False
                            original_lines = 0
                            filtered_lines = 0

                            if snippet:
                                try:
                                    content, filtered_lines, original_lines = apply_snippet_filter(
                                        content, snippet, snippet_lines, snippet_start,
                                        snippet_context, search_pattern
                                    )
                                    is_truncated = filtered_lines < original_lines
                                    if is_truncated:
                                        stats["files_with_snippets"] += 1
                                except Exception as e:
                                    if not silent:
                                        print(f"Warning: Failed to apply snippet filter to {display_path}: {str(e)}")
                                    content_lines = content.splitlines()
                                    original_lines = len(content_lines)
                                    filtered_lines = original_lines
                            else:
                                content_lines = content.splitlines()
                                original_lines = len(content_lines)
                                filtered_lines = original_lines

                            if minify:
                                try:
                                    warning_message = None
                                    if file_extension.lower().endswith('.py'):
                                        # Common invalid escape sequences that trigger SyntaxWarnings
                                        invalid_escapes = {'\\s': 'invalid escape sequence \\s',
                                                           '\\d': 'invalid escape sequence \\d',
                                                           '\\w': 'invalid escape sequence \\w',
                                                           '\\.': 'invalid escape sequence \\.',
                                                           '\\-': 'invalid escape sequence \\-',
                                                           '\\_': 'invalid escape sequence \\_'}
                                        for invalid_escape, warning_text in invalid_escapes.items():
                                            if invalid_escape in content:
                                                warning_message = f"SyntaxWarning: {warning_text}"
                                                files_with_warnings[display_path] = warning_message
                                                break

                                    minified_content, minify_warning = minify_code(content, file_extension, continue_on_error)

                                    if minify_warning:
                                        files_with_warnings[display_path] = minify_warning

                                    # If minification changed the content (was successful)
                                    if minified_content != content:
                                        minified_bytes = len(minified_content.encode('utf-8'))
                                        total_minified_bytes += minified_bytes
                                        content = minified_content
                                    else:
                                        # Content unchanged - could be due to minification not applicable or error
                                        total_minified_bytes += original_content_bytes
                                        if continue_on_error and len(content.strip()) > 0:
                                            # Only count as fail if it wasn't expected (like for markdown)
                                            if not any(file_extension.lower().endswith(ext) for ext in ['.md', '.markdown', '.txt', '.rst']):
                                                stats["failed_minifications"] += 1
                                                if display_path not in files_with_warnings:  # If no warning exists yet
                                                    files_with_warnings[display_path] = "Minification failed, using original content"
                                except Exception as e:
                                    if continue_on_error:
                                        if not silent:
                                            print(f"Warning: Error minifying {display_path}: {str(e)}. Using original content.")
                                        stats["failed_minifications"] += 1
                                        total_minified_bytes += original_content_bytes
                                    else:
                                        # Otherwise abort
                                        error_msg = f"Error bundling {display_path}: {str(e)}"
                                        print(error_msg)
                                        raise RuntimeError(error_msg)
                            else:
                                # Not using minification
                                total_minified_bytes = 0

                            if is_truncated:
                                outfile.write(f"`{display_path}` [Extracted snippet lines: {filtered_lines}/{original_lines}]\n```\n")
                            else:
                                outfile.write(f"`{display_path}` [total lines: {filtered_lines}]\n```\n")
                            outfile.write(content.rstrip())
                            outfile.write("\n```\n\n")

                            stats["files_bundled"] += 1
                            content_bytes = len(content.encode('utf-8'))
                            stats["bytes_bundled"] += content_bytes

                            if not silent:
                                status = "Success"
                                if is_truncated:
                                    status += f" (snippet: {filtered_lines}/{original_lines} lines)"

                                # Add warning indicator for Python files with likely syntax warnings
                                if minify and file_extension.lower().endswith('.py') and display_path in files_with_warnings:
                                    status += " (warn:escapes)"

                                if minify and stats["failed_minifications"] > 0:
                                    if any(file_extension.lower().endswith(ext) for ext in ['.md', '.markdown', '.txt', '.rst']):
                                        # Don't mention failure for text/markdown files
                                        pass
                                    elif content == content:  # This is always true, keeping for structure
                                        status = status  # No change needed

                                file_info = {
                                    "file": display_path,
                                    "size": content_bytes,
                                    "status": status,
                                    "warnings": files_with_warnings.get(display_path, "")
                                }

                                if minify:
                                    reduction = (1 - content_bytes / max(original_content_bytes, 1)) * 100
                                    file_info["original_size"] = original_content_bytes
                                    file_info["reduction"] = reduction

                                files_info.append(file_info)

                        except UnicodeDecodeError:
                            # Handle binary file or encoding issues
                            if continue_on_error:
                                if not silent:
                                    print(f"Warning: Encoding error with file {display_path}. Skipping file.")
                                stats["skipped_files"] += 1
                                if not silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": os.path.getsize(file_path),
                                        "status": "Skipped (encoding issues)"
                                    })
                            else:
                                error_msg = f"Error reading {display_path}: Unicode decode error"
                                print(error_msg)
                                raise RuntimeError(error_msg)
                        except Exception as e:
                            # Handle other errors
                            if continue_on_error:
                                if not silent:
                                    print(f"Warning: Error processing {display_path}: {str(e)}. Skipping file.")
                                stats["skipped_files"] += 1
                                if not silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                                        "status": f"Skipped (error: {str(e)})"
                                    })
                            else:
                                error_msg = f"Error bundling {display_path}: {str(e)}"
                                print(error_msg)
                                raise RuntimeError(error_msg)

        if minify:
            stats["minified_size"] = total_minified_bytes

        # Display results
        if not silent and files_info:
            print("[FILES PROCESSED]")
            file_table = format_file_table(files_info, OPERATION_BUNDLE if not minify else OPERATION_MINIFY_BUNDLE)
            print(file_table)

            if minify and stats["failed_minifications"] > 0 and continue_on_error:
                print(f"\nNote: {stats['failed_minifications']} file(s) could not be minified and were bundled with original content.")

        # Calculate duration and print stats
        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_BUNDLE if not minify else OPERATION_MINIFY_BUNDLE, duration)

        if not silent and minify and files_with_warnings:
            print(
                f"\nNote: {len(files_with_warnings)} Python file(s) contain patterns that may generate syntax warnings.")
            print("These files are marked with '(warn:escapes)' in the status column.")

        return stats

    def acroscan(self, file_path, acronyms, output_file=None,
                find_potential=False, replace_acronyms=True, latex_mode=False, silent=False,
                consolidate_output=True, use_acronym_package=True):
        # Initialize result dictionary
        result = {
            "found_acronyms": {},
            "potential_acronyms": [],
            "file_size": os.path.getsize(file_path),
            "replaced": 0
        }

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            if not silent:
                print(f"Error reading file: {e}")
            return result

        # Find all acronyms in the file
        for acronym, definition in acronyms.items():
            # Skip very short acronyms
            if len(acronym) < 2:
                continue

            # Create regex pattern to find the acronym as a whole word
            if latex_mode:
                if use_acronym_package:
                    # Avoid matching acronyms already in \ac, \acf, \acs, \acl commands
                    pattern = r'(?<!\\ac\{)(?<!\\acf\{)(?<!\\acs\{)(?<!\\acl\{)(?<!\w)' + re.escape(acronym) + r'(?!\w)(?!\})'
                else:
                    # For glossaries package
                    pattern = r'(?<!\\gls\{)(?<!\\ac\{)(?<!\w)' + re.escape(acronym) + r'(?!\w)(?!\})'
            else:
                pattern = r'(?<!\w)' + re.escape(acronym) + r'(?!\w)'

            matches = list(re.finditer(pattern, content))
            if matches:
                result["found_acronyms"][acronym] = {
                    "definition": definition,
                    "count": len(matches),
                    "positions": [(m.start(), m.end()) for m in matches]
                }

        # Find potential unknown acronyms if requested
        if find_potential:
            # Pattern for words with at least 2 uppercase letters
            pattern = r'\b[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*\b'
            potential_matches = set(re.findall(pattern, content))

            # Filter out known acronyms
            result["potential_acronyms"] = sorted(list(
                potential_matches - set(acronyms.keys())
            ))

        # Replace acronyms if requested and if there are any to replace
        if replace_acronyms and result["found_acronyms"] and output_file:
            modified_content = content
            all_positions = []
            
            # Collect all positions
            for acronym, info in result["found_acronyms"].items():
                for start, end in info["positions"]:
                    all_positions.append((start, end, acronym))
            
            # Sort positions in reverse order to avoid position shifts
            all_positions.sort(reverse=True)

            # Track first occurrences of each acronym
            first_occurrences = {}
            for start, end, acronym in sorted(all_positions, key=lambda x: x[0]):  # Sort by position (ascending)
                if acronym not in first_occurrences:
                    first_occurrences[acronym] = (start, end)

            # Perform replacements in reverse order
            for start, end, acronym in all_positions:
                is_first_occurrence = (start, end) == first_occurrences.get(acronym)
                
                if latex_mode:
                    if use_acronym_package:
                        # Use acronym package commands with direct acronym as key
                        if is_first_occurrence:
                            # For first occurrence, use \acf
                            replacement = f"\\acf{{{acronym}}}"
                        else:
                            # For subsequent occurrences, use \ac
                            replacement = f"\\ac{{{acronym}}}"
                    else:
                        # Use glossaries package commands with sanitized key
                        sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
                        if is_first_occurrence:
                            replacement = f"\\acf{{{sanitized_acronym}}}"
                        else:
                            replacement = f"\\ac{{{sanitized_acronym}}}"
                else:
                    # For plain text
                    if is_first_occurrence:
                        # First occurrence: definition (ACRONYM)
                        replacement = f"{acronyms[acronym]} ({acronym})"
                    else:
                        # Subsequent occurrences: just ACRONYM
                        replacement = acronym
                        
                modified_content = modified_content[:start] + replacement + modified_content[end:]
                result["replaced"] += 1

            # Ensure output directory exists
            output_dir = os.path.dirname(output_file)
            if output_dir and not os.path.exists(output_dir):
                os.makedirs(output_dir, exist_ok=True)
                
            # Write the modified content
            try:
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(modified_content)
            except Exception as e:
                if not silent:
                    print(f"Error writing output file: {e}")

        return result

    def acroscan_dir(self, source_dir, output_dir=None, acronym_list_path=None, exclude_dirs=None,
                exclude_exts=None, exclude_files=None, include_dirs=None, include_exts=None,
                include_files=None, find_potential=False, replace_acronyms=True, latex_mode=False,
                clear_dest_dir=False, recursive=True, silent=False, use_acronym_package=True):
        source_dir = os.path.abspath(source_dir)
        acronyms = load_acronyms_csv(acronym_list_path, silent)
        if output_dir:
            output_dir = os.path.abspath(output_dir)
            if clear_dest_dir and os.path.exists(output_dir):
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)

        # Initialize statistics
        stats = {
            "total_files_processed": 0,
            "files_with_acronyms": 0,
            "total_acronyms_replaced": 0,
            "skipped_files": 0,
            "files_scanned": 0,
            "dirs_traversed": 0,
            "max_nesting_level": 0,
            "unique_acronyms_found": set(),
            "potential_acronyms_found": set(),
            "all_found_acronyms": {}
        }

        if not silent:
            if self.extensions == [""]:
                print("Processing files with no extension...\n")
            elif self.extensions:
                print(f"Processing files: {', '.join(self.extensions)}...\n")

            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        # Find and filter files
        file_paths = []
        if recursive:
            for root, dirs, files in os.walk(source_dir):
                stats["dirs_traversed"] += 1
                rel_path = os.path.relpath(root, source_dir)
                current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
                stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

                # Filter directories
                if exclude_dirs:
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]
                if include_dirs:
                    rel_dir_parts = rel_path.split(os.sep)
                    if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                        dirs[:] = []  # Skip this branch
                        continue

                # Add files
                for file in files:
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
        else:
            file_paths = [os.path.join(source_dir, f) for f in os.listdir(source_dir)
                        if os.path.isfile(os.path.join(source_dir, f))]
            stats["dirs_traversed"] = 1

        # Filter files based on criteria
        filtered_files = []
        for file_path in file_paths:
            stats["total_files_processed"] += 1
            rel_path = os.path.relpath(file_path, source_dir)
            filename = os.path.basename(file_path)

            # Check if the file is of a type this handler processes
            if not self.handles_file(filename):
                stats["skipped_files"] += 1
                continue

            # Apply additional file filters
            if should_process_file(filename, self.extensions, exclude_exts, exclude_files,
                                include_exts, include_files, file_rel_path=rel_path):
                filtered_files.append(file_path)
            else:
                stats["skipped_files"] += 1

        # Show a message if no files were found to process
        if not filtered_files:
            if not silent:
                print(f"No files found to process.")
                print(f"Nothing to do for this file type.")
            return stats

        # Process filtered files
        files_info = []  # For table output
        converted_dir = os.path.join(output_dir, "converted") if output_dir and replace_acronyms else None
        
        # Only create the converted directory if we're actually replacing acronyms
        if converted_dir and replace_acronyms:
            os.makedirs(converted_dir, exist_ok=True)
            
        # Track whether any acronyms were found across all files
        found_any_acronyms = False
        
        for file_path in filtered_files:
            rel_path = os.path.relpath(file_path, source_dir)

            try:
                # First pass: just scan for acronyms
                scan_result = self.acroscan(
                    file_path,
                    acronyms,
                    output_file=None,  # Don't specify output file in scan phase
                    find_potential=find_potential,
                    replace_acronyms=False,  # Don't replace in scan phase
                    latex_mode=latex_mode,
                    silent=True,
                    consolidate_output=True,
                    use_acronym_package=use_acronym_package
                )
                
                # Track that we scanned this file
                stats["files_scanned"] += 1
                
                # Only proceed with replacement if acronyms were found
                has_acronyms = bool(scan_result["found_acronyms"])
                
                if has_acronyms:
                    found_any_acronyms = True
                
                if not has_acronyms:
                    # Add file info for reporting
                    files_info.append({
                        "file": rel_path,
                        "size": scan_result["file_size"],
                        "acronyms_found": 0,
                        "acronyms_replaced": 0,
                        "status": "No acronyms found"
                    })
                    continue
                    
                # Update statistics with found acronyms
                stats["files_with_acronyms"] += 1
                stats["unique_acronyms_found"].update(scan_result["found_acronyms"].keys())
                
                if find_potential:
                    stats["potential_acronyms_found"].update(scan_result["potential_acronyms"])
                    
                # Merge acronym details
                for acronym, info in scan_result["found_acronyms"].items():
                    if acronym not in stats["all_found_acronyms"]:
                        stats["all_found_acronyms"][acronym] = {
                            "definition": info["definition"],
                            "count": 0,
                            "files": []
                        }
                    stats["all_found_acronyms"][acronym]["count"] += info["count"]
                    stats["all_found_acronyms"][acronym]["files"].append(rel_path)
                    
                # If replacing acronyms and we have a place to put them
                if replace_acronyms and has_acronyms and converted_dir:
                    output_file = os.path.join(converted_dir, rel_path)
                    output_dir_path = os.path.dirname(output_file)
                    
                    # Create subdirectories only when needed
                    if not os.path.exists(output_dir_path):
                        os.makedirs(output_dir_path, exist_ok=True)
                            
                    # Second pass: do the actual replacement
                    result = self.acroscan(
                        file_path,
                        acronyms,
                        output_file=output_file,
                        find_potential=False,  # Already collected in first pass
                        replace_acronyms=True,
                        latex_mode=latex_mode,
                        silent=silent,
                        consolidate_output=True,
                        use_acronym_package=use_acronym_package
                    )
                    
                    # Update replacement stats
                    stats["total_acronyms_replaced"] += result.get("replaced", 0)
                    
                    # Add file info
                    files_info.append({
                        "file": rel_path,
                        "size": result["file_size"],
                        "acronyms_found": len(scan_result["found_acronyms"]),
                        "acronyms_replaced": result.get("replaced", 0),
                        "status": f"Replaced {result.get('replaced', 0)} acronyms"
                    })
                elif has_acronyms and not replace_acronyms:
                    # Add file info for files with acronyms but not replacing
                    files_info.append({
                        "file": rel_path,
                        "size": scan_result["file_size"],
                        "acronyms_found": len(scan_result["found_acronyms"]),
                        "acronyms_replaced": 0,
                        "status": f"Found {len(scan_result['found_acronyms'])} acronyms"
                    })
                    
            except Exception as e:
                if not silent:
                    print(f"Error processing file {rel_path}: {e}")
                files_info.append({
                    "file": rel_path,
                    "size": os.path.getsize(file_path),
                    "acronyms_found": 0,
                    "acronyms_replaced": 0,
                    "status": f"Error: {str(e)}"
                })

        # If no acronyms were found across all files, show a general message
        if not found_any_acronyms and not silent:
            print("No acronyms found in any files for this file type.")

        stats["file_results"] = files_info
        # Convert sets to lists for easier serialization in the main operation
        stats["unique_acronyms_found"] = list(stats["unique_acronyms_found"])
        stats["potential_acronyms_found"] = list(stats["potential_acronyms_found"])

        # Generate summary output for this specific file type
        if not silent and files_info and found_any_acronyms:
            print("[FILES PROCESSED]")
            file_table = format_file_table(files_info, OPERATION_ACROSCAN)
            print(file_table)

            print("\n[ACRONYMS FOUND]")
            if stats["unique_acronyms_found"]:
                print(f"Found {len(stats['unique_acronyms_found'])} unique acronyms across {stats['files_with_acronyms']} files:")
                for acronym in sorted(stats["all_found_acronyms"].keys()):
                    info = stats["all_found_acronyms"][acronym]
                    print(f"  - {acronym}: {info['definition']} (found {info['count']} times in {len(info['files'])} files)")
            else:
                print("No acronyms found.")

            if find_potential and stats["potential_acronyms_found"]:
                print("\n[POTENTIAL UNKNOWN ACRONYMS]")
                print(f"Found {len(stats['potential_acronyms_found'])} potential unknown acronyms:")
                for acronym in sorted(stats["potential_acronyms_found"]):
                    print(f"  - {acronym}")

        # Generate LaTeX acronym files for found acronyms if needed
        if output_dir and found_any_acronyms:
            # Generate consolidated files
            acronyms_txt_path = os.path.join(output_dir, DEFAULT_ACRONYMS_FOUND_OUTPUT_PATH)
            with open(acronyms_txt_path, 'w', encoding='utf-8') as f:
                f.write(f"# Acronyms found in {os.path.basename(source_dir)}\n\n")

                if stats["unique_acronyms_found"]:
                    f.write("## Known Acronyms\n\n")
                    for acronym in sorted(stats["all_found_acronyms"].keys()):
                        info = stats["all_found_acronyms"][acronym]
                        f.write(f"- {acronym}: {info['definition']} (found {info['count']} times in {len(info['files'])} files)\n")

                    f.write("\n## Files with Acronyms\n\n")
                    file_acronyms = {}
                    for acronym, info in stats["all_found_acronyms"].items():
                        for file_path in info["files"]:
                            if file_path not in file_acronyms:
                                file_acronyms[file_path] = []
                            file_acronyms[file_path].append(acronym)

                    for file_path in sorted(file_acronyms.keys()):
                        f.write(f"### {file_path}\n")
                        for acronym in sorted(file_acronyms[file_path]):
                            info = stats["all_found_acronyms"][acronym]
                            f.write(f"- {acronym}: {info['definition']}\n")
                        f.write("\n")
                else:
                    f.write("No known acronyms found.\n")

                if find_potential and stats["potential_acronyms_found"]:
                    f.write("\n## Potential Unknown Acronyms\n\n")
                    for acronym in sorted(stats["potential_acronyms_found"]):
                        f.write(f"- {acronym}\n")

            if latex_mode and stats["unique_acronyms_found"]:
                # IMPORTANT FIX: Ensure acronyms_found.tex uses the acronym package format when requested
                acronyms_tex_path = os.path.join(output_dir, DEFAULT_ACRONYMS_FOUND_TEX_OUTPUT_PATH)
                with open(acronyms_tex_path, 'w', encoding='utf-8') as f:
                    if use_acronym_package:
                        # Using acronym package format
                        f.write("% Acronyms found by CodeFlux (acronym package format)\n")
                        f.write("% Usage: \n")
                        f.write("%   \\ac{ACRONYM}  - Automatic: first use full form, then short form\n")
                        f.write("%   \\acf{ACRONYM} - Full form: \"definition (ACRONYM)\"\n")
                        f.write("%   \\acs{ACRONYM} - Short form: \"ACRONYM\"\n")
                        f.write("%   \\acl{ACRONYM} - Long form: \"definition\"\n\n")
                        
                        f.write("\\begin{acronym}\n")
                        for acronym in sorted(stats["all_found_acronyms"].keys()):
                            info = stats["all_found_acronyms"][acronym]
                            definition = info["definition"]
                            definition = definition.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
                            f.write(f"    \\acro{{{acronym}}}{{{definition}}}\n")
                        f.write("\\end{acronym}\n")
                    else:
                        # Using glossaries package format
                        f.write("% Acronyms found by CodeFlux (glossaries package format)\n")
                        f.write("% Usage: \n")
                        f.write("%   \\ac{acronym}  - Automatic: first use full form, then short form\n")
                        f.write("%   \\acf{acronym} - Full form: \"definition (ACRONYM)\"\n")
                        f.write("%   \\acs{acronym} - Short form: \"ACRONYM\"\n")
                        f.write("%   \\acl{acronym} - Long form: \"definition\"\n\n")
                        
                        for acronym in sorted(stats["all_found_acronyms"].keys()):
                            info = stats["all_found_acronyms"][acronym]
                            definition = info["definition"]
                            definition = definition.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
                            sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
                            f.write(f"\\newacronym{{{sanitized_acronym}}}{{{acronym}}}{{{definition}}}\n")
            
            # Also generate a file in the acronym package format for direct inclusion
            direct_tex_path = os.path.join(output_dir, DEFAULT_ACRONYMS_TRANSLATED_OUTPUT_PATH)
            if latex_mode and stats["unique_acronyms_found"]:
                # Pass the use_acronym_package parameter to ensure consistent format
                make_acronyms_tex_from_csv(acronym_list_path, direct_tex_path, use_acronym_package)

        return stats
    
    def properties_dir(self, source_dir, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                       include_dirs=None, include_exts=None, include_files=None, silent=False,
                       include_hash=False, include_line_count=False):

        source_dir = os.path.abspath(source_dir)
        stats = {
            "total_files_processed": 0,
            "dirs_traversed": 0,
            "total_files_counted": 0,
            "bytes_total": 0,
            "skipped_files": 0,
            "max_nesting_level": 0,
            "text_files_count": 0,
            "binary_files_count": 0
        }

        files_info = []  # For table output
        start_time = time.time()

        if not silent:
            if self.extensions == [""]:
                print("Processing files with no extension...\n")
            elif self.extensions:
                print(f"Processing files: {', '.join(self.extensions)}...\n")

            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        def human_readable_size(size_in_bytes):
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size_in_bytes < 1024.0 or unit == 'TB':
                    return f"{size_in_bytes:.2f} {unit}"
                size_in_bytes /= 1024.0

        def is_text_file(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    f.read(1024)  # Try to read as text
                    return True
            except UnicodeDecodeError:
                return False

        def count_lines(file_path):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    return len(f.readlines())
            except (UnicodeDecodeError, IOError):
                return 0

        def get_file_hash(file_path):
            try:
                hash_md5 = hashlib.md5()
                with open(file_path, "rb") as f:
                    for chunk in iter(lambda: f.read(4096), b""):
                        hash_md5.update(chunk)
                return hash_md5.hexdigest()
            except IOError:
                return "Error calculating hash"

        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            if include_dirs:
                # Only process specified directories
                rel_dir_parts = rel_path.split(os.sep)
                # Check if any part of the path is in include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []  # Clear dirs to skip this branch
                    continue

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                stats["total_files_processed"] += 1
                file_path = os.path.join(root, file)

                # Skip non-handled file types
                if not self.handles_file(file):
                    stats["skipped_files"] += 1
                    continue

                # Check if file should be included based on filters
                rel_path = os.path.relpath(file_path, source_dir)
                should_include = should_process_file(
                    file, self.extensions, exclude_exts, exclude_files, include_exts,
                    include_files, file_rel_path=rel_path
                )

                if should_include:
                    try:
                        # Get basic file stats
                        file_stat = os.stat(file_path)
                        file_size = file_stat.st_size
                        stats["total_files_counted"] += 1
                        stats["bytes_total"] += file_size

                        # Check if file is text or binary
                        is_text = is_text_file(file_path)
                        if is_text:
                            stats["text_files_count"] += 1
                        else:
                            stats["binary_files_count"] += 1

                        # Get file type based on extension
                        _, file_ext = os.path.splitext(file)
                        file_ext = file_ext.lower()[1:] if file_ext else "unknown"

                        # Get permissions
                        try:
                            permissions = stat.filemode(file_stat.st_mode)
                        except:
                            permissions = "unknown"

                        file_info = {
                            "file": get_relpath(file_path, source_dir),
                            "size": file_size,
                            "readable_size": human_readable_size(file_size),
                            "created": datetime.datetime.fromtimestamp(file_stat.st_ctime).strftime("%Y-%m-%d %H:%M:%S"),
                            "modified": datetime.datetime.fromtimestamp(file_stat.st_mtime).strftime("%Y-%m-%d %H:%M:%S"),
                            "accessed": datetime.datetime.fromtimestamp(file_stat.st_atime).strftime("%Y-%m-%d %H:%M:%S"),
                            "type": file_ext,
                            "permissions": permissions,
                            "is_text": "Text" if is_text else "Binary"
                        }
                        if include_line_count and is_text:
                            file_info["lines"] = count_lines(file_path)
                        if include_hash:
                            file_info["md5"] = get_file_hash(file_path)
                        files_info.append(file_info)
                    except Exception as e:
                        if not silent:
                            print(f"Error getting properties for {rel_path}: {str(e)}")
                else:
                    stats["skipped_files"] += 1

        if not silent:
            if stats["total_files_counted"] == 0:
                print(f"No files found to analyze.")
            elif files_info:
                # Sort files by size (largest first)
                files_info.sort(key=lambda x: x["size"], reverse=True)

                print("[FILES ANALYZED]")
                file_table = format_file_table(files_info, OPERATION_PROPERTIES)
                print(file_table)

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats(stats, OPERATION_PROPERTIES, duration)

        return stats


class PythonHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=PYTHON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PYTHON_EXCLUDE_EXTENSIONS,
            exclude_filenames=PYTHON_EXCLUDE_FILENAMES
        )


class NotebookHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=NOTEBOOK_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOTEBOOK_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOTEBOOK_EXCLUDE_FILENAMES
        )


class JavaScriptTypescriptHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=JSTS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSTS_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSTS_EXCLUDE_FILENAMES
        )


class HtmlHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=HTML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=HTML_EXCLUDE_EXTENSIONS,
            exclude_filenames=HTML_EXCLUDE_FILENAMES
        )


class CssHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=CSS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=CSS_EXCLUDE_EXTENSIONS,
            exclude_filenames=CSS_EXCLUDE_FILENAMES
        )


class PhpHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=PHP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PHP_EXCLUDE_EXTENSIONS,
            exclude_filenames=PHP_EXCLUDE_FILENAMES
        )


class RubyHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=RUBY_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=RUBY_EXCLUDE_EXTENSIONS,
            exclude_filenames=RUBY_EXCLUDE_FILENAMES
        )


class SwiftHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=SWIFT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SWIFT_EXCLUDE_EXTENSIONS,
            exclude_filenames=SWIFT_EXCLUDE_FILENAMES
        )


class KotlinHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=KOTLIN_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=KOTLIN_EXCLUDE_EXTENSIONS,
            exclude_filenames=KOTLIN_EXCLUDE_FILENAMES
        )


class JavaHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=JAVA_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JAVA_EXCLUDE_EXTENSIONS,
            exclude_filenames=JAVA_EXCLUDE_FILENAMES
        )


class CSharpHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=CSHARP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=CSHARP_EXCLUDE_EXTENSIONS,
            exclude_filenames=CSHARP_EXCLUDE_FILENAMES
        )


class ShellHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=SHELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SHELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=SHELL_EXCLUDE_FILENAMES
        )


class MarkdownTextHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=MDTXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=MDTXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=MDTXT_EXCLUDE_FILENAMES
        )


class YamlHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=YML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=YML_EXCLUDE_EXTENSIONS,
            exclude_filenames=YML_EXCLUDE_FILENAMES
        )


class JsonHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=JSON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSON_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSON_EXCLUDE_FILENAMES
        )


class GoHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=GO_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=GO_EXCLUDE_EXTENSIONS,
            exclude_filenames=GO_EXCLUDE_FILENAMES
        )


class IniHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=INI_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=INI_EXCLUDE_EXTENSIONS,
            exclude_filenames=INI_EXCLUDE_FILENAMES
        )


class DatabaseHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=DB_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=DB_EXCLUDE_EXTENSIONS,
            exclude_filenames=DB_EXCLUDE_FILENAMES
        )


class BatchHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=BAT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=BAT_EXCLUDE_EXTENSIONS,
            exclude_filenames=BAT_EXCLUDE_FILENAMES
        )


class ScpHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=SCP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SCP_EXCLUDE_EXTENSIONS,
            exclude_filenames=SCP_EXCLUDE_FILENAMES
        )


class NoExtHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=NOEXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOEXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOEXT_EXCLUDE_FILENAMES
        )

    def handles_file(self, filename):
        """Only handle files that have no extension at all."""
        # Check if the filename has no dot (except for hidden files that start with dot)
        if "." not in filename:
            return True
        # Special case for hidden files (which start with a dot)
        if filename.startswith(".") and filename.count(".") == 1:
            return True
        return False


class PowerShellHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=POWERSHELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=POWERSHELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=POWERSHELL_EXCLUDE_FILENAMES
        )


class DockerHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=DOCKER_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=DOCKER_EXCLUDE_EXTENSIONS,
            exclude_filenames=DOCKER_EXCLUDE_FILENAMES
        )


class XmlHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=XML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=XML_EXCLUDE_EXTENSIONS,
            exclude_filenames=XML_EXCLUDE_FILENAMES
        )


class RHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=R_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=R_EXCLUDE_EXTENSIONS,
            exclude_filenames=R_EXCLUDE_FILENAMES
        )


class CppHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=CPP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=CPP_EXCLUDE_EXTENSIONS,
            exclude_filenames=CPP_EXCLUDE_FILENAMES
        )


class RustHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=RUST_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=RUST_EXCLUDE_EXTENSIONS,
            exclude_filenames=RUST_EXCLUDE_FILENAMES
        )


class ScalaHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=SCALA_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SCALA_EXCLUDE_EXTENSIONS,
            exclude_filenames=SCALA_EXCLUDE_FILENAMES
        )


class PerlHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=PERL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PERL_EXCLUDE_EXTENSIONS,
            exclude_filenames=PERL_EXCLUDE_FILENAMES
        )


class LuaHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=LUA_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=LUA_EXCLUDE_EXTENSIONS,
            exclude_filenames=LUA_EXCLUDE_FILENAMES
        )


class GroovyHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=GROOVY_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=GROOVY_EXCLUDE_EXTENSIONS,
            exclude_filenames=GROOVY_EXCLUDE_FILENAMES
        )


class HaskellHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=HASKELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=HASKELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=HASKELL_EXCLUDE_FILENAMES
        )


class ErlangHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=ERLANG_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=ERLANG_EXCLUDE_EXTENSIONS,
            exclude_filenames=ERLANG_EXCLUDE_FILENAMES
        )


class LatexHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=LATEX_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=LATEX_EXCLUDE_EXTENSIONS,
            exclude_filenames=LATEX_EXCLUDE_FILENAMES
        )


class PDFHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=PDF_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PDF_EXCLUDE_EXTENSIONS,
            exclude_filenames=PDF_EXCLUDE_FILENAMES
        )


class DOCXHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=DOCX_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=DOCX_EXCLUDE_EXTENSIONS,
            exclude_filenames=DOCX_EXCLUDE_FILENAMES
        )


class BibTexHandler(FileExtHandler):
    def __init__(self):
        super().__init__(
            extensions=BIBTEX_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=BIBTEX_EXCLUDE_EXTENSIONS,
            exclude_filenames=BIBTEX_EXCLUDE_FILENAMES
        )

    def bibdedup_dir(self, source_dir, output_file, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                     include_dirs=None, include_exts=None, include_files=None, similarity_threshold=0.9, silent=False):
        """Find similar titles across multiple .bib files."""
        from ui.table import get_table_formatter

        source_dir = os.path.abspath(source_dir)
        stats = {
            "total_files_processed": 0,
            "total_entries": 0,
            "duplicates_found": 0,
            "files_with_duplicates": 0,
            "dirs_traversed": 0,
            "time_taken": 0,
            "max_nesting_level": 0
        }

        files_info = []  # For table output
        start_time = time.time()

        # Find all .bib files in the source directory
        bib_files = []
        entries = {}  # Dictionary to store all BibTeX entries
        file_entries = {}  # Dictionary to map files to their entries

        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            if include_dirs:
                # Only process specified directories
                rel_dir_parts = rel_path.split(os.sep)
                # Check if any part of the path is in include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []  # Clear dirs to skip this branch
                    continue

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            for file in files:
                stats["total_files_processed"] += 1

                # Skip if not a BibTeX file
                if not self.handles_file(file):
                    continue

                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, source_dir)

                # Apply additional filters
                should_include = should_process_file(
                    file, self.extensions, exclude_exts, exclude_files, include_exts,
                    include_files, file_rel_path=rel_file_path
                )

                if should_include:
                    bib_files.append(file_path)

                    # Extract entries from this BibTeX file
                    file_entries[file_path] = {}
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            current_key = None
                            for line in f:
                                key_match = re.search(r'@\w+\{([^,]+),', line)
                                if key_match:
                                    current_key = key_match.group(1)

                                title_match = re.search(r'^\s*title\s*=\s*["]?\s*\{(.+?)\}\s*["]?\s*,', line)
                                if title_match and current_key:
                                    normalized_title = title_match.group(1).strip().lower()
                                    entries[current_key] = {
                                        'title': normalized_title,
                                        'file': file_path
                                    }
                                    file_entries[file_path][current_key] = normalized_title

                        files_info.append({
                            "file": rel_file_path,
                            "size": os.path.getsize(file_path),
                            "entries": len(file_entries[file_path]),
                            "status": "Processed"
                        })
                    except UnicodeDecodeError:
                        if not silent:
                            print(f"Warning: Encoding issues with file {rel_file_path}. Skipping.")
                        files_info.append({
                            "file": rel_file_path,
                            "size": os.path.getsize(file_path),
                            "entries": 0,
                            "status": "Error (encoding)"
                        })
                    except Exception as e:
                        if not silent:
                            print(f"Error processing {rel_file_path}: {str(e)}")
                        files_info.append({
                            "file": rel_file_path,
                            "size": os.path.getsize(file_path),
                            "entries": 0,
                            "status": f"Error: {str(e)}"
                        })

        stats["total_entries"] = len(entries)

        if not bib_files:
            if not silent:
                print(f"No BibTeX files found to analyze.")

            end_time = time.time()
            duration = end_time - start_time
            stats["time_taken"] = duration

            if not silent:
                print_stats(stats, OPERATION_BIBDEDUP, duration)

            return stats

        # Find similar titles
        duplicates = []
        keys = list(entries.keys())
        files_with_duplicates = set()

        for i in range(len(keys)):
            for j in range(i + 1, len(keys)):
                k1, k2 = keys[i], keys[j]
                entry1 = entries[k1]
                entry2 = entries[k2]
                t1, t2 = entry1['title'], entry2['title']

                similarity = difflib.SequenceMatcher(None, t1, t2).ratio()
                # Include all similarities in results
                duplicates.append({
                    'key1': k1,
                    'title1': t1,
                    'file1': entry1['file'],
                    'key2': k2,
                    'title2': t2,
                    'file2': entry2['file'],
                    'similarity': similarity
                })
                # Only count as "duplicates" those with similarity above threshold
                if similarity >= similarity_threshold:
                    files_with_duplicates.add(entry1['file'])
                    files_with_duplicates.add(entry2['file'])

        # Sort duplicates by similarity (highest first)
        duplicates.sort(key=lambda x: x['similarity'], reverse=True)

        # Only count entries above threshold for stats
        duplicates_above_threshold = [d for d in duplicates if d['similarity'] >= similarity_threshold]
        stats["duplicates_found"] = len(duplicates_above_threshold)
        stats["files_with_duplicates"] = len(files_with_duplicates)

        # Generate plain text report
        report_lines = []
        report_lines.append(f"BibTeX Duplicate Detection Report")
        report_lines.append(f"==================================")
        report_lines.append(f"")
        report_lines.append(f"Source directory: {os.path.abspath(source_dir)}")
        report_lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"Similarity threshold for classification: {similarity_threshold}")
        report_lines.append(f"Files processed: {len(bib_files)}")
        report_lines.append(f"Total BibTeX entries: {stats['total_entries']}")
        report_lines.append(f"Potential duplicates found: {stats['duplicates_found']} (similarity >= {similarity_threshold})")
        report_lines.append(f"Files with duplicates: {stats['files_with_duplicates']}")
        report_lines.append(f"")

        if duplicates:
            report_lines.append("Duplicate Entries")
            report_lines.append("----------------")
            report_lines.append("")

            for i, dup in enumerate(duplicates):
                report_lines.append(f"Duplicate Set {i + 1} (Similarity: {dup['similarity']:.4f})")
                report_lines.append("-" * 60)
                report_lines.append(f"Entry 1: {dup['key1']}")
                report_lines.append(f"File: {get_relpath(dup['file1'], source_dir)}")
                report_lines.append(f"Title: {dup['title1']}")
                report_lines.append("")
                report_lines.append(f"Entry 2: {dup['key2']}")
                report_lines.append(f"File: {get_relpath(dup['file2'], source_dir)}")
                report_lines.append(f"Title: {dup['title2']}")
                report_lines.append("")
        else:
            report_lines.append("No duplicates found.")

        # List of all processed files
        report_lines.append("\nProcessed Files")
        report_lines.append("--------------")
        for file_path in bib_files:
            rel_path = get_relpath(file_path, source_dir)
            entry_count = len(file_entries.get(file_path, {}))
            report_lines.append(f"- {rel_path} ({entry_count} entries)")

        # Write report to file
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        # Update file info with duplicate information
        for file_info in files_info:
            file_path = os.path.join(source_dir, file_info["file"])
            if file_path in files_with_duplicates:
                file_info["status"] = "Has duplicates"

        if not silent:
            # Display results
            if files_info:
                print("[FILES PROCESSED]")
                file_table = format_file_table(files_info, OPERATION_BIBDEDUP)
                print(file_table)

            # Display duplicates
            if duplicates:
                print("\n[DUPLICATE ENTRIES]")
                display_duplicates = duplicates_above_threshold
                table_formatter, has_tabulate = get_table_formatter()

                if has_tabulate:
                    headers = ["#", "Entry 1", "Entry 2", "Similarity", "File 1", "File 2"]
                    rows = []

                    for i, dup in enumerate(display_duplicates):
                        title1 = dup['title1'][:40] + "..." if len(dup['title1']) > 40 else dup['title1']
                        title2 = dup['title2'][:40] + "..." if len(dup['title2']) > 40 else dup['title2']

                        rows.append([
                            i + 1,
                            f"{dup['key1']}\n{title1}",
                            f"{dup['key2']}\n{title2}",
                            f"{dup['similarity']:.4f}",
                            get_relpath(dup['file1'], source_dir),
                            get_relpath(dup['file2'], source_dir)
                        ])

                    if len(display_duplicates) > 0:
                        table = table_formatter(rows, headers=headers, tablefmt="grid")
                        print(table)
                        print(f"\nFound {len(display_duplicates)} entries with similarity >= {similarity_threshold}")
                        print(f"Full details in the output file: {get_relpath(output_file)}")
                    else:
                        print(f"No entries found with similarity >= {similarity_threshold}")
                        print(f"All similarity scores are available in the output file: {get_relpath(output_file)}")
                else:
                    # Fallback without tabulate - show duplicates above threshold
                    if len(display_duplicates) > 0:
                        for i, dup in enumerate(display_duplicates):
                            print(f"\n--- Duplicate {i + 1}/{len(display_duplicates)} (Similarity: {dup['similarity']:.4f}) ---")
                            print(f"Entry 1: {dup['key1']}")
                            print(f"Title 1: {dup['title1'][:60]}{'...' if len(dup['title1']) > 60 else ''}")
                            print(f"File 1: {get_relpath(dup['file1'], source_dir)}")
                            print(f"Entry 2: {dup['key2']}")
                            print(f"Title 2: {dup['title2'][:60]}{'...' if len(dup['title2']) > 60 else ''}")
                            print(f"File 2: {get_relpath(dup['file2'], source_dir)}")
                        print(f"\nFound {len(display_duplicates)} entries with similarity >= {similarity_threshold}")
                    else:
                        print(f"No entries found with similarity >= {similarity_threshold}")
                    print(f"Full details in the output file: {get_relpath(output_file)}")
            else:
                print("\nNo duplicate entries found.")

        end_time = time.time()
        duration = end_time - start_time
        stats["time_taken"] = duration

        if not silent:
            print_stats(stats, OPERATION_BIBDEDUP, duration)

        return stats


HANDLERS = {
    "py": PythonHandler(),
    "ipynb": NotebookHandler(),
    "jsts": JavaScriptTypescriptHandler(),
    "html": HtmlHandler(),
    "css": CssHandler(),
    "php": PhpHandler(),
    "ruby": RubyHandler(),
    "swift": SwiftHandler(),
    "kotlin": KotlinHandler(),
    "java": JavaHandler(),
    "csharp": CSharpHandler(),
    "shell": ShellHandler(),
    "mdtxt": MarkdownTextHandler(),
    "yml": YamlHandler(),
    "json": JsonHandler(),
    "go": GoHandler(),
    "ini": IniHandler(),
    "db": DatabaseHandler(),
    "bat": BatchHandler(),
    "scp": ScpHandler(),
    "noext": NoExtHandler(),
    "ps1": PowerShellHandler(),
    "docker": DockerHandler(),
    "xml": XmlHandler(),
    "r": RHandler(),
    "cpp": CppHandler(),
    "rust": RustHandler(),
    "scala": ScalaHandler(),
    "perl": PerlHandler(),
    "lua": LuaHandler(),
    "groovy": GroovyHandler(),
    "haskell": HaskellHandler(),
    "erlang": ErlangHandler(),
    "latex": LatexHandler(),
    "bibtex": BibTexHandler(),
    "pdf": PDFHandler(),
    "docx": DOCXHandler(),
}
