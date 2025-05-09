"""
Bundle Operation: Combines multiple files into a single document.
"""

import datetime
import os
from typing import Any

from file_handler import FileHandler
from operations.base import Operation, OperationStats


class BundleOperation(Operation):
    """Operation to bundle multiple files into a single document."""

    def __init__(self, file_handler: FileHandler, logger: Any = None):
        """Initialize the bundle operation."""
        super().__init__("bundle", file_handler, logger)

    def execute(self, source_dir: str, output_file: str, **kwargs) -> OperationStats:
        """
        Execute the bundle operation.

        Args:
            source_dir: Source directory containing files to bundle
            output_file: Output file path for the bundled content
            **kwargs: Additional arguments:
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - minify: Whether to minify files before bundling
                - snippet: Whether to include only snippets of large files
                - snippet_lines: Number of lines to include in snippets
                - snippet_start: Where to start the snippet (top, middle, bottom)
                - snippet_context: Number of context lines around matches
                - search_pattern: Pattern to search for in snippets
                - continue_on_error: Whether to continue when minification errors occur

        Returns:
            OperationStats with operation results
        """
        source_dir = os.path.abspath(source_dir)
        output_file = os.path.abspath(output_file)

        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])
        include_dirs = kwargs.get('include_dirs', None)
        include_exts = kwargs.get('include_exts', None)
        include_files = kwargs.get('include_files', None)
        minify = kwargs.get('minify', False)
        snippet = kwargs.get('snippet', False)
        snippet_lines = kwargs.get('snippet_lines', 50)
        snippet_start = kwargs.get('snippet_start', "top")
        snippet_context = kwargs.get('snippet_context', 5)
        search_pattern = kwargs.get('search_pattern', None)
        continue_on_error = kwargs.get('continue_on_error', False)

        # Exclude the output file from processing
        output_filename = os.path.basename(output_file)
        if output_filename not in exclude_files and exclude_files is not None:
            exclude_files.append(output_filename)

        files_info = []  # For logging/reporting
        files_with_warnings = {}  # Track files with warnings

        self.stats.start_timer()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        def format_path_for_display(path):
            """Format a path for display in the bundle"""
            if "___" in path:
                parts = path.split("___")
                return "/".join(parts)
            return path

        # Gather files to bundle
        files_to_bundle = []
        for root, dirs, files in os.walk(source_dir):
            self.stats.dirs_traversed += 1

            # Calculate nesting level for stats
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            self.stats.update_max_nesting(current_nesting)

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
                self.stats.total_files_processed += 1
                file_path = os.path.join(root, file)

                # Skip output file
                if os.path.abspath(file_path) == output_file:
                    self.stats.skipped_files += 1
                    continue

                # Skip non-handled file types
                if not self.file_handler.handles_file(file):
                    self.stats.skipped_files += 1
                    continue

                # Check if file should be included based on filters
                rel_path = os.path.relpath(file_path, source_dir)

                if self.file_handler.should_process_file(
                    file,  # filename
                    exclude_exts,  # exclude_exts
                    exclude_files,  # exclude_files
                    include_exts,  # include_exts
                    include_files,  # include_files
                    rel_path  # file_rel_path
                ):
                    # Get path components for formatted path
                    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))
                    path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                    if path_parts:
                        formatted_path = "___".join(path_parts + [file])
                    else:
                        formatted_path = file

                    # Get file extension for language hint
                    _, file_ext = os.path.splitext(file)
                    file_ext = file_ext[1:] if file_ext else ""  # Remove the dot

                    files_to_bundle.append({
                        'file_path': file_path,
                        'formatted_path': formatted_path,
                        'rel_path': rel_path,
                        'extension': file_ext.lower(),
                        'full_extension': file_ext
                    })
                else:
                    self.stats.skipped_files += 1

        if not files_to_bundle:
            if not self.logger.silent:
                self.logger.info(f"No files found to bundle.")

            self.stats.stop_timer()

            if not self.logger.silent:
                self.logger.print_stats(self.stats, "bundle" if not minify else "minify_bundle")

            return self.stats

        # Sort files by extension and name for better organization
        files_to_bundle.sort(key=lambda x: (x['extension'], x['formatted_path']))

        # Calculate total original size
        total_original_bytes = 0
        for file_info in files_to_bundle:
            file_path = file_info['file_path']
            if os.path.exists(file_path):
                file_size = os.path.getsize(file_path)
                total_original_bytes += file_size

        self.stats.bytes_original = total_original_bytes

        # Group files by extension for more efficient processing
        extension_groups = {}
        for file_info in files_to_bundle:
            ext = file_info['extension']
            if ext not in extension_groups:
                extension_groups[ext] = []
            extension_groups[ext].append(file_info)

        total_minified_bytes = 0

        with open(output_file, 'w', encoding='utf-8') as outfile:
            # Write header information
            outfile.write(f"# {os.path.basename(source_dir)} ({len(files_to_bundle)} files)\n")
            outfile.write(f"# Created: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

            if snippet:
                outfile.write(f"# Snippet mode: {snippet_start.capitalize()} {snippet_lines} lines")
                if search_pattern:
                    outfile.write(f" with {snippet_context} context lines around '{search_pattern}'")
                outfile.write("\n")

            if minify:
                outfile.write(f"# Minification: Enabled\n")
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
                            # Check if the file is binary
                            is_binary = False
                            try:
                                with open(file_path, 'r', encoding='utf-8') as test_file:
                                    test_file.read(1024)  # Try to read as text
                            except UnicodeDecodeError:
                                is_binary = True

                            if is_binary:
                                # Skip binary files
                                self.stats.skipped_files += 1
                                if not self.logger.silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": os.path.getsize(file_path),
                                        "status": "Skipped (binary file)"
                                    })
                                continue

                            # Read file content
                            with open(file_path, 'r', encoding='utf-8') as infile:
                                content = infile.read()
                                original_content_bytes = len(content.encode('utf-8'))

                            # Skip empty files
                            if not content.strip():
                                self.stats.skipped_files += 1
                                if not self.logger.silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": 0,
                                        "status": "Skipped (empty file)"
                                    })
                                continue

                            # Apply snippet filtering if enabled
                            is_truncated = False
                            original_lines = 0
                            filtered_lines = 0

                            if snippet:
                                try:
                                    from utils.snippet import apply_snippet_filter
                                    content, filtered_lines, original_lines = apply_snippet_filter(
                                        content, snippet, snippet_lines, snippet_start,
                                        snippet_context, search_pattern
                                    )
                                    is_truncated = filtered_lines < original_lines
                                    if is_truncated:
                                        self.stats.files_with_snippets += 1
                                except Exception as e:
                                    if not self.logger.silent:
                                        self.logger.warning(
                                            f"Failed to apply snippet filter to {display_path}: {str(e)}")
                                    content_lines = content.splitlines()
                                    original_lines = len(content_lines)
                                    filtered_lines = original_lines
                            else:
                                content_lines = content.splitlines()
                                original_lines = len(content_lines)
                                filtered_lines = original_lines

                            # Apply minification if enabled
                            if minify:
                                try:
                                    warning_message = None
                                    from utils.minifier import minify_code

                                    # Check for Python syntax warnings
                                    if file_extension.lower().endswith('.py'):
                                        # Common invalid escape sequences that trigger SyntaxWarnings
                                        invalid_escapes = {
                                            '\\s': 'invalid escape sequence \\s',
                                            '\\d': 'invalid escape sequence \\d',
                                            '\\w': 'invalid escape sequence \\w',
                                            '\\.': 'invalid escape sequence \\.',
                                            '\\-': 'invalid escape sequence \\-',
                                            '\\_': 'invalid escape sequence \\_'
                                        }
                                        for invalid_escape, warning_text in invalid_escapes.items():
                                            if invalid_escape in content:
                                                warning_message = f"SyntaxWarning: {warning_text}"
                                                files_with_warnings[display_path] = warning_message
                                                break

                                    # Minify the content
                                    minified_content, minify_warning = minify_code(content, file_extension,
                                                                                   continue_on_error)

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
                                            if not any(file_extension.lower().endswith(ext) for ext in
                                                       ['.md', '.markdown', '.txt', '.rst']):
                                                self.stats.failed_minifications += 1
                                                if display_path not in files_with_warnings:  # If no warning exists yet
                                                    files_with_warnings[
                                                        display_path] = "Minification failed, using original content"
                                except Exception as e:
                                    if continue_on_error:
                                        if not self.logger.silent:
                                            self.logger.warning(
                                                f"Error minifying {display_path}: {str(e)}. Using original content.")
                                        self.stats.failed_minifications += 1
                                        total_minified_bytes += original_content_bytes
                                    else:
                                        # Otherwise abort
                                        error_msg = f"Error bundling {display_path}: {str(e)}"
                                        self.logger.error(error_msg)
                                        raise RuntimeError(error_msg)
                            else:
                                # Not using minification
                                total_minified_bytes = 0

                            # Write the file content to the bundle
                            if is_truncated:
                                outfile.write(
                                    f"`{display_path}` [Extracted snippet lines: {filtered_lines}/{original_lines}]\n```\n")
                            else:
                                outfile.write(f"`{display_path}` [total lines: {filtered_lines}]\n```\n")
                            outfile.write(content.rstrip())
                            outfile.write("\n```\n\n")

                            self.stats.files_bundled += 1
                            content_bytes = len(content.encode('utf-8'))
                            self.stats.bytes_bundled += content_bytes

                            if not self.logger.silent:
                                status = "Success"
                                if is_truncated:
                                    status += f" (snippet: {filtered_lines}/{original_lines} lines)"

                                # Add warning indicator for Python files with likely syntax warnings
                                if minify and file_extension.lower().endswith('.py') and display_path in files_with_warnings:
                                    status += " (warn:escapes)"

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
                                if not self.logger.silent:
                                    self.logger.warning(f"Encoding error with file {display_path}. Skipping file.")
                                self.stats.skipped_files += 1
                                if not self.logger.silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": os.path.getsize(file_path),
                                        "status": "Skipped (encoding issues)"
                                    })
                            else:
                                error_msg = f"Error reading {display_path}: Unicode decode error"
                                self.logger.error(error_msg)
                                raise RuntimeError(error_msg)
                        except Exception as e:
                            # Handle other errors
                            if continue_on_error:
                                if not self.logger.silent:
                                    self.logger.warning(
                                        f"Error processing {display_path}: {str(e)}. Skipping file.")
                                self.stats.skipped_files += 1
                                if not self.logger.silent:
                                    files_info.append({
                                        "file": display_path,
                                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                                        "status": f"Skipped (error: {str(e)})"
                                    })
                            else:
                                error_msg = f"Error bundling {display_path}: {str(e)}"
                                self.logger.error(error_msg)
                                raise RuntimeError(error_msg)

        if minify:
            self.stats.minified_size = total_minified_bytes

        # Update statistics for proper reporting
        self.stats.files_processed = len(files_info)

        # For minify-bundle, update files_minified count
        if minify:
            # Count files that were successfully minified (reduction > 0)
            minified_files = sum(1 for file_info in files_info
                                 if "reduction" in file_info and file_info["reduction"] > 0)
            self.stats.files_minified = minified_files

        # Display results
        if not self.logger.silent and files_info:
            self.logger.info("[FILES PROCESSED]")
            self.logger.print_file_table(files_info, "bundle" if not minify else "minify_bundle")

            if minify and self.stats.failed_minifications > 0 and continue_on_error:
                self.logger.info(f"\nNote: {self.stats.failed_minifications} file(s) could not be minified and were bundled with original content.")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "bundle" if not minify else "minify_bundle")

            if minify and files_with_warnings:
                self.logger.info(f"\nNote: {len(files_with_warnings)} Python file(s) contain patterns that may generate syntax warnings.")
                self.logger.info("These files are marked with '(warn:escapes)' in the status column.")

        return self.stats
