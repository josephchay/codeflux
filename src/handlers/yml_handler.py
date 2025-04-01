from utils import FileExtHandler
from constants import YML_EXTENSIONS, DEFAULT_EXCLUDE_DIRS, YML_EXCLUDE_EXTENSIONS, YML_EXCLUDE_FILENAMES


class YamlHandler(FileExtHandler):
    """Handler for YAML files"""
    def __init__(self):
        super().__init__(
            extensions=YML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=YML_EXCLUDE_EXTENSIONS,
            exclude_filenames=YML_EXCLUDE_FILENAMES
        )
