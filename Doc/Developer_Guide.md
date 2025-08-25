# Developer Guide

## Overview

This document provides comprehensive information for developers who want to contribute to or extend the AAVC Calculate Tool.

## Project Structure

```
AAVC_calculate_tool/
├── src/
│   └── AAVC_calculate_tool/
│       ├── __init__.py          # Package initialization
│       ├── __main__.py          # CLI entry point
│       ├── calculator.py        # Core AAVC calculation logic
│       ├── config_loader.py     # Configuration file parsing
│       ├── data_loader.py       # Data fetching from Yahoo Finance
│       └── recorder.py          # Investment logging functionality
├── tests/                       # Test suite
├── Doc/                         # Documentation
├── pyproject.toml              # Project configuration
├── requirements.txt            # Dependencies
└── README.md                   # User documentation
```

## Development Setup

### 1. Clone and Setup

```bash
git clone <repository_url>
cd AAVC_calculate_tool
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Development Dependencies

```bash
pip install -e .[dev]
```

### 3. Verify Setup

```bash
# Run tests
pytest

# Run linting
ruff check .

# Run type checking
mypy src/

# Format code
black src/
```

## Architecture

### Core Components

#### 1. Calculator Module (`calculator.py`)

**Purpose**: Implements various AAVC and other investment strategy algorithms.

**Key Concepts**:
- **`BaseAAVCStrategy`**: An abstract base class defining the common interface for AAVC-like strategies. It handles general investment calculation logic, while delegating reference price determination to subclasses.
- **`get_metadata()`**: Each strategy implements this to provide metadata like name, description, version, author, and configurable parameters.
- **`_calculate_reference_price()`**: An abstract method in `BaseAAVCStrategy` that concrete AAVC subclasses must implement to define how their specific reference price is determined.

**Implemented Strategies**:
- **`AAVCStaticStrategy`**: Uses a fixed or initial price as the reference.
- **`AAVCDynamicStrategy`**: Dynamically resets the reference price when the current price rises significantly.
- **`AAVCMovingAverageStrategy`**: Uses a moving average of historical prices as the reference.
- **`AAVCHighestPriceResetStrategy`**: Resets the reference price based on a new highest price seen, scaled by a reset factor.
- **`DCAStrategy`**: Implements Dollar Cost Averaging.
- **`BuyAndHoldStrategy`**: Implements a simple Buy & Hold strategy.

**Algorithm Flow (General for `BaseAAVCStrategy` subclasses)**:
1. Determine investment day based on frequency.
2. Calculate the strategy-specific reference price (delegated to subclass).
3. Calculate volatility.
4. Calculate deviation from the reference price.
5. Apply asymmetric adjustment and volatility adjustment.
6. Calculate final investment amount, applying caps (min 0, max multiplier).

#### 2. Data Loader Module (`data_loader.py`)

**Purpose**: Handles data acquisition from external sources.

**Key Functions**:
- `fetch_price_history()`: Retrieves historical price data
- `validate_ticker()`: Validates ticker symbols

**Data Sources**:
- Yahoo Finance (via yfinance)
- Supports multiple ticker formats (US, Japanese, etc.)

#### 3. Configuration Loader (`config_loader.py`)

**Purpose**: Manages configuration file parsing and validation.

**Features**:
- YAML configuration support
- Default value handling
- Configuration validation
- Multiple investment job processing

#### 4. Recorder Module (`recorder.py`)

**Purpose**: Handles investment logging and data persistence.

**Features**:
- CSV log file management
- Automatic header creation
- Error handling for file operations

### Data Flow

```
User Input → CLI Parser → Config/Data Loader → Calculator → Recorder → Output
     ↓              ↓              ↓              ↓          ↓         ↓
  Arguments    Validation    Data Fetching   AAVC Calc   Logging   Results
```

## Testing

### Test Structure

```
tests/
├── test_calculator.py      # Calculator logic tests
├── test_cli.py            # CLI functionality tests
├── test_config_loader.py  # Configuration tests
├── test_data_loader.py    # Data fetching tests
└── test_recorder.py       # Logging tests
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_calculator.py

# Run with coverage
pytest --cov=src/AAVC_calculate_tool

# Run with verbose output
pytest -v
```

### Writing Tests

Follow these guidelines:

1. **Test Naming**: Use descriptive test names that explain the scenario
2. **Arrange-Act-Assert**: Structure tests with clear sections
3. **Mocking**: Mock external dependencies (API calls, file operations)
4. **Edge Cases**: Test boundary conditions and error scenarios

**Example Test Structure**:
```python
def test_calculate_aavc_investment_with_positive_deviation():
    """Test AAVC calculation when price is above reference."""
    # Arrange
    price_path = [100, 110, 120]  # Rising prices
    base_amount = 10000
    reference_price = 100
    
    # Act
    result = calculate_aavc_investment(
        price_path=price_path,
        base_amount=base_amount,
        reference_price=reference_price
    )
    
    # Assert
    assert result < base_amount  # Should reduce investment
    assert result > 0  # Should remain positive
```

## Code Quality

### Linting and Formatting

The project uses several tools to maintain code quality:

- **Black**: Code formatter (line length: 88)
- **Ruff**: Fast linter with multiple rules
- **MyPy**: Static type checking
- **isort**: Import statement sorting

### Pre-commit Hooks

Set up pre-commit hooks to automatically run quality checks:

```bash
# Install pre-commit
pip install pre-commit

# Install git hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Code Style Guidelines

1. **Python Version**: Target Python 3.8+
2. **Type Hints**: Use type hints for all function parameters and return values
3. **Docstrings**: Follow Google docstring format
4. **Error Handling**: Use custom exception classes for domain-specific errors
5. **Logging**: Use structured logging for debugging and monitoring

## Adding New Features

### 1. Feature Planning

- Create a feature branch from `main`
- Update relevant documentation
- Add tests for new functionality
- Consider backward compatibility

### 2. Implementation Steps

1. **Update Core Logic**: Modify appropriate modules
2. **Add Configuration**: Extend config schema if needed
3. **Update CLI**: Add new command options
4. **Add Tests**: Comprehensive test coverage
5. **Update Documentation**: User and developer docs

### 3. Example: Adding a New Investment Strategy

To add a new investment strategy, you typically create a new class that inherits from `BaseAlgorithm` or `BaseAAVCStrategy` (for AAVC-like strategies).

```python
# 1. Create a new strategy class in calculator.py (or a new strategy file)
from AAVC_calculate_tool.algorithm_registry import AlgorithmMetadata
from AAVC_calculate_tool.calculator import BaseAAVCStrategy # or BaseAlgorithm

class MyNewStrategy(BaseAAVCStrategy):
    def get_metadata(self) -> AlgorithmMetadata:
        return AlgorithmMetadata(
            name="my_new_strategy",
            description="A brief description of my new strategy.",
            version="1.0",
            author="Your Name",
            parameters={
                "my_param": {"type": "float", "default": 1.0, "description": "A parameter for my strategy"},
            },
            category="custom"
        )

    def _calculate_reference_price(
        self,
        current_price: float,
        price_history: List[float],
        parameters: Dict[str, Any]
    ) -> float:
        # Implement your reference price calculation logic here
        # This method is only for BaseAAVCStrategy subclasses
        pass

    # If inheriting from BaseAlgorithm directly, implement calculate_investment instead
    # def calculate_investment(...)

# 2. Register the new strategy in plugin_loader.py
#    Add MyNewStrategy to the import list and register it:
#    registry.register(MyNewStrategy)

# 3. (Optional) Add CLI options in __main__.py if specific arguments are needed
#    Otherwise, parameters can be passed via --algorithm-params

# 4. Add comprehensive unit tests in tests/test_calculator.py (or a new test file)

# 5. Update documentation (this Developer Guide, CLI Specification, etc.)
```

## Performance Considerations

### Optimization Strategies

1. **Data Caching**: Cache frequently accessed data
2. **Lazy Loading**: Load data only when needed
3. **Batch Processing**: Process multiple calculations efficiently
4. **Memory Management**: Handle large datasets appropriately

### Profiling

Use profiling tools to identify bottlenecks:

```bash
# Install profiling tools
pip install cProfile-viewer

# Profile specific function
python -m cProfile -o profile.stats -m AAVC_calculate_tool calc --ticker AAPL --amount 10000

# Analyze results
python -c "import pstats; p = pstats.Stats('profile.stats'); p.sort_stats('cumulative').print_stats(10)"
```

## Deployment

### Building Distribution

```bash
# Build wheel
python -m build

# Build source distribution
python -m build --sdist

# Install from wheel
pip install dist/*.whl
```

### CI/CD Integration

The project supports GitHub Actions for automated testing and deployment:

- **Pull Request Checks**: Automated testing and linting
- **Release Automation**: Automated version bumping and publishing
- **Dependency Updates**: Automated security updates

## Contributing

### Pull Request Process

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add/update tests
5. Update documentation
6. Submit a pull request

### Code Review Guidelines

- Ensure all tests pass
- Check code coverage
- Verify documentation updates
- Review for security implications
- Consider performance impact

## Support and Resources

### Documentation

- [User Guide](README.md)
- [CLI Specification](Doc/01_CLI_Specification.md)
- [Configuration Guide](Doc/03_Configuration_and_Logging.md)

### Community

- GitHub Issues: Bug reports and feature requests
- GitHub Discussions: General questions and discussions
- Contributing Guidelines: [CONTRIBUTING.md](../CONTRIBUTING.md)

### Development Tools

- **IDE Support**: VS Code with Python extensions recommended
- **Debugging**: Use `pdb` or IDE debuggers
- **Version Control**: Git with conventional commit messages 
