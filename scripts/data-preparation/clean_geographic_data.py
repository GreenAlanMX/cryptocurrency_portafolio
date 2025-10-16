#!/usr/bin/env python3
"""
Script to clean and prepare geographic data
Part of the streaming visualization project
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

def clean_geographic_data():
    """
    Cleans and prepares geographic data for visualizations
    """
    print("CLEANING GEOGRAPHIC DATA")
    print("=" * 50)
    
    # Configuration paths
    data_dir = Path("../../analyst")
    output_dir = Path("../../visualizations/spatial")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Country to region mapping
    country_to_region = {
        'US': 'North America',
        'CN': 'Asia',
        'JP': 'Asia',
        'DE': 'Europe',
        'GB': 'Europe',
        'IN': 'Asia',
        'BR': 'South America',
        'CA': 'North America',
        'AU': 'Oceania',
        'KR': 'Asia'
    }
    
    # Crypto to content mapping
    crypto_to_content = {
        'Bitcoin': 'Drama',
        'Ethereum': 'Comedy', 
        'BNB': 'Action',
        'Solana': 'Documentary',
        'Tether': 'Romance'
    }
    
    try:
        # Load integrated data
        print("Loading integrated data...")
        integrated_path = data_dir / "integrated_data.csv"
        if not integrated_path.exists():
            print(f"ERROR: Not found {integrated_path}")
            return False
            
        df_integrated = pd.read_csv(integrated_path)
        print(f"OK: Integrated data loaded: {len(df_integrated)} records")
        
        # Apply mappings
        df_integrated['content_category'] = df_integrated['crypto'].map(crypto_to_content)
        df_integrated['region'] = df_integrated['country_code'].map(country_to_region)
        
        # Clean data
        df_integrated = df_integrated.dropna(subset=['content_category', 'region'])
        
        # Load country aggregated data
        print("Loading country aggregated data...")
        country_path = data_dir / "country_aggregated.csv"
        if not country_path.exists():
            print(f"ERROR: Not found {country_path}")
            return False
            
        df_country = pd.read_csv(country_path)
        print(f"OK: Country data loaded: {len(df_country)} records")
        
        # Apply mappings
        df_country['content_category'] = df_country['crypto'].map(crypto_to_content)
        df_country['region'] = df_country['country_code'].map(country_to_region)
        
        # Clean data
        df_country = df_country.dropna(subset=['content_category', 'region'])
        
        # Create clean geographic data
        print("Creating clean geographic data...")
        
        # Data by region
        region_data = df_country.groupby('region').agg({
            'interest_mean': ['mean', 'sum', 'count'],
            'interest_max': 'max',
            'volatility_7d_mean': 'mean'
        }).round(3)
        
        region_data.columns = ['avg_interest', 'total_interest', 'country_count', 'max_interest', 'avg_volatility']
        region_data = region_data.reset_index()
        
        # Data by country
        country_data = df_country[['name', 'country_code', 'region', 'content_category', 
                                 'interest_mean', 'interest_max', 'volatility_7d_mean']].copy()
        
        # Save clean data
        print("Saving clean data...")
        
        # Save region data
        region_output = output_dir / "region_data_clean.csv"
        region_data.to_csv(region_output, index=False)
        print(f"OK: Region data saved: {region_output}")
        
        # Save country data
        country_output = output_dir / "country_data_clean.csv"
        country_data.to_csv(country_output, index=False)
        print(f"OK: Country data saved: {country_output}")
        
        # Create summary
        summary = {
            "total_countries": len(country_data['country_code'].unique()),
            "total_regions": len(region_data['region'].unique()),
            "total_categories": len(country_data['content_category'].unique()),
            "avg_interest_global": float(country_data['interest_mean'].mean()),
            "max_interest_global": float(country_data['interest_max'].max()),
            "min_interest_global": float(country_data['interest_mean'].min())
        }
        
        summary_output = output_dir / "geographic_summary.json"
        with open(summary_output, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"OK: Geographic summary saved: {summary_output}")
        
        print("\nCLEANING SUMMARY:")
        print(f"  - Unique countries: {summary['total_countries']}")
        print(f"  - Unique regions: {summary['total_regions']}")
        print(f"  - Unique categories: {summary['total_categories']}")
        print(f"  - Global average interest: {summary['avg_interest_global']:.2f}")
        print(f"  - Global max interest: {summary['max_interest_global']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"ERROR during cleaning: {e}")
        return False

if __name__ == "__main__":
    success = clean_geographic_data()
    if success:
        print("\nOK: GEOGRAPHIC DATA CLEANING COMPLETED")
    else:
        print("\nERROR: GEOGRAPHIC DATA CLEANING FAILED")
