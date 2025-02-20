# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2] - 2025-01-21

### Added
- `main.py` script for flattening python project files.
- `setup.py` file.
- Added entry point in `setup.py`.
- Added try-exception blocks in main function execution.
- package installation command.
- Made inclusion of `__init__.py` files for conversion optional - by default not included.
- Coppied files are now prefixed with their parent directory names and Directory names are separated by double hyphens `__`.
- `DEFAULT_EXCLUDES` to exclude files and folders from flattening.
- `deflatten_dir` function to reverse the flattening process.
- `exclude` parameter to exclude files and folders from flattening. 

### Changed
- Execution script in `README.md`.
- Updated `README.md`.
- Updated entry point in `setup.py`.
- From `packages` to `py_modules` in `setup.py`.
