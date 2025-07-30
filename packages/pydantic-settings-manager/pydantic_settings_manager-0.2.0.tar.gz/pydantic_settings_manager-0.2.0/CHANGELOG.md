# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-06-28

### Changed
- **BREAKING**: Migrated from Poetry to uv for dependency management
- Modernized development toolchain with unified linting using ruff
- Updated to use PEP 621 compliant project metadata format
- Introduced PEP 735 dependency groups for flexible development environments
- Enhanced CI/CD pipeline to use uv instead of Poetry
- Improved type checking configuration with stricter MyPy settings
- Updated all development dependencies to latest versions

### Added
- Comprehensive development documentation in README
- Support for modular dependency groups (test, lint, dev)
- Enhanced linting rules including pyupgrade and flake8-comprehensions
- Migration guide for developers updating their local environment

### Removed
- Poetry configuration files (poetry.lock, pyproject.toml Poetry sections)
- Separate black, isort, and flake8 configurations (replaced by ruff)

## [0.1.2] - 2024-03-12

### Added
- Added py.typed file for better type checking support
- Improved package configuration and build process

## [0.1.1] - 2024-03-12

### Added
- Added detailed documentation in README.md
- Added example code for both SingleSettingsManager and MappedSettingsManager

### Fixed
- Improved type hints and documentation

## [0.1.0] - 2024-03-11

### Added
- Initial release
- Implemented SingleSettingsManager for managing single settings object
- Implemented MappedSettingsManager for managing multiple settings objects
- Support for loading settings from multiple sources
- Command line argument overrides
- Settings validation through Pydantic
