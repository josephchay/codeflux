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
        script_dir = os.path.dirname(os.path.abspath(__file__))
        minify_script = os.path.join(script_dir, 'scripts', 'php_minify.js')

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
                return minified
            else:
                if continue_on_error:
                    print("WARNING: PHP minification failed. Output file not created. Using original content.")
                    return source
                else:
                    raise RuntimeError("PHP minification failed: Output file not created")

        except subprocess.CalledProcessError as e:
            error_msg = e.stderr.strip() if e.stderr else "No details available"
            if continue_on_error:
                print(f"WARNING: PHP minification failed. {error_msg}. Using original content.")
                return source
            else:
                raise RuntimeError(f"PHP minification failed: {error_msg}")

        finally:
            # Clean up temporary files
            if os.path.exists(temp_in_path):
                os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                os.unlink(temp_out_path)

    except Exception as e:
        if continue_on_error:
            print(f"WARNING: PHP minification exception: {str(e)}. Using original content.")
            return source
        else:
            raise RuntimeError(f"PHP minification failed: {str(e)}")


def minify_code(source, file_extension, continue_on_error=False):
    if not source or not source.strip():
        return source

    ext_lower = file_extension.lower() if file_extension else ''

    if any(ext_lower.endswith(ext) for ext in ['.md', '.markdown', '.mdown', '.mkdn', '.mkd', '.mdwn', '.mdtxt', '.mdtext', '.txt', '.rst']):
        return source
    if ext_lower.endswith('.py'):
        try:
            return python_minifier.minify(source)
        except Exception as e:
            if continue_on_error:
                print(f"WARNING: Failed to minify Python code: {str(e)}. Using original code.")
                return source
            else:
                print(f"ERROR: Failed to minify Python code: {str(e)}")
                sys.exit(1)
    elif ext_lower.endswith('.ipynb'):
        try:
            notebook = json.loads(source)
            if 'cells' in notebook:
                for cell in notebook['cells']:
                    if cell.get('cell_type') == 'code' and 'source' in cell and cell.get('language', 'python') == 'python':
                        if isinstance(cell['source'], list):
                            code = ''.join(cell['source'])
                            try:
                                minified_code = python_minifier.minify(code)
                                cell['source'] = minified_code
                            except Exception as e:
                                if continue_on_error:
                                    print(f"WARNING: Failed to minify a code cell: {str(e)}. Using original code.")
                                else:
                                    print(f"ERROR: Failed to minify a code cell: {str(e)}")
                                    sys.exit(1)

            return json.dumps(notebook, separators=(',', ':'))
        except json.JSONDecodeError as e:
            if continue_on_error:
                print(f"WARNING: Invalid notebook JSON format: {str(e)}. Using original content.")
                return source
            else:
                print(f"ERROR: Invalid notebook JSON format: {str(e)}")
                sys.exit(1)
        except Exception as e:
            if continue_on_error:
                print(f"WARNING: Error processing notebook: {str(e)}. Using original content.")
                return source
            else:
                print(f"ERROR: Error processing notebook: {str(e)}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.js', '.jsx', '.ts', '.tsx']):
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', encoding='utf-8', delete=False) as temp_in:
                temp_in.write(source)
                temp_in_path = temp_in.name
            temp_out_path = temp_in_path + '.min'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            minify_script = os.path.join(script_dir, 'scripts', 'jsts_minify.js')
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

                if continue_on_error:
                    print(f"WARNING: JS/TS minification failed with return code {e.returncode}")
                    if e.stderr:
                        print(f"Details: {e.stderr}")
                    print("Continuing with original content.")
                    return source
                else:
                    print(f"ERROR: JS/TS minification failed with return code {e.returncode}")
                    if e.stderr:
                        print(f"Details: {e.stderr}")
                    print("Operation aborted due to JS/TS minification error.")
                    sys.exit(1)

            os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                os.unlink(temp_out_path)
                return minified
            else:
                if continue_on_error:
                    print("WARNING: JS/TS minification failed. Output file not created. Using original content.")
                    return source
                else:
                    print("ERROR: JS/TS minification failed. Output file not created.")
                    print("Operation aborted due to JS/TS minification error.")
                    sys.exit(1)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            if continue_on_error:
                print(f"WARNING: Encoding error during JS/TS minification: {str(e)}. Using original content.")
                return source
            else:
                print(f"ERROR: Encoding error during JS/TS minification: {str(e)}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.css', '.scss', '.sass', '.less']):
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', encoding='utf-8', delete=False) as temp_in:
                temp_in.write(source)
                temp_in_path = temp_in.name
            temp_out_path = temp_in_path + '.min'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            minify_script = os.path.join(script_dir, 'scripts', 'css_minify.js')
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

                if continue_on_error:
                    print(f"WARNING: CSS minification failed with return code {e.returncode}")
                    if e.stderr:
                        print(f"Details: {e.stderr}")
                    print("Continuing with original content.")
                    return source
                else:
                    print(f"ERROR: CSS minification failed with return code {e.returncode}")
                    if e.stderr:
                        print(f"Details: {e.stderr}")
                    print("Operation aborted due to CSS minification error.")
                    sys.exit(1)

            os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                os.unlink(temp_out_path)
                return minified
            else:
                if continue_on_error:
                    print("WARNING: CSS minification failed. Output file not created. Using original content.")
                    return source
                else:
                    print("ERROR: CSS minification failed. Output file not created.")
                    print("Operation aborted due to CSS minification error.")
                    sys.exit(1)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            if continue_on_error:
                print(f"WARNING: Encoding error during CSS minification: {str(e)}. Using original content.")
                return source
            else:
                print(f"ERROR: Encoding error during CSS minification: {str(e)}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.html', '.htm', '.xhtml', '.shtml']):
        try:
            with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', encoding='utf-8', delete=False) as temp_in:
                temp_in.write(source)
                temp_in_path = temp_in.name
            temp_out_path = temp_in_path + '.min'
            script_dir = os.path.dirname(os.path.abspath(__file__))
            minify_script = os.path.join(script_dir, 'scripts', 'html_minify.js')
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

                if continue_on_error:
                    print(f"WARNING: HTML minification failed with return code {e.returncode}")
                    if e.stderr:
                        print(f"Details: {e.stderr}")
                    print("Continuing with original content.")
                    return source
                else:
                    print(f"ERROR: HTML minification failed with return code {e.returncode}")
                    if e.stderr:
                        print(f"Details: {e.stderr}")
                    print("Operation aborted due to HTML minification error.")
                    sys.exit(1)

            os.unlink(temp_in_path)
            if os.path.exists(temp_out_path):
                with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                    minified = out_file.read()
                os.unlink(temp_out_path)
                return minified
            else:
                if continue_on_error:
                    print("WARNING: HTML minification failed. Output file not created. Using original content.")
                    return source
                else:
                    print("ERROR: HTML minification failed. Output file not created.")
                    print("Operation aborted due to HTML minification error.")
                    sys.exit(1)
        except (UnicodeEncodeError, UnicodeDecodeError) as e:
            if continue_on_error:
                print(f"WARNING: Encoding error during HTML minification: {str(e)}. Using original content.")
                return source
            else:
                print(f"ERROR: Encoding error during HTML minification: {str(e)}")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.php', '.phtml', '.php5', '.php7', '.phps']):
        return minify_php(source, continue_on_error)
    elif any(ext_lower.endswith(ext) for ext in ['.json', '.jsonl', '.geojson', '.json5', '.ndjson']):
        try:
            parsed_json = json.loads(source)
            return json.dumps(parsed_json, separators=(',', ':'))
        except json.JSONDecodeError:
            if continue_on_error:
                print("WARNING: Invalid JSON content. File will not be minified. Using original content.")
                return source
            else:
                print("ERROR: Invalid JSON content. File will not be minified.")
                sys.exit(1)
    elif any(ext_lower.endswith(ext) for ext in ['.yaml', '.yml']):
        try:
            yaml_parser = YAML(typ='safe')
            data = yaml_parser.load(source)
            flow_style = True

            if flow_style:
                minified = yaml.dump(data, default_flow_style=True, width=float('inf'), allow_unicode=True, sort_keys=False)
                minified = minified.strip()
                minified = re.sub(r',\s+', ', ', minified)
                minified = re.sub(r':\s+', ': ', minified)
                minified = re.sub(r'\s+}', '}', minified)
                minified = re.sub(r'{\s+', '{', minified)
                if minified.endswith('\n'):
                    minified = minified[:-1]
            else:
                minified = yaml.dump(data, default_flow_style=False, indent=2, width=float('inf'), allow_unicode=True, sort_keys=False)
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

            return minified.strip()
        except Exception as e:
            if continue_on_error:
                print(f"WARNING: YAML minification failed: {str(e)}. Using original content.")
                return source
            else:
                print(f"ERROR: YAML minification failed: {str(e)}")
                sys.exit(1)

    return source
