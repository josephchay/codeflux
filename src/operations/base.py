"""
Base Operation: Defines the abstract interface for all operations in CodeFlux.
"""

import os
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any


class OperationStats:
    """Statistics tracking for CodeFlux operations."""

    def __init__(self):
        """Initialize operation statistics counters."""
        self.total_files_processed = 0
        self.dirs_traversed = 0
        self.files_copied = 0
        self.files_processed = 0
        self.bytes_copied = 0
        self.skipped_files = 0
        self.max_nesting_level = 0
        self.start_time = 0
        self.end_time = 0

        # Optional stats for specific operations
        self.dirs_created = 0
        self.files_minified = 0
        self.bytes_original = 0
        self.bytes_minified = 0
        self.empty_files = 0
        self.failed_minifications = 0
        self.files_bundled = 0
        self.bytes_bundled = 0
        self.files_with_snippets = 0

    def start_timer(self):
        """Start the operation timer."""
        self.start_time = time.time()

    def stop_timer(self):
        """Stop the operation timer."""
        self.end_time = time.time()

    @property
    def duration(self):
        """Get the operation duration in seconds."""
        if self.end_time <= 0:
            # If timer hasn't stopped, calculate from current time
            return time.time() - self.start_time
        return self.end_time - self.start_time

    def update_max_nesting(self, level: int):
        """Update the maximum nesting level."""
        self.max_nesting_level = max(self.max_nesting_level, level)

    def merge(self, other_stats):
        """Merge another stats object into this one."""
        for key, value in vars(other_stats).items():
            if key in ['start_time', 'end_time']:
                continue

            if hasattr(self, key):
                current_value = getattr(self, key)
                if isinstance(current_value, (int, float)):
                    # For numeric values, add them
                    setattr(self, key, current_value + value)
                elif key == 'max_nesting_level':
                    # For max values, take the max
                    setattr(self, key, max(current_value, value))

        return self


class Operation(ABC):
    """Base class for all CodeFlux operations."""

    def __init__(self, name: str, file_handler: Any, logger: Any = None):
        """
        Initialize the operation.

        Args:
            name: Operation name
            file_handler: Handler for file operations
            logger: Logger instance (imported dynamically to avoid circular imports)
        """
        self.name = name
        self.file_handler = file_handler

        # Import Logger here to avoid circular imports
        if logger is None:
            from utils.logging import Logger
            self.logger = Logger(silent=True)
        else:
            self.logger = logger

        self.stats = OperationStats()

    @abstractmethod
    def execute(self, source_dir: str, output_path: str, **kwargs) -> OperationStats:
        """
        Execute the operation.

        Args:
            source_dir: Source directory path
            output_path: Output path (file or directory)
            **kwargs: Additional arguments specific to the operation

        Returns:
            OperationStats with operation results
        """
        pass

    def _prepare_directories(self, directory_path: str, clear_dest_dir: bool = False):
        """
        Prepare directories for the operation.

        Args:
            directory_path: Path to prepare
            clear_dest_dir: Whether to clear the directory first
        """
        if clear_dest_dir and os.path.exists(directory_path):
            import shutil
            shutil.rmtree(directory_path)
        os.makedirs(directory_path, exist_ok=True)

    def _get_file_info(self, file_path: str, rel_path: str) -> Dict[str, Any]:
        """
        Get standard file information.

        Args:
            file_path: Absolute path to the file
            rel_path: Relative path for display

        Returns:
            Dictionary with file information
        """
        try:
            file_size = os.path.getsize(file_path)
            return {
                "file": rel_path,
                "size": file_size,
                "status": "Success"
            }
        except Exception as e:
            return {
                "file": rel_path,
                "size": 0,
                "status": f"Error: {str(e)}"
            }
