import ast
import datetime
import os
import re
from difflib import SequenceMatcher

from constants import ALL_EXTENSIONS
from utils import get_relative_path


class Searcher:
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
                if self.is_excluded_file(rel_path):
                    continue

                file_size = os.path.getsize(file_path)
                if (min_size_bytes is None or file_size >= min_size_bytes) and (max_size_bytes is None or file_size <= max_size_bytes):
                    file_size_kb = file_size / 1024
                    results.append((rel_path, file_size_kb))
                    file_count += 1

                    if not silent:
                        print(f"Found: {rel_path} (Size: {file_size_kb:.2f} KB)")

        if not silent:
            print(f"\nTotal files found: {file_count}")

        return results

    def search_by_date(self, source_dir, start_date, end_date=None, extensions=None, silent=False):
        results = []
        file_count = 0

        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").timestamp()
        if end_date:
            end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d").timestamp()
        else:
            end_date = datetime.datetime.now().timestamp()
        extensions = extensions or self.extensions

        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue

                file_path = os.path.join(root, file)
                rel_path = get_relative_path(file_path, source_dir)

                if self.is_excluded_file(rel_path):
                    continue

                mod_time = os.path.getmtime(file_path)
                if start_date <= mod_time <= end_date:
                    mod_date = datetime.datetime.fromtimestamp(mod_time).strftime("%Y-%m-%d %H:%M:%S")
                    results.append((rel_path, mod_date))
                    file_count += 1

                    if not silent:
                        print(f"Found: {rel_path} (Modified: {mod_date})")

        if not silent:
            print(f"\nTotal files found: {file_count}")

        return results

    def search_imports(self, source_dir, module_name, extensions=None, silent=False):
        results = []
        file_count = 0
        import_count = 0

        # Default to Python files only for this search
        extensions = extensions or ['.py']
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue

                file_path = os.path.join(root, file)
                rel_path = get_relative_path(file_path, source_dir)
                if self.is_excluded_file(rel_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

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

                        if not silent:
                            print(f"\nFile: {rel_path}")
                            for import_stmt, line_num in imports:
                                print(f"  Line {line_num}: {import_stmt}")

                        results.append((rel_path, imports))

                except (UnicodeDecodeError, SyntaxError):
                    # Skip files that can't be parsed
                    continue

        if not silent:
            print(f"\nTotal files with imports: {file_count}")
            print(f"Total imports found: {import_count}")

        return results

    def search_duplicates(self, source_dir, min_lines=5, threshold=0.8, extensions=None, silent=False):
        file_contents = []
        extensions = extensions or self.extensions
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in self.exclude_dirs]
            for file in files:
                if not any(file.lower().endswith(ext) for ext in extensions):
                    continue

                file_path = os.path.join(root, file)
                rel_path = get_relative_path(file_path, source_dir)
                if self.is_excluded_file(rel_path):
                    continue

                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    lines = content.splitlines()
                    if len(lines) >= min_lines:
                        file_contents.append((rel_path, lines))

                except UnicodeDecodeError:
                    # Skip binary files
                    continue

        # Now compare chunks across files
        duplicates = []
        compared = set()
        for i, (file1, lines1) in enumerate(file_contents):
            for j, (file2, lines2) in enumerate(file_contents):
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
                                'file2': file2,
                                'start_line2': idx2 + 1,
                                'end_line2': idx2 + min_lines,
                                'similarity': similarity,
                                'code': chunk1
                            })

        duplicates.sort(key=lambda x: x['similarity'], reverse=True)
        if not silent:
            if duplicates:
                print(f"\nFound {len(duplicates)} potential duplicate code blocks:")
                for i, dup in enumerate(duplicates):
                    print(f"\nDuplicate #{i + 1} (Similarity: {dup['similarity']:.2f}):")
                    print(f"  {dup['file1']} (lines {dup['start_line1']}-{dup['end_line1']})")
                    print(f"  {dup['file2']} (lines {dup['start_line2']}-{dup['end_line2']})")
                    print(f"\nCode:")
                    print("```")
                    print(dup['code'])
                    print("```")
            else:
                print("\nNo duplicate code blocks found.")

        return duplicates

    def is_excluded_file(self, file_rel_path):
        """Check if a file should be excluded based on path."""
        norm_rel_path = file_rel_path.replace('\\', '/')

        for exclude_pattern in self.exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if norm_rel_path == norm_exclude:
                return True

        return False
