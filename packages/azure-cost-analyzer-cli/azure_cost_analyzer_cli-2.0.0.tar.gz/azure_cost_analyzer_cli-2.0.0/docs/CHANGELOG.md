# Changelog

All notable changes to the Azure Cost Analyzer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2025-01-XX

### Major Release - Complete Rewrite

#### Added
- **Single File Architecture**: Consolidated entire application into one comprehensive Python file
- **Enhanced CLI Interface**: Professional command-line interface with comprehensive options
- **Tag-Based Deployment**: Automated PyPI deployment via GitHub Actions on version tags
- **Comprehensive Service Driver Analysis**: Detailed tracking of which services drive daily cost changes
- **Multiple Export Formats**: Excel, PDF, and TXT reports with different focuses
- **Advanced Spike Detection**: Configurable thresholds for cost anomaly detection
- **Subscription-Level Analysis**: Detailed tracking across Azure subscriptions
- **Professional PDF Reports**: 9-page reports with charts and text analysis
- **Text-Based Reports**: Terminal-style output perfect for automation
- **PyPI Package Distribution**: Available via `pip install azure-cost-analyzer-cli`

#### Enhanced
- **Day-to-Day Cost Tracking**: Precise percentage and dollar change calculations
- **Service Impact Analysis**: Shows ALL services contributing to daily changes
- **Cost Spike Classification**: Major/Significant increase/decrease categorization
- **Report Customization**: Custom output directories and filenames
- **Performance Optimization**: Better handling of large datasets
- **Error Handling**: Comprehensive validation and user-friendly error messages

#### Technical Improvements
- **Modern Python Packaging**: Using pyproject.toml and setuptools
- **GitHub Actions CI/CD**: Automated testing and deployment
- **Documentation Structure**: Organized docs directory with comprehensive guides
- **Code Quality**: Type hints, better error handling, and modular design
- **CLI Argument Validation**: Robust input validation and helpful error messages

### CLI Features
- `--format` options: excel, pdf, txt, both, all
- `--spike-threshold` and `--min-spike-amount` for custom detection
- `--output-dir` for organized report management
- `--quiet` and `--no-summary` for automation
- Custom filename options for all output formats

### Report Enhancements
- **Excel**: 7 worksheets with comprehensive analysis
- **PDF**: 9 pages with executive summary, charts, and detailed analysis
- **TXT**: Structured text format with complete service driver breakdown

### Security & Deployment
- PyPI trusted publishing for secure deployment
- GitHub Actions with environment protection
- Tag-based version management
- Automated testing across Python versions

## [1.0.0] - 2024-XX-XX

### Initial Release
- Basic Azure cost analysis functionality
- Simple CSV processing
- Basic Excel export
- Command-line interface prototype

---

## Upcoming Features

### [2.1.0] - Planned
- [ ] **Interactive Dashboard**: Web-based dashboard for real-time monitoring
- [ ] **API Endpoints**: REST API for integration with other systems
- [ ] **Database Support**: Direct connection to Azure Cost Management APIs
- [ ] **Alert Webhooks**: Configurable alerts via Slack, Teams, email
- [ ] **Cost Forecasting**: Predictive analysis based on historical trends
- [ ] **Budget Tracking**: Integration with Azure budget alerts
- [ ] **Multi-Cloud Support**: AWS and GCP cost analysis

### [2.2.0] - Future
- [ ] **Machine Learning**: Anomaly detection using ML algorithms
- [ ] **Resource Optimization**: Recommendations for cost optimization
- [ ] **Governance Reporting**: Compliance and governance dashboards
- [ ] **Custom Metrics**: User-defined cost metrics and KPIs

---

## Migration Guide

### From 1.x to 2.0

#### Installation
```bash
# Old method
git clone repo && ./install.sh

# New method
pip install azure-cost-analyzer-cli
```

#### Usage
```bash
# Old usage
python azure_cost_analyzer.py data.csv

# New usage (both work)
azure-cost-analyzer data.csv
python azure_cost_analyzer.py data.csv
```

#### Breaking Changes
- CLI package structure changed (now single file)
- Some internal API changes for programmatic usage
- Output format defaults changed (now 'both' instead of 'excel')

#### New Features Available
- All new CLI options
- Enhanced reporting formats
- Service driver analysis
- Improved spike detection

---

**Maintained by**: Qanooni Development Team  
**Repository**: [Azure Cost Analyzer](https://github.com/CodeVerdict/azure-cost-reporter)  
**PyPI**: [azure-cost-analyzer-cli](https://pypi.org/project/azure-cost-analyzer-cli/) 