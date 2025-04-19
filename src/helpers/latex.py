import csv
import os


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
