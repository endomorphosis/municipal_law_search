# CLAUDE.md - Project Scaffold

## Overview
A generic scaffold to quickly create python-based projects.

## Setup and Run Commands
- Setup: `./install.sh` (creates venv, installs requirements)
- Run: `./start.sh` (activates venv, runs main.py)
- Tests: `source venv/bin/activate && python -m unittest tests.test_scaffold` (run embedding tests)
- Single test: `source venv/bin/activate && python -m unittest tests.test_scaffold.TestScaffold` (run specific test class)
- **IMPORTANT**: Always run tests with the virtual environment activated to ensure all dependencies are available

## Testing Notes and Deprecations
- **IMPORTANT**: Files in the `deprecated` directory are DEPRECATED and should NEVER be run

## IMPORTANT: Configuration Security
- **NEVER** use or modify yaml files that start with an underscore (like _configs.yaml) - they are public!
- For API keys and sensitive configurations, use environment variables
- Set API keys with: `export YOUR_API_KEY="your-api-key"` before running scripts

## Code Style Guidelines
- **Typing**: Use Python type hints
- **Imports**: Group by standard lib, third-party, local modules
- **Naming**: snake_case for functions/variables, PascalCase for classes, ALL_CAPS for constants.
- **Error Handling**: Use try/except with specific exceptions
- **Formatting**: 4-space indentation
- **Functions**: Keep pure, use partial for function composition
- **Configs**: Pydantic models for config validation if using external config sources (e.g. json, yaml, etc.)
- **Async**: Use asyncio for I/O-bound operations
- **Paths**: Use pathlib.Path for file operations
- **Logging**: Use logger from logger.py module

## Project Structure
- Modular utils/ directory for helper functions
- dataclass in config.py for configuration management
- Use process pools for CPU-bound operations
- Use asyncio for I/O-bound operations
- Store tests in tests/ directory with unittest framework