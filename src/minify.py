import json
import os
import re
import subprocess
import sys
import tempfile

import python_minifier
import yaml
from ruamel.yaml import YAML


def minify_php(source, continue_on_error=False):
    try:
        with tempfile.NamedTemporaryFile(suffix='.php', mode='w', encoding='utf-8', delete=False) as temp_in:
            temp_in.write(source)
            temp_in_path = temp_in.name

        temp_out_path = temp_in_path + '.min'
        minify_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'minify', 'php_minify.js')

        try:
            # Run the minifier script which uses @cedx/php-minifier
            result = subprocess.run(
                ['node', minify_script, temp_in_path, temp_out_path],
                capture_output=True,
                text=True,
                check=True
            )

            # Read the minified output
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                return minified, None
            else:
                warning = "PHP minification failed: Output file not created"
                if continue_on_error:
                    return source, warning
                else:
                    raise RuntimeError(warning)

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "No details available"
            warning = f"PHP minification failed: {error_msg}"
            if continue_on_error:
                return source, warning
            else:
                raise RuntimeError(warning)

        finally:
            # Clean up temporary files
            if os.path.exists(temp_in_path):
                os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                os.unlink(temp_out_path)

    except Exception as e:
        warning = f"PHP minification exception: {str(e)}"
        if continue_on_error:
            return source, warning
        else:
            raise RuntimeError(warning)


def safely_minify_python_code(code, continue_on_error=False):
    """Attempt to minify Python code with extensive error handling."""
    if not code or not code.strip():
        return code, None

    try:
        # Check for common issues that cause minification errors
        # Look for invalid decimal literals like leading zeros
        if re.search(r'\b0\d+\b', code):
            warning = "Detected invalid decimal literals (numbers with leading zeros)"
            return code, warning

        # Try to minify the code
        minified = python_minifier.minify(code)
        return minified, None
    except SyntaxError as e:
        warning = f"Python minification syntax error: {str(e)}"
        if continue_on_error:
            return code, warning
        else:
            raise
    except Exception as e:
        warning = f"Python minification error: {str(e)}"
        if continue_on_error:
            return code, warning
        else:
            raise


def minify_shell_script(source, continue_on_error=False):
    if not source or not source.strip():
        return source, None

    try:
        # Remove comments (lines starting with #, but preserve shebang)
        lines = source.splitlines()
        result = []

        # Add shebang line if it exists
        if lines and lines[0].startswith('#!'):
            result.append(lines[0])
            lines = lines[1:]

        for line in lines:
            # Skip comment lines
            if line.strip().startswith('#'):
                continue

            # For lines with inline comments, keep only the code part
            if '#' in line:
                code_part = line.split('#', 1)[0].rstrip()
                if code_part:  # Only add if there's actual code
                    result.append(code_part)
            else:
                if line.strip():  # Skip empty lines
                    result.append(line)

        # Collapse multiple empty lines into one
        minified = '\n'.join(result)
        # Ensure we don't return None
        if minified is None:
            return source, "Shell minification produced None, using original content"
        return minified, None

    except Exception as e:
        warning = f"Shell script minification error: {str(e)}"
        if continue_on_error:
            return source, warning
        else:
            raise RuntimeError(warning)


def minify_code(source, file_extension, continue_on_error=False):
    if not source or not source.strip():
        return source, None

    ext_lower = file_extension.lower() if file_extension else ''

    # Skip minification for certain file types
    if any(ext_lower.endswith(ext) for ext in
           ['.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.mdwn', '.mdtxt', '.mdtext', '.txt', '.rst']):
        return source, None
    if ext_lower.endswith('.py'):
        try:
            return safely_minify_python_code(source, True)
        except Exception as e:
            warning = f"Failed to minify Python code: {str(e)}"
            if not continue_on_error:
                print(f"ERROR: {warning}")
                sys.exit(1)
            return source, warning
    elif ext_lower.endswith('.ipynb'):
        try:
            notebook = json.loads(source)
            warnings = []

            if 'cells' in notebook:
                for cell_index, cell in enumerate(notebook['cells']):
                    if cell.get('cell_type') == 'code' and 'source' in cell and cell.get('language', 'python') == 'python':
                        if isinstance(cell['source'], list):
                            code = ''.join(cell['source'])
                            try:
                                minified_code, cell_warning = safely_minify_python_code(code, True)  # Always continue on error for cells
                                if cell_warning:
                                    cell_num = cell_index + 1
                                    warnings.append(f"Cell #{cell_num}: {cell_warning}")
                                cell['source'] = minified_code
                            except Exception as e:
                                cell_num = cell_index + 1
                                warnings.append(f"Cell #{cell_num}: {str(e)}")
                                # Don't modify this cell's source

            warning = "; ".join(warnings) if warnings else None
            return json.dumps(notebook, separators=(',', ':')), warning

        except json.JSONDecodeError as e:
            warning = f"Invalid notebook JSON format: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
        except Exception as e:
            warning = f"Error processing notebook: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx']):
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', encoding='utf-8',
                                             delete=False) as temp_in:
                temp_in.write(source)
                temp_in_path = temp_in.name
            temp_out_path = temp_in_path + '.min'
            minify_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'minify', 'jsts_minify.js')
            try:
                result = subprocess.run(
                    ['node', minify_script, temp_in_path, temp_out_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                os.unlink(temp_in_path)
                if os.path.exists(temp_out_path):
                    os.unlink(temp_out_path)

                warning = f"JS/TS minification failed: {e.stderr if e.stderr else e}"
                if continue_on_error:
                    return source, warning
                else:
                    print(f"ERROR: {warning}")
                    print("Operation aborted due to JS/TS minification error.")
                    sys.exit(1)

            os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                os.unlink(temp_out_path)
                return minified, None
            else:
                warning = "JS/TS minification failed: Output file not created"
                if continue_on_error:
                    return source, warning
                else:
                    print(f"ERROR: {warning}")
                    print("Operation aborted due to JS/TS minification error.")
                    sys.exit(1)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            warning = f"Encoding error during JS/TS minification: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.css', '.scss', '.sass', '.less']):
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', encoding='utf-8',
                                             delete=False) as temp_in:
                temp_in.write(source)
                temp_in_path = temp_in.name
            temp_out_path = temp_in_path + '.min'
            minify_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'minify', 'css_minify.js')
            try:
                result = subprocess.run(
                    ['node', minify_script, temp_in_path, temp_out_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                os.unlink(temp_in_path)
                if os.path.exists(temp_out_path):
                    os.unlink(temp_out_path)

                warning = f"CSS minification failed: {e.stderr if e.stderr else e}"
                if continue_on_error:
                    return source, warning
                else:
                    print(f"ERROR: {warning}")
                    print("Operation aborted due to CSS minification error.")
                    sys.exit(1)

            os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                os.unlink(temp_out_path)
                return minified, None
            else:
                warning = "CSS minification failed: Output file not created"
                if continue_on_error:
                    return source, warning
                else:
                    print(f"ERROR: {warning}")
                    print("Operation aborted due to CSS minification error.")
                    sys.exit(1)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            warning = f"Encoding error during CSS minification: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.html', '.htm', '.xhtml', '.shtml']):
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', encoding='utf-8',
                                             delete=False) as temp_in:
                temp_in.write(source)
                temp_in_path = temp_in.name
            temp_out_path = temp_in_path + '.min'
            minify_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'scripts', 'minify', 'html_minify.js')
            try:
                result = subprocess.run(
                    ['node', minify_script, temp_in_path, temp_out_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
            except subprocess.CalledProcessError as e:
                os.unlink(temp_in_path)
                if os.path.exists(temp_out_path):
                    os.unlink(temp_out_path)

                warning = f"HTML minification failed: {e.stderr if e.stderr else e}"
                if continue_on_error:
                    return source, warning
                else:
                    print(f"ERROR: {warning}")
                    print("Operation aborted due to HTML minification error.")
                    sys.exit(1)

            os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                os.unlink(temp_out_path)
                return minified, None
            else:
                warning = "HTML minification failed: Output file not created"
                if continue_on_error:
                    return source, warning
                else:
                    print(f"ERROR: {warning}")
                    print("Operation aborted due to HTML minification error.")
                    sys.exit(1)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            warning = f"Encoding error during HTML minification: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.php', '.phtml', '.php5', '.php7', '.phps']):
        return minify_php(source, continue_on_error)
    elif any(ext_lower.endswith(ext) for ext in ['.json', '.jsonl', '.geojson', '.json5', '.ndjson']):
        try:
            parsed_json = json.loads(source)
            return json.dumps(parsed_json, separators=(',', ':')), None
        except json.JSONDecodeError as e:
            warning = f"Invalid JSON content: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.yaml', '.yml']):
        try:
            yaml_parser = YAML(typ='safe')
            data = yaml_parser.load(source)
            flow_style = True

            if flow_style:
                minified = yaml.dump(data, default_flow_style=True, width=float('inf'), allow_unicode=True,
                                     sort_keys=False)
                minified = minified.strip()
                minified = re.sub(r',\s+', ', ', minified)
                minified = re.sub(r':\s+', ': ', minified)
                minified = re.sub(r'\s+}', '}', minified)
                minified = re.sub(r'{\s+', '{', minified)
                if minified.endswith('\n'):
                    minified = minified[:-1]
            else:
                minified = yaml.dump(data, default_flow_style=False, indent=2, width=float('inf'), allow_unicode=True,
                                     sort_keys=False)
                minified = re.sub(r'^\s*#.*$', '', minified, flags=re.MULTILINE)
                minified = re.sub(r'\n\s*\n', '\n', minified)
                minified = re.sub(r'[ \t]+$', '', minified, flags=re.MULTILINE)
                lines = minified.split('\n')
                for i, line in enumerate(lines):
                    match = re.match(r'^(\s*\w+:\s+)["\']([\w\s\-]+)["\']$', line)
                    if match:
                        prefix, value = match.groups()
                        if not (value.lower() in ('yes', 'no', 'true', 'false', 'null', 'on', 'off') or
                                re.search(r'^\d', value) or re.search(r'[:#{}[\],&*!|>\'"%@`]', value)):
                            lines[i] = f"{prefix}{value}"
                minified = '\n'.join(lines)

            return minified.strip(), None
        except Exception as e:
            warning = f"YAML minification failed: {str(e)}"
            if continue_on_error:
                return source, warning
            else:
                print(f"ERROR: {warning}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.sh', '.bash', '.zsh']):
        return minify_shell_script(source, continue_on_error)

    # Return the source without modifications for any other file types
    if source is None:
        return "", "Source content was None"
    return source, None
