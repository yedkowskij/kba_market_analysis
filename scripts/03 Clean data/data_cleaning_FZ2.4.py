# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import glob
import os

# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023']  # Add or remove years as needed

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/02 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Herstellern und Handelsnamen (FZ 2)'
SHEET_NAME = 'FZ 2.4'

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

def process_data():
    """
    Process and combine data from all years.
    """
    # Initialize an empty list to store DataFrames for each year
    dfs = []
    
    # Process each year
    for year in YEARS_TO_PROCESS:
        file_path = get_file_path(year)
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Warning: File not found for year {year}: {file_path}")
            continue
            
        print(f"\nProcessing year {year}...")
        
        # Read data starting from line 8 (index 7) which contains the headers
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)
        
        # 1) Clean headers
        df = clean_header(df)

        # 2) Clean sum lines
        df = remove_sum_rows(df)

        # 3) Deal with merged Columns in values
        df = fill_merged_cells(df, COLUMNS_TO_FILL)

        # 4) Separate merged values in columns (only if SOURCE_COLUMNS is not empty)
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
        df['Jahr'] = year
        
        # Append to list of DataFrames
        dfs.append(df)
    
    if not dfs:
        print("No data was processed. Please check the file paths and years.")
        return None
    
    # Align columns (ensure all years have the same columns)
    all_columns = set()
    for df in dfs:
        all_columns.update(df.columns)
    
    # Reindex all DataFrames to have the same columns
    aligned_dfs = [df.reindex(columns=sorted(all_columns)) for df in dfs]
    
    # Combine aligned DataFrames
    final_df = pd.concat(aligned_dfs, ignore_index=True)
    
    # Save the combined data to CSV
    output_file = f'{SHEET_NAME}_combined.csv'
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\nCombined data has been saved to: {output_file}")
    
    return final_df

def check_dataframes():
    """
    Check the first 2 rows of each year's DataFrame to verify data alignment.
    """
    for year in YEARS_TO_PROCESS:
        file_path = get_file_path(year)
        if not os.path.exists(file_path):
            print(f"Warning: File not found for year {year}: {file_path}")
            continue
        print(f"\nYear: {year}")
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)
        print(df.head(2))
        print("-" * 80)

if __name__ == "__main__":
    check_dataframes()
    df = process_data() 