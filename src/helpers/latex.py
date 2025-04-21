import os
import csv
import re
import sys


def process_acronym_csv_row(acronyms_dict, row):
    """Process a row from the acronym CSV file and add to the acronyms dictionary."""
    if not row or len(row) < 2:
        return

    acronym = row[0].strip()
    definition = row[1].strip()
    if not acronym or not definition:
        return

    acronyms_dict[acronym] = definition


def load_acronyms_csv(path, silent=False):
    """
    Load acronyms from a CSV file with the format:
    title (acronym), meaning (actual word), context, notes
    """
    acronyms = {}
    try:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)

                header_row = next(reader, None)
                if header_row and any(
                        keyword.lower() in header_row[0].lower() for keyword in ['title', 'acronym', 'abbreviation']):
                    pass
                else:
                    process_acronym_csv_row(acronyms, header_row)

                # Process remaining rows
                for row in reader:
                    process_acronym_csv_row(acronyms, row)
    except Exception as e:
        if not silent:
            print(f"Error loading acronym list: {e}")

    return acronyms


def make_acronyms_tex_from_csv(csv_path, output_tex_path):
    os.makedirs(os.path.dirname(output_tex_path), exist_ok=True)

    acronyms = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)    
        all_rows = list(reader)
        header_row = all_rows[0]
        start_idx = 0
        if all_rows and any(keyword.lower() in header_row[0].lower() for keyword in ['title', 'acronym', 'abbreviation']):
            start_idx = 1
        else:
            start_idx = 0
        
        # Process data rows
        for i in range(start_idx, len(all_rows)):
            row = all_rows[i]
            if len(row) >= 2:
                acronym = row[0].strip()
                definition = row[1].strip()
                if acronym and definition:
                    acronyms.append((acronym, definition))
    
    acronyms.sort(key=lambda x: x[0])
    with open(output_tex_path, 'w', encoding='utf-8') as f:
        # Use glossaries package format
        f.write("% Acronyms converted from CSV by CodeFlux\n")
        for acronym, definition in acronyms:
            definition = definition.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
            sanitized_acronym = re.sub(r'[^a-zA-Z0-9]', '', acronym).lower()
            f.write(f"\\newacronym{{{sanitized_acronym}}}{{{acronym}}}{{{definition}}}\n")

    return True
