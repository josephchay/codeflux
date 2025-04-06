# Codebundle - Unravel Your Codebase

**Codebundle** can be used for organizing large codebases, consolidating scripts, optimizations, or 
preparing for migration or backup.

## Overview

Do you often find yourself digging through multiple nested directories to find files?
**Codebundle** is a CLI tool that scans through your source directory (and all its subdirectories), 
processes files in multiple ways (flattening, restructuring, bundling, minifying), and organizes everything into 
timestamped outputs for easy reference. It automatically handles file conflicts and supports powerful filtering options 
to process exactly what you need.

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
| JSON             | `.json`, `.jsonl`, `.geojson`, `.json5`, `.ndjson`                          |

_More extensions to be added in the future._

---

## Installation

> [!WARNING]
> Uninstall the package (If you have already installed a previous version of the package):

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
> Occasionally, check on the `staging` and `develop` branches for new features or bug fixes not yet been merged into the 
> `main` branch.

## Command-Line Arguments

| Argument               | Shorthand | Default                                              | Description                                                                                                                                                                                  |
|------------------------|-----------|------------------------------------------------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `[src]`                | `-s`      | Current directory                                    | Source directory containing the files to flatten                                                                                                                                             |
| `[dest]`               | `-d`      | Based on operation (see below)                       | Destination directory/file where files will be copied                                                                                                                                        |
| `--file-types`         | `-t`      | `py`, `ipynb`, `jsts`, `md`, `yaml`, `shell`, `json` | File types to process: 'py' for Python, 'ipynb' for Python Notebooks, 'jsts' for JavaScript/TypeScript, 'md' for Markdown, 'yaml' for YAML, 'shell' for Shell Scripts, 'json' for JSON files |
| **Operations**         |           |                                                      |                                                                                                                                                                                              |
| `--flatten`            | `-f`      | True (if no other operation specified)               | Flatten the directory structure                                                                                                                                                              |
| `--deflatten`          | `-df`     | False                                                | Deflatten the directory (restore original structure)                                                                                                                                         |
| `--bundle`             | `-b`      | False                                                | Bundle files into a single text file                                                                                                                                                         |
| `--minify`             | `-m`      | False                                                | Create a minified copy of the directory while preserving structure                                                                                                                           |
| `--minify-bundle`      | `-mb`     | False                                                | Minify files and bundle them into a single text file                                                                                                                                         |
| **Exclusion Options**  |           |                                                      |                                                                                                                                                                                              |
| `--exclude-dirs`       | `-xd`     | Various default directories                          | Directory names to exclude                                                                                                                                                                   |
| `--exclude-extensions` | `-xe`     | Various default extensions                           | File extensions to exclude                                                                                                                                                                   |
| `--exclude-files`      | `-xf`     | Various common files                                 | Specific filenames to exclude (e.g., setup.py, jest.config.js)                                                                                                                               |
| **Inclusion Options**  |           |                                                      |                                                                                                                                                                                              |
| `--include-dirs`       | `-id`     | None                                                 | Directory names to include (only these will be processed)                                                                                                                                    |
| `--include-extensions` | `-ie`     | None                                                 | File extensions to include (only these will be processed)                                                                                                                                    |
| `--include-files`      | `-if`     | None                                                 | Specific filenames to include (only these will be processed)                                                                                                                                 |
| **Defaults Handling**  |           |                                                      |                                                                                                                                                                                              |
| `--ignore-defaults`    | `-i`      | `False`                                              | Ignore all default exclusions and only use provided exclusions                                                                                                                               |
| **Other Options**      |           |                                                      |                                                                                                                                                                                              |
| `--clear-dest-dir`     | `-c`      | `False`                                              | Clear the destination directory before copying files                                                                                                                                         |
| `--no-log`             | `-nl`     | `False`                                              | Disable logging output                                                                                                                                                                       |

### Default Paths and Output Organization

* **Source directory**: If not specified, defaults to the current working directory
* **Base output directory**: A `codebundle` directory in the current working directory
* **Operation directories**: A single timestamped directory containing all operations executed in one run
* **Destination paths** (when running multiple operations in a single command):
  * `./codebundle/{timestamp}/flattened/` (for flatten operation)
  * `./codebundle/{timestamp}/deflattened/` (for deflatten operation)
  * `./codebundle/{timestamp}/bundled.txt` (for bundle operation)
  * `./codebundle/{timestamp}/minified/` (for minify operation)
  * `./codebundle/{timestamp}/minified_bundle.txt` (for minify-bundle operation)
  * `./codebundle/{timestamp}/operations_summary.txt` (summary of all operations performed)

For detailed information on default values, refer to the [constants](src/constants.py) file.

## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                            | Command                                                       | Description                                                                               |
|-------------------------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| Basic Flattening                    | `codebundle`                                                  | Flattens the current directory into a timestamped output directory                        |
| Multiple Operations                 | `codebundle -f -df -b`                                        | Performs flatten, deflatten and bundle operations in sequence                             |
| Process Specific Types              | `codebundle -t py ipynb shell`                                | Process only Python, Python Notebooks, and Shell Script files from current directory      |
| Bundle with Minification            | `codebundle -mb`                                              | Bundle the current directory with minified code                                           |
| Minify Python for Optimized Context | `codebundle -mb -t py -s src`                                 | Create a minified bundle of Python files from 'src' suitable for optimized context usages |
| Minify Directory                    | `codebundle -m`                                               | Create a minified copy of the current directory while preserving structure                |
| Minify Specific Project             | `codebundle -m -s src -t py -xd tests venv`                   | Create a minified copy of the src directory, excluding tests and venv directories         |
| Exclude Directories                 | `codebundle -xd .idea .venv`                                  | Flattens the current directory excluding the specified directories                        |
| Include Only Specific Directories   | `codebundle -id utils models`                                 | Only process files from the 'utils' and 'models' directories in the current folder        |
| Include Only Specific Extensions    | `codebundle -ie .py .sh`                                      | Only process files with '.py' and '.sh' extensions from the current directory             |
| Ignore Default Exclusions           | `codebundle -i`                                               | Flattens the current directory without applying default exclusions                        |
| Exclude File Extensions             | `codebundle -xe .txt .csv`                                    | Flattens the current directory excluding files with the specified extensions              |
| Exclude Specific Files              | `codebundle -xf setup.py package.json setup.sh`               | Flattens the current directory excluding the specified files                              |
| Include Only Specific Files         | `codebundle -if main.py analysis.ipynb deploy.sh`             | Processes only the specified files from the current directory                             |
| Minify Only Specific File Types     | `codebundle -m -ie .py .js`                                   | Create a minified copy with only Python and JavaScript files (Python files get minified)  |
| Complex Command with Shorthands     | `codebundle -t py shell -id utils -xf setup.py -i -c`         | Using multiple shorthands for a complex operation                                         |
| All Operations Together             | `codebundle -f -df -b -m -mb -s src -t py -ie .py -xd tests`  | Perform all operations on Python files from src directory, excluding tests                |
| Custom Output Paths                 | `codebundle -f -df -b -s src -d myoutput`                     | Custom destination path for all operations (creates timestamped subdirectories)           |
| Bundle for Team Review              | `codebundle -b -s project -ie .py .js -xd node_modules tests` | Create a bundle with only Python and JavaScript files, excluding tests and modules        |
| Project Migration                   | `codebundle -f -b -s legacy_project -d migration`             | Flatten and bundle a legacy project for migration, preserving both formats                |
| Optimized Context + Human Reference | `codebundle -b -mb`                                           | Create two bundles - one minified (for optimization) and one readable (for humans)        |

### Example Directory Transformations

#### Example 1: Basic Flattening
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

#### Example 11: Minify Operation

```
Before:                             After (Minified):                 
src/                                minified/                      
├── module1/                        ├── module1/                    
│   ├── script1.py                  │   ├── script1.py (minified)  
│   └── utils/                      │   └── utils/                 
│       └── helper.py               │       └── helper.py (minified)
├── module2/                        ├── module2/                    
│   ├── utils.js                    │   ├── utils.js               
│   └── data.ipynb                  │   └── data.ipynb             
└── docs/                           └── docs/                      
    └── README.md                       └── README.md              
```

Command:
```bash
codebundle --src src --minify
```
or
```bash
codebundle src -m
```

This operation creates a minified copy of the directory while preserving the original structure.

#### Example 12: Minify-Bundle Operation

```
Before:                            After (minified_bundle.txt):
src/                               =====================================
├── module1/                       BUNDLED FILES FROM: /path/to/src
│   ├── script1.py                 CREATED: 2025-04-04 15:30:45
│   └── utils/                     MINIFICATION: Enabled
│       └── helper.py              =====================================
└── module2/                       
    └── config.py                  ## PY FILES (3)
                                   
                                   `module1___script1.py`
                                   ```
                                   def main():return"Hello World!"
                                   if __name__=="__main__":main()
                                   ```
                                   
                                   `module1___utils___helper.py`
                                   ```
                                   def helper_function(x):return x*2
                                   ```
                                   
                                   `module2___config.py`
                                   ```
                                   DEBUG=False
                                   VERSION="1.0"
                                   ```
```

Command:
```bash
codebundle --src src --minify-bundle --file-types py
```
or
```bash
codebundle src -mb -t py
```

## Development

Clone the Repository:

```bash
git clone https://github.com/josephchay/codebundle.git
cd codebundle

# Install locally
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
