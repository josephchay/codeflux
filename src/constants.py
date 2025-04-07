DEFAULT_EXCLUDE_DIRS = ["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv",
                        "node_modules", "dist", "build", ".next", "codebundle.egg-info",
                        "codebundle"]

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

GO_EXTENSIONS = [".go", ".mod", ".sum", ".pb.go", ".tmpl", ".tpl"]
GO_EXCLUDE_EXTENSIONS = [".pb.go"]
GO_EXCLUDE_FILENAMES = ["main_test.go"]

INI_EXTENSIONS = [".ini", ".cfg", ".conf", ".properties"]
INI_EXCLUDE_EXTENSIONS = [".sample", ".default"]
INI_EXCLUDE_FILENAMES = ["setup.ini", "config.ini", "environment.ini", "application.properties", "database.properties",
                         "log4j.properties", "system.cfg", "local.conf", "global.conf", "defaults.ini", "template.ini"]

DB_EXTENSIONS = [".sql", ".ddl", ".dml"]
DB_EXCLUDE_EXTENSIONS = []
DB_EXCLUDE_FILENAMES = ["schema.sql", "init.sql", "migration.sql", "seed.sql"]

BAT_EXTENSIONS = [".bat", ".cmd", ".btm"]
BAT_EXCLUDE_EXTENSIONS = []
BAT_EXCLUDE_FILENAMES = ["setup.bat", "install.cmd", "system_init.bat"]

SCP_EXTENSIONS = [".scp", ".script"]
SCP_EXCLUDE_EXTENSIONS = []
SCP_EXCLUDE_FILENAMES = ["main.scp", "config.script", "setup.script"]

ALL_EXTENSIONS = (
    PYTHON_EXTENSIONS + NOTEBOOK_EXTENSIONS + JSTS_EXTENSIONS +
    MDTXT_EXTENSIONS + YML_EXTENSIONS + SHELL_EXTENSIONS +
    JSON_EXTENSIONS + GO_EXTENSIONS + INI_EXTENSIONS + DB_EXTENSIONS +
    BAT_EXTENSIONS + SCP_EXTENSIONS
)

ALL_EXCLUDE_EXTENSIONS = (
    PYTHON_EXCLUDE_EXTENSIONS + NOTEBOOK_EXCLUDE_EXTENSIONS +
    JSTS_EXCLUDE_EXTENSIONS + MDTXT_EXCLUDE_EXTENSIONS +
    YML_EXCLUDE_EXTENSIONS + SHELL_EXCLUDE_EXTENSIONS +
    JSON_EXCLUDE_EXTENSIONS + GO_EXCLUDE_EXTENSIONS + INI_EXCLUDE_EXTENSIONS +
    DB_EXCLUDE_EXTENSIONS + BAT_EXCLUDE_EXTENSIONS + SCP_EXCLUDE_EXTENSIONS
)

ALL_EXCLUDE_FILENAMES = (
    PYTHON_EXCLUDE_FILENAMES + NOTEBOOK_EXCLUDE_FILENAMES +
    JSTS_EXCLUDE_FILENAMES + MDTXT_EXCLUDE_FILENAMES +
    YML_EXCLUDE_FILENAMES + SHELL_EXCLUDE_FILENAMES +
    JSON_EXCLUDE_FILENAMES + GO_EXCLUDE_FILENAMES + INI_EXCLUDE_FILENAMES +
    DB_EXCLUDE_FILENAMES + BAT_EXCLUDE_FILENAMES + SCP_EXCLUDE_FILENAMES
)

DEFAULT_FLATTEN_OUTPUT_PATH = "flattened"
DEFAULT_DEFLATTEN_OUTPUT_PATH = "deflattened"
DEFAULT_MINIFY_OUTPUT_PATH = "minified"
DEFAULT_BUNDLE_OUTPUT_PATH = "bundled.txt"
DEFAULT_MINIFY_BUNDLE_OUTPUT_PATH = "minified_bundle.txt"

OPERATION_FLATTEN = "flatten"
OPERATION_DEFLATTEN = "deflatten"
OPERATION_MINIFY = "minify"
OPERATION_BUNDLE = "bundle"
OPERATION_MINIFY_BUNDLE = "minify_bundle"
OPERATION_SEARCH = "search"
