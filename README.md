# Codebundle - Unravel Your Codebase

_Effortlessly declutter and organize your project by flattening nested files into a single folder,
reconstruct the original directory structure from flattened files, or bundle all files into a single text document._

> [!NOTE]
> _Currently only supports .py, .js, .ts, .jsx, .tsx file extensions._

## Overview

Do you often find yourself digging through multiple nested directories to find files?  
**Codebundle** is here to simplify your life! This lightweight CLI tool scans through your source directory (and all its subdirectories), 
collects all designated files and copies them into a single destination directory - all while automatically renaming conflicting files. 

It's perfect for organizing large codebases, consolidating scripts, or preparing for migration or backup.

---

## Features

- **Flattens Nested Directories**: Gathers all required files into a single folder, no matter how deeply nested they are.
- **Exclude Options**: Allows excluding specific directories and file extensions from the process.
- **Handles File Name Conflicts**: Renames files with duplicate names to ensure no overwriting.
- **Clean Destination Directory**: Automatically clears the destination folder before copying.
- **Command-Line Simplicity**: Provides an easy-to-use CLI interface.
- **Directory Path Preservation**: Option to prefix files with their original directory structure.
- **Exclude Specific Directories**: Allows excluding certain directories from the flattening process.
- **Exclude Specific File Extensions**: Allows excluding files with certain extensions.
- **Deflatten Functionality**: Provides the ability to revert the flattening process and restore the original directory structure.
- **Bundle Functionality**: Packs all files into a single text file while preserving path information.

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

| Argument               | Required | Default                                                        | Description                                                                     |
|------------------------|----------|----------------------------------------------------------------|---------------------------------------------------------------------------------|
| `[src]`                | Yes      | -                                                              | Source directory containing the Python files to flatten                         |
| `[dest]`               | Yes      | -                                                              | Destination directory/file where files will be copied                           |
| `--filetypes`          | No       | `.py`, `.js`, `.ts`, `.jsx`, `.tsx`                            | File extensions types to process                                                |
| `--exclude-dirs`       | No       | `["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv"]` | Directory names to exclude (default: `DEFAULT_EXCLUDE_DIRS`)                    |
| `--exclude-extensions` | No       | `[".pyc", ".pyo", "__init__.py"]`                              | File extensions to exclude (default: `DEFAULT_EXCLUDE_EXTENSIONS`)              |
| `--clear-dest-dir`     | No       | `False`                                                        | Clear the destination directory before copying files                            |
| `--deflatten`          | No       | `False`                                                        | Deflatten the directory instead of flattening (reverses the flattening process) |
| `--pack`               | No       | `False`                                                        | Pack all files into a single text file with path information                    |
| `--no-log`             | No       | `False`                                                        | Disable logging output                                                          |

## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                | Command                                                           | Description                                                                                               |
|-------------------------|-------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Basic Flattening        | `codebundle --src src --dest flat`                                | Flattens all `.py` files (except `__init__.py`) into the 'flat' directory                                 |
| Exclude Directories     | `codebundle --src src --dest flat --exclude-dirs .idea .venv`     | Excludes the `.idea` and `.venv` directories from the flattening process                                  |
| Exclude File Extensions | `codebundle --src src --dest flat --exclude-extensions .txt .csv` | Excludes files with `.txt` and `.csv` extensions from the flattening process                              |
| Deflatten Directory     | `codebundle --src flattened --dest original --deflatten`          | Reverts the flattening process and restores the original directory structure from the flattened directory |
| Pack Files              | `codebundle --src src --dest packed.txt --pack`                   | Packs all files into a single text file with clear file separators and path information                   |
| Disable Logging         | `codebundle --src src --dest flat --no-log`                       | Suppresses all the logging output                                                                         |
| Specifying file types   | `codebundle -src src --dest flat --filetypes py`                  | Selects only the given file types to flatten or deflatten                                                 |

### Example Directory Transformations

#### Example 1: Basic Flattening
```
Before:                             After:
src/                               flat/
├── module1/                       ├── module1___script1.py
│   ├── script1.py                 ├── module1___utils___helper.py
│   ├── __init__.py                └── module2___script2.py
│   └── utils/
│       └── helper.py
└── module2/
    └── script2.py
```

Command: 
```bash
codebundle --src src --dest flat
```
or without explicitly specifying the first two arguments:
```bash
codebundle src flat
```

#### Example 2: With Directory Prefixes

```
Before:                             After:
src/                               flat/
├── auth/                          ├── auth___login.py
│   ├── login.py                   ├── auth___utils___validator.py
│   └── utils/                     ├── models___user.py
│       └── validator.py           └── models___data___schema.py
└── models/
    ├── user.py
    └── data/
        └── schema.py
```

Command:
```bash
codebundle --src src --dest flat
```

#### Example 3: Excluding Directories and File Extensions

```
Before:                            After (Currently only supports python files):
src/                               flat/
├── .idea/                         ├── module1___script1.py
├── .git/                          └── module2___script2.py
├── __pycache__/                   
├── .venv/                         
├── docs/                          
│   └── README.md                  
├── tests/                         
│   ├── test_script1.py            
│   └── test_script2.py            
├── module1/                       
│   ├── script1.py                 
│   ├── __init__.py                
│   └── utils/                     
│       └── helper.pyc             
└── module2/                       
    ├── script2.py                 
    └── data/                      
        ├── input.csv              
        └── output.json            
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
├── module1___script.py            ├── module/
├── module1___utils___helper.py    │   ├── script.py
├── module2___script_2.py          │   └── utils/
└── module2___data___schema.py     │       └── helper.py
                                   └── module2/
                                       ├── script_2.py
                                       └── data/
                                           └── schema.py
```

Command:
```bash
codebundle --src flat --dest original --deflatten
```

#### Example 5: Packing Files into a Single Text File

Before:
```
src/
├── module1/
│   ├── script1.py
│   └── utils/
│       └── helper.py
└── module2/
    └── script2.py
```

After (packed.txt):
```
================================================================================
PACKED FILES FROM: /path/to/src
CREATED: 2025-03-31 10:15:30
================================================================================

================================================================================
FILE: module1___script1.py
================================================================================

# Content of script1.py

================================================================================
FILE: module1___utils___helper.py
================================================================================

# Content of helper.py

================================================================================
FILE: module2___script2.py
================================================================================

# Content of script2.py

================================================================================
END OF PACKED FILES (3 files)
================================================================================
```

Command:
```bash
codebundle --src src --dest packed.txt --pack
```

#### Example 6: Flattening with Duplicated Filenames

```
Before (Third Flattening with modified files):           After (Third Flatten):
src/                                                     flat/
├── utils/                                               ├── utils___helper.py
│   └── helper.py                                        ├── models___user.py
├── auth/                                                ├── data___schema.py
│   └── utils/                                           ├── utils___helper_2.py
│       └── helper.py                                    ├── models___user_2.py
├── models/                                              ├── data___schema_2.py
│   └── user.py                                          ├── utils___helper_3.py
└── data/                                                ├── models___user_3.py
    └── schema.py                                        └── data___schema_3.py
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

To pack all files, run:
```bash
codebundle --src . --dest project_packed.txt --pack
```

All the samples above apply the same for files with other extensions.

### Specifying File Extensions

Without using the `--filetypes` flag, all files will be flattened.

To specify only JS/TS/JSX/TSX file extensions to flatten, use the `--filetypes` flag:
```bash
codebundle src flat --filetypes js
```
or only for Python files:
```bash
codebundle src flat --filetypes py
```

The same applies to packing:
```bash
codebundle src packed.txt --pack --filetypes py
```

### Logging

To suppress logging output, add the `--no-log` flag:
```bash
codebundle --src src --dest flat --no-log
```

## Development

Clone the Repository:

```bash
git clone https://github.com/josephchay/codebundle.git
cd codebundle
```

Install Locally:

```bash
pip install .
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

Make your projects cleaner - flatten, deflatten, or pack your directories today!
