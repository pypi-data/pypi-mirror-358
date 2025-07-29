#!/usr/bin/env python3
"""
Azure Cost Analyzer - Python Integration Example

This script demonstrates how to use the Azure Cost Analyzer
programmatically for custom analysis and integration.
"""

import os
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from azure_cost_analyzer import AzureCostAnalyzer

def analyze_costs(csv_file, spike_threshold=30, min_spike_amount=100):
    """
    Perform comprehensive cost analysis and return structured results.
    """
    print(f"🔍 Analyzing costs from: {csv_file}")
    
    # Initialize analyzer
    analyzer = AzureCostAnalyzer(csv_file)
    
    # Load and analyze data
    analyzer.load_data()
    analyzer.analyze_daily_costs()
    analyzer.analyze_subscription_costs()
    analyzer.analyze_service_costs_by_date_ranges()
    analyzer.identify_cost_spikes(spike_threshold, min_spike_amount)
    
    # Get comprehensive summary
    summary = analyzer.get_summary_statistics()
    
    # Add custom metrics
    daily_costs = analyzer.daily_summary['Cost']
    summary['volatility'] = daily_costs.std()
    summary['trend'] = daily_costs.pct_change().mean() * 100
    
    # Recent activity (last 7 days)
    recent_data = analyzer.daily_summary.tail(7)
    summary['recent_avg'] = recent_data['Cost'].mean()
    summary['recent_trend'] = recent_data['Cost'].pct_change().mean() * 100
    
    return analyzer, summary

def check_alerts(analyzer, summary, alert_thresholds):
    """
    Check for various alert conditions and return alert data.
    """
    alerts = []
    
    # Cost spike alerts
    recent_spikes = analyzer.spikes[
        analyzer.spikes['Date'] >= (datetime.now() - timedelta(days=7))
    ]
    
    for _, spike in recent_spikes.iterrows():
        severity = 'high' if abs(spike['Cost_Change']) > 1000 else 'medium'
        alerts.append({
            'type': 'cost_spike',
            'severity': severity,
            'date': spike['Date'].strftime('%Y-%m-%d'),
            'amount': spike['Cost'],
            'change': spike['Cost_Change'],
            'service': spike['Top_Service'],
            'message': f"Cost spike detected: {spike['Spike_Type']}"
        })
    
    # Budget threshold alerts
    if 'budget_threshold' in alert_thresholds:
        if summary['recent_avg'] > alert_thresholds['budget_threshold']:
            alerts.append({
                'type': 'budget_threshold',
                'severity': 'high',
                'message': f"Average daily cost (${summary['recent_avg']:.2f}) exceeds threshold"
            })
    
    # Trend alerts
    if summary['recent_trend'] > alert_thresholds.get('trend_threshold', 20):
        alerts.append({
            'type': 'trend_alert',
            'severity': 'medium',
            'message': f"Cost trend increasing at {summary['recent_trend']:.1f}% rate"
        })
    
    return alerts

def generate_custom_reports(analyzer, output_dir):
    """
    Generate custom reports with additional analysis.
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Standard reports
    analyzer.export_to_excel(f'{output_dir}/comprehensive_analysis.xlsx')
    analyzer.export_to_txt(f'{output_dir}/detailed_analysis.txt')
    
    # Custom JSON report for API integration
    summary = analyzer.get_summary_statistics()
    
    # Add service breakdown
    top_services = analyzer.get_top_services(10).to_dict()
    summary['top_services_detailed'] = top_services
    
    # Add recent daily data
    recent_daily = analyzer.daily_summary.tail(30).to_dict('records')
    summary['recent_daily_data'] = recent_daily
    
    # Add subscription details
    subscription_details = analyzer.subscription_summary.groupby('SubscriptionName').agg({
        'Cost': ['sum', 'mean', 'std']
    }).to_dict()
    summary['subscription_details'] = subscription_details
    
    # Save JSON report
    with open(f'{output_dir}/analysis_data.json', 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"📊 Custom reports generated in: {output_dir}")
    return summary

def send_alert_email(alerts, summary, email_config):
    """
    Send alert email with cost analysis summary.
    """
    if not alerts or not email_config.get('enabled', False):
        return
    
    # Create email message
    msg = MIMEMultipart()
    msg['From'] = email_config['from']
    msg['To'] = ', '.join(email_config['to'])
    msg['Subject'] = f"Azure Cost Alert - {datetime.now().strftime('%Y-%m-%d')}"
    
    # Email body
    body = f"""
    Azure Cost Analysis Alert
    
    Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    Summary:
    - Total Cost: ${summary['total_cost']:,.2f}
    - Recent Average: ${summary['recent_avg']:,.2f}
    - Trend: {summary['recent_trend']:+.1f}%
    
    Alerts Detected: {len(alerts)}
    
    """
    
    for alert in alerts:
        body += f"\n⚠️  {alert['type'].upper()}: {alert['message']}"
    
    body += f"\n\nFor detailed analysis, check the reports or run the analyzer manually."
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Send email
    try:
        server = smtplib.SMTP(email_config['smtp_server'], email_config['smtp_port'])
        if email_config.get('use_tls', True):
            server.starttls()
        if email_config.get('username'):
            server.login(email_config['username'], email_config['password'])
        
        text = msg.as_string()
        server.sendmail(email_config['from'], email_config['to'], text)
        server.quit()
        
        print("📧 Alert email sent successfully")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

def main():
    """
    Main automation workflow.
    """
    # Configuration
    config = {
        'csv_file': 'azure_usage_data.csv',
        'output_dir': './reports',
        'spike_threshold': 25,
        'min_spike_amount': 200,
        'alert_thresholds': {
            'budget_threshold': 1000,  # Daily budget threshold
            'trend_threshold': 15      # Trend increase threshold (%)
        },
        'email_config': {
            'enabled': False,  # Set to True to enable email alerts
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'from': 'alerts@company.com',
            'to': ['finance@company.com', 'devops@company.com'],
            'username': 'your_email@gmail.com',
            'password': 'your_app_password',
            'use_tls': True
        }
    }
    
    try:
        # Perform analysis
        analyzer, summary = analyze_costs(
            config['csv_file'],
            config['spike_threshold'],
            config['min_spike_amount']
        )
        
        # Check for alerts
        alerts = check_alerts(analyzer, summary, config['alert_thresholds'])
        
        # Generate reports
        report_data = generate_custom_reports(analyzer, config['output_dir'])
        
        # Print summary
        print(f"\n📊 Analysis Summary:")
        print(f"   Total Cost: ${summary['total_cost']:,.2f}")
        print(f"   Recent Avg: ${summary['recent_avg']:,.2f}")
        print(f"   Trend: {summary['recent_trend']:+.1f}%")
        print(f"   Alerts: {len(alerts)}")
        
        # Send alerts if any
        if alerts:
            print(f"\n🚨 Alerts detected:")
            for alert in alerts:
                print(f"   - {alert['type']}: {alert['message']}")
            
            send_alert_email(alerts, summary, config['email_config'])
        else:
            print("\n✅ No alerts detected")
        
        # Return data for further processing
        return {
            'summary': summary,
            'alerts': alerts,
            'analyzer': analyzer
        }
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        raise

if __name__ == '__main__':
    # Example usage
    result = main()
    
    # You can now use the result data for further processing
    # For example, send to monitoring systems, update dashboards, etc.
    
    print(f"\n🎉 Analysis completed successfully!")
    print(f"   Check reports in: ./reports/")
    print(f"   JSON data: ./reports/analysis_data.json") 