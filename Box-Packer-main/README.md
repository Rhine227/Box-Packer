# Box Packer - Optimal Pallet Arrangement Calculator

A Python application that calculates optimal arrangements of rectangular boxes on wooden pallets, featuring both text-based and graphical 2D visualizations.

## Features

- **Optimal Box Arrangement**: Automatically finds the best arrangement to maximize box count per layer
- **Smart Dimension Handling**: Enforces width ≤ length convention with automatic swapping
- **Multiple Orientations**: Supports normal and rotated box orientations for better space utilization
- **Pallet Size Compliance**: Respects standard pallet dimensions (40" × 48")
- **Auto-Optimization**: Automatically determines optimal number of boxes per layer
- **Manual Mode**: Allows specifying exact number of boxes to arrange
- **2D Visualization**: Beautiful graphical representation with matplotlib
- **Modular Architecture**: Clean, maintainable code structure

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/box-packer.git
   cd box-packer
   ```

2. **Install required dependencies**:
   ```bash
   pip install matplotlib
   ```

3. **Run the application**:
   ```bash
   python main.py
   ```

## Usage

### Basic Usage

1. Run the program: `python main.py`
2. Enter box dimensions (width and length)
3. Choose between:
   - **Auto-optimization**: Press Enter to find optimal box count
   - **Manual mode**: Enter specific number of boxes per layer
4. View results in text format
5. Optionally view 2D graphical visualization

### Example

```
Enter box width: 8
Enter box length: 10
Enter number of boxes per layer (or press Enter to auto-optimize): [Press Enter]

Auto-optimizing number of boxes per layer...
Optimal solution: 24 boxes per layer
Arrangement: 6 rows x 4 columns
```

## Project Structure

```
box-packer/
├── main_new.py              # Main application entry point
├── config.py                # Configuration constants
├── models/
│   ├── __init__.py
│   ├── box.py              # Box class definition
│   └── pallet.py           # Pallet class definition
├── algorithms/
│   ├── __init__.py
│   ├── arrangement.py       # Box arrangement logic
│   ├── optimization.py     # Optimization algorithms
│   └── scaling.py          # Pallet scaling utilities
└── utils/
    ├── __init__.py
    ├── input_handler.py     # User input processing
    ├── display.py          # Text output formatting
    ├── geometry.py         # Geometric calculations
    └── visualization.py    # 2D graphical visualization
```

## Key Features

### Smart Dimension Validation
- Automatically ensures width ≤ length
- Warns user with "That's stupid!" message for invalid input
- Automatically swaps dimensions when needed

### Optimization Algorithms
- Tests multiple arrangement patterns
- Prioritizes arrangements that fit within standard pallet size
- Calculates efficiency metrics
- Provides detailed optimization feedback

### Professional Visualization
- Dark blue background with orange pallet outline
- Grey boxes with sequential numbering
- Proper orientation handling (Normal vs Rotated)
- Dimensional annotations and grid lines

## Box Orientations

- **N (Normal)**: Box width horizontal, box length vertical
- **R (Rotated)**: Box length horizontal, box width vertical
- **O (Empty)**: Gap in arrangement for alignment

## Configuration

Default pallet size: 40" × 48" (configurable in `config.py`)

## Technical Details

- **Language**: Python 3.10+
- **Dependencies**: matplotlib
- **Architecture**: Modular design with separation of concerns
- **Validation**: Comprehensive input validation and error handling
- **Efficiency**: Optimized algorithms for fast arrangement calculation

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Created with assistance from GitHub Copilot
Date: July 2025

## Acknowledgments

- Wooden pallet industry standards for optimal 6:5 ratio guidance
- Professional packaging and logistics best practices
- Modern Python development patterns and modular architecture
