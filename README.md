# Codeflux - Unravel Your Codebase

**Codeflux** is a tool for organizing large codebases, consolidating scripts, optimizations, or 
preparing for migration or backup.

## Overview

Tired of wading through tangled directory trees just to make sense of a codebase? 
**Codeflux** is a versatile CLI tool that brings structure, clarity, and control to any source directory. 
It intelligently flattens or reconstructs file hierarchies, bundles and minifies code, snips code chunks, 
performs search functionalities across files, and delivers timestamped outputs. 
With robust filtering and deep code insight features, **Codeflux** transforms messy projects into manageable, transparent systems.

### Supported File Types

| Language            | Extensions                                                                  |
|---------------------|-----------------------------------------------------------------------------|
| Python              | `.py`                                                                       |
| Python Notebooks    | `.ipynb`                                                                    |
| JavaScript          | `.js`, `.jsx`                                                               |
| TypeScript          | `.ts`, `.tsx`                                                               |
| HTML                | `.html`, `.htm`, `.xhtml`, `.shtml`                                         |
| CSS                 | `.css`, `.scss`, `.sass`, `.less`                                           |
| PHP                 | `.php`, `.phtml`, `.php5`, `.php7`, `.phps`                                 |
| Ruby                | `.rb`, `.rake`, `.gemspec`, `.erb`                                          |
| Swift               | `.swift`                                                                    |
| Kotlin              | `.kt`, `.kts`                                                               |
| Java                | `.java`, `.class`, `.jar`                                                   |
| C#                  | `.cs`, `.cshtml`, `.csx`                                                    |
| Shell Scripts       | `.sh`, `.bash`, `.zsh`                                                      |
| Markdown            | `.md`, `.markdown`, `.mdown`, `.mkdn`, `.mkd`, `.mdwn`, `.mdtxt`, `.mdtext` |
| Plain Text          | `.txt`                                                                      |
| YAML                | `.yaml`, `.yml`                                                             |
| JSON                | `.json`, `.jsonl`, `.geojson`, `.json5`, `.ndjson`                          |
| GO                  | `.go`, `.mod`, `.sum`, `.pb.go`, `.tmpl`, `.tpl`                            |
| INI Configuration   | `.ini`, `.cfg`, `.conf`, `.properties`                                      |
| Database Scripts    | `.sql`, `.ddl`, `.dml`                                                      |
| Batch Scripts       | `.bat`, `.cmd`, `.btm`                                                      |
| Custom Scripts      | `.scp`, `.script`                                                           |
| No Extension        | Files without extensions (like `Makefile`, `activate`, `Dockerfile`)        |
| PowerShell          | `.ps1`, `.psm1`, `.psd1`, `.ps1xml`                                         |
| Docker              | `.dockerfile`, `.dockerignore`                                              |
| XML                 | `.xml`, `.xsd`, `.xsl`, `.xslt`, `.wsdl`, `.svg`, `.pom`                    |
| R                   | `.r`, `.rmd`, `.rds`, `.rdata`, `.rda`                                      |
| C/C++               | `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`, `.hxx`, `.hh`                    |
| Rust                | `.rs`, `.rlib`                                                              |
| Scala               | `.scala`, `.sc`                                                             |
| Perl                | `.pl`, `.pm`, `.t`                                                          |
| Lua                 | `.lua`                                                                      |
| Groovy              | `.groovy`, `.gvy`, `.gy`, `.gsh`                                            |
| Haskell             | `.hs`, `.lhs`                                                               |
| Erlang/Elixir       | `.erl`, `.hrl`, `.ex`, `.exs`                                               |

_More file types extensions to be added in the future._

---

## Installation

> [!WARNING]
> Uninstall the package (If you have already installed a previous version of the package)

### Python Projects

```bash
pip install git+https://github.com/josephchay/codeflux.git
```

### NodeJS Projects

```bash
npm install --save-dev git+https://github.com/josephchay/codeflux.git
```
or
```bash
yarn add git+https://github.com/josephchay/codeflux.git --dev
```
or
```bash
pnpm add git+https://github.com/josephchay/codeflux.git --save-dev
```

> [!NOTE]
> Occasionally, check on the `staging` and `develop` branches for new features or bug fixes that has not been merged
> into the `main` branch.

## Pre-requisites

### Dependencies

- Node version 22 or higher
- NPM version 5.1 or higher

## Command-Line Arguments

| Argument                                        | Shorthand | Default                                                                                                                                                                                                                                                                | Description                                                                                        |
|-------------------------------------------------|-----------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------|
| `[src]`                                         | `-s`      | Current directory                                                                                                                                                                                                                                                      | Source directory containing the files to flatten                                                   |
| `[dest]`                                        | `-d`      | Based on operation (see below)                                                                                                                                                                                                                                         | Destination directory/file where files will be copied                                              |
| `--file-types`                                  | `-t`      | `py`, `ipynb`, `jsts`, `html`, `css`, `php`, `ruby`, `swift`, `kotlin`, `java`, `csharp`, `shell`, `mdtxt`, `yml`, `json`, `go`, `ini`, `db`, `bat`, `scp`, `noext`, `ps1`, `docker`, `xml`, `r`, `cpp`, `rust`, `scala`, `perl`, `lua`, `groovy`, `haskell`, `erlang` | File types to process (default: all)                                                               |
| **Operations**                                  |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--flatten`                                     | `-f`      | `True` (if no other operation specified)                                                                                                                                                                                                                               | Flatten the directory structure                                                                    |
| `--deflatten`                                   | `-df`     | `True` (if no other operation specified)                                                                                                                                                                                                                               | Deflatten the directory (restore original structure)                                               |
| `--bundle`                                      | `-b`      | `True` (if no other operation specified)                                                                                                                                                                                                                               | Bundle files into a single text file                                                               |
| `--minify`                                      | `-m`      | `True` (if no other operation specified)                                                                                                                                                                                                                               | Create a minified copy of the directory while preserving structure                                 |
| `--minify-bundle`                               | `-mb`     | `True` (if no other operation specified)                                                                                                                                                                                                                               | Minify files and bundle them into a single text file                                               |
| **Operations Aids**                             |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--no-filetype-dirs` (Flattening only)          | `-nfd`    | `False`                                                                                                                                                                                                                                                                | Place all files directly in the output directory without filetype subdirectories during flattening |
| `--truncate` (Tree only)                        | `-t`      | `False`                                                                                                                                                                                                                                                                | Truncate long tree output in console                                                               |
| `--tree`                                        | `-tr`     | `True` (if no other operation specified)                                                                                                                                                                                                                               | Generate a text-based visualization of the processed directory structure                           |
| `--root-tree`                                   | `-rtr`    | `False`                                                                                                                                                                                                                                                                | Generate a complete text-based visualization of the root directory tree (with operation status)    |
| **Exclusion Options**                           |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--exclude-dirs`                                | `-xd`     | Various default directories                                                                                                                                                                                                                                            | Directory names to exclude                                                                         |
| `--exclude-extensions`                          | `-xe`     | Various default extensions                                                                                                                                                                                                                                             | File extensions to exclude                                                                         |
| `--exclude-files`                               | `-xf`     | Various path-based files                                                                                                                                                                                                                                               | Specific file paths to exclude (requires full path relative to source dir, e.g. 'path/to/file.py') |
| **Defaults Handling**                           |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--ignore-defaults`                             | `-i`      | `False`                                                                                                                                                                                                                                                                | Ignore all default exclusions and only use provided exclusions                                     |
| **Inclusion Options**                           |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--include-dirs`                                | `-id`     | `None`                                                                                                                                                                                                                                                                 | Directory names to include (only these will be processed)                                          |
| `--include-extensions`                          | `-ie`     | `None`                                                                                                                                                                                                                                                                 | File extensions to include (only these will be processed)                                          |
| `--include-files`                               | `-if`     | `None`                                                                                                                                                                                                                                                                 | Specific filenames to include (only these will be processed)                                       |
| **Snippet Options** (bundle/minify-bundle only) |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--snippet`                                     | `-sn`     | `False`                                                                                                                                                                                                                                                                | Enable snippet mode for bundling operations (only includes a portion of each file)                 |
| `--snippet-lines`                               | `-snl`    | `50`                                                                                                                                                                                                                                                                   | Maximum number of lines to include per file in snippet mode                                        |
| `--snippet-start`                               | `-sns`    | `top`                                                                                                                                                                                                                                                                  | Where to take the snippet from: top, middle, or bottom of the file                                 |
| `--snippet-context`                             | `-snc`    | `5`                                                                                                                                                                                                                                                                    | Number of context lines to include around matches when using with search-pattern                   |
| **Search Options**                              |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--search-extensions`                           | `-se`     | `None`                                                                                                                                                                                                                                                                 | Search for files with specific extensions                                                          |
| `--search-pattern`                              | `-sp`     | `None`                                                                                                                                                                                                                                                                 | Search for files containing a specific regex pattern                                               |
| `--search-size`                                 | `-ss`     | `None`                                                                                                                                                                                                                                                                 | Search for files within a size range (in KB, use 'none' for no limit)                              |
| `--search-date`                                 | `-sd`     | `None`                                                                                                                                                                                                                                                                 | Search for files modified between dates (YYYY-MM-DD format)                                        |
| `--search-imports`                              | `-si`     | `None`                                                                                                                                                                                                                                                                 | Search for files that import a specific module                                                     |
| `--search-duplicates`                           | `-sdu`    | `None`                                                                                                                                                                                                                                                                 | Search for duplicate code blocks (with optional minimum line threshold)                            |
| **Properties Options**                          |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--properties`                                  | `-p`      | `None`                                                                                                                                                                                                                                                                 | Display detailed file properties without modifying anything                                        |
| `--exclude-hash` (Properties only)              | `-xh`     | `None`                                                                                                                                                                                                                                                                 | Exclude MD5 hash calculation from properties analysis (faster for large files)                     |
| **Other Options**                               |           |                                                                                                                                                                                                                                                                        |                                                                                                    |
| `--clear-dest-dir`                              | `-c`      | `False`                                                                                                                                                                                                                                                                | Clear the destination directory before copying files                                               |
| `--no-log`                                      | `-nl`     | `False`                                                                                                                                                                                                                                                                | Disable logging output                                                                             |
| `--continue-on-error`                           | `-coe`    | `False`                                                                                                                                                                                                                                                                | Continue processing when minification errors occur (using original content for failed files)       |

### Default Paths and Output Organization

* **Source directory**: If not specified, defaults to the current working directory
* **Base output directory**: A `codeflux` directory in the current working directory
* **Operation directories**: A single timestamped directory containing all operations executed in one run
* **Destination paths** (when running multiple operations in a single command):
  * `./codeflux/{timestamp}/flattened/` (for flatten operation)
  * `./codeflux/{timestamp}/deflattened/` (for deflatten operation)
  * `./codeflux/{timestamp}/bundled.txt` (for bundle operation)
  * `./codeflux/{timestamp}/minified/` (for minify operation)
  * `./codeflux/{timestamp}/minified_bundle.txt` (for minify-bundle operation)
  * `./codeflux/{timestamp}/source_directory_tree.txt` (for tree operation)
  * `./codeflux/{timestamp}/root_directory_tree.txt` (for complete directory tree)
  * `./codeflux/{timestamp}/summary.txt` (summary of all operations performed)

For detailed information on default values, refer to the [constants](src/constants.py) file.

## Usage Examples

Here are various scenarios and how to use the tool:

| Scenario                                  | Command                                                     | Description                                                                               |
|-------------------------------------------|-------------------------------------------------------------|-------------------------------------------------------------------------------------------|
| All Operations                            | `codeflux`                                                  | Performs all operations onto the current directory into a timestamped output directory    |
| Multiple Operations                       | `codeflux -f -df -b`                                        | Performs flatten, deflatten and bundle operations in sequence                             |
| Process Specific Types                    | `codeflux -t py ipynb shell`                                | Process only Python, Python Notebooks, and Shell Script files from current directory      |
| Flatten without filetype subdirectories   | `codeflux -f -nfd`                                          | Flatten the directory structure with all files in a single output directory               |
| Bundle with Minification                  | `codeflux -mb`                                              | Bundle the current directory with minified code                                           |
| Minify Python for Optimized Context       | `codeflux -mb -t py -s src`                                 | Create a minified bundle of Python files from 'src' suitable for optimized context usages |
| Minify Directory                          | `codeflux -m`                                               | Create a minified copy of the current directory while preserving structure                |
| Minify Specific Project                   | `codeflux -m -s src -t py -xd tests venv`                   | Create a minified copy of the src directory, excluding tests and venv directories         |
| Exclude Directories                       | `codeflux -xd .idea .venv`                                  | Flattens the current directory excluding the specified directories                        |
| Include Only Specific Directories         | `codeflux -id utils models`                                 | Only process files from the 'utils' and 'models' directories in the current folder        |
| Include Only Specific Extensions          | `codeflux -ie .py .sh`                                      | Only process files with '.py' and '.sh' extensions from the current directory             |
| Ignore Default Exclusions                 | `codeflux -i`                                               | Flattens the current directory without applying default exclusions                        |
| Exclude File Extensions                   | `codeflux -xe .txt .csv`                                    | Flattens the current directory excluding files with the specified extensions              |
| Exclude Specific Files                    | `codeflux -xf setup.py package.json setup.sh`               | Flattens the current directory excluding the specified files                              |
| Include Only Specific Files               | `codeflux -if main.py analysis.ipynb deploy.sh`             | Processes only the specified files from the current directory                             |
| Minify Only Specific File Types           | `codeflux -m -ie .py .js`                                   | Create a minified copy with only Python and JavaScript files (Python files get minified)  |
| Complex Command with Shorthands           | `codeflux -t py shell -id utils -xf setup.py -i -c`         | Using multiple shorthands for a complex operation                                         |
| Flatten All in One Directory              | `codeflux -f -nfd -s src -d flat_output`                    | Flatten src directory with all files in flat_output without filetype subdirectories       |
| All Operations Together                   | `codeflux -f -df -b -m -mb -s src -t py -ie .py -xd tests`  | Perform all operations on Python files from src directory, excluding tests                |
| Custom Output Paths                       | `codeflux -f -df -b -s src -d myoutput`                     | Custom destination path for all operations (creates timestamped subdirectories)           |
| Bundle for Team Review                    | `codeflux -b -s project -ie .py .js -xd node_modules tests` | Create a bundle with only Python and JavaScript files, excluding tests and modules        |
| Project Migration                         | `codeflux -f -b -s legacy_project -d migration`             | Flatten and bundle a legacy project for migration, preserving both formats                |
| Optimized Context + Human Reference       | `codeflux -b -mb`                                           | Create two bundles - one minified (for optimization) and one readable (for humans)        |
| Find All Python Files                     | `codeflux -se .py`                                          | Lists all Python files in the codebase                                                    |
| Find Files With TODO Comments             | `codeflux -sp "TODO\|FIXME"`                                | Finds code that needs attention (with context)                                            |
| Find Large Files                          | `codeflux -ss 1024 none`                                    | Finds files larger than 1MB                                                               |
| Find Medium-Sized JavaScript Files        | `codeflux -ss 10 100 -ie .js`                               | Finds JS files between 10KB and 100KB                                                     |
| Find HTML Files in Specific Directory     | `codeflux -se .html -id templates views`                    | Finds HTML files but only in templates and views directories                              |
| Find Files With Sensitive Data Patterns   | `codeflux -sp "password\|token\|secret" -ie .js .py .env`   | Finds potential security issues in specific file types                                    |
| Find Modified Files                       | `codeflux -sd 2025-04-08`                                   | Find files modified since April 8, 2025                                                   |
| Analyze Module Dependencies               | `codeflux -si requests`                                     | Find all files importing the 'requests' module                                            |
| Find Duplicate Code                       | `codeflux -sdu 10`                                          | Find code duplicated across 10 or more lines                                              |
| Bundle with Snippets                      | `codeflux -b -sn`                                           | Bundle the current directory but only include up to 50 lines per file                     |
| Minified Bundle with Snippets             | `codeflux -mb -sn`                                          | Create a minified bundle with snippets of each file (up to 50 lines)                      |
| Custom Snippet Size                       | `codeflux -b -sn -snl 100`                                  | Bundle with snippets of up to 100 lines per file                                          |
| Minified Snippets from Middle             | `codeflux -mb -sn -sns middle`                              | Create a minified bundle with snippets from the middle of each file                       |
| Snippet from Bottom of Files              | `codeflux -b -sn -sns bottom`                               | Bundle with snippets from the end of each file                                            |
| Snippet with Pattern Focus                | `codeflux -b -sn -sp "TODO"`                                | Bundle with snippets focused around TODO comments                                         |
| Code Review Bundle (Minified)             | `codeflux -mb -sn -snl 30 -sp "FIXME\|TODO"`                | Create a minified bundle focused on code that needs attention                             |
| API Usage Review                          | `codeflux -b -sn -sp "api\.call\|fetchData"`                | Create a bundle focused on API usage patterns                                             |
| Compact Documentation                     | `codeflux -mb -sn -snl 20 -ie .md .py -id docs src`         | Create a compact, minified bundle of documentation and Python files                       |
| Error-focused Diagnostic Bundle           | `codeflux -b -sn -sp "error\|exception\|fail" -snc 10`      | Bundle focusing on error handling with extended context around matches                    |
| File Properties                           | `codeflux -p`                                               | View detailed properties of all files in the current directory                            |
| File Properties w/o Hash Display          | `codeflux -p -xh`                                           | View file properties without MD5 hash calculation                                         |
| Minify with Error Handling                | `codeflux -m -coe`                                          | Create a minified copy, continuing when minification errors occur                         |
| Standard Tree Visualization               | `codeflux -tr`                                              | Generate visualization of processed source files from the current directory               |
| Truncated Tree Output                     | `codeflux -tr -trc`                                         | Generate tree visualization with truncated console output                                 |
| Complete Tree with Status Indicators      | `codeflux -ct`                                              | Generate a complete tree showing all files with processing status                         |
| Project Structure Comparison              | `codeflux -tr -mb`                                          | Generate tree visualization alongside a minified bundle                                   |
| Tree Visualization of Specific Directory  | `codeflux -tr -s src`                                       | Generate tree visualization only for the src directory                                    |
| Complete Tree with Limited Console Output | `codeflux -ct -trc`                                         | Generate complete tree with truncated console display                                     |
| Tree for Python Files Only                | `codeflux -tr -t py`                                        | Generate tree visualization showing only Python files                                     |
| Visualize Filtered Project Structure      | `codeflux -tr -xd tests venv node_modules`                  | Generate tree without tests, venv, and node_modules directories                           |
| Tree with Custom Output Path              | `codeflux -tr -d project_structure.txt`                     | Save tree visualization to a specific file path                                           |

## Development

Clone the Repository:

```bash
git clone https://github.com/josephchay/codeflux.git
cd codeflux

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
* **GitHub Issues**: [Issues](https://github.com/josephchay/codeflux/issues)
