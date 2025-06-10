# Import required libraries
import pandas as pd
import numpy as np
import os
import re

# Define base path and years to process
BASE_PATH = 'kba_market_analysis/data_source/Bestand/02 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Herstellern und Handelsnamen (FZ 2)'
SHEET_NAME = 'FZ 2.2'
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024']

# Define header mappings for standardization
HEADER_MAPPINGS = {
    'nan: Hersteller\n': 'Hersteller',
    'Hersteller\n': 'Hersteller',
    'nan: Handelsname': 'Handelsname',
    'Handelsname': 'Handelsname',
    'nan: Typ-Schl.-Nr.': 'Typ-Schlüsselnummer',
    'Typ-Schl.-Nr.': 'Typ-Schlüsselnummer',
    'nan: private Halter': 'Private Halter',
    'nan: private Halterinnen\nund Halter': 'Private Halter',
    'nan: Halter\nbis 29 Jahre': 'Halter bis 29 Jahre',
    'nan: Halterinnen \nund Halter\nbis 29 Jahre': 'Halter bis 29 Jahre',
    'nan: Halter\nab 60 Jahre': 'Halter ab 60 Jahre',
    'nan: Halterinnen\nund Halter\nab 60 Jahre': 'Halter ab 60 Jahre',
    'nan: weibliche Halter': 'Weibliche Halter',
    'nan: Halterinnen': 'Weibliche Halter'
}

def standardize_header(header):
    """
    Standardize header names using the mapping dictionary.
    
    Parameters:
    -----------
    header : str or numpy.float64
        Original header name
        
    Returns:
    --------
    str
        Standardized header name
    """
    # Handle numpy.float64 and other non-string types
    if pd.isna(header) or isinstance(header, (np.float64, float)):
        return ''
    
    # Convert to string and handle any remaining NaN values
    header = str(header)
    if header.lower() == 'nan':
        return ''
        
    return HEADER_MAPPINGS.get(header, header)

def determine_header(file_path, sheet_name='FZ 2.2'):
    """
    Determine and combine headers from two potential header rows.
    
    Parameters:
    -----------
    file_path : str
        Path to the Excel file
    sheet_name : str
        Name of the sheet to read
        
    Returns:
    --------
    list
        List of combined headers
    """
    # Read lines 8 and 9 to get both potential header rows
    header_rows = pd.read_excel(file_path, 
                              sheet_name=sheet_name, 
                              skiprows=6, 
                              nrows=2)
    
    # Get the headers from both rows
    header_row1 = header_rows.iloc[0]
    header_row2 = header_rows.iloc[1]
    
    # Combine headers where line 9 has values
    combined_headers = []
    for col1, col2 in zip(header_row1, header_row2):
        if pd.notna(col2):  # If there's a value in line 9
            combined_headers.append(f"{col1}: {col2}")
        else:
            combined_headers.append(col1)
            
    return combined_headers

def analyze_headers():
    """
    Analyze headers across all years and verify consistency.
    Creates a CSV file with header information for visual comparison.
    
    Returns:
    --------
    bool
        True if headers are consistent, False otherwise
    """
    print("Analyzing headers across all years...")
    print("="*80)
    
    header_info = {}
    all_standardized_headers = set()
    
    # Create a list to store header information for CSV
    header_rows = []
    
    for year in YEARS_TO_PROCESS:
        file_path = os.path.join(BASE_PATH, f'fz2_{year}.xlsx')
        try:
            combined_headers = determine_header(file_path, SHEET_NAME)
            standardized_headers = [standardize_header(h) for h in combined_headers]
            
            # Skip the first empty column
            combined_headers = combined_headers[1:]
            standardized_headers = standardized_headers[1:]
            
            header_info[year] = {
                'original': combined_headers,
                'standardized': standardized_headers
            }
            all_standardized_headers.add(tuple(standardized_headers))
            
            # Add headers to the list for CSV, using ';' as separator and removing newlines
            header_rows.append({
                'Year': year,
                'Original_Headers': ';'.join([str(h).replace('\n', ' ').replace('\r', ' ') for h in combined_headers]).replace('nan:', 'Und zwar:'),
                'Standardized_Headers': ';'.join([str(h).replace('\n', ' ').replace('\r', ' ') for h in standardized_headers]).replace('nan:', 'Und zwar:')
            })
            
            print(f"\nHeaders for {year}:")
            print("Original headers:")
            print(combined_headers)
            print("\nStandardized headers:")
            print(standardized_headers)
            print("\n" + "="*80)
            
            # Read the file and strip column names
            df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=8)
            df.columns = df.columns.str.strip().str.replace('\n', '', regex=False)
            
        except Exception as e:
            print(f"Error reading headers for {year}: {str(e)}")
            return False
    
    # Create DataFrame and save to CSV
    header_df = pd.DataFrame(header_rows)
    header_csv_file = f'{SHEET_NAME}_header_analysis.csv'
    header_df.to_csv(header_csv_file, index=False, encoding='utf-8-sig', sep=';')
    print(f"\nHeader analysis has been saved to: {header_csv_file}")
    
    # Check if all standardized headers are identical
    if len(all_standardized_headers) == 1:
        print("\n✅ All headers are consistent across years!")
        return True
    else:
        print("\n❌ Headers are not consistent across years!")
        return False

if __name__ == "__main__":
    headers_consistent = analyze_headers()
    if headers_consistent:
        print("\nYou can now proceed with data processing using process_data_FZ2.2.py")
    else:
        print("\nPlease fix header inconsistencies before proceeding with data processing.") 