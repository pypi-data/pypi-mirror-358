# Azure Cost Analyzer

[![PyPI version](https://badge.fury.io/py/azure-cost-analyzer-cli.svg)](https://badge.fury.io/py/azure-cost-analyzer-cli)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub Actions](https://github.com/CodeVerdict/azure-cost-reporter/workflows/Test%20Package/badge.svg)](https://github.com/CodeVerdict/azure-cost-reporter/actions)

**Enterprise-grade Azure cost analysis tool with comprehensive reporting and day-to-day cost tracking.**

Azure Cost Analyzer provides detailed insights into Azure spending patterns, identifies cost drivers at the service level, and generates professional reports for budget management and cost optimization initiatives.

---

## Quick Start

### Installation

```bash
pip install azure-cost-analyzer-cli
```

### Basic Usage

```bash
# Analyze your Azure usage data
azure-cost-analyzer your_azure_usage.csv

# Generate all report formats
azure-cost-analyzer data.csv --format all

# Custom spike detection
azure-cost-analyzer data.csv --spike-threshold 25 --min-spike-amount 500
```

---

## Key Features

### **Comprehensive Cost Analysis**
- **Day-to-day cost tracking** with percentage change calculations
- **Service-level cost drivers** - identify which Azure services drive daily changes
- **Subscription analysis** across multiple Azure subscriptions
- **Cost spike detection** with configurable thresholds

### **Advanced Reporting**
- **Excel Reports**: Multi-sheet workbooks with detailed analysis
- **PDF Reports**: 9-page professional reports with charts and insights
- **Text Reports**: Structured output perfect for automation

### **Professional CLI**
- Enterprise-grade command-line interface
- Flexible output options and customization
- Quiet mode for automated processing
- Comprehensive help and documentation

### **Service Driver Analysis**
Unique feature that shows exactly which Azure services cause daily cost increases or decreases:

```
17/06/2025 - Service Impact Drivers
COST INCREASES:
  Azure OpenAI                           +$334 (+25.2%)
  Virtual Machines                       +$156 (+8.7%)
  
COST DECREASES:
  Storage Accounts                       -$45 (-12.3%)
```

---

## Requirements

- **Python 3.7+**
- **Azure usage CSV export** from Azure Cost Management
- **Dependencies**: pandas, matplotlib, openpyxl, seaborn (auto-installed)

---

## Usage Examples

### Basic Analysis
```bash
# Standard analysis with Excel and PDF output
azure-cost-analyzer azure_usage_data.csv

# Text-only output for automation
azure-cost-analyzer data.csv --format txt --quiet
```

### Advanced Configuration
```bash
# Custom output directory and spike detection
azure-cost-analyzer data.csv \
  --output-dir ./monthly-reports \
  --spike-threshold 25 \
  --min-spike-amount 500 \
  --format all

# Enterprise-level analysis with custom filenames
azure-cost-analyzer data.csv \
  --excel-output financial_analysis.xlsx \
  --pdf-output executive_report.pdf \
  --spike-threshold 50
```

### Automation & Scripting
```bash
# Daily automated analysis
azure-cost-analyzer daily_export.csv --format txt --quiet > daily_summary.log

# Weekly comprehensive reports
azure-cost-analyzer weekly_export.csv --format all --output-dir ./weekly-reports
```

---

## Report Formats

| Format | Description | Use Case |
|--------|-------------|----------|
| **Excel** | Multi-sheet workbook with 7 detailed worksheets | Detailed analysis, data manipulation |
| **PDF** | 9-page professional report with charts | Executive reporting, presentations |
| **TXT** | Structured text with comprehensive service drivers | Automation, monitoring systems |

### Excel Report Contents
- Daily analysis with service drivers
- Subscription-level tracking
- Service costs by date ranges
- Cost spike analysis
- Top services ranking
- Executive summary

### PDF Report Contents
- Executive summary with key metrics
- Cost trend visualizations
- Service analysis charts
- Spike detection graphs
- Subscription distribution

---

## Use Cases

### **Enterprise Cost Management**
- Monthly executive reporting
- Budget variance analysis
- Cost optimization initiatives
- Departmental chargebacks

### **Cost Investigation**
- Anomaly detection and investigation
- Service-level cost driver analysis
- Unexpected bill analysis
- Resource optimization planning

### **Automation & Monitoring**
- Daily cost monitoring
- Automated alerting systems
- Integration with monitoring tools
- Scheduled reporting

### **Financial Planning**
- Trend analysis for budgeting
- Forecasting support data
- Cost allocation tracking
- ROI analysis preparation

---

## Command Reference

### Required Arguments
- `csv_file` - Path to Azure usage CSV export file

### Output Format Options
- `--format {excel,pdf,txt,both,all}` - Report format (default: both)

### Analysis Configuration
- `--spike-threshold FLOAT` - Spike detection percentage threshold (default: 30)
- `--min-spike-amount FLOAT` - Minimum spike amount in dollars (default: 100)

### File Management
- `--output-dir DIR` - Output directory for reports
- `--excel-output FILE` - Custom Excel filename
- `--pdf-output FILE` - Custom PDF filename
- `--txt-output FILE` - Custom text filename

### Display Options
- `--quiet` - Minimal output for automation
- `--no-summary` - Skip console analysis summary
- `--version` - Show version information

---

## Integration

### Python API
```python
from azure_cost_analyzer import AzureCostAnalyzer

analyzer = AzureCostAnalyzer('data.csv')
analyzer.load_data()
analyzer.analyze_daily_costs()
summary = analyzer.get_summary_statistics()
```

### Automation Scripts
```bash
# Bash automation example
#!/bin/bash
azure-cost-analyzer daily_$(date +%Y%m%d).csv \
  --format txt --quiet \
  --output-dir ./reports
```

---

## Documentation

- **[User Guide](docs/USER_GUIDE.md)** - Complete usage documentation
- **[API Reference](docs/API_REFERENCE.md)** - Developer documentation
- **[Deployment Guide](docs/DEPLOYMENT.md)** - GitHub Actions deployment
- **[Changelog](docs/CHANGELOG.md)** - Version history and updates

---

## Installation Methods

### PyPI (Recommended)
```bash
pip install azure-cost-analyzer-cli
```

### Development Installation
```bash
git clone https://github.com/CodeVerdict/azure-cost-reporter.git
cd azure-cost-reporter
pip install -e .
```

### Manual Installation
```bash
git clone https://github.com/CodeVerdict/azure-cost-reporter.git
cd azure-cost-reporter
pip install -r requirements.txt
chmod +x azure_cost_analyzer.py
```

---

## Sample Output

### Console Summary
```
AZURE COST ANALYSIS SUMMARY
===============================================
Period: 2025-01-16 to 2025-06-26
Total Cost: $115,668.79
Average Daily Cost: $738.65
Maximum Daily Cost: $9,985.27
Minimum Daily Cost: $82.01
Cost Spikes Detected: 37

SUBSCRIPTION BREAKDOWN:
  • production: $64,912.34 (56.1%)
  • non-production: $48,012.45 (41.5%)
  • management: $2,744.00 (2.4%)

TOP 5 SERVICES:
  1. Azure OpenAI: $66,553.87 (57.5%)
  2. Virtual Machines: $23,445.12 (20.3%)
  3. Storage Accounts: $12,334.56 (10.7%)
```

### Service Driver Analysis
```
RECENT DAILY CHANGES (Last 10 days):
  25/6/2025: $614.65 (+649.8%) 
      Top driver: Azure OpenAI (+$534)
  26/6/2025: $82.01 (-86.7%)
      Top driver: Azure OpenAI (-$532)
```

---

## Contributing

We welcome contributions! Please see our contributing guidelines for details.

### Development Setup
```bash
git clone https://github.com/CodeVerdict/azure-cost-reporter.git
cd azure-cost-reporter
pip install -e ".[dev]"
```

### Running Tests
```bash
pytest
azure-cost-analyzer --version
azure-cost-analyzer --help
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Enterprise Support

**Qanooni Internal Tool** - For enterprise support, feature requests, or custom implementations, contact the Qanooni development team.

### Version Information
- **Current Version**: 2.0.0
- **Python Support**: 3.7+
- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Status**: Production Ready

---

## Recent Updates

- **v2.0.0**: Complete rewrite with single-file architecture
- **Enhanced CLI**: Professional command-line interface
- **Service Drivers**: Detailed service-level cost analysis
- **Multiple Formats**: Excel, PDF, and TXT reporting
- **PyPI Distribution**: Available via pip install
- **GitHub Actions**: Automated testing and deployment

---

<div align="center">

**[Documentation](docs/) | [Quick Start](#quick-start) | [Download](https://pypi.org/project/azure-cost-analyzer-cli/) | [Issues](https://github.com/CodeVerdict/azure-cost-reporter/issues)**

Made with care by the Qanooni Team

</div> 