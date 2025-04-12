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


def get_relpath(path, base_path=None, output_base=None):
    base_path = base_path or os.getcwd()
    clean_path = path.replace('\\', '/')

    try:
        abs_path = os.path.abspath(path)
        abs_base = os.path.abspath(base_path)

        # Try to strip out codeflux timestamp patterns first (highest priority)
        match = re.search(r'(codeflux[/\\]\d{8}_\d{6}[/\\])', abs_path)
        if match:
            # Remove the matched pattern and return the rest
            timestamp_dir = match.group(0)
            timestamp_index = abs_path.find(timestamp_dir) + len(timestamp_dir)
            if timestamp_index < len(abs_path):
                return abs_path[timestamp_index:].replace('\\', '/')
            else:
                # If the pattern is at the end, return an empty string or the basename
                return os.path.basename(abs_path)

        if output_base:
            try:
                output_abs = os.path.abspath(output_base)
                rel_path = os.path.relpath(abs_path, output_abs)
                if rel_path != '.':
                    return rel_path.replace('\\', '/')
            except ValueError:
                pass  # Continue to other methods if this fails

        if abs_path.startswith(abs_base + os.sep) or abs_path == abs_base:
            rel_path = os.path.relpath(abs_path, abs_base)
            if rel_path == '.':
                return os.path.basename(abs_path)
            return rel_path.replace('\\', '/')

        # If none of the special cases apply, return the path relative to base_path
        return os.path.relpath(abs_path, abs_base).replace('\\', '/')

    except ValueError:
        # If there's an error calculating the relative path (e.g., different drives on Windows),
        # return the basename as a fallback
        return os.path.basename(path)


def format_path(path):
    abs_path = os.path.abspath(path)
    rel_path = get_relpath(path)

    if rel_path == abs_path:
        return abs_path
    return f"{rel_path} ({abs_path})"


def print_stats(stats, operation_type, duration, show_full=True):
    if show_full:
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
        "files_minified": 0,
        "bytes_original": 0,
        "bytes_minified": 0,
        "failed_minifications": 0
    }

    # These fields should not be summed, but rather take the max value across all stats
    # or should be calculated from other values
    special_fields = {
        "max_nesting_level": max,
        "original_size": max,
        "minified_size": max
    }

    for stats in stats_list:
        for key, value in stats.items():
            if key in special_fields:
                # For fields that need special handling
                if key in merged_stats:
                    merged_stats[key] = special_fields[key](merged_stats[key], value)
                else:
                    merged_stats[key] = value
            elif key in merged_stats:
                # Normal summation for most fields
                merged_stats[key] += value
            else:
                # For any fields not explicitly handled
                merged_stats[key] = value

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
    base_dir = os.path.join(os.getcwd(), "codeflux")
    os.makedirs(base_dir, exist_ok=True)

    if operation:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        timestamp_dir = os.path.join(base_dir, timestamp)
        os.makedirs(timestamp_dir, exist_ok=True)
        return timestamp_dir, operation

    return base_dir, None
