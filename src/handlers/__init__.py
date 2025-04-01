from .py_handler import PythonHandler
from .jsts_handler import JavaScriptTypescriptHandler
from .md_handler import MarkdownHandler
from .yml_handler import YamlHandler


py_handler = PythonHandler()
jsts_handler = JavaScriptTypescriptHandler()
md_handler = MarkdownHandler()
yml_handler = YamlHandler()

HANDLERS = {
    "py": py_handler,
    "jsts": jsts_handler,
    "md": md_handler,
    "yaml": yml_handler
}


__all__ = ["py_handler", "jsts_handler", "md_handler", "yml_handler", "HANDLERS"]
