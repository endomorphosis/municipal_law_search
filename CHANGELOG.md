# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[unreleased]: https://github.com/kylerose1946/american_law_search/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/kylerose1946/american_law_search/releases/tag/v0.1.0