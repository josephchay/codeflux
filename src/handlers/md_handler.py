from utils import FileExtHandler
from constants import MDTXT_EXTENSIONS, DEFAULT_EXCLUDE_DIRS, MDTXT_EXCLUDE_EXTENSIONS, MDTXT_EXCLUDE_FILENAMES


class MarkdownHandler(FileExtHandler):
    """Handler for Markdown files"""
    def __init__(self):
        super().__init__(
            extensions=MDTXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=MDTXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=MDTXT_EXCLUDE_FILENAMES
        )
