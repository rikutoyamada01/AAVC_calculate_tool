# Gemini Agent Guide for AAVC Calculate Tool

This document provides guidance for the Gemini agent on how to interact with the `AAVC_calculate_tool` project.

## About This Project

The "AAVC Calculate Tool" is a Python-based command-line interface (CLI) tool designed to calculate the "Asymmetric Average Volatility Cost" (AAVC). This calculation helps investors determine a strategic purchase price for a stock by analyzing its historical volatility. The tool can fetch data from Yahoo Finance, perform calculations for single or multiple stocks, and display the results in a user-friendly format.

## How to Run

The tool is executed as a Python module from the root of the project directory.

### Calculate for a Single Stock

To calculate the AAVC for a single stock ticker:

```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000
```

### Calculate for a Portfolio

To calculate the AAVC for a portfolio of stocks defined in a YAML file:

```bash
python -m AAVC_calculate_tool calc --config path/to/your/portfolio.yaml
```

### Display Help Messages

To get help on available commands and options:

```bash
# General help
python -m AAVC_calculate_tool --help

# Help for the 'calc' command
python -m AAVC_calculate_tool calc --help
```

## How to Run Tests

The project uses `python -m pytest` for testing.

### Run All Tests

To execute the entire test suite:

```bash
python -m pytest
```

### Run a Specific Test File

To run tests from a specific file:

```bash
python -m pytest tests/test_calculator.py
```

## Code Generation and Modification Rules

When generating or modifying code within this project, please adhere to the following guidelines:

*   **Style Guide**: All Python code must follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) conventions. Use `ruff` for linting and formatting.
*   **Unit Tests**: For any new features or bug fixes, corresponding unit tests must be added or updated in the `tests/` directory. Ensure existing tests pass after your changes.
*   **Documentation**: If you add new features, modify existing functionality, or fix bugs that impact user-facing behavior, update the relevant documentation in the `Doc/` directory.
*   **Dependencies**: Manage dependencies using `requirements.txt` for direct dependencies and `pyproject.toml` for project metadata and build system. Avoid introducing new, unnecessary dependencies.
*   **Error Handling**: Implement robust error handling using Python's `try-except` blocks. Provide informative error messages.
*   **Logging**: Use the project's logging mechanism (if defined in `config_loader.py` or similar) for debugging and operational insights, rather than `print()` statements for production code.

## Documentation Guidelines

The project's documentation is located in the `Doc/` directory and is written in Markdown.

*   **Clarity and Conciseness**: Write clear, concise, and easy-to-understand documentation. Avoid jargon where possible, or explain it thoroughly.
*   **Examples**: Include practical examples for commands, configurations, and code snippets to illustrate usage.
*   **Consistency**: Maintain consistent formatting, terminology, and tone throughout the documentation.
*   **Updates**: Always update relevant documentation files when making changes to the codebase that affect functionality, configuration, or usage.
*   **Structure**: Follow the existing structure within the `Doc/` directory (e.g., `01_CLI_Specification.md`, `Developer_Guide.md`).

## Detailed Directory Structure

Here's a more detailed overview of the project's directory structure and the purpose of key components:

*   `./`: The project root directory.
    *   `.gitignore`: Specifies intentionally untracked files to ignore by Git.
    *   `config.yaml`: Default configuration file for the AAVC tool.
    *   `CONTRIBUTING.md`: Guidelines for contributing to the project.
    *   `LICENSE.md`: Project's license information.
    *   `pyproject.toml`: Project metadata, build system configuration, and dependencies.
    *   `README.md`: Main project overview, quick start, and user guide.
    *   `requirements.txt`: Lists Python dependencies required for the project.
    *   `test_log.csv`: (Potentially) A log file for test runs or backtesting results.
*   `.git/`: Git version control repository.
*   `.pytest_cache/`: Cache directory for pytest.
*   `.ruff_cache/`: Cache directory for ruff linter/formatter.
*   `build/`: Directory for build artifacts (e.g., wheels, eggs).
*   `charts/`: (Potentially) Directory for storing generated charts or plots.
*   `Doc/`: Contains all project documentation in Markdown format.
    *   `01_CLI_Detailed_Design.md`: Detailed design document for the CLI.
    *   `01_CLI_Specification.md`: Specification for the command-line interface.
    *   `Developer_Guide.md`: Comprehensive guide for developers.
    *   `Documentation_Index.md`: Index of all available documentation.
    *   `Quick_Start_Guide.md`: A quick guide to get started with the tool.
    *   ... (other detailed design and specification documents)
*   `src/`: Source code directory.
    *   `AAVC_calculate_tool/`: The main Python package for the tool.
        *   `__init__.py`: Initializes the Python package.
        *   `__main__.py`: The entry point for the CLI application when run as a module (`python -m AAVC_calculate_tool`).
        *   `algorithm_registry.py`: (Potentially) Manages different calculation algorithms.
        *   `backtester.py`: Contains logic for backtesting investment strategies.
        *   `calculator.py`: Implements the core AAVC calculation logic.
        *   `config_loader.py`: Handles loading and parsing configuration files (e.g., `config.yaml`).
        *   `data_loader.py`: Responsible for fetching historical stock data (e.g., from Yahoo Finance).
        *   `display.py`: Manages formatting and displaying output to the user.
        *   `minus_five_percent_rule.py`: (Potentially) Implements a specific investment rule.
        *   `plotter.py`: Generates visual plots and charts from data.
        *   `plugin_loader.py`: (Potentially) Handles loading external plugins or extensions.
        *   `recorder.py`: Records and saves results, especially from backtesting, to files.
        *   `__pycache__/`: Python bytecode cache.
    *   `AAVC_calculate_tool.egg-info/`: Metadata for the Python egg distribution.
    *   `aavc-calculate-tool/`: (Potentially) A nested or separate project/module, possibly an older version or a sub-component.
*   `tests/`: Contains all unit and integration tests for the project.
    *   `test_backtester.py`: Tests for the backtesting module.
    *   `test_calculator.py`: Tests for the core calculation logic.
    *   `test_cli.py`: Tests for the command-line interface.
    *   `test_config_loader.py`: Tests for configuration loading.
    *   `test_data_loader.py`: Tests for data loading.
    *   `test_display.py`: Tests for output display.
    *   `test_plotter.py`: Tests for plotting functionality.
    *   `test_recorder.py`: Tests for result recording.
    *   `__pycache__/`: Python bytecode cache for tests.

## Commands Summary

The primary command is `calc`, which performs the AAVC calculation.

-   `AAVC_calculate_tool calc`:
    -   `--ticker`: The stock ticker symbol (e.g., "AAPL").
    -   `--amount`: The base investment amount.
    -   `--config`: Path to a YAML file containing a portfolio of stocks.
