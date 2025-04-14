import os
import datetime
import re

from constants import DEFAULT_EXCLUDE_DIRS, ALL_EXTENSIONS, ALL_EXCLUDE_EXTENSIONS, ALL_EXCLUDE_FILENAMES, \
    ROOT_TREE_UI_EXCLUDE_DIRS, ROOT_TREE_UI_STATUS_SYMBOLS
from utils import should_process_file


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
                rel_file_path = os.path.relpath(file_path, root_dir)
                if not should_process_file(file, ALL_EXTENSIONS, exclude_exts, exclude_files, file_rel_path=rel_file_path):
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
                rel_file_path = os.path.relpath(file_path, root_dir)
                if not should_process_file(file, ALL_EXTENSIONS, exclude_exts, exclude_files, file_rel_path=rel_file_path):
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


def visualize_root_dir_tree(source_dir, output_file, print_to_console=True, truncate_output=False,
                            show_processing_status=False):
    """
    Generate a complete tree visualization of the directory structure starting from the
    current working directory, with status indicators showing which files/directories
    would be processed or excluded.
    """
    root_dir = os.getcwd()
    source_dir = os.path.abspath(source_dir)
    base_name = os.path.basename(root_dir)

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
        "out_of_scope_dirs": 0,
        "out_of_scope_files": 0,
        "processed_size": 0
    }

    start_time = datetime.datetime.now()

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    exclude_dirs = DEFAULT_EXCLUDE_DIRS if show_processing_status else []
    exclude_exts = ALL_EXCLUDE_EXTENSIONS if show_processing_status else []
    exclude_files = ALL_EXCLUDE_FILENAMES if show_processing_status else []
    output_abs_path = os.path.abspath(output_file)
    output_abs_dir = os.path.dirname(output_abs_path)

    # Check if path is in source directory
    def is_in_source_dir(path):
        """Check if a path is within the source directory."""
        abs_path = os.path.abspath(path)
        abs_source = os.path.abspath(source_dir)

        # Handle case sensitivity in Windows
        if os.name == 'nt':
            abs_path = abs_path.lower()
            abs_source = abs_source.lower()

        return abs_path.startswith(abs_source + os.sep) or abs_path == abs_source

    # Determine file status - fixed to handle regex patterns
    def get_file_status(file_path):
        """Determine if a file would be processed based on the filtering rules."""
        if not is_in_source_dir(file_path):
            return "out_of_scope"

        # Calculate relative path to source
        try:
            rel_path = os.path.relpath(file_path, source_dir)
            file_name = os.path.basename(file_path)

            # Check if file is in an excluded directory
            dir_path = os.path.dirname(rel_path)
            dir_parts = dir_path.replace('\\', '/').split('/')
            if any(exclude_dir in dir_parts for exclude_dir in exclude_dirs):
                return "excluded"

            for ext in exclude_exts:
                # Check if this is a regex pattern (starts with r"\" or contains special regex chars)
                if ext.startswith(r"\.") or any(c in ext for c in ".*+?()[]{}|^$"):
                    if re.search(ext + "$", file_name.lower()):
                        return "excluded"
                elif file_name.lower().endswith(ext.lower()):
                    return "excluded"
            if any(file_name.lower() == excl.lower() for excl in exclude_files):
                return "excluded"
            if any(file_name.lower().endswith(ext.lower()) for ext in ALL_EXTENSIONS):
                return "processed"
            return "excluded"  # Not a supported file type
        except ValueError:  # Different drives on Windows
            return "out_of_scope"

    # Determine directory status
    def get_dir_status(dir_path):
        """Check if a directory would be excluded."""
        if not is_in_source_dir(dir_path):
            return "out_of_scope"

        dir_name = os.path.basename(dir_path)
        if dir_name in exclude_dirs:
            return "excluded"
        return "processed"

    # Recursively build the directory tree
    def build_directory_tree(path, depth=0):
        """Recursively build a directory tree from the given path."""
        # Skip if it's the output directory or file
        abs_path = os.path.abspath(path)
        if abs_path == output_abs_path or (abs_path.startswith(output_abs_dir) and abs_path != root_dir):
            return None

        # Get item name and check if it's a directory
        name = os.path.basename(path)
        is_dir = os.path.isdir(path)

        if is_dir:
            # Directory node
            status = get_dir_status(path)
            dir_node = {
                "name": name,
                "type": "dir",
                "children": {},
                "path": path,
                "status": status,
                "depth": depth
            }

            stats["total_dirs"] += 1
            stats["max_depth"] = max(stats["max_depth"], depth)

            if status == "processed":
                stats["processed_dirs"] += 1
            elif status == "excluded":
                stats["excluded_dirs"] += 1
            elif status == "out_of_scope":
                stats["out_of_scope_dirs"] += 1

            # Skip processing contents of special directories
            if name in ROOT_TREE_UI_EXCLUDE_DIRS and path != root_dir:
                dir_node["_special"] = True
                dir_node["_special_type"] = "exclude_dir"
                return dir_node

            # Skip "codeflux" subdirectories that aren't the root (output directory)
            if name == "codeflux" and path != root_dir:
                dir_node["_special"] = True
                dir_node["_special_type"] = "codeflux"
                return dir_node

            # Process children
            try:
                items = sorted(os.listdir(path))
                for item in items:
                    item_path = os.path.join(path, item)

                    # Skip self-referential paths
                    if os.path.samefile(item_path, path):
                        continue

                    # Recursively process this item
                    child_node = build_directory_tree(item_path, depth + 1)

                    # Add to children if valid
                    if child_node:
                        dir_node["children"][item] = child_node
            except (PermissionError, OSError) as e:
                # Can't read directory contents
                dir_node["_error"] = str(e)

            return dir_node
        else:
            # File node
            try:
                file_size = os.path.getsize(path)
                status = get_file_status(path)

                # Create file node
                file_node = {
                    "name": name,
                    "type": "file",
                    "size": file_size,
                    "size_str": format_file_size(file_size),
                    "path": path,
                    "status": status,
                    "depth": depth
                }

                stats["total_files"] += 1
                stats["total_size"] += file_size

                if status == "processed":
                    stats["processed_files"] += 1
                    stats["processed_size"] += file_size
                elif status == "excluded":
                    stats["excluded_files"] += 1
                elif status == "out_of_scope":
                    stats["out_of_scope_files"] += 1

                return file_node
            except (PermissionError, OSError, FileNotFoundError) as e:
                # Can't access file
                return {
                    "name": name,
                    "type": "file",
                    "size": 0,
                    "size_str": "N/A (error)",
                    "path": path,
                    "status": "error",
                    "depth": depth,
                    "_error": str(e)
                }

    # Build the complete directory tree
    tree = build_directory_tree(root_dir)

    # Update directory statuses based on children
    def update_dir_statuses(node):
        """Update directory status based on its children."""
        if node["type"] != "dir" or "_special" in node:
            return node["status"]

        child_statuses = []
        for child in node["children"].values():
            if child["type"] == "dir":
                child_status = update_dir_statuses(child)
            else:
                child_status = child["status"]
            child_statuses.append(child_status)

        if not child_statuses:
            return node["status"]

        # If all children have the same status, use that
        unique_statuses = set(child_statuses)
        if len(unique_statuses) == 1:
            status = list(unique_statuses)[0]
            if status != node["status"]:
                # Update statistics
                if node["status"] == "processed":
                    stats["processed_dirs"] -= 1
                elif node["status"] == "excluded":
                    stats["excluded_dirs"] -= 1
                elif node["status"] == "out_of_scope":
                    stats["out_of_scope_dirs"] -= 1

                if status == "processed":
                    stats["processed_dirs"] += 1
                elif status == "excluded":
                    stats["excluded_dirs"] += 1
                elif status == "out_of_scope":
                    stats["out_of_scope_dirs"] += 1

                node["status"] = status
        else:
            # Mixed statuses
            old_status = node["status"]
            if old_status != "mixed":
                # Update statistics
                if old_status == "processed":
                    stats["processed_dirs"] -= 1
                elif old_status == "excluded":
                    stats["excluded_dirs"] -= 1
                elif old_status == "out_of_scope":
                    stats["out_of_scope_dirs"] -= 1

                stats["mixed_dirs"] += 1
                node["status"] = "mixed"

        return node["status"]

    update_dir_statuses(tree)

    def generate_tree_lines(node, lines, prefix="", is_last=True):
        """Generate lines for the tree visualization."""
        connector = "└── " if is_last else "├── "

        # Add this node
        if node["type"] == "dir":
            # Directory
            if show_processing_status:
                symbol = ROOT_TREE_UI_STATUS_SYMBOLS.get(node["status"], "?")
                lines.append(f"{prefix}{connector}{node['name']}/ {symbol}")
            else:
                lines.append(f"{prefix}{connector}{node['name']}/")

            # Special handling for special directories
            if "_special" in node:
                new_prefix = prefix + ("    " if is_last else "│   ")
                child_connector = "└── "  # Always last item in special dir

                if node["_special_type"] == "exclude_dir":
                    lines.append(
                        f"{new_prefix}{child_connector}[Content inside {node['name']} directory - full tree saved to file]")
                elif node["_special_type"] == "codeflux":
                    lines.append(
                        f"{new_prefix}{child_connector}[codeflux package files and directories - see full tree in file]")
                return

            # Process children
            new_prefix = prefix + ("    " if is_last else "│   ")

            # First sort children by type (dirs first) and name
            dirs = []
            files = []
            for name, child in node["children"].items():
                if child["type"] == "dir":
                    dirs.append((name, child))
                else:
                    files.append((name, child))

            dirs.sort()
            files.sort()
            children = dirs + files

            # Add each child
            for i, (name, child) in enumerate(children):
                is_last_child = (i == len(children) - 1)
                generate_tree_lines(child, lines, new_prefix, is_last_child)
        else:
            # File
            if show_processing_status:
                symbol = ROOT_TREE_UI_STATUS_SYMBOLS.get(node["status"], "?")
                lines.append(f"{prefix}{connector}{node['name']} ({node['size_str']}) {symbol}")
            else:
                lines.append(f"{prefix}{connector}{node['name']} ({node['size_str']})")

    # Generate tree lines for file output
    tree_lines = []
    tree_lines.append(f"# Root Directory Tree Visualization")
    tree_lines.append(f"# Project Root Directory: {root_dir}")
    tree_lines.append(f"# Source Directory: {source_dir}")
    tree_lines.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    if show_processing_status:
        tree_lines.append(f"# Processing Status Symbols: {ROOT_TREE_UI_STATUS_SYMBOLS['processed']} (processed), "
                          f"{ROOT_TREE_UI_STATUS_SYMBOLS['excluded']} (excluded), {ROOT_TREE_UI_STATUS_SYMBOLS['mixed']} (mixed), "
                          f"{ROOT_TREE_UI_STATUS_SYMBOLS['out_of_scope']} (out of scope)")
    tree_lines.append("")
    # Add root with status
    if show_processing_status:
        root_symbol = ROOT_TREE_UI_STATUS_SYMBOLS.get(tree["status"], "?")
        tree_lines.append(f"{base_name}/ {root_symbol}")
    else:
        tree_lines.append(f"{base_name}/")

    # Add children
    dirs = []
    files = []
    for name, child in tree["children"].items():
        if child["type"] == "dir":
            dirs.append((name, child))
        else:
            files.append((name, child))
    dirs.sort()
    files.sort()
    children = dirs + files

    # Generate lines for all children
    for i, (name, child) in enumerate(children):
        is_last_child = (i == len(children) - 1)
        generate_tree_lines(child, tree_lines, "", is_last_child)

    tree_lines.append("")
    tree_lines.append("# Summary")
    tree_lines.append(f"Total directories: {stats['total_dirs']}")
    if show_processing_status:
        tree_lines.append(f"  - Processed directories: {stats['processed_dirs']}")
        tree_lines.append(f"  - Excluded directories: {stats['excluded_dirs']}")
        tree_lines.append(f"  - Mixed directories: {stats['mixed_dirs']}")
        tree_lines.append(f"  - Out of scope directories: {stats['out_of_scope_dirs']}")
    tree_lines.append(f"Total files: {stats['total_files']}")
    if show_processing_status:
        tree_lines.append(f"  - Processed files: {stats['processed_files']}")
        tree_lines.append(f"  - Excluded files: {stats['excluded_files']}")
        tree_lines.append(f"  - Out of scope files: {stats['out_of_scope_files']}")
    total_size_str = format_file_size(stats["total_size"])
    tree_lines.append(f"Total size: {total_size_str}")
    if show_processing_status:
        processed_size_str = format_file_size(stats["processed_size"])
        tree_lines.append(f"  - Processed size: {processed_size_str}")
    tree_lines.append(f"Maximum directory depth: {stats['max_depth']}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))

    # Calculate duration
    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    if print_to_console:
        print("\n[ROOT DIRECTORY TREE]")

        console_lines = []
        if show_processing_status:
            root_symbol = ROOT_TREE_UI_STATUS_SYMBOLS.get(tree["status"], "?")
            console_lines.append(f"{base_name}/ {root_symbol}")
        else:
            console_lines.append(f"{base_name}/")

        # Add children to console lines
        for i, (name, child) in enumerate(children):
            is_last_child = (i == len(children) - 1)
            generate_tree_lines(child, console_lines, "", is_last_child)

        # Display console lines with possible truncation
        if truncate_output and len(console_lines) > 50:
            for line in console_lines[:50]:
                print(line)
            print(f"... (truncated, full tree saved to file) ...")
        else:
            for line in console_lines:
                print(line)

        print("\n[OPERATION SUMMARY]")
        stats_data = [
            ["Time taken", f"{duration:.6f} seconds"],
            ["Total directories", stats["total_dirs"]]
        ]
        if show_processing_status:
            stats_data.append(["Processed directories", stats["processed_dirs"]])
            stats_data.append(["Excluded directories", stats["excluded_dirs"]])
            stats_data.append(["Mixed directories", stats["mixed_dirs"]])
            stats_data.append(["Out of scope directories", stats["out_of_scope_dirs"]])
        stats_data.extend([
            ["Maximum directory depth", stats["max_depth"]],
            ["Total files", stats["total_files"]]
        ])
        if show_processing_status:
            stats_data.append(["Processed files", stats["processed_files"]])
            stats_data.append(["Excluded files", stats["excluded_files"]])
            stats_data.append(["Out of scope files", stats["out_of_scope_files"]])
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
