# Codepeek - Unravel Your Codebase

_Effortlessly declutter and organize your project by flattening nested `.py` files into a single folder or
reconstructing the original directory structure from flattened files._

> [!NOTE] 
> _Currently only supports python files._

## Overview

Do you often find yourself digging through multiple nested directories to find Python files?  
**Codepeek** is here to simplify your life! This lightweight CLI tool scans through your source directory (and all its subdirectories), collects all `.py` files (excluding `__init__.py`), and copies them into a single destination directory — all while automatically renaming conflicting files. 

It's perfect for organizing large codebases, consolidating scripts, or preparing for migration or backup.

---

## Features
- **Flattens Nested Directories**: Gathers all `.py` files into a single folder, no matter how deeply nested they are.
- **Excludes `__init__.py`**: Avoids copying module definition files (`__init__.py`) by default.
- **Handles File Name Conflicts**: Renames files with duplicate names to ensure no overwriting.
- **Clean Destination Directory**: Automatically clears the destination folder before copying.
- **Command-Line Simplicity**: Provides an easy-to-use CLI interface.
- **Directory Path Preservation**: Option to prefix files with their original directory structure.
- **Exclude Specific Directories**: Allows excluding certain directories from the flattening process.
- **Exclude Specific File Extensions**: Allows excluding files with certain extensions.
- **Deflatten Functionality**: Provides the ability to revert the flattening process and restore the original directory structure.

---

## Installation

> [!WARNING]
> Uninstall the Package (If you have already installed a previous version of the package):
> ```bash
> pip uninstall codepeek
> ```

Install the package from source:

```bash
pip install git+https://github.com/josephchay/codepeek.git
```

## Command-Line Arguments

| Argument               | Required | Default                                                        | Description                                                                     |
|------------------------|----------|----------------------------------------------------------------|---------------------------------------------------------------------------------|
| `[src]`                | Yes      | -                                                              | Source directory containing the Python files to flatten                         |
| `[dest]`               | Yes      | -                                                              | Destination directory where files will be copied                                |
| `--exclude-dirs`       | No       | `["__pycache__", ".git", ".idea", ".vscode", ".venv", "venv"]` | Directory names to exclude (default: `DEFAULT_EXCLUDE_DIRS`)                    |
| `--exclude-extensions` | No       | `[".pyc", ".pyo", "__init__.py"]`                              | File extensions to exclude (default: `DEFAULT_EXCLUDE_EXTENSIONS`)              |
| `--clear-dest-dir`     | No       | `False`                                                        | Clear the destination directory before copying files                            |
| `--deflatten`          | No       | `False`                                                        | Deflatten the directory instead of flattening (reverses the flattening process) |

## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                | Command                                                         | Description                                                                                               |
|-------------------------|-----------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Basic Flattening        | `codepeek --src src --dest flat`                                | Flattens all `.py` files (except `__init__.py`) into the 'flat' directory                                 |
| Exclude Directories     | `codepeek --src src --dest flat --exclude-dirs .idea .venv`     | Excludes the `.idea` and `.venv` directories from the flattening process                                  |
| Exclude File Extensions | `codepeek --src src --dest flat --exclude-extensions .txt .csv` | Excludes files with `.txt` and `.csv` extensions from the flattening process                              |
| Deflatten Directory     | `codepeek --src flattened --dest original --deflatten`          | Reverts the flattening process and restores the original directory structure from the flattened directory |

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
codepeek --src src --dest flat
```
or
```bash
# First two arguments can be src and dest without flags
codepeek src flat
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
codepeek --src src --dest flat
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
codepeek --src src --dest flat --exclude-dirs .idea .git __pycache__ .venv docs tests --exclude-extensions .md .pyc .csv .json
```
or
```bash
codepeek src flat --exclude-dirs .idea .git __pycache__ .venv docs tests --exclude-extensions .md .pyc .csv .json
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
codepeek --src flat --dest original --deflatten
```

#### Example 5: Flattening with Duplicated Filenames
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
codepeek --src src --dest flat
```

You can also flatten
```bash
codepeek --src . --dest flat
```
or
```bash
codepeek --src flat --dest .
```
or
```bash
codepeek . flat
```

To deflatten the directory, run:
```bash
codepeek --src . --dest . --deflatten
```

## Development

Clone the Repository:

```bash
git clone https://github.com/josephchay/codepeek.git
cd codepeek
```

Install Locally:

```bash
pip install .
```

Run Tests:
To test functionality during development, you can run:

```bash
python -m src.main --src <source_dir> --dest <dest_dir>
```

## Contributing
Contributions are welcome! If you'd like to report a bug, suggest a feature, or submit a PR:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m "Description of changes"`).
4. Push your branch and open a PR.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Support
Need help? Have a question? Feel free to reach out:
* **Email**: [josephemmanuelchay@gmail.com](mailto:josephemmanuelchay@gmail.com)
* **GitHub Issues**: [Issues](https://github.com/josephchay/codepeek/issues)

Make your projects cleaner — flatten and deflatten your directories today!
