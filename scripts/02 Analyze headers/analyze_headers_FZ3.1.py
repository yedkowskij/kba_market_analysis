# Import required libraries
import pandas as pd
import os
import re

# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024', '2025']

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/03 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Gemeinden (FZ 3)'
SHEET_NAME = 'FZ 3.1'

# Define header standardization mappings
HEADER_STANDARDIZATION = {
    # Gemeinde/PLZ variations
    r'^: PLZ, Gemeinde$': 'Gemeinde (PLZ)',
    r'^Gemeinde \(Postleitzahl\)$': 'Gemeinde (PLZ)',
    r'^Gemeinde$': 'Gemeinde (PLZ)',
    r'^Gemeinde $': 'Gemeinde (PLZ)',
    
    # Gewerbliche Halter variations
    r'^darunter gewerbliche Halter$': 'darunter gewerbliche Halterinnen und Halter',
    
    # Land-/Forstwirtschaftliche Zugmaschinen variations
    r'.*land-.*forst.*wirtschaftliche.*Zugma.*schinen.*': 'darunter land-/forst-wirtschaftliche Zugmaschinen',
    r'.*land-.*forst.*wirtschaftliche.*Zugmaschinen.*': 'darunter land-/forst-wirtschaftliche Zugmaschinen',
    r'^dar\.land-.*forstwirt-.*schaftliche.*Zugma-.*schinen$': 'darunter land-/forst-wirtschaftliche Zugmaschinen',
    
    # Kraftfahrzeuge variations
    r'.*Kraftfahr.*zeuge.*insgesamt.*': 'Kraftfahrzeuge insgesamt',
    r'.*Kraftfahr.*zeug.*anhänger.*': 'Kraftfahrzeuganhänger',
    r'^Kraftfahrzeuge insgesamt$': 'Kraftfahrzeuge insgesamt',
    r'^Kraftfahrzeuganhänger$': 'Kraftfahrzeuganhänger',
    
    # Handle empty/nan values
    r'^nan.*$': '',
    r'^$': ''
}

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
    return os.path.join(BASE_PATH, f'fz3_{year}.xlsx')

def determine_header(file_path, sheet_name='FZ3.1'):
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
                              skiprows=6,  # Skip first 7 rows to get to row 8
                              nrows=2)     # Read 2 rows (8 and 9)
    
    # Get the headers from both rows
    header_row1 = header_rows.iloc[0]  # Row 8
    header_row2 = header_rows.iloc[1]  # Row 9
    
    # Combine headers based on the specified logic
    combined_headers = []
    for col1, col2 in zip(header_row1, header_row2):
        if pd.notna(col1):  # If line 8 has a value
            if pd.notna(col2):  # If line 9 also has a value
                combined_headers.append(f"{col1}: {col2}")
            else:
                combined_headers.append(col1)
        else:  # If line 8 has no value
            combined_headers.append(col2 if pd.notna(col2) else '')
            
    return combined_headers

def standardize_header(header):
    """
    Standardize a header according to the defined mappings.
    
    Parameters:
    -----------
    header : str
        The header to standardize
        
    Returns:
    --------
    str
        The standardized header
    """
    # First clean the header
    if pd.isna(header):
        return ''
        
    header = str(header).replace('\n', ' ').replace('\t', ' ').strip()
    header = re.sub(r'\s+', ' ', header)  # Replace multiple spaces with single space
    
    # Remove any 'nan:' prefix
    header = re.sub(r'^nan:\s*', '', header)
    
    # Special case for Kraftfahrzeuge columns
    if 'Kraftfahrzeuge insgesamt' in header:
        return 'Kraftfahrzeuge insgesamt'
    if 'Kraftfahrzeuganhänger' in header:
        return 'Kraftfahrzeuganhänger'
    
    # Apply standardization mappings
    for pattern, replacement in HEADER_STANDARDIZATION.items():
        if re.search(pattern, header, re.IGNORECASE):
            return replacement
    
    return header

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
    # Print original columns
    print("\nOriginal columns:")
    print(df.columns.tolist())
    
    # Clean and standardize headers
    df.columns = [standardize_header(col) for col in df.columns]
    
    # Print cleaned columns
    print("\nCleaned columns:")
    print(df.columns.tolist())
    
    return df

def analyze_headers():
    """
    Analyze headers across all years and create a comparison CSV.
    """
    header_data = []
    
    for year in YEARS_TO_PROCESS:
        print(f"\nAnalyzing headers for year: {year}")
        file_path = get_file_path(year)
        
        try:
            # Get headers for the year
            headers = determine_header(file_path, SHEET_NAME)
            
            # Standardize headers
            headers = [standardize_header(header) for header in headers]
            
            # Create a DataFrame with headers and year
            year_df = pd.DataFrame({
                'Column_Index': range(len(headers)),
                'Header': headers,
                'Year': year
            })
            
            header_data.append(year_df)
            print(f"Successfully analyzed headers for {year}")
            
        except Exception as e:
            print(f"Error analyzing headers for {year}: {str(e)}")
            continue
    
    if not header_data:
        raise Exception("No header data was successfully analyzed")
    
    # Combine all header data
    combined_headers = pd.concat(header_data, ignore_index=True)
    
    # Pivot the data to compare headers across years
    header_comparison = combined_headers.pivot(
        index='Column_Index',
        columns='Year',
        values='Header'
    )
    
    # Save the header analysis to CSV
    output_file = f'{SHEET_NAME}_header_analysis.csv'
    header_comparison.to_csv(output_file, encoding='utf-8-sig')
    print(f"\nHeader analysis has been saved to: {output_file}")
    
    # Check for consistency
    is_consistent = True
    for year in YEARS_TO_PROCESS:
        if year in header_comparison.columns:
            if not header_comparison[year].equals(header_comparison[YEARS_TO_PROCESS[0]]):
                is_consistent = False
                print(f"\nWarning: Headers for {year} are inconsistent with {YEARS_TO_PROCESS[0]}")
                # Print the differences
                diff_mask = header_comparison[year] != header_comparison[YEARS_TO_PROCESS[0]]
                if diff_mask.any():
                    print("\nDifferences found:")
                    for idx in diff_mask[diff_mask].index:
                        print(f"Column {idx}:")
                        print(f"  {YEARS_TO_PROCESS[0]}: {header_comparison.loc[idx, YEARS_TO_PROCESS[0]]}")
                        print(f"  {year}: {header_comparison.loc[idx, year]}")
    
    if is_consistent:
        print("\nSuccess: Headers are consistent across all years")
    else:
        print("\nWarning: Headers are inconsistent across years. Please check the header analysis file.")
    
    return header_comparison

if __name__ == "__main__":
    header_comparison = analyze_headers() 