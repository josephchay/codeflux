DEFAULT_EXCLUDE_DIRS = ["__pycache__",  ".git",  ".idea",  ".vscode",  ".venv",  "venv",  "node_modules",  "dist",
                        "build",  ".next",  "codebundle.egg-info"]

PYTHON_EXTENSIONS = [".py"]
PYTHON_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]
PYTHON_EXCLUDE_FILENAMES = ["setup.py", "conftest.py"]

NOTEBOOK_EXTENSIONS = [".ipynb"]
NOTEBOOK_EXCLUDE_EXTENSIONS = [".nbconvert.ipynb"]
NOTEBOOK_EXCLUDE_FILENAMES = ["Untitled.ipynb"]

JSTS_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
JSTS_EXCLUDE_EXTENSIONS = ["d.ts", ".test.js", ".test.ts", ".spec.js", ".spec.ts", ".min.js"]
JSTS_EXCLUDE_FILENAMES = ["babel.config.js", "jest.config.js", "webpack.config.js"]

MDTXT_EXTENSIONS = [".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn", ".mdtxt", ".mdtext", ".txt"]
MDTXT_EXCLUDE_EXTENSIONS = []
MDTXT_EXCLUDE_FILENAMES = ["LICENSE.md", "LICENSE.txt", "CONTRIBUTING.md", "CONTRIBUTING.txt", "CODE_OF_CONDUCT.md",
                           "CODE_OF_CONDUCT.txt", "CHANGELOG.md", "CHANGELOG.txt"]

YML_EXTENSIONS = [".yaml", ".yml"]
YML_EXCLUDE_EXTENSIONS = []
YML_EXCLUDE_FILENAMES = ["docker-compose.yaml", "docker-compose.yml", "circleci.yml"]

SHELL_EXTENSIONS = [".sh", ".bash", ".zsh"]
SHELL_EXCLUDE_EXTENSIONS = []
SHELL_EXCLUDE_FILENAMES = ["setup.sh", "install.sh", "bootstrap.sh"]

JSON_EXTENSIONS = [".json", ".jsonl", ".geojson", ".json5", ".ndjson"]
JSON_EXCLUDE_EXTENSIONS = []
JSON_EXCLUDE_FILENAMES = ["package-lock.json", "yarn.lock.json", "composer.lock", "poetry.lock"]

ALL_EXTENSIONS = (
    PYTHON_EXTENSIONS + NOTEBOOK_EXTENSIONS + JSTS_EXTENSIONS +
    MDTXT_EXTENSIONS + YML_EXTENSIONS + SHELL_EXTENSIONS + JSON_EXTENSIONS
)

ALL_EXCLUDE_EXTENSIONS = (
    PYTHON_EXCLUDE_EXTENSIONS + NOTEBOOK_EXCLUDE_EXTENSIONS +
    JSTS_EXCLUDE_EXTENSIONS + MDTXT_EXCLUDE_EXTENSIONS +
    YML_EXCLUDE_EXTENSIONS + SHELL_EXCLUDE_EXTENSIONS + JSON_EXCLUDE_EXTENSIONS
)

ALL_EXCLUDE_FILENAMES = (
    PYTHON_EXCLUDE_FILENAMES + NOTEBOOK_EXCLUDE_FILENAMES +
    JSTS_EXCLUDE_FILENAMES + MDTXT_EXCLUDE_FILENAMES +
    YML_EXCLUDE_FILENAMES + SHELL_EXCLUDE_FILENAMES + JSON_EXCLUDE_FILENAMES
)

DEFAULT_FLATTEN_OUTPUT_PATH = "flattened"
DEFAULT_DEFLATTEN_OUTPUT_PATH = "deflattened"
DEFAULT_BUNDLE_OUTPUT_PATH = "bundled.txt"
DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH = "minified_bundle.txt"
DEFAULT_MINIFY_OUTPUT_PATH = "minified"
