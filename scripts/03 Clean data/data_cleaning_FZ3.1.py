# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import glob
import os

# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024', '2025']

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/03 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Gemeinden (FZ 3)'
SHEET_NAME = 'FZ 3.1'

# Define columns for data cleaning
COLUMNS_TO_FILL = ['Land', 'Zulassungsbezirk']

# Define columns that need to be split
SOURCE_COLUMNS = {
    # Split into two columns, first part is numeric (5 digits)
     'Zulassungsbezirk': (
         ['Bezirk_Nummer', 'Bezirk_Name'],
         5,
         True
     ),
     # Split into two columns, first part is numeric (8 digits)
     'Gemeinde (PLZ)': (
         ['Gemeinde_Nummer', 'Gemeinde_Name'],
         8,
         True
     )
}

# Define the expected columns for all years (unified schema)
EXPECTED_COLUMNS = [
    'Land',
    'Zulassungsbezirk',
    'Gemeinde (PLZ)',
    'Krafträder',
    'Personenkraftwagen: insgesamt',
    'darunter gewerbliche Halterinnen und Halter',
    'Lastkraft- wagen',
    'Zugmaschinen: insgesamt',
    'darunter land-/forst-wirtschaftliche Zugmaschinen',
    'Sonstige Kfz einschl. Kraftomni- busse',
    'Kraftfahrzeuganhänger',
    'Jahr'  # Add year column at the end
]

# Define possible header variations for each logical column
COLUMN_VARIANTS = {
    'Gemeinde (PLZ)': ['Gemeinde (PLZ)', 'Gemeinde', 'Gemeinde (Postleitzahl)', ': PLZ, Gemeinde'],
    # Add more columns with variants if needed
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
    
    # Remove "Und zwar:" prefix from column names
    df.columns = df.columns.str.replace('^Und zwar: ', '', regex=True)
    
    return df

def remove_sum_rows(df, filter_words='zusammen|insgesamt'):
    """
    Remove rows that contain sum-related words.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to clean
    filter_words : str
        Regular expression pattern for words to filter out
        
    Returns:
    --------
    pandas.DataFrame
        The dataframe with sum rows removed
    """
    # Drop empty columns at the beginning of the file
    df = df.iloc[:, 1:]
    
    # Create a mask for rows to keep
    mask = pd.Series(True, index=df.index)
    
    # Filter all columns in the dataframe
    for column in df.columns:
        try:
            column_series = df[column].squeeze()  # Try to convert to Series
            if isinstance(column_series, pd.Series):
                column_mask = ~column_series.fillna('').astype(str).str.contains(filter_words, case=False, regex=True)
                mask = mask & column_mask
        except Exception as e:
            print(f"Error processing column {column}: {str(e)}")
    
    # Apply the mask and reset index
    df = df[mask].reset_index(drop=True)
    
    return df

def fill_merged_cells(df, columns_to_fill):
    """
    Fill merged cells in specified columns using forward fill method.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to clean
    columns_to_fill : list
        List of column names to fill
        
    Returns:
    --------
    pandas.DataFrame
        The dataframe with filled merged cells
    """
    for col in columns_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna(method='ffill')
    
    return df

def extract_columns(df, source_column, target_columns, first_part_length, is_numeric=True, year=None):
    """
    Extract and split columns based on specified patterns.
    
    Args:
        df (pd.DataFrame): Input DataFrame
        source_column (str): Column to split
        target_columns (list): List of new column names
        first_part_length (int): Length of first part to extract
        is_numeric (bool): Whether first part should be numeric
        year (str): Year being processed (for format-specific handling)
    """
    if source_column not in df.columns:
        print(f"Warning: Column '{source_column}' not found in DataFrame")
        return df
    
    # Create new columns
    df[target_columns[0]] = None
    df[target_columns[1]] = None
    
    # Get sample values for debugging
    print(f"\n[DEBUG] Sample values for '{source_column}' in year {year}:")
    print(df[source_column].head(10).tolist())
    
    # Handle different formats based on year
    if year in ['2020', '2021', '2022']:
        # Format: "STUTTGART,STADT (08111)"
        pattern = r'^(.*?)\s*\((\d+)\)$'
        matches = df[source_column].str.extract(pattern)
        if not matches.empty and matches.shape[1] == 2:
            df[target_columns[1]] = matches[0]  # Name
            df[target_columns[0]] = matches[1]  # Number
    else:
        # Format: "08111 STUTTGART,STADT"
        pattern = r'^(\d+)\s+(.*?)$'
        matches = df[source_column].str.extract(pattern)
        if not matches.empty and matches.shape[1] == 2:
            df[target_columns[0]] = matches[0]  # Number
            df[target_columns[1]] = matches[1]  # Name
    
    # Convert first column to numeric if specified
    if is_numeric:
        df[target_columns[0]] = pd.to_numeric(df[target_columns[0]], errors='coerce')
    
    return df

def manual_replacements(df):
    """
    Perform manual replacements for specific cases.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to modify
        
    Returns:
    --------
    pandas.DataFrame
        The modified dataframe
    """
    # Replace values for SCHLESWIG-HOLSTEIN
    mask = df.iloc[:, 0] == "SCHLESWIG-HOLSTEIN"
    df.loc[mask, df.columns[1]] = "KIEL"
    if 'Bezirk_Name' in df.columns:
        df.loc[mask, 'Bezirk_Name'] = "KIEL"
    
    return df

def process_data():
    """
    Process data for all years and combine results.
    
    Returns:
    --------
    pandas.DataFrame
        Combined dataframe with all years' data
    """
    all_dfs = []
    
    for year in YEARS_TO_PROCESS:
        print(f"\nProcessing year: {year}")
        file_path = get_file_path(year)
        
        try:
            # 1) Get and apply combined headers
            combined_headers = determine_header(file_path, SHEET_NAME)
            df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)  # Start from line 8
            df.columns = combined_headers
            df = df.reset_index(drop=True)  # Reset index without dropping first row
            
            # 2) Clean headers
            df = clean_header(df)
            df.columns = df.columns.str.strip()
            print(f"\n[DEBUG] Columns after cleaning for year {year}:\n{df.columns.tolist()}")

            # 3) Clean sum lines
            df = remove_sum_rows(df)

            # 4) Deal with merged Columns in values
            df = fill_merged_cells(df, COLUMNS_TO_FILL)

            # 5) Apply flexible column alignment logic
            for logical_col, variants in COLUMN_VARIANTS.items():
                found = False
                for variant in variants:
                    if variant in df.columns:
                        df[logical_col] = df[variant]
                        found = True
                        break
                if not found:
                    df[logical_col] = pd.NA
            # Ensure all expected columns are present
            for col in EXPECTED_COLUMNS:
                if col not in df.columns:
                    df[col] = pd.NA
            df = df[EXPECTED_COLUMNS]

            # 6) Now split columns as needed
            if SOURCE_COLUMNS:
                for source_col, params in SOURCE_COLUMNS.items():
                    if source_col in df.columns:
                        if source_col == 'Zulassungsbezirk':
                            print(f"\n[DEBUG] Sample values for 'Zulassungsbezirk' in year {year}:")
                            print(df[source_col].head(10).tolist())
                        df = extract_columns(
                            df,
                            source_col,
                            params[0],
                            params[1],
                            params[2],
                            year
                        )
            
            # 7) Apply manual replacements
            df = manual_replacements(df)
            
            # Add year column
            df['Jahr'] = year
            
            all_dfs.append(df)
            print(f"Successfully processed {year}")
            
        except Exception as e:
            print(f"Error processing {year}: {str(e)}")
            continue
    
    if not all_dfs:
        raise Exception("No data was successfully processed")
    
    # Combine all dataframes
    combined_df = pd.concat(all_dfs, ignore_index=True)
    
    # Save the combined data to CSV
    output_file = f'{SHEET_NAME}_combined.csv'
    combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nCombined data has been saved to: {output_file}")
    
    return combined_df

def check_dataframes():
    """
    Print the first 2 rows of each year's DataFrame for verification.
    """
    for year in YEARS_TO_PROCESS:
        print(f"\n{'='*50}")
        print(f"Checking data for year: {year}")
        print(f"{'='*50}")
        
        try:
            file_path = get_file_path(year)
            combined_headers = determine_header(file_path, SHEET_NAME)
            df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)
            df.columns = combined_headers
            
            print("\nFirst 2 rows:")
            print(df.head(2))
            print("\nColumns:")
            print(df.columns.tolist())
            
        except Exception as e:
            print(f"Error checking {year}: {str(e)}")

if __name__ == "__main__":
    # First check the dataframes
    check_dataframes()
    
    # Then process all years
    df = process_data() 