import json
import os
import datetime
import subprocess
import sys
import tempfile
import python_minifier
import re
import yaml
from ruamel.yaml import YAML
from ui.table import format_stats_table


def get_unique_filename(destination_file):
    counter = 2
    name, ext = os.path.splitext(destination_file)
    unique_destination_file = destination_file

    while os.path.exists(unique_destination_file):
        unique_destination_file = f"{name}_{counter}{ext}"
        counter += 1

    return unique_destination_file


def get_relative_path(path, base_path=None):
    base_path = base_path or os.getcwd()
    try:
        rel_path = os.path.relpath(path, base_path)

        # Special handling for codebundle timestamp directories
        timestamp_match = re.search(r'codebundle[/\\]\d{8}_\d{6}', path)
        if timestamp_match:
            # Extract the part after the timestamp directory
            timestamp_dir = timestamp_match.group(0)
            timestamp_index = path.find(timestamp_dir) + len(timestamp_dir)
            if timestamp_index < len(path):
                return path[timestamp_index + 1:].replace('\\', '/')

        return rel_path
    except ValueError:
        return path


def format_path(path):
    abs_path = os.path.abspath(path)
    rel_path = get_relative_path(path)

    if rel_path == abs_path:
        return abs_path
    return f"{rel_path} ({abs_path})"


def print_stats(stats, operation_type, duration, show_full=True):
    if not show_full:
        print(f"\nTime taken: {duration:.6f} seconds")
        return

    print("\n[OPERATION SUMMARY]")
    print(format_stats_table(stats, operation_type, duration))


def merge_with_defaults(user_values, defaults, ignore_defaults=False):
    if user_values is None:
        return [] if ignore_defaults else defaults

    if ignore_defaults:
        return user_values

    return list(set(user_values + defaults))


def merge_stats(stats_list):
    if not stats_list:
        return {}

    merged_stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_copied": 0,
        "bytes_copied": 0,
        "skipped_files": 0,
        "max_nesting_level": 0,
        "dirs_created": 0,
        "files_bundled": 0,
        "bytes_bundled": 0,
        "original_size": 0,
        "minified_size": 0,
        "files_minified": 0,
        "bytes_original": 0,
        "bytes_minified": 0
    }

    for stats in stats_list:
        for key, value in stats.items():
            if key in merged_stats:
                merged_stats[key] += value
                # For max_nesting_level, keep the maximum value
                if key == "max_nesting_level":
                    merged_stats[key] = max(merged_stats[key], value)

    return merged_stats


def should_process_file(filename, handler_extensions, exclude_exts=None, exclude_files=None,
                        include_exts=None, include_files=None, file_rel_path=None):
    if include_files:
        return filename in include_files
    if include_exts:
        is_included_ext = any(filename.lower().endswith(ext) for ext in include_exts)
        if not is_included_ext:
            return False
    else:
        is_target_ext = any(filename.lower().endswith(ext) for ext in handler_extensions)
        if not is_target_ext:
            return False

    is_excluded_ext = exclude_exts and any(filename.endswith(ext) for ext in exclude_exts)
    is_excluded_file = False
    if exclude_files and file_rel_path:
        norm_rel_path = file_rel_path.replace('\\', '/')
        for exclude_pattern in exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if norm_rel_path == norm_exclude:
                is_excluded_file = True
                break

    return not (is_excluded_ext or is_excluded_file)


def create_output_dir(operation=None):
    base_dir = os.path.join(os.getcwd(), "codebundle")
    os.makedirs(base_dir, exist_ok=True)

    if operation:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp_dir = os.path.join(base_dir, timestamp)
        os.makedirs(timestamp_dir, exist_ok=True)
        return timestamp_dir, operation

    return base_dir, None


def minify_yaml(yaml_content, flow_style=False):
    try:
        yaml_parser = YAML(typ='safe')
        data = yaml_parser.load(yaml_content)

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
                    if not (value.lower() in ('yes', 'no', 'true', 'false', 'null', 'on', 'off') or re.search(r'^\d', value) or re.search(r'[:#{}[\],&*!|>\'"%@`]', value)):
                        lines[i] = f"{prefix}{value}"
            minified = '\n'.join(lines)

        return minified.strip()
    except Exception as e:
        print(f"Warning: YAML minification failed: {str(e)}")
        return yaml_content


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
            print("WARNING: Invalid JSON content. File will not be minified.\n")
            return source
    elif file_extension.lower() in ['.yaml', '.yml']:
        return minify_yaml(source, flow_style=True)


def get_file_snippet(content, max_lines=50, position="top", pattern=None, context_lines=5):
    lines = content.splitlines()
    original_line_count = len(lines)

    if len(lines) <= max_lines:
        return content, False, original_line_count
    if pattern:
        matches = list(re.finditer(pattern, content))
        if matches:
            match_line_numbers = []
            line_indexes = [0]
            for i, line in enumerate(lines):
                line_indexes.append(line_indexes[-1] + len(line) + 1)
            for match in matches:
                start_pos = match.start()
                for i in range(len(line_indexes) - 1):
                    if line_indexes[i] <= start_pos < line_indexes[i + 1]:
                        match_line_numbers.append(i)
                        break

            extracted_lines = set()
            for line_num in match_line_numbers:
                start = max(0, line_num - context_lines)
                end = min(len(lines), line_num + context_lines + 1)
                for i in range(start, end):
                    extracted_lines.add(i)

            extracted_lines = sorted(list(extracted_lines))
            if len(extracted_lines) > max_lines:
                # If we have too many lines, prioritize first matches
                extracted_lines = extracted_lines[:max_lines]

            result_lines = []
            current_group = []
            for i, line_num in enumerate(extracted_lines):
                if i > 0 and line_num > extracted_lines[i - 1] + 1:
                    result_lines.extend(current_group)
                    result_lines.append("# [...] Skipped lines")
                    current_group = []
                current_group.append(lines[line_num])

            result_lines.extend(current_group)
            return "\n".join(result_lines), True, original_line_count

    if position == "top":
        return "\n".join(lines[:max_lines]) + "\n# [...] Remaining lines omitted", True, original_line_count
    elif position == "bottom":
        return "\n".join(["# [...] Initial lines omitted"] + lines[-max_lines:]), True, original_line_count
    else:  # middle
        mid_point = len(lines) // 2
        half_snippet = max_lines // 2
        start = max(0, mid_point - half_snippet)
        end = min(len(lines), mid_point + half_snippet)
        return "\n".join(["# [...] Initial lines omitted"] +
                         lines[start:end] +
                         ["# [...] Remaining lines omitted"]), True, original_line_count
