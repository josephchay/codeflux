import os
import datetime

from constants import ROOT_TREE_UI_TRUNCATE_DIRS
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


def should_process_file(file_path, rel_path, extensions, exclude_exts, exclude_files):
    """Determine if a file should be processed based on filtering."""
    file_name = os.path.basename(file_path)

    # Check excluded extensions
    if any(file_path.lower().endswith(ext.lower()) for ext in exclude_exts):
        return False

    # Check excluded files
    norm_rel_path = rel_path.replace('\\', '/')
    for exclude_pattern in exclude_files:
        norm_exclude = exclude_pattern.replace('\\', '/')
        if (norm_rel_path.lower() == norm_exclude.lower() or
                norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                file_name.lower() == norm_exclude.lower()):
            return False

    # Check if file has a handled extension
    return any(file_path.lower().endswith(ext.lower()) for ext in extensions)


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
                    size_str = format_file_size(file_size)

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
                    size_str = format_file_size(file_size)

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

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    if print_to_console:
        console_tree_lines = []
        console_tree_lines.append(f"{base_name}/")

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

        total_size = stats["total_size"]
        total_size_str = format_file_size(total_size)
        avg_file_size = 0
        if stats["total_files"] > 0:
            avg_file_size = stats["total_size"] / stats["total_files"]
            avg_size_str = format_file_size(avg_file_size)

        # Create table-formatted stats like other operations
        stats_data = [
            ["Time taken", f"{stats['time_taken']:.6f} seconds"],
            ["Total directories", stats["total_dirs"]],
            ["Maximum directory depth", stats["max_depth"]],
            ["Total files", stats["total_files"]],
            ["Total size", total_size_str]
        ]

        if stats["total_files"] > 0:
            # Add average file size if there are files
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
            print("\n".join([f"{row[0]}: {row[1]}" for row in stats_data]))

    return stats


def visualize_root_dir_tree(root_dir, output_file, print_to_console=True, truncate_output=False,
                            show_processing_status=False):
    """
    Generate a complete tree visualization of the root directory structure with
    status indicators showing which files/directories would be processed or excluded.
    """
    root_dir = os.path.abspath(root_dir)
    base_name = os.path.basename(root_dir)

    # Define status symbols
    status_symbols = {
        "processed": "✓",
        "excluded": "✗",
        "mixed": "⟳",
        "error": "!",
        "unknown": "?"
    }

    # Initialize statistics
    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "total_size": 0,
        "max_depth": 0,
        "time_taken": 0,
        "processed_files": 0,
        "excluded_files": 0,
        "processed_dirs": 0,
        "excluded_dirs": 0,
        "mixed_dirs": 0,
        "processed_size": 0
    }

    start_time = datetime.datetime.now()

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    exclude_dirs = DEFAULT_EXCLUDE_DIRS if show_processing_status else []
    exclude_exts = ALL_EXCLUDE_EXTENSIONS if show_processing_status else []
    exclude_files = ALL_EXCLUDE_FILENAMES if show_processing_status else []

    def is_file_processed(file_path, rel_path):
        """Determine if a file would be processed based on the filtering rules."""
        dir_path = os.path.dirname(rel_path)
        dir_parts = dir_path.replace('\\', '/').split('/')
        if any(exclude_dir in dir_parts for exclude_dir in exclude_dirs):
            return False
        if any(file_path.lower().endswith(ext.lower()) for ext in exclude_exts):
            return False
        file_name = os.path.basename(file_path)
        norm_rel_path = rel_path.replace('\\', '/')
        for exclude_pattern in exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if (norm_rel_path.lower() == norm_exclude.lower() or
                    norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                    file_name.lower() == norm_exclude.lower()):
                return False

        return any(file_path.lower().endswith(ext.lower()) for ext in ALL_EXTENSIONS)

    # Check if a directory would be processed
    def is_dir_excluded(dir_path):
        """Check if a directory would be excluded."""
        dir_name = os.path.basename(dir_path)
        return dir_name in exclude_dirs

    tree = {"name": base_name, "type": "dir", "children": {}, "path": root_dir, "status": "unknown", "depth": 0}

    for root, dirs, files in os.walk(root_dir):
        rel_path = os.path.relpath(root, root_dir)
        depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))
        stats["max_depth"] = max(stats["max_depth"], depth)
        if rel_path == '.':
            current = tree
        else:
            path_parts = rel_path.split(os.sep)
            current = tree
            for i, part in enumerate(path_parts):
                if part not in current["children"]:
                    dir_path = os.path.join(current["path"], part)
                    rel_dir_path = os.path.relpath(dir_path, root_dir)
                    is_excluded = is_dir_excluded(dir_path)
                    status = "excluded" if is_excluded else "processed"

                    # Create node
                    dir_node = {
                        "name": part,
                        "type": "dir",
                        "children": {},
                        "path": dir_path,
                        "status": status,  # Initial status, may be updated later
                        "depth": i + 1  # Store the depth for display decisions (root is 0, first level is 1)
                    }

                    # Update stats
                    stats["total_dirs"] += 1
                    if status == "processed":
                        stats["processed_dirs"] += 1
                    else:
                        stats["excluded_dirs"] += 1
                    current["children"][part] = dir_node
                current = current["children"][part]

        # Process files
        for file in sorted(files):
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, root_dir)

            try:
                file_size = os.path.getsize(file_path)
                size_str = format_file_size(file_size)
                is_processed = is_file_processed(file_path, rel_file_path)
                status = "processed" if is_processed else "excluded"

                # Create file node
                file_node = {
                    "name": file,
                    "type": "file",
                    "size": file_size,
                    "size_str": size_str,
                    "path": file_path,
                    "status": status,
                    "depth": depth  # Store the depth for display decisions
                }

                stats["total_files"] += 1
                stats["total_size"] += file_size
                if status == "processed":
                    stats["processed_files"] += 1
                    stats["processed_size"] += file_size
                else:
                    stats["excluded_files"] += 1
                current["children"][file] = file_node

            except (FileNotFoundError, PermissionError, OSError):
                # Handle access issues
                file_node = {
                    "name": file,
                    "type": "file",
                    "size": 0,
                    "size_str": "N/A (error)",
                    "path": file_path,
                    "status": "error",
                    "depth": depth  # Store the depth for display decisions
                }
                current["children"][file] = file_node
                stats["total_files"] += 1

    # Update directory statuses based on children
    def update_dir_statuses(node):
        """
        Recursively update directory statuses based on children.
        Returns status of current node.
        """
        if node["type"] != "dir" or not node["children"]:
            return node["status"]

        # Process children first (depth-first)
        child_statuses = []
        for child_name, child_node in node["children"].items():
            if child_node["type"] == "dir":
                child_status = update_dir_statuses(child_node)
                child_statuses.append(child_status)
            else:
                child_statuses.append(child_node["status"])

        # Determine status based on children
        if not child_statuses:
            # Empty directory keeps its initial status
            return node["status"]

        if all(status == "processed" for status in child_statuses):
            node["status"] = "processed"
        elif all(status == "excluded" for status in child_statuses):
            node["status"] = "excluded"
        else:
            # Mixed statuses
            old_status = node["status"]
            node["status"] = "mixed"

            # Only increment mixed_dirs if it wasn't already counted
            if old_status != "mixed":
                stats["mixed_dirs"] += 1

                # Adjust processed/excluded dir counts
                if old_status == "processed":
                    stats["processed_dirs"] -= 1
                elif old_status == "excluded":
                    stats["excluded_dirs"] -= 1

        return node["status"]

    # Update all directory statuses
    update_dir_statuses(tree)

    # Generate tree visualization for file output
    tree_lines = []
    tree_lines.append(f"# Root Directory Tree Visualization")
    tree_lines.append(f"# Root: {root_dir}")
    tree_lines.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if show_processing_status:
        tree_lines.append(f"# Processing Status Symbols: {status_symbols['processed']} (processed), "
                          f"{status_symbols['excluded']} (excluded), {status_symbols['mixed']} (mixed)")

    tree_lines.append("")

    # Add root with status
    if show_processing_status:
        root_symbol = status_symbols.get(tree["status"], "?")
        tree_lines.append(f"{base_name}/ {root_symbol}")
    else:
        tree_lines.append(f"{base_name}/")

    # Recursively build tree lines for file output (includes everything)
    def build_tree_lines(node, prefix="", is_last=True):
        sorted_children = []
        dirs = []
        files = []

        # Sort dirs and files
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
                if show_processing_status:
                    symbol = status_symbols.get(child["status"], "?")
                    tree_lines.append(f"{prefix}{connector}{name}/ {symbol}")
                else:
                    tree_lines.append(f"{prefix}{connector}{name}/")

                # Process children
                extended_prefix = prefix + ("    " if is_last_child else "│   ")
                build_tree_lines(child, extended_prefix, is_last_child)
            else:
                # File node
                if show_processing_status:
                    symbol = status_symbols.get(child["status"], "?")
                    tree_lines.append(f"{prefix}{connector}{name} ({child['size_str']}) {symbol}")
                else:
                    tree_lines.append(f"{prefix}{connector}{name} ({child['size_str']})")

    # Start building tree lines for file output
    build_tree_lines(tree)

    tree_lines.append("")
    tree_lines.append("# Summary")
    tree_lines.append(f"Total directories: {stats['total_dirs']}")
    if show_processing_status:
        tree_lines.append(f"  - Processed directories: {stats['processed_dirs']}")
        tree_lines.append(f"  - Excluded directories: {stats['excluded_dirs']}")
        tree_lines.append(f"  - Mixed directories: {stats['mixed_dirs']}")
    tree_lines.append(f"Total files: {stats['total_files']}")
    if show_processing_status:
        tree_lines.append(f"  - Processed files: {stats['processed_files']}")
        tree_lines.append(f"  - Excluded files: {stats['excluded_files']}")
    total_size_str = format_file_size(stats["total_size"])
    tree_lines.append(f"Total size: {total_size_str}")
    if show_processing_status:
        processed_size_str = format_file_size(stats["processed_size"])
        tree_lines.append(f"  - Processed size: {processed_size_str}")
    tree_lines.append(f"Maximum directory depth: {stats['max_depth']}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    if print_to_console:
        print("\n[ROOT DIRECTORY TREE]")
        console_lines = []

        if show_processing_status:
            root_symbol = status_symbols.get(tree["status"], "?")
            console_lines.append(f"{base_name}/ {root_symbol}")
        else:
            console_lines.append(f"{base_name}/")

        # Special function to build console tree lines with special handling for directories to truncate
        def build_console_lines(node, prefix="", is_last=True, path=None):
            if path is None:
                path = []

            sorted_children = []
            dirs = []
            files = []

            # Sort dirs and files
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

                if child["type"] == "dir" and name in ROOT_TREE_UI_TRUNCATE_DIRS:
                    if show_processing_status:
                        symbol = status_symbols.get(child["status"], "?")
                        console_lines.append(f"{prefix}{connector}{name}/ {symbol}")
                    else:
                        console_lines.append(f"{prefix}{connector}{name}/")
                    extended_prefix = prefix + ("    " if is_last_child else "│   ")
                    console_lines.append(f"{extended_prefix}[Content inside {name} directory - full tree saved to file]")

                    # Skip processing children
                    continue

                # Normal handling for other directories and files
                if child["type"] == "dir":
                    if show_processing_status:
                        symbol = status_symbols.get(child["status"], "?")
                        console_lines.append(f"{prefix}{connector}{name}/ {symbol}")
                    else:
                        console_lines.append(f"{prefix}{connector}{name}/")

                    # Process children
                    extended_prefix = prefix + ("    " if is_last_child else "│   ")
                    new_path = path + [name]
                    build_console_lines(child, extended_prefix, is_last_child, new_path)
                else:
                    # File node
                    if show_processing_status:
                        symbol = status_symbols.get(child["status"], "?")
                        console_lines.append(f"{prefix}{connector}{name} ({child['size_str']}) {symbol}")
                    else:
                        console_lines.append(f"{prefix}{connector}{name} ({child['size_str']})")

        # Start building console lines
        build_console_lines(tree)

        # Display console lines with possible truncation
        if truncate_output and len(console_lines) > 50:
            for line in console_lines[:50]:
                print(line)
            print(f"... (truncated, full tree saved to file) ...")
        else:
            for line in console_lines:
                print(line)

        # Print summary table
        print("\n[OPERATION SUMMARY]")
        stats_data = [
            ["Time taken", f"{duration:.6f} seconds"],
            ["Total directories", stats["total_dirs"]]
        ]

        if show_processing_status:
            stats_data.append(["Processed directories", stats["processed_dirs"]])
            stats_data.append(["Excluded directories", stats["excluded_dirs"]])
            stats_data.append(["Mixed directories", stats["mixed_dirs"]])

        stats_data.extend([
            ["Maximum directory depth", stats["max_depth"]],
            ["Total files", stats["total_files"]]
        ])

        if show_processing_status:
            stats_data.append(["Processed files", stats["processed_files"]])
            stats_data.append(["Excluded files", stats["excluded_files"]])

        stats_data.append(["Total size", total_size_str])

        if show_processing_status:
            stats_data.append(["Processed size", processed_size_str])

        # Add average file size and processing rate
        if stats["total_files"] > 0:
            avg_file_size = stats["total_size"] / stats["total_files"]
            avg_size_str = format_file_size(avg_file_size)
            stats_data.append(["Average file size", avg_size_str])

            if duration > 0:
                files_per_second = stats["total_files"] / max(duration, 0.001)
                stats_data.append(["Processing rate", f"{files_per_second:.2f} files/second"])

        # Display as table
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
    total_size_str = format_file_size(total_size)

    summary_lines.extend([
        f"Total size: {total_size_str}",
        f"Maximum directory depth: {stats['max_depth']}"
    ])

    return "\n".join(summary_lines)
