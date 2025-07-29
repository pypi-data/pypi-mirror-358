#!/bin/bash
# Azure Cost Analyzer - Daily Automation Example
# This script demonstrates how to automate daily cost analysis

set -e  # Exit on any error

# Configuration
DATA_DIR="/path/to/azure/exports"
REPORTS_DIR="/path/to/reports"
DATE=$(date +%Y%m%d)
AZURE_DATA_FILE="${DATA_DIR}/azure_usage_${DATE}.csv"

# Spike detection thresholds
SPIKE_THRESHOLD=30
MIN_SPIKE_AMOUNT=100

# Email settings (optional)
EMAIL_RECIPIENT="finance@company.com"
EMAIL_SUBJECT="Daily Azure Cost Analysis - ${DATE}"

echo "🚀 Starting Azure Cost Analysis for ${DATE}"

# Check if data file exists
if [ ! -f "$AZURE_DATA_FILE" ]; then
    echo "❌ Error: Azure data file not found: $AZURE_DATA_FILE"
    exit 1
fi

# Create reports directory
mkdir -p "$REPORTS_DIR"

# Run analysis with text output for automation
echo "📊 Running cost analysis..."
azure-cost-analyzer "$AZURE_DATA_FILE" \
    --format txt \
    --output-dir "$REPORTS_DIR" \
    --txt-output "daily_analysis_${DATE}.txt" \
    --spike-threshold $SPIKE_THRESHOLD \
    --min-spike-amount $MIN_SPIKE_AMOUNT \
    --quiet

# Check for cost spikes
SPIKE_COUNT=$(grep -c "Major\|Significant" "${REPORTS_DIR}/daily_analysis_${DATE}.txt" || echo "0")

if [ "$SPIKE_COUNT" -gt 0 ]; then
    echo "🚨 Cost spikes detected: $SPIKE_COUNT"
    
    # Optional: Send alert email
    if command -v mail >/dev/null 2>&1; then
        echo "Cost spikes detected in today's Azure analysis. See attached report." | \
        mail -s "$EMAIL_SUBJECT - ALERT" -A "${REPORTS_DIR}/daily_analysis_${DATE}.txt" "$EMAIL_RECIPIENT"
    fi
else
    echo "✅ No significant cost spikes detected"
fi

# Generate weekly comprehensive report on Mondays
if [ "$(date +%u)" -eq 1 ]; then
    echo "📈 Generating weekly comprehensive report..."
    
    # Get last 7 days of data (you'll need to combine files or use a weekly export)
    azure-cost-analyzer "$AZURE_DATA_FILE" \
        --format all \
        --output-dir "$REPORTS_DIR" \
        --excel-output "weekly_analysis_${DATE}.xlsx" \
        --pdf-output "weekly_executive_${DATE}.pdf" \
        --spike-threshold 25
    
    echo "📧 Weekly reports generated"
fi

echo "✅ Daily analysis completed successfully"
echo "📁 Reports saved to: $REPORTS_DIR"

# Cleanup old reports (keep last 30 days)
find "$REPORTS_DIR" -name "daily_analysis_*.txt" -mtime +30 -delete
find "$REPORTS_DIR" -name "weekly_*.xlsx" -mtime +90 -delete

echo "�� Cleanup completed" 