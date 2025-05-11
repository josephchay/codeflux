"""
Line break Operation: Breaks long lines in text and code files at specified width.
"""

import os
import shutil
from typing import List

from file_handler import FileHandler
from operations.base import Operation, OperationStats
from utils.logging import Logger


class LinebreakOperation(Operation):
    """Operation to line break long lines in files."""

    def __init__(self, file_handler: FileHandler, logger: Logger = None):
        """Initialize the line break operation."""
        super().__init__("linebreak", file_handler, logger)

    def execute(self, source_dir: str, output_dir: str, **kwargs) -> OperationStats:
        """
        Execute the line break operation.

        Args:
            source_dir: Source directory containing files to process
            output_dir: Output directory for processed files
            **kwargs: Additional arguments:
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - line_width: Maximum line width (default: 80)
                - break_on_word: Whether to break on word boundaries (default: True)
                - preserve_indent: Whether to preserve indentation (default: True)
                - clear_dest_dir: Whether to clear the destination directory first

        Returns:
            OperationStats with operation results
        """
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(output_dir)

        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])
        include_dirs = kwargs.get('include_dirs', None)
        include_exts = kwargs.get('include_exts', None)
        include_files = kwargs.get('include_files', None)
        line_width = kwargs.get('line_width', 80)
        break_on_word = kwargs.get('break_on_word', True)
        preserve_indent = kwargs.get('preserve_indent', True)
        clear_dest_dir = kwargs.get('clear_dest_dir', False)

        files_info = []  # For logging/reporting
        self.stats.start_timer()

        # Initialize additional statistics for linebreak operation
        self.stats.files_with_long_lines = 0
        self.stats.total_lines_broken = 0
        self.stats.total_lines_original = 0
        self.stats.total_lines_processed = 0

        # Prepare the output directory
        self._prepare_directories(output_dir, clear_dest_dir)

        if not self.logger.silent:
            self.logger.info(f"Processing files: {', '.join(self.file_handler.extensions)}...\n")
            self.logger.info(f"Maximum line width: {line_width} characters")
            self.logger.info(f"Break on word boundaries: {break_on_word}")
            self.logger.info(f"Preserve indentation: {preserve_indent}")

            if include_exts:
                self.logger.info(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                self.logger.info(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                self.logger.info(f"Including only files: {', '.join(include_files)}")

        # Walk through source directory
        for root, dirs, files in os.walk(source_dir):
            self.stats.dirs_traversed += 1

            # Calculate nesting level
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            self.stats.update_max_nesting(current_nesting)

            # Apply directory filters
            if include_dirs:
                rel_dir_parts = rel_path.split(os.sep)
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []
                    continue

            # Exclude directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]

            # Create corresponding output directory
            rel_output_path = os.path.relpath(root, source_dir)
            output_path = os.path.normpath(os.path.join(output_dir, rel_output_path))
            os.makedirs(output_path, exist_ok=True)

            # Process files
            for file in files:
                self.stats.total_files_processed += 1
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, source_dir)
                output_file_path = os.path.join(output_path, file)

                # Check if file should be processed
                if not self.file_handler.handles_file(file):
                    self.stats.skipped_files += 1
                    continue

                if not self.file_handler.should_process_file(
                        file, exclude_exts, exclude_files, include_exts, include_files, rel_path
                ):
                    self.stats.skipped_files += 1
                    continue

                # Process the file
                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        original_lines = content.splitlines()
                        self.stats.total_lines_original += len(original_lines)

                    # Process lines
                    processed_lines, lines_broken = self._process_file_content(
                        content, line_width, break_on_word, preserve_indent
                    )
                    self.stats.total_lines_processed += len(processed_lines.splitlines())

                    # Write to output file
                    with open(output_file_path, 'w', encoding='utf-8') as outfile:
                        outfile.write(processed_lines)

                    # Update statistics
                    if lines_broken > 0:
                        self.stats.files_with_long_lines += 1
                    self.stats.total_lines_broken += lines_broken
                    self.stats.files_copied += 1

                    # Get file size info
                    original_size = os.path.getsize(file_path)
                    processed_size = os.path.getsize(output_file_path)
                    self.stats.bytes_copied += processed_size

                    file_info = {
                        "file": rel_file_path,
                        "size": processed_size,
                        "original_size": original_size,
                        "lines_broken": lines_broken,
                        "status": f"{'Modified' if lines_broken > 0 else 'Copied as-is'}"
                    }
                    files_info.append(file_info)

                except UnicodeDecodeError:
                    # Binary file, just copy it
                    shutil.copy2(file_path, output_file_path)
                    self.stats.files_copied += 1
                    file_size = os.path.getsize(file_path)
                    self.stats.bytes_copied += file_size

                    file_info = {
                        "file": rel_file_path,
                        "size": file_size,
                        "original_size": file_size,
                        "lines_broken": 0,
                        "status": "Copied as-is (binary)"
                    }
                    files_info.append(file_info)

                except Exception as e:
                    error_msg = f"Error processing {file}: {str(e)}"
                    self.logger.error(error_msg)

                    file_info = {
                        "file": rel_file_path,
                        "size": 0,
                        "original_size": 0,
                        "lines_broken": 0,
                        "status": f"Error: {str(e)}"
                    }
                    files_info.append(file_info)

        # Display results
        if not self.logger.silent and files_info:
            self.logger.info("\n[FILES PROCESSED]")
            self.logger.print_file_table(files_info, "linebreak")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "linebreak")

        return self.stats

    def _process_file_content(self, content: str, line_width: int,
                              break_on_word: bool = True,
                              preserve_indent: bool = True) -> tuple[str, int]:
        """
        Process file content to break long lines.

        Args:
            content: File content to process
            line_width: Maximum line width
            break_on_word: Whether to break on word boundaries
            preserve_indent: Whether to preserve indentation

        Returns:
            Tuple of (processed_content, lines_broken_count)
        """
        lines = content.splitlines()
        processed_lines = []
        lines_broken = 0

        for line in lines:
            if len(line) <= line_width:
                processed_lines.append(line)
            else:
                # Get indentation if preserving
                indent = ""
                if preserve_indent:
                    stripped = line.lstrip()
                    indent = line[:len(line) - len(stripped)]

                # Break the line
                broken_lines = self._break_line(line, line_width, break_on_word, indent)
                processed_lines.extend(broken_lines)
                lines_broken += len(broken_lines) - 1

        return '\n'.join(processed_lines), lines_broken

    def _break_line(self, line: str, line_width: int,
                    break_on_word: bool = True, indent: str = "") -> List[str]:
        """
        Break a single line into multiple lines.

        Args:
            line: Line to break
            line_width: Maximum line width
            break_on_word: Whether to break on word boundaries
            indent: Indentation to preserve

        Returns:
            List of broken lines
        """
        if len(line) <= line_width:
            return [line]

        broken_lines = []
        remaining = line
        first_line = True

        while remaining:
            if first_line:
                # First line uses original indentation
                available_width = line_width
                current_indent = ""
                first_line = False
            else:
                # Subsequent lines may have additional indentation
                current_indent = indent
                available_width = line_width - len(current_indent)

            # Make sure we have at least 1 character width available
            if available_width <= 0:
                available_width = 1

            if len(remaining) <= available_width:
                broken_lines.append(current_indent + remaining)
                break

            if break_on_word:
                # Find the last space before the width limit
                break_pos = available_width
                while break_pos > 0 and remaining[break_pos - 1] not in ' \t':
                    break_pos -= 1

                # If no space found, force break at the available width
                if break_pos == 0:
                    break_pos = available_width
            else:
                break_pos = available_width

            # Make sure we're making progress (avoid infinite loop)
            if break_pos == 0:
                break_pos = 1

            # Split the line
            broken_lines.append(current_indent + remaining[:break_pos].rstrip())
            remaining = remaining[break_pos:].lstrip()

        return broken_lines
