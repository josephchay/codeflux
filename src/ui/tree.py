import os
import datetime
from ui.table import format_stats_table


def format_file_size(size_in_bytes):
    """Format file size to human-readable string."""
    if size_in_bytes < 1024:
        return f"{size_in_bytes} B"
    elif size_in_bytes < 1024 * 1024:
        return f"{size_in_bytes / 1024:.1f} KB"
    elif size_in_bytes < 1024 * 1024 * 1024:
        return f"{size_in_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_in_bytes / (1024 * 1024 * 1024):.1f} GB"


def is_file_excluded(file_path, rel_path, exclude_exts, exclude_files):
    """Check if a file should be excluded based on extension or path."""
    # Check excluded extensions
    if any(file_path.lower().endswith(ext.lower()) for ext in exclude_exts):
        return True

    # Check excluded file paths
    file_name = os.path.basename(file_path)
    norm_rel_path = rel_path.replace('\\', '/')

    for exclude_pattern in exclude_files:
        norm_exclude = exclude_pattern.replace('\\', '/')
        if (norm_rel_path.lower() == norm_exclude.lower() or
                norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                file_name.lower() == norm_exclude.lower()):
            return True

    return False


def should_process_file(file_path, rel_path, extensions, exclude_exts, exclude_files):
    """Determine if a file should be processed based on filters."""
    if is_file_excluded(file_path, rel_path, exclude_exts, exclude_files):
        return False
    return any(file_path.lower().endswith(ext.lower()) for ext in extensions)


def build_directory_tree(root_dir, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                         extensions=None, show_processing_status=False):
    """Build a complete directory tree structure as a nested dictionary."""
    exclude_dirs = exclude_dirs or []
    exclude_exts = exclude_exts or []
    exclude_files = exclude_files or []

    root_dir = os.path.abspath(root_dir)
    base_name = os.path.basename(root_dir)

    # Initialize statistics
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "total_size": 0,
        "max_depth": 0,
    }

    if show_processing_status:
        stats.update({
            "processed_files": 0,
            "excluded_files": 0,
            "processed_dirs": 0,
            "excluded_dirs": 0,
            "mixed_dirs": 0,
            "processed_size": 0
        })

    # Create the root node
    tree = {"name": base_name, "type": "dir", "children": {}, "path": root_dir}
    if show_processing_status:
        tree["status"] = "unknown"

    # Walk the directory tree
    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = sorted([d for d in dirs if d not in exclude_dirs])

        # Calculate relative path and depth
        rel_path = os.path.relpath(root, root_dir)
        depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))

        # Update max depth statistic
        stats["max_depth"] = max(stats["max_depth"], depth)

        # Get or create current node in the tree
        if rel_path == '.':
            current = tree
        else:
            # Navigate to the correct node for the current path
            path_parts = rel_path.split(os.sep)
            current = tree

            for part in path_parts:
                if part not in current["children"]:
                    dir_path = os.path.join(current["path"], part)
                    dir_node = {
                        "name": part,
                        "type": "dir",
                        "children": {},
                        "path": dir_path
                    }

                    # Add processing status if needed
                    if show_processing_status:
                        dir_status = "processed" if part not in exclude_dirs else "excluded"
                        dir_node["status"] = dir_status
                        if dir_status == "processed":
                            stats["processed_dirs"] += 1
                        else:
                            stats["excluded_dirs"] += 1

                    current["children"][part] = dir_node
                    stats["total_dirs"] += 1

                current = current["children"][part]

        # Process files in current directory
        for file in sorted(files):
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, root_dir)

            # Determine if the file should be excluded
            excluded = is_file_excluded(file_path, rel_file_path, exclude_exts, exclude_files)
            if not excluded or show_processing_status:  # Include all files in complete tree mode
                try:
                    file_size = os.path.getsize(file_path)
                    size_str = format_file_size(file_size)

                    file_node = {
                        "name": file,
                        "type": "file",
                        "size": file_size,
                        "size_str": size_str,
                        "path": file_path
                    }

                    # Only count non-excluded files in standard tree mode
                    if not excluded or show_processing_status:
                        stats["total_files"] += 1
                        stats["total_size"] += file_size

                    # Add processing status if needed
                    if show_processing_status:
                        if extensions:
                            file_status = "processed" if should_process_file(
                                file_path, rel_file_path, extensions, exclude_exts, exclude_files) else "excluded"
                        else:
                            file_status = "processed" if not excluded else "excluded"

                        file_node["status"] = file_status

                        if file_status == "processed":
                            stats["processed_files"] += 1
                            stats["processed_size"] += file_size
                        else:
                            stats["excluded_files"] += 1

                    # Only add to tree if not excluded in standard mode, or always in complete mode
                    if not excluded or show_processing_status:
                        current["children"][file] = file_node

                except (FileNotFoundError, PermissionError):
                    # Skip files with access issues
                    if show_processing_status:
                        current["children"][file] = {
                            "name": file,
                            "type": "file",
                            "size": 0,
                            "size_str": "N/A",
                            "path": file_path,
                            "status": "error"
                        }

    # Update directory status based on children if using processing status
    if show_processing_status:
        def update_dir_status(node):
            """Update directory status based on its children."""
            if node["type"] == "dir" and node["children"]:
                child_statuses = [child.get("status", "unknown") for child in node["children"].values()]

                if all(status == "processed" for status in child_statuses):
                    node["status"] = "processed"
                    return "processed"
                elif all(status == "excluded" for status in child_statuses):
                    node["status"] = "excluded"
                    return "excluded"
                else:
                    node["status"] = "mixed"
                    stats["mixed_dirs"] += 1
                    return "mixed"
            return node.get("status", "unknown")

        def recursively_update_status(node):
            """Recursively update status for all directories in the tree."""
            if node["type"] == "dir":
                for child in node["children"].values():
                    recursively_update_status(child)
                update_dir_status(node)

        recursively_update_status(tree)

    return tree, stats


def generate_tree_visualization(tree, stats, include_status=False, is_complete_tree=False):
    """Generate text lines for tree visualization."""
    base_name = tree["name"]
    tree_lines = []

    if is_complete_tree:
        tree_lines.append(f"# Complete Directory Tree Visualization")
    else:
        tree_lines.append(f"# Directory Tree Visualization")
    tree_lines.append(f"# Root: {tree['path']}")
    tree_lines.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if include_status:
        tree_lines.append(f"# Processing Status Symbols: ✓ (processed), ✗ (excluded), ⟳ (mixed)")
    tree_lines.append("")

    # Status symbols mapping
    status_symbols = {
        "processed": "✓",
        "excluded": "✗",
        "mixed": "⟳",
        "error": "!",
        "unknown": "?"
    }

    # Add root with status if needed
    if include_status:
        root_symbol = status_symbols.get(tree.get("status", "unknown"), "?")
        tree_lines.append(f"{base_name}/ {root_symbol}")
    else:
        tree_lines.append(f"{base_name}/")

    # Recursively build tree lines
    def build_tree_lines(node, prefix="", is_last=True):
        sorted_children = []
        dirs = []
        files = []

        # Sort directories and files separately
        for name, child in node["children"].items():
            if child["type"] == "dir":
                dirs.append((name, child))
            else:
                files.append((name, child))
        dirs.sort()
        files.sort()
        sorted_children = dirs + files
        for i, (name, child) in enumerate(sorted_children):
            is_last_child = (i == len(sorted_children) - 1)
            connector = "└── " if is_last_child else "├── "
            line = f"{prefix}{connector}"
            if child["type"] == "dir":
                if include_status:
                    symbol = status_symbols.get(child.get("status", "unknown"), "?")
                    line += f"{name}/ {symbol}"
                else:
                    line += f"{name}/"
            else:
                if include_status:
                    symbol = status_symbols.get(child.get("status", "unknown"), "?")
                    line += f"{name} ({child['size_str']}) {symbol}"
                else:
                    line += f"{name} ({child['size_str']})"
            tree_lines.append(line)

            # Recursively process children for directories
            if child["type"] == "dir":
                # Extend prefix for children based on whether this was the last item
                extended_prefix = prefix + ("    " if is_last_child else "│   ")
                build_tree_lines(child, extended_prefix, is_last_child)

    # Start the recursive tree building
    build_tree_lines(tree)

    # Add summary information
    tree_lines.append("")
    tree_lines.append("# Summary")
    tree_lines.append(f"Total directories: {stats['total_dirs']}")
    if include_status:
        tree_lines.append(f"  - Processed directories: {stats['processed_dirs']}")
        tree_lines.append(f"  - Excluded directories: {stats['excluded_dirs']}")
        tree_lines.append(f"  - Mixed directories: {stats['mixed_dirs']}")
    tree_lines.append(f"Total files: {stats['total_files']}")
    if include_status:
        tree_lines.append(f"  - Processed files: {stats['processed_files']}")
        tree_lines.append(f"  - Excluded files: {stats['excluded_files']}")

    # Add size information
    total_size_str = format_file_size(stats["total_size"])
    tree_lines.append(f"Total size: {total_size_str}")
    if include_status:
        processed_size_str = format_file_size(stats["processed_size"])
        tree_lines.append(f"  - Processed size: {processed_size_str}")
    tree_lines.append(f"Maximum directory depth: {stats['max_depth']}")
    tree_lines.append("")

    return tree_lines


def format_stats_for_display(stats, include_processing_stats=False, duration=0):
    """Format statistics into a list of rows for tabular display."""
    total_size_str = format_file_size(stats["total_size"])

    stats_data = [
        ["Time taken", f"{duration:.6f} seconds"],
        ["Total directories", stats["total_dirs"]],
        ["Maximum directory depth", stats["max_depth"]],
        ["Total files", stats["total_files"]],
        ["Total size", total_size_str]
    ]

    if include_processing_stats:
        # Insert processing stats at appropriate positions
        stats_data.insert(2, ["Processed directories", stats["processed_dirs"]])
        stats_data.insert(3, ["Excluded directories", stats["excluded_dirs"]])
        stats_data.insert(4, ["Mixed directories", stats["mixed_dirs"]])
        stats_data.insert(6, ["Processed files", stats["processed_files"]])
        stats_data.insert(7, ["Excluded files", stats["excluded_files"]])

        processed_size_str = format_file_size(stats["processed_size"])
        stats_data.insert(10, ["Processed size", processed_size_str])

    # Calculate average file size and processing rate
    if stats["total_files"] > 0:
        avg_file_size = stats["total_size"] / stats["total_files"]
        avg_size_str = format_file_size(avg_file_size)
        stats_data.append(["Average file size", avg_size_str])

        if duration > 0:
            files_per_second = stats["total_files"] / max(duration, 0.001)
            stats_data.append(["Processing rate", f"{files_per_second:.2f} files/second"])

    return stats_data


def visualize_dir_tree(root_dir, output_file, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                       print_to_console=True, truncate_output=False):
    """
    Generate a text-based tree visualization of the directory structure,
    focusing only on files that pass the exclusion filters.
    """
    start_time = datetime.datetime.now()

    # Build the directory tree (standard version - excludes filtered files)
    tree, stats = build_directory_tree(
        root_dir,
        exclude_dirs=exclude_dirs,
        exclude_exts=exclude_exts,
        exclude_files=exclude_files,
        show_processing_status=False
    )

    tree_lines = generate_tree_visualization(tree, stats, include_status=False, is_complete_tree=False)

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    if print_to_console:
        print("\n[DIRECTORY TREE]")

        # Handle truncation for console output
        display_lines = []
        # Get just the tree structure (skip headers, start with root dir)
        for line in tree_lines:
            if line.startswith(tree["name"]):
                display_lines.append(line)
                break

        # Get the remaining tree structure (skip summary at the end)
        content_lines = []
        for line in tree_lines[len(tree_lines) - tree_lines[::-1].index(display_lines[0]):]:
            if line.strip() and not line.startswith("#") and not line == "":
                content_lines.append(line)
            # Stop when we hit an empty line (before summary)
            if line == "" and len(content_lines) > 0:
                break

        # Add the rest of the content lines to display
        display_lines.extend(content_lines[1:])

        if truncate_output and len(display_lines) > 50:
            print("\n".join(display_lines[:50]))
            print(f"... (truncated, full tree saved to file) ...")
        else:
            print("\n".join(display_lines))

        print("\n[OPERATION SUMMARY]")
        stats_data = format_stats_for_display(stats, include_processing_stats=False, duration=duration)

        try:
            from tabulate import tabulate
            table = tabulate(stats_data, headers=["Statistic", "Value"], tablefmt="grid")
            print(table)
        except ImportError:
            # Fallback if tabulate is not available
            print("\n".join([f"{row[0]}: {row[1]}" for row in stats_data]))

    return stats


def visualize_complete_dir_tree(root_dir, output_file, show_processing_status=False, extensions=None,
                                exclude_dirs=None, exclude_exts=None, exclude_files=None,
                                print_to_console=True, truncate_output=False):
    """
    Generate a complete directory tree visualization showing all files and directories.
    Optionally indicate which files/folders are being processed with symbols when an operation is active.
    """
    start_time = datetime.datetime.now()

    # Build the complete directory tree
    tree, stats = build_directory_tree(root_dir, exclude_dirs=exclude_dirs, exclude_exts=exclude_exts,
                                       exclude_files=exclude_files, extensions=extensions,
                                       show_processing_status=show_processing_status)
    tree_lines = generate_tree_visualization(tree, stats, include_status=show_processing_status, is_complete_tree=True)

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    if print_to_console:
        print("\n[COMPLETE DIRECTORY TREE]")

        # Handle truncation for console output - similar to visualize_dir_tree
        display_lines = []
        # Get just the tree structure (skip headers, start with root dir)
        for line in tree_lines:
            if line.startswith(tree["name"]):
                display_lines.append(line)
                break

        # Get the remaining tree structure (skip summary at the end)
        content_lines = []
        for line in tree_lines[len(tree_lines) - tree_lines[::-1].index(display_lines[0]):]:
            if line.strip() and not line.startswith("#") and not line == "":
                content_lines.append(line)
            # Stop when we hit an empty line (before summary)
            if line == "" and len(content_lines) > 0:
                break

        # Add the rest of the content lines to display
        display_lines.extend(content_lines[1:])

        # Apply truncation if requested
        if truncate_output and len(display_lines) > 50:
            print("\n".join(display_lines[:50]))
            print(f"... (truncated, full tree saved to file) ...")
        else:
            print("\n".join(display_lines))

        # Display statistics in table format
        print("\n[OPERATION SUMMARY]")
        stats_data = format_stats_for_display(stats, include_processing_stats=show_processing_status, duration=duration)

        try:
            from tabulate import tabulate
            table = tabulate(stats_data, headers=["Statistic", "Value"], tablefmt="grid")
            print(table)
        except ImportError:
            # Fallback if tabulate is not available
            print("\n".join([f"{row[0]}: {row[1]}" for row in stats_data]))

    return stats


def format_dir_tree_summary(stats):
    """Format tree statistics into a human-readable summary."""
    summary_lines = [
        f"Total files: {stats['total_files']}",
        f"Total directories: {stats['total_dirs']}"
    ]
    total_size_str = format_file_size(stats["total_size"])
    summary_lines.extend([
        f"Total size: {total_size_str}",
        f"Maximum directory depth: {stats['max_depth']}"
    ])

    return "\n".join(summary_lines)
