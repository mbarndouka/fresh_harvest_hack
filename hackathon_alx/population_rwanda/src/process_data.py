import pandas as pd
import os
from pathlib import Path

def clean_sector_name(name):
    """Remove leading spaces and other artifacts from sector names"""
    return name.strip().replace('  ', '')

def load_provincial_data(file_patterns, data_dir=None):
    """
    Load and combine data from multiple provincial CSV files
    """
    if data_dir is None:
        # Use the main data directory instead of the one in population_rwanda
        data_dir = Path(__file__).parent.parent.parent / 'data'
    else:
        data_dir = Path(data_dir)
        
    all_data = []
    
    for pattern in file_patterns:
        file_path = data_dir / pattern.strip()
        if not file_path.exists():
            print(f"Warning: File not found: {file_path}")
            continue
            
        try:
            # Extract file number for province mapping
            file_num = int(pattern.split('Table ')[-1].split('.')[0])
            
            # Read the CSV file, skipping the first two rows (header)
            df = pd.read_csv(file_path, skiprows=2)
            
            # Clean up the data
            df.columns = ['Unnamed', 'Location', 'Total Population', 'Male', 'Female', 'Total Percentage', 'Male Percentage', 'Female Percentage']
            df = df.dropna(subset=['Location'])
            df['Location'] = df['Location'].apply(clean_sector_name)
            
            # Convert population columns to numeric, removing commas
            for col in ['Total Population', 'Male', 'Female']:
                df[col] = pd.to_numeric(df[col].astype(str).str.replace(',', ''), errors='coerce')
            
            # Extract district and sector information
            current_district = None
            rows = []
            
            for _, row in df.iterrows():
                location = row['Location']
                if pd.isna(location) or location == '':
                    continue
                    
                if not location.startswith('  '):  # This is a district
                    current_district = location
                    # Add district level data
                    rows.append({
                        'Province': province_mapping.get(file_num, "Unknown"),
                        'District': location,
                        'Sector': None,
                        'Total Population': row['Total Population'],
                        'Male': row['Male'],
                        'Female': row['Female']
                    })
                else:  # This is a sector
                    if current_district:  # Only add if we have a current district
                        rows.append({
                            'Province': province_mapping.get(file_num, "Unknown"),
                            'District': current_district,
                            'Sector': location.strip(),
                            'Total Population': row['Total Population'],
                            'Male': row['Male'],
                            'Female': row['Female']
                        })
            
            # Create a new dataframe with the processed data
            processed_df = pd.DataFrame(rows)
            all_data.append(processed_df)
            print(f"Successfully loaded data from {pattern}")
            
        except Exception as e:
            print(f"Error loading {pattern}: {e}")
            import traceback
            traceback.print_exc()
    
    if not all_data:
        raise ValueError("No data files were successfully loaded")
    
    # Combine all provincial data
    combined_data = pd.concat(all_data, ignore_index=True)
    return combined_data

def prepare_population_data(df, level='district'):
    """
    Prepare population data for mapping at the specified administrative level
    """
    if level.lower() == 'province':
        # Group by province if needed
        return df.groupby('Province').agg({
            'Total Population': 'sum',
            'Male': 'sum',
            'Female': 'sum'
        }).reset_index()
    elif level.lower() == 'district':
        # Return district level data
        return df.groupby(['District', 'Province']).agg({
            'Total Population': 'sum',
            'Male': 'sum',
            'Female': 'sum'
        }).reset_index()
    elif level.lower() == 'sector':
        # Return sector level data
        return df[df['Sector'].notna()][['Sector', 'District', 'Province', 'Total Population', 'Male', 'Female']]
    else:
        raise ValueError(f"Unsupported administrative level: {level}")

# Define the province mapping globally
province_mapping = {
    96: "City of Kigali",
    97: "Eastern Province",
    98: "Northern Province",
    99: "Southern Province",
    100: "Western Province"
}

def main():
    try:
        # Define the file patterns
        file_patterns = [
            "PHC5-2022_Main_Indicators.xlsx - Table 96.csv",  # City of Kigali
            "PHC5-2022_Main_Indicators.xlsx - Table 97.csv",  # Eastern Province
            "PHC5-2022_Main_Indicators.xlsx - Table 98.csv",  # Northern Province
            "PHC5-2022_Main_Indicators.xlsx - Table 99.csv",  # Southern Province
            "PHC5-2022_Main_Indicators.xlsx - Table 100.csv"  # Western Province
        ]
        
        # Load and combine all provincial data
        combined_data = load_provincial_data(file_patterns)
        
        print("\nData loading summary:")
        print(f"Total number of records: {len(combined_data)}")
        print("\nColumns in the dataset:")
        print(combined_data.columns.tolist())
        
        print("\nSample of the data:")
        print(combined_data.head())
        
        # Show population by province
        province_data = prepare_population_data(combined_data, 'province')
        print("\nPopulation by Province:")
        print(province_data)
        
        # Show population by district
        district_data = prepare_population_data(combined_data, 'district')
        print("\nPopulation by District (first few rows):")
        print(district_data.head())
        
        # Save processed data
        output_dir = Path(__file__).parent.parent / 'data'
        output_dir.mkdir(exist_ok=True)
        
        province_data.to_csv(output_dir / 'processed_province_data.csv', index=False)
        district_data.to_csv(output_dir / 'processed_district_data.csv', index=False)
        
        sector_data = prepare_population_data(combined_data, 'sector')
        sector_data.to_csv(output_dir / 'processed_sector_data.csv', index=False)
        
        print("\nProcessed data has been saved to the data directory.")
        
    except Exception as e:
        print(f"Error processing data: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 