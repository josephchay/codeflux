"""
File handlers for different file types.
Each handler specializes in processing files of a specific type or extension.
"""

from file_handler import FileHandler
from constants import *


class PythonHandler(FileHandler):
    """Handler for Python files."""

    def __init__(self):
        super().__init__(
            extensions=PYTHON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PYTHON_EXCLUDE_EXTENSIONS,
            exclude_filenames=PYTHON_EXCLUDE_FILENAMES
        )


class NotebookHandler(FileHandler):
    """Handler for Jupyter Notebook files."""

    def __init__(self):
        super().__init__(
            extensions=NOTEBOOK_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOTEBOOK_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOTEBOOK_EXCLUDE_FILENAMES
        )


class JavaScriptTypescriptHandler(FileHandler):
    """Handler for JavaScript and TypeScript files."""

    def __init__(self):
        super().__init__(
            extensions=JSTS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSTS_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSTS_EXCLUDE_FILENAMES
        )


class HtmlHandler(FileHandler):
    """Handler for HTML files."""

    def __init__(self):
        super().__init__(
            extensions=HTML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=HTML_EXCLUDE_EXTENSIONS,
            exclude_filenames=HTML_EXCLUDE_FILENAMES
        )


class CssHandler(FileHandler):
    """Handler for CSS files."""

    def __init__(self):
        super().__init__(
            extensions=CSS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=CSS_EXCLUDE_EXTENSIONS,
            exclude_filenames=CSS_EXCLUDE_FILENAMES
        )


class PhpHandler(FileHandler):
    """Handler for PHP files."""

    def __init__(self):
        super().__init__(
            extensions=PHP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PHP_EXCLUDE_EXTENSIONS,
            exclude_filenames=PHP_EXCLUDE_FILENAMES
        )


class RubyHandler(FileHandler):
    """Handler for Ruby files."""

    def __init__(self):
        super().__init__(
            extensions=RUBY_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=RUBY_EXCLUDE_EXTENSIONS,
            exclude_filenames=RUBY_EXCLUDE_FILENAMES
        )


class SwiftHandler(FileHandler):
    """Handler for Swift files."""

    def __init__(self):
        super().__init__(
            extensions=SWIFT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SWIFT_EXCLUDE_EXTENSIONS,
            exclude_filenames=SWIFT_EXCLUDE_FILENAMES
        )


class KotlinHandler(FileHandler):
    """Handler for Kotlin files."""

    def __init__(self):
        super().__init__(
            extensions=KOTLIN_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=KOTLIN_EXCLUDE_EXTENSIONS,
            exclude_filenames=KOTLIN_EXCLUDE_FILENAMES
        )


class JavaHandler(FileHandler):
    """Handler for Java files."""

    def __init__(self):
        super().__init__(
            extensions=JAVA_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JAVA_EXCLUDE_EXTENSIONS,
            exclude_filenames=JAVA_EXCLUDE_FILENAMES
        )


class CSharpHandler(FileHandler):
    """Handler for C# files."""

    def __init__(self):
        super().__init__(
            extensions=CSHARP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=CSHARP_EXCLUDE_EXTENSIONS,
            exclude_filenames=CSHARP_EXCLUDE_FILENAMES
        )


class ShellHandler(FileHandler):
    """Handler for Shell script files."""

    def __init__(self):
        super().__init__(
            extensions=SHELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SHELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=SHELL_EXCLUDE_FILENAMES
        )


class MarkdownTextHandler(FileHandler):
    """Handler for Markdown and text files."""

    def __init__(self):
        super().__init__(
            extensions=MDTXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=MDTXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=MDTXT_EXCLUDE_FILENAMES
        )


class YamlHandler(FileHandler):
    """Handler for YAML files."""

    def __init__(self):
        super().__init__(
            extensions=YML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=YML_EXCLUDE_EXTENSIONS,
            exclude_filenames=YML_EXCLUDE_FILENAMES
        )


class JsonHandler(FileHandler):
    """Handler for JSON files."""

    def __init__(self):
        super().__init__(
            extensions=JSON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSON_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSON_EXCLUDE_FILENAMES
        )


class GoHandler(FileHandler):
    """Handler for Go files."""

    def __init__(self):
        super().__init__(
            extensions=GO_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=GO_EXCLUDE_EXTENSIONS,
            exclude_filenames=GO_EXCLUDE_FILENAMES
        )


class IniHandler(FileHandler):
    """Handler for INI files."""

    def __init__(self):
        super().__init__(
            extensions=INI_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=INI_EXCLUDE_EXTENSIONS,
            exclude_filenames=INI_EXCLUDE_FILENAMES
        )


class DatabaseHandler(FileHandler):
    """Handler for Database files."""

    def __init__(self):
        super().__init__(
            extensions=DB_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=DB_EXCLUDE_EXTENSIONS,
            exclude_filenames=DB_EXCLUDE_FILENAMES
        )


class BatchHandler(FileHandler):
    """Handler for Batch files."""

    def __init__(self):
        super().__init__(
            extensions=BAT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=BAT_EXCLUDE_EXTENSIONS,
            exclude_filenames=BAT_EXCLUDE_FILENAMES
        )


class ScpHandler(FileHandler):
    """Handler for Script files."""

    def __init__(self):
        super().__init__(
            extensions=SCP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SCP_EXCLUDE_EXTENSIONS,
            exclude_filenames=SCP_EXCLUDE_FILENAMES
        )


class NoExtHandler(FileHandler):
    """Handler for files without extensions."""

    def __init__(self):
        super().__init__(
            extensions=NOEXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOEXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOEXT_EXCLUDE_FILENAMES
        )

    def handles_file(self, filename):
        """Only handle files that have no extension at all."""
        # Check if the filename has no dot (except for hidden files that start with dot)
        if "." not in filename:
            return True
        # Special case for hidden files (which start with a dot)
        if filename.startswith(".") and filename.count(".") == 1:
            return True
        return False


class PowerShellHandler(FileHandler):
    """Handler for PowerShell files."""

    def __init__(self):
        super().__init__(
            extensions=POWERSHELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=POWERSHELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=POWERSHELL_EXCLUDE_FILENAMES
        )


class DockerHandler(FileHandler):
    """Handler for Docker files."""

    def __init__(self):
        super().__init__(
            extensions=DOCKER_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=DOCKER_EXCLUDE_EXTENSIONS,
            exclude_filenames=DOCKER_EXCLUDE_FILENAMES
        )


class XmlHandler(FileHandler):
    """Handler for XML files."""

    def __init__(self):
        super().__init__(
            extensions=XML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=XML_EXCLUDE_EXTENSIONS,
            exclude_filenames=XML_EXCLUDE_FILENAMES
        )


class RHandler(FileHandler):
    """Handler for R files."""

    def __init__(self):
        super().__init__(
            extensions=R_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=R_EXCLUDE_EXTENSIONS,
            exclude_filenames=R_EXCLUDE_FILENAMES
        )


class CppHandler(FileHandler):
    """Handler for C/C++ files."""

    def __init__(self):
        super().__init__(
            extensions=CPP_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=CPP_EXCLUDE_EXTENSIONS,
            exclude_filenames=CPP_EXCLUDE_FILENAMES
        )


class RustHandler(FileHandler):
    """Handler for Rust files."""

    def __init__(self):
        super().__init__(
            extensions=RUST_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=RUST_EXCLUDE_EXTENSIONS,
            exclude_filenames=RUST_EXCLUDE_FILENAMES
        )


class ScalaHandler(FileHandler):
    """Handler for Scala files."""

    def __init__(self):
        super().__init__(
            extensions=SCALA_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=SCALA_EXCLUDE_EXTENSIONS,
            exclude_filenames=SCALA_EXCLUDE_FILENAMES
        )


class PerlHandler(FileHandler):
    """Handler for Perl files."""

    def __init__(self):
        super().__init__(
            extensions=PERL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PERL_EXCLUDE_EXTENSIONS,
            exclude_filenames=PERL_EXCLUDE_FILENAMES
        )


class LuaHandler(FileHandler):
    """Handler for Lua files."""

    def __init__(self):
        super().__init__(
            extensions=LUA_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=LUA_EXCLUDE_EXTENSIONS,
            exclude_filenames=LUA_EXCLUDE_FILENAMES
        )


class GroovyHandler(FileHandler):
    """Handler for Groovy files."""

    def __init__(self):
        super().__init__(
            extensions=GROOVY_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=GROOVY_EXCLUDE_EXTENSIONS,
            exclude_filenames=GROOVY_EXCLUDE_FILENAMES
        )


class HaskellHandler(FileHandler):
    """Handler for Haskell files."""

    def __init__(self):
        super().__init__(
            extensions=HASKELL_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=HASKELL_EXCLUDE_EXTENSIONS,
            exclude_filenames=HASKELL_EXCLUDE_FILENAMES
        )


class ErlangHandler(FileHandler):
    """Handler for Erlang files."""

    def __init__(self):
        super().__init__(
            extensions=ERLANG_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=ERLANG_EXCLUDE_EXTENSIONS,
            exclude_filenames=ERLANG_EXCLUDE_FILENAMES
        )


class LatexHandler(FileHandler):
    """Handler for LaTeX files."""

    def __init__(self):
        super().__init__(
            extensions=LATEX_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=LATEX_EXCLUDE_EXTENSIONS,
            exclude_filenames=LATEX_EXCLUDE_FILENAMES
        )


class PDFHandler(FileHandler):
    """Handler for PDF files."""

    def __init__(self):
        super().__init__(
            extensions=PDF_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PDF_EXCLUDE_EXTENSIONS,
            exclude_filenames=PDF_EXCLUDE_FILENAMES
        )


class DOCXHandler(FileHandler):
    """Handler for DOCX files."""

    def __init__(self):
        super().__init__(
            extensions=DOCX_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=DOCX_EXCLUDE_EXTENSIONS,
            exclude_filenames=DOCX_EXCLUDE_FILENAMES
        )


class BibTexHandler(FileHandler):
    """Handler for BibTeX files."""

    def __init__(self):
        super().__init__(
            extensions=BIBTEX_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=BIBTEX_EXCLUDE_EXTENSIONS,
            exclude_filenames=BIBTEX_EXCLUDE_FILENAMES
        )


# Register all handlers
HANDLERS = {
    "py": PythonHandler(),
    "ipynb": NotebookHandler(),
    "jsts": JavaScriptTypescriptHandler(),
    "html": HtmlHandler(),
    "css": CssHandler(),
    "php": PhpHandler(),
    "ruby": RubyHandler(),
    "swift": SwiftHandler(),
    "kotlin": KotlinHandler(),
    "java": JavaHandler(),
    "csharp": CSharpHandler(),
    "shell": ShellHandler(),
    "mdtxt": MarkdownTextHandler(),
    "yml": YamlHandler(),
    "json": JsonHandler(),
    "go": GoHandler(),
    "ini": IniHandler(),
    "db": DatabaseHandler(),
    "bat": BatchHandler(),
    "scp": ScpHandler(),
    "noext": NoExtHandler(),
    "ps1": PowerShellHandler(),
    "docker": DockerHandler(),
    "xml": XmlHandler(),
    "r": RHandler(),
    "cpp": CppHandler(),
    "rust": RustHandler(),
    "scala": ScalaHandler(),
    "perl": PerlHandler(),
    "lua": LuaHandler(),
    "groovy": GroovyHandler(),
    "haskell": HaskellHandler(),
    "erlang": ErlangHandler(),
    "latex": LatexHandler(),
    "bibtex": BibTexHandler(),
    "pdf": PDFHandler(),
    "docx": DOCXHandler(),
}
