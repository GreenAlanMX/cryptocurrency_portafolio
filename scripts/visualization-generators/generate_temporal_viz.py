#!/usr/bin/env python3
"""
Script to generate temporal visualizations
Part of the streaming visualization project
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import numpy as np
import warnings
warnings.filterwarnings('ignore')

def generate_temporal_viz():
    """
    Generates temporal visualizations
    """
    print("GENERATING TEMPORAL VISUALIZATIONS")
    print("=" * 50)
    
    # Path configuration
    data_dir = Path("../../visualizations/temporal")
    output_dir = Path("../../visualizations/temporal/line-graphs")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load temporal data
        print("Loading temporal data...")
        
        daily_category_path = data_dir / "daily_category_data.csv"
        daily_region_path = data_dir / "daily_region_data.csv"
        weekly_path = data_dir / "weekly_data.csv"
        
        if not daily_category_path.exists():
            print("ERROR: Temporal data not found. Run prepare_temporal_data.py first")
            return False
        
        df_daily_category = pd.read_csv(daily_category_path)
        df_daily_region = pd.read_csv(daily_region_path) if daily_region_path.exists() else None
        df_weekly = pd.read_csv(weekly_path) if weekly_path.exists() else None
        
        # Convert dates
        df_daily_category['Date'] = pd.to_datetime(df_daily_category['Date'])
        if df_daily_region is not None:
            df_daily_region['Date'] = pd.to_datetime(df_daily_region['Date'])
        
        print(f"OK: Daily category data loaded: {len(df_daily_category)} records")
        if df_daily_region is not None:
            print(f"OK: Daily region data loaded: {len(df_daily_region)} records")
        
        # 1. Time series by category
        print("Generating time series by category...")
        
        fig_category = px.line(
            df_daily_category,
            x='Date',
            y='avg_interest',
            color='content_category',
            title="Interest Evolution by Content Category",
            markers=True
        )
        
        fig_category.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Average Interest",
            hovermode='x unified'
        )
        
        category_line_path = output_dir / "interest_by_category_timeline.html"
        fig_category.write_html(str(category_line_path))
        print(f"OK: Category time series saved: {category_line_path}")
        
        # 2. Time series by region (if exists)
        if df_daily_region is not None:
            print("Generating time series by region...")
            
            fig_region = px.line(
                df_daily_region,
                x='Date',
                y='avg_interest',
                color='region',
                title="Interest Evolution by Region",
                markers=True
            )
            
            fig_region.update_layout(
                height=500,
                xaxis_title="Date",
                yaxis_title="Average Interest",
                hovermode='x unified'
            )
            
            region_line_path = output_dir / "interest_by_region_timeline.html"
            fig_region.write_html(str(region_line_path))
            print(f"OK: Region time series saved: {region_line_path}")
        
        # 3. Volatility chart by category
        print("Generating volatility chart...")
        
        fig_volatility = px.line(
            df_daily_category,
            x='Date',
            y='avg_volatility',
            color='content_category',
            title="Volatility Evolution by Category",
            markers=True
        )
        
        fig_volatility.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Average Volatility",
            hovermode='x unified'
        )
        
        volatility_path = output_dir / "volatility_by_category_timeline.html"
        fig_volatility.write_html(str(volatility_path))
        print(f"OK: Volatility chart saved: {volatility_path}")
        
        # 4. Stacked area chart
        print("Generating stacked area chart...")
        
        fig_area = px.area(
            df_daily_category,
            x='Date',
            y='total_interest',
            color='content_category',
            title="Total Interest Distribution by Category",
            groupnorm='percent'
        )
        
        fig_area.update_layout(
            height=500,
            xaxis_title="Date",
            yaxis_title="Percentage of Total Interest",
            hovermode='x unified'
        )
        
        area_path = output_dir / "interest_distribution_area.html"
        fig_area.write_html(str(area_path))
        print(f"OK: Area chart saved: {area_path}")
        
        # 5. Bar chart by category (average)
        print("Generating bar chart by category...")
        
        category_avg = df_daily_category.groupby('content_category')['avg_interest'].mean().reset_index()
        category_avg = category_avg.sort_values('avg_interest', ascending=True)
        
        fig_bars = px.bar(
            category_avg,
            x='avg_interest',
            y='content_category',
            orientation='h',
            title="Average Interest by Category",
            color='avg_interest',
            color_continuous_scale="Blues",
            text='avg_interest'
        )
        
        fig_bars.update_traces(texttemplate='%{text:.1f}', textposition='outside')
        fig_bars.update_layout(
            height=400,
            xaxis_title="Average Interest",
            yaxis_title="Content Category",
            showlegend=False
        )
        
        bars_path = output_dir / "interest_by_category_bars.html"
        fig_bars.write_html(str(bars_path))
        print(f"OK: Bar chart saved: {bars_path}")
        
        # 6. Create temporal visualizations index
        print("Creating temporal visualizations index...")
        
        temporal_viz_index = {
            "generated_visualizations": [
                {
                    "name": "Time Series by Category",
                    "file": "interest_by_category_timeline.html",
                    "description": "Evolution of average interest by content category",
                    "type": "line"
                },
                {
                    "name": "Time Series by Region",
                    "file": "interest_by_region_timeline.html",
                    "description": "Evolution of average interest by region",
                    "type": "line"
                },
                {
                    "name": "Volatility by Category",
                    "file": "volatility_by_category_timeline.html",
                    "description": "Evolution of volatility by category",
                    "type": "line"
                },
                {
                    "name": "Interest Distribution",
                    "file": "interest_distribution_area.html",
                    "description": "Percentage distribution of total interest by category",
                    "type": "area"
                },
                {
                    "name": "Average Interest by Category",
                    "file": "interest_by_category_bars.html",
                    "description": "Comparison of average interest between categories",
                    "type": "bar"
                }
            ],
            "generation_date": str(pd.Timestamp.now()),
            "date_range": {
                "start": str(df_daily_category['Date'].min()),
                "end": str(df_daily_category['Date'].max())
            },
            "total_observations": len(df_daily_category)
        }
        
        index_path = output_dir / "temporal_viz_index.json"
        with open(index_path, 'w') as f:
            json.dump(temporal_viz_index, f, indent=2)
        print(f"OK: Temporal visualizations index saved: {index_path}")
        
        print("\nTEMPORAL GENERATION SUMMARY:")
        print(f"  - Generated visualizations: {len(temporal_viz_index['generated_visualizations'])}")
        print(f"  - Date range: {temporal_viz_index['date_range']['start']} to {temporal_viz_index['date_range']['end']}")
        print(f"  - Total observations: {temporal_viz_index['total_observations']}")
        print(f"  - Output directory: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"ERROR during temporal generation: {e}")
        return False

if __name__ == "__main__":
    success = generate_temporal_viz()
    if success:
        print("\nOK: TEMPORAL VISUALIZATIONS GENERATION COMPLETED")
    else:
        print("\nERROR: TEMPORAL VISUALIZATIONS GENERATION FAILED")
