import os
import datetime


def visualize_dir_tree(root_dir, output_file, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                       print_to_console=True, truncate_output=False):
    """Generate a text-based tree visualization of the directory structure."""
    exclude_dirs = exclude_dirs or []
    exclude_exts = exclude_exts or []
    exclude_files = exclude_files or []

    # Convert root_dir to absolute path
    root_dir = os.path.abspath(root_dir)
    base_name = os.path.basename(root_dir)

    stats = {
        "total_files": 0,
        "total_dirs": 0,
        "total_size": 0,
        "max_depth": 0
    }

    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Build a complete directory tree structure
    tree = {"name": base_name, "type": "dir", "children": {}, "path": root_dir}

    for root, dirs, files in os.walk(root_dir):
        # Skip excluded directories
        dirs[:] = sorted([d for d in dirs if d not in exclude_dirs])

        # Calculate relative path from root
        rel_path = os.path.relpath(root, root_dir)
        depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))

        # Update max depth
        stats["max_depth"] = max(stats["max_depth"], depth)

        # Skip processing files in the root directory if we're at root level
        if depth > 0:
            # Find/create the current node in the tree
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

                # Get file size
                try:
                    file_size = os.path.getsize(file_path)
                    stats["total_size"] += file_size

                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    # Add file to current node
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

                # Get file size
                try:
                    file_size = os.path.getsize(file_path)
                    stats["total_size"] += file_size

                    # Format file size
                    if file_size < 1024:
                        size_str = f"{file_size} B"
                    elif file_size < 1024 * 1024:
                        size_str = f"{file_size / 1024:.1f} KB"
                    else:
                        size_str = f"{file_size / (1024 * 1024):.1f} MB"

                    # Add file to the root node
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

    # Generate the tree visualization as text
    tree_lines = []
    tree_lines.append(f"# Directory Tree Visualization")
    tree_lines.append(f"# Root: {root_dir}")
    tree_lines.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    tree_lines.append("")
    tree_lines.append(f"{base_name}/")

    # Recursively build tree lines
    def build_tree_lines(node, prefix="", is_last=True, is_root=False):
        # Sort children: directories first, then files
        sorted_children = []
        dirs = []
        files = []

        for name, child in node["children"].items():
            if child["type"] == "dir":
                dirs.append((name, child))
            else:
                files.append((name, child))

        # Sort directories and files by name
        dirs.sort()
        files.sort()

        # Combine sorted directories and files
        sorted_children = dirs + files

        # Process each child
        for i, (name, child) in enumerate(sorted_children):
            # Determine if this is the last item at this level
            is_last_child = (i == len(sorted_children) - 1)

            # Choose the connector based on whether this is the last item
            connector = "└── " if is_last_child else "├── "

            # Create the line for this item
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

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("\n".join(tree_lines))
    if print_to_console:
        print("\nDirectory Tree:")

        if truncate_output:
            max_lines = min(100, len(tree_lines))
            truncated = len(tree_lines) > max_lines

            for line in tree_lines[:max_lines]:
                print(line)
            if truncated:
                print(f"... (truncated, {len(tree_lines) - max_lines} more lines) ...")
                print("Full tree saved to file.")

            # Always print summary section
            summary_start = tree_lines.index("# Summary")
            if summary_start > max_lines:
                print("\n".join(tree_lines[summary_start:]))
        else:
            # Print the entire tree without truncation
            for line in tree_lines:
                print(line)

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
