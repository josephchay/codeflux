"""
Flatten Operation: Flattens a directory structure into a single directory.
"""

import os
import shutil
from typing import Dict, List, Optional, Any, Set, Union

from file_handler import FileHandler
from operations.base import Operation, OperationStats


class FlattenOperation(Operation):
    """Operation to flatten directory structure."""

    def __init__(self, file_handler: FileHandler, logger: Any = None):
        """Initialize the flatten operation."""
        super().__init__("flatten", file_handler, logger)

    def execute(self, source_dir: str, output_dir: str, **kwargs) -> OperationStats:
        """
        Execute the flatten operation.

        Args:
            source_dir: Source directory to flatten
            output_dir: Output directory for flattened files
            **kwargs: Additional arguments:
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - clear_dest_dir: Whether to clear the destination directory first

        Returns:
            OperationStats with operation results
        """
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(kwargs.get('output_dir', output_dir))

        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])
        include_dirs = kwargs.get('include_dirs', None)
        include_exts = kwargs.get('include_exts', None)
        include_files = kwargs.get('include_files', None)
        clear_dest_dir = kwargs.get('clear_dest_dir', False)

        files_info = []  # For logging/reporting
        self.stats.start_timer()

        # Prepare the output directory
        if clear_dest_dir and os.path.exists(output_dir):
            shutil.rmtree(output_dir)
        os.makedirs(output_dir, exist_ok=True)

        source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

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

        # Walk the directory tree
        for root, dirs, files in os.walk(source_dir):
            self.stats.dirs_traversed += 1

            # Calculate nesting level for stats
            rel_path = os.path.relpath(root, source_dir)
            current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
            self.stats.update_max_nesting(current_nesting)

            # Include only specified directories if provided
            if include_dirs:
                rel_dir_parts = rel_path.split(os.sep)
                # Check if any part of the path matches include_dirs
                if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                    dirs[:] = []  # Skip this branch
                    continue

            # Filter out excluded directories
            dirs[:] = [
                d for d in dirs
                if d not in exclude_dirs and os.path.abspath(os.path.join(root, d)) != output_dir
            ]

            # Process files in the current directory
            for file in files:
                self.stats.total_files_processed += 1
                source_file = os.path.join(root, file)
                rel_path = os.path.relpath(source_file, source_dir)

                # Only process files handled by this handler
                if not self.file_handler.handles_file(file):
                    self.stats.skipped_files += 1
                    continue

                # Apply additional filtering criteria
                if self.file_handler.should_process_file(
                        file, self.file_handler.extensions, exclude_exts, exclude_files,
                        include_exts, include_files, file_rel_path=rel_path
                ):
                    # Create flattened filename with path components
                    path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                    if path_parts:
                        new_filename = "___".join(path_parts + [file])
                    else:
                        new_filename = file

                    # Copy the file to its flattened destination
                    destination_file = os.path.join(output_dir, new_filename)
                    unique_destination_file = self.file_handler.get_unique_filename(destination_file)

                    try:
                        shutil.copy2(source_file, unique_destination_file)
                        self.stats.files_copied += 1
                        file_size = os.path.getsize(source_file)
                        self.stats.bytes_copied += file_size

                        if not self.logger.silent:
                            dest_rel_path = os.path.relpath(
                                unique_destination_file, os.path.dirname(output_dir)
                            )

                            file_info = {
                                "file": self.file_handler.get_relpath(source_file, source_dir),
                                "size": file_size,
                                "status": "Success"
                            }
                            files_info.append(file_info)
                    except Exception as e:
                        error_msg = f"Error copying {file}: {str(e)}"
                        self.logger.error(error_msg)
                        raise RuntimeError(error_msg)
                else:
                    self.stats.skipped_files += 1

        # Log results if not silent
        if not self.logger.silent:
            if self.stats.files_copied == 0:
                self.logger.info(f"No files found to process.")
                self.logger.info(f"No files were copied.")
                self.logger.info("\nNothing to do for this file type.")
            elif files_info:
                self.logger.info("[FILES PROCESSED]")
                self.logger.print_file_table(files_info, "flatten")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "flatten")

        return self.stats
