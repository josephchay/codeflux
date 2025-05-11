# CodeFlux - Unravel Your Codebase

<p align="center">
  <img src="assets/brand.png" alt="Description" style="width: 380px; border-radius: 10px; display: block; margin: auto;" />
</p>

**CodeFlux** is a versatile command-line tool for organizing, transforming, and enhancing large codebases. 
Whether you need to consolidate scripts, optimize file structure, prepare for migration, or add documentation, 
**CodeFlux** provides powerful features to streamline your workflow.

## Overview

Tired of wading through tangled directory trees just to make sense of a codebase?
**CodeFlux** intelligently flattens or reconstructs file hierarchies, bundles and minifies code, 
automatically adds quality comments, performs search operations across files, and delivers timestamped outputs.

With **CodeFlux**, you can quickly transform sprawling projects into well-organized, documented, and optimized codebases. 
Perfect for code review preparation, knowledge transfer, technical documentation, legacy system migration, 
or creating optimized context for AI tools.

### Supported File Types

| Category              | Extensions                                                                          | Key Type  |
|-----------------------|-------------------------------------------------------------------------------------|-----------|
| Python                | `.py`                                                                               | `py`      |
| Python Notebooks      | `.ipynb`                                                                            | `ipynb`   |
| JavaScript/TypeScript | `.js`, `.jsx`, `.ts`, `.tsx`                                                        | `jsts`    |
| HTML                  | `.html`, `.htm`, `.xhtml`, `.shtml`                                                 | `html`    |
| CSS/Preprocessors     | `.css`, `.scss`, `.sass`, `.less`                                                   | `css`     |
| PHP                   | `.php`, `.phtml`, `.php5`, `.php7`, `.phps`                                         | `php`     |
| Ruby                  | `.rb`, `.rake`, `.gemspec`, `.erb`                                                  | `ruby`    |
| Swift                 | `.swift`                                                                            | `swift`   |
| Kotlin                | `.kt`, `.kts`                                                                       | `kotlin`  |
| Java                  | `.java`, `.class`, `.jar`                                                           | `java`    |
| C#                    | `.cs`, `.cshtml`, `.csx`                                                            | `csharp`  |
| Shell Scripts         | `.sh`, `.bash`, `.zsh`                                                              | `shell`   |
| Markdown/Text         | `.md`, `.markdown`, `.mdown`, `.mkdn`, `.mkd`, `.mdwn`, `.mdtxt`, `.mdtext`, `.txt` | `mdtxt`   |
| YAML                  | `.yaml`, `.yml`                                                                     | `yml`     |
| JSON                  | `.json`, `.jsonl`, `.geojson`, `.json5`, `.ndjson`                                  | `json`    |
| Go                    | `.go`, `.mod`, `.sum`, `.pb.go`, `.tmpl`, `.tpl`                                    | `go`      |
| Configuration         | `.ini`, `.cfg`, `.conf`, `.properties`                                              | `ini`     |
| Database Scripts      | `.sql`, `.ddl`, `.dml`                                                              | `db`      |
| Batch Scripts         | `.bat`, `.cmd`, `.btm`                                                              | `bat`     |
| Script Files          | `.scp`, `.script`                                                                   | `scp`     |
| PowerShell            | `.ps1`, `.psm1`, `.psd1`, `.ps1xml`                                                 | `ps1`     |
| Docker                | `.dockerfile`, `.dockerignore`                                                      | `docker`  |
| XML                   | `.xml`, `.xsd`, `.xsl`, `.xslt`, `.wsdl`, `.svg`, `.pom`                            | `xml`     |
| R                     | `.r`, `.rmd`, `.rds`, `.rdata`, `.rda`                                              | `r`       |
| C/C++                 | `.c`, `.cpp`, `.cc`, `.cxx`, `.h`, `.hpp`, `.hxx`, `.hh`                            | `cpp`     |
| Rust                  | `.rs`, `.rlib`                                                                      | `rust`    |
| Scala                 | `.scala`, `.sc`                                                                     | `scala`   |
| Perl                  | `.pl`, `.pm`, `.t`                                                                  | `perl`    |
| Lua                   | `.lua`                                                                              | `lua`     |
| Groovy                | `.groovy`, `.gvy`, `.gy`, `.gsh`                                                    | `groovy`  |
| Haskell               | `.hs`, `.lhs`                                                                       | `haskell` |
| Erlang/Elixir         | `.erl`, `.hrl`, `.ex`, `.exs`                                                       | `erlang`  |
| LaTeX                 | `.tex`, `.sty`, `.cls`, `.bib`, `.bst`, `.dtx`, `.ltx`, `.ins`                      | `latex`   |
| BibTeX                | `.bib`                                                                              | `bibtex`  |
| PDF                   | `.pdf`                                                                              | `pdf`     |
| Word Documents        | `.docx`, `.doc`                                                                     | `docx`    |
| No Extension          | Files without extensions (like `Makefile`, `README`, `Dockerfile`)                  | `noext`   |

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

### Command-Line Arguments

| Argument                          | Shorthand | Default                                | Description                                                                              |
|-----------------------------------|-----------|----------------------------------------|------------------------------------------------------------------------------------------|
| **Source/Destination**            |           |                                        |                                                                                          |
| `[src]`, `--src`                  | `-s`      | Current directory                      | Source directory containing the files to process                                         |
| `[dest]`, `--dest`                | `-d`      | Based on operation                     | Destination directory/file for output                                                    |
| **Main Operations**               |           |                                        |                                                                                          |
| `--flatten`                       | `-f`      | `False`                                | Flatten the directory structure                                                          |
| `--deflatten`                     | `-df`     | `False`                                | Deflatten the directory (restore original structure)                                     |
| `--minify`                        | `-m`      | `False`                                | Create a minified copy preserving directory structure                                    |
| `--bundle`                        | `-b`      | `False`                                | Bundle files into a single text file                                                     |
| `--minify-bundle`                 | `-mb`     | `False`                                | Minify files and bundle them into a single text file                                     |
| `--autocomment`                   | `-ac`     | `False`                                | Automatically add comments to code files                                                 |
| `--linebreak`                     | `-hb`     | `False`                                | Hard-break long lines at specified width while preserving structure                      |
| `--acroscan`                      | `-as`     | `False`                                | Scan for and optionally replace acronyms in documents                                    |
| `--bibdedup`                      | `-bd`     | `False`                                | Check for similar titles across multiple `.bib` files                                    |
| `--properties`                    | `-p`      | `False`                                | Display detailed file properties without modifying anything                              |
| **Tree Visualization**            |           |                                        |                                                                                          |
| `--tree`                          | `-tr`     | `True`                                 | Generate a text-based visualization of the processed directory structure                 |
| `--root-tree`                     | `-rtr`    | `True`                                 | Generate a complete tree visualization with operation status                             |
| `--no-tree`                       | `-ntr`    | `False`                                | Do not generate the processed directory tree visualization                               |
| `--no-root-tree`                  | `-nrtr`   | `False`                                | Do not generate the root directory tree visualization                                    |
| **Search Operations**             |           |                                        |                                                                                          |
| `--search-ext`                    | `-se`     | `None`                                 | Search for files with specific extensions                                                |
| `--search-pattern`                | `-sp`     | `None`                                 | Search for files containing a specific regex pattern                                     |
| `--search-size`                   | `-ss`     | `None`                                 | Search for files within a size range (in KB)                                             |
| `--search-date`                   | `-sd`     | `None`                                 | Search for files modified between dates (YYYY-MM-DD format)                              |
| `--search-imports`                | `-si`     | `None`                                 | Find files that import a specific module                                                 |
| `--search-duplicates`             | `-sdu`    | `None`                                 | Find duplicate code blocks (optional: minimum lines)                                     |
| **File Type Selection**           |           |                                        |                                                                                          |
| `--file-types`                    | `-t`      | All types                              | File types to process (e.g., `py`, `jsts`, `html`)                                       |
| **Inclusion/Exclusion Options**   |           |                                        |                                                                                          |
| `--include-dirs`                  | `-id`     | `None`                                 | Directory names to include (only these will be processed)                                |
| `--include-extensions`            | `-ie`     | `None`                                 | File extensions to include (only these will be processed)                                |
| `--include-files`                 | `-if`     | `None`                                 | Specific filenames to include (only these will be processed)                             |
| `--exclude-dirs`                  | `-xd`     | Various default directories            | Directory names to exclude                                                               |
| `--exclude-extensions`            | `-xe`     | Various default extensions             | File extensions to exclude                                                               |
| `--exclude-files`                 | `-xf`     | Various default files                  | Specific file paths to exclude                                                           |
| `--ignore-defaults`               | `-i`      | `False`                                | Ignore all default exclusions                                                            |
| **Snippet Options** (bundle only) |           |                                        |                                                                                          |
| `--snippet`                       | `-sn`     | `False`                                | Enable snippet mode for bundling operations                                              |
| `--snippet-lines`                 | `-snl`    | `50`                                   | Maximum number of lines to include per file                                              |
| `--snippet-start`                 | `-sns`    | `top`                                  | Where to take the snippet from: top, middle, or bottom                                   |
| `--snippet-context`               | `-snc`    | `5`                                    | Context lines around matches when using with search-pattern                              |
| **Acroscan Options**              |           |                                        |                                                                                          |
| `--acronym-list`                  | `-al`     | `None`                                 | Path to CSV file containing acronyms                                                     |
| `--acronym-output`                | `-ao`     | `None`                                 | Path to output the acronyms file                                                         |
| `--latex-mode`                    | `-lm`     | `True`                                 | Process files in LaTeX mode (uses \ac{...} syntax)                                       |
| `--find-potential`                | `-fp`     | `False`                                | Find potential acronyms not in the list                                                  |
| `--replace-acronyms`              | `-ra`     | `True`                                 | Replace found acronyms in processed files                                                |
| `--no-recursive-acroscan`         | `-nras`   | `False`                                | Do not recursively process subdirectories                                                |
| **AutoComment Options**           |           |                                        |                                                                                          |
| `--comment-level`                 | `-cl`     | `standard`                             | Level of commenting: minimal, standard, or verbose                                       |
| `--no-add-docstrings`             | `-nad`    | `False`                                | Don't add docstrings to functions and classes                                            |
| `--no-add-inline`                 | `-nai`    | `False`                                | Don't add inline comments for complex logic                                              |
| `--no-add-header`                 | `-nah`    | `False`                                | Don't add file header comments                                                           |
| `--no-preserve-existing`          | `-npe`    | `False`                                | Don't preserve existing comments                                                         |
| **Linebreak Options**             |           |                                        |                                                                                          |
| `--line-width`                    | `-lw`     | `80`                                   | Maximum line width for hardbreak operation                                               |
| `--break-on-word`                 | `-bow`    | `True`                                 | Break lines on word boundaries when possible                                             |
| `--no-break-on-word`              | `-nbow`   | `False`                                | Break lines at exact character position                                                  |
| `--preserve-indent`               | `-pi`     | `True`                                 | Preserve indentation when breaking lines                                                 |
| `--no-preserve-indent`            | `-npi`    | `False`                                | Don't preserve indentation when breaking lines                                           |
| **BibTeX Options**                |           |                                        |                                                                                          |
| `--similarity-threshold`          | `-st`     | `0.9`                                  | Similarity threshold for duplicate detection (0.0-1.0)                                   |
| **Other Options**                 |           |                                        |                                                                                          |
| `--no-filetype-dirs`              | `-nfd`    | `False`                                | Place all files directly in output directory (flatten only)                              |
| `--exclude-hash`                  | `-xh`     | `False`                                | Exclude MD5 hash calculation (properties only)                                           |
| `--clear-dest-dir`                | `-c`      | `False`                                | Clear the destination directory before copying                                           |
| `--truncate`                      | `-trc`    | `False`                                | Truncate long tree output in console                                                     |
| `--no-log`                        | `-nl`     | `False`                                | Suppress all output logs                                                                 |
| `--continue-on-error`             | `-coe`    | `False`                                | Continue processing when minification errors occur                                       |

### Default Paths and Output Organization

- **Source directory**: If not specified, defaults to the current working directory
- **Base output directory**: A `codeflux` directory in the current working directory
- **Operation directories**: A single timestamped directory containing all operations executed in one run
- **Destination paths** (when running multiple operations in a single command):
  - `./codeflux/{timestamp}/flattened/` (for flatten operation)
  - `./codeflux/{timestamp}/deflattened/` (for deflatten operation)
  - `./codeflux/{timestamp}/minified/` (for minify operation)
  - `./codeflux/{timestamp}/autocommented/` (for autocomment operation)
  - `./codeflux/{timestamp}/linebreak/` (for linebreak operation)
  - `./codeflux/{timestamp}/bundled.txt` (for bundle operation)
  - `./codeflux/{timestamp}/minified_bundle.txt` (for minify-bundle operation)
  - `./codeflux/{timestamp}/processed_directory_tree.txt` (for tree operation)
  - `./codeflux/{timestamp}/root_directory_tree.txt` (for complete directory tree)
  - `./codeflux/{timestamp}/summary.txt` (summary of all operations performed)

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
| Complete Tree with Status Indicators      | `codeflux -rtr`                                             | Generate a complete tree showing all files with processing status                         |
| Project Structure Comparison              | `codeflux -tr -mb`                                          | Generate tree visualization alongside a minified bundle                                   |
| Tree Visualization of Specific Directory  | `codeflux -tr -s src`                                       | Generate tree visualization only for the src directory                                    |
| Complete Tree with Limited Console Output | `codeflux -rtr -trc`                                        | Generate complete tree with truncated console display                                     |
| Tree for Python Files Only                | `codeflux -tr -t py`                                        | Generate tree visualization showing only Python files                                     |
| Visualize Filtered Project Structure      | `codeflux -tr -xd tests venv node_modules`                  | Generate tree without tests, venv, and node_modules directories                           |
| Tree with Custom Output Path              | `codeflux -tr -d project_structure.txt`                     | Save tree visualization to a specific file path                                           |
| Default deduplication                     | `codeflux -bd`                                              | Find similar BibTeX titles using default threshold (0.9)                                  |
| Check BibTeX Lower threshold Similarity   | `codeflux -bd -st 0.8`                                      | Find more duplicates (80% similarity)                                                     |
| Check BibTeX Higher threshold Similarity  | `codeflux -bd -st 0.95`                                     | Only nearly identical titles flagged (95% similarity)                                     |
| Check BibTeX from Specific directory      | `codeflux -s references -bd`                                | Deduplicate `.bib` files in `references` directory                                        |
| Multiple operations with BibTeX Checking  | `codeflux -f -m -bd -st 0.85`                               | Flatten, minify, and deduplicate BibTeX with 85% similarity                               |
| Auto-comment All Files                    | `codeflux -ac`                                              | Add standard comments to all code files                                                   |
| Auto-comment with Verbose Comments        | `codeflux -ac -cl verbose`                                  | Add detailed, extensive comments to all files                                             |
| Minimal Auto-commenting                   | `codeflux -ac -cl minimal`                                  | Add only essential comments to code files                                                 |
| Auto-comment Python Files Only            | `codeflux -ac -t py`                                        | Add comments only to Python files                                                         |
| Auto-comment Without Docstrings           | `codeflux -ac --no-add-docstrings`                          | Add comments but skip function/class docstrings                                           |
| Auto-comment Without Inline Comments      | `codeflux -ac --no-add-inline`                              | Add docstrings and headers but skip inline comments                                       |
| Auto-comment Without Headers              | `codeflux -ac --no-add-header`                              | Add docstrings and inline comments but skip file headers                                  |
| Replace Existing Comments                 | `codeflux -ac --no-preserve-existing`                       | Overwrite existing comments with new ones                                                 |
| Auto-comment Project Files                | `codeflux -ac -s src -xd tests`                             | Add comments to source files, excluding tests                                             |
| Auto-comment for Documentation            | `codeflux -ac -cl verbose -id docs examples`                | Add extensive comments to documentation and example files                                 |
| Break Long Lines (Default)                | `codeflux -hb`                                              | Break lines longer than 80 characters                                                     |
| Break Lines at 100 Characters             | `codeflux -hb -lw 100`                                      | Break lines longer than 100 characters                                                    |
| Break Lines at Exact Position             | `codeflux -hb --no-break-on-word`                           | Break lines at exact character position (not word boundaries)                             |
| Break Lines Without Indent                | `codeflux -hb --no-preserve-indent`                         | Break lines without preserving indentation                                                |
| Break Lines in Python Files               | `codeflux -hb -t py -lw 120`                                | Break lines at 120 characters in Python files only                                        |
| Reformat Documentation Files              | `codeflux -hb -ie .md .txt -lw 80`                          | Break long lines in markdown and text files                                               |
| Clean Up Long SQL Queries                 | `codeflux -hb -ie .sql -lw 160`                             | Break long SQL statements at 160 characters                                               |
| Reformat Configuration Files              | `codeflux -hb -ie .yaml .json -lw 100`                      | Break long lines in YAML and JSON configuration files                                     |
| Break Lines in Source Code                | `codeflux -hb -s src -xd tests -lw 88`                      | Break lines at 88 chars (Python Black standard) in source files                           |
| PEP 8 Compliance Helper                   | `codeflux -hb -t py -lw 79`                                 | Enforce PEP 8 line length in Python files                                                 |
| Prepare Code for Code Review              | `codeflux -hb -ac -t py js`                                 | Break long lines and add comments for Python and JS files                                 |
| Full Code Cleanup                         | `codeflux -m -hb -ac`                                       | Minify, break long lines, and add comments to all files                                   |
| Documentation Enhancement                 | `codeflux -ac -hb -ie .md -cl verbose -lw 100`              | Add verbose comments and break lines in markdown files                                    |
| Legacy Code Modernization                 | `codeflux -ac -hb -m -s legacy`                             | Add comments, break lines, and minify legacy codebase                                     |
| Code Style Standardization                | `codeflux -hb -lw 100 -ac -cl standard`                     | Standardize line length and add consistent comments                                       |
| Prepare for AI Analysis                   | `codeflux -mb -hb -lw 120 -sn`                              | Create minified, line-broken bundle with snippets for AI consumption                      |
| Team Code Review Bundle                   | `codeflux -b -ac -hb -lw 100`                               | Create bundle with comments and consistent line lengths                                   |
| Find and Fix Long Lines                   | `codeflux -sp ".\{120,\}" -hb -lw 100`                      | Find lines over 120 chars, then break them at 100                                         |
| Combined Search and Format                | `codeflux -se .py -ac -hb`                                  | Find Python files, add comments, and break long lines                                     |
| Comprehensive Code Analysis               | `codeflux -p -se .py -ac -hb -tr`                           | Get properties, find Python files, add comments, break lines, and show tree               |
| Multi-operation Pipeline                  | `codeflux -f -ac -hb -m -b -mb`                             | Flatten, comment, break lines, minify, bundle (both regular and minified)                 |
| Project Documentation Generator           | `codeflux -ac -cl verbose -b -tr`                           | Add verbose comments, create bundle, and generate tree view                               |
| Code Compliance Check                     | `codeflux -hb -lw 79 -ac -p`                                | Break lines to PEP 8 length, add comments, show file properties                           |
| Acronym Scanning                          | `codeflux -as`                                              | Scan for and replace acronyms in all files                                                |
| Acronym Scanning Without Replacement      | `codeflux -as --no-replace-acronyms`                        | Only find acronyms without replacing them                                                 |
| Find Potential Unknown Acronyms           | `codeflux -as -fp`                                          | Find potential acronyms not in the acronym list                                           |
| Acronym Scan with Custom List             | `codeflux -as -al custom_acronyms.csv`                      | Use custom acronym list for scanning                                                      |
| Non-recursive Acronym Scan                | `codeflux -as -nras`                                        | Scan only the current directory (not subdirectories)                                      |
| LaTeX Document Acronym Processing         | `codeflux -as -ie .tex -lm`                                 | Process LaTeX files with appropriate acronym syntax                                       |
| Documentation Acronym Standardization     | `codeflux -as -id docs -ie .md .tex`                        | Standardize acronyms in documentation files                                               |

## Development

Clone the Repository:

```bash
git clone https://github.com/josephchay/codeflux.git
cd codeflux

# Install locally
pip install -e .
```

### Code Architecture

The codebase follows a modular structure:

- `main.py` - Entry point and command processing
- `file_handler.py` - Core file processing logic
- `operations/` - Operation implementations (flatten, deflatten, etc.)
- `utils/` - Helper utilities for logging, minification, etc.
- `helpers/` - Helper functions for various tasks
- `templates/` - Predefined input structures for operations
- `ui/` - User interface components for command-line interaction
- `scripts/` - Scripts for specific tasks or examples

### Testing

To test functionality during development, you can run:

```bash
python -m src.main --src <source_dir> --dest <dest_dir>
```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE.txt) file for details.

## Support

Need help? Have a question? Feel free to reach out:

- **Email**: [josephemmanuelchay@gmail.com](mailto:josephemmanuelchay@gmail.com)
- **GitHub Issues**: [Issues](https://github.com/josephchay/codeflux/issues)
