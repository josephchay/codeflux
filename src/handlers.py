import os
import shutil
import time
import datetime

from constants import *
from minify import minify_code
from snipping import apply_snippet_filter
from ui.table import format_file_table
from utils import get_unique_filename, print_stats, should_process_file, get_relative_path


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
                                "file": get_relative_path(source_file, source_dir),
                                "size": file_size,
                                "status": f"Flattened to {dest_rel_path}"
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
            print(f"Processing files: {', '.join(self.extensions)}...")
            if include_exts:
                print(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                print(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                print(f"Including only files: {', '.join(include_files)}")

        if not os.path.exists(flattened_dir) or not os.listdir(flattened_dir):
            if not silent:
                print(f"Source directory {get_relative_path(flattened_dir)} does not exist or is empty.")
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
                print(f"Skipping to avoid overwriting source: {get_relative_path(flattened_file)}")
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
                        "file": get_relative_path(flattened_file),
                        "size": file_size,
                        "status": f"Deflattened to {get_relative_path(unique_destination_file)}"
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
            text_markdown_exts = ['.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.mdwn', '.mdtxt', '.mdtext', '.txt',
                                  '.rst']
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

                            # Check if minification was successful (content changed)
                            if minified_content != content:
                                # Also using byte count for minified content
                                minified_size = len(minified_content.encode('utf-8'))
                                stats["bytes_minified"] += minified_size
                                stats["files_minified"] += 1
                            else:
                                # If content is unchanged, it might mean minification was not applicable
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

                                status = "Minified"
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
                    print(
                        f"\nNote: {stats['failed_minifications']} file(s) could not be minified and were copied as-is.")

            # Display warning summary if any warnings were found
            if files_with_warnings:
                print(
                    f"\nNote: {len(files_with_warnings)} Python file(s) contain patterns that may generate syntax warnings.")
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
                            # Read file content
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
                                if minify:
                                    status = "Minified & Bundled"
                                else:
                                    status = "Bundled"
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

        # Update minified_size stat after processing all files
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
}
