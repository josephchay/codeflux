# Codebundle - Unravel Your Codebase

_Effortlessly declutter and organize your project by flattening nested files into a single folder,
reconstruct the original directory structure from flattened files, or bundle all files into a single text document._

## Overview

Do you often find yourself digging through multiple nested directories to find files?
**Codebundle** is here to simplify your life! This lightweight CLI tool scans through your source directory (and all its subdirectories), 
collects all designated files and copies them into a single destination directory - all while automatically renaming conflicting files. 

It's perfect for organizing large codebases, consolidating scripts, or preparing for migration or backup.

### Supported File Types

| Language   | Extensions                                                                  |
|------------|-----------------------------------------------------------------------------|
| Python     | `.py`                                                                       |
| JavaScript | `.js`, `.jsx`                                                               |
| TypeScript | `.ts`, `.tsx`                                                               |
| Markdown   | `.md`, `.markdown`, `.mdown`, `.mkdn`, `.mkd`, `.mdwn`, `.mdtxt`, `.mdtext` |
| Plain Text | `.txt`                                                                      |

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
- **Include Specific Files**: Allows processing only specific files by name (new feature!).
- **Deflatten Functionality**: Provides the ability to revert the flattening process and restore the original directory structure.
- **Bundle Functionality**: Bundles all files into a single text file while preserving path information.
- **Markdown Support**: Now handles Markdown (.md) and text files alongside code files.

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

### Current Development

Occasionally, check on the `staging` branch, as they may be some new features or bug fixes 
that have not been merged into the `main` branch.

```bash
pip install git+https://github.com/josephchay/codebundle.git@staging
```
or
```bash
pip install git+https://github.com/josephchay/codebundle.git@test/functionality/main
```

## Command-Line Arguments

| Argument               | Required | Default                     | Description                                                                               |
|------------------------|----------|-----------------------------|-------------------------------------------------------------------------------------------|
| `[src]`                | Yes      | -                           | Source directory containing the files to flatten                                          |
| `[dest]`               | Yes      | -                           | Destination directory/file where files will be copied                                     |
| `--file-types`         | No       | `py`, `js`, `md`            | File types to process: 'py' for Python, 'js' for JavaScript/TypeScript, 'md' for Markdown |
| `--exclude-dirs`       | No       | Various default directories | Directory names to exclude                                                                |
| `--exclude-extensions` | No       | Various default extensions  | File extensions to exclude                                                                |
| `--exclude-files`      | No       | Various common files        | Specific filenames to exclude (e.g., setup.py, jest.config.js)                            |
| `--include-files`      | No       | None                        | Specific filenames to include (only these will be processed)                              |
| `--clear-dest-dir`     | No       | `False`                     | Clear the destination directory before copying files                                      |
| `--deflatten`          | No       | `False`                     | Deflatten the directory instead of flattening (reverses the flattening process)           |
| `--bundle`             | No       | `False`                     | Bundle all files into a single text file with path information                            |
| `--no-log`             | No       | `False`                     | Disable logging output                                                                    |

## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                    | Command                                                                                       | Description                                                                                               |
|-----------------------------|-----------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------|
| Basic Flattening            | `codebundle --src src --dest flat`                                                            | Flattens all Python, JavaScript, and Markdown files into the 'flat' directory                             |
| Exclude Directories         | `codebundle --src src --dest flat --exclude-dirs .idea .venv`                                 | Excludes the `.idea` and `.venv` directories from the flattening process                                  |
| Exclude File Extensions     | `codebundle --src src --dest flat --exclude-extensions .txt .csv`                             | Excludes files with `.txt` and `.csv` extensions from the flattening process                              |
| Exclude Specific Files      | `codebundle --src src --dest flat --exclude-files setup.py package.json`                      | Excludes specific files like setup.py and package.json from the flattening process                        |
| Include Only Specific Files | `codebundle --src src --dest flat --include-files main.py index.js README.md`                 | Processes only the specified files, ignoring all others                                                   |
| Deflatten Directory         | `codebundle --src flattened --dest original --deflatten`                                      | Reverts the flattening process and restores the original directory structure from the flattened directory |
| Bundle Files                | `codebundle --src src --dest bundled.txt --bundle`                                            | Bundles all files into a single text file with clear file separators and path information                 |
| Bundle Only Specific Files  | `codebundle --src src --dest bundle.txt --bundle --include-files config.py app.js`            | Bundles only the specified files into a single text file                                                  |
| Combine Exclusions          | `codebundle --src src --dest flat --exclude-dirs node_modules --exclude-files .env config.js` | Uses multiple exclusion types together                                                                    |

### Example Directory Transformations

#### Example 1: Basic Flattening
```
Before:                             After:
src/                               flat/
├── module1/                       ├── py/
│   ├── script1.py                 │   ├── module1___script1.py
│   ├── __init__.py                │   └── module1___utils___helper.py
│   └── utils/                     ├── jsts/
│       └── helper.py              │   └── module2___script2.js
└── module2/                       └── md/
    └── script2.js                     └── README.md
```

Command: 
```bash
codebundle --src src --dest flat
```

#### Example 2: Excluding Specific Files

```
Before:                            After:
src/                               flat/
├── module1/                       ├── py/
│   ├── script1.py                 │   └── module1___utils___helper.py
│   ├── setup.py                   ├── jsts/
│   └── utils/                     │   └── module2___utils.js
│       └── helper.py              └── md/
└── module2/                           └── GUIDE.md
    ├── utils.js
    ├── config.js
    └── docs/
        ├── README.md
        └── GUIDE.md
```

Command:
```bash
codebundle --src src --dest flat --exclude-files setup.py config.js README.md
```

#### Example 3: Including Only Specific Files

```
Before:                            After:
src/                               flat/
├── module1/                       ├── py/
│   ├── script1.py                 │   └── module1___script1.py
│   ├── setup.py                   └── md/
│   └── utils/                         └── docs___README.md
│       └── helper.py              
└── module2/                       
    ├── utils.js                   
    ├── config.js                  
    └── docs/                      
        ├── README.md              
        └── GUIDE.md               
```

Command:
```bash
codebundle --src src --dest flat --include-files script1.py README.md
```

#### Example 4: Bundling With Include Files

```
Before:                            After (bundled.txt):
src/                               =====================================
├── module1/                       BUNDLED FILES FROM: /path/to/src
│   ├── script1.py                 CREATED: 2025-03-31 12:15:30
│   ├── setup.py                   =====================================
│   └── utils/
│       └── helper.py              =====================================
└── module2/                       FILE: module1___script1.py
    ├── utils.js                   =====================================
    ├── main.js                    # Content of script1.py
    └── config.js                  
                                   =====================================
                                   FILE: module2___main.js
                                   =====================================
                                   // Content of main.js
                                   
                                   =====================================
                                   END OF BUNDLED FILES (2 files)
                                   =====================================
```

Command:
```bash
codebundle --src src --dest bundled.txt --bundle --include-files script1.py main.js
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

Make your projects cleaner - flatten, deflatten, or bundle your directories today!
