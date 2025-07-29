# Azure Cost Analyzer - User Guide

Complete guide for using the Azure Cost Analyzer CLI tool.

## Quick Start

### Installation
```bash
pip install azure-cost-analyzer-cli
```

### Basic Usage
```bash
azure-cost-analyzer your_azure_data.csv
```

## Understanding Your Data

### Required CSV Format
Your Azure usage export should contain these columns:
- `SubscriptionName` - Azure subscription name
- `SubscriptionGuid` - Subscription GUID
- `Date` - Usage date (YYYY-MM-DD)
- `ResourceGuid` - Resource identifier
- `ServiceName` - Service name
- `ServiceType` - Service category
- `ServiceRegion` - Azure region
- `ServiceResource` - Resource details
- `Quantity` - Usage quantity
- `Cost` - Cost amount

### Exporting Data from Azure
1. Go to **Cost Management + Billing** in Azure Portal
2. Select **Cost analysis**
3. Choose your time range
4. Click **Download** → **CSV**
5. Use the downloaded file with this tool

## Command Options

### Output Formats

#### Excel Report (Default)
```bash
azure-cost-analyzer data.csv --format excel
```
- Multi-sheet workbook
- Daily analysis with service drivers
- Subscription breakdowns
- Cost spike detection
- Top services analysis

#### PDF Report
```bash
azure-cost-analyzer data.csv --format pdf
```
- 9-page professional report
- Executive summary
- Charts and visualizations
- Text-based analysis pages

#### Text Report
```bash
azure-cost-analyzer data.csv --format txt
```
- Terminal-style output
- Comprehensive service driver analysis
- Perfect for automation
- Easy to parse programmatically

#### All Formats
```bash
azure-cost-analyzer data.csv --format all
```

### Analysis Configuration

#### Spike Detection
```bash
# Default: 30% change or $100 minimum
azure-cost-analyzer data.csv --spike-threshold 25 --min-spike-amount 200

# High sensitivity
azure-cost-analyzer data.csv --spike-threshold 15 --min-spike-amount 50

# Enterprise level (less sensitive)
azure-cost-analyzer data.csv --spike-threshold 50 --min-spike-amount 1000
```

#### Output Management
```bash
# Custom output directory
azure-cost-analyzer data.csv --output-dir ./reports

# Custom filenames
azure-cost-analyzer data.csv \
  --excel-output monthly_analysis.xlsx \
  --pdf-output executive_summary.pdf \
  --txt-output detailed_breakdown.txt
```

#### Display Options
```bash
# Quiet mode (minimal output)
azure-cost-analyzer data.csv --quiet

# Skip console summary
azure-cost-analyzer data.csv --no-summary

# Version information
azure-cost-analyzer --version
```

## Understanding the Analysis

### Daily Cost Tracking
The tool shows day-to-day cost changes:
```
Date         Cost ($)     Change ($)   Change (%)
17/06/2025   $5,073.00    $541.86      +12.0%
18/06/2025   $8,260.51    $3,187.51    +62.8%
```

### Service Driver Analysis
For each day, see which services caused cost changes:
```
17/06/2025 - Service Impact Drivers
COST INCREASES:
  Azure OpenAI                           +$334 (+25.2%)
  Virtual Machines                       +$156 (+8.7%)
  
COST DECREASES:
  Storage Accounts                       -$45 (-12.3%)
```

### Cost Spike Detection
Automatically identifies unusual cost patterns:
- **Major Increase**: Large dollar amount + high percentage
- **Major Decrease**: Large cost reduction
- **Significant Change**: Meets threshold criteria

### Subscription Analysis
Track costs across Azure subscriptions:
- Daily cost changes per subscription
- Percentage breakdown of total costs
- Subscription-level trends

## Use Cases

### Daily Monitoring
```bash
# Quick daily check
azure-cost-analyzer daily_export.csv --format txt --quiet
```

### Weekly Reports
```bash
# Comprehensive weekly analysis
azure-cost-analyzer weekly_data.csv --format all --output-dir ./weekly-reports
```

### Cost Investigation
```bash
# High-sensitivity spike detection for anomaly investigation
azure-cost-analyzer suspicious_period.csv --spike-threshold 10 --min-spike-amount 25
```

### Executive Reporting
```bash
# Professional reports for management
azure-cost-analyzer monthly_data.csv --format pdf --pdf-output executive_summary.pdf
```

### Automation Integration
```bash
# Automated processing with structured output
azure-cost-analyzer data.csv --format txt --quiet > cost_analysis.log
```

## Report Contents

### Excel Report Sheets
1. **Daily_Analysis** - Day-by-day costs with service drivers
2. **Subscription_Analysis** - Subscription-level tracking
3. **Service_Daily_Changes** - Detailed service changes
4. **Service_by_DateRange** - Service costs by time periods
5. **Cost_Spikes** - Spike analysis with root causes
6. **Top_Services** - Services ranked by cost
7. **Summary** - Executive summary statistics

### PDF Report Pages
1. **Executive Summary** - Key metrics and insights
2. **Daily Analysis** - Recent cost trends
3. **Service Analysis** - Service breakdown
4. **Cost Spikes** - Spike analysis
5. **Daily Trend Chart** - Cost visualization
6. **Cost Changes Chart** - Change patterns
7. **Subscription Chart** - Distribution analysis
8. **Top Services Chart** - Service comparison
9. **Spikes Chart** - Spike visualization

### Text Report Sections
- Executive summary with key metrics
- Recent daily changes with ALL service drivers
- Comprehensive service driver analysis
- Cost spike detection and analysis
- Service costs by date ranges
- Subscription breakdown
- Top services ranking

## Troubleshooting

### Common Issues

**"CSV file not found"**
- Check file path is correct
- Ensure file exists and is readable

**"No data loaded"**
- Verify CSV has required columns
- Check date format (should be YYYY-MM-DD)
- Ensure Cost column contains numeric values

**"Memory error with large files"**
- Filter data by date range in Azure before export
- Process smaller time periods
- Use `--quiet` mode to reduce memory usage

**"Permission denied writing files"**
- Check write permissions in output directory
- Use `--output-dir` to specify writable location

### Performance Tips

- **Large datasets**: Filter by date range before analysis
- **Automation**: Use `--quiet` and `--format txt` for fastest processing
- **Memory optimization**: Process monthly chunks for very large datasets
- **Network drives**: Copy files locally before processing

## Advanced Usage

### Scripting Examples

#### Bash Script for Daily Processing
```bash
#!/bin/bash
DATE=$(date +%Y%m%d)
azure-cost-analyzer daily_${DATE}.csv \
  --format txt \
  --quiet \
  --output-dir ./daily-reports \
  --txt-output daily_${DATE}_analysis.txt
```

#### PowerShell Script for Weekly Reports
```powershell
$date = Get-Date -Format "yyyyMMdd"
azure-cost-analyzer "weekly_$date.csv" `
  --format all `
  --output-dir ".\weekly-reports" `
  --spike-threshold 25
```

### Integration with Monitoring Systems

#### Log Analysis
```bash
# Generate structured output for log analysis
azure-cost-analyzer data.csv --format txt --quiet | grep "SPIKE\|INCREASE" > alerts.log
```

#### Threshold Alerting
```bash
# Check for cost spikes and alert if found
SPIKE_COUNT=$(azure-cost-analyzer data.csv --format txt --quiet | grep -c "Major Increase")
if [ $SPIKE_COUNT -gt 0 ]; then
  echo "Cost spikes detected: $SPIKE_COUNT"
  # Send alert
fi
```

## Support

For issues or feature requests:
- Check this user guide first
- Review the troubleshooting section
- Contact your system administrator
- Report bugs through your organization's IT support channels

---

**Version**: 2.0.0  
**Last Updated**: $(date +%Y-%m-%d)  
**Tool**: Azure Cost Analyzer CLI 