import os
import argparse
import sys
import time
import shutil

from constants import DEFAULT_EXCLUDE_DIRS, ALL_EXCLUDE_EXTENSIONS, ALL_EXCLUDE_FILENAMES, DEFAULT_FLATTEN_OUTPUT_PATH, \
    DEFAULT_DEFLATTEN_OUTPUT_PATH, DEFAULT_BUNDLE_OUTPUT_PATH, DEFAULT_MINIFY_OUTPUT_PATH, \
    DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH
from handlers import HANDLERS
from utils import get_relative_path, print_stats, merge_with_defaults, merge_stats, should_process_file, minify_code, \
    create_timestamped_dir


def minify(source_dir, dest_dir, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None,
           include_dirs=None, include_exts=None, include_files=None, clear_dest_dir=False, silent=False,
           ignore_defaults=False):
    """Create a minified copy of a directory structure while preserving the original structure."""
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml", "shell"]

    exclude_dirs = merge_with_defaults(exclude_dirs, DEFAULT_EXCLUDE_DIRS, ignore_defaults)
    exclude_exts = merge_with_defaults(exclude_exts, ALL_EXCLUDE_EXTENSIONS, ignore_defaults)
    exclude_files = merge_with_defaults(exclude_files, ALL_EXCLUDE_FILENAMES, ignore_defaults)

    source_dir = os.path.abspath(source_dir)
    dest_dir = os.path.abspath(dest_dir)

    # Stats tracking
    stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_copied": 0,
        "files_minified": 0,
        "bytes_original": 0,
        "bytes_minified": 0,
        "skipped_files": 0,
        "max_nesting_level": 0
    }

    if clear_dest_dir and os.path.exists(dest_dir):
        shutil.rmtree(dest_dir)

    start_time = time.time()

    if not silent:
        print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
        print(f"Destination: {get_relative_path(dest_dir, os.getcwd())}\n")
        print(f"Processing files: {', '.join([ft for ft in file_types if ft in HANDLERS])}")
        print(f"Minification: Using python-minifier for Python files")

        if include_exts:
            print(f"Including only extensions: {', '.join(include_exts)}")
        if include_dirs:
            print(f"Including only directories: {', '.join(include_dirs)}")
        if include_files:
            print(f"Including only files: {', '.join(include_files)}")

    # Gather all extensions from selected handlers
    included_extensions = []
    for file_type in file_types:
        if file_type in HANDLERS:
            included_extensions.extend(HANDLERS[file_type].extensions)

    # Override with user-specified extensions if provided
    if include_exts:
        included_extensions = include_exts

    for root, dirs, files in os.walk(source_dir):
        stats["dirs_traversed"] += 1

        # Calculate nesting level for stats
        current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
        stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

        # Process directory inclusion/exclusion
        if include_dirs:
            rel_dir = os.path.relpath(root, source_dir)
            rel_dir_parts = rel_dir.split(os.sep)
            if not any(part in include_dirs for part in rel_dir_parts) and rel_dir != '.':
                dirs[:] = []  # Skip this branch
                continue

        # Exclude directories
        dirs[:] = [
            d for d in dirs
            if d not in exclude_dirs and os.path.abspath(os.path.join(root, d)) != dest_dir
        ]

        # Create corresponding directory in destination
        rel_path = os.path.relpath(root, source_dir)
        target_dir = os.path.join(dest_dir, rel_path)
        os.makedirs(target_dir, exist_ok=True)

        for file in files:
            stats["total_files_processed"] += 1

            # Use centralized file filtering logic
            should_include = should_process_file(file, included_extensions, exclude_exts, exclude_files, include_exts,
                                                 include_files)

            if should_include:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)

                # Get file extension
                _, file_ext = os.path.splitext(file)

                try:
                    # For text files that can be minified
                    with open(source_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        original_size = len(content)
                        stats["bytes_original"] += original_size

                    # Apply minification based on file type
                    if file_ext.lower() == '.py':
                        minified_content = minify_code(content, file_ext)
                        minified_size = len(minified_content)

                        # Write minified content
                        with open(target_file, 'w', encoding='utf-8') as f:
                            f.write(minified_content)

                        stats["files_minified"] += 1
                        stats["bytes_minified"] += minified_size
                        stats["files_copied"] += 1

                        if not silent:
                            rel_source = get_relative_path(source_file, os.getcwd())
                            rel_dest = get_relative_path(target_file, os.getcwd())
                            reduction = (1 - minified_size / max(original_size, 1)) * 100
                            print(f"{rel_source} → {rel_dest} (Size reduction: {reduction:.2f}%)")
                    else:
                        # Just copy non-Python files
                        shutil.copy2(source_file, target_file)
                        stats["files_copied"] += 1
                        stats["bytes_minified"] += original_size  # No reduction

                        if not silent:
                            rel_source = get_relative_path(source_file, os.getcwd())
                            rel_dest = get_relative_path(target_file, os.getcwd())
                            print(f"{rel_source} → {rel_dest}")

                except UnicodeDecodeError:
                    # Handle binary files
                    shutil.copy2(source_file, target_file)
                    file_size = os.path.getsize(source_file)
                    stats["files_copied"] += 1
                    stats["bytes_original"] += file_size
                    stats["bytes_minified"] += file_size  # No reduction for binary files

                    if not silent:
                        rel_source = get_relative_path(source_file, os.getcwd())
                        rel_dest = get_relative_path(target_file, os.getcwd())
                        print(f"{rel_source} → {rel_dest} (binary file)")
                except Exception as e:
                    # Report error to user instead of falling back
                    error_msg = f"Error processing {file}: {str(e)}"
                    print(error_msg)
                    raise RuntimeError(error_msg)
            else:
                stats["skipped_files"] += 1

    end_time = time.time()
    duration = end_time - start_time

    if not silent:
        print("\n================ MINIFY DIRECTORY SUMMARY ================\n")
        print(f"Time taken: {duration:.6f} seconds")
        print(f"Directories traversed: {stats['dirs_traversed']}")
        print(f"Total files processed: {stats['total_files_processed']}")
        print(f"Files copied: {stats['files_copied']}")
        print(f"Files minified: {stats['files_minified']}")

        if stats["bytes_original"] > 0 and stats["bytes_minified"] > 0:
            orig_kb = stats["bytes_original"] / 1024
            mini_kb = stats["bytes_minified"] / 1024
            reduction = (1 - stats["bytes_minified"] / max(stats["bytes_original"], 1)) * 100

            print(f"Original size: {orig_kb:.2f} KB")
            print(f"Minified size: {mini_kb:.2f} KB")
            print(f"Overall reduction: {reduction:.2f}%")

        print(f"Files skipped: {stats['skipped_files']}")
        print(f"Processing rate: {stats['files_copied'] / max(duration, 0.1):.2f} files/second")

    return stats


def process_files_for_bundling(source_dir, file_types, exclude_dirs, exclude_exts, exclude_files,
                               include_dirs, include_exts, include_files, output_file, silent):
    """Gather and process files for bundling - extracted to eliminate code duplication."""
    source_dir = os.path.abspath(source_dir)
    output_file = os.path.abspath(output_file)
    output_filename = os.path.basename(output_file)
    if output_filename not in exclude_files and exclude_files is not None:
        exclude_files.append(output_filename)
    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_bundled": 0,
        "bytes_bundled": 0,
        "skipped_files": 0,
        "max_nesting_level": 0,
        "original_size": 0,
        "minified_size": 0
    }

    included_extensions = []
    for file_type in file_types:
        if file_type in HANDLERS:
            included_extensions.extend(HANDLERS[file_type].extensions)

    if include_exts:
        included_extensions = include_exts

    files_to_bundle = []
    for root, dirs, files in os.walk(source_dir):
        stats["dirs_traversed"] += 1

        # Calculate nesting level
        current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
        stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

        if include_dirs:
            # Only process specified directories
            rel_dir = os.path.relpath(root, source_dir)
            rel_dir_parts = rel_dir.split(os.sep)
            # Check if any part of the path is in include_dirs
            if not any(part in include_dirs for part in rel_dir_parts) and rel_dir != '.':
                dirs[:] = []  # Clear dirs to skip this branch
                continue

        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            stats["total_files_processed"] += 1
            file_path = os.path.join(root, file)
            if os.path.abspath(file_path) == output_file:
                stats["skipped_files"] += 1
                continue

            # Use centralized file filtering logic
            should_include = should_process_file(file, included_extensions, exclude_exts, exclude_files, include_exts, include_files)
            if should_include:
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                if path_parts:
                    formatted_path = "___".join(path_parts + [file])
                else:
                    formatted_path = file

                # Get file extension for language hint
                _, file_ext = os.path.splitext(file)
                if file_ext:
                    file_ext = file_ext[1:]  # Remove the dot

                files_to_bundle.append({
                    'file_path': file_path,
                    'formatted_path': formatted_path,
                    'rel_path': os.path.relpath(file_path, source_dir),
                    'extension': file_ext,
                    'full_extension': file_ext
                })
            else:
                stats["skipped_files"] += 1

    return files_to_bundle, stats, source_dir_parts


def bundle_files(source_dir, output_file, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                 include_dirs=None, include_exts=None, include_files=None, silent=False, ignore_defaults=False,
                 minify=False):
    """Bundle files into a single text file with path information."""
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml", "shell"]

    exclude_dirs = merge_with_defaults(exclude_dirs, DEFAULT_EXCLUDE_DIRS, ignore_defaults)
    exclude_exts = merge_with_defaults(exclude_exts, ALL_EXCLUDE_EXTENSIONS, ignore_defaults)
    exclude_files = merge_with_defaults(exclude_files, ALL_EXCLUDE_FILENAMES, ignore_defaults)
    if exclude_files is None:
        exclude_files = []

    start_time = time.time()

    if not silent:
        print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
        print(f"Output file: {get_relative_path(output_file, os.getcwd())}\n")
        if minify:
            print(f"Minification: Using python-minifier for Python files")

    # Gather and process files for bundling
    files_to_bundle, stats, _ = process_files_for_bundling(
        source_dir, file_types, exclude_dirs, exclude_exts, exclude_files,
        include_dirs, include_exts, include_files, output_file, silent
    )

    if not files_to_bundle:
        if not silent:
            print("No files found to bundle.")
        end_time = time.time()
        duration = end_time - start_time
        if not silent:
            print_stats("bundle", stats, duration)
        return stats

    # Sort files to group similar types together - aids in AI analysis
    files_to_bundle.sort(key=lambda x: (x['extension'], x['formatted_path']))

    stats["original_size"] = sum(os.path.getsize(f['file_path']) for f in files_to_bundle if os.path.exists(f['file_path']))

    # Group files by extension for more efficient processing
    extension_groups = {}
    for file_info in files_to_bundle:
        ext = file_info['extension']
        if ext not in extension_groups:
            extension_groups[ext] = []
        extension_groups[ext].append(file_info)

    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# {os.path.basename(source_dir)} ({len(files_to_bundle)} files)\n")
        if minify:
            outfile.write(f"# Minification: Enabled (using python-minifier for Python files)\n")
        outfile.write("\n")

        for ext, group_files in extension_groups.items():
            if group_files:
                outfile.write(f"## {ext.upper() or 'UNKNOWN'} FILES ({len(group_files)})\n\n")

            for file_info in group_files:
                file_path = file_info['file_path']
                formatted_path = file_info['formatted_path']
                file_extension = '.' + file_info['full_extension'] if file_info['full_extension'] else ''

                try:
                    with open(file_path, 'r', encoding='utf-8') as infile:
                        content = infile.read()
                        original_content_size = len(content)

                    if not content.strip():
                        if not silent:
                            print(f"Skipped empty file: {formatted_path}")
                        stats["skipped_files"] += 1
                        continue

                    if minify:
                        minified_content = minify_code(content, file_extension)
                        stats["minified_size"] += len(minified_content)
                        content = minified_content
                    else:
                        stats["minified_size"] = 0  # Not using minification

                    outfile.write(f"`{formatted_path}`\n```\n")
                    outfile.write(content.rstrip())
                    outfile.write("\n```\n\n")

                    stats["files_bundled"] += 1
                    stats["bytes_bundled"] += len(content)

                    if not silent:
                        if minify and file_extension.lower() == '.py':
                            reduction = (1 - len(content) / max(original_content_size, 1)) * 100
                            print(f"Bundled: {formatted_path} (Size reduction: {reduction:.2f}%)")
                        else:
                            print(f"Bundled: {formatted_path}")

                except UnicodeDecodeError:
                    if not silent:
                        print(f"Skipped binary file: {formatted_path}")
                    stats["skipped_files"] += 1
                except Exception as e:
                    error_msg = f"Error bundling {formatted_path}: {str(e)}"
                    print(error_msg)
                    raise RuntimeError(error_msg)

    end_time = time.time()
    duration = end_time - start_time

    if not silent:
        print_stats("bundle", stats, duration)

    return stats


def flatten_dir(source_dir, dest_dir, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                include_dirs=None, include_exts=None, include_files=None, clear_dest_dir=False, silent=False,
                ignore_defaults=False):
    """Flatten a directory structure by copying files to a destination directory."""
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml", "shell"]

    exclude_dirs = merge_with_defaults(exclude_dirs, DEFAULT_EXCLUDE_DIRS, ignore_defaults)
    exclude_exts = merge_with_defaults(exclude_exts, ALL_EXCLUDE_EXTENSIONS, ignore_defaults)
    exclude_files = merge_with_defaults(exclude_files, ALL_EXCLUDE_FILENAMES, ignore_defaults)

    all_stats = []
    start_time = time.time()

    for file_type in file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            file_dest_dir = os.path.join(dest_dir, file_type)

            if include_exts:
                if not any(ext in include_exts for ext in handler.extensions):
                    continue

            if not silent:
                print(f"\n================ {file_type.upper()} FILES ================\n")

            file_stats = handler.flatten_dir(source_dir, file_dest_dir, exclude_dirs, exclude_exts, exclude_files,
                                             include_dirs, include_exts, include_files, clear_dest_dir, silent)

            if file_stats["files_copied"] > 0:
                all_stats.append(file_stats)
            elif os.path.exists(file_dest_dir) and not os.listdir(file_dest_dir):
                try:
                    os.rmdir(file_dest_dir)
                    if not silent:
                        print(f"Removed empty directory: {file_dest_dir}")
                except OSError:
                    pass

    merged_stats = merge_stats(all_stats)
    end_time = time.time()
    duration = end_time - start_time

    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("flatten", merged_stats, duration)

    return merged_stats


def deflatten_dir(flattened_dir, dest_dir, file_types=None, exclude_files=None, include_dirs=None,
                  include_exts=None, include_files=None, clear_dest_dir=False, silent=False, ignore_defaults=False):
    """Deflatten a directory by reconstructing the original directory structure."""
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml", "shell"]

    exclude_files = merge_with_defaults(exclude_files, ALL_EXCLUDE_FILENAMES, ignore_defaults)

    all_stats = []
    start_time = time.time()

    for file_type in file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            source_dir = os.path.join(flattened_dir, file_type)

            if include_exts:
                if not any(ext in include_exts for ext in handler.extensions):
                    continue

            if os.path.exists(source_dir) and os.listdir(source_dir):
                if not silent:
                    print(f"\n================ {file_type.upper()} FILES ================\n")

                file_stats = handler.deflatten_dir(source_dir, dest_dir, exclude_files, include_dirs,
                                                   include_exts, include_files, clear_dest_dir, silent)
                all_stats.append(file_stats)

    merged_stats = merge_stats(all_stats)
    end_time = time.time()
    duration = end_time - start_time

    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("deflatten", merged_stats, duration)

    return merged_stats


def main():
    parser = argparse.ArgumentParser(description="Flatten, deflatten, bundle, or minify a directory of files.")

    src_group = parser.add_argument_group('source')
    src_group.add_argument("src_pos", nargs="?", help="Source directory path (positional, default: current directory)")
    src_group.add_argument("--src", "-s", dest="src_named", help="Source directory path (named)")

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument("dest_pos", nargs="?",
                            help="Destination directory or file path (positional, defaults based on operation)")
    dest_group.add_argument("--dest", "-d", dest="dest_named", help="Destination directory or file path (named)")

    parser.add_argument("--file-types", "-t",
                        nargs="+",
                        choices=["py", "ipynb", "jsts", "mdtxt", "yml", "shell"],
                        default=["py", "ipynb", "jsts", "mdtxt", "yml", "shell"],
                        help="File types to process: 'py' for Python, 'ipynb' for Python Notebooks, 'jsts' for JavaScript/TypeScript, 'md' for Markdown, 'yml' for YAML, 'shell' for Shell Scripts (default: all)")

    exclusion_group = parser.add_argument_group('exclusion options')
    exclusion_group.add_argument("--exclude-dirs", "-xd",
                                 nargs="+",
                                 help="Directory names to exclude")
    exclusion_group.add_argument("--exclude-extensions", "-xe",
                                 nargs="+",
                                 help="File extensions to exclude")
    exclusion_group.add_argument("--exclude-files", "-xf",
                                 nargs="+",
                                 help="Specific filenames to exclude")

    inclusion_group = parser.add_argument_group('inclusion options')
    inclusion_group.add_argument("--include-dirs", "-id",
                                 nargs="+",
                                 help="Directory names to include (only these will be processed)")
    inclusion_group.add_argument("--include-extensions", "-ie",
                                 nargs="+",
                                 help="File extensions to include (only these will be processed)")
    inclusion_group.add_argument("--include-files", "-if",
                                 nargs="+",
                                 help="Specific filenames to include (only these will be processed)")

    defaults_group = parser.add_argument_group('defaults handling')
    defaults_group.add_argument("--ignore-defaults", "-i",
                                action="store_true",
                                help="Ignore all default exclusion lists and only use the provided options")

    operation_group = parser.add_argument_group('operations')
    operation_group.add_argument("--flatten", "-f",
                                 action="store_true",
                                 help="Flatten the directory structure (default: True if no other operation specified)")
    operation_group.add_argument("--deflatten", "-df",
                                 action="store_true",
                                 help="Deflatten the directory (restore original structure)")
    operation_group.add_argument("--bundle", "-b",
                                 action="store_true",
                                 help="Bundle files into a single document file")
    operation_group.add_argument("--minify-bundle", "-mb",
                                 action="store_true",
                                 help="Minify files and bundle them into a single document file")
    operation_group.add_argument("--minify", "-m",
                                 action="store_true",
                                 help="Create a minified copy of the directory while preserving structure")

    parser.add_argument("--clear-dest-dir", "-c",
                        action="store_true",
                        help="Clear the destination directory before copying (default: False)")
    parser.add_argument('--no-log', "-nl",
                        action='store_true',
                        help="Suppress all output logs.")

    args = parser.parse_args()

    source_dir = args.src_named if args.src_named else args.src_pos
    if not source_dir:
        source_dir = os.getcwd()

    output_base_dir = create_timestamped_dir()
    print(f"Output directory: {output_base_dir}")

    operations = []
    if args.flatten:
        operations.append("flatten")
    if args.deflatten:
        operations.append("deflatten")
    if args.bundle:
        operations.append("bundle")
    if args.minify_bundle:
        operations.append("minify_bundle")
    if args.minify:
        operations.append("minify")
    if not operations:
        operations.append("flatten")

    try:
        for operation in operations:
            if operation == "flatten":
                flatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not flatten_dest:
                    flatten_dest = os.path.join(output_base_dir, DEFAULT_FLATTEN_OUTPUT_PATH)

                print(f"\n===== EXECUTING FLATTEN: {source_dir} -> {flatten_dest} =====\n")
                stats = flatten_dir(source_dir, flatten_dest, args.file_types,
                                    args.exclude_dirs, args.exclude_extensions, args.exclude_files,
                                    args.include_dirs, args.include_extensions, args.include_files,
                                    args.clear_dest_dir, args.no_log, args.ignore_defaults)

            elif operation == "deflatten":
                deflatten_dest = args.dest_named if args.dest_named else args.dest_pos
                if not deflatten_dest:
                    deflatten_dest = os.path.join(output_base_dir, DEFAULT_DEFLATTEN_OUTPUT_PATH)

                print(f"\n===== EXECUTING DEFLATTEN: {source_dir} -> {deflatten_dest} =====\n")
                stats = deflatten_dir(source_dir, deflatten_dest, args.file_types, args.exclude_files,
                                      args.include_dirs, args.include_extensions, args.include_files,
                                      args.clear_dest_dir, args.no_log, args.ignore_defaults)

            elif operation == "bundle":
                bundle_dest = args.dest_named if args.dest_named else args.dest_pos
                if not bundle_dest:
                    bundle_dest = os.path.join(output_base_dir, DEFAULT_BUNDLE_OUTPUT_PATH)

                print(f"\n===== EXECUTING BUNDLE: {source_dir} -> {bundle_dest} =====\n")
                stats = bundle_files(source_dir, bundle_dest, args.file_types,
                                     args.exclude_dirs, args.exclude_extensions, args.exclude_files,
                                     args.include_dirs, args.include_extensions, args.include_files,
                                     args.no_log, args.ignore_defaults, minify=False)

            elif operation == "minify_bundle":
                bundle_dest = args.dest_named if args.dest_named else args.dest_pos
                if not bundle_dest:
                    bundle_dest = os.path.join(output_base_dir, DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH)

                print(f"\n===== EXECUTING MINIFY-BUNDLE: {source_dir} -> {bundle_dest} =====\n")
                stats = bundle_files(source_dir, bundle_dest, args.file_types,
                                     args.exclude_dirs, args.exclude_extensions, args.exclude_files,
                                     args.include_dirs, args.include_extensions, args.include_files,
                                     args.no_log, args.ignore_defaults, minify=True)

            elif operation == "minify":
                minify_dest = args.dest_named if args.dest_named else args.dest_pos
                if not minify_dest:
                    minify_dest = os.path.join(output_base_dir, DEFAULT_MINIFY_OUTPUT_PATH)

                print(f"\n===== EXECUTING MINIFY: {source_dir} -> {minify_dest} =====\n")
                stats = minify(source_dir, minify_dest, args.file_types,
                               args.exclude_dirs, args.exclude_extensions, args.exclude_files,
                               args.include_dirs, args.include_extensions, args.include_files,
                               args.clear_dest_dir, args.no_log, args.ignore_defaults)

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
