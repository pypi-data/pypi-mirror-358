#!/usr/bin/env python3
"""
Comprehensive Azure Cost Analyzer
Single file solution for complete Azure cost analysis with:
- Day-to-day cost tracking with percentage changes
- Service costs grouped by date ranges
- Subscription-level analysis
- Spike identification
- Excel and PDF export
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages
import matplotlib.patches as mpatches
from typing import Dict, List, Tuple, Optional
import argparse
import sys
import warnings
warnings.filterwarnings('ignore')

class AzureCostAnalyzer:
    def __init__(self, csv_file_path: str):
        """Initialize the analyzer with the CSV file path"""
        self.csv_file_path = csv_file_path
        self.df = None
        self.daily_summary = None
        self.service_summary = None
        self.subscription_summary = None
        self.spikes = None
        self.service_daily_changes = None
        self.daily_service_drivers = None
        
    def load_data(self) -> pd.DataFrame:
        """Load and preprocess the Azure usage data"""
        print("📊 Loading Azure usage data...")
        
        # Load the CSV file
        self.df = pd.read_csv(self.csv_file_path)
        
        # Convert Date column to datetime
        self.df['Date'] = pd.to_datetime(self.df['Date'])
        
        # Convert Cost and Quantity to numeric
        self.df['Cost'] = pd.to_numeric(self.df['Cost'], errors='coerce')
        self.df['Quantity'] = pd.to_numeric(self.df['Quantity'], errors='coerce')
        
        # Fill NaN values with 0
        self.df['Cost'] = self.df['Cost'].fillna(0)
        self.df['Quantity'] = self.df['Quantity'].fillna(0)
        
        print(f"✅ Loaded {len(self.df)} records from {self.df['Date'].min().strftime('%Y-%m-%d')} to {self.df['Date'].max().strftime('%Y-%m-%d')}")
        print(f"📈 Subscriptions: {self.df['SubscriptionName'].nunique()}")
        print(f"🔧 Services: {self.df['ServiceType'].nunique()}")
        return self.df
    
    def analyze_daily_costs(self) -> pd.DataFrame:
        """Analyze day-to-day costs with percentage changes"""
        print("📅 Analyzing daily costs and day-to-day changes...")
        
        # Group by date and sum costs
        daily_costs = self.df.groupby('Date')['Cost'].sum().reset_index()
        daily_costs = daily_costs.sort_values('Date')
        
        # Calculate day-to-day changes
        daily_costs['Previous_Day_Cost'] = daily_costs['Cost'].shift(1)
        daily_costs['Cost_Change'] = daily_costs['Cost'] - daily_costs['Previous_Day_Cost']
        daily_costs['Cost_Change_Percent'] = (daily_costs['Cost_Change'] / daily_costs['Previous_Day_Cost']) * 100
        
        # Format the data
        daily_costs['Cost_Change_Percent'] = daily_costs['Cost_Change_Percent'].round(2)
        daily_costs['Cost'] = daily_costs['Cost'].round(2)
        daily_costs['Cost_Change'] = daily_costs['Cost_Change'].round(2)
        
        # Add formatted date for display
        daily_costs['Date_Display'] = daily_costs['Date'].dt.strftime('%d/%m/%Y')
        
        self.daily_summary = daily_costs
        
        # Analyze service-level daily changes
        self.analyze_daily_service_changes()
        
        return daily_costs
    
    def analyze_daily_service_changes(self):
        """Analyze which services drive daily cost changes"""
        print("🔍 Analyzing service-level daily changes...")
        
        # Get daily costs by service
        service_daily = self.df.groupby(['Date', 'ServiceType'])['Cost'].sum().reset_index()
        service_daily = service_daily.sort_values(['ServiceType', 'Date'])
        
        # Calculate day-to-day changes for each service
        service_daily['Previous_Day_Cost'] = service_daily.groupby('ServiceType')['Cost'].shift(1)
        service_daily['Service_Cost_Change'] = service_daily['Cost'] - service_daily['Previous_Day_Cost']
        service_daily['Service_Cost_Change_Percent'] = (
            service_daily['Service_Cost_Change'] / service_daily['Previous_Day_Cost']
        ) * 100
        
        # Store service changes
        self.service_daily_changes = service_daily
        
        # For each date, find ALL services contributing to increases/decreases
        self.daily_service_drivers = {}
        
        for date in self.daily_summary['Date'].unique():
            date_changes = service_daily[
                (service_daily['Date'] == date) & 
                (service_daily['Service_Cost_Change'].notna())
            ].copy()
            
            if not date_changes.empty:
                # Sort by absolute change to get biggest movers
                date_changes['Abs_Change'] = date_changes['Service_Cost_Change'].abs()
                date_changes = date_changes.sort_values('Abs_Change', ascending=False)
                
                # Get top 3 increases and decreases (for summary)
                increases = date_changes[date_changes['Service_Cost_Change'] > 0].head(3)
                decreases = date_changes[date_changes['Service_Cost_Change'] < 0].head(3)
                
                # Get ALL significant service changes (for comprehensive analysis)
                # Filter for meaningful changes: > $10 or > 5% to focus on real impact
                all_increases = date_changes[
                    (date_changes['Service_Cost_Change'] > 0) & 
                    ((date_changes['Service_Cost_Change'] > 10) | (date_changes['Service_Cost_Change_Percent'] > 5))
                ].sort_values('Service_Cost_Change', ascending=False)
                
                all_decreases = date_changes[
                    (date_changes['Service_Cost_Change'] < 0) & 
                    ((date_changes['Service_Cost_Change'].abs() > 10) | (date_changes['Service_Cost_Change_Percent'].abs() > 5))
                ].sort_values('Service_Cost_Change', ascending=True)
                
                # Get ALL services with any change (for complete tracking)
                all_changes = date_changes[date_changes['Service_Cost_Change'] != 0].copy()
                
                self.daily_service_drivers[date] = {
                    'increases': increases,  # Top 3 for summary
                    'decreases': decreases,  # Top 3 for summary
                    'top_changes': date_changes.head(5),  # Top 5 overall
                    'all_significant_increases': all_increases,  # ALL meaningful increases
                    'all_significant_decreases': all_decreases,  # ALL meaningful decreases
                    'all_changes': all_changes  # Complete daily service impact
                }
    
    def analyze_subscription_costs(self) -> pd.DataFrame:
        """Analyze costs by subscription with day-to-day tracking"""
        print("🏢 Analyzing subscription-level costs...")
        
        # Group by date and subscription
        sub_daily = self.df.groupby(['Date', 'SubscriptionName'])['Cost'].sum().reset_index()
        
        # Calculate day-to-day changes for each subscription
        subscription_analysis = []
        
        for subscription in sub_daily['SubscriptionName'].unique():
            sub_data = sub_daily[sub_daily['SubscriptionName'] == subscription].sort_values('Date')
            sub_data['Previous_Day_Cost'] = sub_data['Cost'].shift(1)
            sub_data['Cost_Change'] = sub_data['Cost'] - sub_data['Previous_Day_Cost']
            sub_data['Cost_Change_Percent'] = (sub_data['Cost_Change'] / sub_data['Previous_Day_Cost']) * 100
            subscription_analysis.append(sub_data)
        
        subscription_summary = pd.concat(subscription_analysis, ignore_index=True)
        subscription_summary = subscription_summary.round(2)
        
        self.subscription_summary = subscription_summary
        return subscription_summary
    
    def analyze_service_costs_by_date_ranges(self, date_ranges: Optional[List[Tuple[str, str]]] = None) -> pd.DataFrame:
        """Analyze service costs grouped by date ranges"""
        print("🔧 Analyzing service costs by date ranges...")
        
        if date_ranges is None:
            # Create weekly date ranges automatically
            start_date = self.df['Date'].min()
            end_date = self.df['Date'].max()
            date_ranges = []
            
            current_date = start_date
            while current_date <= end_date:
                week_end = min(current_date + timedelta(days=6), end_date)
                date_ranges.append((current_date.strftime('%Y-%m-%d'), week_end.strftime('%Y-%m-%d')))
                current_date = week_end + timedelta(days=1)
        
        service_range_analysis = []
        
        for start_str, end_str in date_ranges:
            start_date = pd.to_datetime(start_str)
            end_date = pd.to_datetime(end_str)
            
            # Filter data for this date range
            range_data = self.df[(self.df['Date'] >= start_date) & (self.df['Date'] <= end_date)]
            
            if len(range_data) > 0:
                # Group by service type
                service_costs = range_data.groupby('ServiceType')['Cost'].sum().reset_index()
                service_costs['Date_Range'] = f"{start_str} to {end_str}"
                service_costs['Start_Date'] = start_date
                service_costs['End_Date'] = end_date
                service_costs['Days_in_Range'] = (end_date - start_date).days + 1
                service_range_analysis.append(service_costs)
        
        if service_range_analysis:
            service_summary = pd.concat(service_range_analysis, ignore_index=True)
            service_summary = service_summary.round(2)
            service_summary = service_summary.sort_values(['Start_Date', 'Cost'], ascending=[True, False])
        else:
            service_summary = pd.DataFrame()
        
        self.service_summary = service_summary
        return service_summary
    
    def identify_cost_spikes(self, threshold_percent: float = 30.0, min_cost_change: float = 100.0) -> pd.DataFrame:
        """Identify cost spikes based on percentage change and absolute change"""
        print(f"🚨 Identifying cost spikes (>{threshold_percent}% change or >${min_cost_change}$ change)...")
        
        if self.daily_summary is None:
            self.analyze_daily_costs()
        
        # Identify spikes based on percentage OR absolute change
        spikes = self.daily_summary[
            (abs(self.daily_summary['Cost_Change_Percent']) > threshold_percent) |
            (abs(self.daily_summary['Cost_Change']) > min_cost_change)
        ].copy()
        
        # Add spike classification
        spikes['Spike_Type'] = spikes.apply(lambda row: 
            'Major Increase' if row['Cost_Change'] > min_cost_change and row['Cost_Change_Percent'] > threshold_percent
            else 'Major Decrease' if row['Cost_Change'] < -min_cost_change and row['Cost_Change_Percent'] < -threshold_percent
            else 'Significant Increase' if row['Cost_Change'] > 0
            else 'Significant Decrease', axis=1)
        
        # Add service breakdown for spike days
        spike_details = []
        for _, spike_row in spikes.iterrows():
            spike_date = spike_row['Date']
            day_services = self.df[self.df['Date'] == spike_date].groupby('ServiceType')['Cost'].sum().sort_values(ascending=False)
            
            spike_detail = spike_row.copy()
            spike_detail['Top_Service'] = day_services.index[0] if len(day_services) > 0 else 'N/A'
            spike_detail['Top_Service_Cost'] = day_services.iloc[0] if len(day_services) > 0 else 0
            spike_detail['Service_Count'] = len(day_services)
            spike_details.append(spike_detail)
        
        if spike_details:
            spikes_detailed = pd.DataFrame(spike_details)
        else:
            spikes_detailed = spikes
        
        self.spikes = spikes_detailed
        return spikes_detailed
    
    def get_top_services(self, top_n: int = 10) -> pd.Series:
        """Get top N services by total cost"""
        return self.df.groupby('ServiceType')['Cost'].sum().sort_values(ascending=False).head(top_n)
    
    def get_summary_statistics(self) -> Dict:
        """Generate comprehensive summary statistics"""
        if self.daily_summary is None:
            self.analyze_daily_costs()
        if self.subscription_summary is None:
            self.analyze_subscription_costs()
        if self.service_summary is None:
            self.analyze_service_costs_by_date_ranges()
        if self.spikes is None:
            self.identify_cost_spikes()
        
        total_cost = self.df['Cost'].sum()
        avg_daily_cost = self.daily_summary['Cost'].mean()
        max_daily_cost = self.daily_summary['Cost'].max()
        min_daily_cost = self.daily_summary['Cost'].min()
        
        # Get date range
        start_date = self.df['Date'].min()
        end_date = self.df['Date'].max()
        
        # Top services
        top_services = self.get_top_services(5)
        
        # Subscription breakdown
        subscription_totals = self.df.groupby('SubscriptionName')['Cost'].sum().sort_values(ascending=False)
        
        # Biggest cost changes
        biggest_increase = self.daily_summary.loc[self.daily_summary['Cost_Change'].idxmax()] if not self.daily_summary['Cost_Change'].isna().all() else None
        biggest_decrease = self.daily_summary.loc[self.daily_summary['Cost_Change'].idxmin()] if not self.daily_summary['Cost_Change'].isna().all() else None
        
        summary = {
            'period': f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}",
            'total_cost': round(total_cost, 2),
            'avg_daily_cost': round(avg_daily_cost, 2),
            'max_daily_cost': round(max_daily_cost, 2),
            'min_daily_cost': round(min_daily_cost, 2),
            'total_days': len(self.daily_summary),
            'top_services': top_services.to_dict(),
            'subscription_totals': subscription_totals.to_dict(),
            'spikes_count': len(self.spikes),
            'unique_services': self.df['ServiceType'].nunique(),
            'unique_subscriptions': self.df['SubscriptionName'].nunique(),
            'biggest_increase': biggest_increase,
            'biggest_decrease': biggest_decrease
        }
        
        return summary
    
    def print_analysis_summary(self):
        """Print a comprehensive analysis summary"""
        summary = self.get_summary_statistics()
        
        print("\n" + "="*60)
        print("📊 AZURE COST ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📅 Period: {summary['period']}")
        print(f"💰 Total Cost: ${summary['total_cost']:,.2f}")
        print(f"📈 Average Daily Cost: ${summary['avg_daily_cost']:,.2f}")
        print(f"🔺 Maximum Daily Cost: ${summary['max_daily_cost']:,.2f}")
        print(f"🔻 Minimum Daily Cost: ${summary['min_daily_cost']:,.2f}")
        print(f"📊 Total Days: {summary['total_days']}")
        print(f"🚨 Cost Spikes Detected: {summary['spikes_count']}")
        
        print(f"\n🏢 SUBSCRIPTION BREAKDOWN:")
        for sub, cost in summary['subscription_totals'].items():
            percentage = (cost / summary['total_cost']) * 100
            print(f"  • {sub}: ${cost:,.2f} ({percentage:.1f}%)")
        
        print(f"\n🔧 TOP 5 SERVICES:")
        for i, (service, cost) in enumerate(list(summary['top_services'].items())[:5], 1):
            percentage = (cost / summary['total_cost']) * 100
            print(f"  {i}. {service}: ${cost:,.2f} ({percentage:.1f}%)")
        
        if summary['biggest_increase'] is not None:
            print(f"\n📈 BIGGEST COST INCREASE:")
            inc = summary['biggest_increase']
            print(f"  Date: {inc['Date_Display']}")
            print(f"  Cost: ${inc['Cost']:,.2f}")
            print(f"  Change: +${inc['Cost_Change']:,.2f} (+{inc['Cost_Change_Percent']:.1f}%)")
        
        if summary['biggest_decrease'] is not None:
            print(f"\n📉 BIGGEST COST DECREASE:")
            dec = summary['biggest_decrease']
            print(f"  Date: {dec['Date_Display']}")
            print(f"  Cost: ${dec['Cost']:,.2f}")
            print(f"  Change: ${dec['Cost_Change']:,.2f} ({dec['Cost_Change_Percent']:.1f}%)")
        
        # Show recent daily changes
        print(f"\n📅 RECENT DAILY CHANGES (Last 10 days):")
        recent_days = self.daily_summary.tail(10)
        for _, day in recent_days.iterrows():
            change_symbol = "📈" if day['Cost_Change'] > 0 else "📉" if day['Cost_Change'] < 0 else "➡️"
            if pd.notna(day['Cost_Change']):
                print(f"  {change_symbol} {day['Date_Display']}: ${day['Cost']:,.2f} ({day['Cost_Change_Percent']:+.1f}%)")
                
                # Show top service drivers for this day
                if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers and day['Date'] in self.daily_service_drivers:
                    drivers = self.daily_service_drivers[day['Date']]
                    if not drivers['top_changes'].empty:
                        top_driver = drivers['top_changes'].iloc[0]
                        driver_emoji = "🔺" if top_driver['Service_Cost_Change'] > 0 else "🔻"
                        print(f"      {driver_emoji} Top driver: {top_driver['ServiceType'][:30]} (${top_driver['Service_Cost_Change']:+,.2f})")
            else:
                print(f"  {change_symbol} {day['Date_Display']}: ${day['Cost']:,.2f} (First day)")
        
        print("="*60)
    
    def export_to_txt(self, output_file: str = 'azure_cost_analysis.txt'):
        """Export comprehensive analysis to TXT file (terminal-style output)"""
        print(f"📄 Exporting analysis to TXT: {output_file}")
        
        summary = self.get_summary_statistics()
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("="*80 + "\n")
            f.write("AZURE COST ANALYSIS REPORT\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("="*80 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 40 + "\n")
            f.write(f"Period: {summary['period']}\n")
            f.write(f"Total Cost: ${summary['total_cost']:,.2f}\n")
            f.write(f"Average Daily Cost: ${summary['avg_daily_cost']:,.2f}\n")
            f.write(f"Maximum Daily Cost: ${summary['max_daily_cost']:,.2f}\n")
            f.write(f"Minimum Daily Cost: ${summary['min_daily_cost']:,.2f}\n")
            f.write(f"Total Days: {summary['total_days']}\n")
            f.write(f"Cost Spikes Detected: {summary['spikes_count']}\n")
            f.write(f"Unique Services: {summary['unique_services']}\n")
            f.write(f"Unique Subscriptions: {summary['unique_subscriptions']}\n\n")
            
            # Subscription Breakdown
            f.write("SUBSCRIPTION BREAKDOWN\n")
            f.write("-" * 40 + "\n")
            for sub, cost in summary['subscription_totals'].items():
                percentage = (cost / summary['total_cost']) * 100
                f.write(f"• {sub}: ${cost:,.2f} ({percentage:.1f}%)\n")
            f.write("\n")
            
            # Top Services
            f.write("TOP 10 SERVICES BY COST\n")
            f.write("-" * 40 + "\n")
            top_services = self.get_top_services(10)
            for i, (service, cost) in enumerate(top_services.items(), 1):
                percentage = (cost / summary['total_cost']) * 100
                f.write(f"{i:2d}. {service:<40} ${cost:>12,.2f} ({percentage:>5.1f}%)\n")
            f.write("\n")
            
            # Recent Daily Changes with ALL Service Drivers in Same Row
            f.write("RECENT DAILY CHANGES WITH ALL SERVICE DRIVERS (Last 15 days)\n")
            f.write("-" * 120 + "\n")
            f.write(f"{'Date':<12} {'Cost ($)':<12} {'Change ($)':<12} {'Change (%)':<12} {'All Service Drivers (>$10 or >5%)':<60}\n")
            f.write("-" * 120 + "\n")
            recent_days = self.daily_summary.tail(15)
            for _, day in recent_days.iterrows():
                if pd.notna(day['Cost_Change']):
                    # Get ALL significant service drivers for this day
                    drivers_info = "N/A"
                    if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers and day['Date'] in self.daily_service_drivers:
                        drivers = self.daily_service_drivers[day['Date']]
                        driver_parts = []
                        
                        # Add significant increases
                        if 'all_significant_increases' in drivers and not drivers['all_significant_increases'].empty:
                            for _, service in drivers['all_significant_increases'].head(5).iterrows():  # Top 5 to fit in row
                                service_short = service['ServiceType'][:15] + '..' if len(service['ServiceType']) > 15 else service['ServiceType']
                                driver_parts.append(f"{service_short}(+${service['Service_Cost_Change']:,.0f})")
                        
                        # Add significant decreases
                        if 'all_significant_decreases' in drivers and not drivers['all_significant_decreases'].empty:
                            for _, service in drivers['all_significant_decreases'].head(3).iterrows():  # Top 3 to fit in row
                                service_short = service['ServiceType'][:15] + '..' if len(service['ServiceType']) > 15 else service['ServiceType']
                                driver_parts.append(f"{service_short}(${service['Service_Cost_Change']:,.0f})")
                        
                        if driver_parts:
                            drivers_info = " | ".join(driver_parts[:8])  # Limit to 8 total to fit in row
                    
                    f.write(f"{day['Date_Display']:<12} ${day['Cost']:<11,.2f} ${day['Cost_Change']:<11,.2f} {day['Cost_Change_Percent']:>+8.1f}% {drivers_info:<60}\n")
                else:
                    f.write(f"{day['Date_Display']:<12} ${day['Cost']:<11,.2f} {'N/A':<12} {'N/A':<12} {'First day':<60}\n")
            f.write("\n")
            
            # Comprehensive Daily Service Drivers Analysis
            if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers:
                f.write("COMPREHENSIVE DAILY SERVICE DRIVERS (Last 10 days)\n")
                f.write("-" * 100 + "\n")
                f.write("Shows ALL services that drove meaningful cost changes each day (>$10 or >5%)\n\n")
                
                recent_dates = sorted(list(self.daily_service_drivers.keys()))[-10:]
                for date in recent_dates:
                    date_str = date.strftime('%d/%m/%Y')
                    drivers = self.daily_service_drivers[date]
                    
                    f.write(f"{date_str} - All Service Impact Drivers\n")
                    f.write("-" * 80 + "\n")
                    
                    # Show ALL significant increases in one section
                    if 'all_significant_increases' in drivers and not drivers['all_significant_increases'].empty:
                        f.write("  COST INCREASES:\n")
                        for _, service in drivers['all_significant_increases'].iterrows():
                            service_name = service['ServiceType'][:40] + '...' if len(service['ServiceType']) > 40 else service['ServiceType']
                            f.write(f"    {service_name:<43} +${service['Service_Cost_Change']:>8,.0f} (+{service['Service_Cost_Change_Percent']:>5.1f}%)\n")
                        f.write("\n")
                    
                    # Show ALL significant decreases in one section
                    if 'all_significant_decreases' in drivers and not drivers['all_significant_decreases'].empty:
                        f.write("  COST DECREASES:\n")
                        for _, service in drivers['all_significant_decreases'].iterrows():
                            service_name = service['ServiceType'][:40] + '...' if len(service['ServiceType']) > 40 else service['ServiceType']
                            f.write(f"    {service_name:<43} ${service['Service_Cost_Change']:>9,.0f} ({service['Service_Cost_Change_Percent']:>5.1f}%)\n")
                        f.write("\n")
                    
                    # Summary line showing total services with changes
                    if 'all_changes' in drivers:
                        total_services = len(drivers['all_changes'])
                        total_increase = drivers['all_changes'][drivers['all_changes']['Service_Cost_Change'] > 0]['Service_Cost_Change'].sum()
                        total_decrease = drivers['all_changes'][drivers['all_changes']['Service_Cost_Change'] < 0]['Service_Cost_Change'].sum()
                        f.write(f"  SUMMARY: {total_services} services changed | Total increase: +${total_increase:,.0f} | Total decrease: ${total_decrease:,.0f}\n")
                    
                    f.write("\n")
                f.write("\n")
            
            # Cost Spikes
            if not self.spikes.empty:
                f.write("COST SPIKES DETECTED\n")
                f.write("-" * 40 + "\n")
                f.write(f"{'Date':<12} {'Cost ($)':<12} {'Change ($)':<12} {'Change (%)':<12} {'Type':<20} {'Top Service':<30}\n")
                f.write("-" * 100 + "\n")
                for _, spike in self.spikes.iterrows():
                    top_service = spike['Top_Service'][:28] if len(spike['Top_Service']) > 28 else spike['Top_Service']
                    f.write(f"{spike['Date_Display']:<12} ${spike['Cost']:<11,.2f} ${spike['Cost_Change']:<11,.2f} {spike['Cost_Change_Percent']:>+8.1f}% {spike['Spike_Type']:<20} {top_service:<30}\n")
                f.write("\n")
            
            # Service Costs by Date Ranges
            if not self.service_summary.empty:
                f.write("SERVICE COSTS BY DATE RANGES (Top 20 per period)\n")
                f.write("-" * 80 + "\n")
                
                # Group by date range
                for date_range in self.service_summary['Date_Range'].unique():
                    range_data = self.service_summary[self.service_summary['Date_Range'] == date_range]
                    range_data = range_data.sort_values('Cost', ascending=False).head(20)
                    
                    f.write(f"\n{date_range}\n")
                    f.write("-" * 60 + "\n")
                    f.write(f"{'Service Type':<40} {'Cost ($)':<15} {'Days':<5}\n")
                    f.write("-" * 60 + "\n")
                    
                    for _, service in range_data.iterrows():
                        service_name = service['ServiceType'][:38] if len(service['ServiceType']) > 38 else service['ServiceType']
                        f.write(f"{service_name:<40} ${service['Cost']:<14,.2f} {service['Days_in_Range']:<5}\n")
                f.write("\n")
            
            # Biggest Changes
            if summary['biggest_increase'] is not None:
                f.write("BIGGEST COST INCREASE\n")
                f.write("-" * 40 + "\n")
                inc = summary['biggest_increase']
                f.write(f"Date: {inc['Date_Display']}\n")
                f.write(f"Cost: ${inc['Cost']:,.2f}\n")
                f.write(f"Change: +${inc['Cost_Change']:,.2f} (+{inc['Cost_Change_Percent']:.1f}%)\n\n")
            
            if summary['biggest_decrease'] is not None:
                f.write("BIGGEST COST DECREASE\n")
                f.write("-" * 40 + "\n")
                dec = summary['biggest_decrease']
                f.write(f"Date: {dec['Date_Display']}\n")
                f.write(f"Cost: ${dec['Cost']:,.2f}\n")
                f.write(f"Change: ${dec['Cost_Change']:,.2f} ({dec['Cost_Change_Percent']:.1f}%)\n\n")
            
            f.write("="*80 + "\n")
            f.write("END OF REPORT\n")
            f.write("="*80 + "\n")
        
        print(f"✅ TXT report exported: {output_file}")
    
    def export_to_excel(self, output_file: str = 'azure_cost_analysis.xlsx'):
        """Export comprehensive analysis to Excel with same detail as TXT export"""
        print(f"📊 Exporting analysis to Excel: {output_file}")
        
        with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
            # 1. Enhanced Daily Analysis with ALL Service Drivers
            daily_export = self.daily_summary[['Date_Display', 'Cost', 'Cost_Change', 'Cost_Change_Percent']].copy()
            
            # Add comprehensive service driver information (same as TXT export)
            if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers:
                all_service_drivers = []
                top_drivers = []
                driver_changes = []
                
                for _, row in daily_export.iterrows():
                    date_key = None
                    for date in self.daily_service_drivers.keys():
                        if date.strftime('%d/%m/%Y') == row['Date_Display']:
                            date_key = date
                            break
                    
                    if date_key and date_key in self.daily_service_drivers:
                        drivers = self.daily_service_drivers[date_key]
                        
                        # Get comprehensive driver info (same logic as TXT export)
                        driver_parts = []
                        if 'all_significant_increases' in drivers and not drivers['all_significant_increases'].empty:
                            for _, service in drivers['all_significant_increases'].head(5).iterrows():
                                service_short = service['ServiceType'][:15] + '..' if len(service['ServiceType']) > 15 else service['ServiceType']
                                driver_parts.append(f"{service_short}(+${service['Service_Cost_Change']:,.0f})")
                        
                        if 'all_significant_decreases' in drivers and not drivers['all_significant_decreases'].empty:
                            for _, service in drivers['all_significant_decreases'].head(3).iterrows():
                                service_short = service['ServiceType'][:15] + '..' if len(service['ServiceType']) > 15 else service['ServiceType']
                                driver_parts.append(f"{service_short}(${service['Service_Cost_Change']:,.0f})")
                        
                        all_drivers_text = " | ".join(driver_parts[:8]) if driver_parts else "N/A"
                        all_service_drivers.append(all_drivers_text)
                        
                        # Top driver (for backward compatibility)
                        if not drivers['top_changes'].empty:
                            top_driver = drivers['top_changes'].iloc[0]
                            top_drivers.append(top_driver['ServiceType'])
                            driver_changes.append(top_driver['Service_Cost_Change'])
                        else:
                            top_drivers.append('N/A')
                            driver_changes.append(0)
                    else:
                        all_service_drivers.append('First day' if pd.isna(row['Cost_Change']) else 'N/A')
                        top_drivers.append('N/A')
                        driver_changes.append(0)
                
                daily_export['All Service Drivers (>$10 or >5%)'] = all_service_drivers
                daily_export['Top Service Driver'] = top_drivers
                daily_export['Driver Change ($)'] = driver_changes
            
            daily_export.columns = ['Date', 'Daily Cost ($)', 'Change ($)', 'Change (%)', 'All Service Drivers (>$10 or >5%)', 'Top Service Driver', 'Driver Change ($)']
            daily_export.to_excel(writer, sheet_name='Daily_Analysis', index=False)
            
            # 2. Comprehensive Daily Service Drivers (NEW - same as TXT export)
            if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers:
                service_driver_data = []
                recent_dates = sorted(list(self.daily_service_drivers.keys()))[-15:]  # Last 15 days
                
                for date in recent_dates:
                    date_str = date.strftime('%d/%m/%Y')
                    drivers = self.daily_service_drivers[date]
                    
                    # Add increases
                    if 'all_significant_increases' in drivers and not drivers['all_significant_increases'].empty:
                        for _, service in drivers['all_significant_increases'].iterrows():
                            service_driver_data.append({
                                'Date': date_str,
                                'Type': 'INCREASE',
                                'Service': service['ServiceType'],
                                'Change ($)': service['Service_Cost_Change'],
                                'Change (%)': service['Service_Cost_Change_Percent'],
                                'Daily Cost ($)': service['Cost']
                            })
                    
                    # Add decreases
                    if 'all_significant_decreases' in drivers and not drivers['all_significant_decreases'].empty:
                        for _, service in drivers['all_significant_decreases'].iterrows():
                            service_driver_data.append({
                                'Date': date_str,
                                'Type': 'DECREASE',
                                'Service': service['ServiceType'],
                                'Change ($)': service['Service_Cost_Change'],
                                'Change (%)': service['Service_Cost_Change_Percent'],
                                'Daily Cost ($)': service['Cost']
                            })
                
                if service_driver_data:
                    service_drivers_df = pd.DataFrame(service_driver_data)
                    service_drivers_df.to_excel(writer, sheet_name='Service_Drivers_Detail', index=False)
            
            # 3. Subscription analysis
            sub_export = self.subscription_summary[['Date', 'SubscriptionName', 'Cost', 'Cost_Change', 'Cost_Change_Percent']].copy()
            sub_export['Date'] = sub_export['Date'].dt.strftime('%Y-%m-%d')
            sub_export.columns = ['Date', 'Subscription', 'Cost ($)', 'Change ($)', 'Change (%)']
            sub_export.to_excel(writer, sheet_name='Subscription_Analysis', index=False)
            
            # 4. Service costs by date ranges (enhanced)
            if not self.service_summary.empty:
                service_export = self.service_summary[['Date_Range', 'ServiceType', 'Cost', 'Days_in_Range']].copy()
                service_export.columns = ['Date Range', 'Service Type', 'Total Cost ($)', 'Days']
                # Add percentage of total for each range
                for date_range in service_export['Date Range'].unique():
                    range_total = service_export[service_export['Date Range'] == date_range]['Total Cost ($)'].sum()
                    service_export.loc[service_export['Date Range'] == date_range, 'Percentage of Range'] = \
                        (service_export.loc[service_export['Date Range'] == date_range, 'Total Cost ($)'] / range_total * 100).round(1)
                service_export.to_excel(writer, sheet_name='Service_by_DateRange', index=False)
            
            # 5. Cost spikes (enhanced)
            if not self.spikes.empty:
                spikes_export = self.spikes[['Date_Display', 'Cost', 'Cost_Change', 'Cost_Change_Percent', 'Spike_Type', 'Top_Service', 'Top_Service_Cost']].copy()
                spikes_export.columns = ['Date', 'Cost ($)', 'Change ($)', 'Change (%)', 'Spike Type', 'Top Service', 'Top Service Cost ($)']
                spikes_export.to_excel(writer, sheet_name='Cost_Spikes', index=False)
            
            # 6. Service daily changes detail (enhanced)
            if hasattr(self, 'service_daily_changes') and self.service_daily_changes is not None:
                service_changes_export = self.service_daily_changes[
                    ['Date', 'ServiceType', 'Cost', 'Service_Cost_Change', 'Service_Cost_Change_Percent']
                ].copy()
                service_changes_export['Date'] = service_changes_export['Date'].dt.strftime('%Y-%m-%d')
                service_changes_export.columns = ['Date', 'Service Type', 'Daily Cost ($)', 'Change ($)', 'Change (%)']
                # Filter for significant changes only (same as TXT logic)
                significant_changes = service_changes_export[
                    (service_changes_export['Change ($)'].abs() > 10) | 
                    (service_changes_export['Change (%)'].abs() > 5)
                ].copy()
                significant_changes.to_excel(writer, sheet_name='Significant_Service_Changes', index=False)
                
                # Also include all changes
                service_changes_export.to_excel(writer, sheet_name='All_Service_Changes', index=False)
            
            # 7. Top services summary (enhanced)
            top_services = self.get_top_services(20)
            summary = self.get_summary_statistics()
            top_services_df = pd.DataFrame({
                'Service Type': top_services.index, 
                'Total Cost ($)': top_services.values,
                'Percentage of Total': (top_services.values / summary['total_cost'] * 100).round(1)
            })
            top_services_df.to_excel(writer, sheet_name='Top_Services', index=False)
            
            # 8. Executive Summary (same as TXT export)
            summary_data = []
            summary_data.append(['Analysis Period', summary['period']])
            summary_data.append(['Total Cost ($)', f"${summary['total_cost']:,.2f}"])
            summary_data.append(['Average Daily Cost ($)', f"${summary['avg_daily_cost']:,.2f}"])
            summary_data.append(['Maximum Daily Cost ($)', f"${summary['max_daily_cost']:,.2f}"])
            summary_data.append(['Minimum Daily Cost ($)', f"${summary['min_daily_cost']:,.2f}"])
            summary_data.append(['Total Days', summary['total_days']])
            summary_data.append(['Cost Spikes Detected', summary['spikes_count']])
            summary_data.append(['Unique Services', summary['unique_services']])
            summary_data.append(['Unique Subscriptions', summary['unique_subscriptions']])
            
            # Add subscription breakdown
            summary_data.append(['', ''])  # Empty row
            summary_data.append(['SUBSCRIPTION BREAKDOWN', ''])
            for sub, cost in summary['subscription_totals'].items():
                percentage = (cost / summary['total_cost']) * 100
                summary_data.append([f"• {sub}", f"${cost:,.2f} ({percentage:.1f}%)"])
            
            # Add biggest changes
            if summary['biggest_increase'] is not None:
                inc = summary['biggest_increase']
                summary_data.append(['', ''])
                summary_data.append(['BIGGEST COST INCREASE', ''])
                summary_data.append(['Date', inc['Date_Display']])
                summary_data.append(['Cost', f"${inc['Cost']:,.2f}"])
                summary_data.append(['Change', f"+${inc['Cost_Change']:,.2f} (+{inc['Cost_Change_Percent']:.1f}%)"])
            
            if summary['biggest_decrease'] is not None:
                dec = summary['biggest_decrease']
                summary_data.append(['', ''])
                summary_data.append(['BIGGEST COST DECREASE', ''])
                summary_data.append(['Date', dec['Date_Display']])
                summary_data.append(['Cost', f"${dec['Cost']:,.2f}"])
                summary_data.append(['Change', f"${dec['Cost_Change']:,.2f} ({dec['Cost_Change_Percent']:.1f}%)"])
            
            summary_df = pd.DataFrame(summary_data, columns=['Metric', 'Value'])
            summary_df.to_excel(writer, sheet_name='Executive_Summary', index=False)
        
        print(f"✅ Excel report exported with comprehensive analysis: {output_file}")
    
    def create_pdf_report(self, output_file: str = 'azure_cost_analysis.pdf'):
        """Generate comprehensive PDF report with text and charts"""
        print(f"📄 Generating PDF report: {output_file}")
        
        with PdfPages(output_file) as pdf:
            # Page 1: Executive Summary
            fig = plt.figure(figsize=(8.5, 11))
            self._create_summary_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 2: Daily Cost Analysis (Text)
            fig = plt.figure(figsize=(8.5, 11))
            self._create_daily_analysis_text_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 3: Service Analysis (Text)
            fig = plt.figure(figsize=(8.5, 11))
            self._create_service_analysis_text_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 4: Cost Spikes Analysis (Text)
            fig = plt.figure(figsize=(8.5, 11))
            self._create_spikes_text_page(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 5: Daily Cost Trend Chart
            fig = plt.figure(figsize=(8.5, 11))
            self._create_daily_trend_chart(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 6: Daily Cost Changes Chart
            fig = plt.figure(figsize=(8.5, 11))
            self._create_cost_changes_chart(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 7: Subscription Analysis Chart
            fig = plt.figure(figsize=(8.5, 11))
            self._create_subscription_chart(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 8: Top Services Chart
            fig = plt.figure(figsize=(8.5, 11))
            self._create_top_services_chart(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
            
            # Page 9: Cost Spikes Chart
            fig = plt.figure(figsize=(8.5, 11))
            self._create_spikes_chart(fig)
            pdf.savefig(fig, bbox_inches='tight')
            plt.close(fig)
        
        print(f"✅ PDF report generated: {output_file}")
    
    def _create_summary_page(self, fig):
        """Create executive summary page with text-based format"""
        fig.clear()
        summary = self.get_summary_statistics()
        
        # Create the same format as TXT export
        summary_text = f"""AZURE COST ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

EXECUTIVE SUMMARY
{'-'*30}
Period: {summary['period']}
Total Cost: ${summary['total_cost']:,.2f}
Average Daily Cost: ${summary['avg_daily_cost']:,.2f}
Maximum Daily Cost: ${summary['max_daily_cost']:,.2f}
Minimum Daily Cost: ${summary['min_daily_cost']:,.2f}
Total Days: {summary['total_days']}
Cost Spikes Detected: {summary['spikes_count']}
Unique Services: {summary['unique_services']}
Unique Subscriptions: {summary['unique_subscriptions']}

SUBSCRIPTION BREAKDOWN
{'-'*30}"""
        
        for sub, cost in summary['subscription_totals'].items():
            percentage = (cost / summary['total_cost']) * 100
            summary_text += f"\n• {sub}: ${cost:,.2f} ({percentage:.1f}%)"
        
        summary_text += f"\n\nTOP 10 SERVICES BY COST\n{'-'*30}"
        top_services = self.get_top_services(10)
        for i, (service, cost) in enumerate(top_services.items(), 1):
            percentage = (cost / summary['total_cost']) * 100
            service_short = service[:35] + '...' if len(service) > 35 else service
            summary_text += f"\n{i:2d}. {service_short:<38} ${cost:>10,.2f} ({percentage:>4.1f}%)"
        
        if summary['biggest_increase'] is not None:
            inc = summary['biggest_increase']
            summary_text += f"\n\nBIGGEST COST INCREASE\n{'-'*30}"
            date_str = inc['Date'].strftime('%d/%m/%Y') if hasattr(inc['Date'], 'strftime') else str(inc['Date'])
            summary_text += f"\nDate: {date_str}"
            summary_text += f"\nCost: ${inc['Cost']:,.2f}"
            summary_text += f"\nChange: +${inc['Cost_Change']:,.2f} (+{inc['Cost_Change_Percent']:.1f}%)"
        
        if summary['biggest_decrease'] is not None:
            dec = summary['biggest_decrease']
            summary_text += f"\n\nBIGGEST COST DECREASE\n{'-'*30}"
            date_str = dec['Date'].strftime('%d/%m/%Y') if hasattr(dec['Date'], 'strftime') else str(dec['Date'])
            summary_text += f"\nDate: {date_str}"
            summary_text += f"\nCost: ${dec['Cost']:,.2f}"
            summary_text += f"\nChange: ${dec['Cost_Change']:,.2f} ({dec['Cost_Change_Percent']:.1f}%)"
        
        fig.text(0.05, 0.95, summary_text, fontsize=8, fontfamily='monospace',
                verticalalignment='top', transform=fig.transFigure)
    
    def _create_daily_trend_chart(self, fig):
        """Create daily cost trend chart"""
        fig.clear()
        ax = fig.add_subplot(111)
        
        ax.plot(self.daily_summary['Date'], self.daily_summary['Cost'], 
               marker='o', linewidth=2, markersize=2, color='#2E86AB')
        
        # Add trend line
        x_numeric = np.arange(len(self.daily_summary))
        z = np.polyfit(x_numeric, self.daily_summary['Cost'], 1)
        p = np.poly1d(z)
        ax.plot(self.daily_summary['Date'], p(x_numeric), "--", alpha=0.7, color='red', linewidth=2, label='Trend')
        
        ax.set_title('Daily Cost Trend Analysis', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Daily Cost (USD)', fontsize=12)
        ax.grid(True, alpha=0.3)
        ax.legend()
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        fig.tight_layout()
    
    def _create_cost_changes_chart(self, fig):
        """Create daily cost changes chart"""
        fig.clear()
        ax = fig.add_subplot(111)
        
        colors = ['red' if x < 0 else 'green' for x in self.daily_summary['Cost_Change'].fillna(0)]
        
        ax.bar(self.daily_summary['Date'], self.daily_summary['Cost_Change'].fillna(0), 
               color=colors, alpha=0.7)
        
        ax.set_title('Daily Cost Changes', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Date', fontsize=12)
        ax.set_ylabel('Cost Change (USD)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='y')
        ax.axhline(y=0, color='black', linestyle='-', alpha=0.5)
        
        red_patch = mpatches.Patch(color='red', alpha=0.7, label='Cost Decrease')
        green_patch = mpatches.Patch(color='green', alpha=0.7, label='Cost Increase')
        ax.legend(handles=[red_patch, green_patch])
        
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        fig.tight_layout()
    
    def _create_subscription_chart(self, fig):
        """Create subscription breakdown chart"""
        fig.clear()
        ax = fig.add_subplot(111)
        
        summary = self.get_summary_statistics()
        subscriptions = list(summary['subscription_totals'].keys())
        costs = list(summary['subscription_totals'].values())
        
        colors = plt.cm.Set3(np.linspace(0, 1, len(subscriptions)))
        wedges, texts, autotexts = ax.pie(costs, labels=subscriptions, autopct='%1.1f%%', 
                                         colors=colors, startangle=90)
        
        ax.set_title('Cost Distribution by Subscription', fontsize=16, fontweight='bold', pad=20)
        
        # Add cost values to labels
        for i, (subscription, cost) in enumerate(summary['subscription_totals'].items()):
            texts[i].set_text(f'{subscription}\n${cost:,.0f}')
        
        fig.tight_layout()
    
    def _create_top_services_chart(self, fig):
        """Create top services chart"""
        fig.clear()
        ax = fig.add_subplot(111)
        
        top_services = self.get_top_services(10)
        
        bars = ax.barh(range(len(top_services)), top_services.values, color='skyblue', alpha=0.8)
        ax.set_yticks(range(len(top_services)))
        ax.set_yticklabels([service[:40] + '...' if len(service) > 40 else service 
                           for service in top_services.index], fontsize=9)
        
        ax.set_title('Top 10 Services by Total Cost', fontsize=16, fontweight='bold', pad=20)
        ax.set_xlabel('Total Cost (USD)', fontsize=12)
        ax.grid(True, alpha=0.3, axis='x')
        
        for i, (bar, value) in enumerate(zip(bars, top_services.values)):
            ax.text(value + max(top_services.values) * 0.01, i, f'${value:,.0f}', 
                   va='center', fontsize=8)
        
        fig.tight_layout()
    
    def _create_spikes_chart(self, fig):
        """Create cost spikes visualization"""
        fig.clear()
        
        if self.spikes.empty:
            fig.text(0.5, 0.5, 'No significant cost spikes detected', 
                    ha='center', va='center', fontsize=14,
                    bbox=dict(boxstyle="round,pad=1", facecolor="lightgreen", alpha=0.8))
        else:
            ax = fig.add_subplot(111)
            
            # Create scatter plot of spikes
            increases = self.spikes[self.spikes['Cost_Change'] > 0]
            decreases = self.spikes[self.spikes['Cost_Change'] < 0]
            
            if not increases.empty:
                ax.scatter(increases['Date'], increases['Cost'], 
                          s=abs(increases['Cost_Change']), c='red', alpha=0.6, label='Cost Increases')
            
            if not decreases.empty:
                ax.scatter(decreases['Date'], decreases['Cost'], 
                          s=abs(decreases['Cost_Change']), c='blue', alpha=0.6, label='Cost Decreases')
            
            ax.set_title('Cost Spikes Analysis', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Daily Cost (USD)', fontsize=12)
            ax.grid(True, alpha=0.3)
            ax.legend()
            
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45)
        
        fig.suptitle('Cost Spikes Detection', fontsize=16, fontweight='bold', y=0.95)
        fig.tight_layout()
    
    def _create_daily_analysis_text_page(self, fig):
        """Create daily cost analysis text page (same format as TXT export)"""
        fig.clear()
        
        # Use same format as TXT export
        text_content = f"""RECENT DAILY CHANGES WITH ALL SERVICE DRIVERS (Last 15 days)
{'-'*85}
{'Date':<12} {'Cost ($)':<12} {'Change ($)':<12} {'Change (%)':<12} {'All Service Drivers (>$10 or >5%)':<30}
{'-'*85}"""
        
        recent_days = self.daily_summary.tail(15)
        for _, day in recent_days.iterrows():
            if pd.notna(day['Cost_Change']):
                # Get ALL significant service drivers for this day (same logic as TXT)
                drivers_info = "N/A"
                if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers and day['Date'] in self.daily_service_drivers:
                    drivers = self.daily_service_drivers[day['Date']]
                    driver_parts = []
                    
                    # Add significant increases
                    if 'all_significant_increases' in drivers and not drivers['all_significant_increases'].empty:
                        for _, service in drivers['all_significant_increases'].head(3).iterrows():  # Top 3 for PDF space
                            service_short = service['ServiceType'][:12] + '..' if len(service['ServiceType']) > 12 else service['ServiceType']
                            driver_parts.append(f"{service_short}(+${service['Service_Cost_Change']:,.0f})")
                    
                    # Add significant decreases
                    if 'all_significant_decreases' in drivers and not drivers['all_significant_decreases'].empty:
                        for _, service in drivers['all_significant_decreases'].head(2).iterrows():  # Top 2 for PDF space
                            service_short = service['ServiceType'][:12] + '..' if len(service['ServiceType']) > 12 else service['ServiceType']
                            driver_parts.append(f"{service_short}(${service['Service_Cost_Change']:,.0f})")
                    
                    if driver_parts:
                        drivers_info = " | ".join(driver_parts[:5])  # Limit to 5 total for PDF
                
                text_content += f"\n{day['Date_Display']:<12} ${day['Cost']:<11,.0f} ${day['Cost_Change']:<11,.0f} {day['Cost_Change_Percent']:>+7.1f}% {drivers_info:<30}"
            else:
                text_content += f"\n{day['Date_Display']:<12} ${day['Cost']:<11,.0f} {'N/A':<12} {'N/A':<12} {'First day':<30}"
        
        # Add comprehensive service drivers analysis (same as TXT export)
        text_content += f"\n\nCOMPREHENSIVE DAILY SERVICE DRIVERS (Last 8 days)\n{'-'*75}"
        text_content += f"\nShows ALL services that drove meaningful cost changes each day (>$10 or >5%)\n"
        
        if hasattr(self, 'daily_service_drivers') and self.daily_service_drivers:
            recent_dates = sorted(list(self.daily_service_drivers.keys()))[-8:]  # Last 8 days for PDF space
            for date in recent_dates:
                date_str = date.strftime('%d/%m/%Y')
                drivers = self.daily_service_drivers[date]
                
                text_content += f"\n\n{date_str} - All Service Impact Drivers\n{'-'*50}"
                
                # Show ALL significant increases
                if 'all_significant_increases' in drivers and not drivers['all_significant_increases'].empty:
                    text_content += f"\n  COST INCREASES:"
                    for _, service in drivers['all_significant_increases'].head(5).iterrows():  # Top 5 for PDF
                        service_name = service['ServiceType'][:25] + '...' if len(service['ServiceType']) > 25 else service['ServiceType']
                        text_content += f"\n    {service_name:<28} +${service['Service_Cost_Change']:>6,.0f} (+{service['Service_Cost_Change_Percent']:>4.1f}%)"
                
                # Show ALL significant decreases
                if 'all_significant_decreases' in drivers and not drivers['all_significant_decreases'].empty:
                    text_content += f"\n  COST DECREASES:"
                    for _, service in drivers['all_significant_decreases'].head(5).iterrows():  # Top 5 for PDF
                        service_name = service['ServiceType'][:25] + '...' if len(service['ServiceType']) > 25 else service['ServiceType']
                        text_content += f"\n    {service_name:<28} ${service['Service_Cost_Change']:>7,.0f} ({service['Service_Cost_Change_Percent']:>4.1f}%)"
                
                # Summary line
                if 'all_changes' in drivers:
                    total_services = len(drivers['all_changes'])
                    total_increase = drivers['all_changes'][drivers['all_changes']['Service_Cost_Change'] > 0]['Service_Cost_Change'].sum()
                    total_decrease = drivers['all_changes'][drivers['all_changes']['Service_Cost_Change'] < 0]['Service_Cost_Change'].sum()
                    text_content += f"\n  SUMMARY: {total_services} services changed | +${total_increase:,.0f} | ${total_decrease:,.0f}"
        
        fig.text(0.02, 0.98, text_content, fontsize=6, fontfamily='monospace',
                verticalalignment='top', transform=fig.transFigure)
    
    def _create_service_analysis_text_page(self, fig):
        """Create service analysis text page (same format as TXT export)"""
        fig.clear()
        
        summary = self.get_summary_statistics()
        
        # Use same format as TXT export
        text_content = f"""TOP 10 SERVICES BY COST
{'-'*40}"""
        
        top_services = self.get_top_services(10)
        for i, (service, cost) in enumerate(top_services.items(), 1):
            percentage = (cost / summary['total_cost']) * 100
            service_short = service[:35] + '...' if len(service) > 35 else service
            text_content += f"\n{i:2d}. {service_short:<38} ${cost:>10,.2f} ({percentage:>5.1f}%)"
        
        # Add service costs by date ranges (same as TXT export)
        text_content += f"\n\nSERVICE COSTS BY DATE RANGES (Top 10 per period)\n{'-'*60}"
        
        if not self.service_summary.empty:
            # Group by date range
            for date_range in self.service_summary['Date_Range'].unique():
                range_data = self.service_summary[self.service_summary['Date_Range'] == date_range]
                range_data = range_data.sort_values('Cost', ascending=False).head(10)  # Top 10 for PDF space
                
                text_content += f"\n\n{date_range}\n{'-'*45}"
                text_content += f"\n{'Service Type':<30} {'Cost ($)':<12} {'Days':<5}"
                text_content += f"\n{'-'*45}"
                
                for _, service in range_data.iterrows():
                    service_name = service['ServiceType'][:28] if len(service['ServiceType']) > 28 else service['ServiceType']
                    text_content += f"\n{service_name:<30} ${service['Cost']:<11,.0f} {service['Days_in_Range']:<5}"
        
        # Add biggest changes (same as TXT export)
        if summary['biggest_increase'] is not None:
            text_content += f"\n\nBIGGEST COST INCREASE\n{'-'*30}"
            inc = summary['biggest_increase']
            text_content += f"\nDate: {inc['Date_Display']}"
            text_content += f"\nCost: ${inc['Cost']:,.2f}"
            text_content += f"\nChange: +${inc['Cost_Change']:,.2f} (+{inc['Cost_Change_Percent']:.1f}%)"
        
        if summary['biggest_decrease'] is not None:
            text_content += f"\n\nBIGGEST COST DECREASE\n{'-'*30}"
            dec = summary['biggest_decrease']
            text_content += f"\nDate: {dec['Date_Display']}"
            text_content += f"\nCost: ${dec['Cost']:,.2f}"
            text_content += f"\nChange: ${dec['Cost_Change']:,.2f} ({dec['Cost_Change_Percent']:.1f}%)"
        
        fig.text(0.02, 0.98, text_content, fontsize=6, fontfamily='monospace',
                verticalalignment='top', transform=fig.transFigure)
    
    def _create_spikes_text_page(self, fig):
        """Create cost spikes analysis text page (same format as TXT export)"""
        fig.clear()
        
        text_content = f"""COST SPIKES DETECTED
{'-'*40}"""
        
        if self.spikes.empty:
            text_content += "\n\nNo significant cost spikes detected with current thresholds."
        else:
            # Use same format as TXT export
            text_content += f"\n{'Date':<12} {'Cost ($)':<12} {'Change ($)':<12} {'Change (%)':<12} {'Type':<15} {'Top Service':<25}"
            text_content += f"\n{'-'*90}"
            
            for _, spike in self.spikes.iterrows():
                top_service = spike['Top_Service'][:23] if len(spike['Top_Service']) > 23 else spike['Top_Service']
                text_content += f"\n{spike['Date_Display']:<12} ${spike['Cost']:<11,.0f} ${spike['Cost_Change']:<11,.0f} {spike['Cost_Change_Percent']:>+7.1f}% {spike['Spike_Type']:<15} {top_service:<25}"
            
            # Add spike statistics (same as TXT export)
            increases = self.spikes[self.spikes['Cost_Change'] > 0]
            decreases = self.spikes[self.spikes['Cost_Change'] < 0]
            
            text_content += f"\n\nSPIKE STATISTICS\n{'-'*20}"
            text_content += f"\nTotal Spikes: {len(self.spikes)}"
            text_content += f"\nCost Increases: {len(increases)}"
            text_content += f"\nCost Decreases: {len(decreases)}"
            
            if not increases.empty:
                avg_increase = increases['Cost_Change'].mean()
                max_increase = increases['Cost_Change'].max()
                text_content += f"\nAverage Increase: ${avg_increase:,.2f}"
                text_content += f"\nLargest Increase: ${max_increase:,.2f}"
            
            if not decreases.empty:
                avg_decrease = decreases['Cost_Change'].mean()
                max_decrease = decreases['Cost_Change'].min()
                text_content += f"\nAverage Decrease: ${avg_decrease:,.2f}"
                text_content += f"\nLargest Decrease: ${max_decrease:,.2f}"
        
        fig.text(0.02, 0.98, text_content, fontsize=6, fontfamily='monospace',
                verticalalignment='top', transform=fig.transFigure)

def create_cli_parser():
    """Create and configure the CLI argument parser"""
    parser = argparse.ArgumentParser(
        prog='azure-cost-analyzer',
        description='🔍 Azure Cost Analysis CLI - Comprehensive cost analysis and reporting tool',
        epilog='''
Examples:
  %(prog)s data.csv                                    # Quick analysis with Excel + PDF
  %(prog)s data.csv --format txt                       # Text-only output
  %(prog)s data.csv --format all                       # Generate all formats
  %(prog)s data.csv --spike-threshold 50               # Custom spike detection
  %(prog)s data.csv --output-dir ./reports             # Custom output directory
  %(prog)s data.csv --quiet                            # Minimal output
  %(prog)s --version                                   # Show version
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Positional arguments
    parser.add_argument('csv_file', 
                       help='Path to Azure usage CSV file')
    
    # Output format options
    format_group = parser.add_argument_group('📊 Output Format Options')
    format_group.add_argument('--format', '-f',
                             choices=['excel', 'pdf', 'txt', 'both', 'all'], 
                             default='both',
                             help='Output format (default: both)')
    
    # File naming options
    files_group = parser.add_argument_group('📁 File Options')
    files_group.add_argument('--output-dir', '-o',
                            help='Output directory for generated files (default: current directory)')
    files_group.add_argument('--excel-output',
                            default='azure_cost_analysis.xlsx',
                            help='Excel output filename (default: azure_cost_analysis.xlsx)')
    files_group.add_argument('--pdf-output',
                            default='azure_cost_analysis.pdf',
                            help='PDF output filename (default: azure_cost_analysis.pdf)')
    files_group.add_argument('--txt-output',
                            default='azure_cost_analysis.txt',
                            help='TXT output filename (default: azure_cost_analysis.txt)')
    
    # Analysis options
    analysis_group = parser.add_argument_group('🔍 Analysis Options')
    analysis_group.add_argument('--spike-threshold', '-s',
                               type=float, default=30.0,
                               help='Spike detection threshold percentage (default: 30.0)')
    analysis_group.add_argument('--min-spike-amount', '-m',
                               type=float, default=100.0,
                               help='Minimum spike amount in dollars (default: 100.0)')
    
    # Display options
    display_group = parser.add_argument_group('🎨 Display Options')
    display_group.add_argument('--quiet', '-q',
                              action='store_true',
                              help='Minimal output (suppress detailed analysis)')
    display_group.add_argument('--no-summary',
                              action='store_true',
                              help='Skip printing analysis summary to console')
    display_group.add_argument('--version', '-v',
                              action='version',
                              version='Azure Cost Analyzer v2.0.0')
    
    return parser

def validate_arguments(args):
    """Validate command line arguments"""
    import os
    
    # Check if CSV file exists
    if not os.path.exists(args.csv_file):
        raise FileNotFoundError(f"CSV file '{args.csv_file}' not found")
    
    # Create output directory if specified
    if args.output_dir:
        os.makedirs(args.output_dir, exist_ok=True)
        # Update file paths to include output directory
        args.excel_output = os.path.join(args.output_dir, args.excel_output)
        args.pdf_output = os.path.join(args.output_dir, args.pdf_output)
        args.txt_output = os.path.join(args.output_dir, args.txt_output)
    
    # Validate thresholds
    if args.spike_threshold <= 0:
        raise ValueError("Spike threshold must be positive")
    if args.min_spike_amount < 0:
        raise ValueError("Minimum spike amount cannot be negative")
    
    return args

def print_welcome_banner():
    """Print welcome banner"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                   🔍 AZURE COST ANALYZER                     ║
║              Comprehensive Cost Analysis & Reporting         ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def print_completion_summary(args, analyzer):
    """Print completion summary with file information"""
    import os
    
    print(f"\n{'='*60}")
    print("🎉 ANALYSIS COMPLETED SUCCESSFULLY!")
    print(f"{'='*60}")
    
    # Show analysis stats
    summary = analyzer.get_summary_statistics()
    print(f"📊 Analyzed: {summary['total_cost']:,.2f} USD over {summary['total_days']} days")
    print(f"🚨 Detected: {summary['spikes_count']} cost spikes")
    print(f"🏢 Subscriptions: {summary['unique_subscriptions']}")
    print(f"🔧 Services: {summary['unique_services']}")
    
    print(f"\n📁 Generated Files:")
    
    if args.format in ['excel', 'both', 'all']:
        size = os.path.getsize(args.excel_output) / 1024
        print(f"  📊 Excel: {args.excel_output} ({size:.1f} KB)")
    
    if args.format in ['pdf', 'both', 'all']:
        size = os.path.getsize(args.pdf_output) / 1024
        print(f"  📄 PDF:   {args.pdf_output} ({size:.1f} KB)")
    
    if args.format in ['txt', 'all']:
        size = os.path.getsize(args.txt_output) / 1024
        print(f"  📄 TXT:   {args.txt_output} ({size:.1f} KB)")
    
    print(f"\n💡 Tip: Use --help to see all available options")

def main():
    """Main CLI function"""
    try:
        # Parse arguments
        parser = create_cli_parser()
        args = parser.parse_args()
        
        # Validate arguments
        args = validate_arguments(args)
        
        # Print banner unless quiet mode
        if not args.quiet:
            print_welcome_banner()
        
        # Initialize analyzer
        if not args.quiet:
            print("🚀 Initializing Azure Cost Analyzer...")
        
        analyzer = AzureCostAnalyzer(args.csv_file)
        
        # Load and analyze data
        if not args.quiet:
            print("📊 Loading and analyzing data...")
        
        analyzer.load_data()
        analyzer.analyze_daily_costs()
        analyzer.analyze_subscription_costs()
        analyzer.analyze_service_costs_by_date_ranges()
        analyzer.identify_cost_spikes(args.spike_threshold, args.min_spike_amount)
        
        # Print analysis summary unless suppressed
        if not args.no_summary and not args.quiet:
            analyzer.print_analysis_summary()
        elif not args.quiet:
            # Print minimal summary
            summary = analyzer.get_summary_statistics()
            print(f"\n📈 Quick Summary: ${summary['total_cost']:,.2f} total cost, {summary['spikes_count']} spikes detected")
        
        # Generate reports
        if not args.quiet:
            print(f"\n📝 Generating reports...")
        
        if args.format in ['excel', 'both', 'all']:
            if not args.quiet:
                print("  📊 Creating Excel report...")
            analyzer.export_to_excel(args.excel_output)
        
        if args.format in ['pdf', 'both', 'all']:
            if not args.quiet:
                print("  📄 Creating PDF report...")
            analyzer.create_pdf_report(args.pdf_output)
        
        if args.format in ['txt', 'all']:
            if not args.quiet:
                print("  📄 Creating TXT report...")
            analyzer.export_to_txt(args.txt_output)
        
        # Print completion summary
        if not args.quiet:
            print_completion_summary(args, analyzer)
        else:
            # Minimal completion message
            print("✅ Analysis completed")
        
    except KeyboardInterrupt:
        print(f"\n❌ Analysis interrupted by user")
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"❌ File Error: {e}")
        sys.exit(1)
    except ValueError as e:
        print(f"❌ Invalid Input: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected Error: {str(e)}")
        if not args.quiet if 'args' in locals() else True:
            import traceback
            print("\n🔍 Detailed Error Information:")
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
