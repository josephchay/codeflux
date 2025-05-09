"""
Logging utilities for the CodeFlux application.
"""

import shutil
from typing import Dict, List, Any


# Forward declaration for type hints
class OperationStats:
    pass


class Logger:
    """Simple logger for CodeFlux operations."""

    def __init__(self, silent: bool = False):
        """
        Initialize the logger.

        Args:
            silent: Whether to suppress output
        """
        self.silent = silent
        self.terminal_width = self._get_terminal_width()

    def _get_terminal_width(self) -> int:
        """Get the terminal width."""
        try:
            return shutil.get_terminal_size().columns
        except (AttributeError, OSError):
            return 80

    def info(self, message: str):
        """Log an informational message."""
        if not self.silent:
            print(message)

    def warning(self, message: str):
        """Log a warning message."""
        if not self.silent:
            print(f"Warning: {message}")

    def error(self, message: str):
        """Log an error message."""
        if not self.silent:
            print(f"Error: {message}")

    def print_file_table(self, files_info: List[Dict[str, Any]], operation_type: str):
        """
        Print a formatted table of file information.

        Args:
            files_info: List of file information dictionaries
            operation_type: Type of operation (flatten, deflatten, minify, etc.)
        """
        if not files_info:
            print("No files processed.")
            return

        # Try to use tabulate if available
        try:
            from tabulate import tabulate
            self._print_tabulate_table(files_info, operation_type)
        except ImportError:
            # Fall back to simple table formatting
            self._print_simple_table(files_info, operation_type)

    def _print_tabulate_table(self, files_info: List[Dict[str, Any]], operation_type: str):
        """Print a table using the tabulate library."""
        from tabulate import tabulate

        has_warnings = any("warnings" in file_info and file_info["warnings"] for file_info in files_info)

        if operation_type in ["flatten", "deflatten"]:
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

        elif operation_type == "minify":
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

        elif operation_type in ["bundle", "minify_bundle"]:
            headers = ["File", "Size (KB)", "Status"]
            if operation_type == "minify_bundle":
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

                if operation_type == "minify_bundle" and "original_size" in file_info:
                    row.extend([
                        f"{file_info['original_size'] / 1024:.2f}",
                        f"{file_info['reduction']:.2f}"
                    ])

                if has_warnings:
                    row.append(file_info.get("warnings", ""))

                rows.append(row)

        elif operation_type == "acroscan":
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

        elif operation_type == "properties":
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

        elif operation_type == "bibdedup":
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

        # Calculate max column widths based on terminal size
        max_table_width = self.terminal_width - 4  # 2 characters padding on each side
        max_col_widths = [
            int(max_table_width * 0.4),  # File column (40% of space)
            int(max_table_width * 0.1),  # Size column (10% of space)
            int(max_table_width * 0.2),  # Status column (20% of space)
            int(max_table_width * 0.1),  # Additional column 1 (10% of space)
            int(max_table_width * 0.1),  # Additional column 2 (10% of space)
            int(max_table_width * 0.2),  # Warnings column (20% of space)
        ]

        print(tabulate(rows, headers=headers, tablefmt="grid", maxcolwidths=max_col_widths))

    def _print_simple_table(self, files_info: List[Dict[str, Any]], operation_type: str):
        """Print a simple table for environments without tabulate."""
        has_warnings = any("warnings" in file_info and file_info["warnings"] for file_info in files_info)

        result = []
        header_format = "| {:<30} | {:<10} | {:<20} |"
        divider_format = "+{}+{}+{}+"
        divider_lens = [32, 12, 22]

        if has_warnings:
            header_format += " {:<15} |"
            divider_format += "{}+"
            divider_lens.append(17)

        if operation_type == "minify" or operation_type == "minify_bundle":
            header_format += " {:<15} | {:<12} |"
            divider_format += "{}+{}+"
            divider_lens.extend([17, 14])

        # Create header
        if operation_type in ["flatten", "deflatten"]:
            headers = ["File", "Size (KB)", "Status"]
        elif operation_type == "minify":
            headers = ["File", "Size (KB)", "Status", "Original (KB)", "Reduction %"]
        elif operation_type in ["bundle", "minify_bundle"]:
            headers = ["File", "Size (KB)", "Status"]
            if operation_type == "minify_bundle":
                headers.extend(["Original (KB)", "Reduction %"])
        elif operation_type == "acroscan":
            headers = ["File", "Size (KB)", "Acronyms", "Replaced", "Status"]
        elif operation_type == "properties":
            headers = ["File", "Size", "Type", "Modified", "Permissions"]
        elif operation_type == "bibdedup":
            headers = ["File", "Size (KB)", "Entries", "Status"]
        else:
            headers = ["File", "Size (KB)", "Status"]

        if has_warnings:
            headers.append("Warnings")

        headers_to_use = headers[:3]
        if has_warnings:
            headers_to_use.append("Warnings")
        if len(headers) > 3:
            headers_to_use.extend(headers[3:5])  # Add up to 2 more columns

        divider = divider_format.format(*["-" * length for length in divider_lens])
        result.append(divider)
        result.append(header_format.format(*headers_to_use))
        result.append(divider)

        # Add rows
        row_format = header_format
        for file_info in files_info:
            formatted_row = []

            # File column
            formatted_row.append(str(file_info["file"])[:28])

            # Size column
            if "size" in file_info:
                formatted_row.append(f"{file_info['size'] / 1024:.2f}")
            else:
                formatted_row.append("")

            # Status column
            formatted_row.append(str(file_info.get("status", ""))[:18])

            # Additional columns based on operation type
            if has_warnings:
                formatted_row.append(str(file_info.get("warnings", ""))[:13])

            if operation_type == "minify" or operation_type == "minify_bundle":
                if "original_size" in file_info:
                    formatted_row.append(f"{file_info['original_size'] / 1024:.2f}")
                else:
                    formatted_row.append("")

                if "reduction" in file_info:
                    formatted_row.append(f"{file_info['reduction']:.2f}")
                else:
                    formatted_row.append("")

            result.append(row_format.format(*formatted_row))

        result.append(divider)
        print("\n".join(result))

    def print_stats(self, stats: Any, operation_type: str):
        """
        Print operation statistics.

        Args:
            stats: OperationStats object with operation results
            operation_type: Type of operation (flatten, deflatten, minify, etc.)
        """
        try:
            from tabulate import tabulate
            self._print_tabulate_stats(stats, operation_type)
        except ImportError:
            self._print_simple_stats(stats, operation_type)

    def _print_tabulate_stats(self, stats: Any, operation_type: str):
        """Print statistics using the tabulate library."""
        from tabulate import tabulate

        data = [
            ["Time taken", f"{stats.duration:.6f} seconds"],
            ["Directories scanned", stats.dirs_traversed],
            ["Maximum nesting level", stats.max_nesting_level],
            ["Total files scanned", stats.total_files_processed],
            ["Files skipped", f"{stats.skipped_files} (non-target or excluded)"]
        ]

        # Add empty files count if available and non-zero
        if getattr(stats, "empty_files", 0) > 0:
            data.append(["Empty files", stats.empty_files])

        if operation_type in ["flatten", "deflatten"]:
            files_copied = stats.files_copied
            bytes_copied = stats.bytes_copied / 1024  # Convert to KB
            avg_file_size = bytes_copied / max(files_copied, 1)

            if operation_type == "flatten":
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
                    ["Directories created", stats.dirs_created],
                ])
                if files_copied > 0:
                    data.append(["Average file size", f"{avg_file_size:.2f} KB"])

        elif operation_type == "bundle":
            files_bundled = stats.files_bundled
            bytes_bundled = stats.bytes_bundled / 1024  # Convert to KB
            avg_file_size = bytes_bundled / max(files_bundled, 1)
            data.extend([
                ["Files bundled", files_bundled],
                ["Data bundled", f"{bytes_bundled:.2f} KB"],
            ])

            if hasattr(stats, "files_with_snippets") and stats.files_with_snippets > 0:
                data.append(["Files with snippets applied", stats.files_with_snippets])
                total_files = stats.files_bundled
                if total_files > 0:
                    snippet_percentage = (stats.files_with_snippets / total_files) * 100
                    data.append(["Percentage of files with snippets", f"{snippet_percentage:.1f}%"])

            if files_bundled > 0:
                data.append(["Average file size", f"{avg_file_size:.2f} KB"])

        elif operation_type == "minify" or operation_type == "minify_bundle":
            files_copied = stats.files_copied
            files_minified = stats.files_minified
            bytes_original = stats.bytes_original / 1024  # Convert to KB
            bytes_minified = stats.bytes_minified / 1024  # Convert to KB
            data.extend([
                ["Files processed", files_copied],
                ["Files minified", files_minified],
            ])

            if hasattr(stats, "failed_minifications") and stats.failed_minifications > 0:
                data.append(["Files with failed minification", stats.failed_minifications])
                if files_copied > 0:
                    fail_percentage = (stats.failed_minifications / files_copied) * 100
                    data.append(["Percentage of failed minifications", f"{fail_percentage:.1f}%"])

            if files_copied > 0:
                avg_orig_size = bytes_original / max(files_copied, 1)
                avg_mini_size = bytes_minified / max(files_copied, 1)
                data.extend([
                    ["Average original file size", f"{avg_orig_size:.2f} KB"],
                    ["Average minified file size", f"{avg_mini_size:.2f} KB"],
                ])

            if bytes_original > 0:
                reduction = (1 - stats.bytes_minified / max(stats.bytes_original, 1)) * 100
                data.extend([
                    ["Original size", f"{bytes_original:.2f} KB"],
                    ["Minified size", f"{bytes_minified:.2f} KB"],
                    ["Size reduction", f"{reduction:.2f}%"],
                ])

        # Add files processing rate if applicable
        files_processed = stats.total_files_processed
        if files_processed > 0:
            files_per_second = files_processed / max(stats.duration, 0.001)
            data.append(["Processing rate", f"{files_per_second:.2f} files/second"])

        print("\n[OPERATION SUMMARY]")
        print(tabulate(data, headers=["Statistic", "Value"], tablefmt="grid"))

    def _print_simple_stats(self, stats: Any, operation_type: str):
        """Print simple statistics for environments without tabulate."""
        result = ["\n[OPERATION SUMMARY]"]

        data = [
            f"Time taken: {stats.duration:.6f} seconds",
            f"Directories scanned: {stats.dirs_traversed}",
            f"Maximum nesting level: {stats.max_nesting_level}",
            f"Total files scanned: {stats.total_files_processed}",
            f"Files skipped: {stats.skipped_files} (non-target or excluded)"
        ]

        # Add empty files count if available and non-zero
        if getattr(stats, "empty_files", 0) > 0:
            data.append(f"Empty files: {stats.empty_files}")

        if operation_type in ["flatten", "deflatten"]:
            files_copied = stats.files_copied
            bytes_copied = stats.bytes_copied / 1024  # Convert to KB

            if operation_type == "flatten":
                data.extend([
                    f"Files in flatten output: {files_copied}",
                    f"Data in flatten output: {bytes_copied:.2f} KB",
                ])
                if files_copied > 0:
                    avg_file_size = bytes_copied / max(files_copied, 1)
                    data.append(f"Average file size: {avg_file_size:.2f} KB")
            else:
                data.extend([
                    f"Files in deflatten output: {files_copied}",
                    f"Data in deflatten output: {bytes_copied:.2f} KB",
                    f"Directories created: {stats.dirs_created}",
                ])
                if files_copied > 0:
                    avg_file_size = bytes_copied / max(files_copied, 1)
                    data.append(f"Average file size: {avg_file_size:.2f} KB")

        elif operation_type == "bundle":
            files_bundled = stats.files_bundled
            bytes_bundled = stats.bytes_bundled / 1024  # Convert to KB
            data.extend([
                f"Files bundled: {files_bundled}",
                f"Data bundled: {bytes_bundled:.2f} KB",
            ])

            if hasattr(stats, "files_with_snippets") and stats.files_with_snippets > 0:
                data.append(f"Files with snippets applied: {stats.files_with_snippets}")
                total_files = stats.files_bundled
                if total_files > 0:
                    snippet_percentage = (stats.files_with_snippets / total_files) * 100
                    data.append(f"Percentage of files with snippets: {snippet_percentage:.1f}%")

            if files_bundled > 0:
                avg_file_size = bytes_bundled / max(files_bundled, 1)
                data.append(f"Average file size: {avg_file_size:.2f} KB")

        elif operation_type == "minify" or operation_type == "minify_bundle":
            files_copied = stats.files_copied
            files_minified = stats.files_minified
            bytes_original = stats.bytes_original / 1024  # Convert to KB
            bytes_minified = stats.bytes_minified / 1024  # Convert to KB
            data.extend([
                f"Files processed: {files_copied}",
                f"Files minified: {files_minified}",
            ])

            if hasattr(stats, "failed_minifications") and stats.failed_minifications > 0:
                data.append(f"Files with failed minification: {stats.failed_minifications}")
                if files_copied > 0:
                    fail_percentage = (stats.failed_minifications / files_copied) * 100
                    data.append(f"Percentage of failed minifications: {fail_percentage:.1f}%")

            if files_copied > 0:
                avg_orig_size = bytes_original / max(files_copied, 1)
                avg_mini_size = bytes_minified / max(files_copied, 1)
                data.extend([
                    f"Average original file size: {avg_orig_size:.2f} KB",
                    f"Average minified file size: {avg_mini_size:.2f} KB",
                ])

            if bytes_original > 0:
                reduction = (1 - stats.bytes_minified / max(stats.bytes_original, 1)) * 100
                data.extend([
                    f"Original size: {bytes_original:.2f} KB",
                    f"Minified size: {bytes_minified:.2f} KB",
                    f"Size reduction: {reduction:.2f}%",
                ])

        # Add files processing rate if applicable
        files_processed = stats.total_files_processed
        if files_processed > 0:
            files_per_second = files_processed / max(stats.duration, 0.001)
            data.append(f"Processing rate: {files_per_second:.2f} files/second")

        result.extend(data)
        print("\n".join(result))
