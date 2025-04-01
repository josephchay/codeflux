from utils import FileExtHandler
from constants import PYTHON_EXTENSIONS, DEFAULT_EXCLUDE_DIRS, PYTHON_EXCLUDE_EXTENSIONS, PYTHON_EXCLUDE_FILENAMES


class PythonHandler(FileExtHandler):
    """Handler for Python files"""
    def __init__(self):
        super().__init__(
            extensions=PYTHON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PYTHON_EXCLUDE_EXTENSIONS,
            exclude_filenames=PYTHON_EXCLUDE_FILENAMES
        )
