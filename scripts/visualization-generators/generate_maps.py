#!/usr/bin/env python3
"""
Script to generate map visualizations
Part of the streaming visualization project
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import warnings
warnings.filterwarnings('ignore')

def generate_maps():
    """
    Generates spatial map visualizations
    """
    print("GENERATING MAP VISUALIZATIONS")
    print("=" * 50)
    
    # Path configuration
    data_dir = Path("../../visualizations/spatial")
    output_dir = Path("../../visualizations/spatial/choropleth-maps")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        # Load clean data
        print("Loading clean geographic data...")
        country_data_path = data_dir / "country_data_clean.csv"
        region_data_path = data_dir / "region_data_clean.csv"
        
        if not country_data_path.exists() or not region_data_path.exists():
            print("ERROR: Geographic data not found. Run clean_geographic_data.py first")
            return False
        
        df_country = pd.read_csv(country_data_path)
        df_region = pd.read_csv(region_data_path)
        
        print(f"OK: Country data loaded: {len(df_country)} records")
        print(f"OK: Region data loaded: {len(df_region)} records")
        
        # 1. Interest map by country
        print("Generating interest map by country...")
        
        fig_country = px.choropleth(
            df_country,
            locations="country_code",
            color="interest_mean",
            hover_name="name",
            hover_data=["region", "content_category", "interest_max", "volatility_7d_mean"],
            title="Average Interest by Country",
            color_continuous_scale="Blues",
            projection="equirectangular"
        )
        
        fig_country.update_layout(
            height=600,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        country_map_path = output_dir / "interest_by_country.html"
        fig_country.write_html(str(country_map_path))
        print(f"OK: Country map saved: {country_map_path}")
        
        # 2. Volatility map by country
        print("Generating volatility map by country...")
        
        fig_volatility = px.choropleth(
            df_country,
            locations="country_code",
            color="volatility_7d_mean",
            hover_name="name",
            hover_data=["region", "content_category", "interest_mean", "interest_max"],
            title="Average Volatility by Country",
            color_continuous_scale="Reds",
            projection="equirectangular"
        )
        
        fig_volatility.update_layout(
            height=600,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        volatility_map_path = output_dir / "volatility_by_country.html"
        fig_volatility.write_html(str(volatility_map_path))
        print(f"OK: Volatility map saved: {volatility_map_path}")
        
        # 3. Point map by country
        print("Generating point map by country...")
        
        # Approximate coordinates for countries
        country_coords = {
            'US': {'lat': 39.8283, 'lon': -98.5795},
            'CN': {'lat': 35.8617, 'lon': 104.1954},
            'JP': {'lat': 36.2048, 'lon': 138.2529},
            'DE': {'lat': 51.1657, 'lon': 10.4515},
            'GB': {'lat': 55.3781, 'lon': -3.4360},
            'IN': {'lat': 20.5937, 'lon': 78.9629},
            'BR': {'lat': -14.2350, 'lon': -51.9253},
            'CA': {'lat': 56.1304, 'lon': -106.3468},
            'AU': {'lat': -25.2744, 'lon': 133.7751},
            'KR': {'lat': 35.9078, 'lon': 127.7669}
        }
        
        # Add coordinates
        df_country['lat'] = df_country['country_code'].map(lambda x: country_coords.get(x, {}).get('lat', 0))
        df_country['lon'] = df_country['country_code'].map(lambda x: country_coords.get(x, {}).get('lon', 0))
        df_country_coords = df_country[df_country['lat'] != 0]
        
        fig_scatter = px.scatter_geo(
            df_country_coords,
            lat='lat',
            lon='lon',
            size='interest_mean',
            color='interest_mean',
            hover_name='name',
            hover_data=["region", "content_category", "interest_max", "volatility_7d_mean"],
            title="Interest by Country (Size = Interest)",
            color_continuous_scale="Blues",
            size_max=50
        )
        
        fig_scatter.update_layout(
            height=600,
            geo=dict(
                showframe=False,
                showcoastlines=True,
                projection_type='equirectangular'
            ),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        scatter_map_path = output_dir / "interest_scatter_map.html"
        fig_scatter.write_html(str(scatter_map_path))
        print(f"OK: Point map saved: {scatter_map_path}")
        
        # 4. Create maps index
        print("Creating maps index...")
        
        maps_index = {
            "generated_maps": [
                {
                    "name": "Interest by Country",
                    "file": "interest_by_country.html",
                    "description": "Choropleth map showing average interest by country",
                    "type": "choropleth"
                },
                {
                    "name": "Volatility by Country",
                    "file": "volatility_by_country.html",
                    "description": "Choropleth map showing average volatility by country",
                    "type": "choropleth"
                },
                {
                    "name": "Interest by Country (Points)",
                    "file": "interest_scatter_map.html",
                    "description": "Point map where size represents interest level",
                    "type": "scatter"
                }
            ],
            "generation_date": str(pd.Timestamp.now()),
            "total_countries": len(df_country),
            "total_regions": len(df_region)
        }
        
        index_path = output_dir / "maps_index.json"
        with open(index_path, 'w') as f:
            json.dump(maps_index, f, indent=2)
        print(f"OK: Maps index saved: {index_path}")
        
        print("\nMAP GENERATION SUMMARY:")
        print(f"  - Generated maps: {len(maps_index['generated_maps'])}")
        print(f"  - Included countries: {maps_index['total_countries']}")
        print(f"  - Included regions: {maps_index['total_regions']}")
        print(f"  - Output directory: {output_dir}")
        
        return True
        
    except Exception as e:
        print(f"ERROR during map generation: {e}")
        return False

if __name__ == "__main__":
    success = generate_maps()
    if success:
        print("\nOK: MAP GENERATION COMPLETED")
    else:
        print("\nERROR: MAP GENERATION FAILED")