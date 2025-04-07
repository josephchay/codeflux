import os
import re
from constants import ALL_EXTENSIONS
from utils import get_relative_path


class SearchHandler:
    def __init__(self, extensions=None, exclude_dirs=None, exclude_exts=None, exclude_files=None):
        self.extensions = extensions or ALL_EXTENSIONS
        self.exclude_dirs = exclude_dirs or []
        self.exclude_exts = exclude_exts or []
        self.exclude_files = exclude_files or []

    def search_by_extension(self, source_dir, extensions, silent=False):
        """Search for files with specific extensions."""
        results = []
        file_count = 0

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if any(file.lower().endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    rel_path = get_relative_path(file_path, source_dir)

                    # Skip excluded files
                    if self.is_excluded_file(rel_path):
                        continue

                    results.append(rel_path)
                    file_count += 1

                    if not silent:
                        print(f"Found: {rel_path}")

        if not silent:
            print(f"\nTotal files found: {file_count}")

        return results

    def search_by_pattern(self, source_dir, pattern, extensions=None, silent=False):
        """Search for files containing a specific pattern."""
        results = []
        file_count = 0
        match_count = 0

        extensions = extensions or self.extensions

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue

                file_path = os.path.join(root, file)
                rel_path = get_relative_path(file_path, source_dir)

                # Skip excluded files
                if self.is_excluded_file(rel_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        matches = re.finditer(pattern, content)
                        found_matches = list(matches)

                        if found_matches:
                            file_count += 1
                            match_count += len(found_matches)

                            if not silent:
                                print(f"\nFile: {rel_path}")
                                for i, match in enumerate(found_matches):
                                    start = max(0, match.start() - 20)
                                    end = min(len(content), match.end() + 20)
                                    context = content[start:end].replace('\n', ' ')
                                    print(f"  Match {i + 1}: ...{context}...")

                            results.append((rel_path, found_matches))
                except UnicodeDecodeError:
                    # Skip binary files
                    continue

        if not silent:
            print(f"\nTotal files with matches: {file_count}")
            print(f"Total matches found: {match_count}")

        return results

    def search_by_size(self, source_dir, min_size=None, max_size=None, extensions=None, silent=False):
        """Search for files within a size range (in KB)."""
        results = []
        file_count = 0

        extensions = extensions or self.extensions
        min_size_bytes = min_size * 1024 if min_size is not None else None
        max_size_bytes = max_size * 1024 if max_size is not None else None

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]

            for file in files:
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue

                file_path = os.path.join(root, file)
                rel_path = get_relative_path(file_path, source_dir)

                # Skip excluded files
                if self.is_excluded_file(rel_path):
                    continue

                file_size = os.path.getsize(file_path)

                if ((min_size_bytes is None or file_size >= min_size_bytes) and
                        (max_size_bytes is None or file_size <= max_size_bytes)):
                    file_size_kb = file_size / 1024
                    results.append((rel_path, file_size_kb))
                    file_count += 1

                    if not silent:
                        print(f"Found: {rel_path} (Size: {file_size_kb:.2f} KB)")

        if not silent:
            print(f"\nTotal files found: {file_count}")

        return results

    def is_excluded_file(self, file_rel_path):
        """Check if a file should be excluded based on path."""
        norm_rel_path = file_rel_path.replace('\\', '/')

        for exclude_pattern in self.exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if norm_rel_path == norm_exclude:
                return True

        return False
