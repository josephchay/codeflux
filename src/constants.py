DEFAULT_PYTHON_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv"]
DEFAULT_PYTHON_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]
DEFAULT_PYTHON_EXCLUDE_FILENAMES = ["setup.py", "conftest.py"]

DEFAULT_JS_EXCLUDE_DIRS = [".git", "node_modules", "dist", "build", ".next", ".vscode", ".idea"]
DEFAULT_JS_EXCLUDE_EXTENSIONS = ["d.ts", ".test.js", ".test.ts", ".spec.js", ".spec.ts", ".min.js"]
DEFAULT_JS_EXCLUDE_FILENAMES = ["babel.config.js", "jest.config.js", "webpack.config.js"]

JS_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]

DEFAULT_MD_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv", "node_modules"]
DEFAULT_MD_EXCLUDE_EXTENSIONS = []  # No specific exclusions for markdown
DEFAULT_MD_EXCLUDE_FILENAMES = ["LICENSE.md", "CONTRIBUTING.md", "CODE_OF_CONDUCT.md"]

MD_EXTENSIONS = [".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn", ".mdtxt", ".mdtext", ".txt"]

DEFAULT_YAML_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv", "node_modules"]
DEFAULT_YAML_EXCLUDE_EXTENSIONS = []  # No specific exclusions for YAML
DEFAULT_YAML_EXCLUDE_FILENAMES = ["docker-compose.yaml", "docker-compose.yml", "circleci.yml"]

YAML_EXTENSIONS = [".yaml", ".yml"]
