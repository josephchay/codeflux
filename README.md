# Codebundle - Unravel Your Codebase

_Effortlessly declutter and organize your project by flattening nested files into a single folder,
reconstruct the original directory structure from flattened files (deflattening), or bundle all files into a single document._

## Overview

Do you often find yourself digging through multiple nested directories to find files?
**Codebundle** is a CLI tool that scans through your source directory (and all its subdirectories), 
processes files in multiple ways (flattening, restructuring, bundling), and organizes everything into timestamped outputs for easy reference. 
It automatically handles file conflicts and supports powerful filtering options to process exactly what you need.

It's perfect for organizing large codebases, consolidating scripts, optimizations, or preparing for migration or backup.

### Supported File Types

| Language         | Extensions                                                                  |
|------------------|-----------------------------------------------------------------------------|
| Python           | `.py`                                                                       |
| Python Notebooks | `.ipynb`                                                                    |
| JavaScript       | `.js`, `.jsx`                                                               |
| TypeScript       | `.ts`, `.tsx`                                                               |
| Shell Scripts    | `.sh`, `.bash`, `.zsh`                                                      |
| Markdown         | `.md`, `.markdown`, `.mdown`, `.mkdn`, `.mkd`, `.mdwn`, `.mdtxt`, `.mdtext` |
| Plain Text       | `.txt`                                                                      |
| YAML             | `.yaml`, `.yml`                                                             |

_More extensions to be added in the future._

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

> [!NOTE]
> Occasionally, check on the `staging` and `develop`branch for  new features or bug fixes not yet been merged into the 
> `main` branch.

## Command-Line Arguments

| Argument                 | Shorthand | Default                                    | Description                                                                                                                                                           |
|--------------------------|-----------|--------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[src]`                  | `-s`      | Current directory                          | Source directory containing the files to flatten                                                                                                                      |
| `[dest]`                 | `-d`      | Based on operation (see below)             | Destination directory/file where files will be copied                                                                                                                 |
| `--file-types`           | `-t`      | `py`, `ipynb`, `js`, `md`, `yaml`, `shell` | File types to process: 'py' for Python, 'ipynb' for Python Notebooks, 'jsts' for JavaScript/TypeScript, 'md' for Markdown, 'yaml' for YAML, 'shell' for Shell Scripts |
| **Operations**           |           |                                            |                                                                                                                                                                       |
| `--flatten`              | `-f`      | True (if no other operation specified)     | Flatten the directory structure                                                                                                                                       |
| `--deflatten`            | `-df`     | False                                      | Deflatten the directory (restore original structure)                                                                                                                  |
| `--bundle`               | `-b`      | False                                      | Bundle files into a single text file                                                                                                                                  |
| **Exclusion Options**    |           |                                            |                                                                                                                                                                       |
| `--exclude-dirs`         | `-xd`     | Various default directories                | Directory names to exclude                                                                                                                                            |
| `--exclude-extensions`   | `-xe`     | Various default extensions                 | File extensions to exclude                                                                                                                                            |
| `--exclude-files`        | `-xf`     | Various common files                       | Specific filenames to exclude (e.g., setup.py, jest.config.js)                                                                                                        |
| **Inclusion Options**    |           |                                            |                                                                                                                                                                       |
| `--include-dirs`         | `-id`     | None                                       | Directory names to include (only these will be processed)                                                                                                             |
| `--include-extensions`   | `-ie`     | None                                       | File extensions to include (only these will be processed)                                                                                                             |
| `--include-files`        | `-if`     | None                                       | Specific filenames to include (only these will be processed)                                                                                                          |
| **Minification Options** |           |                                            |                                                                                                                                                                       |
| `--minify`               | `-m`      | `False`                                    | Minify Python code when bundling (using python-minifier)                                                                                                              |
| **Defaults Handling**    |           |                                            |                                                                                                                                                                       |
| `--ignore-defaults`      | `-i`      | `False`                                    | Ignore all default exclusions and only use provided exclusions                                                                                                        |
| **Other Options**        |           |                                            |                                                                                                                                                                       |
| `--clear-dest-dir`       | `-c`      | `False`                                    | Clear the destination directory before copying files                                                                                                                  |
| `--no-log`               | `-nl`     | `False`                                    | Disable logging output                                                                                                                                                |

### Default Paths and Output Organization

* **Source directory**: If not specified, defaults to the current working directory
* **Destination paths**:
  * For `flatten`: `./codebundle_YYYYMMDD_HHMMSS/flattened/`
  * For `deflatten`: `./codebundle_YYYYMMDD_HHMMSS/deflattened/`
  * For `bundle`: `./codebundle_YYYYMMDD_HHMMSS/bundled.txt`
  * If custom destination paths are provided, they're used as specified

For detailed information on default values, refer to the [constants](src/constants.py) file.

## Usage Examples

Here are various scenarios and how to use the tool:
## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                            | Command                                                       | Description                                                                                        |
|-------------------------------------|---------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| Basic Flattening                    | `codebundle`                                                  | Flattens the current directory into a timestamped output directory                                 |
| Multiple Operations                 | `codebundle -f -df -b`                                        | Performs flatten, deflatten and bundle operations in sequence                                      |
| Process Specific Types              | `codebundle -t py ipynb shell`                                | Process only Python, Python Notebooks, and Shell Script files from current directory               |
| Bundle with Minification            | `codebundle -b -m`                                            | Bundle the current directory with minified Python code                                             |
| Minify Python for Optimized Context | `codebundle -b -m -t py -s src`                               | Create a minified bundle of Python files from 'src' suitable for optimized context usages          |
| Exclude Directories                 | `codebundle -xd .idea .venv`                                  | Flattens the current directory excluding the specified directories                                 |
| Include Only Specific Directories   | `codebundle -id utils models`                                 | Only process files from the 'utils' and 'models' directories in the current folder                 |
| Include Only Specific Extensions    | `codebundle -ie .py .sh`                                      | Only process files with '.py' and '.sh' extensions from the current directory                      |
| Ignore Default Exclusions           | `codebundle -i`                                               | Flattens the current directory without applying default exclusions                                 |
| Exclude File Extensions             | `codebundle -xe .txt .csv`                                    | Flattens the current directory excluding files with the specified extensions                       |
| Exclude Specific Files              | `codebundle -xf setup.py package.json setup.sh`               | Flattens the current directory excluding the specified files                                       |
| Include Only Specific Files         | `codebundle -if main.py analysis.ipynb deploy.sh`             | Processes only the specified files from the current directory                                      |
| Bundle for Optimized Context        | `codebundle -b -m -ie .py`                                    | Create a minified bundle of Python files from the current directory                                |
| Complex Command with Shorthands     | `codebundle -t py shell -id utils -xf setup.py -i -c`         | Using multiple shorthands for a complex operation                                                  |
| All Operations Together             | `codebundle -f -df -b -m -s src -t py -ie .py -xd tests`      | Flatten, deflatten, and bundle Python files from src directory, excluding tests, with minification |
| Custom Output Paths                 | `codebundle -f -df -b -s src -d myoutput`                     | Custom destination path for all operations (creates timestamped subdirectories)                    |
| Bundle for Team Review              | `codebundle -b -s project -ie .py .js -xd node_modules tests` | Create a bundle with only Python and JavaScript files, excluding tests and modules                 |
| Project Migration                   | `codebundle -f -b -s legacy_project -d migration`             | Flatten and bundle a legacy project for migration, preserving both formats                         |
| Optimized Context + Human Reference | `codebundle -b -m -b`                                         | Create two bundles - one minified (for optimization) and one readable (for humans)                 |
| Timestamped Outputs                 | `codebundle`                                                  | Creates a timestamped directory (e.g., codebundle_20250403_123045) for all outputs                 |
| Flatten for Different Project       | `codebundle -f -s project1 -f -s project2`                    | Process multiple source directories in separate timestamped outputs                                |
| Quick Environment Setup             | `codebundle -f -s modules -id core utils -df -s config`       | Flatten core modules and deflatten configuration files in one command                              |

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
