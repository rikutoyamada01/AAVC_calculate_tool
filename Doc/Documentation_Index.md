# Documentation Index

## Welcome to AAVC Calculate Tool Documentation

This index provides an overview of all available documentation to help you find the information you need quickly and efficiently.

## 📚 Documentation Structure

### 🚀 Getting Started
- **[Quick Start Guide](Quick_Start_Guide.md)** - Get up and running in minutes
- **[README](../README.md)** - Main project overview and user guide

### 📋 Specifications
- **[CLI Specification](01_CLI_Specification.md)** - Command-line interface overview
- **[Data Acquisition](02_Data_Acquisition.md)** - Data fetching and validation
- **[Configuration and Logging](03_Configuration_and_Logging.md)** - Settings and logging
- **[Backtesting](04_Backtesting.md)** - Strategy testing
- **[Backtest Comparison](05_Backtest_Comparison.md)** - Performance analysis

### 🔧 Technical Details
- **[CLI Detailed Design](01_CLI_Detailed_Design.md)** - CLI implementation details
- **[Data Acquisition Detailed Design](02_Data_Acquisition_Detailed_Design.md)** - Data handling architecture
- **[Configuration and Logging Detailed Design](03_Configuration_and_Logging_Detailed_Design.md)** - Configuration system design
- **[Backtesting Detailed Design](04_Backtesting_Detailed_Design.md)** - Backtesting implementation
- **[Backtest Comparison Detailed Design](05_Backtest_Comparison_Detailed_Design.md)** - Comparison system design
- **[Monthly Notification Feature Detailed Design](07_Monthly_Notification_Feature_Detailed_Design.md)** - Monthly Notification Feature Detailed Design

### 👨‍💻 Developer Resources
- **[Developer Guide](Developer_Guide.md)** - Comprehensive development information
- **[API Reference](API_Reference.md)** - Complete API documentation

## 🎯 Choose Your Path

### For New Users
1. Start with the **[Quick Start Guide](Quick_Start_Guide.md)**
2. Read the **[README](../README.md)** for comprehensive information
3. Refer to **[Configuration and Logging](03_Configuration_and_Logging.md)** for setup details

### For Regular Users
1. Use **[CLI Specification](01_CLI_Specification.md)** for command reference
2. Check **[Data Acquisition](02_Data_Acquisition.md)** for supported tickers
3. Review **[Configuration and Logging](03_Configuration_and_Logging.md)** for advanced features

### For Developers
1. Begin with **[Developer Guide](Developer_Guide.md)** for setup and architecture
2. Use **[API Reference](API_Reference.md)** for detailed function documentation
3. Review detailed design documents for implementation insights

### For Contributors
1. Read **[Developer Guide](Developer_Guide.md)** for contribution guidelines
2. Check **[CONTRIBUTING.md](../CONTRIBUTING.md)** for coding standards
3. Review detailed design documents for architectural decisions

## 📖 Document Categories

### User Documentation
| Document | Purpose | Audience |
|----------|---------|----------|
| [Quick Start Guide](Quick_Start_Guide.md) | Get started quickly | New users |
| [README](../README.md) | Complete user guide | All users |
| [CLI Specification](01_CLI_Specification.md) | Command reference | Regular users |
| [Configuration and Logging](03_Configuration_and_Logging.md) | Setup and configuration | All users |

### Technical Documentation
| Document | Purpose | Audience |
|----------|---------|----------|
| [Developer Guide](Developer_Guide.md) | Development setup and guidelines | Developers |
| [API Reference](API_Reference.md) | Function and class documentation | Developers |
| [Data Acquisition](02_Data_Acquisition.md) | Data handling overview | Users & Developers |
| [Backtesting](04_Backtesting.md) | Strategy testing (planned) | Advanced users |

### Design Documents
| Document | Purpose | Audience |
|----------|---------|----------|
| [CLI Detailed Design](01_CLI_Detailed_Design.md) | CLI implementation details | Developers |
| [Data Acquisition Detailed Design](02_Data_Acquisition_Detailed_Design.md) | Data architecture | Developers |
| [Configuration Detailed Design](03_Configuration_and_Logging_Detailed_Design.md) | Configuration system | Developers |

## 🔍 Quick Reference

### Common Commands
```bash
# Calculate for single stock
python -m AAVC_calculate_tool calc --ticker "AAPL" --amount 10000

# Calculate from configuration
python -m AAVC_calculate_tool calc --config portfolio.yaml

# Get help
python -m AAVC_calculate_tool --help
python -m AAVC_calculate_tool calc --help
```

### Configuration Example
```yaml
default_settings:
  base_amount: 10000
  asymmetric_coefficient: 2.0

stocks:
  - ticker: "AAPL"
    base_amount: 8000
  - ticker: "SPY"
    base_amount: 12000
```

### Supported Tickers
- **US Stocks**: AAPL, SPY, QQQ, MSFT, GOOGL
- **Japanese Stocks**: 7203.T (Toyota), 6758.T (Sony)
- **ETFs**: SPY, QQQ, VTI, VOO
- **International**: ^GSPC (S&P 500), ^DJI (Dow Jones)

## 🆘 Getting Help

### Documentation Issues
- Check if you're reading the correct document for your needs
- Verify you're using the latest version of the documentation
- Look for related documents in the same category

### Tool Issues
- Review the [Troubleshooting section](../README.md#troubleshooting) in the README
- Check the [GitHub Issues](https://github.com/your-repo/AAVC_calculate_tool/issues) page
- Create a new issue with detailed information

### Feature Requests
- Use the [GitHub Issues](https://github.com/your-repo/AAVC_calculate_tool/issues) page
- Provide clear description of the desired functionality
- Include use cases and examples

## 📝 Contributing to Documentation

### How to Contribute
1. **Report Issues**: Found an error or unclear section? Report it!
2. **Suggest Improvements**: Have ideas for better organization or clarity?
3. **Submit Updates**: Fix typos, add examples, or improve explanations
4. **Translate**: Help translate documentation to other languages

### Documentation Standards
- Use clear, concise language
- Include practical examples
- Maintain consistent formatting
- Update related documents when making changes

### Getting Started with Contributions
1. Fork the repository
2. Make your changes in a feature branch
3. Submit a pull request
4. Follow the [CONTRIBUTING.md](../CONTRIBUTING.md) guidelines

## 🔄 Documentation Updates

### Recent Changes
- **v0.1.0**: Initial documentation release
- Added comprehensive user guides
- Created developer documentation
- Established documentation structure

### Planned Updates
- Backtesting documentation (when feature is implemented)
- Additional examples and use cases
- Video tutorials and screenshots
- Multi-language support

## 📞 Contact and Support

### Documentation Team
- **Maintainer**: [Your Name](mailto:you@example.com)
- **Contributors**: See [CONTRIBUTING.md](../CONTRIBUTING.md)

### Community Resources
- **GitHub Discussions**: [Link to discussions](https://github.com/your-repo/AAVC_calculate_tool/discussions)
- **Wiki**: [Link to wiki](https://github.com/your-repo/AAVC_calculate_tool/wiki)
- **Blog**: [Link to blog](https://your-blog.com)

---

**Last Updated**: August 2025  
**Version**: 0.1.0  

---

*This documentation is maintained by the AAVC Calculate Tool community. Your contributions help make it better for everyone!* 
