"""
Rwanda Map Module
Handles all geographic data loading and map visualization functionality
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import json
import os
from pathlib import Path

try:
    import geopandas as gpd
    GEOPANDAS_AVAILABLE = True
    print("✅ Geopandas successfully imported")
except ImportError as e:
    GEOPANDAS_AVAILABLE = False
    print(f"⚠️ Geopandas not available: {e}")
    print("📊 Will use fallback visualization mode")

class RwandaMapHandler:
    def __init__(self, data_dir="data"):
        """
        Initialize the Rwanda Map Handler
        
        Args:
            data_dir (str): Directory containing the geographic data files
        """
        self.data_dir = Path(data_dir)
        
        # Province-level data
        self.gdf = None
        self.geojson_data = None
        self.provinces = []
        
        # District-level data
        self.districts_gdf = None
        self.districts_geojson_data = None
        self.districts = []
        
        # Try to load the geographic data
        self.load_geographic_data()
    
    def load_geographic_data(self):
        """Load Rwanda geographic data from zip file or extracted files"""
        print(f"🔍 Looking for geographic data in: {self.data_dir}")
        print(f"📁 Data directory exists: {self.data_dir.exists()}")
        
        # Load province data (ADM1)
        province_loaded = self._load_province_data()
        
        # Load district data (ADM2)
        district_loaded = self._load_district_data()
        
        return province_loaded or district_loaded
    
    def _load_province_data(self):
        """Load province-level geographic data (ADM1)"""
        try:
            if GEOPANDAS_AVAILABLE:
                # Try to read directly from zip file
                zip_path = self.data_dir / "geoBoundaries-RWA-ADM1-all.zip"
                print(f"🔍 Checking province zip file: {zip_path}")
                print(f"📁 Zip file exists: {zip_path.exists()}")
                
                if zip_path.exists():
                    print(f"📂 Loading province data from {zip_path}")
                    try:
                        # Geopandas can read directly from zip files
                        self.gdf = gpd.read_file(f"zip://{zip_path}")
                        print(f"✅ Successfully loaded {len(self.gdf)} provinces from zip file")
                        
                        # Convert to GeoJSON for Plotly
                        self.geojson_data = json.loads(self.gdf.to_json())
                        self.provinces = self.gdf['shapeName'].tolist()
                        print(f"🗺️ Provinces from zip: {', '.join(self.provinces[:3])}...")
                        return True
                        
                    except Exception as e:
                        print(f"❌ Failed to load from zip: {e}")
                        print("🔄 Trying extracted directory...")
                
                # Try to read from extracted directory
                adm1_dir = self.data_dir / "ADM1"
                geojson_path = adm1_dir / "geoBoundaries-RWA-ADM1.geojson"
                print(f"🔍 Checking extracted directory: {adm1_dir}")
                print(f"📁 ADM1 directory exists: {adm1_dir.exists()}")
                print(f"📄 GeoJSON file exists: {geojson_path.exists()}")
                
                if geojson_path.exists():
                    print(f"📂 Loading province data from {geojson_path}")
                    try:
                        self.gdf = gpd.read_file(geojson_path)
                        self.geojson_data = json.loads(self.gdf.to_json())
                        self.provinces = self.gdf['shapeName'].tolist()
                        print(f"✅ Successfully loaded {len(self.gdf)} provinces from GeoJSON")
                        print(f"🗺️ Provinces from GeoJSON: {', '.join(self.provinces[:3])}...")
                        return True
                    except Exception as e:
                        print(f"❌ Failed to load from GeoJSON with geopandas: {e}")
            
            # Fallback: try to read GeoJSON directly without geopandas
            adm1_dir = self.data_dir / "ADM1"
            geojson_path = adm1_dir / "geoBoundaries-RWA-ADM1.geojson"
            
            print(f"🔄 Attempting fallback: direct JSON loading from {geojson_path}")
            if geojson_path.exists():
                print(f"📂 Loading province data from {geojson_path} (without geopandas)")
                try:
                    with open(geojson_path, 'r', encoding='utf-8') as f:
                        self.geojson_data = json.load(f)
                    
                    # Extract province names
                    self.provinces = [
                        feature['properties']['shapeName'] 
                        for feature in self.geojson_data['features']
                    ]
                    print(f"✅ Successfully loaded {len(self.provinces)} provinces from GeoJSON")
                    print(f"🗺️ Provinces from JSON: {', '.join(self.provinces[:3])}...")
                    return True
                except Exception as e:
                    print(f"❌ Failed to load GeoJSON directly: {e}")
            
            print("❌ No province geographic data sources found")
            return False
                
        except Exception as e:
            print(f"❌ Unexpected error in _load_province_data: {str(e)}")
            import traceback
            print(f"� Full traceback: {traceback.format_exc()}")
            return False
    
    def _load_district_data(self):
        """Load district-level geographic data (ADM2)"""
        try:
            if GEOPANDAS_AVAILABLE:
                # Try to read districts from zip file (ADM2 level)
                zip_path = self.data_dir / "geoBoundaries-RWA-ADM2-all.zip"
                alt_zip_path = self.data_dir / "geoBoundaries-RWA-ADM2-all (1).zip"
                
                for zip_file in [zip_path, alt_zip_path]:
                    print(f"🔍 Checking district zip file: {zip_file}")
                    
                    if zip_file.exists():
                        print(f"📂 Loading district data from {zip_file}")
                        try:
                            self.districts_gdf = gpd.read_file(f"zip://{zip_file}")
                            print(f"✅ Successfully loaded {len(self.districts_gdf)} districts from zip file")
                            
                            # Convert to GeoJSON for Plotly
                            self.districts_geojson_data = json.loads(self.districts_gdf.to_json())
                            self.districts = self.districts_gdf['shapeName'].tolist()
                            print(f"🗺️ Districts loaded: {len(self.districts)} districts")
                            return True
                            
                        except Exception as e:
                            print(f"❌ Failed to load districts from {zip_file}: {e}")
                
                # Try to read from extracted directory (ADM2)
                adm2_dir = self.data_dir / "ADM2"
                districts_geojson_path = adm2_dir / "geoBoundaries-RWA-ADM2.geojson"
                
                print(f"🔍 Checking extracted district directory: {adm2_dir}")
                if districts_geojson_path.exists():
                    print(f"📂 Loading district data from {districts_geojson_path}")
                    try:
                        self.districts_gdf = gpd.read_file(districts_geojson_path)
                        self.districts_geojson_data = json.loads(self.districts_gdf.to_json())
                        self.districts = self.districts_gdf['shapeName'].tolist()
                        print(f"✅ Successfully loaded {len(self.districts)} districts from GeoJSON")
                        return True
                    except Exception as e:
                        print(f"❌ Failed to load districts from GeoJSON: {e}")
            
            # Fallback: try to read district GeoJSON directly
            adm2_dir = self.data_dir / "ADM2"
            districts_geojson_path = adm2_dir / "geoBoundaries-RWA-ADM2.geojson"
            
            if districts_geojson_path.exists():
                print(f"🔄 Loading district data directly from JSON: {districts_geojson_path}")
                try:
                    with open(districts_geojson_path, 'r', encoding='utf-8') as f:
                        self.districts_geojson_data = json.load(f)
                    
                    self.districts = [
                        feature['properties']['shapeName'] 
                        for feature in self.districts_geojson_data['features']
                    ]
                    print(f"✅ Successfully loaded {len(self.districts)} districts from JSON")
                    return True
                except Exception as e:
                    print(f"❌ Failed to load district JSON directly: {e}")
            
            print("❌ No district geographic data found")
            return False
                
        except Exception as e:
            print(f"❌ Error loading district data: {str(e)}")
            return False
    
    def get_sample_data(self):
        """
        Generate sample data that matches the loaded provinces
        
        Returns:
            pd.DataFrame: Sample data with matching province names
        """
        if self.provinces:
            # Use actual province names from the geographic data
            num_provinces = len(self.provinces)
            
            # Generate realistic sample data
            import random
            random.seed(42)  # For reproducible results
            
            data = {
                'Region': self.provinces,
                'Vitamin_A': [random.randint(30, 70) for _ in range(num_provinces)],
                'Iron': [random.randint(35, 75) for _ in range(num_provinces)],
                'Zinc': [random.randint(25, 65) for _ in range(num_provinces)],
                'Population': [random.randint(200000, 1500000) for _ in range(num_provinces)]
            }
        else:
            # Fallback data if no geographic data is available
            data = {
                'Region': ['Kigali', 'Northern', 'Southern', 'Eastern', 'Western'],
                'Vitamin_A': [65, 45, 55, 40, 50],
                'Iron': [70, 50, 60, 45, 55],
                'Zinc': [60, 40, 50, 35, 45],
                'Population': [1200000, 800000, 950000, 750000, 900000]
            }
        
        return pd.DataFrame(data)
    
    def get_sample_district_data(self):
        """
        Generate sample data for districts
        
        Returns:
            pd.DataFrame: Sample data with district names
        """
        if self.districts:
            # Use actual district names from the geographic data
            num_districts = len(self.districts)
            
            import random
            random.seed(42)  # For reproducible results
            
            data = {
                'District': self.districts,
                'Vitamin_A': [random.randint(25, 75) for _ in range(num_districts)],
                'Iron': [random.randint(30, 80) for _ in range(num_districts)],
                'Zinc': [random.randint(20, 70) for _ in range(num_districts)],
                'Population': [random.randint(50000, 400000) for _ in range(num_districts)]
            }
        else:
            # Fallback with some known Rwanda districts
            districts = [
                'Nyarugenge', 'Gasabo', 'Kicukiro', 'Nyanza', 'Gisagara', 
                'Nyamagabe', 'Ruhango', 'Muhanga', 'Kamonyi', 'Musanze',
                'Burera', 'Gicumbi', 'Rulindo', 'Nyabihu', 'Ngororero'
            ]
            data = {
                'District': districts,
                'Vitamin_A': [45, 38, 52, 41, 47, 39, 44, 36, 49, 42, 40, 46, 43, 37, 48],
                'Iron': [50, 43, 57, 46, 52, 44, 49, 41, 54, 47, 45, 51, 48, 42, 53],
                'Zinc': [40, 33, 47, 36, 42, 34, 39, 31, 44, 37, 35, 41, 38, 32, 43],
                'Population': [284551, 530515, 319145, 162509, 142332, 181598, 
                              161368, 290969, 87211, 368267, 298484, 485883, 
                              287681, 309668, 415906]
            }
        
        return pd.DataFrame(data)
    
    def create_choropleth_map(self, df, nutrient_column, title):
        """
        Create a choropleth map of Rwanda showing nutrient deficiency levels
        
        Args:
            df (pd.DataFrame): Data with Region and nutrient columns
            nutrient_column (str): Name of the nutrient column to visualize
            title (str): Title for the map
            
        Returns:
            plotly.graph_objects.Figure: Choropleth map figure
        """
        if self.geojson_data is None:
            return self.create_fallback_visualization(df, nutrient_column, title)
        
        try:
            # Create the choropleth map
            fig = px.choropleth(
                df,
                geojson=self.geojson_data,
                locations='Region',
                color=nutrient_column,
                featureidkey="properties.shapeName",
                projection="mercator",
                title=title,
                color_continuous_scale="RdYlBu_r",
                range_color=[df[nutrient_column].min(), df[nutrient_column].max()],
                labels={nutrient_column: f"{nutrient_column.replace('_', ' ')} Deficiency (%)"}
            )
            
            # Update layout for better appearance
            fig.update_geos(
                fitbounds="locations",
                visible=False
            )
            
            fig.update_layout(
                title_x=0.5,
                title_font_size=16,
                height=500,
                margin=dict(t=60, b=20, l=20, r=20)
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>" +
                            f"{nutrient_column.replace('_', ' ')} Deficiency: %{{z:.1f}}%<br>" +
                            "Population: %{customdata[1]:,.0f}<extra></extra>",
                customdata=df[['Region', 'Population']].values
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating choropleth map: {str(e)}")
            return self.create_fallback_visualization(df, nutrient_column, title)
    
    def create_fallback_visualization(self, df, nutrient_column, title, location_col='Region'):
        """
        Create a fallback visualization when geographic data is not available
        
        Args:
            df (pd.DataFrame): Data with Region/District and nutrient columns
            nutrient_column (str): Name of the nutrient column to visualize
            title (str): Title for the visualization
            location_col (str): Name of the location column ('Region' or 'District')
            
        Returns:
            plotly.graph_objects.Figure: Scatter plot figure
        """
        fig = px.scatter(
            df,
            x='Population',
            y=nutrient_column,
            size='Population',
            color=nutrient_column,
            hover_name=location_col,
            title=f"{title} (Geographic data not available)",
            color_continuous_scale='RdYlBu_r',
            labels={
                'Population': 'Population',
                nutrient_column: f"{nutrient_column.replace('_', ' ')} Deficiency (%)"
            }
        )
        
        fig.update_layout(
            title_x=0.5,
            title_font_size=16,
            height=500,
            margin=dict(t=60, b=20, l=20, r=20)
        )
        
        return fig
    
    def create_district_choropleth_map(self, df, nutrient_column, title):
        """
        Create a choropleth map showing district-level data
        
        Args:
            df (pd.DataFrame): Data with District and nutrient columns
            nutrient_column (str): Name of the nutrient column to visualize
            title (str): Title for the map
            
        Returns:
            plotly.graph_objects.Figure: Choropleth map figure
        """
        if self.districts_geojson_data is None:
            return self.create_fallback_visualization(df, nutrient_column, title, location_col='District')
        
        try:
            # Create the district-level choropleth map
            fig = px.choropleth(
                df,
                geojson=self.districts_geojson_data,
                locations='District',
                color=nutrient_column,
                featureidkey="properties.shapeName",
                projection="mercator",
                title=f"{title} (District Level)",
                color_continuous_scale="RdYlBu_r",
                range_color=[df[nutrient_column].min(), df[nutrient_column].max()],
                labels={nutrient_column: f"{nutrient_column.replace('_', ' ')} Deficiency (%)"}
            )
            
            # Update layout for better appearance
            fig.update_geos(
                fitbounds="locations",
                visible=False
            )
            
            fig.update_layout(
                title_x=0.5,
                title_font_size=16,
                height=600,  # Slightly taller for district detail
                margin=dict(t=60, b=20, l=20, r=20)
            )
            
            # Add hover information
            fig.update_traces(
                hovertemplate="<b>%{customdata[0]}</b><br>" +
                            f"{nutrient_column.replace('_', ' ')} Deficiency: %{{z:.1f}}%<br>" +
                            "Population: %{customdata[1]:,.0f}<extra></extra>",
                customdata=df[['District', 'Population']].values
            )
            
            return fig
            
        except Exception as e:
            print(f"Error creating district choropleth map: {str(e)}")
            return self.create_fallback_visualization(df, nutrient_column, title, location_col='District')
    
    def create_layered_map(self, province_df, district_df, nutrient_column, title, level='district'):
        """
        Create a map with both province and district boundaries
        
        Args:
            province_df (pd.DataFrame): Province-level data
            district_df (pd.DataFrame): District-level data
            nutrient_column (str): Name of the nutrient column to visualize
            title (str): Title for the map
            level (str): Primary level to show data for ('district' or 'province')
            
        Returns:
            plotly.graph_objects.Figure: Layered map figure
        """
        if level == 'district' and self.districts_geojson_data is not None:
            # Start with district-level choropleth
            fig = self.create_district_choropleth_map(district_df, nutrient_column, title)
            
            # Add province boundaries as overlay
            if self.geojson_data is not None:
                self._add_province_boundaries_overlay(fig)
                
            fig.update_layout(title=f"{title} (Districts with Province Boundaries)")
            
        elif self.geojson_data is not None:
            # Fallback to province-level with district boundaries if available
            fig = self.create_choropleth_map(province_df, nutrient_column, title)
            
            if self.districts_geojson_data is not None:
                self._add_district_boundaries_overlay(fig)
                
            fig.update_layout(title=f"{title} (Provinces with District Boundaries)")
        else:
            # No geographic data available
            return self.create_fallback_visualization(
                district_df if level == 'district' else province_df, 
                nutrient_column, 
                title, 
                location_col='District' if level == 'district' else 'Region'
            )
        
        return fig
    
    def _add_province_boundaries_overlay(self, fig):
        """Add province boundaries as overlay lines to existing figure"""
        if self.geojson_data is None:
            return
        
        try:
            for feature in self.geojson_data['features']:
                coords = feature['geometry']['coordinates']
                
                # Handle different geometry types
                if feature['geometry']['type'] == 'Polygon':
                    coords = [coords]
                
                for polygon in coords:
                    if len(polygon) > 0:
                        lons = [coord[0] for coord in polygon[0]] + [polygon[0][0][0]]
                        lats = [coord[1] for coord in polygon[0]] + [polygon[0][0][1]]
                        
                        fig.add_trace(go.Scatter(
                            x=lons,
                            y=lats,
                            mode='lines',
                            line=dict(width=3, color='black'),
                            name='Province Boundaries',
                            showlegend=False,
                            hoverinfo='skip'
                        ))
        except Exception as e:
            print(f"Error adding province boundaries overlay: {e}")
    
    def _add_district_boundaries_overlay(self, fig):
        """Add district boundaries as overlay lines to existing figure"""
        if self.districts_geojson_data is None:
            return
        
        try:
            for feature in self.districts_geojson_data['features']:
                coords = feature['geometry']['coordinates']
                
                # Handle different geometry types
                if feature['geometry']['type'] == 'Polygon':
                    coords = [coords]
                
                for polygon in coords:
                    if len(polygon) > 0:
                        lons = [coord[0] for coord in polygon[0]] + [polygon[0][0][0]]
                        lats = [coord[1] for coord in polygon[0]] + [polygon[0][0][1]]
                        
                        fig.add_trace(go.Scatter(
                            x=lons,
                            y=lats,
                            mode='lines',
                            line=dict(width=1, color='gray'),
                            name='District Boundaries',
                            showlegend=False,
                            hoverinfo='skip'
                        ))
        except Exception as e:
            print(f"Error adding district boundaries overlay: {e}")
    
    def get_map_info(self):
        """
        Get information about the loaded map data
        
        Returns:
            dict: Information about the map data
        """
        return {
            'geopandas_available': GEOPANDAS_AVAILABLE,
            'geographic_data_loaded': self.geojson_data is not None,
            'district_data_loaded': self.districts_geojson_data is not None,
            'num_provinces': len(self.provinces) if self.provinces else 0,
            'num_districts': len(self.districts) if self.districts else 0,
            'provinces': self.provinces,
            'districts': self.districts[:10] if len(self.districts) > 10 else self.districts,  # Show first 10 districts
            'data_source': {
                'provinces': 'zip file' if self.gdf is not None else 'geojson file' if self.geojson_data else 'none',
                'districts': 'zip file' if self.districts_gdf is not None else 'geojson file' if self.districts_geojson_data else 'none'
            }
        }

# Create a global instance
rwanda_map = RwandaMapHandler()

def get_rwanda_data():
    """Convenience function to get Rwanda data"""
    return rwanda_map.get_sample_data()

def create_rwanda_map(df, nutrient_column, title):
    """Convenience function to create Rwanda map"""
    return rwanda_map.create_choropleth_map(df, nutrient_column, title)

# Add convenience functions for district-level functionality
def get_rwanda_district_data():
    """Convenience function to get Rwanda district data"""
    return rwanda_map.get_sample_district_data()

def create_rwanda_district_map(df, nutrient_column, title):
    """Convenience function to create Rwanda district map"""
    return rwanda_map.create_district_choropleth_map(df, nutrient_column, title)

def create_rwanda_layered_map(province_df, district_df, nutrient_column, title, level='district'):
    """Convenience function to create layered map with both levels"""
    return rwanda_map.create_layered_map(province_df, district_df, nutrient_column, title, level)

def get_rwanda_map_info():
    """Convenience function to get map information"""
    return rwanda_map.get_map_info()
