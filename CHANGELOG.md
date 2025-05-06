# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Implemented Search History feature:
  - Created `search_history` table in database with appropriate indexes
  - Added API endpoints for retrieving, deleting, and clearing search history
  - Integrated search history with existing search functionality
  - Implemented frontend UI for displaying and managing search history
  - Added client-side cookie tracking for per-user history without requiring login
  - Enabled "search again" functionality for previous searches
- Comprehensive Google-style docstrings for missing modules and functions:
  - Added module docstrings for app modules, including logger.py
  - Added docstrings for Pydantic models in schemas package (ErrorResponse, LawItem)
  - Added docstrings for database connection utilities (_get_a_database_connection, _get_data_from_sql)
  - Added docstrings for cursor and connection management in search utilities
  - Added type variable documentation to improve type hinting clarity
  - Added docstrings to all search-related functions with proper algorithm descriptions
  - Added complete class documentation for UploadToHuggingFaceInParallel
- Complete documentation for app.py with 100% docstring coverage:
  - Detailed class docstring for the SearchFunction class explaining the search pipeline
  - Comprehensive docstrings for all SearchFunction methods with algorithm explanations
  - Complete API endpoint documentation for search, get_law, and SSE endpoints
  - Added context manager method docstrings for proper resource management
  - Documented static file serving endpoints and utility methods
  - Added full docstrings for all helper methods including pagination calculations
- Improved database utility docstrings:
  - Added detailed algorithm descriptions for database operations
  - Documented connection handling and resource cleanup
  - Included error handling and exception documentation
  - Added usage examples for database functions
- Added reports to identify docstring gaps and inconsistencies:
  - Created missing_docstrings.md with documentation gaps in the app directory
  - Created missing_docstrings_utils.md with documentation gaps in utility modules

### Fixed

- Duplicate line in SearchFunction.__init__ initialization
- Improved error handling documentation in various functions
- Clarified return type annotations in several methods
- Fixed inconsistent parameter types in several function signatures
- Updated function return type hints to match actual return values

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