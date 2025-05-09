"""
Acroscan Operation: Scans files for acronyms and optionally replaces them.
"""

import csv
import os
import re
from typing import Dict, List, Optional, Any

from constants import DEFAULT_ACRONYMS_FOUND_OUTPUT_PATH, DEFAULT_ACRONYMS_FOUND_TEX_OUTPUT_PATH, \
    DEFAULT_ACRONYMS_TRANSLATED_OUTPUT_PATH
from file_handler import FileHandler
from operations.base import Operation, OperationStats
from utils.logging import Logger


class AcroscanOperation(Operation):
    """Operation to scan for and replace acronyms in files."""

    def __init__(self, file_handler: FileHandler, logger: Logger = None):
        """Initialize the acroscan operation."""
        super().__init__("acroscan", file_handler, logger)

    def execute(self, source_dir: str, output_dir: str, **kwargs) -> OperationStats:
        """
        Execute the acroscan operation.

        Args:
            source_dir: Source directory containing files to scan
            output_dir: Output directory for processed files
            **kwargs: Additional arguments:
                - acronym_list_path: Path to CSV file with acronyms
                - exclude_dirs: Directories to exclude
                - exclude_exts: File extensions to exclude
                - exclude_files: Specific files to exclude
                - include_dirs: Only include these directories
                - include_exts: Only include these file extensions
                - include_files: Only include these specific files
                - find_potential: Whether to find potential undefined acronyms
                - replace_acronyms: Whether to replace acronyms in files
                - latex_mode: Whether to use LaTeX syntax for acronyms
                - clear_dest_dir: Whether to clear the destination directory first
                - recursive: Whether to recursively process subdirectories

        Returns:
            OperationStats with operation results
        """
        source_dir = os.path.abspath(source_dir)
        output_dir = os.path.abspath(kwargs.get('output_dir', output_dir))

        acronym_list_path = kwargs.get('acronym_list_path')
        exclude_dirs = kwargs.get('exclude_dirs', [])
        exclude_exts = kwargs.get('exclude_exts', [])
        exclude_files = kwargs.get('exclude_files', [])
        include_dirs = kwargs.get('include_dirs', None)
        include_exts = kwargs.get('include_exts', None)
        include_files = kwargs.get('include_files', None)
        find_potential = kwargs.get('find_potential', False)
        replace_acronyms = kwargs.get('replace_acronyms', True)
        latex_mode = kwargs.get('latex_mode', True)
        clear_dest_dir = kwargs.get('clear_dest_dir', False)
        recursive = kwargs.get('recursive', True)

        # Load acronyms from CSV
        acronyms = self._load_acronyms_csv(acronym_list_path)

        # Create output directory
        if output_dir:
            if clear_dest_dir and os.path.exists(output_dir):
                import shutil
                shutil.rmtree(output_dir)
            os.makedirs(output_dir, exist_ok=True)

        # Log operation information
        if not self.logger.silent:
            if self.file_handler.extensions == [""]:
                self.logger.info("Processing files with no extension...\n")
            elif self.file_handler.extensions:
                self.logger.info(f"Processing files: {', '.join(self.file_handler.extensions)}...\n")

            if include_exts:
                self.logger.info(f"Including only extensions: {', '.join(include_exts)}")
            if include_dirs:
                self.logger.info(f"Including only directories: {', '.join(include_dirs)}")
            if include_files:
                self.logger.info(f"Including only files: {', '.join(include_files)}")
            if latex_mode:
                self.logger.info(f"LaTeX mode: Enabled")

        # Initialize statistics
        files_info = []
        self.stats.start_timer()

        # Initialize for aggregated stats
        all_unique_acronyms = set()
        all_acronyms_details = {}
        all_potential_acronyms = set()

        # Find and filter files
        file_paths = []
        if recursive:
            for root, dirs, files in os.walk(source_dir):
                self.stats.dirs_traversed += 1

                # Calculate nesting level
                rel_path = os.path.relpath(root, source_dir)
                current_nesting = len(rel_path.split(os.sep)) if rel_path != '.' else 0
                self.stats.update_max_nesting(current_nesting)

                # Filter directories
                if exclude_dirs:
                    dirs[:] = [d for d in dirs if d not in exclude_dirs]

                if include_dirs:
                    rel_dir_parts = rel_path.split(os.sep)
                    if not any(part in include_dirs for part in rel_dir_parts) and rel_path != '.':
                        dirs[:] = []  # Skip this branch
                        continue

                # Add files
                for file in files:
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
        else:
            file_paths = [os.path.join(source_dir, f) for f in os.listdir(source_dir)
                          if os.path.isfile(os.path.join(source_dir, f))]
            self.stats.dirs_traversed = 1

        # Filter files based on criteria
        filtered_files = []
        for file_path in file_paths:
            self.stats.total_files_processed += 1
            rel_path = os.path.relpath(file_path, source_dir)
            filename = os.path.basename(file_path)

            # Check if the file is of a type this handler processes
            if not self.file_handler.handles_file(filename):
                self.stats.skipped_files += 1
                continue

            # Apply additional file filters
            if self.file_handler.should_process_file(
                    filename,  # filename
                    exclude_exts,  # exclude_exts
                    exclude_files,  # exclude_files
                    include_exts,  # include_exts
                    include_files,  # include_files
                    rel_path  # file_rel_path
            ):
                filtered_files.append(file_path)
            else:
                self.stats.skipped_files += 1

        # Show a message if no files were found to process
        if not filtered_files:
            if not self.logger.silent:
                self.logger.info(f"No files found to process.")
                self.logger.info(f"Nothing to do for this file type.")

            self.stats.stop_timer()
            return self.stats

        # Setup directories for output
        converted_dir = os.path.join(output_dir, "converted") if output_dir and replace_acronyms else None

        # Only create the converted directory if actually replacing acronyms
        if converted_dir and replace_acronyms:
            os.makedirs(converted_dir, exist_ok=True)

        # Track whether any acronyms were found across files
        found_any_acronyms = False
        found_any_definitions = False

        # Process each file
        for file_path in filtered_files:
            rel_path = os.path.relpath(file_path, source_dir)

            try:
                # First scan for acronyms without replacing
                scan_result = self._acroscan_file(
                    file_path,
                    acronyms,
                    output_file=None,
                    find_potential=find_potential,
                    replace_acronyms=False,
                    latex_mode=latex_mode
                )

                # Track that we scanned this file
                self.stats.files_scanned += 1

                # Check for matches
                has_acronyms = bool(scan_result["found_acronyms"])
                has_definitions = bool(scan_result.get("found_definitions", {}))

                if has_acronyms:
                    found_any_acronyms = True

                if has_definitions:
                    found_any_definitions = True

                if not has_acronyms and not has_definitions:
                    # Add file info for reporting
                    files_info.append({
                        "file": rel_path,
                        "size": scan_result["file_size"],
                        "acronyms_found": 0,
                        "definitions_found": 0,
                        "acronyms_replaced": 0,
                        "definitions_replaced": 0,
                        "status": "No matches found"
                    })
                    continue

                # Update statistics with found acronyms
                if has_acronyms:
                    all_unique_acronyms.update(scan_result["found_acronyms"].keys())

                    # Merge acronym details
                    for acronym, info in scan_result["found_acronyms"].items():
                        if acronym not in all_acronyms_details:
                            all_acronyms_details[acronym] = {
                                "definition": info["definition"],
                                "count": 0,
                                "files": []
                            }
                        all_acronyms_details[acronym]["count"] += info["count"]
                        all_acronyms_details[acronym]["files"].append(rel_path)

                # Update statistics with found definitions
                if has_definitions:
                    all_unique_acronyms.update(scan_result["found_definitions"].keys())

                    # Merge definition details
                    for acronym, info in scan_result["found_definitions"].items():
                        if acronym not in all_acronyms_details:
                            definition = acronyms.get(acronym, "Unknown")
                            all_acronyms_details[acronym] = {
                                "definition": definition,
                                "count": 0,
                                "files": []
                            }
                        all_acronyms_details[acronym]["count"] += info["count"]
                        if rel_path not in all_acronyms_details[acronym]["files"]:
                            all_acronyms_details[acronym]["files"].append(rel_path)

                if find_potential:
                    all_potential_acronyms.update(scan_result["potential_acronyms"])

                # If replacing acronyms and we have matches
                if replace_acronyms and (has_acronyms or has_definitions) and converted_dir:
                    output_file = os.path.join(converted_dir, rel_path)
                    os.makedirs(os.path.dirname(output_file), exist_ok=True)

                    # Do the actual replacement
                    result = self._acroscan_file(
                        file_path,
                        acronyms,
                        output_file=output_file,
                        find_potential=False,
                        replace_acronyms=True,
                        latex_mode=latex_mode
                    )

                    # Add file info for reporting
                    files_info.append({
                        "file": rel_path,
                        "size": result["file_size"],
                        "acronyms_found": len(scan_result["found_acronyms"]),
                        "definitions_found": len(scan_result.get("found_definitions", {})),
                        "acronyms_replaced": result.get("replaced", 0) - result.get("definition_matches_replaced", 0),
                        "definitions_replaced": result.get("definition_matches_replaced", 0),
                        "status": f"Replaced {result.get('replaced', 0)} matches"
                    })
                elif (has_acronyms or has_definitions) and not replace_acronyms:
                    # Add file info for scan-only mode
                    files_info.append({
                        "file": rel_path,
                        "size": scan_result["file_size"],
                        "acronyms_found": len(scan_result["found_acronyms"]),
                        "definitions_found": len(scan_result.get("found_definitions", {})),
                        "acronyms_replaced": 0,
                        "definitions_replaced": 0,
                        "status": f"Found {len(scan_result['found_acronyms'])} acronyms, {len(scan_result.get('found_definitions', {}))} definitions"
                    })

            except Exception as e:
                if not self.logger.silent:
                    self.logger.error(f"Error processing file {rel_path}: {e}")

                files_info.append({
                    "file": rel_path,
                    "size": os.path.getsize(file_path),
                    "acronyms_found": 0,
                    "definitions_found": 0,
                    "acronyms_replaced": 0,
                    "definitions_replaced": 0,
                    "status": f"Error: {str(e)}"
                })

        # If no matches were found, show a message
        if not found_any_acronyms and not found_any_definitions and not self.logger.silent:
            self.logger.info("No acronyms or definition matches found in any files.")

        # Generate summary files if needed
        if output_dir and (found_any_acronyms or found_any_definitions):
            self._generate_acronyms_report(
                output_dir, source_dir,
                list(all_unique_acronyms),
                all_acronyms_details,
                list(all_potential_acronyms) if find_potential else [],
                acronyms,
                latex_mode
            )

        # Log results
        if not self.logger.silent and files_info and (found_any_acronyms or found_any_definitions):
            self.logger.info("[FILES PROCESSED]")
            self.logger.print_file_table(files_info, "acroscan")

            if all_unique_acronyms:
                self.logger.info("\n[ACRONYMS FOUND]")
                self.logger.info(f"Found {len(all_unique_acronyms)} unique acronyms")
                for acronym in sorted(all_acronyms_details.keys())[:10]:  # Show top 10
                    info = all_acronyms_details[acronym]
                    self.logger.info(f"  - {acronym}: {info['definition']} (found {info['count']} times)")
                if len(all_acronyms_details) > 10:
                    self.logger.info(f"  (and {len(all_acronyms_details) - 10} more...)")

            if find_potential and all_potential_acronyms:
                self.logger.info("\n[POTENTIAL UNKNOWN ACRONYMS]")
                self.logger.info(f"Found {len(all_potential_acronyms)} potential unknown acronyms")
                for acronym in sorted(list(all_potential_acronyms))[:10]:  # Show top 10
                    self.logger.info(f"  - {acronym}")
                if len(all_potential_acronyms) > 10:
                    self.logger.info(f"  (and {len(all_potential_acronyms) - 10} more...)")

        self.stats.stop_timer()

        if not self.logger.silent:
            self.logger.print_stats(self.stats, "acroscan")

        return self.stats

    def _acroscan_file(self, file_path: str, acronyms: Dict[str, str], output_file: Optional[str] = None,
                       find_potential: bool = False, replace_acronyms: bool = True,
                       latex_mode: bool = False) -> Dict[str, Any]:
        """
        Scan a file for acronyms and optionally replace them.

        Args:
            file_path: Path to the file to scan
            acronyms: Dictionary mapping acronyms to their definitions
            output_file: Path to write the modified file
            find_potential: Whether to find potential acronyms not in the list
            replace_acronyms: Whether to replace found acronyms
            latex_mode: Whether to use LaTeX syntax for replacements

        Returns:
            Dictionary with scan results
        """
        # Initialize result dictionary
        result = {
            "found_acronyms": {},
            "found_definitions": {},
            "potential_acronyms": [],
            "file_size": os.path.getsize(file_path),
            "replaced": 0,
            "definition_matches_replaced": 0
        }

        # Read file content
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Find acronyms
        for acronym, definition in acronyms.items():
            # Skip very short acronyms
            if len(acronym) < 2:
                continue

            # Create regex pattern to find the acronym as a whole word
            if latex_mode:
                pattern = r'(?<!\\gls\{)(?<!\\ac\{)(?<!\w)' + re.escape(acronym) + r'(?!\w)(?!\})'
            else:
                pattern = r'(?<!\w)' + re.escape(acronym) + r'(?!\w)'

            matches = list(re.finditer(pattern, content))
            if matches:
                result["found_acronyms"][acronym] = {
                    "definition": definition,
                    "count": len(matches),
                    "positions": [(m.start(), m.end()) for m in matches]
                }

        # Find definitions that might be acronyms
        for acronym, definition in acronyms.items():
            # Skip very short acronyms or those without definitions
            if len(acronym) < 2 or not definition:
                continue

            # Create patterns for definition variations
            words = definition.split()
            if not words:
                continue

            # Build regex pattern for the definition with variations
            if len(words[0]) > 0:
                first_char = words[0][0]
                rest_of_word = words[0][1:] if len(words[0]) > 1 else ""
                if first_char.isalpha():
                    first_word_pattern = f"[{first_char.upper()}{first_char.lower()}]{re.escape(rest_of_word.lower())}"
                else:
                    first_word_pattern = re.escape(words[0].lower())
            else:
                continue

            # Process middle words
            middle_words_pattern = []
            for word in words[1:-1] if len(words) > 2 else []:
                middle_words_pattern.append(re.escape(word.lower()))

            # Process last word (can be singular or plural)
            if len(words) > 1:
                last_word = words[-1].lower()
                if last_word.endswith('s'):
                    last_word_pattern = f"{re.escape(last_word)}|{re.escape(last_word[:-1])}"
                else:
                    last_word_pattern = f"{re.escape(last_word)}s?"
            else:
                last_word_pattern = ""

            # Build the complete pattern
            definition_parts = []
            if first_word_pattern:
                definition_parts.append(f"({first_word_pattern})")

            for middle_pattern in middle_words_pattern:
                definition_parts.append(f"([-\\s]+{middle_pattern})")

            if last_word_pattern and len(words) > 1:
                definition_parts.append(f"([-\\s]+({last_word_pattern}))")

            # Complete pattern with word boundaries
            if definition_parts:
                definition_pattern = r"\b" + "".join(definition_parts) + r"\b"

                try:
                    # Find definition matches
                    def_matches = list(re.finditer(definition_pattern, content, re.IGNORECASE))
                    if def_matches:
                        result["found_definitions"][acronym] = {
                            "pattern": definition_pattern,
                            "count": len(def_matches),
                            "positions": [(m.start(), m.end(), m.group(0)) for m in def_matches]
                        }
                except re.error:
                    pass  # Skip invalid regex patterns

        # Find potential unknown acronyms
        if find_potential:
            pattern = r'\b[A-Z][A-Za-z0-9]*[A-Z][A-Za-z0-9]*\b'
            potential_matches = set(re.findall(pattern, content))
            result["potential_acronyms"] = sorted(list(
                potential_matches - set(acronyms.keys())
            ))

        # Replace acronyms if requested
        if replace_acronyms and (result["found_acronyms"] or result["found_definitions"]) and output_file:
            modified_content = content

            # Collect and sort all positions
            all_acronym_positions = []
            for acronym, info in result["found_acronyms"].items():
                for start, end in info["positions"]:
                    all_acronym_positions.append((start, end, acronym, "acronym"))

            all_definition_positions = []
            for acronym, info in result["found_definitions"].items():
                for start, end, matched_text in info["positions"]:
                    all_definition_positions.append((start, end, acronym, "definition", matched_text))

            # Combine and sort in reverse to avoid position shifts
            all_positions = all_acronym_positions + all_definition_positions
            all_positions.sort(reverse=True, key=lambda x: x[0])

            # Track first occurrences
            first_occurrences = {}
            forward_sorted = sorted(all_positions, key=lambda x: x[0])
            for pos in forward_sorted:
                acronym = pos[2]
                if acronym not in first_occurrences:
                    first_occurrences[acronym] = pos

            # Perform replacements
            for pos in all_positions:
                if len(pos) == 4:  # Acronym replacement
                    start, end, acronym, pos_type = pos
                    is_first_occurrence = pos == first_occurrences.get(acronym)

                    if latex_mode:
                        sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
                        replacement = f"\\gls{{{sanitized_acronym}}}"
                    else:
                        if is_first_occurrence:
                            replacement = f"{acronyms[acronym]} ({acronym})"
                        else:
                            replacement = acronym
                else:  # Definition replacement
                    start, end, acronym, pos_type, matched_text = pos
                    is_first_occurrence = pos == first_occurrences.get(acronym)

                    if latex_mode:
                        sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
                        replacement = f"\\gls{{{sanitized_acronym}}}"
                        result["definition_matches_replaced"] += 1
                    else:
                        replacement = f"{matched_text} ({acronym})"
                        result["definition_matches_replaced"] += 1

                modified_content = modified_content[:start] + replacement + modified_content[end:]
                result["replaced"] += 1

            # Write modified content
            os.makedirs(os.path.dirname(output_file), exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(modified_content)

        return result

    def _load_acronyms_csv(self, path: str) -> Dict[str, str]:
        """
        Load acronyms from a CSV file.

        Args:
            path: Path to CSV file

        Returns:
            Dictionary mapping acronyms to their definitions
        """
        acronyms = {}

        if not path or not os.path.exists(path):
            return acronyms

        try:
            with open(path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)

                # Check for header row
                header_row = next(reader, None)
                if header_row and any(
                        keyword.lower() in header_row[0].lower()
                        for keyword in ['title', 'acronym', 'abbreviation']
                ):
                    # Skip header
                    pass
                else:
                    # Process first row as data
                    self._process_acronym_csv_row(acronyms, header_row)

                # Process remaining rows
                for row in reader:
                    self._process_acronym_csv_row(acronyms, row)
        except Exception as e:
            if not self.logger.silent:
                self.logger.error(f"Error loading acronyms list: {e}")

        return acronyms

    def _process_acronym_csv_row(self, acronyms_dict: Dict[str, str], row: List[str]):
        """Process a row from the acronym CSV file and add to the acronyms dictionary."""
        if not row or len(row) < 2:
            return

        acronym = row[0].strip()
        definition = row[1].strip()
        if not acronym or not definition:
            return

        acronyms_dict[acronym] = definition

    def _generate_acronyms_report(self, output_dir: str, source_dir: str,
                                  unique_acronyms: List[str], acronyms_details: Dict[str, Any],
                                  potential_acronyms: List[str], acronyms: Dict[str, str],
                                  latex_mode: bool = False):
        """
        Generate summary files for acronyms.

        Args:
            output_dir: Directory to write report files
            source_dir: Source directory that was processed
            unique_acronyms: List of unique acronyms found
            acronyms_details: Dictionary with details about each acronym
            potential_acronyms: List of potential acronyms found
            acronyms: Dictionary of known acronyms and their definitions
            latex_mode: Whether to generate LaTeX-specific files
        """
        # Generate text report
        acronyms_txt_path = os.path.join(output_dir, DEFAULT_ACRONYMS_FOUND_OUTPUT_PATH)
        with open(acronyms_txt_path, 'w', encoding='utf-8') as f:
            f.write(f"# Acronyms found in {os.path.basename(source_dir)}\n\n")

            if unique_acronyms:
                f.write("## Known Acronyms\n\n")
                for acronym in sorted(acronyms_details.keys()):
                    info = acronyms_details[acronym]
                    f.write(
                        f"- {acronym}: {info['definition']} (found {info['count']} times in {len(info['files'])} files)\n")

                f.write("\n## Files with Acronyms\n\n")
                file_acronyms = {}
                for acronym, info in acronyms_details.items():
                    for file_path in info["files"]:
                        if file_path not in file_acronyms:
                            file_acronyms[file_path] = []
                        file_acronyms[file_path].append(acronym)

                for file_path in sorted(file_acronyms.keys()):
                    f.write(f"### {file_path}\n")
                    for acronym in sorted(file_acronyms[file_path]):
                        info = acronyms_details[acronym]
                        f.write(f"- {acronym}: {info['definition']}\n")
                    f.write("\n")
            else:
                f.write("No known acronyms found.\n")

            if potential_acronyms:
                f.write("\n## Potential Unknown Acronyms\n\n")
                for acronym in sorted(potential_acronyms):
                    f.write(f"- {acronym}\n")

        # Generate LaTeX file if needed
        if latex_mode and unique_acronyms:
            acronyms_tex_path = os.path.join(output_dir, DEFAULT_ACRONYMS_FOUND_TEX_OUTPUT_PATH)
            with open(acronyms_tex_path, 'w', encoding='utf-8') as f:
                f.write("% Acronyms found by CodeFlux (glossaries package format)\n")

                for acronym in sorted(unique_acronyms):
                    definition = None
                    if acronym in acronyms_details:
                        definition = acronyms_details[acronym]["definition"]
                    else:
                        definition = acronyms.get(acronym, "")

                    if definition:
                        # Escape special LaTeX characters
                        definition = definition.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
                        sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
                        f.write(f"\\newacronym{{{sanitized_acronym}}}{{{acronym}}}{{{definition}}}\n")

            # Generate direct translations of all acronyms from CSV
            self._make_acronyms_tex_from_csv(acronyms, os.path.join(output_dir, DEFAULT_ACRONYMS_TRANSLATED_OUTPUT_PATH))

    def _make_acronyms_tex_from_csv(self, acronyms: Dict[str, str], output_tex_path: str):
        """
        Generate a LaTeX file with acronym definitions from a dictionary.

        Args:
            acronyms: Dictionary of acronyms and their definitions
            output_tex_path: Path to write the LaTeX file
        """
        os.makedirs(os.path.dirname(output_tex_path), exist_ok=True)

        with open(output_tex_path, 'w', encoding='utf-8') as f:
            f.write("% Acronyms converted from CSV by CodeFlux\n")

            for acronym, definition in sorted(acronyms.items()):
                # Skip empty definitions
                if not definition:
                    continue

                # Escape special LaTeX characters
                definition = definition.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
                sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
                f.write(f"\\newacronym{{{sanitized_acronym}}}{{{acronym}}}{{{definition}}}\n")
