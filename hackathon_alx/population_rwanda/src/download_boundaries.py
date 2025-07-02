import requests
from pathlib import Path
import geopandas as gpd

def download_and_process_boundaries():
    """Download and process Rwanda boundary files from GADM"""
    # Create data directory if it doesn't exist
    data_dir = Path(__file__).parent.parent / 'data'
    data_dir.mkdir(exist_ok=True)
    
    # GADM URLs for different administrative levels
    urls = {
        'province': "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_RWA_1.json",
        'district': "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_RWA_2.json",
        'sector': "https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_RWA_3.json"
    }
    
    try:
        for level, url in urls.items():
            print(f"Downloading {level} boundary data...")
            response = requests.get(url)
            
            if response.status_code == 200:
                # Save the JSON file temporarily
                json_path = data_dir / f"rwanda_{level}_temp.json"
                with open(json_path, 'wb') as f:
                    f.write(response.content)
                
                # Read with GeoPandas
                gdf = gpd.read_file(json_path)
                
                # Rename columns appropriately
                if level == 'province':
                    gdf = gdf.rename(columns={
                        'NAME_1': 'province_name',
                        'VARNAME_1': 'province_alt_name'
                    })
                elif level == 'district':
                    gdf = gdf.rename(columns={
                        'NAME_2': 'district_name',
                        'NAME_1': 'province_name'
                    })
                elif level == 'sector':
                    gdf = gdf.rename(columns={
                        'NAME_3': 'sector_name',
                        'NAME_2': 'district_name',
                        'NAME_1': 'province_name'
                    })
                
                # Save as GeoJSON
                output_path = data_dir / f'rwanda_{level}.geojson'
                gdf.to_file(output_path, driver='GeoJSON')
                print(f"Saved {level} boundaries")
                
                # Clean up temporary file
                json_path.unlink()
            else:
                print(f"Failed to download {level} data: HTTP {response.status_code}")
        
        print("\nBoundary files have been processed and saved in GeoJSON format")
            
    except Exception as e:
        print(f"Error downloading or processing boundary data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    download_and_process_boundaries() 