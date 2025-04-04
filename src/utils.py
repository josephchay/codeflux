import os
import datetime
import python_minifier


def get_unique_filename(destination_file):
    """
    Generate a unique filename if the destination file already exists
    by appending an incrementing counter
    """
    counter = 2
    name, ext = os.path.splitext(destination_file)
    unique_destination_file = destination_file

    while os.path.exists(unique_destination_file):
        unique_destination_file = f"{name}_{counter}{ext}"
        counter += 1

    return unique_destination_file


def get_relative_path(path, base_path):
    """Get a relative path representation from base_path for readability"""
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        return path


def print_stats(operation_type, stats, duration):
    """Print formatted statistics about an operation"""
    print(f"Time taken: {duration:.6f} seconds")

    # Processing stats section
    print("\n[INPUT PROCESSING]")
    if operation_type in ["flatten", "bundle", "minify"]:
        if "dirs_traversed" in stats:
            print(f"Directories scanned: {stats['dirs_traversed']}")
        if "max_nesting_level" in stats:
            print(f"Maximum nesting level: {stats['max_nesting_level']}")
    print(f"Total files scanned: {stats['total_files_processed']}")
    print(f"Files skipped: {stats['skipped_files']} (non-target or excluded)")

    # Output stats section
    print("\n[OUTPUT RESULT]")
    if operation_type == "deflatten":
        if "dirs_created" in stats:
            print(f"Directories created: {stats['dirs_created']}")
        if "files_copied" in stats:
            print(f"Files in {operation_type} output: {stats['files_copied']}")
            print(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")
    elif operation_type == "bundle":
        if "files_bundled" in stats:
            print(f"Files bundled: {stats['files_bundled']}")
            print(f"Data bundled: {stats['bytes_bundled'] / 1024:.2f} KB")
        if "original_size" in stats and "minified_size" in stats and stats["minified_size"] > 0:
            print(f"Original size: {stats['original_size'] / 1024:.2f} KB")
            print(f"Minified size: {stats['minified_size'] / 1024:.2f} KB")
            print(f"Size reduction: {(1 - stats['minified_size'] / max(stats['original_size'], 1)) * 100:.2f}%")
    elif operation_type == "minify":
        if "files_copied" in stats:
            print(f"Files copied: {stats['files_copied']}")
        if "files_minified" in stats:
            print(f"Files minified: {stats['files_minified']}")
        if "bytes_original" in stats and "bytes_minified" in stats:
            print(f"Original size: {stats['bytes_original'] / 1024:.2f} KB")
            print(f"Minified size: {stats['bytes_minified'] / 1024:.2f} KB")
            print(f"Size reduction: {(1 - stats['bytes_minified'] / max(stats['bytes_original'], 1)) * 100:.2f}%")
    else:  # flatten
        if "files_copied" in stats:
            print(f"Files in {operation_type} output: {stats['files_copied']}")
            print(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")

    # Calculate and print the appropriate processing rate
    if operation_type == "bundle":
        if "files_bundled" in stats:
            print(f"Processing rate: {stats['files_bundled'] / max(duration, 0.1):.2f} files/second")
    else:
        if "files_copied" in stats:
            print(f"Processing rate: {stats['files_copied'] / max(duration, 0.1):.2f} files/second")
    print("=" * 50)


def merge_with_defaults(user_values, defaults, ignore_defaults=False):
    if user_values is None:
        return [] if ignore_defaults else defaults

    if ignore_defaults:
        return user_values
    else:
        return list(set(user_values + defaults))


def merge_stats(stats_list):
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
    # If include_files is specified, only include those files
    if include_files:
        return filename in include_files

    # Check extension inclusion if specified
    if include_exts:
        is_included_ext = any(filename.lower().endswith(ext) for ext in include_exts)
        if not is_included_ext:
            return False
    else:
        # Otherwise check if it's one of the handler's extensions
        is_target_ext = any(filename.lower().endswith(ext) for ext in handler_extensions)
        if not is_target_ext:
            return False

    # Check exclusions
    is_excluded_ext = exclude_exts and any(filename.endswith(ext) for ext in exclude_exts)
    is_excluded_file = exclude_files and filename in exclude_files

    return not (is_excluded_ext or is_excluded_file)


def create_timestamped_dir():
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = os.path.join(os.getcwd(), f"codebundle_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)
    return output_dir


def minify_code(source, file_ext):
    if not source:
        return source

    if file_ext.lower() in ['.py']:
        try:
            return python_minifier.minify(source)
        except Exception as e:
            error_msg = f"Error minifying Python code: {str(e)}"
            print(error_msg)
            raise RuntimeError(error_msg)

    return source
