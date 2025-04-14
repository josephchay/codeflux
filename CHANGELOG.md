# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `src/search.py` file for search functionality.
- New `--search-ext`, `--search-pattern`, `--search-size` arguments for file and content searching.
- `--search-date`, `--search-imports`, `--search-duplicates` arguments for file searching.
- Each search functionality to have the file size shown. 
- `get_file_snippet` method for getting file snippets.
- New `--snippet`, `--snippet-lines`, `--snippet-start`, `--snippet-context` arguments for snippet generation for bundling and minify-bundling operations.
- Optional table UI output display using `tabulate` library package with `grid` as `tablefmt`.
- `html`, `css`, `php`, `ruby`, `swift`, `kotlin`, `java`, `csharp` file extensions handling.
- HTML minifier using the JS-based library package `html-minifier`.
- Use of `python-minifier` minification for python codes in `.ipynb` files.
- New minifier for CSS related files with package `csso`.
- New minifier for PHP related files with package `php-minify`.
- `Pre-requisites` section in `README.md` for required dependencies and versions.
- `--continue-on-error` argument to continue the process even if an error occurs for a file or a part of it.
- `--no-filetypes-dir` argument to disable file extension types subdirectories in the `flattened` output directory.
- `--properties` to view properties of specified directory or files.
- `--exclude-hash` argument to exclude MD5 hash calculation for files.
- `maxcolwidths` of `tabulate` table UI to be more dynamic towards the terminal width.
- `tree.py` for source directory tree visualization, and saving to `diretory_tree.txt` in the output directory.
- Command used tracking for each instance - saved into `summary.txt` file in the output directory.
- Command and Raw Command being used to perform the instance in the CLI.
- File handling for `noext` (no extension files), `ps1`, `docker`, `xml`, `r`, `cpp`, `rust`, `scala`, `perl`, `lua`, `groovy`, `haskell`, and `erlang` extensions.
- Complete tree visualization from root directory (with and without operation status checking)
- `--truncate` argument to truncate the output of the tree visualization.
- `--root-tree` argument to visualize the root directory tree.
- `ROOT_TREE_UI_TRUNCATE_DIRS` constant for the directories to be excluded from the root tree visualization (but maintained during printing).
- File handling for LaTeX related file extensions.
- `LATEX_EXCLUDE_EXTENSIONS` list of default extensions to be excluded with regex pattern (currently for numeric values after the extension name).

### Fixed

- Made sure now `--exclude-files` properly handle path-based exclusion. 
- Duplicate shorthand argument for `--search-duplicate` and `--search-date` fixed.
- Added missing file extension handlers for `db` and `bat` files.
- Prevented multiple exact printing of Destination and minification information for each file type.
- Processing for files passed using argument `--include-files` or `-if` now works as expected.
- Information for original size and reduction size now being calculated and displayed for all file types.
- New `snipping.py` file for handling snippet functionality.
- Minification process for both `MINIFY` and `MINIFY_BUNDLE` operations now have their warnings properly displayed in the output table.
- Minification warnings for `.ipynb` files - warnings now display in the `Warnings` column in the output table UI.
- Shell related scripts returning `None` instead of a string.
- Display from the root directory (package installed directory) for the root directory tree.

### Changed

- Updated `bundle_files` method to include snippet generation feature.
- Updated `print_stats` method in the `src/utils.py` file to include the new `tabulate` table UI functionality. 
- `minify_code` method to not return any default `source` value, and when encountering an error, it will print it and exit.
- Renamed method `create_output_dir` to `mkdir_output`.
- Moved minification (non-script) codes to `minify.py`. 
- console printing output display more accurate.
- Segregated parsing code to the `make_parser` method in `main.py`.
- Renamed project from `Codebundle` to `Codeflux`.
- Renamed attribute name from `--search-ext` to `--seach-extensions`.
- Console print formatting for `--tree` visualization standardized like other operations.
- Removed output file path from being displayed in the status columns of `flattening`, and `deflattening` operations.
- Renamed `ROOT_TREE_UI_TRUNCATE_DIRS` to `ROOT_TREE_UI_EXCLUDE_DIRS` constant.

### Removed

- The term `EXECUTING` from title of each operation in `main.py`.

## [0.8.0] - 2025-04-07

### Added

- File handling for INI and SCP related file extensions.
- Database and Batch scripts file extension handling in `constants.py`.
- Minification for YAML files with `ruamel.yaml` package library.
- Original file size for each file, and minified file size for each file when minifying.

### Fixed

- Bundling operation now performs for all file handlers, and not just only for the first one.

### Changed

- If no operations are specified, then it will perform all operations (flattening, deflattening, minifying, bundling, and minifying-bundling) by default.
- Updated INI config and SCP scripts related file extensions constants.
- Renamed the `src/scripts/minify.js` file to `src/scripts/jsts_minify.js`.
- Added `pyyaml` and `ruamel.yaml` to the `requirements.txt` file.

## [0.7.0] - 2025-04-06

### Added

- Support for minification features. Default minification `-m` and aggressive minification `-am`.
- Support for default values for source directory and destination paths, if not provided for flattening, deflattening, and bundling operations.
- `requirements.txt` file for package dependencies.
- Long description and project URLs to `setup.py` for PyPI.
- File handling for JSON files.
- File handling for GO related file extensions.
- `MANIFEST.in` file to include all files in the package.
- Minification support for JSTS files using `terser` package library, with `src/minify.js` script.
- `package.json`, and `package-lock.json` files for `terser` package library.
- `codebundle` to default excluded directories.

### Fixed

- Imported `create_timestamped_dir` function in `main.py` to create a timestamped directory for output files.
- Minor console output printing inconsistencies.
- Minor printing inconsistencies in `main.py`.

### Changed

- `--minify` to use the `python-minifier` package library.
- Default outputs will be saved into `codebundle` prefix directory.
- Each output will not overwrite the previous one. Instead, it will create a new directory with a timestamp.
- Enable multiple operations (flattening, deflattening, and bundling) in a single command (no longer mutually exclusive).
- `--minify` flag to create a minified copy of the directory while preserving structure (without bundling).
- Functionality of the `--minify` flag passed to the `--minify-bundle` flag for a minified bundle.
- Default output dir will be `codebundle` with timestamped subdirectories for each operation.
- Refactored code to have all operations handling codes to be in the `handlers.py` file.

### Removed

- `--aggressive-minify` flag.
- Unnecessary `get_incremented_path` function in `utils.py`.

## [0.6.0] - 2025-04-02

### Added

- `--ignore-defaults` flag to ignore default file extensions and directories that will apply for exclusion/inclusion.
- `--include-dirs` argument for directory inclusion.
- `--include-extensions` argument for file extension inclusion.
- New shorthand flags for all `arg_parse` arguments.

### Changed

- New `arg_parse` grouping for exclusion and inclusion flags.

## [0.5.1] - 2025-04-01

### Added

- File handling for Shell scripts.

### Fixed

- Added `handlers` to the `py_modules` attribute in `setup.py` file.

## [0.5.0] - 2025-03-31

### Added

- `--bundle` flag to bundle all files into a single `.txt` file with proper formatting.
- `bundling`, `flattening`, and `deflattening` functionality for `markdown` files.
- `--exclude-files` argument for file exclusion for python, javascript/typescript, and markdown files.
- `CHANGELOG.md` file to be excluded from the markdown files during process handling.
- `--include-files` argument for file inclusion for python, javascript/typescript, and markdown files.
- `src/constants.py` file for constant values.
- File handling for `yaml` files.
- `utils`, `constants` to the `py_modules` attribute in `setup.py` file.
- Constants for `.ipynb` notebook handling in the `constants.py` file.
- File handling and processing for notebook files.

### Changed

- Refactored handler, flatten, and deflatten functions to segregate common functionalities to `src/utils.py`
- Moved common usages of constant variables to `src/constants.py` file.
- Moved all file handlers and base `FileExtHandler` to only the `handlers.py` file.

### Fixed

- Proper renames from `pack` to `bundle` in `utils.py`.

### Removed

- `utils` from `py_modules` attribute in `setup.py` file.

## [0.4.0] - 2025-03-02

### Added

- `--no-log` flag to suppress logging.
- Supports `.js`, `.jsx`, `.ts`, and `.tsx` extensions.
- `--file-exts` flag to specify file extensions to flatten.
- `__init__.py` file in `src/exts`.

### Fixed

- Corrected argument parsing for `--exclude-exts`, and `--filetypes` flags.
- Replace `py_modules=['main']` with `packages=find_packages(where='src')` in `setup.py`.

### Changed

- Moved handling for python file flattening and deflattening to `exts/py_handler.py` module.
- Moved general utility functions to `utils.py` module.
- Renamed directory `exts` to `handlers`.
- Changed output dirs name from `python` to `py`, and `javascript` to `jsts`.

### Removed

- Unnecessary `setup_2.py` file in root directory.

## [0.3.4] - 2025-03-01

### Added

- Added more metrics for flattening and deflattening processes.

### Removed

- Remove absolute path from the printing of the source and destination directories.

## [0.3.3] - 2025-03-01

### Fixed

- First two arguments without flags now work as expected (Try 2).

## [0.3.2] - 2025-03-01

### Fixed

- First two arguments without flags now work as expected.

## [0.3.1] - 2025-03-01

### Added

- Allowing the first two arguments to be src and dest without flags.

## [0.3.0] - 2025-02-21

### Changed

- Directory prefixes changed from `__` (double underscore) to `___` (triple underscore).

## [0.2.2] - 2025-02-21

### Added

- Flatten and Deflatten feature for current (root) directory.

## [0.2.1] - 2025-02-21

### Fixed

- Make destination directory if it does not exist.

## [0.2.0] - 2025-02-21

### Added

- `DEFAULT_EXCLUDES` to exclude files and folders from flattening.
- `deflatten_dir` function to reverse the flattening process.
- `exclude` parameter to exclude files and folders from flattening.
- Separated `exclude` parameter to `exclude_dirs` for directories and `exclude_extensions` for files.
- `get_unique_filename` that generates a unique filename by appending a counter to the filename if a file with the same name already exists in the destination directory.
- `clear_dest_dir` optional parameter to clear the destination directory before copying files.

## [0.1.2] - 2025-01-21

### Added

- `main.py` script for flattening python project files.
- `setup.py` file.
- Added entry point in `setup.py`.
- Added try-exception blocks in main function execution.
- package installation command.
- Made inclusion of `__init__.py` files for conversion optional - by default not included.
- Copied files are now prefixed with their parent directory names and Directory names are separated by double hyphens `__`.

### Changed

- Execution script in `README.md`.
- Updated `README.md`.
- Updated entry point in `setup.py`.
- From `packages` to `py_modules` in `setup.py`.
