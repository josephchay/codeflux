import os
import datetime
from ui.table import format_stats_table


def visualize_dir_tree(root_dir, output_file, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                       print_to_console=True, truncate_output=False):
    """Generate a text-based tree visualization of the directory structure."""
    exclude_dirs = exclude_dirs or []
    exclude_exts = exclude_exts or []
    exclude_files = exclude_files or []

    root_dir = os.path.abspath(root_dir)
    base_name = os.path.basename(root_dir)

    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "total_size": 0,
        "max_depth": 0,
        "time_taken": 0  # Will be updated later
    }

    start_time = datetime.datetime.now()

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Build a complete directory tree structure
    tree = {"name": base_name, "type": "dir", "children": {}, "path": root_dir}
    for root, dirs, files in os.walk(root_dir):
        dirs[:] = sorted([d for d in dirs if d not in exclude_dirs])
        rel_path = os.path.relpath(root, root_dir)
        depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))

        # Update max depth
        stats["max_depth"] = max(stats["max_depth"], depth)

        # Skip processing files in the root directory if we're at root level
        if depth > 0:
            path_parts = rel_path.split(os.sep)
            current = tree
            for i, part in enumerate(path_parts):
                if part not in current["children"]:
                    current["children"][part] = {
                        "name": part,
                        "type": "dir",
                        "children": {},
                        "path": os.path.join(current["path"], part)
                    }
                    stats["total_dirs"] += 1

                current = current["children"][part]

            # Add files to current directory
            for file in sorted(files):
                file_path = os.path.join(root, file)

                if any(file.lower().endswith(ext.lower()) for ext in exclude_exts):
                    continue
                rel_file_path = os.path.relpath(file_path, root_dir)
                norm_rel_path = rel_file_path.replace('\\', '/')
                excluded = False
                for exclude_pattern in exclude_files:
                    norm_exclude = exclude_pattern.replace('\\', '/')
                    if (norm_rel_path.lower() == norm_exclude.lower() or
                            norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                            file.lower() == norm_exclude.lower()):
                        excluded = True
                        break

                if excluded:
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    stats["total_size"] += file_size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    current["children"][file] = {
                        "name": file,
                        "type": "file",
                        "size": file_size,
                        "size_str": size_str,
                        "path": file_path
                    }
                    stats["total_files"] += 1
                except (FileNotFoundError, PermissionError):
                    # Skip files with access issues
                    continue
        else:
            # Process files directly in the root directory
            for file in sorted(files):
                file_path = os.path.join(root, file)

                # Skip excluded extensions
                if any(file.lower().endswith(ext.lower()) for ext in exclude_exts):
                    continue

                # Skip excluded file paths
                rel_file_path = os.path.relpath(file_path, root_dir)
                norm_rel_path = rel_file_path.replace('\\', '/')
                excluded = False
                for exclude_pattern in exclude_files:
                    norm_exclude = exclude_pattern.replace('\\', '/')
                    if (norm_rel_path.lower() == norm_exclude.lower() or
                            norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                            file.lower() == norm_exclude.lower()):
                        excluded = True
                        break

                if excluded:
                    continue

                try:
                    file_size = os.path.getsize(file_path)
                    stats["total_size"] += file_size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    tree["children"][file] = {
                        "name": file,
                        "type": "file",
                        "size": file_size,
                        "size_str": size_str,
                        "path": file_path
                    }
                    stats["total_files"] += 1
                except (FileNotFoundError, PermissionError):
                    # Skip files with access issues
                    continue

    # Generate the tree visualization as text for the file output
    tree_lines = []
    tree_lines.append(f"# Directory Tree Visualization")
    tree_lines.append(f"# Root: {root_dir}")
    tree_lines.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    tree_lines.append("")
    tree_lines.append(f"{base_name}/")

    # Recursively build tree lines
    def build_tree_lines(node, prefix="", is_last=True, is_root=False):
        sorted_children = []
        dirs = []
        files = []

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
            if child["type"] == "dir":
                tree_lines.append(f"{prefix}{connector}{name}/")
            else:
                tree_lines.append(f"{prefix}{connector}{name} ({child['size_str']})")

            # Recursively process children for directories
            if child["type"] == "dir":
                # Extend prefix for children based on whether this was the last item
                extended_prefix = prefix + ("    " if is_last_child else "│   ")
                build_tree_lines(child, extended_prefix, is_last_child)
    # Start the recursive tree building from the root's children
    build_tree_lines(tree, is_root=True)

    tree_lines.append("")
    tree_lines.append("# Summary")
    tree_lines.extend(format_dir_tree_summary(stats).split("\n"))
    tree_lines.append("")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    # Calculate time taken
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    # Print to console if requested
    if print_to_console:
        # Create console-specific tree lines without the summary section
        console_tree_lines = []
        console_tree_lines.append(f"{base_name}/")

        # Rebuild the tree for console display (simplified for readability)
        def build_console_lines(node, prefix="", is_last=True, is_root=False):
            sorted_children = []
            dirs = []
            files = []

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

                if child["type"] == "dir":
                    console_tree_lines.append(f"{prefix}{connector}{name}/")
                else:
                    console_tree_lines.append(f"{prefix}{connector}{name} ({child['size_str']})")

                if child["type"] == "dir":
                    extended_prefix = prefix + ("    " if is_last_child else "│   ")
                    build_console_lines(child, extended_prefix, is_last_child)
        # Start the recursive tree building for console output
        build_console_lines(tree, is_root=True)

        print("\n[DIRECTORY TREE]")

        if truncate_output:
            max_lines = min(50, len(console_tree_lines))
            truncated = len(console_tree_lines) > max_lines

            for line in console_tree_lines[:max_lines]:
                print(line)
            if truncated:
                print(f"... (truncated, full tree saved to file) ...")
        else:
            for line in console_tree_lines:
                print(line)
        print("\n[OPERATION SUMMARY]")

        # Format the summary data for the table output
        total_size = stats["total_size"]
        if total_size < 1024:
            size_str = f"{total_size} B"
        elif total_size < 1024 * 1024:
            size_str = f"{total_size / 1024:.2f} KB"
        elif total_size < 1024 * 1024 * 1024:
            size_str = f"{total_size / (1024 * 1024):.2f} MB"
        else:
            size_str = f"{total_size / (1024 * 1024 * 1024):.2f} GB"

        # Calculate average file size
        avg_file_size = 0
        if stats["total_files"] > 0:
            avg_file_size = stats["total_size"] / stats["total_files"]

        # Create table-formatted stats like other operations
        stats_data = [
            ["Time taken", f"{stats['time_taken']:.6f} seconds"],
            ["Total directories", stats["total_dirs"]],
            ["Maximum directory depth", stats["max_depth"]],
            ["Total files", stats["total_files"]],
            ["Total size", size_str]
        ]

        if stats["total_files"] > 0:
            # Add average file size if there are files
            if avg_file_size < 1024:
                avg_size_str = f"{avg_file_size:.2f} B"
            elif avg_file_size < 1024 * 1024:
                avg_size_str = f"{avg_file_size / 1024:.2f} KB"
            else:
                avg_size_str = f"{avg_file_size / (1024 * 1024):.2f} MB"
            stats_data.append(["Average file size", avg_size_str])

            # Add processing rate
            if stats['time_taken'] > 0:
                files_per_second = stats["total_files"] / max(stats['time_taken'], 0.001)
                stats_data.append(["Processing rate", f"{files_per_second:.2f} files/second"])

        # Format the stats data into a table
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

    total_size = stats["total_size"]
    if total_size < 1024:
        size_str = f"{total_size} B"
    elif total_size < 1024 * 1024:
        size_str = f"{total_size / 1024:.1f} KB"
    elif total_size < 1024 * 1024 * 1024:
        size_str = f"{total_size / (1024 * 1024):.1f} MB"
    else:
        size_str = f"{total_size / (1024 * 1024 * 1024):.1f} GB"

    summary_lines.extend([
        f"Total size: {size_str}",
        f"Maximum directory depth: {stats['max_depth']}"
    ])

    return "\n".join(summary_lines)
