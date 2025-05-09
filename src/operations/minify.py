"""
Minify Operation: Creates minified versions of files while preserving directory structure.
"""

import os
import shutil
from typing import Dict, List, Optional, Any, Tuple

from file_handler import FileHandler
from operations.base import Operation, OperationStats
from utils.logging import Logger
from utils.minifier import minify_code


class MinifyOperation(Operation):
    """Operation to create minified versions of files."""

    def __init__(self, file_handler: FileHandler, logger: Logger = None):
        """Initialize the minify operation."""
        super().__init__("minify", file_handler, logger)

    def execute(self, source_dir: str, output_dir: str, **kwargs) -> OperationStats:
        """
        Execute the minify operation.

        Args:
            source_dir: Source directory containing files to minify
            output_dir: Output directory for minified files
            **kwargs: Additional arguments:
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - clear_dest_dir: Whether to clear the destination directory first
                - continue_on_error: Whether to continue when minification errors occur

        Returns:
            OperationStats with operation results
        """
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(output_dir)

        # Validate source and output directories are different
        if output_dir == source_dir:
            raise ValueError("Source and output directories cannot be the same for minify operations")

        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])
        include_dirs = kwargs.get('include_dirs', None)
        include_exts = kwargs.get('include_exts', None)
        include_files = kwargs.get('include_files', None)
        clear_dest_dir = kwargs.get('clear_dest_dir', False)
        continue_on_error = kwargs.get('continue_on_error', False)

        files_info = []  # For logging/reporting
        files_with_warnings = {}  # Track files with warnings

        self.stats.start_timer()

        # Prepare the output directory
        self._prepare_directories(output_dir, clear_dest_dir)

        # Log operation information
        if not self.logger.silent:
            if self.file_handler.extensions == [""]:
                self.logger.info("Processing files with no extension...\n")
            elif self.file_handler.extensions:
                self.logger.info(f"Processing files: {', '.join(self.file_handler.extensions)}...\n")

            if include_exts:
                self.logger.info(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                self.logger.info(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                self.logger.info(f"Including only files: {', '.join(include_files)}")

            self.logger.info(f"Minification enabled")
            if continue_on_error:
                self.logger.info("Note: Continuing on minification errors (original content used for failed files)")

        # Whether any files are found that should be processed
        files_found = False

        # Helper function to identify text/markdown files that shouldn't be minified
        def is_text_markdown_file(filename):
            """Check if a file is a text or markdown file that shouldn't attempt minification."""
            text_markdown_exts = ['.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.mdwn', '.mdtxt', '.mdtext', '.txt',
                                  '.rst']
            return any(filename.lower().endswith(ext) for ext in text_markdown_exts)

        # Walk the directory tree
        for root, dirs, files in os.walk(source_dir):
            self.stats.dirs_traversed += 1

            # Calculate nesting level for stats
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            self.stats.update_max_nesting(current_nesting)

            # Apply directory inclusion/exclusion filters
            if include_dirs:
                # Only process specified directories
                rel_dir_parts = rel_path.split(os.sep)
                # Check if any part of the path is in include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []  # Clear dirs to skip this branch
                    continue

            # Filter out excluded directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Create corresponding output directory
            rel_output_path = os.path.relpath(root, source_dir)
            output_path = os.path.normpath(os.path.join(output_dir, rel_output_path))
            os.makedirs(output_path, exist_ok=True)

            # Process files in the current directory
            for file in files:
                self.stats.total_files_processed += 1
                file_path = os.path.join(root, file)
                output_file_path = os.path.join(output_path, file)

                # Skip if source and destination are the same
                if os.path.abspath(file_path) == os.path.abspath(output_file_path):
                    self.stats.skipped_files += 1
                    continue

                # Skip files not handled by this handler
                if not self.file_handler.handles_file(file):
                    self.stats.skipped_files += 1
                    continue

                # Apply additional filters
                rel_file_path = os.path.relpath(file_path, source_dir)
                should_include = self.file_handler.should_process_file(
                    file, self.file_handler.extensions, exclude_exts,
                    exclude_files, include_exts, include_files, file_rel_path=rel_file_path
                )

                if should_include:
                    files_found = True

                    # Check if file exists and has size
                    if os.path.getsize(file_path) == 0:
                        # Handle empty file
                        shutil.copy2(file_path, output_file_path)
                        self.stats.files_copied += 1
                        self.stats.empty_files += 1

                        if not self.logger.silent:
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
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            content = infile.read()

                            # Skip empty files with whitespace only
                            if not content.strip():
                                shutil.copy2(file_path, output_file_path)
                                self.stats.files_copied += 1
                                self.stats.empty_files += 1
                                file_size = len(content.encode('utf-8'))

                                if not self.logger.silent:
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
                            self.stats.bytes_original += original_size

                        _, ext = os.path.splitext(file)
                        ext_lower = ext.lower()

                        # Determine if this is a file type we shouldn't try to minify
                        is_text_md = is_text_markdown_file(file)

                        # For text/markdown files, just copy without attempting minification
                        if is_text_md:
                            shutil.copy2(file_path, output_file_path)
                            self.stats.files_copied += 1
                            file_size = original_size
                            self.stats.bytes_copied += file_size
                            self.stats.bytes_minified += file_size  # Count as minified size too

                            if not self.logger.silent:
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

                        # Attempt to minify the file
                        try:
                            warning_message = None

                            # Check for common warnings in Python files
                            if ext_lower.endswith('.py'):
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
                                        files_with_warnings[rel_file_path] = warning_message
                                        break

                            # Minify the content
                            minified_content, minify_warning = minify_code(content, ext, continue_on_error)
                            if minify_warning:
                                files_with_warnings[rel_file_path] = minify_warning

                            # Check if minification was successful (content changed and returned value is not None)
                            if minified_content is not None and minified_content != content:
                                # Also using byte count for minified content
                                minified_size = len(minified_content.encode('utf-8'))
                                self.stats.bytes_minified += minified_size
                                self.stats.files_minified += 1
                            else:
                                # If content is unchanged or minified_content is None, use original size
                                minified_size = original_size
                                self.stats.bytes_minified += minified_size

                                # Only count as a failed minification if continue_on_error is True
                                # and the content is unchanged (could be due to error handling)
                                if continue_on_error and len(content.strip()) > 0:
                                    self.stats.failed_minifications += 1

                            # Write the minified content
                            with open(output_file_path, 'w', encoding='utf-8') as outfile:
                                outfile.write(minified_content)

                            self.stats.files_copied += 1
                            self.stats.bytes_copied += minified_size

                            if not self.logger.silent:
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
                                self.stats.files_copied += 1
                                self.stats.failed_minifications += 1
                                file_size = os.path.getsize(file_path)
                                self.stats.bytes_copied += file_size
                                self.stats.bytes_minified += file_size  # Count original size in minified bytes

                                if not self.logger.silent:
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
                                self.logger.error(error_msg)
                                raise RuntimeError(error_msg)
                    except UnicodeDecodeError:
                        # Binary file, just copy it
                        shutil.copy2(file_path, output_file_path)
                        self.stats.files_copied += 1
                        file_size = os.path.getsize(file_path)
                        self.stats.bytes_original += file_size
                        self.stats.bytes_minified += file_size
                        self.stats.bytes_copied += file_size

                        if not self.logger.silent:
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
                    self.stats.skipped_files += 1

        # Log results if not silent
        if not self.logger.silent:
            if not files_found:
                self.logger.info(f"No files found to minify.")
                self.logger.info(f"No files were copied.")
            elif files_info:
                self.logger.info("[FILES PROCESSED]")
                self.logger.print_file_table(files_info, "minify")

                if self.stats.failed_minifications > 0 and continue_on_error:
                    self.logger.info(
                        f"\nNote: {self.stats.failed_minifications} file(s) could not be minified and were copied as-is.")

                # Display warning summary if any warnings were found
                if files_with_warnings:
                    self.logger.info(
                        f"\nNote: {len(files_with_warnings)} Python file(s) contain patterns that may generate syntax warnings.")
                    self.logger.info("These files are marked with '(warn:escapes)' in the status column.")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "minify")

        return self.stats
