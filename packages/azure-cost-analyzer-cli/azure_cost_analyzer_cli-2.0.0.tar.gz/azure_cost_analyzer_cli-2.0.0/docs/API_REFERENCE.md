# API Reference

Developer reference for using Azure Cost Analyzer programmatically.

## Python Module Usage

You can import and use the Azure Cost Analyzer directly in your Python code:

```python
from azure_cost_analyzer import AzureCostAnalyzer

# Initialize analyzer
analyzer = AzureCostAnalyzer('your_data.csv')

# Load and analyze data
analyzer.load_data()
analyzer.analyze_daily_costs()
analyzer.analyze_subscription_costs()
analyzer.analyze_service_costs_by_date_ranges()
analyzer.identify_cost_spikes(threshold_percent=30.0, min_cost_change=100.0)

# Get summary statistics
summary = analyzer.get_summary_statistics()
print(f"Total cost: ${summary['total_cost']:,.2f}")

# Export reports
analyzer.export_to_excel('analysis.xlsx')
analyzer.export_to_txt('analysis.txt')
analyzer.create_pdf_report('analysis.pdf')
```

## Class Reference

### AzureCostAnalyzer

Main class for Azure cost analysis.

#### Constructor
```python
AzureCostAnalyzer(csv_file_path: str)
```

**Parameters:**
- `csv_file_path` (str): Path to Azure usage CSV file

#### Methods

##### Data Loading
```python
load_data() -> pd.DataFrame
```
Loads and preprocesses Azure usage data.

**Returns:** Pandas DataFrame with cleaned data

##### Daily Analysis
```python
analyze_daily_costs() -> pd.DataFrame
```
Analyzes day-to-day costs with percentage changes.

**Returns:** DataFrame with daily cost analysis

##### Service Analysis
```python
analyze_daily_service_changes() -> None
```
Analyzes which services drive daily cost changes.

##### Subscription Analysis
```python
analyze_subscription_costs() -> pd.DataFrame
```
Analyzes costs by subscription with day-to-day tracking.

**Returns:** DataFrame with subscription analysis

##### Service Cost Ranges
```python
analyze_service_costs_by_date_ranges(date_ranges: Optional[List[Tuple[str, str]]] = None) -> pd.DataFrame
```
Analyzes service costs grouped by date ranges.

**Parameters:**
- `date_ranges` (optional): List of (start_date, end_date) tuples

**Returns:** DataFrame with service costs by date ranges

##### Spike Detection
```python
identify_cost_spikes(threshold_percent: float = 30.0, min_cost_change: float = 100.0) -> pd.DataFrame
```
Identifies cost spikes based on thresholds.

**Parameters:**
- `threshold_percent` (float): Percentage threshold for spike detection
- `min_cost_change` (float): Minimum dollar amount for spike detection

**Returns:** DataFrame with detected cost spikes

##### Summary Statistics
```python
get_summary_statistics() -> Dict
```
Generates comprehensive summary statistics.

**Returns:** Dictionary with summary metrics

##### Top Services
```python
get_top_services(top_n: int = 10) -> pd.Series
```
Gets top N services by total cost.

**Parameters:**
- `top_n` (int): Number of top services to return

**Returns:** Series with top services

##### Export Methods
```python
export_to_excel(output_file: str = 'azure_cost_analysis.xlsx') -> None
export_to_txt(output_file: str = 'azure_cost_analysis.txt') -> None
create_pdf_report(output_file: str = 'azure_cost_analysis.pdf') -> None
```

Export analysis to various formats.

#### Properties

- `df`: Main DataFrame with Azure usage data
- `daily_summary`: DataFrame with daily cost analysis
- `subscription_summary`: DataFrame with subscription analysis
- `service_summary`: DataFrame with service cost ranges
- `spikes`: DataFrame with detected cost spikes
- `service_daily_changes`: DataFrame with service-level daily changes
- `daily_service_drivers`: Dictionary with daily service driver analysis

## Data Structures

### Daily Summary DataFrame
```python
columns = [
    'Date',                    # Date of usage
    'Cost',                    # Total daily cost
    'Previous_Day_Cost',       # Previous day cost
    'Cost_Change',             # Dollar change from previous day
    'Cost_Change_Percent',     # Percentage change
    'Date_Display'             # Formatted date string
]
```

### Service Daily Changes DataFrame
```python
columns = [
    'Date',                           # Date of usage
    'ServiceType',                    # Azure service type
    'Cost',                           # Service daily cost
    'Previous_Day_Cost',              # Previous day cost for service
    'Service_Cost_Change',            # Dollar change for service
    'Service_Cost_Change_Percent'     # Percentage change for service
]
```

### Cost Spikes DataFrame
```python
columns = [
    'Date',                    # Date of spike
    'Cost',                    # Daily cost
    'Cost_Change',             # Dollar change
    'Cost_Change_Percent',     # Percentage change
    'Spike_Type',              # Type of spike
    'Top_Service',             # Top service contributing to spike
    'Top_Service_Cost',        # Cost of top service
    'Service_Count',           # Number of services active
    'Date_Display'             # Formatted date
]
```

### Summary Statistics Dictionary
```python
{
    'period': str,                    # Analysis period
    'total_cost': float,              # Total cost
    'avg_daily_cost': float,          # Average daily cost
    'max_daily_cost': float,          # Maximum daily cost
    'min_daily_cost': float,          # Minimum daily cost
    'total_days': int,                # Number of days
    'top_services': dict,             # Top services by cost
    'subscription_totals': dict,      # Subscription cost totals
    'spikes_count': int,              # Number of detected spikes
    'unique_services': int,           # Number of unique services
    'unique_subscriptions': int,      # Number of subscriptions
    'biggest_increase': dict,         # Biggest cost increase day
    'biggest_decrease': dict          # Biggest cost decrease day
}
```

## Advanced Usage Examples

### Custom Analysis Pipeline
```python
import pandas as pd
from azure_cost_analyzer import AzureCostAnalyzer

def custom_analysis(csv_file, spike_threshold=25):
    """Custom analysis with additional processing."""
    
    # Initialize and load data
    analyzer = AzureCostAnalyzer(csv_file)
    analyzer.load_data()
    
    # Perform standard analysis
    analyzer.analyze_daily_costs()
    analyzer.analyze_subscription_costs()
    analyzer.identify_cost_spikes(threshold_percent=spike_threshold)
    
    # Custom processing
    summary = analyzer.get_summary_statistics()
    
    # Calculate additional metrics
    daily_variance = analyzer.daily_summary['Cost'].var()
    cost_trend = analyzer.daily_summary['Cost'].pct_change().mean()
    
    # Return enhanced summary
    return {
        **summary,
        'daily_variance': daily_variance,
        'cost_trend': cost_trend,
        'volatility': 'High' if daily_variance > 1000000 else 'Normal'
    }
```

### Automated Alerting
```python
def check_cost_alerts(csv_file, alert_threshold=50):
    """Check for cost alerts and return alert data."""
    
    analyzer = AzureCostAnalyzer(csv_file)
    analyzer.load_data()
    analyzer.analyze_daily_costs()
    analyzer.identify_cost_spikes(threshold_percent=alert_threshold)
    
    alerts = []
    
    # Check for recent spikes
    recent_spikes = analyzer.spikes[
        analyzer.spikes['Date'] >= (pd.Timestamp.now() - pd.Timedelta(days=7))
    ]
    
    for _, spike in recent_spikes.iterrows():
        alerts.append({
            'type': 'cost_spike',
            'date': spike['Date'].strftime('%Y-%m-%d'),
            'amount': spike['Cost'],
            'change': spike['Cost_Change'],
            'service': spike['Top_Service'],
            'severity': 'high' if abs(spike['Cost_Change']) > 1000 else 'medium'
        })
    
    return alerts
```

### Data Export Customization
```python
def export_custom_report(analyzer, output_dir='./reports'):
    """Export customized reports with additional analysis."""
    
    import os
    os.makedirs(output_dir, exist_ok=True)
    
    # Standard exports
    analyzer.export_to_excel(f'{output_dir}/standard_analysis.xlsx')
    
    # Custom CSV exports
    analyzer.daily_summary.to_csv(f'{output_dir}/daily_costs.csv', index=False)
    analyzer.spikes.to_csv(f'{output_dir}/cost_spikes.csv', index=False)
    
    # Top services analysis
    top_services = analyzer.get_top_services(20)
    top_services.to_csv(f'{output_dir}/top_services.csv')
    
    # Custom summary JSON
    import json
    summary = analyzer.get_summary_statistics()
    with open(f'{output_dir}/summary.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
```

### Integration with Monitoring Systems
```python
def send_to_monitoring_system(csv_file):
    """Send metrics to monitoring system."""
    
    analyzer = AzureCostAnalyzer(csv_file)
    analyzer.load_data()
    analyzer.analyze_daily_costs()
    
    # Get latest metrics
    latest_cost = analyzer.daily_summary.iloc[-1]['Cost']
    cost_change = analyzer.daily_summary.iloc[-1]['Cost_Change']
    
    # Send to monitoring (example with custom function)
    metrics = {
        'azure.cost.daily': latest_cost,
        'azure.cost.change': cost_change,
        'azure.cost.services': analyzer.df['ServiceType'].nunique()
    }
    
    # send_metrics_to_datadog(metrics)  # Example integration
    return metrics
```

## CLI Integration

### Programmatic CLI Usage
```python
import subprocess
import json

def run_analysis_cli(csv_file, format='txt', quiet=True):
    """Run CLI analysis programmatically."""
    
    cmd = [
        'azure-cost-analyzer',
        csv_file,
        '--format', format
    ]
    
    if quiet:
        cmd.append('--quiet')
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        return result.stdout
    else:
        raise Exception(f"CLI failed: {result.stderr}")
```

## Error Handling

### Common Exceptions
```python
try:
    analyzer = AzureCostAnalyzer('data.csv')
    analyzer.load_data()
except FileNotFoundError:
    print("CSV file not found")
except pd.errors.EmptyDataError:
    print("CSV file is empty")
except KeyError as e:
    print(f"Required column missing: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Data Validation
```python
def validate_data(analyzer):
    """Validate loaded data."""
    
    required_columns = ['Date', 'Cost', 'ServiceType', 'SubscriptionName']
    
    for col in required_columns:
        if col not in analyzer.df.columns:
            raise ValueError(f"Missing required column: {col}")
    
    if analyzer.df.empty:
        raise ValueError("No data loaded")
    
    if analyzer.df['Cost'].isna().all():
        raise ValueError("No valid cost data")
    
    return True
```

---

**Version**: 2.0.0  
**Module**: azure_cost_analyzer  
**Python**: 3.7+ 