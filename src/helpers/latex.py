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


def make_acronyms_tex_from_csv(csv_path, output_tex_path):
    os.makedirs(os.path.dirname(output_tex_path), exist_ok=True)

    acronyms = []
    with open(csv_path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)

        # Skip header if present
        header_row = next(reader, None)
        if header_row and any(keyword.lower() in header_row[0].lower() for keyword in ['title', 'acronym', 'abbreviation']):
            pass
        else:
            # If first row doesn't look like a header, process it as data
            if header_row and len(header_row) >= 2:
                acronyms.append((header_row[0].strip(), header_row[1].strip()))

        for row in reader:
            if len(row) >= 2:
                acronym = row[0].strip()
                definition = row[1].strip()
                if acronym and definition:
                    acronyms.append((acronym, definition))

    acronyms.sort(key=lambda x: x[0])
    with open(output_tex_path, 'w', encoding='utf-8') as f:
        f.write("% Acronyms converted from given csv template by CodeFlux\n")
        f.write("\\begin{acronym}[XXXXXXXXX]\n")
        for acronym, definition in acronyms:
            definition = definition.replace("_", "\\_").replace("&", "\\&").replace("#", "\\#")
            f.write(f"  \\acro{{{acronym}}}{{{definition}}}\n")
        f.write("\\end{acronym}\n")

    return True
