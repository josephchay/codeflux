# operations/autocomment.py
"""
Auto-comment Operation: Automatically adds comments to code files.
"""

import ast
import os
import re
from typing import Dict, List, Optional, Any, Tuple

from file_handler import FileHandler
from operations.base import Operation, OperationStats
from utils.logging import Logger


class AutoCommentOperation(Operation):
    """Operation to automatically add comments to code files."""

    def __init__(self, file_handler: FileHandler, logger: Logger = None):
        """Initialize the auto-comment operation."""
        super().__init__("autocomment", file_handler, logger)

    def execute(self, source_dir: str, output_dir: str, **kwargs) -> OperationStats:
        """
        Execute the auto-comment operation.

        Args:
            source_dir: Source directory containing files to comment
            output_dir: Output directory for commented files
            **kwargs: Additional arguments:
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - comment_level: Level of commenting (minimal, standard, verbose)
                - add_docstrings: Whether to add docstrings
                - add_inline: Whether to add inline comments
                - add_header: Whether to add file headers
                - preserve_existing: Whether to preserve existing comments
                - language_style: Comment style override for specific languages

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

        comment_level = kwargs.get('comment_level', 'standard')
        add_docstrings = kwargs.get('add_docstrings', True)
        add_inline = kwargs.get('add_inline', True)
        add_header = kwargs.get('add_header', True)
        preserve_existing = kwargs.get('preserve_existing', True)
        language_style = kwargs.get('language_style', {})

        files_info = []
        self.stats.start_timer()

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        if not self.logger.silent:
            self.logger.info(f"Processing files for auto-commenting...")
            self.logger.info(f"Comment level: {comment_level}")
            self.logger.info(f"Add docstrings: {add_docstrings}")
            self.logger.info(f"Add inline comments: {add_inline}")
            self.logger.info(f"Add file headers: {add_header}")
            self.logger.info(f"Preserve existing comments: {preserve_existing}")

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

            # Process files
            for file in files:
                self.stats.total_files_processed += 1
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, source_dir)

                # Check if file should be processed
                if not self.file_handler.handles_file(file):
                    self.stats.skipped_files += 1
                    continue

                if not self.file_handler.should_process_file(
                        file, exclude_exts, exclude_files, include_exts, include_files, rel_file_path
                ):
                    self.stats.skipped_files += 1
                    continue

                # Process the file
                try:
                    # Detect file type and language
                    file_ext = os.path.splitext(file)[1].lower()
                    language = self._detect_language(file_ext)

                    if not language:
                        self.stats.skipped_files += 1
                        continue

                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Process comments based on language
                    commented_content = self._add_comments_to_content(
                        content, language, file_path,
                        comment_level=comment_level,
                        add_docstrings=add_docstrings,
                        add_inline=add_inline,
                        add_header=add_header,
                        preserve_existing=preserve_existing,
                        language_style=language_style
                    )

                    # Write to output file
                    output_file_path = os.path.join(output_dir, rel_file_path)
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(commented_content)

                    self.stats.files_copied += 1

                    # Update statistics
                    original_lines = len(content.splitlines())
                    commented_lines = len(commented_content.splitlines())
                    comments_added = commented_lines - original_lines

                    file_info = {
                        "file": rel_file_path,
                        "size": os.path.getsize(output_file_path),
                        "original_lines": original_lines,
                        "commented_lines": commented_lines,
                        "comments_added": comments_added,
                        "status": "Success"
                    }
                    files_info.append(file_info)

                except Exception as e:
                    self.logger.error(f"Error processing {rel_file_path}: {str(e)}")
                    file_info = {
                        "file": rel_file_path,
                        "size": 0,
                        "original_lines": 0,
                        "commented_lines": 0,
                        "comments_added": 0,
                        "status": f"Error: {str(e)}"
                    }

                    files_info.append(file_info)

        # Display results
        if not self.logger.silent and files_info:
            self.logger.info("\n[FILES PROCESSED]")
            self.logger.print_file_table(files_info, "autocomment")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "autocomment")

        return self.stats

    def _detect_language(self, file_ext: str) -> Optional[str]:
        """Detect programming language from file extension."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.c': 'c',
            '.cpp': 'cpp',
            '.cc': 'cpp',
            '.cxx': 'cpp',
            '.h': 'c',
            '.hpp': 'cpp',
            '.cs': 'csharp',
            '.php': 'php',
            '.rb': 'ruby',
            '.go': 'go',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.r': 'r',
            '.lua': 'lua',
            '.pl': 'perl',
            '.sh': 'shell',
            '.bash': 'shell',
            '.zsh': 'shell',
            '.ps1': 'powershell',
            '.psm1': 'powershell',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.xml': 'xml',
            '.html': 'html',
            '.htm': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.sass': 'sass',
            '.sql': 'sql',
            '.md': 'markdown',
            '.markdown': 'markdown',
        }
        return language_map.get(file_ext.lower())

    def _add_comments_to_content(self, content: str, language: str, file_path: str, **kwargs) -> str:
        """Add comments to content based on language."""
        comment_processors = {
            'python': self._process_python_comments,
            'javascript': self._process_javascript_comments,
            'typescript': self._process_javascript_comments,  # Similar to JS
        }

        processor = comment_processors.get(language, self._process_generic_comments)
        return processor(content, file_path, **kwargs)

    def _process_python_comments(self, content: str, file_path: str, **kwargs) -> str:
        """Process Python files to add comments."""
        add_header = kwargs.get('add_header', True)
        add_docstrings = kwargs.get('add_docstrings', True)
        add_inline = kwargs.get('add_inline', True)
        preserve_existing = kwargs.get('preserve_existing', True)
        comment_level = kwargs.get('comment_level', 'standard')

        try:
            # Parse the Python AST
            tree = ast.parse(content)

            # Add file header if needed
            file_header = ""
            if add_header and not self._has_file_header(content):
                file_header = self._generate_file_header(file_path, 'python')

            # Process AST to add comments
            commenter = PythonCommenter(
                add_docstrings=add_docstrings,
                add_inline=add_inline,
                preserve_existing=preserve_existing,
                comment_level=comment_level
            )

            modified_content = commenter.process(tree, content)

            # Combine header and content
            if file_header:
                modified_content = file_header + "\n\n" + modified_content

            return modified_content

        except SyntaxError:
            # If parsing fails, return original content
            self.logger.warning(f"Syntax error in {file_path}, skipping auto-comment")
            return content
        except Exception as e:
            # Catch any other errors and return original content
            self.logger.warning(f"Error processing {file_path}: {str(e)}, using original content")
            return content

    def _process_javascript_comments(self, content: str, file_path: str, **kwargs) -> str:
        """Process JavaScript/TypeScript files to add comments."""
        # This would use a JavaScript parser like Esprima
        # For now, we'll use regex-based approach
        add_header = kwargs.get('add_header', True)
        preserve_existing = kwargs.get('preserve_existing', True)

        modified_content = content

        # Add file header
        if add_header and not self._has_file_header(content):
            file_header = self._generate_file_header(file_path, 'javascript')
            modified_content = file_header + "\n\n" + modified_content

        # Add function comments
        function_pattern = r'(function\s+(\w+)\s*\([^)]*\)|(\w+)\s*=\s*function\s*\([^)]*\)|(\w+)\s*=\s*\([^)]*\)\s*=>)'

        def add_function_comment(match):
            if preserve_existing and self._has_preceding_comment(modified_content, match.start()):
                return match.group(0)

            func_name = match.group(2) or match.group(3) or match.group(4)
            comment = f"/**\n * {func_name} function\n */\n"
            return comment + match.group(0)

        modified_content = re.sub(function_pattern, add_function_comment, modified_content)

        return modified_content

    def _process_generic_comments(self, content: str, file_path: str, **kwargs) -> str:
        """Generic comment processor for unsupported languages."""
        # Just add a file header for now
        add_header = kwargs.get('add_header', True)

        if add_header and not self._has_file_header(content):
            file_header = self._generate_file_header(file_path, 'generic')
            return file_header + "\n\n" + content

        return content

    def _has_file_header(self, content: str) -> bool:
        """Check if file already has a header comment."""
        lines = content.split('\n')
        if not lines:
            return False

        # Check first few lines for common header patterns
        header_patterns = [
            r'^#!',  # Shebang
            r'^/\*\*',  # Block comment
            r'^/\*',  # Block comment
            r'^"""',  # Python docstring
            r"^'''",  # Python docstring
            r'^//',  # Line comment
            r'^#',  # Hash comment
            r'^--',  # SQL comment
        ]

        for i, line in enumerate(lines[:10]):  # Check first 10 lines
            for pattern in header_patterns:
                if re.match(pattern, line.strip()):
                    return True

        return False

    def _generate_file_header(self, file_path: str, language: str) -> str:
        """Generate a file header comment."""
        import datetime

        filename = os.path.basename(file_path)
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        headers = {
            'python': f'''"""
{filename}

Auto-generated comments by CodeFlux
Created: {date_str}
"""''',
            'javascript': f'''/**
 * {filename}
 * 
 * Auto-generated comments by CodeFlux
 * Created: {date_str}
 */''',
            'java': f'''/**
 * {filename}
 * 
 * Auto-generated comments by CodeFlux
 * Created: {date_str}
 */''',
            'c': f'''/*
 * {filename}
 * 
 * Auto-generated comments by CodeFlux
 * Created: {date_str}
 */''',
            'shell': f'''#!/usr/bin/env bash
#
# {filename}
#
# Auto-generated comments by CodeFlux
# Created: {date_str}
#''',
            'generic': f'''/*
 * {filename}
 * 
 * Auto-generated comments by CodeFlux
 * Created: {date_str}
 */'''
        }

        return headers.get(language, headers['generic'])

    def _has_preceding_comment(self, content: str, position: int) -> bool:
        """Check if there's already a comment before this position."""
        # Simplified check - looks for comment in the previous lines
        lines_before = content[:position].split('\n')
        if len(lines_before) < 2:
            return False

        # Check last few lines for comments
        for line in lines_before[-3:]:
            if any(pattern in line.strip() for pattern in ['#', '//', '/*', '*/', '"""', "'''"]):
                return True

        return False


class PythonCommenter(ast.NodeTransformer):
    """Add comments to Python code using AST transformation."""

    def __init__(self, add_docstrings: bool = True, add_inline: bool = True,
                 preserve_existing: bool = True, comment_level: str = 'standard'):
        self.add_docstrings = add_docstrings
        self.add_inline = add_inline
        self.preserve_existing = preserve_existing
        self.comment_level = comment_level
        self.source_lines = []

    def process(self, tree: ast.AST, source: str) -> str:
        """Process AST and add comments."""
        self.source_lines = source.splitlines()

        # Track which lines need comments
        self.comments_to_add = {}

        # Visit all nodes
        self.visit(tree)

        # Add comments to source
        return self._apply_comments(source)

    def visit_FunctionDef(self, node: ast.FunctionDef) -> ast.FunctionDef:
        """Add docstrings to functions."""
        if self.add_docstrings and not ast.get_docstring(node):
            # Generate docstring
            docstring = self._generate_function_docstring(node)

            # Add to comments
            self.comments_to_add[node.lineno] = {
                'type': 'docstring',
                'content': docstring,
                'indent': self._get_indent(node.lineno)
            }

        # Add inline comments for complex logic
        if self.add_inline and self.comment_level in ['standard', 'verbose']:
            self._add_inline_comments(node)

        self.generic_visit(node)
        return node

    def visit_ClassDef(self, node: ast.ClassDef) -> ast.ClassDef:
        """Add docstrings to classes."""
        if self.add_docstrings and not ast.get_docstring(node):
            # Generate docstring
            docstring = self._generate_class_docstring(node)

            # Add to comments
            self.comments_to_add[node.lineno] = {
                'type': 'docstring',
                'content': docstring,
                'indent': self._get_indent(node.lineno)
            }

        self.generic_visit(node)
        return node

    def visit_If(self, node: ast.If) -> ast.If:
        """Add comments to if statements."""
        if self.add_inline and self.comment_level in ['standard', 'verbose']:
            # Add comment explaining the condition
            if self._is_complex_condition(node.test):
                comment = self._explain_condition(node.test)
                if comment:
                    self.comments_to_add[node.lineno] = {
                        'type': 'inline',
                        'content': f"# {comment}",
                        'indent': self._get_indent(node.lineno),
                        'position': 'before'
                    }

        self.generic_visit(node)
        return node

    def visit_For(self, node: ast.For) -> ast.For:
        """Add comments to for loops."""
        if self.add_inline and self.comment_level in ['standard', 'verbose']:
            # Add comment explaining the loop
            comment = self._explain_loop(node)
            if comment:
                self.comments_to_add[node.lineno] = {
                    'type': 'inline',
                    'content': f"# {comment}",
                    'indent': self._get_indent(node.lineno),
                    'position': 'before'
                }

        self.generic_visit(node)
        return node

    def _generate_function_docstring(self, node: ast.FunctionDef) -> str:
        """Generate a docstring for a function."""
        params = []
        for arg in node.args.args:
            params.append(f"    {arg.arg}: Description of {arg.arg}")

        returns = "    Description of return value" if node.returns else ""

        # Basic docstring template
        docstring = f'"""{node.name} function.\n\n'

        if params:
            docstring += "Args:\n" + "\n".join(params) + "\n\n"

        if returns:
            docstring += "Returns:\n" + returns + "\n"

        docstring += '"""'

        return docstring

    def _generate_class_docstring(self, node: ast.ClassDef) -> str:
        """Generate a docstring for a class."""
        # Get class methods
        methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]

        docstring = f'"""{node.name} class.\n\n'

        if methods:
            docstring += "Methods:\n"
            for method in methods:
                if not method.startswith('_'):  # Skip private methods
                    docstring += f"    {method}: Description of {method}\n"

        docstring += '"""'

        return docstring

    def _is_complex_condition(self, node: ast.AST) -> bool:
        """Check if a condition is complex enough to warrant a comment."""
        # Count operators
        operators = 0
        for child in ast.walk(node):
            if isinstance(child, (ast.BoolOp, ast.Compare)):
                operators += 1

        return operators > 2  # Arbitrary threshold

    def _explain_condition(self, node: ast.AST) -> str:
        """Generate explanation for a condition."""
        if isinstance(node, ast.Compare):
            return "Check if condition is met"
        elif isinstance(node, ast.BoolOp):
            return "Complex boolean condition"
        else:
            return ""

    def _explain_loop(self, node: ast.For) -> str:
        """Generate explanation for a loop."""
        if isinstance(node.iter, ast.Call):
            if isinstance(node.iter.func, ast.Name):
                if node.iter.func.id == 'range':
                    return "Iterate over range"
                elif node.iter.func.id == 'enumerate':
                    return "Iterate with index"
        elif isinstance(node.iter, ast.Name):
            return f"Iterate over {node.iter.id}"

        return "Loop iteration"

    def _get_indent(self, lineno: int) -> str:
        """Get indentation for a line."""
        if lineno <= len(self.source_lines):
            line = self.source_lines[lineno - 1]
            return re.match(r'^(\s*)', line).group(1)
        return ""

    def _add_inline_comments(self, node: ast.AST):
        """Add inline comments to AST nodes (placeholder implementation)."""
        pass

    def _apply_comments(self, source: str) -> str:
        """Apply comments to source code."""
        lines = source.splitlines()

        # Sort comments by line number (reverse order to avoid offset issues)
        sorted_comments = sorted(self.comments_to_add.items(), key=lambda x: x[0], reverse=True)

        for lineno, comment_info in sorted_comments:
            if lineno <= len(lines):
                indent = comment_info['indent']
                content = comment_info['content']

                if comment_info['type'] == 'docstring':
                    # Add docstring after function/class definition
                    if lineno < len(lines):
                        # Add proper indentation to each line of docstring
                        docstring_lines = content.splitlines()
                        indented_docstring = [indent + '    ' + line if line else '' for line in docstring_lines]
                        lines.insert(lineno, '\n'.join(indented_docstring))
                elif comment_info['type'] == 'inline':
                    # Add inline comment
                    position = comment_info.get('position', 'before')
                    if position == 'before':
                        lines.insert(lineno - 1, indent + content)
                    else:  # end of line
                        lines[lineno - 1] += '  ' + content

        return '\n'.join(lines)
