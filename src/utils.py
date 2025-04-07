import json
import os
import datetime
import subprocess
import tempfile
import python_minifier
import re
import yaml
from ruamel.yaml import YAML

from constants import OPERATION_DEFLATTEN, OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE, OPERATION_MINIFY, \
    OPERATION_FLATTEN


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
    """Print statistics about an operation"""
    files_processed = stats.get("files_processed", 0) or stats.get("total_files_processed", 0)
    files_per_second = files_processed / max(duration, 0.001)

    print(f"\nTime taken: {duration:.6f} seconds")
    if show_full:
        print("\n[INPUT PROCESSING]")
        dirs_traversed = stats.get("dirs_traversed", 0)
        max_nesting = stats.get("max_nesting_level", 0)
        total_files = stats.get("total_files_processed", 0)
        skipped_files = stats.get("skipped_files", 0)

        print(f"Directories scanned: {dirs_traversed}")
        print(f"Maximum nesting level: {max_nesting}")
        print(f"Total files scanned: {total_files}")
        print(f"Files skipped: {skipped_files} (non-target or excluded)")

        print("\n[OUTPUT RESULT]")

        if operation_type in [OPERATION_FLATTEN, OPERATION_DEFLATTEN]:
            files_copied = stats.get("files_copied", 0)
            bytes_copied = stats.get("bytes_copied", 0) / 1024  # Convert to KB
            avg_file_size = bytes_copied / max(files_copied, 1)

            if operation_type == OPERATION_FLATTEN:
                print(f"Files in flatten output: {files_copied}")
                print(f"Data in flatten output: {bytes_copied:.2f} KB")
                if files_copied > 0:
                    print(f"Average file size: {avg_file_size:.2f} KB")
            else:
                print(f"Files in deflatten output: {files_copied}")
                print(f"Data in deflatten output: {bytes_copied:.2f} KB")
                print(f"Directories created: {stats.get('dirs_created', 0)}")
                if files_copied > 0:
                    print(f"Average file size: {avg_file_size:.2f} KB")

            if files_processed > 0:
                print(f"Processing rate: {files_per_second:.2f} files/second")


        elif operation_type == OPERATION_BUNDLE:
            files_bundled = stats.get("files_bundled", 0)
            bytes_bundled = stats.get("bytes_bundled", 0) / 1024  # Convert to KB
            avg_file_size = bytes_bundled / max(files_bundled, 1)
            print(f"Files bundled: {files_bundled}")
            print(f"Data bundled: {bytes_bundled:.2f} KB")

            if files_bundled > 0:
                print(f"Average file size: {avg_file_size:.2f} KB")
            if files_processed > 0:
                print(f"Processing rate: {files_per_second:.2f} files/second")

        elif operation_type == OPERATION_MINIFY:
            files_copied = stats.get("files_copied", 0)
            files_minified = stats.get("files_minified", 0)

            print(f"Files copied: {files_copied}")
            print(f"Files minified: {files_minified}")

            bytes_original = stats.get("bytes_original", 0) / 1024  # Convert to KB
            bytes_minified = stats.get("bytes_minified", 0) / 1024  # Convert to KB

            if files_copied > 0:
                avg_orig_size = bytes_original / max(files_copied, 1)
                avg_mini_size = bytes_minified / max(files_copied, 1)
                print(f"Average original file size: {avg_orig_size:.2f} KB")
                print(f"Average minified file size: {avg_mini_size:.2f} KB")

            if bytes_original > 0:
                reduction = (1 - stats.get("bytes_minified", 0) / max(stats.get("bytes_original", 1), 1)) * 100
                print(f"Original size: {bytes_original:.2f} KB")
                print(f"Minified size: {bytes_minified:.2f} KB")
                print(f"Size reduction: {reduction:.2f}%")

            if files_processed > 0:
                print(f"Processing rate: {files_per_second:.2f} files/second")

        elif operation_type == OPERATION_MINIFY_BUNDLE:
            files_bundled = stats.get("files_bundled", 0)
            bytes_bundled = stats.get("bytes_bundled", 0) / 1024  # Convert to KB

            print(f"Files bundled: {files_bundled}")
            print(f"Data bundled: {bytes_bundled:.2f} KB")
            if files_bundled > 0:
                avg_bundle_size = bytes_bundled / max(files_bundled, 1)
                print(f"Average bundled file size: {avg_bundle_size:.2f} KB")

            bytes_original = stats.get("original_size", 0) / 1024  # Convert to KB
            bytes_minified = stats.get("minified_size", 0) / 1024  # Convert to KB

            if bytes_original > 0:
                reduction = (1 - stats.get("minified_size", 0) / max(stats.get("original_size", 1), 1)) * 100
                print(f"Original size: {bytes_original:.2f} KB")
                print(f"Minified size: {bytes_minified:.2f} KB")
                print(f"Size reduction: {reduction:.2f}%")

                if files_bundled > 0:
                    avg_orig_size = bytes_original / max(files_bundled, 1)
                    avg_mini_size = bytes_minified / max(files_bundled, 1)
                    print(f"Average original file size: {avg_orig_size:.2f} KB")
                    print(f"Average minified file size: {avg_mini_size:.2f} KB")

            if files_processed > 0:
                print(f"Processing rate: {files_per_second:.2f} files/second")


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
                        include_exts=None, include_files=None):
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
    is_excluded_file = exclude_files and filename in exclude_files

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
    elif file_extension.lower() in ['.js', '.jsx', '.ts', '.tsx']:
        node_result = subprocess.run(['node', '--version'], capture_output=True)
        if node_result.returncode != 0:
            print("WARNING: Node.js is required for JavaScript/TypeScript minification.")
            print("JavaScript/TypeScript files will not be minified.\n")
            return source

        with tempfile.NamedTemporaryFile(suffix=file_extension, mode='w', delete=False) as temp_in:
            temp_in.write(source)
            temp_in_path = temp_in.name
        temp_out_path = temp_in_path + '.min'
        script_dir = os.path.dirname(os.path.abspath(__file__))
        minify_script = os.path.join(script_dir, 'scripts', 'jsts_minify.js')

        if not os.path.exists(minify_script):
            print(f"WARNING: minify.js script not found at {minify_script}")
            print("JavaScript/TypeScript files will not be minified.\n")
            os.unlink(temp_in_path)
            return source

        result = subprocess.run(
            ['node', minify_script, temp_in_path, temp_out_path],
            capture_output=True,
            text=True
        )

        os.unlink(temp_in_path)
        if result.returncode == 0 and os.path.exists(temp_out_path):
            with open(temp_out_path, 'r', encoding='utf-8') as out_file:
                minified = out_file.read()
            os.unlink(temp_out_path)
            return minified
        else:
            if os.path.exists(temp_out_path):
                os.unlink(temp_out_path)

            print("WARNING: JavaScript/TypeScript minification failed.")
            if result.stderr:
                print(f"Details: {result.stderr}")
            return source
    elif file_extension.lower() in ['.json', '.jsonl', '.geojson', '.json5', '.ndjson']:
        try:
            parsed_json = json.loads(source)
            return json.dumps(parsed_json, separators=(',', ':'))
        except json.JSONDecodeError:
            print("WARNING: Invalid JSON content. File will not be minified.\n")
            return source
    elif file_extension.lower() in ['.yaml', '.yml']:
        return minify_yaml(source, flow_style=True)

    return source
