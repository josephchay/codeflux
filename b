# Bundled Code from codefile-directory-flatterner
# Files: 79 | Created: 2025-04-02

### FILE: README.md
```md
# Codebundle - Unravel Your Codebase

_Effortlessly declutter and organize your project by flattening nested files into a single folder,
reconstruct the original directory structure from flattened files, or bundle all files into a single text document._

## Overview

Do you often find yourself digging through multiple nested directories to find files?
**Codebundle** is here to simplify your life! This lightweight CLI tool scans through your source directory (and all its subdirectories), 
collects all designated files and copies them into a single destination directory - all while automatically renaming conflicting files. 

It's perfect for organizing large codebases, consolidating scripts, or preparing for migration or backup.

### Supported File Types

| Language         | Extensions                                                                  |
|------------------|-----------------------------------------------------------------------------|
| Python           | `.py`                                                                       |
| Python Notebooks | `.ipynb`                                                                    |
| JavaScript       | `.js`, `.jsx`                                                               |
| TypeScript       | `.ts`, `.tsx`                                                               |
| Markdown         | `.md`, `.markdown`, `.mdown`, `.mkdn`, `.mkd`, `.mdwn`, `.mdtxt`, `.mdtext` |
| Plain Text       | `.txt`                                                                      |
| YAML             | `.yaml`, `.yml`                                                             |

_More extensions to be added in the future._

---

## Features

- **Flattens Nested Directories**: Gathers all required files into a single folder, no matter how deeply nested they are.
- **Exclude Options**: Allows excluding specific directories, file extensions, and specific filenames from the process.
- **Include Options**: Allows specifying exactly which files to process, ignoring all others.
- **Handles File Name Conflicts**: Renames files with duplicate names to ensure no overwriting.
- **Clean Destination Directory**: Automatically clears the destination folder before copying.
- **Command-Line Simplicity**: Provides an easy-to-use CLI interface.
- **Directory Path Preservation**: Option to prefix files with their original directory structure.
- **Exclude Specific Directories**: Allows excluding certain directories from the flattening process.
- **Exclude Specific File Extensions**: Allows excluding files with certain extensions.
- **Exclude Specific Files**: Allows excluding specific files by name.
- **Include Specific Files**: Allows processing only specific files by name.
- **Deflatten Functionality**: Provides the ability to revert the flattening process and restore the original directory structure.
- **Bundle Functionality**: Bundles all files into a single text file while preserving path information.
- **Multiple File Format Support**: 
  - Python files (.py)
  - Python Notebook files (.ipynb)
  - JavaScript/TypeScript files (.js, .jsx, .ts, .tsx)
  - Markdown files (.md, .markdown, etc.)
  - YAML files (.yaml, .yml)

---

## Installation

> [!WARNING]
> Uninstall the Package (If you have already installed a previous version of the package):

### Python Projects

```bash
pip install git+https://github.com/josephchay/codebundle.git
```

### NodeJS Projects

```bash
npm install --save-dev git+https://github.com/josephchay/codebundle.git
```
or
```bash
yarn add git+https://github.com/josephchay/codebundle.git --dev
```
or
```bash
pnpm add git+https://github.com/josephchay/codebundle.git --save-dev
```

Occasionally, check on the `staging` branch, as they may be some new features or bug fixes 
that have not been merged into the `main` branch.

## Command-Line Arguments

| Argument               | Required | Default                           | Description                                                                                                                              |
|------------------------|----------|-----------------------------------|------------------------------------------------------------------------------------------------------------------------------------------|
| `[src]`                | Yes      | -                                 | Source directory containing the files to flatten                                                                                         |
| `[dest]`               | Yes      | -                                 | Destination directory/file where files will be copied                                                                                    |
| `--file-types`         | No       | `py`, `ipynb`, `js`, `md`, `yaml` | File types to process: 'py' for Python, 'ipynb' for Python Notebooks, 'js' for JavaScript/TypeScript, 'md' for Markdown, 'yaml' for YAML |
| `--exclude-dirs`       | No       | Various default directories       | Directory names to exclude                                                                                                               |
| `--exclude-extensions` | No       | Various default extensions        | File extensions to exclude                                                                                                               |
| `--exclude-files`      | No       | Various common files              | Specific filenames to exclude (e.g., setup.py, jest.config.js)                                                                           |
| `--include-files`      | No       | None                              | Specific filenames to include (only these will be processed)                                                                             |
| `--clear-dest-dir`     | No       | `False`                           | Clear the destination directory before copying files                                                                                     |
| `--deflatten`          | No       | `False`                           | Deflatten the directory instead of flattening (reverses the flattening process)                                                          |
| `--bundle`             | No       | `False`                           | Bundle all files into a single text file with path information                                                                           |
| `--no-log`             | No       | `False`                           | Disable logging output                                                                                                                   |

For detailed information on the default values on the arguments, refer to the [constants](src/constants.py) file.

## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                    | Command                                                                                       | Description                                                                                               |
|-----------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Basic Flattening            | `codebundle --src src --dest flat`                                                            | Flattens all supported files into the 'flat' directory                                                    |
| Process Specific Types      | `codebundle --src src --dest flat --file-types py ipynb yaml`                                 | Process only Python, Python Notebooks, and YAML files, ignoring other types                               |
| Exclude Directories         | `codebundle --src src --dest flat --exclude-dirs .idea .venv`                                 | Excludes the `.idea` and `.venv` directories from the flattening process                                  |
| Exclude File Extensions     | `codebundle --src src --dest flat --exclude-extensions .txt .csv`                             | Excludes files with `.txt` and `.csv` extensions from the flattening process                              |
| Exclude Specific Files      | `codebundle --src src --dest flat --exclude-files setup.py package.json`                      | Excludes specific files like setup.py and package.json from the flattening process                        |
| Include Only Specific Files | `codebundle --src src --dest flat --include-files main.py analysis.ipynb config.yaml`         | Processes only the specified files, ignoring all others                                                   |
| Deflatten Directory         | `codebundle --src flattened --dest original --deflatten`                                      | Reverts the flattening process and restores the original directory structure from the flattened directory |
| Bundle Files                | `codebundle --src src --dest bundled.txt --bundle`                                            | Bundles all files into a single text file with clear file separators and path information                 |
| Bundle Only Specific Files  | `codebundle --src src --dest bundle.txt --bundle --include-files config.yaml notebook.ipynb`  | Bundles only the specified files into a single text file                                                  |
| Combine Exclusions          | `codebundle --src src --dest flat --exclude-dirs node_modules --exclude-files .env config.js` | Uses multiple exclusion types together                                                                    |


### Example Directory Transformations

#### Example 1: Basic Flattening With Python Notebooks
```
Before:                             After:
src/                               flat/
├── module1/                       ├── py/
│   ├── script1.py                 │   ├── module1___script1.py
│   ├── __init__.py                │   └── module1___utils___helper.py
│   └── utils/                     ├── ipynb/
│       └── helper.py              │   └── notebooks___analysis.ipynb
├── module2/                       ├── jsts/
│   └── script2.js                 │   └── module2___script2.js
├── notebooks/                     ├── md/
│   └── analysis.ipynb             │   └── docs___README.md
└── docs/                          └── yaml/
    ├── README.md                      ├── config___app.yaml
    └── config/                        └── config___env.yml
        ├── app.yaml
        └── env.yml
```

Command: 
```bash
codebundle --src src --dest flat
```
or without explicitly specifying the first two arguments:
```bash
codebundle src flat
```

#### Example 2: Flattening with Directory Prefixes

```
Before:                             After:
src/                               flat/
├── auth/                          ├── auth___login.py
│   ├── login.py                   ├── auth___utils___validator.py
│   └── utils/                     ├── models___user.py
│       └── validator.py           ├── data___analysis.ipynb
└── models/                        └── models___data___schema.py
    ├── user.py
    ├── data/
    │   └── schema.py
    └── data.ipynb
```

Command:
```bash
codebundle --src src --dest flat
```

#### Example 3: Excluding Directories and File Extensions

```
Before:                            After:
src/                               flat/
├── .idea/                         ├── py/
├── .git/                          │   ├── module1___script1.py
├── __pycache__/                   │   └── module2___script2.py
├── .venv/                         └── ipynb/
├── docs/                              └── notebooks___data_analysis.ipynb
│   └── README.md                  
├── tests/                         
│   ├── test_script1.py            
│   └── test_script2.py            
├── module1/                       
│   ├── script1.py                 
│   ├── __init__.py                
│   └── utils/                     
│       └── helper.pyc             
├── module2/                       
│   ├── script2.py                 
│   └── data/                      
│       ├── input.csv              
│       └── output.json            
└── notebooks/
    └── data_analysis.ipynb
```

Command:
```bash
codebundle --src src --dest flat --exclude-dirs .idea .git __pycache__ .venv docs tests --exclude-exts .md .pyc .csv .json
```
or
```bash
codebundle src flat --exclude-dirs .idea .git __pycache__ .venv docs tests --exclude-exts .md .pyc .csv .json
```

#### Example 4: Deflattening a Directory

```
Before:                             After:
flat/                              original/
├── py/                            ├── module1/
│   ├── module1___script.py        │   ├── script.py
│   └── module1___utils___helper.py│   └── utils/
├── ipynb/                         │       └── helper.py
│   └── data___analysis.ipynb      ├── module2/
├── jsts/                          │   ├── script_2.py
│   └── module2___script_2.js      │   └── data/
└── yaml/                          │       └── schema.py
    └── module2___data___schema.yml└── data/
                                       └── analysis.ipynb
```

Command:
```bash
codebundle --src flat --dest original --deflatten
```

#### Example 5: Flattening with Duplicated Filenames

```
Before:                                                     After:
src/                                                     flat/
├── projects/                                            ├── ipynb/
│   └── analysis.ipynb                                   │   ├── projects___analysis.ipynb
├── notebooks/                                           │   ├── notebooks___analysis.ipynb
│   └── analysis.ipynb                                   │   └── research___analysis.ipynb
└── research/                                            └── py/
    ├── analysis.ipynb                                       └── research___process.py
    └── process.py
```

Command:
```bash
codebundle --src src --dest flat
```

You can also flatten
```bash
codebundle --src . --dest flat
```
or
```bash
codebundle --src flat --dest .
```
or
```bash
codebundle . flat
```

To deflatten the directory, run:
```bash
codebundle --src . --dest . --deflatten
```

All the samples above apply the same for files with other extensions.

#### Example 6: Excluding Specific Files

```
Before:                            After:
src/                               flat/
├── module1/                       ├── py/
│   ├── script1.py                 │   └── module1___utils___helper.py
│   ├── setup.py                   ├── ipynb/
│   └── utils/                     │   └── module2___data.ipynb
│       └── helper.py              ├── jsts/
└── module2/                       │   └── module2___utils.js
    ├── utils.js                   └── md/
    ├── config.js                      └── GUIDE.md
    ├── Untitled.ipynb
    ├── data.ipynb
    └── docs/
        ├── README.md
        └── GUIDE.md
```

Command:
```bash
codebundle --src src --dest flat --exclude-files setup.py config.js README.md Untitled.ipynb
```

#### Example 7: Including Only Specific Files

```
Before:                             After:
src/                               flat/
├── module1/                       ├── py/
│   ├── script1.py                 │   └── module1___script1.py
│   ├── setup.py                   ├── ipynb/
│   └── utils/                     │   └── research___analysis.ipynb
│       └── helper.py              └── yaml/
├── module2/                           └── config___settings.yaml
│   ├── utils.js                   
│   ├── config.js                  
│   └── docs/                      
│       ├── README.md              
│       └── GUIDE.md               
├── research/
│   └── analysis.ipynb
└── config/
    ├── settings.yaml
    └── env.yml
```

Command:
```bash
codebundle --src src --dest flat --include-files script1.py analysis.ipynb settings.yaml
```

#### Example 8: Bundling Files into a Single Text File

```
Before:                            After (bundled.txt):
src/                               =================================================================================
├── module1/                       BUNDLED FILES FROM: /path/to/src
│   ├── script1.py                 CREATED: 2025-03-31 10:15:30
│   └── utils/                     =================================================================================
│       └── helper.py
├── notebooks/                     =================================================================================
│   └── analysis.ipynb             FILE: module1___script1.py
└── module2/                       =================================================================================
    └── script2.py                 
                                    # Content of script1.py

                                    =================================================================================
                                    FILE: module1___utils___helper.py
                                    =================================================================================

                                    # Content of helper.py

                                    =================================================================================
                                    FILE: notebooks___analysis.ipynb
                                    =================================================================================

                                    {
                                        "cells": [
                                            {
                                                "cell_type": "markdown",
                                                "metadata": {},
                                                "source": [
                                                    "# Data Analysis Notebook"
                                                ]
                                            },
                                            ...
                                        ]
                                    }

                                    =================================================================================
                                    FILE: module2___script2.py
                                    =================================================================================

                                    # Content of script2.py

                                    =================================================================================
                                    END OF BUNDLED FILES (4 files)
                                    =================================================================================
```

Command:
```bash
codebundle --src src --dest bundled.txt --bundle
```
or
```bash
codebundle src bundled.txt --bundle
```

#### Example 9: Bundling With Exclusions

```
Before:                            After (bundled.txt):
src/                               =====================================
├── module1/                       BUNDLED FILES FROM: /path/to/src
│   ├── script1.py                 CREATED: 2025-03-31 12:15:30
│   ├── setup.py                   =====================================
│   └── utils/
│       └── helper.py              =====================================
├── notebooks/                     FILE: module1___script1.py
│   ├── Untitled.ipynb             =====================================
│   └── analysis.ipynb             # Content of script1.py
└── module2/                      
    ├── utils.js                   =====================================
    └── config.js                  FILE: module1___utils___helper.py
                                   =====================================
                                   # Content of helper.py
                                   
                                   =====================================
                                   FILE: notebooks___analysis.ipynb
                                   =====================================
                                   {
                                       "cells": [
                                           ...
                                       ]
                                   }
                                   
                                   =====================================
                                   FILE: module2___utils.js
                                   =====================================
                                   // Content of utils.js
                                   
                                   =====================================
                                   END OF BUNDLED FILES (4 files)
                                   =====================================
```

Command:
```bash
codebundle --src src --dest bundled.txt --bundle --exclude-files setup.py config.js Untitled.ipynb
```

#### Example 10: Bundling only Specific Files (Inclusion)

```
Before:                            After (bundled.txt):
src/                               =====================================
├── module1/                       BUNDLED FILES FROM: /path/to/src
│   ├── script1.py                 CREATED: 2025-03-31 12:15:30
│   ├── setup.py                   =====================================
│   └── utils/
│       └── helper.py              =====================================
├── notebooks/                     FILE: module1___script1.py
│   └── analysis.ipynb             =====================================
└── module2/                       # Content of script1.py
    ├── utils.js                  
    ├── main.js                    =====================================
    └── config.js                  FILE: notebooks___analysis.ipynb
                                   =====================================
                                   {
                                       "cells": [
                                           ...
                                       ]
                                   }
                                   
                                   =====================================
                                   FILE: module2___main.js
                                   =====================================
                                   // Content of main.js
                                   
                                   =====================================
                                   END OF BUNDLED FILES (3 files)
                                   =====================================
```

Command:
```bash
codebundle --src src --dest bundled.txt --bundle --include-files script1.py analysis.ipynb main.js
```
or
```bash
codebundle src bundled.txt --b --include-files script1.py analysis.ipynb main.js
```

## Development

Clone the Repository:

```bash
git clone https://github.com/josephchay/codebundle.git
cd codebundle
```

Install Locally:

```bash
pip install -e .
```

### Testing

To test functionality during development, you can run:

```bash
python -m src.main --src <source_dir> --dest <dest_dir>
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Support

Need help? Have a question? Feel free to reach out:
* **Email**: [josephemmanuelchay@gmail.com](mailto:josephemmanuelchay@gmail.com)
* **GitHub Issues**: [Issues](https://github.com/josephchay/codebundle/issues)

Make your projects cleaner - flatten, deflatten, or bundle your directories today!
```

### FILE: src___constants.py
```py
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
```

### FILE: src___handlers.py
```py
import os
import shutil
import time

from constants import *
from utils import get_relative_path, get_unique_filename, print_stats


class FileExtHandler:
    def __init__(self, extensions, exclude_dirs, exclude_extensions, exclude_filenames):
        self.extensions = extensions
        self.default_exclude_dirs = exclude_dirs
        self.default_exclude_extensions = exclude_extensions
        self.default_exclude_filenames = exclude_filenames

    def is_valid_file(self, filename, exclude_exts=None, exclude_files=None, include_files=None):
        exclude_exts = exclude_exts or self.default_exclude_extensions
        exclude_files = exclude_files or self.default_exclude_filenames

        if include_files:
            return filename in include_files

        is_target_ext = any(filename.lower().endswith(ext) for ext in self.extensions)
        is_excluded_ext = any(filename.endswith(ext) for ext in exclude_exts)
        is_excluded_file = filename in exclude_files

        return is_target_ext and not is_excluded_ext and not is_excluded_file

    def flatten_dir(self, source_dir, dest_dir, exclude_dirs=None, exclude_exts=None,
                    exclude_files=None, include_files=None, clear_dest_dir=False, silent=False):
        exclude_dirs = exclude_dirs or self.default_exclude_dirs
        exclude_exts = exclude_exts or self.default_exclude_extensions
        exclude_files = exclude_files or self.default_exclude_filenames

        # Convert to absolute paths
        source_dir = os.path.abspath(source_dir)
        dest_dir = os.path.abspath(dest_dir)

        # Stats tracking
        stats = {
            "total_files_processed": 0,
            "dirs_traversed": 0,
            "files_copied": 0,
            "bytes_copied": 0,
            "skipped_files": 0,
            "max_nesting_level": 0
        }

        if clear_dest_dir and os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

        os.makedirs(dest_dir, exist_ok=True)

        source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))
        start_time = time.time()

        if not silent:
            print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
            print(f"Destination: {get_relative_path(dest_dir, os.getcwd())}\n")
            print(f"Processing files: {', '.join(self.extensions)}...")

        for root, dirs, files in os.walk(source_dir):
            stats["dirs_traversed"] += 1

            # Calculate nesting level
            current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
            stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

            # Exclude directories
            dirs[:] = [
                d for d in dirs
                if d not in exclude_dirs and os.path.abspath(os.path.join(root, d)) != dest_dir
            ]

            for file in files:
                stats["total_files_processed"] += 1

                if self.is_valid_file(file, exclude_exts, exclude_files, include_files):
                    source_file = os.path.join(root, file)
                    path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]

                    if path_parts:
                        new_filename = "___".join(path_parts + [file])
                    else:
                        new_filename = file

                    destination_file = os.path.join(dest_dir, new_filename)
                    unique_destination_file = get_unique_filename(destination_file)

                    # Copy file
                    shutil.copy2(source_file, unique_destination_file)
                    stats["files_copied"] += 1
                    stats["bytes_copied"] += os.path.getsize(source_file)

                    # Print relative paths with arrow
                    rel_source = get_relative_path(source_file, os.getcwd())
                    rel_dest = get_relative_path(unique_destination_file, os.getcwd())
                    if not silent:
                        print(f"{rel_source} → {rel_dest}")
                else:
                    stats["skipped_files"] += 1

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats("flatten", stats, duration)

        return stats

    def deflatten_dir(self, flattened_dir, dest_dir, exclude_files=None, include_files=None,
                      clear_dest_dir=False, silent=False):
        exclude_files = exclude_files or self.default_exclude_filenames

        flattened_dir = os.path.abspath(flattened_dir)
        dest_dir = os.path.abspath(dest_dir)

        stats = {
            "total_files_processed": 0,
            "dirs_created": 0,
            "files_copied": 0,
            "bytes_copied": 0,
            "skipped_files": 0
        }

        if clear_dest_dir and os.path.exists(dest_dir):
            shutil.rmtree(dest_dir)

        os.makedirs(dest_dir, exist_ok=True)
        stats["dirs_created"] += 1

        start_time = time.time()

        if not silent:
            print(f"Source: {get_relative_path(flattened_dir, os.getcwd())}")
            print(f"Destination: {get_relative_path(dest_dir, os.getcwd())}\n")
            print(f"Processing files: {', '.join(self.extensions)}...")

        for file in os.listdir(flattened_dir):
            stats["total_files_processed"] += 1
            original_filename = file.split("___")[-1]

            is_target_ext = any(file.lower().endswith(ext) for ext in self.extensions)
            is_excluded_file = original_filename in exclude_files

            if include_files:
                should_process = original_filename in include_files
            else:
                should_process = is_target_ext and not is_excluded_file

            if should_process:
                flattened_file = os.path.join(flattened_dir, file)
                path_parts = file.split("___")
                original_file = path_parts[-1]
                original_dir = os.path.join(dest_dir, *path_parts[:-1])

                if os.path.abspath(original_dir).startswith(flattened_dir):
                    print(f"Skipping to avoid overwriting source: {get_relative_path(flattened_file, os.getcwd())}")
                    stats["skipped_files"] += 1
                    continue

                if not os.path.exists(original_dir):
                    os.makedirs(original_dir, exist_ok=True)
                    stats["dirs_created"] += 1

                destination_file = os.path.join(original_dir, original_file)
                unique_destination_file = get_unique_filename(destination_file)

                shutil.copy2(flattened_file, unique_destination_file)
                stats["files_copied"] += 1
                stats["bytes_copied"] += os.path.getsize(flattened_file)

                rel_source = get_relative_path(flattened_file, os.getcwd())
                rel_dest = get_relative_path(unique_destination_file, os.getcwd())
                if not silent:
                    print(f"{rel_source} → {rel_dest}")
            else:
                stats["skipped_files"] += 1

        end_time = time.time()
        duration = end_time - start_time

        if not silent:
            print_stats("deflatten", stats, duration)

        return stats


class JavaScriptTypescriptHandler(FileExtHandler):
    """Handler for JavaScript/TypeScript files"""
    def __init__(self):
        super().__init__(
            extensions=JSTS_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=JSTS_EXCLUDE_EXTENSIONS,
            exclude_filenames=JSTS_EXCLUDE_FILENAMES
        )


class MarkdownTextHandler(FileExtHandler):
    """Handler for Markdown files"""
    def __init__(self):
        super().__init__(
            extensions=MDTXT_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=MDTXT_EXCLUDE_EXTENSIONS,
            exclude_filenames=MDTXT_EXCLUDE_FILENAMES
        )


class NotebookHandler(FileExtHandler):
    """Handler for Python Notebook files"""
    def __init__(self):
        super().__init__(
            extensions=NOTEBOOK_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=NOTEBOOK_EXCLUDE_EXTENSIONS,
            exclude_filenames=NOTEBOOK_EXCLUDE_FILENAMES
        )


class PythonHandler(FileExtHandler):
    """Handler for Python files"""
    def __init__(self):
        super().__init__(
            extensions=PYTHON_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=PYTHON_EXCLUDE_EXTENSIONS,
            exclude_filenames=PYTHON_EXCLUDE_FILENAMES
        )


class YamlHandler(FileExtHandler):
    """Handler for YAML files"""
    def __init__(self):
        super().__init__(
            extensions=YML_EXTENSIONS,
            exclude_dirs=DEFAULT_EXCLUDE_DIRS,
            exclude_extensions=YML_EXCLUDE_EXTENSIONS,
            exclude_filenames=YML_EXCLUDE_FILENAMES
        )


HANDLERS = {
    "py": PythonHandler(),
    "ipynb": NotebookHandler(),
    "jsts": JavaScriptTypescriptHandler(),
    "mdtxt": MarkdownTextHandler(),
    "yml": YamlHandler(),
}
```

### FILE: src___main.py
```py
import os
import argparse
import sys
import time

from constants import DEFAULT_EXCLUDE_DIRS, ALL_EXCLUDE_EXTENSIONS, ALL_EXCLUDE_FILENAMES, ALL_EXTENSIONS
from handlers import HANDLERS
from utils import get_relative_path, print_stats


def bundle_files(source_dir, output_file, file_types=None, exclude_dirs=None, exclude_exts=None,
                 exclude_files=None, include_files=None, silent=False):
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml"]
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_exts = exclude_exts or ALL_EXCLUDE_EXTENSIONS
    exclude_files = exclude_files or ALL_EXCLUDE_FILENAMES

    if isinstance(exclude_files, list):
        exclude_files = list(exclude_files)
    else:
        exclude_files = []

    source_dir = os.path.abspath(source_dir)
    output_file = os.path.abspath(output_file)
    output_filename = os.path.basename(output_file)
    if output_filename not in exclude_files:
        exclude_files.append(output_filename)
    source_dir_parts = len(os.path.normpath(source_dir).split(os.sep))

    stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_bundled": 0,
        "bytes_bundled": 0,
        "skipped_files": 0,
        "max_nesting_level": 0
    }

    # Get all file extensions based on selected file types
    included_extensions = []
    for file_type in file_types:
        if file_type in HANDLERS:
            included_extensions.extend(HANDLERS[file_type].extensions)

    start_time = time.time()

    if not silent:
        print(f"Source: {get_relative_path(source_dir, os.getcwd())}")
        print(f"Output file: {get_relative_path(output_file, os.getcwd())}\n")
        print(f"Bundling files into a single text file...")

    files_to_bundle = []
    for root, dirs, files in os.walk(source_dir):
        stats["dirs_traversed"] += 1

        # Calculate nesting level
        current_nesting = len(os.path.relpath(root, source_dir).split(os.sep))
        stats["max_nesting_level"] = max(stats["max_nesting_level"], current_nesting)

        # Exclude directories
        dirs[:] = [d for d in dirs if d not in exclude_dirs]

        for file in files:
            stats["total_files_processed"] += 1
            file_path = os.path.join(root, file)
            if os.path.abspath(file_path) == output_file:
                stats["skipped_files"] += 1
                continue

            # Check if file should be included
            is_included_ext = any(file.lower().endswith(ext) for ext in included_extensions)
            is_excluded_ext = any(file.endswith(ext) for ext in exclude_exts)
            is_excluded_file = file in exclude_files

            # If include_files is specified, only include those files
            if include_files:
                should_include = file in include_files
            else:
                should_include = is_included_ext and not is_excluded_ext and not is_excluded_file

            if should_include:
                path_parts = os.path.normpath(root).split(os.sep)[source_dir_parts:]
                if path_parts:
                    formatted_path = "___".join(path_parts + [file])
                else:
                    formatted_path = file

                # Get file extension for language hint
                _, file_ext = os.path.splitext(file)
                if file_ext:
                    file_ext = file_ext[1:]  # Remove the dot

                files_to_bundle.append({
                    'file_path': file_path,
                    'formatted_path': formatted_path,
                    'rel_path': os.path.relpath(file_path, source_dir),
                    'extension': file_ext
                })
            else:
                stats["skipped_files"] += 1

    if not files_to_bundle:
        if not silent:
            print("No files found to bundle.")
        end_time = time.time()
        duration = end_time - start_time
        if not silent:
            print_stats("bundling", stats, duration)
        return stats

    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.write(f"# Bundled Code from {os.path.basename(source_dir)}\n")
        outfile.write(f"# Files: {len(files_to_bundle)} | Created: {time.strftime('%Y-%m-%d')}\n\n")

        for file_info in files_to_bundle:
            file_path = file_info['file_path']
            formatted_path = file_info['formatted_path']
            file_ext = file_info['extension']

            try:
                with open(file_path, 'r', encoding='utf-8') as infile:
                    content = infile.read()

                outfile.write(f"### FILE: {formatted_path}\n")
                if file_ext:
                    outfile.write(f"```{file_ext}\n")
                else:
                    outfile.write("```\n")
                outfile.write(content)
                if not content.endswith('\n'):
                    outfile.write('\n')
                outfile.write("```\n\n")

                stats["files_bundled"] += 1
                stats["bytes_bundled"] += os.path.getsize(file_path)

                if not silent:
                    print(f"Bundled: {formatted_path}")

            except UnicodeDecodeError:
                if not silent:
                    print(f"Skipped binary file: {formatted_path}")
                stats["skipped_files"] += 1
            except Exception as e:
                if not silent:
                    print(f"Error bundling {formatted_path}: {str(e)}")
                stats["skipped_files"] += 1

    end_time = time.time()
    duration = end_time - start_time

    if not silent:
        print_stats("bundle", stats, duration)

    return stats


def merge_stats(stats_list):
    """Merge multiple statistics dictionaries into one"""
    merged_stats = {
        "total_files_processed": 0,
        "dirs_traversed": 0,
        "files_copied": 0,
        "bytes_copied": 0,
        "skipped_files": 0,
        "max_nesting_level": 0,
        "dirs_created": 0,
        "files_bundled": 0,
        "bytes_bundled": 0
    }

    for stats in stats_list:
        for key, value in stats.items():
            if key in merged_stats:
                merged_stats[key] += value
                # For max_nesting_level, keep the maximum value
                if key == "max_nesting_level":
                    merged_stats[key] = max(merged_stats[key], value)

    return merged_stats


def flatten_dir(source_dir, dest_dir, file_types=None, exclude_dirs=None, exclude_exts=None, exclude_files=None,
                include_files=None, clear_dest_dir=False, silent=False):
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml"]
    exclude_dirs = exclude_dirs or DEFAULT_EXCLUDE_DIRS
    exclude_exts = exclude_exts or ALL_EXCLUDE_EXTENSIONS
    exclude_files = exclude_files or ALL_EXCLUDE_FILENAMES

    all_stats = []
    start_time = time.time()

    for file_type in file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            file_dest_dir = os.path.join(dest_dir, file_type)

            if not silent:
                print(f"\n================ {file_type.upper()} FILES ================\n")

            file_stats = handler.flatten_dir(source_dir, file_dest_dir, exclude_dirs, exclude_exts, exclude_files,
                                             include_files, clear_dest_dir, silent)

            if file_stats["files_copied"] > 0:
                all_stats.append(file_stats)
            elif os.path.exists(file_dest_dir) and not os.listdir(file_dest_dir):
                try:
                    os.rmdir(file_dest_dir)
                    if not silent:
                        print(f"Removed empty directory: {file_dest_dir}")
                except OSError:
                    pass

    merged_stats = merge_stats(all_stats)
    end_time = time.time()
    duration = end_time - start_time

    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("flatten", merged_stats, duration)

    return merged_stats


def deflatten_dir(flattened_dir, dest_dir, file_types=None, exclude_files=None, include_files=None, clear_dest_dir=False,
                  silent=False):
    file_types = file_types or ["py", "ipynb", "jsts", "mdtxt", "yml"]
    exclude_files = exclude_files or ALL_EXCLUDE_FILENAMES

    all_stats = []
    start_time = time.time()

    for file_type in file_types:
        if file_type in HANDLERS:
            handler = HANDLERS[file_type]
            source_dir = os.path.join(flattened_dir, file_type)

            if os.path.exists(source_dir) and os.listdir(source_dir):
                if not silent:
                    print(f"\n================ {file_type.upper()} FILES ================\n")

                file_stats = handler.deflatten_dir(source_dir, dest_dir, exclude_files, include_files, clear_dest_dir, silent)
                all_stats.append(file_stats)

    merged_stats = merge_stats(all_stats)
    end_time = time.time()
    duration = end_time - start_time

    if not silent and merged_stats["files_copied"] > 0:
        print("\n================ OVERALL SUMMARY ================\n")
        print_stats("deflatten", merged_stats, duration)

    return merged_stats


def main():
    parser = argparse.ArgumentParser(description="Flatten, deflatten, or bundle a directory of Python, JavaScript, TypeScript, Markdown, and YAML files.")

    # Support both positional and named arguments
    src_group = parser.add_argument_group('source')
    src_group.add_argument("src_pos", nargs="?", help="Source directory path (positional)")
    src_group.add_argument("--src", dest="src_named", help="Source directory path (named)")

    dest_group = parser.add_argument_group('destination')
    dest_group.add_argument("dest_pos", nargs="?", help="Destination directory or file path (positional)")
    dest_group.add_argument("--dest", dest="dest_named", help="Destination directory or file path (named)")

    parser.add_argument("--file-types",
                        nargs="+",
                        choices=["py", "ipynb", "jsts", "mdtxt", "yml"],
                        default=["py", "ipynb", "jsts", "mdtxt", "yml"],
                        help="File types to process: 'py' for Python, 'ipynb' for Python Notebooks, 'jsts' for JavaScript/TypeScript, 'mdtxt' for Markdown, 'yml' for YAML (default: all)")

    parser.add_argument("--exclude-dirs",
                        nargs="+",
                        help="Directory names to exclude")
    parser.add_argument("--exclude-extensions",
                        nargs="+",
                        help="File extensions to exclude")
    parser.add_argument("--exclude-files",
                        nargs="+",
                        help="Specific filenames to exclude")

    parser.add_argument("--include-files",
                        nargs="+",
                        help="Specific filenames to include (only these will be processed)")

    operation_group = parser.add_mutually_exclusive_group()
    operation_group.add_argument("--deflatten",
                                 action="store_true",
                                 help="Deflatten the directory instead of flattening (default: False)")
    operation_group.add_argument("--bundle", "-b",
                                 action="store_true",
                                 help="Bundle files into a single text file (default: False)")

    parser.add_argument("--clear-dest-dir",
                        action="store_true",
                        help="Clear the destination directory before copying (default: False)")
    parser.add_argument('--no-log',
                        action='store_true',
                        help="Suppress all output logs.")

    args = parser.parse_args()

    source_dir = args.src_named if args.src_named else args.src_pos
    dest_path = args.dest_named if args.dest_named else args.dest_pos

    if not source_dir or not dest_path:
        parser.print_help()
        print("\nError: Both source and destination are required.")
        return 1

    try:
        if args.deflatten:
            stats = deflatten_dir(source_dir, dest_path, args.file_types, args.exclude_files, args.include_files,
                                  args.clear_dest_dir, args.no_log)
        elif args.bundle:
            stats = bundle_files(source_dir, dest_path, args.file_types, args.exclude_dirs, args.exclude_extensions,
                                 args.exclude_files, args.include_files, args.no_log)
        else:
            stats = flatten_dir(source_dir, dest_path, args.file_types, args.exclude_dirs, args.exclude_extensions,
                                args.exclude_files, args.include_files, args.clear_dest_dir, args.no_log)

        return 0
    except ValueError as e:
        print(f"Error: {e}")
        return 1
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
```

### FILE: src___utils.py
```py
import os


def get_unique_filename(destination_file):
    """
    Generate a unique filename if the destination file already exists
    by appending an incrementing counter
    """
    counter = 2
    name, ext = os.path.splitext(destination_file)
    unique_destination_file = destination_file

    while os.path.exists(unique_destination_file):
        unique_destination_file = f"{name}_{counter}{ext}"
        counter += 1

    return unique_destination_file


def get_relative_path(path, base_path):
    try:
        return os.path.relpath(path, base_path)
    except ValueError:
        return path


def print_stats(operation_type, stats, duration):
    print(f"Time taken: {duration:.6f} seconds")

    # Processing stats section
    print("\n[INPUT PROCESSING]")
    if operation_type in ["flatten", "bundle"]:
        if "dirs_traversed" in stats:
            print(f"Directories scanned: {stats['dirs_traversed']}")
        if "max_nesting_level" in stats:
            print(f"Maximum nesting level: {stats['max_nesting_level']}")
    print(f"Total files scanned: {stats['total_files_processed']}")
    print(f"Files skipped: {stats['skipped_files']} (non-target or excluded)")

    # Output stats section
    print("\n[OUTPUT RESULT]")
    if operation_type == "deflatten":
        if "dirs_created" in stats:
            print(f"Directories created: {stats['dirs_created']}")
        if "files_copied" in stats:
            print(f"Files in {operation_type} output: {stats['files_copied']}")
            print(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")
    elif operation_type == "bundle":
        if "files_bundled" in stats:
            print(f"Files bundled: {stats['files_bundled']}")
            print(f"Data bundled: {stats['bytes_bundled'] / 1024:.2f} KB")
    else:  # flatten
        if "files_copied" in stats:
            print(f"Files in {operation_type} output: {stats['files_copied']}")
            print(f"Data in {operation_type} output: {stats['bytes_copied'] / 1024:.2f} KB")

    # Calculate and print the appropriate processing rate
    if operation_type == "bundle":
        if "files_bundled" in stats:
            print(f"Processing rate: {stats['files_bundled'] / max(duration, 0.1):.2f} files/second")
    else:
        if "files_copied" in stats:
            print(f"Processing rate: {stats['files_copied'] / max(duration, 0.1):.2f} files/second")
    print("=" * 50)
```

### FILE: temp___constants.py
```py

```

### FILE: temp___fluxGUI.py
```py

```

### FILE: temp___FluxMusic_jupyter.ipynb
```ipynb
{
    "cells": [
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {
                "id": "VjYy0F2gZIPR"
            },
            "outputs": [],
            "source": [
                "%cd /content\n",
                "!git clone -b dev https://github.com/camenduru/FluxMusic\n",
                "%cd C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/FluxMusic\n",
                "\n",
                "!apt -y install -qq aria2\n",
                "!aria2c --console-log-level=error -c -x 16 -s 16 -k 1M https://huggingface.co/audo/FluxMusic/resolve/main/musicflow_b.pt -d C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/FluxMusic -o musicflow_b.pt\n",
                "\n",
                "!pip install transformers diffusers accelerate einops soundfile progressbar unidecode phonemizer torchlibrosa ftfy pandas timm matplotlib numpy==1.26.4 thop flash-attn==2.6.3 sentencepiece"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {
                "id": "NoTEt9Wto70D"
            },
            "outputs": [],
            "source": [
                "%cd C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter\n",
                "\n",
                "import os\n",
                "import torch\n",
                "import argparse\n",
                "import math\n",
                "from einops import rearrange, repeat\n",
                "from PIL import Image\n",
                "from diffusers import AutoencoderKL\n",
                "from transformers import SpeechT5HifiGan\n",
                "\n",
                "from utils import load_t5, load_clap, load_ae\n",
                "from train import RF\n",
                "from constants import build_model\n",
                "\n",
                "def prepare(t5, clip, img, prompt):\n",
                "    bs, c, h, w = img.shape\n",
                "    if bs == 1 and not isinstance(prompt, str):\n",
                "        bs = len(prompt)\n",
                "\n",
                "    img = rearrange(img, \"b c (h ph) (w pw) -> b (h w) (c ph pw)\", ph=2, pw=2)\n",
                "    if img.shape[0] == 1 and bs > 1:\n",
                "        img = repeat(img, \"1 ... -> bs ...\", bs=bs)\n",
                "\n",
                "    img_ids = torch.zeros(h // 2, w // 2, 3)\n",
                "    img_ids[..., 1] = img_ids[..., 1] + torch.arange(h // 2)[:, None]\n",
                "    img_ids[..., 2] = img_ids[..., 2] + torch.arange(w // 2)[None, :]\n",
                "    img_ids = repeat(img_ids, \"h w c -> b (h w) c\", b=bs)\n",
                "\n",
                "    if isinstance(prompt, str):\n",
                "        prompt = [prompt]\n",
                "    txt = t5(prompt)\n",
                "    if txt.shape[0] == 1 and bs > 1:\n",
                "        txt = repeat(txt, \"1 ... -> bs ...\", bs=bs)\n",
                "    txt_ids = torch.zeros(bs, txt.shape[1], 3)\n",
                "\n",
                "    vec = clip(prompt)\n",
                "    if vec.shape[0] == 1 and bs > 1:\n",
                "        vec = repeat(vec, \"1 ... -> bs ...\", bs=bs)\n",
                "\n",
                "    print(img_ids.size(), txt.size(), vec.size())\n",
                "    return img, {\n",
                "        \"img_ids\": img_ids.to(img.device),\n",
                "        \"txt\": txt.to(img.device),\n",
                "        \"txt_ids\": txt_ids.to(img.device),\n",
                "        \"y\": vec.to(img.device),\n",
                "    }\n",
                "\n",
                "version=\"base\"\n",
                "seed=2024\n",
                "prompt_file=\"C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/config/example.txt\"\n",
                "\n",
                "print('generate with MusicFlux')\n",
                "torch.manual_seed(seed)\n",
                "torch.set_grad_enabled(False)\n",
                "device = \"cuda\" if torch.cuda.is_available() else \"cpu\"\n",
                "\n",
                "latent_size = (256, 16)\n",
                "\n",
                "model = build_model(version).to(device)\n",
                "local_path = 'C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/musicflow_b.pt'\n",
                "state_dict = torch.load(local_path, map_location=lambda storage, loc: storage, weights_only=True)\n",
                "model.load_state_dict(state_dict['ema'])\n",
                "model.eval()  # important!\n",
                "diffusion = RF()"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {
                "id": "B5ebyTmto70D"
            },
            "outputs": [],
            "source": [
                "t5 = load_t5(device, max_length=256)\n",
                "clap = load_clap(device, max_length=256)\n",
                "\n",
                "vae = AutoencoderKL.from_pretrained('cvssp/audioldm2', subfolder=\"vae\").to(device)\n",
                "vocoder = SpeechT5HifiGan.from_pretrained('cvssp/audioldm2', subfolder=\"vocoder\").to(device)"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {
                "id": "xqG8Px6xo70D"
            },
            "outputs": [],
            "source": [
                "prompt_file=\"C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/config/example.txt\"\n",
                "\n",
                "with open(prompt_file, 'r') as f:\n",
                "    conds_txt = f.readlines()\n",
                "L = len(conds_txt)\n",
                "unconds_txt = [\"low quality, gentle\"] * L\n",
                "print(L, conds_txt, unconds_txt)\n",
                "\n",
                "init_noise = torch.randn(L, 8, latent_size[0], latent_size[1]).cuda()\n",
                "\n",
                "STEPSIZE = 50\n",
                "img, conds = prepare(t5, clap, init_noise, conds_txt)\n",
                "_, unconds = prepare(t5, clap, init_noise, unconds_txt)\n",
                "with torch.autocast(device_type='cuda'):\n",
                "    images = diffusion.sample_with_xps(model, img, conds=conds, null_cond=unconds, sample_steps = STEPSIZE, cfg = 7.0)\n",
                "\n",
                "print(images[-1].size(), )\n",
                "\n",
                "images = rearrange(\n",
                "    images[-1],\n",
                "    \"b (h w) (c ph pw) -> b c (h ph) (w pw)\",\n",
                "    h=128,\n",
                "    w=8,\n",
                "    ph=2,\n",
                "    pw=2,)\n",
                "# print(images.size())\n",
                "latents = 1 / vae.config.scaling_factor * images\n",
                "mel_spectrogram = vae.decode(latents).sample\n",
                "print(mel_spectrogram.size())"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": null,
            "metadata": {
                "id": "ytAXlAEdo70D"
            },
            "outputs": [],
            "source": [
                "!mkdir C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/FluxMusic/b_output\n",
                "\n",
                "for i in range(L):\n",
                "    x_i = mel_spectrogram[i]\n",
                "    if x_i.dim() == 4:\n",
                "        x_i = x_i.squeeze(1)\n",
                "    waveform = vocoder(x_i)\n",
                "    waveform = waveform[0].cpu().float().detach().numpy()\n",
                "    print(waveform.shape)\n",
                "    # import soundfile as sf\n",
                "    # sf.write('reconstruct.wav', waveform, samplerate=16000)\n",
                "    from  scipy.io import wavfile\n",
                "    wavfile.write('C:/Users/Curt/Developer/AItools/AIaudio/AudioCreation/FluxMusicJupyter/FluxMusic/b_output/sample_' + str(i) + '.wav', 16000, waveform)"
            ]
        }
    ],
    "metadata": {
        "accelerator": "GPU",
        "colab": {
            "gpuType": "T4",
            "provenance": []
        },
        "kernelspec": {
            "display_name": "Python 3",
            "name": "python3"
        },
        "language_info": {
            "name": "python"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 0
}
```

### FILE: temp___model.py
```py

```

### FILE: temp___README.md
```md

```

### FILE: temp___requirements.txt
```txt

```

### FILE: temp___sample.py
```py

```

### FILE: temp___test.py
```py

```

### FILE: temp___train.py
```py

```

### FILE: temp___utils.py
```py

```

### FILE: temp___audioldm2___pipeline.py
```py

```

### FILE: temp___audioldm2___utils.py
```py

```

### FILE: temp___audioldm2_____main__.py
```py

```

### FILE: temp___audioldm2___audiomae_gen___sequence_input.py
```py

```

### FILE: temp___audioldm2___audiomae_gen___utils.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___factory.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___feature_fusion.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___htsat.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___loss.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___model.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___openai.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___pann_model.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___pretrained.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___timm_model.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___tokenizer.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___transform.py
```py

```

### FILE: temp___audioldm2___clap___open_clip___utils.py
```py

```

### FILE: temp___audioldm2___clap___training___data.py
```py

```

### FILE: temp___audioldm2___clap___training___params.py
```py

```

### FILE: temp___audioldm2___hifigan___models.py
```py

```

### FILE: temp___audioldm2___hifigan___models_v2.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___util.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___models___ddim.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___models___ddpm.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___models___plms.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___attention.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___ema.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___AudioMAE.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___models_mae.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___models_vit.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___crop.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___datasets.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___lars.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___lr_decay.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___lr_sched.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___misc.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___patch_embed.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___pos_embed.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___audiomae___util___stat.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___diffusionmodules___model.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___diffusionmodules___openaimodel.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___diffusionmodules___util.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___distributions___distributions.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___encoders___modules.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___phoneme_encoder___attentions.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___phoneme_encoder___commons.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___phoneme_encoder___encoder.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___phoneme_encoder___text___cleaners.py
```py

```

### FILE: temp___audioldm2___latent_diffusion___modules___phoneme_encoder___text___symbols.py
```py

```

### FILE: temp___audioldm2___utilities___model.py
```py

```

### FILE: temp___audioldm2___utilities___sampler.py
```py

```

### FILE: temp___audioldm2___utilities___tools.py
```py

```

### FILE: temp___audioldm2___utilities___audio___audio_processing.py
```py

```

### FILE: temp___audioldm2___utilities___audio___stft.py
```py

```

### FILE: temp___audioldm2___utilities___audio___tools.py
```py

```

### FILE: temp___audioldm2___utilities___data___add_on.py
```py

```

### FILE: temp___audioldm2___utilities___data___dataset.py
```py

```

### FILE: temp___config___16k_64.yaml
```yaml

```

### FILE: temp___config___example.txt
```txt

```

### FILE: temp___generations___generationsShowUpHere.txt
```txt

```

### FILE: temp___models___modelsgohere.txt
```txt

```

### FILE: temp___modules___autoencoder.py
```py

```

### FILE: temp___modules___conditioner.py
```py

```

### FILE: temp___modules___layers.py
```py

```

