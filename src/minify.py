import json
import os
import subprocess
import sys
import tempfile
import re
import python_minifier
import yaml
from ruamel.yaml import YAML


def minify_code(source, file_extension):
    if not source:
        return source

    if file_extension.lower() in ['.py']:
        return python_minifier.minify(source)
    elif file_extension.lower() in ['.ipynb']:
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
                                print(f"Warning: Failed to minify a code cell: {str(e)}")
                                sys.exit(1)

            return json.dumps(notebook, separators=(',', ':'))
        except json.JSONDecodeError as e:
            print(f"Warning: Invalid notebook JSON format: {str(e)}")
            sys.exit(1)
        except Exception as e:
            print(f"Warning: Error processing notebook: {str(e)}")
            sys.exit(1)
    elif file_extension.lower() in ['.js', '.jsx', '.ts', '.tsx']:
        with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', delete=False) as temp_in:
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
            print("ERROR: JS/TS minification failed. Output file not created.")
            print("Operation aborted due to JS/TS minification error.")
            sys.exit(1)
    elif file_extension.lower() in ['.html', '.htm', '.xhtml', '.shtml']:
        with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', delete=False) as temp_in:
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
            print("ERROR: HTML minification failed. Output file not created.")
            print("Operation aborted due to HTML minification error.")
            sys.exit(1)
    elif file_extension.lower() in ['.json', '.jsonl', '.geojson', '.json5', '.ndjson']:
        try:
            parsed_json = json.loads(source)
            return json.dumps(parsed_json, separators=(',', ':'))
        except json.JSONDecodeError:
            print("ERROR: Invalid JSON content. File will not be minified.\n")
            sys.exit(1)
    elif file_extension.lower() in ['.yaml', '.yml']:
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
            print(f"ERROR: YAML minification failed: {str(e)}")
            sys.exit(1)
