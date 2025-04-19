import shutil

from constants import OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE, OPERATION_FLATTEN, OPERATION_DEFLATTEN, \
    OPERATION_MINIFY, TABULATE_FORMAT, OPERATION_PROPERTIES, OPERATION_BIBDEDUP, OPERATION_ACROSCAN


def get_table_formatter():
    try:
        from tabulate import tabulate
        return tabulate, True
    except ImportError:
        return None, False


def format_file_table(files_info, operation_type):
    if not files_info:
        return "No files processed."

    table_formatter, tabulate_available = get_table_formatter()
    has_warnings = any("warnings" in file_info and file_info["warnings"] for file_info in files_info)

    if operation_type in [OPERATION_FLATTEN, OPERATION_DEFLATTEN]:
        headers = ["File", "Size (KB)", "Status"]
        if has_warnings:
            headers.append("Warnings")

        rows = []
        for file_info in files_info:
            row = [
                file_info["file"],
                f"{file_info['size'] / 1024:.2f}",
                file_info["status"]
            ]
            if has_warnings:
                row.append(file_info.get("warnings", ""))
            rows.append(row)
    elif operation_type == OPERATION_MINIFY:
        headers = ["File", "Size (KB)", "Status", "Original (KB)", "Reduction %"]
        if has_warnings:
            headers.append("Warnings")

        rows = []
        for file_info in files_info:
            row = [
                file_info["file"],
                f"{file_info['size'] / 1024:.2f}",
                file_info["status"],
                f"{file_info['original_size'] / 1024:.2f}",
                f"{file_info['reduction']:.2f}"
            ]
            if has_warnings:
                row.append(file_info.get("warnings", ""))
            rows.append(row)
    elif operation_type in [OPERATION_BUNDLE, OPERATION_MINIFY_BUNDLE]:
        headers = ["File", "Size (KB)", "Status"]
        if operation_type == OPERATION_MINIFY_BUNDLE:
            headers.extend(["Original (KB)", "Reduction %"])
        if has_warnings:
            headers.append("Warnings")

        rows = []
        for file_info in files_info:
            row = [
                file_info["file"],
                f"{file_info['size'] / 1024:.2f}",
                file_info["status"]
            ]

            if operation_type == OPERATION_MINIFY_BUNDLE and "original_size" in file_info:
                row.extend([
                    f"{file_info['original_size'] / 1024:.2f}",
                    f"{file_info['reduction']:.2f}"
                ])

            if has_warnings:
                row.append(file_info.get("warnings", ""))

            rows.append(row)
    elif operation_type == OPERATION_ACROSCAN:
        headers = ["File", "Size (KB)", "Acronyms Found", "Acronyms Replaced", "Status"]

        rows = []
        for file_info in files_info:
            row = [
                file_info["file"],
                f"{file_info['size'] / 1024:.2f}",
                file_info.get("acronyms_found", 0),
                file_info.get("acronyms_replaced", 0),
                file_info["status"]
            ]
            rows.append(row)
    elif operation_type == OPERATION_PROPERTIES:
        headers = ["File", "Size", "Type", "Modified", "Permissions"]

        # Check for optional columns
        has_hash = any("md5" in file_info for file_info in files_info)
        has_lines = any("lines" in file_info for file_info in files_info)

        if has_hash:
            headers.append("MD5 Hash")
        if has_lines:
            headers.append("Lines")
        if has_warnings:
            headers.append("Warnings")

        rows = []
        for file_info in files_info:
            row = [
                file_info["file"],
                file_info["readable_size"],
                file_info["type"],
                file_info["modified"],
                file_info["permissions"]
            ]

            # Add optional columns if present
            if has_hash:
                row.append(file_info.get("md5", ""))
            if has_lines:
                row.append(file_info.get("lines", ""))
            if has_warnings:
                row.append(file_info.get("warnings", ""))

            rows.append(row)
    elif operation_type == OPERATION_BIBDEDUP:
        has_entries = any("entries" in file_info for file_info in files_info)
        if has_entries:
            headers = ["File", "Size (KB)", "Entries", "Status"]
        else:
            headers = ["File", "Size (KB)", "Status"]

        if has_warnings:
            headers.append("Warnings")

        rows = []
        for file_info in files_info:
            if has_entries:
                row = [
                    file_info["file"],
                    f"{file_info['size'] / 1024:.2f}",
                    file_info.get("entries", 0),
                    file_info["status"]
                ]
            else:
                row = [
                    file_info["file"],
                    f"{file_info['size'] / 1024:.2f}",
                    file_info["status"]
                ]

            if has_warnings:
                row.append(file_info.get("warnings", ""))
            rows.append(row)
    else:
        headers = ["File", "Size (KB)", "Status"]
        if has_warnings:
            headers.append("Warnings")

        rows = []
        for file_info in files_info:
            row = [
                file_info["file"],
                f"{file_info['size'] / 1024:.2f}",
                file_info["status"]
            ]
            if has_warnings:
                row.append(file_info.get("warnings", ""))
            rows.append(row)

    if tabulate_available:
        terminal_width = shutil.get_terminal_size().columns
        max_table_width = terminal_width - 4  # 2 characters padding on each side
        return table_formatter(
            rows,
            headers=headers,
            tablefmt=TABULATE_FORMAT,
            maxcolwidths=[
                int(max_table_width * 0.4),
                int(max_table_width * 0.1),
                int(max_table_width * 0.2),
                int(max_table_width * 0.1),
                int(max_table_width * 0.1),
                int(max_table_width * 0.2)
            ]
        )
    else:
        # Fallback to simple formatting with warnings column
        result = []
        header_format = "| {:<30} | {:<10} | {:<20} |"
        divider_format = "+{}+{}+{}+"
        divider_lens = [32, 12, 22]

        if has_warnings:
            header_format += " {:<15} |"
            divider_format += "{}+"
            divider_lens.append(17)

        if operation_type == OPERATION_MINIFY or operation_type == OPERATION_MINIFY_BUNDLE:
            header_format += " {:<15} | {:<12} |"
            divider_format += "{}+{}+"
            divider_lens.extend([17, 14])

        # Create header
        headers_to_use = headers[:3]
        if has_warnings:
            headers_to_use.append("Warnings")
        if len(headers) > 3:
            headers_to_use.extend(headers[3:])

        divider = divider_format.format(*["-" * length for length in divider_lens])
        result.append(divider)
        result.append(header_format.format(*headers_to_use))
        result.append(divider)

        # Add rows
        row_format = header_format
        for row in rows:
            formatted_row = []
            for i, col in enumerate(row):
                if i == 0:  # File name column
                    formatted_row.append(str(col)[:28])
                else:
                    formatted_row.append(str(col)[:divider_lens[i] - 2])
            result.append(row_format.format(*formatted_row))

        result.append(divider)
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

    # Add empty files count if available and non-zero
    if stats.get("empty_files", 0) > 0:
        data.append(["Empty files", stats.get("empty_files", 0)])

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
    elif operation_type == OPERATION_PROPERTIES:
        files_counted = stats.get("total_files_counted", 0)
        bytes_total = stats.get("bytes_total", 0) / 1024  # Convert to KB
        avg_file_size = bytes_total / max(files_counted, 1)

        data.extend([
            ["Files analyzed", files_counted],
            ["Total data size", f"{bytes_total:.2f} KB"],
        ])

        if files_counted > 0:
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

        if "failed_minifications" in stats and stats["failed_minifications"] > 0:
            data.append(["Files with failed minification", stats["failed_minifications"]])
            if files_copied > 0:
                fail_percentage = (stats["failed_minifications"] / files_copied) * 100
                data.append(["Percentage of failed minifications", f"{fail_percentage:.1f}%"])

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
    elif operation_type == OPERATION_ACROSCAN:
        files_processed = stats.get("total_files_processed", 0)
        files_scanned = stats.get("files_scanned", 0)
        files_with_acronyms = stats.get("files_with_acronyms", 0)
        total_acronyms_replaced = stats.get("total_acronyms_replaced", 0)
        unique_acronyms = len(stats.get("unique_acronyms_found", []))
        potential_acronyms = len(stats.get("potential_acronyms_found", []))

        data.extend([
            ["Files processed", files_processed],
            ["Files scanned", files_scanned],
            ["Files with acronyms", files_with_acronyms],
        ])

        if total_acronyms_replaced > 0:
            data.append(["Acronyms replaced", total_acronyms_replaced])
        if unique_acronyms > 0:
            data.append(["Unique acronyms found", unique_acronyms])
        if potential_acronyms > 0:
            data.append(["Potential unknown acronyms", potential_acronyms])
    elif operation_type == OPERATION_BIBDEDUP:
        # For BibTeX deduplication
        bib_files_processed = stats.get("total_files_processed", 0)
        total_entries = stats.get("total_entries", 0)
        duplicates_found = stats.get("duplicates_found", 0)
        files_with_duplicates = stats.get("files_with_duplicates", 0)

        data.extend([
            ["BibTeX files processed", bib_files_processed],
            ["Total BibTeX entries", total_entries],
            ["Potential duplicates found", duplicates_found],
            ["Files with duplicates", files_with_duplicates]
        ])

        if total_entries > 0 and duplicates_found > 0:
            duplicate_percentage = (duplicates_found / total_entries) * 100
            data.append(["Percentage of duplicate entries", f"{duplicate_percentage:.2f}%"])

        if bib_files_processed > 0 and files_with_duplicates > 0:
            files_with_dupes_percentage = (files_with_duplicates / bib_files_processed) * 100
            data.append(["Percentage of files with duplicates", f"{files_with_dupes_percentage:.2f}%"])
    elif operation_type == OPERATION_PROPERTIES:
        files_counted = stats.get("total_files_counted", 0)
        bytes_total = stats.get("bytes_total", 0) / 1024  # Convert to KB
        text_files = stats.get("text_files_count", 0)
        binary_files = stats.get("binary_files_count", 0)

        hr_size = ""
        size_kb = bytes_total

        if size_kb < 1024:
            hr_size = f"{size_kb:.2f} KB"
        elif size_kb < 1024 * 1024:
            hr_size = f"{size_kb / 1024:.2f} MB"
        else:
            hr_size = f"{size_kb / (1024 * 1024):.2f} GB"

        data.extend([
            ["Files analyzed", files_counted],
            ["Total data size", hr_size],
            ["Text files", text_files],
            ["Binary files", binary_files]
        ])

        if files_counted > 0:
            avg_file_size = bytes_total / max(files_counted, 1)
            if avg_file_size < 1024:
                avg_hr_size = f"{avg_file_size:.2f} KB"
            else:
                avg_hr_size = f"{avg_file_size / 1024:.2f} MB"
            data.append(["Average file size", avg_hr_size])

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
