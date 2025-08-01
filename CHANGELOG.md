# Changelog

All notable changes to the Box Packer project will be documented in this file.

## [1.0.1] - 2025-07-16 - Refactored and Cleaned

### Fixed
- Fixed inappropriate warning message in Box class validation
- Removed duplicate and empty files (main_new.py, enhanced utility files)
- Fixed setup.py entry point to reference correct main module
- Cleaned up all __pycache__ directories

### Improved
- Enhanced input validation with proper error handling and user feedback
- Added comprehensive type hints throughout the codebase
- Improved Box class with additional utility methods (aspect_ratio, can_fit_in_space, best_orientation_for_space)
- Enhanced error handling and user experience in main.py
- Better code organization and documentation

### Added
- Configuration constants for validation (MIN_DIMENSION, MAX_DIMENSION, MAX_REASONABLE_BOXES)
- Comprehensive unit test suite with integration tests
- Improved requirements.txt with proper version constraints
- Enhanced documentation and code comments
- Equality and hash methods for Box class

## [1.0.0] - 2025-07-01

### Added
- Initial release of Box Packer application
- Modular architecture with separate packages for models, algorithms, and utilities
- Box and Pallet classes with dimension validation
- Auto-optimization algorithm to find optimal number of boxes per layer
- Manual mode for specifying exact box count
- Smart dimension handling with width ≤ length enforcement
- Multiple box orientations (Normal and Rotated)
- Text-based arrangement visualization
- 2D graphical visualization with matplotlib
- Professional dark blue theme with orange pallet and grey boxes
- Box numbering in graphical display (top to bottom, left to right)
- Comprehensive input validation and error handling
- Efficiency calculations and optimization feedback
- Support for standard 40" × 48" pallet size
- Pallet scaling capability (for manual mode only)

### Features
- **Models Package**: Box and Pallet classes with validation
- **Algorithms Package**: Arrangement, optimization, and scaling logic
- **Utils Package**: Input handling, display formatting, geometry calculations, and visualization
- **Configuration**: Centralized constants in config.py
- **Error Analysis**: Detailed feedback when arrangements don't fit
- **User-Friendly Interface**: Clear prompts and helpful messages

### Technical Details
- Python 3.10+ compatibility
- Matplotlib integration for graphical visualization
- Modular design for maintainability and extensibility
- Comprehensive docstrings and type hints
- Professional code organization following Python best practices

### Breaking Changes
- N/A (initial release)

### Known Issues
- None at release

### Dependencies
- matplotlib >= 3.5.0
