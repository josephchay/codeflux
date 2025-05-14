import os
import re

from operations.base import Operation, OperationStats
from scripts.commenter import GeminiCommentGenerator


class AutoCommentOperation(Operation):
    """Operation to add AI-generated comments to code files."""

    def __init__(self, file_handler, logger=None):
        """Initialize the AI-powered auto-comment operation."""
        super().__init__("autocomment", file_handler, logger)
        # Add missing statistics attributes
        self.stats.files_commented = 0
        self.stats.comments_added = 0

    def execute(self, source_dir, output_dir, **kwargs) -> OperationStats:
        """Execute the AI-powered auto-comment operation."""
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(output_dir)

        # Parse kwargs
        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])
        include_dirs = kwargs.get('include_dirs', None)
        include_exts = kwargs.get('include_exts', None)
        include_files = kwargs.get('include_files', None)
        api_key = kwargs.get('api_key', None)
        comment_level = kwargs.get('comment_level', 'standard')

        files_info = []
        self.stats.start_timer()

        # Create output directory
        os.makedirs(output_dir, exist_ok=True)

        # Initialize Gemini comment generator
        try:
            ai_generator = GeminiCommentGenerator(api_key=api_key)
            if not self.logger.silent:
                self.logger.info("Using Gemini 2.0 Flash model for AI-powered commenting")
        except Exception as e:
            if not self.logger.silent:
                self.logger.error(f"Failed to initialize Gemini comment generator: {e}")
                self.logger.error("Cannot proceed without Gemini API access")
            self.stats.stop_timer()
            return self.stats

        # Walk through source directory
        for root, dirs, files in os.walk(source_dir):
            self.stats.dirs_traversed += 1

            # Apply directory filters
            if include_dirs:
                rel_dir_parts = os.path.relpath(root, source_dir).split(os.sep)
                if not any(part in include_dirs for part in rel_dir_parts) and os.path.relpath(root, source_dir) != '.':
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

                if not self.file_handler.should_process_file(file, exclude_exts, exclude_files, include_exts,
                                                             include_files, rel_file_path):
                    self.stats.skipped_files += 1
                    continue

                # Process the file
                try:
                    # Read file content
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Get file size for reporting
                    file_size = os.path.getsize(file_path)

                    # Count original lines
                    original_lines = len(content.splitlines())

                    # Get language from file extension
                    _, file_ext = os.path.splitext(file)
                    language = file_ext.lstrip('.').lower()

                    # Generate comments
                    commented_content, comments_added = self._process_file_for_comments(
                        content, language, file_path, ai_generator, comment_level
                    )

                    # Count commented lines
                    commented_lines = len(commented_content.splitlines())

                    # Write to output file
                    output_file_path = os.path.join(output_dir, rel_file_path)
                    os.makedirs(os.path.dirname(output_file_path), exist_ok=True)

                    with open(output_file_path, 'w', encoding='utf-8') as f:
                        f.write(commented_content)

                    # Update statistics
                    self.stats.files_commented += 1
                    self.stats.comments_added += comments_added

                    # Add to files info for reporting
                    files_info.append({
                        "file": rel_file_path,
                        "size": file_size,
                        "original_lines": original_lines,
                        "commented_lines": commented_lines,
                        "comments_added": comments_added,
                        "status": "Commented" if comments_added > 0 else "No comments added"
                    })

                except Exception as e:
                    if not self.logger.silent:
                        self.logger.error(f"Error processing {rel_file_path}: {str(e)}")

                    files_info.append({
                        "file": rel_file_path,
                        "size": os.path.getsize(file_path) if os.path.exists(file_path) else 0,
                        "original_lines": 0,
                        "commented_lines": 0,
                        "comments_added": 0,
                        "status": f"Error: {str(e)}"
                    })

        self.stats.stop_timer()

        # Log results
        if not self.logger.silent and files_info:
            self.logger.info("[FILES PROCESSED]")
            self.logger.print_file_table(files_info, "AUTOCOMMENT")

        return self.stats

    def _process_file_for_comments(self, content, language, file_path, ai_generator, comment_level):
        """Process a file to add AI-generated comments."""
        # Extract code structures
        code_parts = self._extract_code_parts(content, language)

        # Sort parts by their position in reverse order (to insert comments from end to beginning)
        code_parts.sort(key=lambda x: x['start'], reverse=True)

        modified_content = content
        comments_added = 0

        # Add file header comment if needed
        if not self._has_header_comment(content, language):
            header_context = {
                "file_path": os.path.basename(file_path),
                "type": "file_header"
            }

            header_comment = ai_generator.generate_comment(content[:min(500, len(content))], header_context)
            formatted_comment = self._format_comment(header_comment, language, "header")

            modified_content = formatted_comment + "\n\n" + modified_content
            comments_added += 1

        # Process each part in reverse order (to maintain positions)
        for part in code_parts:
            context = {
                "file_path": os.path.basename(file_path),
                "type": part['type']
            }

            if part['type'] == 'class':
                context['class_name'] = part['name']
            elif part['type'] == 'function':
                context['function_name'] = part['name']
                if part.get('class'):
                    context['class_name'] = part['class']

            # Check if already has a comment
            if not self._has_existing_comment(modified_content, part['start']):
                comment = ai_generator.generate_comment(part['code'], context)
                formatted_comment = self._format_comment(comment, language, part['type'])

                # Insert the comment before the code part
                insert_pos = part['start']
                modified_content = modified_content[:insert_pos] + formatted_comment + "\n" + modified_content[
                                                                                              insert_pos:]
                comments_added += 1

        return modified_content, comments_added

    def _extract_code_parts(self, content, language):
        """Extract classes, functions, and other structures from code."""
        parts = []

        if language in ['py', 'python']:
            # Extract classes using regex
            class_pattern = r'class\s+(\w+)(?:$$.*?$$)?:'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                start_pos = match.start()

                # Get the class code
                # (simplified approach - in production you would parse the full class)
                parts.append({
                    'type': 'class',
                    'name': class_name,
                    'start': start_pos,
                    'code': match.group(0)[:100]  # Get the first 100 chars for context
                })

            # Extract functions using regex
            func_pattern = r'def\s+(\w+)\s*$$([^)]*)$$:'
            for match in re.finditer(func_pattern, content):
                func_name = match.group(1)
                start_pos = match.start()

                # Check if this is a method in a class
                lines = content[:start_pos].splitlines()
                if lines:
                    last_lines = lines[-3:]  # Check the last few lines
                    in_class = False
                    class_name = None

                    for line in last_lines:
                        class_match = re.search(r'class\s+(\w+)', line)
                        if class_match:
                            in_class = True
                            class_name = class_match.group(1)
                            break

                    parts.append({
                        'type': 'function',
                        'name': func_name,
                        'class': class_name if in_class else None,
                        'start': start_pos,
                        'code': match.group(0)[:100]  # Get the first 100 chars for context
                    })

        # Add similar patterns for other languages
        elif language in ['js', 'javascript', 'ts', 'typescript']:
            # Class pattern for JS/TS
            class_pattern = r'class\s+(\w+)(?:\s+extends\s+\w+)?[\s{]'
            for match in re.finditer(class_pattern, content):
                class_name = match.group(1)
                start_pos = match.start()

                parts.append({
                    'type': 'class',
                    'name': class_name,
                    'start': start_pos,
                    'code': content[start_pos:start_pos + 100]  # First 100 chars
                })

            # Function patterns for JS/TS
            func_patterns = [
                r'function\s+(\w+)\s*$$([^)]*)$$',  # Regular functions
                r'(?:const|let|var)\s+(\w+)\s*=\s*function\s*$$([^)]*)$$',  # Function expressions
                r'(?:const|let|var)\s+(\w+)\s*=\s*$$([^)]*)$$\s*=>'  # Arrow functions
            ]

            for pattern in func_patterns:
                for match in re.finditer(pattern, content):
                    func_name = match.group(1)
                    start_pos = match.start()

                    parts.append({
                        'type': 'function',
                        'name': func_name,
                        'start': start_pos,
                        'code': content[start_pos:start_pos + 100]  # First 100 chars
                    })

        return parts

    def _has_header_comment(self, content, language):
        """Check if the file already has a header comment."""
        lines = content.splitlines()[:5]  # Check first 5 lines

        if language in ['py', 'python']:
            for line in lines:
                if line.strip().startswith('"""') or line.strip().startswith('#'):
                    return True
        elif language in ['js', 'javascript', 'ts', 'typescript']:
            for line in lines:
                if line.strip().startswith('//') or line.strip().startswith('/*'):
                    return True

        return False

    def _has_existing_comment(self, content, position):
        """Check if there's already a comment before the given position."""
        lines = content[:position].splitlines()
        if not lines:
            return False

        # Check the last few lines before position
        last_lines = lines[-3:]
        for line in last_lines:
            line = line.strip()
            if line.startswith('"""') or line.startswith("'''") or line.startswith('//') or line.startswith(
                    '#') or line.startswith('/*'):
                return True

        return False

    def _format_comment(self, comment, language, comment_type):
        """Format the generated comment according to language conventions."""
        if not comment:
            return ""

        if language in ['py', 'python']:
            if comment_type in ['class', 'function', 'header']:
                return f'"""\n{comment}\n"""'
            else:
                # Single line or block comment with #
                lines = comment.split('\n')
                return '\n'.join(f'# {line}' for line in lines)

        elif language in ['js', 'javascript', 'ts', 'typescript']:
            if comment_type in ['class', 'function', 'header']:
                lines = comment.split('\n')
                result = ['/**']
                result.extend(f' * {line}' for line in lines)
                result.append(' */')
                return '\n'.join(result)
            else:
                # Single line comment
                if '\n' not in comment:
                    return f'// {comment}'
                else:
                    lines = comment.split('\n')
                    return '\n'.join(f'// {line}' for line in lines)

        # Default format for other languages
        return f'/* {comment} */'
