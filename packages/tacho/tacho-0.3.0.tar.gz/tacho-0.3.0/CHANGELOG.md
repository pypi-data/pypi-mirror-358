# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-01-26

### Changed
- Improved error handling with specific exception types for authentication, rate limits, and connection issues
- Enhanced user feedback with clearer error messages during model validation
- Added graceful handling of keyboard interrupts (Ctrl+C)
- Updated README to accurately reflect output metrics

### Fixed
- Corrected README documentation about displayed metrics (removed mention of median and average tokens)

## [0.2.1] - 2025-01-26

### Changed
- Major code refactoring for improved elegance and maintainability
- Unified benchmark functions to eliminate code duplication (~80 lines removed)
- Simplified progress tracking by removing complex queue system
- Cleaner CLI argument handling using Typer's callback feature
- Extracted metrics calculation into reusable helper function
- Improved error handling with cleaner validation messages
- Reduced total codebase by ~15% while maintaining all functionality

### Fixed
- Fixed module import issues in pyproject.toml entry point

## [0.1.5] - 2025-01-26

### Changed
- Display average time and tokens per run instead of totals
- Improved clarity of benchmark metrics

## [0.1.4] - 2025-01-26

### Added
- `--lim` parameter to control maximum tokens per response (default: 2000)
- Full async/parallel execution for all benchmarks
- Dynamic model testing with `test-models` command

### Changed
- Tokens/second is now the primary metric instead of raw time
- All benchmarks run in parallel by default
- Simplified progress indicators to just spinners

### Removed
- Sequential benchmark mode (everything is now parallel)
- Hardcoded provider list in favor of dynamic testing
- Individual model completion outputs during benchmarking
- "Fastest model" announcement at the end

## [0.1.3] - 2025-01-26

### Changed
- Reorganized package structure: moved CLI code to separate module
- Updated entry point configuration

## [0.1.2] - 2025-01-26

### Changed
- Fixed import issues with package entry point

## [0.1.1] - 2025-01-26

### Added
- Initial release
- Basic benchmarking functionality
- Support for multiple LLM providers via LiteLLM
- Progress bars and formatted output tables
- `list-providers` command