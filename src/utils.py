import json
import os
import re
import datetime
import python_minifier

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
        return os.path.relpath(path, base_path)
    except ValueError:
        return path


def format_path(path):
    abs_path = os.path.abspath(path)
    rel_path = get_relative_path(path)

    if rel_path == abs_path:
        return abs_path
    return f"{rel_path} ({abs_path})"


def print_stats(stats, operation_type=None, duration=None):
    """Print formatted statistics about an operation."""
    result = []

    if duration is not None:
        result.append(f"Time taken: {duration:.6f} seconds")

    # Input processing stats
    result.append("\n[INPUT PROCESSING]")
    if "dirs_traversed" in stats:
        result.append(f"Directories scanned: {stats['dirs_traversed']}")
    if "max_nesting_level" in stats:
        result.append(f"Maximum nesting level: {stats['max_nesting_level']}")
    result.append(f"Total files scanned: {stats['total_files_processed']}")
    result.append(f"Files skipped: {stats['skipped_files']} (non-target or excluded)")

    # Output result stats
    result.append("\n[OUTPUT RESULT]")
    if operation_type == OPERATION_DEFLATTEN:
        if "dirs_created" in stats:
            result.append(f"Directories created: {stats['dirs_created']}")
        if "files_copied" in stats:
            result.append(f"Files in {operation_type} output: {stats['files_copied']}")
            result.append(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")

    elif operation_type == OPERATION_BUNDLE or operation_type == OPERATION_MINIFY_BUNDLE:
        if "files_bundled" in stats:
            result.append(f"Files bundled: {stats['files_bundled']}")
            result.append(f"Data bundled: {stats['bytes_bundled'] / 1024:.2f} KB")
        if "original_size" in stats and "minified_size" in stats and stats["minified_size"] > 0:
            result.append(f"Original size: {stats['original_size'] / 1024:.2f} KB")
            result.append(f"Minified size: {stats['minified_size'] / 1024:.2f} KB")
            reduction = (1 - stats['minified_size'] / max(stats['original_size'], 1)) * 100
            result.append(f"Size reduction: {reduction:.2f}%")

    elif operation_type == OPERATION_MINIFY:
        if "files_copied" in stats:
            result.append(f"Files copied: {stats['files_copied']}")
        if "files_minified" in stats:
            result.append(f"Files minified: {stats['files_minified']}")
        if "bytes_original" in stats and "bytes_minified" in stats:
            result.append(f"Original size: {stats['bytes_original'] / 1024:.2f} KB")
            result.append(f"Minified size: {stats['bytes_minified'] / 1024:.2f} KB")
            reduction = (1 - stats['bytes_minified'] / max(stats['bytes_original'], 1)) * 100
            result.append(f"Size reduction: {reduction:.2f}%")

    elif operation_type == OPERATION_FLATTEN:
        if "files_copied" in stats:
            result.append(f"Files in {operation_type} output: {stats['files_copied']}")
            result.append(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")

    if len(result) == 5:  # Only has headers but no actual output results
        if "files_bundled" in stats and stats["files_bundled"] > 0:
            result.append(f"Files bundled: {stats['files_bundled']}")
        if "files_copied" in stats and stats["files_copied"] > 0:
            result.append(f"Files processed: {stats['files_copied']}")
        if "bytes_bundled" in stats and stats["bytes_bundled"] > 0:
            result.append(f"Data processed: {stats['bytes_bundled'] / 1024:.2f} KB")

    # Processing rate
    if duration is not None:
        if (operation_type == OPERATION_BUNDLE or operation_type == OPERATION_MINIFY_BUNDLE) and "files_bundled" in stats:
            result.append(f"Processing rate: {stats['files_bundled'] / max(duration, 0.1):.2f} files/second")
        elif "files_copied" in stats and stats["files_copied"] > 0:
            result.append(f"Processing rate: {stats['files_copied'] / max(duration, 0.1):.2f} files/second")

    output = "\n".join(result)
    print(output)
    return output


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


def is_timestamp_dir(dir_name):
    return bool(re.match(r'\d{8}_\d{6}', os.path.basename(dir_name)))


def minify_code(source, file_ext):
    if not source:
        return source

    if file_ext.lower() in ['.py']:
        return python_minifier.minify(source)
    elif file_ext.lower() in ['.json', '.jsonl', '.geojson', '.json5', '.ndjson']:
        parsed_json = json.loads(source)
        return json.dumps(parsed_json, separators=(',', ':'))

    return source
