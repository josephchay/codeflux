# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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

### Changed

- Refactored handler, flatten, and deflatten functions to segregate common functionalities to `src/utils.py`
- Moved common usages of constant variables to `src/constants.py` file.

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
