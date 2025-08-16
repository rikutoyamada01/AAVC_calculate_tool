# AAVC Calculate Tool

<!-- Badges -->
<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  <img src="https://img.shields.io/badge/python-3.8%2B-blue.svg" alt="Python version">
</p>

A tool to calculate daily investment amounts based on the **Asymmetric Volatility-Adjusted Cost Average (AAVC)** algorithm.

## Features

- **Core Calculation Engine**: Implements the AAVC algorithm.
- **Command-Line Interface (CLI)**: Provides a 'calc' subcommand to calculate daily investment amounts.
- **Automatic Data Acquisition**: Fetches the latest stock/fund data automatically using yfinance.
- **Configuration Management**: Manage your portfolio and parameters via a simple configuration file.
- **Backtesting (Planned)**: Simulate and evaluate the strategy's performance on historical data.

## Installation

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd AAVC_calculate_tool
    ```

2.  Install the required dependencies. It is recommended to use a virtual environment.
    ```bash
    # Using requirements.txt
    pip install -r requirements.txt

    # Or, to install with development tools
    pip install .[dev]
    ```

## Usage

You can run the tool directly from the command line.

**Calculate for a single stock:**
```bash
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000
```

**Calculate for all stocks in your config file:**
```bash
python -m AAVC_calculate_tool calc --config config.yaml
```

<details>
<summary><b>AAVCアルゴリズムの詳細 (Click to expand)</b></summary>

### AAVCアルゴリズムとは？

AAVCは、**非対称ボラティリティ調整型ドルコスト平均法(Asymmetric Volatility-Adjusted Cost Average)** の略称です。これは、従来のドルコスト平均平均法をさらに進化させた投資アルゴリズムです。

従来のドルコスト平均法は、株価の変動に関わらず**常に一定額**を投資します。これにより、株価が高いときには少ない株数を、低いときには多い株数を購入し、平均購入価格を平準化する効果があります。

一方、AAVCアルゴリズムは、この「常に一定額」というルールを、**市場の状況に応じて変化させる**のが大きな特徴です。

### 仕組み

AAVCは、以下の3つの要素を組み合わせて投資額を調整します。

1.  **基準価格からの乖離率**:
    *   現在の株価が、事前に設定した**基準価格**からどれだけ離れているかを計算します。
    *   株価が基準価格より下落していれば、**投資額を増やします**。逆に、基準価格より上昇していれば、**投資額を減らします**。

2.  **非対称性係数**:
    *   株価が下落したときだけ、投資額を増やす効果を**さらに加速**させます。例えば、株価が10%下落した場合、ただ投資額を増やすだけでなく、その効果を2倍にするなど、下落局面に積極的に対応します。これが「非対称（Asymmetric）」と呼ばれる理由です。

3.  **ボラティリティ（変動幅）**:
    *   株価の変動が大きい（ボラティリティが高い）市場では、投資額の調整幅を大きくします。これにより、変動の激しい相場でも効果的に株価下落時の買い増しや上昇時の買い控えを行うことができます。

### まとめ

AAVCアルゴリズムは、ただ機械的に買い続けるのではなく、**株価の下落時に強く、上昇時には控えめに投資額を調整する**ことで、より効率的な資産形成を目指すための戦略です。特に、長期的な下落局面で効果を発揮するように設計されています。

</details>

## Dependencies

This project relies on the following Python libraries:

### Core Dependencies

These are required to run the main functionalities of the tool:

-   `numpy`: For numerical operations, especially in the AAVC calculation.
-   `yfinance`: To fetch historical stock and fund data from Yahoo Finance.
-   `PyYAML`: To parse and load configuration files in YAML format.

### Development Dependencies

These are required for development, testing, and maintaining code quality:

-   `black`: Code formatter.
-   `ruff`: Linter for code style and quality checks.
-   `mypy`: Static type checker.
-   `isort`: For sorting import statements.
-   `pytest`: Testing framework.
-   `matplotlib`: For generating plots and charts in backtesting results.

You can install all core dependencies using `pip install -r requirements.txt`.
To install all development dependencies (including core dependencies), use `pip install .[dev]` from the project root.

## Contributing

Contributions are welcome! Please read the [CONTRIBUTING.md](CONTRIBUTING.md) file for details on our coding standards and how to get started.

## License

This project is licensed under the MIT License. See the [LICENSE.md](LICENSE.md) file for details.
