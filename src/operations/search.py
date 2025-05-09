"""
Search Operation: Searches for files matching specific criteria.
"""

import os
import re
import ast
import datetime
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Any, Set, Tuple

from file_handler import FileHandler
from operations.base import Operation, OperationStats
from utils.logging import Logger
from constants import ALL_EXTENSIONS


class SearchOperation(Operation):
    """Operation to search for files matching specific criteria."""

    def __init__(self, file_handler: FileHandler, logger: Logger = None):
        """Initialize the search operation."""
        super().__init__("search", file_handler, logger)

    def execute(self, source_dir: str, **kwargs) -> OperationStats:
        """
        Execute the search operation.

        Args:
            source_dir: Source directory to search
            **kwargs: Additional arguments:
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - search_ext: File extensions to search for
                - search_pattern: Pattern to search for in file content
                - search_size: Tuple of (min_size, max_size) in KB
                - search_date: Tuple of (start_date, end_date)
                - search_imports: Module name to search for in imports
                - search_duplicates: Minimum number of lines for duplicate detection

        Returns:
            OperationStats with search results
        """
        source_dir = os.path.abspath(source_dir)
        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])

        search_ext = kwargs.get('search_ext')
        search_pattern = kwargs.get('search_pattern')
        search_size = kwargs.get('search_size')
        search_date = kwargs.get('search_date')
        search_imports = kwargs.get('search_imports')
        search_duplicates = kwargs.get('search_duplicates')

        self.stats.start_timer()

        # Perform requested search operations
        if search_ext:
            self._search_by_extension(source_dir, search_ext, exclude_dirs, exclude_files)

        if search_pattern:
            target_exts = kwargs.get('include_extensions') or None
            self._search_by_pattern(source_dir, search_pattern, target_exts, exclude_dirs, exclude_files)

        if search_size:
            min_size, max_size = search_size
            min_size = None if min_size.lower() == 'none' else float(min_size)
            max_size = None if max_size.lower() == 'none' else float(max_size)
            target_exts = kwargs.get('include_extensions') or None
            self._search_by_size(source_dir, min_size, max_size, target_exts, exclude_dirs, exclude_files)

        if search_date:
            start_date = search_date[0]
            end_date = search_date[1] if len(search_date) > 1 else None
            target_exts = kwargs.get('include_extensions') or None
            self._search_by_date(source_dir, start_date, end_date, target_exts, exclude_dirs, exclude_files)

        if search_imports:
            target_exts = kwargs.get('include_extensions') or ['.py']
            self._search_imports(source_dir, search_imports, target_exts, exclude_dirs, exclude_files)

        if search_duplicates is not None:
            min_lines = search_duplicates
            target_exts = kwargs.get('include_extensions') or None
            self._search_duplicates(source_dir, min_lines, target_exts, exclude_dirs, exclude_files)

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "search")

        return self.stats

    def _is_excluded_file(self, file_rel_path: str, exclude_files: List[str]) -> bool:
        """Check if a file should be excluded based on path."""
        norm_rel_path = file_rel_path.replace('\\', '/')

        for exclude_pattern in exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if norm_rel_path == norm_exclude:
                return True

        return False

    def _search_by_extension(self, source_dir: str, extensions: List[str],
                           exclude_dirs: List[str], exclude_files: List[str]):
        """Search for files with specific extensions."""
        results = []
        file_count = 0
        total_size_bytes = 0

        if not self.logger.silent:
            self.logger.info(f"\nSearching for files with extensions: {', '.join(extensions)}")

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            self.stats.dirs_traversed += 1

            for file in files:
                self.stats.total_files_processed += 1
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, source_dir)

                    if self._is_excluded_file(rel_path, exclude_files):
                        self.stats.skipped_files += 1
                        continue

                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024
                    total_size_bytes += file_size
                    results.append((rel_path, file_size))
                    file_count += 1

                    if not self.logger.silent:
                        self.logger.info(f"Found: {rel_path} (Size: {file_size_kb:.2f} KB)")

        if not self.logger.silent:
            total_size_kb = total_size_bytes / 1024
            self.logger.info(f"\nTotal files found: {file_count}")
            self.logger.info(f"Total size: {total_size_kb:.2f} KB")
            if file_count > 0:
                avg_size_kb = total_size_kb / file_count
                self.logger.info(f"Average file size: {avg_size_kb:.2f} KB")

    def _search_by_pattern(self, source_dir: str, pattern: str,
                          extensions: Optional[List[str]], exclude_dirs: List[str], exclude_files: List[str]):
        """Search for files containing a specific pattern."""
        results = []
        file_count = 0
        match_count = 0
        total_size_bytes = 0

        extensions = extensions or ALL_EXTENSIONS

        if not self.logger.silent:
            self.logger.info(f"\nSearching for pattern: '{pattern}'")
            if extensions:
                self.logger.info(f"In files with extensions: {', '.join(extensions)}")

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            self.stats.dirs_traversed += 1

            for file in files:
                self.stats.total_files_processed += 1
                if not any(file.lower().endswith(ext) for ext in extensions):
                    self.stats.skipped_files += 1
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                if self._is_excluded_file(rel_path, exclude_files):
                    self.stats.skipped_files += 1
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.finditer(pattern, content)
                        found_matches = list(matches)

                        if found_matches:
                            file_count += 1
                            match_count += len(found_matches)
                            total_size_bytes += file_size

                            if not self.logger.silent:
                                self.logger.info(f"\nFile: {rel_path} (Size: {file_size_kb:.2f} KB)")
                                for i, match in enumerate(found_matches[:5]):  # Show first 5 matches
                                    start = max(0, match.start() - 20)
                                    end = min(len(content), match.end() + 20)
                                    context = content[start:end].replace('\n', ' ')
                                    self.logger.info(f"  Match {i + 1}: ...{context}...")

                                if len(found_matches) > 5:
                                    self.logger.info(f"  (and {len(found_matches) - 5} more matches)")

                            results.append((rel_path, found_matches, file_size))
                except UnicodeDecodeError:
                    # Skip binary files
                    self.stats.skipped_files += 1
                    continue

        if not self.logger.silent:
            total_size_kb = total_size_bytes / 1024
            self.logger.info(f"\nTotal files with matches: {file_count}")
            self.logger.info(f"Total matches found: {match_count}")
            self.logger.info(f"Total size of matching files: {total_size_kb:.2f} KB")
            if file_count > 0:
                avg_size_kb = total_size_kb / file_count
                self.logger.info(f"Average matching file size: {avg_size_kb:.2f} KB")

    def _search_by_size(self, source_dir: str, min_size: Optional[float], max_size: Optional[float],
                       extensions: Optional[List[str]], exclude_dirs: List[str], exclude_files: List[str]):
        """Search for files within a size range (in KB)."""
        results = []
        file_count = 0

        extensions = extensions or ALL_EXTENSIONS
        min_size_bytes = min_size * 1024 if min_size is not None else None
        max_size_bytes = max_size * 1024 if max_size is not None else None

        size_range = []
        if min_size is not None:
            size_range.append(f">= {min_size} KB")
        if max_size is not None:
            size_range.append(f"<= {max_size} KB")

        if not self.logger.silent:
            self.logger.info(f"\nSearching for files with size {' and '.join(size_range)}")
            if extensions:
                self.logger.info(f"In files with extensions: {', '.join(extensions)}")

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            self.stats.dirs_traversed += 1

            for file in files:
                self.stats.total_files_processed += 1
                if not any(file.lower().endswith(ext) for ext in extensions):
                    self.stats.skipped_files += 1
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                if self._is_excluded_file(rel_path, exclude_files):
                    self.stats.skipped_files += 1
                    continue

                file_size = os.path.getsize(file_path)
                if (min_size_bytes is None or file_size >= min_size_bytes) and (max_size_bytes is None or file_size <= max_size_bytes):
                    file_size_kb = file_size / 1024
                    results.append((rel_path, file_size_kb))
                    file_count += 1

                    if not self.logger.silent:
                        self.logger.info(f"Found: {rel_path} (Size: {file_size_kb:.2f} KB)")

        if not self.logger.silent:
            self.logger.info(f"\nTotal files found: {file_count}")

    def _search_by_date(self, source_dir: str, start_date: str, end_date: Optional[str],
                       extensions: Optional[List[str]], exclude_dirs: List[str], exclude_files: List[str]):
        """Search for files modified between specific dates."""
        results = []
        file_count = 0
        total_size_bytes = 0

        extensions = extensions or ALL_EXTENSIONS
        start_date_ts = datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()

        if end_date:
            end_date_ts = datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp()
        else:
            end_date_ts = datetime.datetime.now().timestamp()

        if not self.logger.silent:
            date_range = f"since {start_date}"
            if end_date:
                date_range += f" until {end_date}"

            self.logger.info(f"\nSearching for files modified {date_range}")
            if extensions:
                self.logger.info(f"In files with extensions: {', '.join(extensions)}")

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            self.stats.dirs_traversed += 1

            for file in files:
                self.stats.total_files_processed += 1
                if not any(file.lower().endswith(ext) for ext in extensions):
                    self.stats.skipped_files += 1
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                if self._is_excluded_file(rel_path, exclude_files):
                    self.stats.skipped_files += 1
                    continue

                mod_time = os.path.getmtime(file_path)
                if start_date_ts <= mod_time <= end_date_ts:
                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024
                    total_size_bytes += file_size

                    mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    results.append((rel_path, mod_date, file_size))
                    file_count += 1

                    if not self.logger.silent:
                        self.logger.info(f"Found: {rel_path} (Modified: {mod_date}, Size: {file_size_kb:.2f} KB)")

        if not self.logger.silent:
            total_size_kb = total_size_bytes / 1024
            self.logger.info(f"\nTotal files found: {file_count}")
            self.logger.info(f"Total size: {total_size_kb:.2f} KB")
            if file_count > 0:
                avg_size_kb = total_size_kb / file_count
                self.logger.info(f"Average file size: {avg_size_kb:.2f} KB")

    def _search_imports(self, source_dir: str, module_name: str,
                       extensions: List[str], exclude_dirs: List[str], exclude_files: List[str]):
        """Search for files that import a specific module."""
        results = []
        file_count = 0
        import_count = 0
        total_size_bytes = 0

        if not self.logger.silent:
            self.logger.info(f"\nSearching for imports of '{module_name}'")
            if extensions:
                self.logger.info(f"In files with extensions: {', '.join(extensions)}")

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            self.stats.dirs_traversed += 1

            for file in files:
                self.stats.total_files_processed += 1
                if not any(file.lower().endswith(ext) for ext in extensions):
                    self.stats.skipped_files += 1
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                if self._is_excluded_file(rel_path, exclude_files):
                    self.stats.skipped_files += 1
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    try:
                        tree = ast.parse(content)
                        imports = []

                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for name in node.names:
                                    if module_name in name.name:
                                        imports.append((name.name, node.lineno))
                            elif isinstance(node, ast.ImportFrom):
                                if module_name in node.module or any(module_name in name.name for name in node.names):
                                    imported_names = [name.name for name in node.names]
                                    imports.append((f"from {node.module} import {', '.join(imported_names)}", node.lineno))

                        if imports:
                            file_count += 1
                            import_count += len(imports)
                            total_size_bytes += file_size

                            if not self.logger.silent:
                                self.logger.info(f"\nFile: {rel_path} (Size: {file_size_kb:.2f} KB)")
                                for import_stmt, line_num in imports:
                                    self.logger.info(f"  Line {line_num}: {import_stmt}")

                            results.append((rel_path, imports, file_size))
                    except SyntaxError:
                        # Skip files with syntax errors
                        self.stats.skipped_files += 1
                        continue
                except UnicodeDecodeError:
                    # Skip binary files
                    self.stats.skipped_files += 1
                    continue

        if not self.logger.silent:
            total_size_kb = total_size_bytes / 1024
            self.logger.info(f"\nTotal files with imports: {file_count}")
            self.logger.info(f"Total imports found: {import_count}")
            self.logger.info(f"Total size of files with imports: {total_size_kb:.2f} KB")
            if file_count > 0:
                avg_size_kb = total_size_kb / file_count
                self.logger.info(f"Average file size: {avg_size_kb:.2f} KB")

    def _search_duplicates(self, source_dir: str, min_lines: int = 5, threshold: float = 0.8,
                           extensions: Optional[List[str]] = None, exclude_dirs: List[str] = None,
                           exclude_files: List[str] = None):
        """Search for duplicate code blocks across files."""
        file_contents = []
        total_size_bytes = 0
        file_count = 0

        extensions = extensions or ALL_EXTENSIONS

        if not self.logger.silent:
            self.logger.info(f"\nSearching for duplicate code blocks (min {min_lines} lines)")
            if extensions:
                self.logger.info(f"In files with extensions: {', '.join(extensions)}")

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            self.stats.dirs_traversed += 1

            for file in files:
                self.stats.total_files_processed += 1
                if not any(file.lower().endswith(ext) for ext in extensions):
                    self.stats.skipped_files += 1
                    continue

                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, source_dir)

                if self._is_excluded_file(rel_path, exclude_files):
                    self.stats.skipped_files += 1
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    file_size_kb = file_size / 1024
                    total_size_bytes += file_size
                    file_count += 1

                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    lines = content.splitlines()
                    if len(lines) >= min_lines:
                        file_contents.append((rel_path, lines, file_size))
                except UnicodeDecodeError:
                    # Skip binary files
                    self.stats.skipped_files += 1
                    continue

        # Compare chunks across files
        duplicates = []
        compared = set()

        for i, (file1, lines1, size1) in enumerate(file_contents):
            for j, (file2, lines2, size2) in enumerate(file_contents):
                if i == j or (i, j) in compared or (j, i) in compared:
                    continue

                compared.add((i, j))

                for idx1 in range(len(lines1) - min_lines + 1):
                    chunk1 = '\n'.join(lines1[idx1:idx1 + min_lines])

                    for idx2 in range(len(lines2) - min_lines + 1):
                        chunk2 = '\n'.join(lines2[idx2:idx2 + min_lines])
                        similarity = SequenceMatcher(None, chunk1, chunk2).ratio()

                        if similarity >= threshold:
                            duplicates.append({
                                'file1': file1,
                                'start_line1': idx1 + 1,
                                'end_line1': idx1 + min_lines,
                                'size1': size1,
                                'file2': file2,
                                'start_line2': idx2 + 1,
                                'end_line2': idx2 + min_lines,
                                'size2': size2,
                                'similarity': similarity,
                                'code': chunk1
                            })

        duplicates.sort(key=lambda x: x['similarity'], reverse=True)

        if not self.logger.silent:
            if duplicates:
                self.logger.info(f"\nFound {len(duplicates)} potential duplicate code blocks:")
                for i, dup in enumerate(duplicates[:10]):  # Show top 10 duplicates
                    size1_kb = dup['size1'] / 1024
                    size2_kb = dup['size2'] / 1024
                    self.logger.info(f"\nDuplicate #{i + 1} (Similarity: {dup['similarity']:.2f}):")
                    self.logger.info(f"  {dup['file1']} (lines {dup['start_line1']}-{dup['end_line1']}, Size: {size1_kb:.2f} KB)")
                    self.logger.info(f"  {dup['file2']} (lines {dup['start_line2']}-{dup['end_line2']}, Size: {size2_kb:.2f} KB)")
                    self.logger.info(f"\nCode:")
                    self.logger.info("```")
                    self.logger.info(dup['code'])
                    self.logger.info("```")

                if len(duplicates) > 10:
                    self.logger.info(f"\n(and {len(duplicates) - 10} more duplicates)")
            else:
                self.logger.info("\nNo duplicate code blocks found.")

            total_size_kb = total_size_bytes / 1024
            self.logger.info(f"\nTotal files processed: {file_count}")
            self.logger.info(f"Total size of processed files: {total_size_kb:.2f} KB")
            if file_count > 0:
                avg_size_kb = total_size_kb / file_count
                self.logger.info(f"Average file size: {avg_size_kb:.2f} KB")
