import os
import datetime
import re

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
        lower_include_files = [f.lower() for f in include_files]
        filename_lower = filename.lower()
        if filename_lower in lower_include_files:
            return True

        if file_rel_path:
            rel_path_lower = file_rel_path.lower()
            for inc in lower_include_files:
                if rel_path_lower.endswith(inc) or rel_path_lower == inc:
                    return True

        return False

    if include_exts:
        is_included_ext = any(filename.lower().endswith(ext.lower()) for ext in include_exts)
        if not is_included_ext:
            return False
    else:
        is_target_ext = any(filename.lower().endswith(ext.lower()) for ext in handler_extensions)
        if not is_target_ext:
            return False

    is_excluded_ext = exclude_exts and any(filename.lower().endswith(ext.lower()) for ext in exclude_exts)
    is_excluded_file = False
    if exclude_files and file_rel_path:
        norm_rel_path = file_rel_path.replace('\\', '/')
        for exclude_pattern in exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if (norm_rel_path.lower() == norm_exclude.lower() or
                    norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                    filename.lower() == norm_exclude.lower()):
                is_excluded_file = True
                break

    return not (is_excluded_ext or is_excluded_file)


def mkdir_output(operation=None):
    base_dir = os.path.join(os.getcwd(), "codebundle")
    os.makedirs(base_dir, exist_ok=True)

    if operation:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp_dir = os.path.join(base_dir, timestamp)
        os.makedirs(timestamp_dir, exist_ok=True)
        return timestamp_dir, operation

    return base_dir, None
