DEFAULT_EXCLUDE_DIRS = ["__pycache__",  ".git",  ".idea",  ".vscode",  ".venv",  "venv",  "node_modules", "dist",
                        "build",  ".next", "codebundle.egg-info"]

# Python-specific settings
PYTHON_EXTENSIONS = [".py"]
PYTHON_EXCLUDE_EXTENSIONS = [".pyc", ".pyo", "__init__.py"]
PYTHON_EXCLUDE_FILENAMES = ["setup.py", "conftest.py"]

# Python Notebook-specific settings
NOTEBOOK_EXTENSIONS = [".ipynb"]
NOTEBOOK_EXCLUDE_EXTENSIONS = [".nbconvert.ipynb"]
NOTEBOOK_EXCLUDE_FILENAMES = ["Untitled.ipynb"]

# JavaScript/TypeScript-specific settings
JSTS_EXTENSIONS = [".js", ".jsx", ".ts", ".tsx"]
JSTS_EXCLUDE_EXTENSIONS = ["d.ts", ".test.js", ".test.ts", ".spec.js", ".spec.ts", ".min.js"]
JSTS_EXCLUDE_FILENAMES = ["babel.config.js", "jest.config.js", "webpack.config.js"]

# Markdown/Text-specific settings
MDTXT_EXTENSIONS = [".md", ".markdown", ".mdown", ".mkdn", ".mkd", ".mdwn", ".mdtxt", ".mdtext", ".txt"]
MDTXT_EXCLUDE_EXTENSIONS = []
MDTXT_EXCLUDE_FILENAMES = ["LICENSE.md", "LICENSE.txt", "CONTRIBUTING.md", "CONTRIBUTING.txt", "CODE_OF_CONDUCT.md",
                           "CODE_OF_CONDUCT.txt", "CHANGELOG.md", "CHANGELOG.txt"]

# YAML-specific settings
YML_EXTENSIONS = [".yaml", ".yml"]
YML_EXCLUDE_EXTENSIONS = []
YML_EXCLUDE_FILENAMES = ["docker-compose.yaml", "docker-compose.yml", "circleci.yml"]

# Combined settings for quick access
ALL_EXTENSIONS = PYTHON_EXTENSIONS + NOTEBOOK_EXTENSIONS + JSTS_EXTENSIONS + MDTXT_EXTENSIONS + YML_EXTENSIONS
ALL_EXCLUDE_EXTENSIONS = PYTHON_EXCLUDE_EXTENSIONS + NOTEBOOK_EXCLUDE_EXTENSIONS + JSTS_EXCLUDE_EXTENSIONS + MDTXT_EXCLUDE_EXTENSIONS + YML_EXCLUDE_EXTENSIONS
ALL_EXCLUDE_FILENAMES = PYTHON_EXCLUDE_FILENAMES + NOTEBOOK_EXCLUDE_FILENAMES + JSTS_EXCLUDE_FILENAMES + MDTXT_EXCLUDE_FILENAMES + YML_EXCLUDE_FILENAMES
