"""
Snippet utilities for code extraction and line range handling.
"""

import re
from typing import Tuple, List, Optional, Any, Dict, Set


def apply_snippet_filter(content: str, snippet_enabled: bool = False, snippet_lines: int = 50,
                         snippet_start: str = "top", snippet_context: int = 5,
                         search_pattern: Optional[str] = None) -> Tuple[str, int, int]:
    """
    Extract a snippet from the content based on the specified parameters.

    Args:
        content: The full file content
        snippet_enabled: Whether to enable snippet mode
        snippet_lines: Maximum number of lines to include
        snippet_start: Where to start the snippet (top, middle, bottom)
        snippet_context: Number of context lines around matches
        search_pattern: Pattern to search for

    Returns:
        Tuple of (snippet_content, line_count, original_line_count)
    """
    if not snippet_enabled:
        # If snippet mode is not enabled, return the original content
        return content, len(content.splitlines()), len(content.splitlines())

    lines = content.splitlines()
    original_line_count = len(lines)

    # If the file is already smaller than the snippet size, return the whole file
    if original_line_count <= snippet_lines:
        return content, original_line_count, original_line_count

    # If there's a search pattern, extract the context around matches
    if search_pattern:
        try:
            pattern = re.compile(search_pattern, re.IGNORECASE)
            match_lines = []

            # Find all lines that match the pattern
            for i, line in enumerate(lines):
                if pattern.search(line):
                    match_lines.append(i)

            # If there are matches, extract lines with context
            if match_lines:
                included_lines = set()

                for line_num in match_lines:
                    # Add context lines around the match
                    start = max(0, line_num - snippet_context)
                    end = min(original_line_count, line_num + snippet_context + 1)

                    for i in range(start, end):
                        included_lines.add(i)

                # If we have too many lines, prioritize the first matches
                included_lines = sorted(list(included_lines))
                if len(included_lines) > snippet_lines:
                    included_lines = included_lines[:snippet_lines]

                # Extract the filtered lines
                filtered_lines = [lines[i] for i in included_lines]
                return '\n'.join(filtered_lines), len(filtered_lines), original_line_count
        except Exception as e:
            print(f"Warning: Error applying search pattern in snippet mode: {str(e)}")
            # Fall back to normal snippet behavior

    # Apply normal snippet behavior based on snippet_start
    if snippet_start == "top":
        filtered_lines = lines[:snippet_lines]
    elif snippet_start == "bottom":
        filtered_lines = lines[max(0, original_line_count - snippet_lines):]
    elif snippet_start == "middle":
        # Take lines from the middle of the file
        middle = original_line_count // 2
        half_snippet = snippet_lines // 2
        start = max(0, middle - half_snippet)
        end = min(original_line_count, middle + half_snippet + (snippet_lines % 2))
        filtered_lines = lines[start:end]
    else:
        # Default to top if an invalid value is provided
        filtered_lines = lines[:snippet_lines]

    return '\n'.join(filtered_lines), len(filtered_lines), original_line_count


def parse_line_ranges(line_ranges_str: str, max_lines: int) -> List[int]:
    """
    Parse a string of line ranges into a list of line numbers.

    Args:
        line_ranges_str: String with line ranges (e.g. "1-5,7,9-12")
        max_lines: Maximum number of lines in the file

    Returns:
        List of line numbers
    """
    line_numbers = []
    try:
        for part in line_ranges_str.split(','):
            part = part.strip()
            if '-' in part:
                start, end = map(int, part.split('-'))
                line_numbers.extend(range(start, min(end + 1, max_lines + 1)))
            else:
                line_number = int(part)
                if 0 < line_number <= max_lines:
                    line_numbers.append(line_number)
    except ValueError:
        # Handle invalid format gracefully
        print(f"Warning: Invalid line range format '{line_ranges_str}'. Expected format: '1-10,15,20-30'")

    return sorted(set(line_numbers))  # Remove duplicates and sort


def get_file_snippet(content: str, max_lines: int = 50, position: str = "top",
                     pattern: Optional[str] = None, context_lines: int = 5) -> Tuple[str, bool, int]:
    """
    Get a snippet from a file based on various criteria.

    Args:
        content: File content
        max_lines: Maximum number of lines to include
        position: Where to extract from (top, middle, bottom)
        pattern: Pattern to search for
        context_lines: Number of context lines around matches

    Returns:
        Tuple of (snippet_content, is_truncated, original_line_count)
    """
    lines = content.splitlines()
    original_line_count = len(lines)

    if len(lines) <= max_lines:
        return content, False, original_line_count

    if pattern:
        matches = list(re.finditer(pattern, content))
        if matches:
            match_line_numbers = []
            line_indexes = [0]
            for i, line in enumerate(lines):
                line_indexes.append(line_indexes[-1] + len(line) + 1)
            for match in matches:
                start_pos = match.start()
                for i in range(len(line_indexes) - 1):
                    if line_indexes[i] <= start_pos < line_indexes[i + 1]:
                        match_line_numbers.append(i)
                        break

            extracted_lines = set()
            for line_num in match_line_numbers:
                start = max(0, line_num - context_lines)
                end = min(len(lines), line_num + context_lines + 1)
                for i in range(start, end):
                    extracted_lines.add(i)

            extracted_lines = sorted(list(extracted_lines))
            if len(extracted_lines) > max_lines:
                # If we have too many lines, prioritize first matches
                extracted_lines = extracted_lines[:max_lines]

            result_lines = []
            current_group = []
            for i, line_num in enumerate(extracted_lines):
                if i > 0 and line_num > extracted_lines[i - 1] + 1:
                    result_lines.extend(current_group)
                    result_lines.append("# [...] Skipped lines")
                    current_group = []
                current_group.append(lines[line_num])

            result_lines.extend(current_group)
            return "\n".join(result_lines), True, original_line_count

    if position == "top":
        return "\n".join(lines[:max_lines]) + "\n# [...] Remaining lines omitted", True, original_line_count
    elif position == "bottom":
        return "\n".join(["# [...] Initial lines omitted"] + lines[-max_lines:]), True, original_line_count
    else:  # middle
        mid_point = len(lines) // 2
        half_snippet = max_lines // 2
        start = max(0, mid_point - half_snippet)
        end = min(len(lines), mid_point + half_snippet)
        return "\n".join(["# [...] Initial lines omitted"] +
                         lines[start:end] +
                         ["# [...] Remaining lines omitted"]), True, original_line_count
