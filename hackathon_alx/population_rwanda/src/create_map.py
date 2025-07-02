import geopandas as gpd
import folium
import pandas as pd
import os
from pathlib import Path
import branca.colormap as cm
import numpy as np

def create_base_map():
    """Create a base map centered on Rwanda"""
    rwanda_center = [-1.9403, 29.8739]
    return folium.Map(location=rwanda_center, 
                     zoom_start=8,
                     tiles='cartodbpositron',
                     prefer_canvas=True)

def calculate_statistics(data):
    """Calculate additional statistics from population data"""
    data['Gender Ratio'] = (data['Male'] / data['Female'] * 100).round(2)
    if 'Area_km2' in data.columns:
        data['Population Density'] = (data['Total Population'] / data['Area_km2']).round(2)
    return data

def format_number(num):
    """Format large numbers with commas"""
    return "{:,}".format(int(num))

def create_choropleth_map(gdf, population_data, level, output_dir):
    """Create an enhanced choropleth map for the specified administrative level"""
    m = create_base_map()
    
    # Merge GeoJSON with population data
    id_field = f'{level}_name'
    if level == 'province':
        population_data = population_data.rename(columns={'Province': id_field})
    elif level == 'district':
        population_data = population_data.rename(columns={'District': id_field})
    elif level == 'sector':
        population_data = population_data.rename(columns={'Sector': id_field})
    
    merged_data = gdf.merge(population_data, on=id_field, how='left')
    merged_data = calculate_statistics(merged_data)
    
    # Calculate area if geometry is available
    if 'geometry' in merged_data.columns:
        merged_data['Area_km2'] = merged_data.geometry.area / 1e6
        merged_data['Population Density'] = (merged_data['Total Population'] / merged_data['Area_km2']).round(2)
    
    # Create custom colormaps with vibrant colors
    population_colormap = cm.LinearColormap(
        colors=['#c6dbef', '#9ecae1', '#6baed6', '#3182bd', '#08519c'],
        vmin=merged_data['Total Population'].min(),
        vmax=merged_data['Total Population'].max(),
        caption='Total Population'
    )
    
    # Add the main choropleth layer with population data
    folium.Choropleth(
        geo_data=merged_data.__geo_interface__,
        name='Population',
        data=merged_data,
        columns=[id_field, 'Total Population'],
        key_on=f'feature.properties.{id_field}',
        fill_color='YlOrRd',  # Changed to Yellow-Orange-Red for better visibility
        fill_opacity=0.8,
        line_opacity=0.5,
        line_color='white',
        line_weight=2,
        highlight=True,
        smooth_factor=2
    ).add_to(m)

    # Add a separate GeoJson layer for boundaries
    folium.GeoJson(
        merged_data,
        style_function=lambda x: {
            'fillColor': 'transparent',
            'color': 'white',
            'weight': 2,
            'fillOpacity': 0,
            'opacity': 0.8
        },
        highlight_function=lambda x: {
            'color': '#fff',
            'weight': 3,
            'opacity': 1
        }
    ).add_to(m)

    # Create labels and popups
    for idx, row in merged_data.iterrows():
        # Calculate centroid for label placement
        centroid = row.geometry.centroid
        
        # Create popup content
        popup_content = f"""
        <div style="font-family: Arial; min-width: 200px; padding: 10px;">
            <h4 style="margin-bottom: 10px; color: #2c3e50;">{row[id_field]}</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px;">Total Population:</td>
                    <td style="padding: 8px; text-align: right;"><b>{format_number(row['Total Population'])}</b></td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Male:</td>
                    <td style="padding: 8px; text-align: right;">{format_number(row['Male'])}</td>
                </tr>
                <tr style="background-color: #f8f9fa;">
                    <td style="padding: 8px;">Female:</td>
                    <td style="padding: 8px; text-align: right;">{format_number(row['Female'])}</td>
                </tr>
                <tr>
                    <td style="padding: 8px;">Gender Ratio:</td>
                    <td style="padding: 8px; text-align: right;">{row['Gender Ratio']}%</td>
                </tr>
            </table>
        </div>
        """
        
        # Add a circle marker at the centroid with the total population
        folium.CircleMarker(
            location=[centroid.y, centroid.x],
            radius=12,  # Increased radius
            color='white',
            fill=True,
            fillColor='#2c3e50',  # Darker blue for better contrast
            fillOpacity=1.0,  # Full opacity
            weight=2,
            popup=folium.Popup(popup_content, max_width=300),
            tooltip=f"{row[id_field]}: {format_number(row['Total Population'])} people"
        ).add_to(m)

        # Add the region name as a permanent label
        folium.map.Marker(
            [centroid.y, centroid.x],
            icon=folium.DivIcon(
                html=f'''
                <div style="
                    font-size: 12pt; 
                    color: white; 
                    text-shadow: 2px 2px 2px rgba(0,0,0,0.8);
                    background-color: rgba(44, 62, 80, 0.7);
                    padding: 5px 8px;
                    border-radius: 4px;
                    text-align: center;
                    width: auto;
                    white-space: nowrap;
                ">
                    <strong>{row[id_field]}</strong><br>
                    <span style="font-size: 11pt;">{format_number(row["Total Population"])}</span>
                </div>
                ''',
                class_name='transparent_label'
            )
        ).add_to(m)

    # Add the colormap to the map
    population_colormap.add_to(m)
    
    # Add info box
    info_html = f"""
    <div style="position: fixed; 
                bottom: 50px; 
                right: 50px; 
                width: 250px;
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                z-index: 1000;
                box-shadow: 0 0 15px rgba(0,0,0,0.2);">
        <h4 style="margin-top: 0; color: #2c3e50;">Rwanda {level.title()} Population</h4>
        <p style="font-size: 14px; color: #34495e;">
            • Population numbers are shown directly on the map<br>
            • Click on regions or markers for detailed statistics<br>
            • Darker blue indicates higher population
        </p>
        <div style="font-size: 12px; color: #7f8c8d; margin-top: 10px;">
            Data source: PHC5-2022
        </div>
    </div>
    """
    m.get_root().html.add_child(folium.Element(info_html))
    
    # Add custom CSS for labels
    css = """
    <style>
        .transparent_label {
            background-color: transparent !important;
            border: none !important;
            box-shadow: none !important;
            text-align: center;
        }
    </style>
    """
    m.get_root().html.add_child(folium.Element(css))
    
    # Add Layer Control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add scale bar
    folium.plugins.MeasureControl(position='bottomleft').add_to(m)
    
    # Save the map
    output_path = output_dir / f'rwanda_population_{level}.html'
    m.save(str(output_path))
    print(f"Created enhanced {level} level map at {output_path}")
    
    return m

def main():
    try:
        # Set up directories
        data_dir = Path(__file__).parent.parent / 'data'
        output_dir = Path(__file__).parent.parent / 'output'
        output_dir.mkdir(exist_ok=True)
        
        # Load processed population data
        province_data = pd.read_csv(data_dir / 'processed_province_data.csv')
        district_data = pd.read_csv(data_dir / 'processed_district_data.csv')
        sector_data = pd.read_csv(data_dir / 'processed_sector_data.csv')
        
        # Create maps for each administrative level
        levels = ['province', 'district', 'sector']
        data_mapping = {
            'province': province_data,
            'district': district_data,
            'sector': sector_data
        }
        
        for level in levels:
            try:
                # Load GeoJSON data
                geojson_path = data_dir / f'rwanda_{level}.geojson'
                if not geojson_path.exists():
                    print(f"Warning: GeoJSON file for {level} not found at {geojson_path}")
                    continue
                    
                gdf = gpd.read_file(geojson_path)
                population_data = data_mapping[level]
                
                # Create and save the map
                create_choropleth_map(gdf, population_data, level, output_dir)
                print(f"Successfully created {level} level map")
                
            except Exception as e:
                print(f"Error creating {level} map: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print("\nAll enhanced maps have been created in the output directory")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()