# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2025-04-05

### Added

- Comprehensive docstrings for database utility functions in `create_american_law_db.py` 
- Complete Google-style docstrings for all hash utility functions in `utils/get_hash.py`
- Detailed parameter, return type and exception documentation for concurrency utilities
- Class-level docstrings for `IpfsMultiformats`, `LLMOutput`, `LLMInput` and utility classes
- Method-level docstrings for all properties in LLM models
- Property docstrings for computed fields in Pydantic models
- Usage examples in utility function documentation for better developer guidance
- Documentation summary file (docstring_additions_summary.md) for tracking improvement efforts

### Fixed

- Logic bug in `IpfsMultiformats.get_cid` method in `utils/get_cid.py` that caused incorrect file processing
- Critical bug in `generate_rag_response` method with undefined variable reference that would cause runtime failure
- Type handling issues in several LLM interface methods leading to potential crashes
- Null reference handling in `calculate_cost` method to prevent potential exceptions
- Corrected error handling in multiple utility functions for better robustness
- Fixed potential null reference errors in several functions across the codebase
- Corrected misleading comments and docstrings that didn't match implementation
- Improved error handling with proper try-except blocks in several utility functions

## [0.1.0] - 2025-03-31

### Added

- Documentation Generator tool for automatic code documentation
- Comprehensive database migration tests

### Changed

- Migrated database layer from SQLite to DuckDB for improved performance
- Added backward compatibility with SQLite as a fallback option
- Updated database connection functions to support both engines
- Modified database setup utilities to use DuckDB by default
- Updated documentation with DuckDB usage guidelines
- Improved error handling in database setup modules

### Fixed

- Database path inconsistencies across different modules
- Connection management in database utilities

### Security

- Improved input validation for database queries

[unreleased]: https://github.com/kylerose1946/american_law_search/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/kylerose1946/american_law_search/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/kylerose1946/american_law_search/releases/tag/v0.1.0