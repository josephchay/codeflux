from utils import FileExtHandler
from constants import JSTS_EXTENSIONS, DEFAULT_EXCLUDE_DIRS, JSTS_EXCLUDE_EXTENSIONS, JSTS_EXCLUDE_FILENAMES


class JavaScriptTypescriptHandler(FileExtHandler):
    """Handler for JavaScript/TypeScript files"""
    def __init__(self):
        super().__init__(
            extensions=JSTS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSTS_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSTS_EXCLUDE_FILENAMES
        )
