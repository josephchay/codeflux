# Codebundle - Unravel Your Codebase

**Codebundle** can be used for organizing large codebases, consolidating scripts, optimizations, or 
preparing for migration or backup.

## Overview

Tired of wading through tangled directory trees just to make sense of a codebase? 
**Codebundle** is a powerful CLI tool that brings structure, clarity, and control to any source directory. 
It intelligently flattens or reconstructs file hierarchies, bundles and minifies code, 
performs search functionalities across files, and delivers timestamped outputs. 
With robust filtering and deep code insight features, **Codebundle** transforms messy projects into manageable, transparent systems.

### Supported File Types

| Language          | Extensions                                                                  |
|-------------------|-----------------------------------------------------------------------------|
| Python            | `.py`                                                                       |
| Python Notebooks  | `.ipynb`                                                                    |
| JavaScript        | `.js`, `.jsx`                                                               |
| TypeScript        | `.ts`, `.tsx`                                                               |
| Shell Scripts     | `.sh`, `.bash`, `.zsh`                                                      |
| Markdown          | `.md`, `.markdown`, `.mdown`, `.mkdn`, `.mkd`, `.mdwn`, `.mdtxt`, `.mdtext` |
| Plain Text        | `.txt`                                                                      |
| YAML              | `.yaml`, `.yml`                                                             |
| JSON              | `.json`, `.jsonl`, `.geojson`, `.json5`, `.ndjson`                          |
| GO                | `.go`, `.mod`, `.sum`, `.pb.go`, `.tmpl`, `.tpl`                            |
| INI Configuration | `.ini`, `.cfg`, `.conf`, `.properties`                                      |
| Database Scripts  | `.sql`, `.ddl`, `.dml`                                                      |
| Batch Scripts     | `.bat`, `.cmd`, `.btm`                                                      |
| Custom Scripts    | `.scp`, `.script`                                                           |

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

| Argument               | Shorthand | Default                                                                                 | Description                                                                                        |
|------------------------|-----------|-----------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `[src]`                | `-s`      | Current directory                                                                       | Source directory containing the files to flatten                                                   |
| `[dest]`               | `-d`      | Based on operation (see below)                                                          | Destination directory/file where files will be copied                                              |
| `--file-types`         | `-t`      | `py`, `ipynb`, `jsts`, `mdtxt`, `yml`, `shell`, `json`, `go`, `ini`, `db`, `bat`, `scp` | File types to process (default: all)                                                               |
| **Operations**         |           |                                                                                         |                                                                                                    |
| `--flatten`            | `-f`      | `True` (if no other operation specified)                                                | Flatten the directory structure                                                                    |
| `--deflatten`          | `-df`     | `True` (if no other operation specified)                                                | Deflatten the directory (restore original structure)                                               |
| `--bundle`             | `-b`      | `True` (if no other operation specified)                                                | Bundle files into a single text file                                                               |
| `--minify`             | `-m`      | `True` (if no other operation specified)                                                | Create a minified copy of the directory while preserving structure                                 |
| `--minify-bundle`      | `-mb`     | `True` (if no other operation specified)                                                | Minify files and bundle them into a single text file                                               |
| **Exclusion Options**  |           |                                                                                         |                                                                                                    |
| `--exclude-dirs`       | `-xd`     | Various default directories                                                             | Directory names to exclude                                                                         |
| `--exclude-extensions` | `-xe`     | Various default extensions                                                              | File extensions to exclude                                                                         |
| `--exclude-files`      | `-xf`     | Various path-based files                                                                | Specific file paths to exclude (requires full path relative to source dir, e.g. 'path/to/file.py') |
| **Inclusion Options**  |           |                                                                                         |                                                                                                    |
| `--include-dirs`       | `-id`     | `None`                                                                                  | Directory names to include (only these will be processed)                                          |
| `--include-extensions` | `-ie`     | `None`                                                                                  | File extensions to include (only these will be processed)                                          |
| `--include-files`      | `-if`     | `None`                                                                                  | Specific filenames to include (only these will be processed)                                       |
| **Defaults Handling**  |           |                                                                                         |                                                                                                    |
| `--ignore-defaults`    | `-i`      | `False`                                                                                 | Ignore all default exclusions and only use provided exclusions                                     |
| **Search Options**     |           |                                                                                         |                                                                                                    |
| `--search-ext`         | `-se`     | `None`                                                                                  | Search for files with specific extensions                                                          |
| `--search-pattern`     | `-sp`     | `None`                                                                                  | Search for files containing a specific regex pattern                                               |
| `--search-size`        | `-ss`     | `None`                                                                                  | Search for files within a size range (in KB, use 'none' for no limit)                              |
| `--search-date`        | `-sd`     | `None`                                                                                  | Search for files modified between dates (YYYY-MM-DD format)                                        |
| `--search-imports`     | `-si`     | `None`                                                                                  | Search for files that import a specific module                                                     |
| `--search-duplicates`  | `-sdu`    | `None`                                                                                  | Search for duplicate code blocks (with optional minimum line threshold)                            |
| **Other Options**      |           |                                                                                         |                                                                                                    |
| `--clear-dest-dir`     | `-c`      | `False`                                                                                 | Clear the destination directory before copying files                                               |
| `--no-log`             | `-nl`     | `False`                                                                                 | Disable logging output                                                                             |

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

| Scenario                                | Command                                                       | Description                                                                               |
|-----------------------------------------|---------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| All Operations                          | `codebundle`                                                  | Performs all operations onto the current directory into a timestamped output directory    |
| Multiple Operations                     | `codebundle -f -df -b`                                        | Performs flatten, deflatten and bundle operations in sequence                             |
| Process Specific Types                  | `codebundle -t py ipynb shell`                                | Process only Python, Python Notebooks, and Shell Script files from current directory      |
| Bundle with Minification                | `codebundle -mb`                                              | Bundle the current directory with minified code                                           |
| Minify Python for Optimized Context     | `codebundle -mb -t py -s src`                                 | Create a minified bundle of Python files from 'src' suitable for optimized context usages |
| Minify Directory                        | `codebundle -m`                                               | Create a minified copy of the current directory while preserving structure                |
| Minify Specific Project                 | `codebundle -m -s src -t py -xd tests venv`                   | Create a minified copy of the src directory, excluding tests and venv directories         |
| Exclude Directories                     | `codebundle -xd .idea .venv`                                  | Flattens the current directory excluding the specified directories                        |
| Include Only Specific Directories       | `codebundle -id utils models`                                 | Only process files from the 'utils' and 'models' directories in the current folder        |
| Include Only Specific Extensions        | `codebundle -ie .py .sh`                                      | Only process files with '.py' and '.sh' extensions from the current directory             |
| Ignore Default Exclusions               | `codebundle -i`                                               | Flattens the current directory without applying default exclusions                        |
| Exclude File Extensions                 | `codebundle -xe .txt .csv`                                    | Flattens the current directory excluding files with the specified extensions              |
| Exclude Specific Files                  | `codebundle -xf setup.py package.json setup.sh`               | Flattens the current directory excluding the specified files                              |
| Include Only Specific Files             | `codebundle -if main.py analysis.ipynb deploy.sh`             | Processes only the specified files from the current directory                             |
| Minify Only Specific File Types         | `codebundle -m -ie .py .js`                                   | Create a minified copy with only Python and JavaScript files (Python files get minified)  |
| Complex Command with Shorthands         | `codebundle -t py shell -id utils -xf setup.py -i -c`         | Using multiple shorthands for a complex operation                                         |
| All Operations Together                 | `codebundle -f -df -b -m -mb -s src -t py -ie .py -xd tests`  | Perform all operations on Python files from src directory, excluding tests                |
| Custom Output Paths                     | `codebundle -f -df -b -s src -d myoutput`                     | Custom destination path for all operations (creates timestamped subdirectories)           |
| Bundle for Team Review                  | `codebundle -b -s project -ie .py .js -xd node_modules tests` | Create a bundle with only Python and JavaScript files, excluding tests and modules        |
| Project Migration                       | `codebundle -f -b -s legacy_project -d migration`             | Flatten and bundle a legacy project for migration, preserving both formats                |
| Optimized Context + Human Reference     | `codebundle -b -mb`                                           | Create two bundles - one minified (for optimization) and one readable (for humans)        |
| Find All Python Files                   | `codebundle -se .py`                                          | Lists all Python files in the codebase                                                    |
| Find Files With TODO Comments           | `codebundle -sp "TODO\|FIXME"`                                | Finds code that needs attention (with context)                                            |
| Find Large Files                        | `codebundle -ss 1024 none`                                    | Finds files larger than 1MB                                                               |
| Find Medium-Sized JavaScript Files      | `codebundle -ss 10 100 -ie .js`                               | Finds JS files between 10KB and 100KB                                                     |
| Find HTML Files in Specific Directory   | `codebundle -se .html -id templates views`                    | Finds HTML files but only in templates and views directories                              |
| Find Files With Sensitive Data Patterns | `codebundle -sp "password\|token\|secret" -ie .js .py .env`   | Finds potential security issues in specific file types                                    |
| Find Modified Files                     | `codebundle -sd 2025-04-08`                                   | Find files modified since April 8, 2025                                                   |
| Analyze Module Dependencies             | `codebundle -si requests`                                     | Find all files importing the 'requests' module                                            |
| Find Duplicate Code                     | `codebundle -sdu 10`                                          | Find code duplicated across 10 or more lines                                              |

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
