"""
FileHandler: Core file operations for the CodeFlux application.
Provides abstracted file I/O operations for various file types.
"""

import os
import re
import shutil
import hashlib
from typing import Dict, List, Tuple, Optional, Set, Any, Union


class FileHandler:
    """A unified interface for file operations across different file types."""
    
    def __init__(self, extensions: List[str], exclude_dirs: List[str] = None, 
                 exclude_extensions: List[str] = None, exclude_filenames: List[str] = None):
        """
        Initialize a file handler for specific file extensions.
        
        Args:
            extensions: List of file extensions this handler processes
            exclude_dirs: Directories to exclude from processing
            exclude_extensions: File extensions to exclude from processing
            exclude_filenames: Specific filenames to exclude from processing
        """
        self.extensions = extensions
        self.exclude_dirs = exclude_dirs or []
        self.exclude_extensions = exclude_extensions or []
        self.exclude_filenames = exclude_filenames or []
    
    def handles_file(self, filename: str) -> bool:
        """Check if this handler should process the given filename based on its extension."""
        return any(filename.lower().endswith(ext.lower()) for ext in self.extensions)
    
    def get_unique_filename(self, destination_file: str) -> str:
        """Generate a unique filename if the destination already exists."""
        counter = 2
        name, ext = os.path.splitext(destination_file)
        unique_destination_file = destination_file

        while os.path.exists(unique_destination_file):
            unique_destination_file = f"{name}_{counter}{ext}"
            counter += 1

        return unique_destination_file
    
    def should_process_file(self, filename: str, exclude_exts: List[str] = None,
                           exclude_files: List[str] = None, include_exts: List[str] = None, 
                           include_files: List[str] = None, file_rel_path: str = None) -> bool:
        """
        Determine if a file should be processed based on inclusion/exclusion criteria.
        
        Args:
            filename: Name of the file to check
            exclude_exts: File extensions to exclude
            exclude_files: Specific filenames or paths to exclude
            include_exts: Only process files with these extensions (if specified)
            include_files: Only process these specific files (if specified)
            file_rel_path: Relative path of the file (for path-based filtering)
            
        Returns:
            True if the file should be processed, False otherwise
        """
        # If specific files are included, check if this file matches
        if include_files:
            lower_include_files = [f.lower() for f in include_files]
            filename_lower = filename.lower()
            if filename_lower in lower_include_files:
                return True

            if file_rel_path:
                rel_path_lower = file_rel_path.lower()
                for inc in lower_include_files:
                    if rel_path_lower.endswith(inc) or rel_path_lower == inc:
                        return True

            return False

        # Check if the file matches our target extensions
        if include_exts:
            is_included_ext = any(filename.lower().endswith(ext.lower()) for ext in include_exts)
            if not is_included_ext:
                return False
        else:
            is_target_ext = any(filename.lower().endswith(ext.lower()) for ext in self.extensions)
            if not is_target_ext:
                return False

        # Check exclusion criteria
        exclude_exts = exclude_exts or []
        exclude_files = exclude_files or []
        
        # Check excluded extensions
        for ext in exclude_exts:
            # Handle regex patterns
            if ext.startswith(r"\.") or any(c in ext for c in ".*+?()[]{}|^$"):
                if re.search(ext + "$", filename.lower()):
                    return False
            # Regular suffix check
            elif filename.lower().endswith(ext.lower()):
                return False

        # Check excluded files/paths
        if exclude_files and file_rel_path:
            norm_rel_path = file_rel_path.replace('\\', '/')
            for exclude_pattern in exclude_files:
                norm_exclude = exclude_pattern.replace('\\', '/')
                if (norm_rel_path.lower() == norm_exclude.lower() or
                        norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                        filename.lower() == norm_exclude.lower()):
                    return False

        return True
    
    def is_dir_excluded(self, rel_dir_path: str) -> bool:
        """Check if a directory should be excluded based on its path."""
        if not rel_dir_path or rel_dir_path == '.':
            return False
            
        # Check for exact directory name match
        dir_parts = rel_dir_path.split(os.sep)
        if any(part in self.exclude_dirs for part in dir_parts):
            return True
            
        # Check for path-based exclusions
        for exclude_dir in self.exclude_dirs:
            if os.sep in exclude_dir or '/' in exclude_dir:
                # Normalize paths for comparison
                norm_exclude = exclude_dir.replace('\\', os.sep).replace('/', os.sep)
                norm_rel_path = rel_dir_path.replace('\\', os.sep)
                
                # Check if the exclusion path is a substring of the full path
                if norm_rel_path == norm_exclude or norm_rel_path.startswith(norm_exclude + os.sep):
                    return True
        
        return False
    
    def get_file_hash(self, file_path: str) -> str:
        """Calculate an MD5 hash for a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except IOError:
            return "Error calculating hash"

    def count_lines(self, file_path: str) -> int:
        """Count the number of lines in a text file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return len(f.readlines())
        except (UnicodeDecodeError, IOError):
            return 0

    def is_text_file(self, file_path: str) -> bool:
        """Check if a file is a text file (vs binary)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1024)  # Try to read as text
                return True
        except UnicodeDecodeError:
            return False
    
    def format_file_size(self, size_in_bytes: int) -> str:
        """Format file size to human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_in_bytes < 1024.0 or unit == 'TB':
                return f"{size_in_bytes:.2f} {unit}"
            size_in_bytes /= 1024.0
    
    def copy_file(self, source_file: str, dest_file: str, allow_overwrite: bool = False) -> Tuple[bool, str]:
        """
        Copy a file from source to destination.
        
        Args:
            source_file: Source file path
            dest_file: Destination file path
            allow_overwrite: Whether to overwrite existing files
            
        Returns:
            Tuple of (success, error_message)
        """
        try:
            os.makedirs(os.path.dirname(dest_file), exist_ok=True)
            
            if not allow_overwrite:
                dest_file = self.get_unique_filename(dest_file)
                
            shutil.copy2(source_file, dest_file)
            return True, ""
        except Exception as e:
            return False, str(e)
    
    def get_relpath(self, path: str, base_path: str = None) -> str:
        """Get the relative path from base_path."""
        base_path = base_path or os.getcwd()
        try:
            abs_path = os.path.abspath(path)
            abs_base = os.path.abspath(base_path)
            
            # Try to strip out codeflux timestamp patterns
            match = re.search(r'(codeflux[/\\]\d{8}_\d{6}[/\\])', abs_path)
            if match:
                timestamp_dir = match.group(0)
                timestamp_index = abs_path.find(timestamp_dir) + len(timestamp_dir)
                if timestamp_index < len(abs_path):
                    return abs_path[timestamp_index:].replace('\\', '/')
                else:
                    return os.path.basename(abs_path)

            # Calculate relative path
            if abs_path.startswith(abs_base + os.sep) or abs_path == abs_base:
                rel_path = os.path.relpath(abs_path, abs_base)
                if rel_path == '.':
                    return os.path.basename(abs_path)
                return rel_path.replace('\\', '/')

            # Default case
            return os.path.relpath(abs_path, abs_base).replace('\\', '/')
        except ValueError:
            # If there's an error (e.g., different drives on Windows)
            return os.path.basename(path)
        