import os
import datetime
import re
import sys

from constants import ALL_EXTENSIONS, ROOT_TREE_UI_EXCLUDE_DIRS, ROOT_TREE_UI_STATUS_SYMBOLS


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

    # Define a helper function to check if a directory should be excluded
    def is_dir_excluded(rel_dir_path):
        """Check if a directory should be excluded based on its path."""
        if not rel_dir_path or rel_dir_path == '.':
            return False
            
        # Check for exact directory name match
        dir_parts = rel_dir_path.split(os.sep)
        if any(part in exclude_dirs for part in dir_parts):
            return True
            
        # Check for path-based exclusions (for patterns like "temp/rz/data")
        for exclude_dir in exclude_dirs:
            if os.sep in exclude_dir or '/' in exclude_dir:  # This is a path-based exclusion
                # Normalize paths for comparison
                norm_exclude = exclude_dir.replace('\\', os.sep).replace('/', os.sep)
                norm_rel_path = rel_dir_path.replace('\\', os.sep)
                
                # Check if the exclusion path is a substring of the full path
                if norm_rel_path == norm_exclude or norm_rel_path.startswith(norm_exclude + os.sep):
                    return True
        
        return False
    
    # Define a helper function to check if a file should be excluded
    def is_file_excluded(file_path, rel_file_path):
        # Check file extension exclusion
        for ext in exclude_exts:
            # Check if this is a regex pattern (starts with r"\." or contains special regex chars)
            if ext.startswith(r"\.") or any(c in ext for c in ".*+?()[]{}|^$"):
                try:
                    if re.search(ext + "$", file_path.lower()):
                        return True
                except re.error:
                    # If regex is invalid, fall back to simple suffix check
                    if file_path.lower().endswith(ext.lower().replace(r"\.", ".")):
                        return True
            # normal suffix check
            elif file_path.lower().endswith(ext.lower()):
                return True
            
        # Check file name exclusion
        file_name = os.path.basename(file_path)
        norm_rel_path = rel_file_path.replace('\\', '/')
        
        for exclude_pattern in exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if (norm_rel_path.lower() == norm_exclude.lower() or
                    norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                    file_name.lower() == norm_exclude.lower()):
                return True
                
        return False

    # Build a complete directory tree structure
    tree = {"name": base_name, "type": "dir", "children": {}, "path": root_dir}
    
    for root, dirs, files in os.walk(root_dir):
        # Calculate relative path for current directory
        rel_path = os.path.relpath(root, root_dir)
        
        # Skip this directory and its subdirectories if it should be excluded
        if is_dir_excluded(rel_path):
            # Clear dirs to skip subdirectories
            dirs[:] = []
            continue
            
        # Filter dirs for next iteration (only affects subdirectories to visit)
        # This ensures we don't descend into excluded subdirectories
        dirs[:] = sorted([d for d in dirs if not is_dir_excluded(os.path.join(rel_path, d))])
        
        depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))
        # Update max depth
        stats["max_depth"] = max(stats["max_depth"], depth)

        # Get the current node in our tree
        if depth > 0:
            path_parts = rel_path.split(os.sep)
            current = tree
            skip_dir = False
            
            for i, part in enumerate(path_parts):
                if skip_dir:
                    break
                    
                if part not in current["children"]:
                    current_path = os.path.join(*path_parts[:i+1])
                    if is_dir_excluded(current_path):
                        skip_dir = True
                        break
                        
                    current["children"][part] = {
                        "name": part,
                        "type": "dir",
                        "children": {},
                        "path": os.path.join(current["path"], part)
                    }
                    stats["total_dirs"] += 1

                current = current["children"][part]
            
            # If we need to skip this directory, continue to next iteration
            if skip_dir:
                continue
                
            # Add files to current directory
            for file in sorted(files):
                file_path = os.path.join(root, file)
                rel_file_path = os.path.relpath(file_path, root_dir)
                
                # Skip excluded files
                if is_file_excluded(file_path, rel_file_path):
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
                
                # Skip excluded files
                if is_file_excluded(file_path, rel_file_path):
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


def visualize_root_dir_tree(source_dir, output_file, print_to_console=True, truncate_output=False,
                            show_processing_status=False, user_exclude_dirs=None, user_exclude_exts=None,
                            user_exclude_files=None):
    """
    Generate a complete tree visualization of the root directory structure with
    status indicators showing which files/directories would be processed or excluded.
    """
    # Use provided exclude lists OR default ones if not provided
    exclude_dirs = user_exclude_dirs if user_exclude_dirs is not None else []
    exclude_exts = user_exclude_exts if user_exclude_exts is not None else []
    exclude_files = user_exclude_files if user_exclude_files is not None else []

    # Find the actual package installation directory
    source_dir_abs = os.path.abspath(source_dir)

    # Try to find the codeflux installation directory
    try:
        # Try to get the directory from the running executable
        if hasattr(sys, 'frozen') and hasattr(sys, '_MEIPASS'):  # PyInstaller
            root_dir = os.path.dirname(sys.executable)
        elif hasattr(sys, 'executable'):  # Regular Python
            # Try to find the main module
            import __main__
            if hasattr(__main__, '__file__'):
                root_dir = os.path.dirname(os.path.abspath(__main__.__file__))
            else:
                # If we can't determine from the main module, use current directory
                root_dir = os.getcwd()
        else:
            root_dir = os.getcwd()

        # Look for installation indicators by walking up from the directory
        orig_root = root_dir
        while root_dir != os.path.dirname(root_dir):  # Stop at filesystem root
            # Check if this looks like a project root
            if (os.path.exists(os.path.join(root_dir, "setup.py")) or
                    os.path.exists(os.path.join(root_dir, "pyproject.toml")) or
                    os.path.exists(os.path.join(root_dir, ".git")) or
                    os.path.exists(os.path.join(root_dir, "requirements.txt")) or
                    os.path.basename(root_dir) == "codeflux"):
                break  # Found a likely project root

            # Move up one directory
            root_dir = os.path.dirname(root_dir)

        # If we ended up at filesystem root without finding indicators,
        # fall back to the original directory
        if root_dir == os.path.dirname(root_dir):
            root_dir = orig_root

    except Exception as e:
        # Fallback to source directory if anything goes wrong
        root_dir = source_dir_abs

    base_name = os.path.basename(root_dir)

    # Define status symbols
    status_symbols = ROOT_TREE_UI_STATUS_SYMBOLS

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
        "processed_size": 0,
        "out_of_scope_files": 0,
        "out_of_scope_dirs": 0
    }

    start_time = datetime.datetime.now()

    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Determine if path is within source directory
    def is_in_source_dir(path):
        try:
            rel_path = os.path.relpath(path, source_dir_abs)
            return not rel_path.startswith('..')
        except ValueError:
            # Different drives on Windows
            return False

    def is_file_processed(file_path, rel_path):
        """Determine if a file would be processed based on the filtering rules."""
        # Check directory exclusion
        dir_path = os.path.dirname(rel_path)
        dir_parts = dir_path.replace('\\', '/').split('/')

        # Check if any part of the directory path is in exclude_dirs
        if any(part in exclude_dirs for part in dir_parts):
            return False

        # Check path-based directory exclusions
        for exclude_dir in exclude_dirs:
            if os.sep in exclude_dir or '/' in exclude_dir:  # This is a path-based exclusion
                # Normalize paths for comparison
                norm_exclude = exclude_dir.replace('\\', os.sep).replace('/', os.sep)
                norm_rel_path = rel_path.replace('\\', os.sep)

                # Check if the exclusion path matches or is a parent of this file's path
                if (norm_rel_path.startswith(norm_exclude + os.sep) or
                        norm_rel_path == norm_exclude):
                    return False

        # Check file extension exclusion
        for ext in exclude_exts:
            # Check if this is a regex pattern
            if ext.startswith(r"\.") or any(c in ext for c in ".*+?()[]{}|^$"):
                try:
                    if re.search(ext + "$", file_path.lower()):
                        return False
                except re.error:
                    # Fall back to simple check if regex is invalid
                    if file_path.lower().endswith(ext.lower().replace(r"\.", ".")):
                        return False
            elif file_path.lower().endswith(ext.lower()):
                return False

        # Check file name exclusion
        file_name = os.path.basename(file_path)
        norm_rel_path = rel_path.replace('\\', '/')

        for exclude_pattern in exclude_files:
            norm_exclude = exclude_pattern.replace('\\', '/')
            if (norm_rel_path.lower() == norm_exclude.lower() or
                    norm_rel_path.lower().endswith('/' + norm_exclude.lower()) or
                    file_name.lower() == norm_exclude.lower()):
                return False

        # File is processed if it has one of the target extensions
        return any(file_path.lower().endswith(ext.lower()) for ext in ALL_EXTENSIONS)

    def is_dir_excluded(dir_path, rel_path):
        """Check if a directory would be excluded."""
        dir_name = os.path.basename(dir_path)

        # Check if the directory name itself is in exclude_dirs
        if dir_name in exclude_dirs:
            return True

        # Check if any parent directory is in exclude_dirs
        dir_parts = rel_path.split(os.sep)
        if any(part in exclude_dirs for part in dir_parts):
            return True

        # Check path-based exclusions
        for exclude_dir in exclude_dirs:
            if os.sep in exclude_dir or '/' in exclude_dir:  # This is a path-based exclusion
                # Normalize paths for comparison
                norm_exclude = exclude_dir.replace('\\', os.sep).replace('/', os.sep)
                norm_rel_path = rel_path.replace('\\', os.sep)

                # Check if the exclusion path matches this directory
                if norm_rel_path == norm_exclude or norm_rel_path.startswith(norm_exclude + os.sep):
                    return True

        return False

    # Check if source_dir is a subdirectory of root_dir
    source_is_sub_of_root = False
    try:
        rel_source_to_root = os.path.relpath(source_dir_abs, root_dir)
        source_is_sub_of_root = not rel_source_to_root.startswith('..')
    except ValueError:
        # Different drives on Windows
        source_is_sub_of_root = False

    tree = {"name": base_name, "type": "dir", "children": {}, "path": root_dir, "status": "unknown", "depth": 0}

    for root, dirs, files in os.walk(root_dir):
        rel_path = os.path.relpath(root, root_dir)
        depth = 0 if rel_path == '.' else len(rel_path.split(os.sep))
        stats["max_depth"] = max(stats["max_depth"], depth)

        # Check if this directory is within source_dir
        in_source = is_in_source_dir(root)

        if rel_path == '.':
            current = tree
            # If source_dir is not a subdirectory of root_dir, mark tree root as mixed
            if not source_is_sub_of_root:
                tree["status"] = "out_of_scope"
        else:
            path_parts = rel_path.split(os.sep)
            current = tree
            for i, part in enumerate(path_parts):
                if part not in current["children"]:
                    dir_path = os.path.join(current["path"], part)
                    rel_dir_path = os.path.relpath(dir_path, root_dir)

                    # Check if this directory is within source_dir
                    dir_in_source = is_in_source_dir(dir_path)

                    if dir_in_source:
                        # Only apply exclusion rules for directories within source_dir
                        is_excluded = is_dir_excluded(dir_path, rel_dir_path)
                        status = "excluded" if is_excluded else "processed"
                    else:
                        # Directories outside source_dir are marked as out_of_scope
                        status = "out_of_scope"

                    # Create node
                    dir_node = {
                        "name": part,
                        "type": "dir",
                        "children": {},
                        "path": dir_path,
                        "status": status,  # Initial status, may be updated later
                        "depth": i + 1,  # Store the depth for display decisions (root is 0, first level is 1)
                        "special": part in ROOT_TREE_UI_EXCLUDE_DIRS
                    }

                    # Update stats
                    stats["total_dirs"] += 1
                    if status == "processed":
                        stats["processed_dirs"] += 1
                    elif status == "excluded":
                        stats["excluded_dirs"] += 1
                    elif status == "out_of_scope":
                        stats["out_of_scope_dirs"] += 1

                    current["children"][part] = dir_node
                current = current["children"][part]

        # Process files
        for file in sorted(files):
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, root_dir)

            # Check if this file is within source_dir
            file_in_source = is_in_source_dir(file_path)
            try:
                file_size = os.path.getsize(file_path)
                size_str = format_file_size(file_size)
                if file_in_source:
                    # Only apply processing rules for files within source_dir
                    is_processed = is_file_processed(file_path, rel_file_path)
                    status = "processed" if is_processed else "excluded"
                else:
                    # Files outside source_dir are marked as out_of_scope
                    status = "out_of_scope"

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
                elif status == "excluded":
                    stats["excluded_files"] += 1
                elif status == "out_of_scope":
                    stats["out_of_scope_files"] += 1

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

        # Check if all children have the same status
        all_processed = all(status == "processed" for status in child_statuses)
        all_excluded = all(status == "excluded" for status in child_statuses)
        all_out_of_scope = all(status == "out_of_scope" for status in child_statuses)

        old_status = node["status"]

        if all_processed:
            node["status"] = "processed"
        elif all_excluded:
            node["status"] = "excluded"
        elif all_out_of_scope:
            node["status"] = "out_of_scope"
        else:
            # Mixed statuses
            node["status"] = "mixed"

        # Update stats if status changed
        if old_status != node["status"]:
            if old_status == "processed":
                stats["processed_dirs"] -= 1
            elif old_status == "excluded":
                stats["excluded_dirs"] -= 1
            elif old_status == "out_of_scope":
                stats["out_of_scope_dirs"] -= 1
            elif old_status == "mixed":
                stats["mixed_dirs"] -= 1

            if node["status"] == "processed":
                stats["processed_dirs"] += 1
            elif node["status"] == "excluded":
                stats["excluded_dirs"] += 1
            elif node["status"] == "out_of_scope":
                stats["out_of_scope_dirs"] += 1
            elif node["status"] == "mixed":
                stats["mixed_dirs"] += 1

        return node["status"]

    # Update all directory statuses
    update_dir_statuses(tree)

    # Generate tree visualization for file output
    tree_lines = []
    tree_lines.append(f"# Root Directory Tree Visualization")
    tree_lines.append(f"# Project Root: {root_dir}")
    tree_lines.append(f"# Source Directory: {source_dir_abs}")
    tree_lines.append(f"# Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if show_processing_status:
        tree_lines.append(f"# Processing Status Symbols: {status_symbols['processed']} (processed), "
                          f"{status_symbols['excluded']} (excluded), {status_symbols['mixed']} (mixed), "
                          f"{status_symbols['out_of_scope']} (out of scope)")

    tree_lines.append("")

    # Add root with status
    if show_processing_status:
        root_symbol = status_symbols.get(tree["status"], status_symbols['unknown'])
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
                    symbol = status_symbols.get(child["status"], status_symbols['unknown'])
                    tree_lines.append(f"{prefix}{connector}{name}/ {symbol}")
                else:
                    tree_lines.append(f"{prefix}{connector}{name}/")

                # Handle special directories with proper indentation
                extended_prefix = prefix + ("    " if is_last_child else "│   ")

                if child.get("special", False):
                    special_connector = "├── "  # Use the same connector style
                    tree_lines.append(
                        f"{extended_prefix}{special_connector}[Content inside {name} directory - full tree saved to file]")
                else:
                    # Process children normally
                    build_tree_lines(child, extended_prefix, is_last_child)
            else:
                # File node
                if show_processing_status:
                    symbol = status_symbols.get(child["status"], status_symbols['unknown'])
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
        tree_lines.append(f"  - Out of scope directories: {stats['out_of_scope_dirs']}")
        tree_lines.append(f"  - Mixed directories: {stats['mixed_dirs']}")
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

    end_time = datetime.datetime.now()
    duration = (end_time - start_time).total_seconds()
    stats['time_taken'] = duration

    if print_to_console:
        print("\n[DIRECTORY TREE]")
        if show_processing_status:
            status_description = []
            for status_key in ['processed', 'excluded', 'mixed', 'out_of_scope']:
                symbol = status_symbols.get(status_key, '?')
                status_description.append(f"{symbol} ({status_key})")

            print(f"Legend: {', '.join(status_description)}")

        console_lines = []
        if show_processing_status:
            root_symbol = status_symbols.get(tree["status"], status_symbols['unknown'])
            console_lines.append(f"{base_name}/ {root_symbol}")
        else:
            console_lines.append(f"{base_name}/")

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

                if child["type"] == "dir":
                    if show_processing_status:
                        symbol = status_symbols.get(child["status"], status_symbols['unknown'])
                        console_lines.append(f"{prefix}{connector}{name}/ {symbol}")
                    else:
                        console_lines.append(f"{prefix}{connector}{name}/")

                    # Extended prefix for children
                    extended_prefix = prefix + ("    " if is_last_child else "│   ")

                    # Handle special directories with proper indentation
                    if child.get("special", False) or name in ROOT_TREE_UI_EXCLUDE_DIRS:
                        special_connector = "├── "  # Use a connector for consistent style
                        console_lines.append(
                            f"{extended_prefix}{special_connector}[Content inside {name} directory - full tree saved to file]")
                    else:
                        # Process children normally
                        new_path = path + [name]
                        build_console_lines(child, extended_prefix, is_last_child, new_path)
                else:
                    # File node
                    if show_processing_status:
                        symbol = status_symbols.get(child["status"], status_symbols['unknown'])
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

        print("\n[OPERATION SUMMARY]")
        stats_data = [
            ["Time taken", f"{duration:.6f} seconds"],
            ["Total directories", stats["total_dirs"]]
        ]
        if show_processing_status:
            stats_data.append(["Processed directories", stats["processed_dirs"]])
            stats_data.append(["Excluded directories", stats["excluded_dirs"]])
            stats_data.append(["Out of scope directories", stats["out_of_scope_dirs"]])
            stats_data.append(["Mixed directories", stats["mixed_dirs"]])
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
