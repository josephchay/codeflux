"""
Deflatten Operation: Restores the original directory structure from flattened files.
"""

import os
import shutil
from typing import Dict, List, Optional, Any

from file_handler import FileHandler
from operations.base import Operation, OperationStats
from utils.logging import Logger


class DeflattenOperation(Operation):
    """Operation to restore the original directory structure from flattened files."""

    def __init__(self, file_handler: FileHandler, logger: Logger = None):
        """Initialize the deflatten operation."""
        super().__init__("deflatten", file_handler, logger)

    def execute(self, source_dir: str, output_dir: str, **kwargs) -> OperationStats:
        """
        Execute the deflatten operation.

        Args:
            source_dir: Source directory containing flattened files
            output_dir: Output directory for restored directory structure
            **kwargs: Additional arguments:
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - clear_dest_dir: Whether to clear the destination directory first

        Returns:
            OperationStats with operation results
        """
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(output_dir)

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
        self.stats.dirs_created += 1

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

        # Check if source directory exists and has files
        if not os.path.exists(source_dir) or not os.listdir(source_dir):
            if not self.logger.silent:
                self.logger.info(
                    f"Source directory {self.file_handler.get_relpath(source_dir)} does not exist or is empty.")
                self.logger.info(f"No files to deflatten.")
                self.logger.info("\nNothing to do for this file type.")

            self.stats.stop_timer()
            return self.stats

        # Process each file in the source directory
        for file in os.listdir(source_dir):
            self.stats.total_files_processed += 1

            # Extract original path and filename from the flattened filename
            original_filename = file.split("___")[-1]

            # Check if it's a file type this handler processes
            if not self.file_handler.handles_file(original_filename):
                self.stats.skipped_files += 1
                continue

            # Get path components
            path_parts = file.split("___")
            original_path = '/'.join(path_parts[:-1] + [original_filename]) if len(
                path_parts) > 1 else original_filename
            should_include = True

            # Apply filtering criteria
            if include_exts:
                is_included_ext = any(original_filename.lower().endswith(ext.lower()) for ext in include_exts)
                if not is_included_ext:
                    should_include = False

            if exclude_files:
                for exclude_pattern in exclude_files:
                    norm_exclude = exclude_pattern.replace('\\', '/')
                    norm_path = original_path.replace('\\', '/')
                    if (norm_path.lower() == norm_exclude.lower() or
                            norm_path.lower().endswith('/' + norm_exclude.lower()) or
                            original_filename.lower() == norm_exclude.lower()):
                        should_include = False
                        break

            if include_dirs:
                path_parts = file.split("___")[:-1]  # Get directory parts
                if not any(part in include_dirs for part in path_parts):
                    should_include = False

            if include_files:
                file_matches = False
                for include_file in include_files:
                    if original_filename.lower() == include_file.lower() or original_path.lower().endswith(
                            include_file.lower()):
                        file_matches = True
                        break
                should_include = file_matches

            if not should_include:
                self.stats.skipped_files += 1
                continue

            # Process the file
            source_file = os.path.join(source_dir, file)
            path_parts = file.split("___")
            original_file = path_parts[-1]
            original_dir = os.path.join(output_dir, *path_parts[:-1])

            # Avoid overwriting the source
            if os.path.abspath(original_dir).startswith(source_dir):
                self.logger.info(f"Skipping to avoid overwriting source: {self.file_handler.get_relpath(source_file)}")
                self.stats.skipped_files += 1
                continue

            # Create destination directory if it doesn't exist
            if not os.path.exists(original_dir):
                try:
                    os.makedirs(original_dir, exist_ok=True)
                    self.stats.dirs_created += 1
                except Exception as e:
                    error_msg = f"Error creating directory {original_dir}: {str(e)}"
                    self.logger.error(error_msg)
                    raise RuntimeError(error_msg)

            # Copy the file
            destination_file = os.path.join(original_dir, original_file)
            unique_destination_file = self.file_handler.get_unique_filename(destination_file)

            try:
                shutil.copy2(source_file, unique_destination_file)
                self.stats.files_copied += 1
                file_size = os.path.getsize(source_file)
                self.stats.bytes_copied += file_size

                if not self.logger.silent:
                    file_info = {
                        "file": self.file_handler.get_relpath(source_file),
                        "size": file_size,
                        "status": "Success"
                    }
                    files_info.append(file_info)
            except Exception as e:
                error_msg = f"Error copying {file}: {str(e)}"
                self.logger.error(error_msg)
                raise RuntimeError(error_msg)

        # Log results if not silent
        if not self.logger.silent:
            if self.stats.files_copied == 0:
                self.logger.info(f"No files found to process.")
                self.logger.info(f"No files were copied.")
            elif files_info:
                self.logger.info("[FILES PROCESSED]")
                self.logger.print_file_table(files_info, "deflatten")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "deflatten")

        return self.stats
    