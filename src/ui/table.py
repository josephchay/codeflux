from constants import OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE, OPERATION_FLATTEN, OPERATION_DEFLATTEN, \
    OPERATION_MINIFY, TABULATE_FORMAT


def get_table_formatter():
    try:
        from tabulate import tabulate
        return tabulate, True
    except ImportError:
        return None, False


def format_file_table(files_data, operation_type):
    tabulate_func, has_tabulate = get_table_formatter()
    headers = ["File", "Size (KB)", "Status"]
    if operation_type in [OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE]:
        if operation_type == OPERATION_MINIFY_BUNDLE:
            headers.extend(["Original (KB)", "Reduction %"])
    elif operation_type == OPERATION_MINIFY:
        headers.extend(["Original (KB)", "Reduction %"])

    table_data = []
    for file_info in files_data:
        row = [file_info.get("file", "")]
        size_kb = file_info.get("size", 0) / 1024
        row.append(f"{size_kb:.2f}")
        status = file_info.get("status", "")
        row.append(status)

        if (operation_type in [OPERATION_MINIFY_BUNDLE, OPERATION_MINIFY]) and "original_size" in file_info:
            orig_kb = file_info.get("original_size", 0) / 1024
            row.append(f"{orig_kb:.2f}")
            reduction = file_info.get("reduction", 0)
            row.append(f"{reduction:.2f}")
        table_data.append(row)

    if has_tabulate:
        return tabulate_func(table_data, headers, tablefmt=TABULATE_FORMAT)
    else:
        result = []
        for file_info in files_data:
            file_path = file_info.get("file", "")
            size_kb = file_info.get("size", 0) / 1024
            status = file_info.get("status", "")
            file_str = f"{file_path} (Size: {size_kb:.2f} KB"
            if (operation_type in [OPERATION_MINIFY_BUNDLE, OPERATION_MINIFY]) and "original_size" in file_info:
                orig_kb = file_info.get("original_size", 0) / 1024
                reduction = file_info.get("reduction", 0)
                file_str += f", Original: {orig_kb:.2f} KB, Reduction: {reduction:.2f}%"

            file_str += f") - {status}"
            result.append(file_str)

        return "\n".join(result)


def format_stats_table(stats, operation_type, duration):
    tabulate_func, has_tabulate = get_table_formatter()
    data = [
        ["Time taken", f"{duration:.6f} seconds"],
        ["Directories scanned", stats.get("dirs_traversed", 0)],
        ["Maximum nesting level", stats.get("max_nesting_level", 0)],
        ["Total files scanned", stats.get("total_files_processed", 0)],
        ["Files skipped", f"{stats.get('skipped_files', 0)} (non-target or excluded)"]
    ]

    # Operation-specific stats
    if operation_type in [OPERATION_FLATTEN, OPERATION_DEFLATTEN]:
        files_copied = stats.get("files_copied", 0)
        bytes_copied = stats.get("bytes_copied", 0) / 1024  # Convert to KB
        avg_file_size = bytes_copied / max(files_copied, 1)

        if operation_type == OPERATION_FLATTEN:
            data.extend([
                ["Files in flatten output", files_copied],
                ["Data in flatten output", f"{bytes_copied:.2f} KB"],
            ])
            if files_copied > 0:
                data.append(["Average file size", f"{avg_file_size:.2f} KB"])
        else:
            data.extend([
                ["Files in deflatten output", files_copied],
                ["Data in deflatten output", f"{bytes_copied:.2f} KB"],
                ["Directories created", stats.get("dirs_created", 0)],
            ])
            if files_copied > 0:
                data.append(["Average file size", f"{avg_file_size:.2f} KB"])

    elif operation_type == OPERATION_BUNDLE:
        files_bundled = stats.get("files_bundled", 0)
        bytes_bundled = stats.get("bytes_bundled", 0) / 1024  # Convert to KB
        avg_file_size = bytes_bundled / max(files_bundled, 1)
        data.extend([
            ["Files bundled", files_bundled],
            ["Data bundled", f"{bytes_bundled:.2f} KB"],
        ])

        if "files_with_snippets" in stats and stats["files_with_snippets"] > 0:
            data.append(["Files with snippets applied", stats["files_with_snippets"]])
            total_files = stats.get("files_bundled", 0)
            if total_files > 0:
                snippet_percentage = (stats["files_with_snippets"] / total_files) * 100
                data.append(["Percentage of files with snippets", f"{snippet_percentage:.1f}%"])

        if files_bundled > 0:
            data.append(["Average file size", f"{avg_file_size:.2f} KB"])

    elif operation_type == OPERATION_MINIFY:
        files_copied = stats.get("files_copied", 0)
        files_minified = stats.get("files_minified", 0)
        bytes_original = stats.get("bytes_original", 0) / 1024  # Convert to KB
        bytes_minified = stats.get("bytes_minified", 0) / 1024  # Convert to KB
        data.extend([
            ["Files copied", files_copied],
            ["Files minified", files_minified],
        ])

        if files_copied > 0:
            avg_orig_size = bytes_original / max(files_copied, 1)
            avg_mini_size = bytes_minified / max(files_copied, 1)
            data.extend([
                ["Average original file size", f"{avg_orig_size:.2f} KB"],
                ["Average minified file size", f"{avg_mini_size:.2f} KB"],
            ])

        if bytes_original > 0:
            reduction = (1 - stats.get("bytes_minified", 0) / max(stats.get("bytes_original", 1), 1)) * 100
            data.extend([
                ["Original size", f"{bytes_original:.2f} KB"],
                ["Minified size", f"{bytes_minified:.2f} KB"],
                ["Size reduction", f"{reduction:.2f}%"],
            ])

    elif operation_type == OPERATION_MINIFY_BUNDLE:
        files_bundled = stats.get("files_bundled", 0)
        bytes_bundled = stats.get("bytes_bundled", 0) / 1024  # Convert to KB
        bytes_original = stats.get("original_size", 0) / 1024  # Convert to KB
        bytes_minified = stats.get("minified_size", 0) / 1024  # Convert to KB
        data.extend([
            ["Files bundled", files_bundled],
            ["Data bundled", f"{bytes_bundled:.2f} KB"],
        ])

        if "files_with_snippets" in stats and stats["files_with_snippets"] > 0:
            data.append(["Files with snippets applied", stats["files_with_snippets"]])
            total_files = stats.get("files_bundled", 0)
            if total_files > 0:
                snippet_percentage = (stats["files_with_snippets"] / total_files) * 100
                data.append(["Percentage of files with snippets", f"{snippet_percentage:.1f}%"])

        if bytes_original > 0:
            reduction = (1 - stats.get("minified_size", 0) / max(stats.get("original_size", 1), 1)) * 100
            data.extend([
                ["Original size", f"{bytes_original:.2f} KB"],
                ["Minified size", f"{bytes_minified:.2f} KB"],
                ["Size reduction", f"{reduction:.2f}%"],
            ])

            if files_bundled > 0:
                avg_orig_size = bytes_original / max(files_bundled, 1)
                avg_mini_size = bytes_minified / max(files_bundled, 1)
                data.extend([
                    ["Average original file size", f"{avg_orig_size:.2f} KB"],
                    ["Average minified file size", f"{avg_mini_size:.2f} KB"],
                ])

    files_processed = stats.get("total_files_processed", 0)
    if files_processed > 0:
        files_per_second = files_processed / max(duration, 0.001)
        data.append(["Processing rate", f"{files_per_second:.2f} files/second"])

    if has_tabulate:
        return tabulate_func(data, headers=["Statistic", "Value"], tablefmt=TABULATE_FORMAT)
    else:
        result = []
        for row in data:
            result.append(f"{row[0]}: {row[1]}")
        return "\n".join(result)
