# Import required libraries
import pandas as pd
import os
import re

# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024']  # Add or remove years as needed

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/02 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Herstellern und Handelsnamen (FZ 2)'
SHEET_NAME = 'FZ 2.4'

def get_file_path(year):
    """
    Generate the file path for a given year.
    
    Parameters:
    -----------
    year : str
        The year to process
        
    Returns:
    --------
    str
        The complete file path
    """
    return os.path.join(BASE_PATH, f'fz2_{year}.xlsx')

def clean_header(df):
    """
    Clean and format the dataframe headers.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to clean
        
    Returns:
    --------
    pandas.DataFrame
        The dataframe with cleaned headers
    """
    # Adjust header format
    df.columns = df.columns.str.replace('\n', ' ', regex=False)
    df.columns = df.columns.str.replace('\t', ' ', regex=False)
    df.columns = df.columns.str.strip()
    
    # Replace "nan:" with "Und zwar:"
    df.columns = df.columns.str.replace('nan:', 'Und zwar:')
    
    # Standardize Brandenburg column name
    df.columns = df.columns.str.replace('Branden- burg', 'Brandenburg')
    
    return df

def analyze_headers():
    """
    Analyze headers across all years and create a comparison CSV.
    """
    # Dictionary to store headers for each year
    headers_by_year = {}
    
    # Process each year
    for year in YEARS_TO_PROCESS:
        file_path = get_file_path(year)
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Warning: File not found for year {year}: {file_path}")
            continue
            
        print(f"\nAnalyzing headers for year {year}...")
        
        # Read headers from Excel file
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)
        
        # Clean headers
        df = clean_header(df)
        
        # Store headers for this year
        headers_by_year[year] = list(df.columns)
    
    if not headers_by_year:
        print("No files were processed. Please check the file paths and years.")
        return None
    
    # Create a DataFrame to compare headers across years
    all_headers = set()
    for headers in headers_by_year.values():
        all_headers.update(headers)
    
    # Create comparison DataFrame
    comparison_df = pd.DataFrame(index=sorted(all_headers))
    
    # Fill in headers for each year
    for year, headers in headers_by_year.items():
        comparison_df[year] = comparison_df.index.isin(headers)
    
    # Save the comparison to CSV
    output_file = f'{SHEET_NAME}_header_analysis.csv'
    comparison_df.to_csv(output_file)
    print(f"\nHeader analysis has been saved to: {output_file}")
    
    # Check for consistency
    all_headers_same = all(
        set(headers) == set(headers_by_year[list(headers_by_year.keys())[0]])
        for headers in headers_by_year.values()
    )
    
    if all_headers_same:
        print("\n✅ All years have the same headers!")
    else:
        print("\n⚠️ Warning: Headers are not consistent across all years.")
        print("Please check the header analysis CSV for details.")
    
    return comparison_df

if __name__ == "__main__":
    df = analyze_headers() 