# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import glob
import os

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/02 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Herstellern und Handelsnamen (FZ 2)'
SHEET_NAME = 'FZ 2.2'
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023']  # Add or remove years as needed

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

# Define columns for data cleaning
COLUMNS_TO_FILL = ['Hersteller', 'Handelsname']

# Define columns that need to be split (empty dict if no columns need splitting)
# Format: 'source_column': (target_columns, first_part_length, is_numeric)
SOURCE_COLUMNS = {}  # Empty by default, add columns here when needed

# region Example Column Splits
# Example:
# SOURCE_COLUMNS = {
#     # Split into two columns, first part is numeric (5 digits)
#     'Statistische Kennziffer und Zulassungsbezirk': (
#         ['Statistische Kennziffer', 'Zulassungsbezirk'],
#         5,
#         True
#     ),
#     # Split into two columns, first part is letters (2 characters)
#     'Regierungsbezirk': (
#         ['Regierungs_Bezirk', 'Bezirk_Name'],
#         2,
#         False
#     ),
#     # Split into single column, first part is numeric (3 digits)
#     'Kennzeichen': (
#         ['Kennzeichen_Nummer'],
#         3,
#         True
#     ),
#     # Split into three columns, first part is letters (4 characters)
#     'Fahrzeug Details': (
#         ['Typ', 'Modell', 'Version'],
#         4,
#         False
#     )
# }
# endregion

def standardize_header(header):
    """
    Standardize header names using the mapping dictionary.
    
    Parameters:
    -----------
    header : str
        Original header name
        
    Returns:
    --------
    str
        Standardized header name
    """
    if pd.isna(header):
        return ''
    header = str(header)
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
    
    # Standardize headers
    df.columns = [standardize_header(col) for col in df.columns]
    
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
    
    # Filter all columns in the dataframe
    for column in df.columns:
        df = df[~df[column].astype(str).str.lower().str.contains(filter_words.lower(), case=False, na=False)].reset_index(drop=True)
    
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
        df[col] = df[col].fillna(method='ffill')
    return df

def extract_columns(df, source_column, target_columns, first_part_length, is_numeric=True):
    """
    Extract and split data from a source column into target columns.
    
    Parameters:
    -----------
    df : pandas.DataFrame
        The dataframe to modify
    source_column : str
        The source column name containing the data to split
    target_columns : str or list
        The target column name(s) for the extracted data
    first_part_length : int
        Number of characters for the first part
    is_numeric : bool
        If True, first part is numeric (\\d), if False, first part is letters ([A-ZÄÖÜa-zäöü])
    
    Returns:
    --------
    pandas.DataFrame
        The modified dataframe
    """
    # Convert single target column to list for consistent handling
    if isinstance(target_columns, str):
        target_columns = [target_columns]
    
    # Create pattern based on whether we're extracting one or two columns
    if len(target_columns) == 1:
        # For single column extraction, remove the first part
        pattern_type = '\\d' if is_numeric else '[A-ZÄÖÜa-zäöü]'
        pattern = f'^{pattern_type}{{{first_part_length}}}\\s+'
        df[target_columns[0]] = df[source_column].str.replace(pattern, '', regex=True)
    else:
        # For two column extraction, capture both parts
        pattern_type = '\\d' if is_numeric else '[A-ZÄÖÜa-zäöü]'
        pattern = f'({pattern_type}{{{first_part_length}}})\\s+(.+)'
        df[target_columns] = df[source_column].str.extract(pattern)
    
    return df

def validate_headers():
    """
    Validate headers across all years to ensure consistency.
    
    Returns:
    --------
    dict
        Dictionary containing header information for each year
    """
    header_info = {}
    for year in YEARS_TO_PROCESS:
        file_path = os.path.join(BASE_PATH, f'fz2_{year}.xlsx')
        try:
            combined_headers = determine_header(file_path, SHEET_NAME)
            standardized_headers = [standardize_header(h) for h in combined_headers]
            header_info[year] = {
                'original': combined_headers,
                'standardized': standardized_headers
            }
            print(f"\nHeaders for {year}:")
            print("Original headers:")
            print(combined_headers)
            print("\nStandardized headers:")
            print(standardized_headers)
            print("\n" + "="*80)
        except Exception as e:
            print(f"Error reading headers for {year}: {str(e)}")
    return header_info

def process_single_file(file_path):
    """
    Process a single Excel file and return cleaned dataframe.
    
    Parameters:
    -----------
    file_path : str
        Path to the Excel file
        
    Returns:
    --------
    pandas.DataFrame
        Cleaned dataframe with year column added
    """
    # Extract year from file path
    year = re.search(r'fz2_(\d{4})\.xlsx', file_path).group(1)
    
    # Get and apply combined headers
    combined_headers = determine_header(file_path, SHEET_NAME)
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)
    df.columns = combined_headers
    df = df[1:].reset_index(drop=True)
    
    # Clean headers
    df = clean_header(df)
    
    # Clean sum lines
    df = remove_sum_rows(df)
    
    # Deal with merged Columns in values
    df = fill_merged_cells(df, COLUMNS_TO_FILL)
    
    # Separate merged values in columns if needed
    if SOURCE_COLUMNS:
        for source_col, params in SOURCE_COLUMNS.items():
            df = extract_columns(
                df,
                source_col,
                params[0],
                params[1],
                params[2]
            )
    
    # Add year column
    df['year'] = year
    
    return df

def main():
    # First validate headers
    print("Validating headers across all years...")
    header_info = validate_headers()
    
    # Get list of files to process
    excel_files = []
    for year in YEARS_TO_PROCESS:
        file_path = os.path.join(BASE_PATH, f'fz2_{year}.xlsx')
        if os.path.exists(file_path):
            excel_files.append(file_path)
    
    # Process each file
    all_data = []
    for file_path in excel_files:
        try:
            print(f"\nProcessing {file_path}...")
            df = process_single_file(file_path)
            all_data.append(df)
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Combine and save
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        output_file = f'{SHEET_NAME}_combined.csv'
        combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nCombined data has been saved to: {output_file}")
        return combined_df
    else:
        print("No data was processed successfully.")
        return None

if __name__ == "__main__":
    df = main() 