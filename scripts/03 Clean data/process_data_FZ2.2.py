# Import required libraries
import pandas as pd
import numpy as np
import os
import re
from analyze_headers_FZ2_2 import (
    BASE_PATH, SHEET_NAME, YEARS_TO_PROCESS,
    HEADER_MAPPINGS, standardize_header, determine_header
)

# Ensure 2024 is included in YEARS_TO_PROCESS
if '2024' not in YEARS_TO_PROCESS:
    YEARS_TO_PROCESS.append('2024')

# Define columns for data cleaning
COLUMNS_TO_FILL = ['Hersteller', 'Handelsname']

# Define columns that need to be split (empty dict if no columns need splitting)
SOURCE_COLUMNS = {}

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
    
    # Remove "Und zwar: " prefix from all column names
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
        if col in df.columns:
            df[col] = df[col].fillna(method='ffill')
        else:
            print(f"Warning: Column '{col}' not found in DataFrame columns: {df.columns.tolist()}")
    return df

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
    # Use different header row for 2020, 2021, and 2022
    if year in ['2020', '2021', '2022']:
        header_row = 8  # header is on row 9 (zero-based index)
    else:
        header_row = 7  # default
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=header_row)
    df.columns = df.columns.str.strip().str.replace('\n', '', regex=False)
    df = df.iloc[:, 1:]
    print(f"Columns read for year {year}: {df.columns.tolist()}")
    combined_headers = combined_headers[1:]
    # Align columns and headers
    min_len = min(len(df.columns), len(combined_headers))
    df = df.iloc[:, :min_len]
    df.columns = combined_headers[:min_len]
    
    # Clean headers
    df = clean_header(df)
    print(f"Columns after clean_header for year {year}: {df.columns.tolist()}")
    
    # Clean sum lines
    df = remove_sum_rows(df)
    
    # Deal with merged Columns in values
    df = fill_merged_cells(df, COLUMNS_TO_FILL)
    
    # Drop completely empty columns
    df = df.dropna(axis=1, how='all')
    
    # Add year column
    df['year'] = year
    
    return df

def main():
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
    
    # Align all DataFrames to the union of all columns
    if all_data:
        # Get the union of all columns
        all_columns = set()
        for df in all_data:
            all_columns.update(df.columns)
        all_columns = list(all_columns)
        # Reindex each DataFrame to have the same columns
        all_data = [df.reindex(columns=all_columns) for df in all_data]
        combined_df = pd.concat(all_data, ignore_index=True)
        # Remove duplicate columns if any
        combined_df = combined_df.loc[:, ~combined_df.columns.duplicated()]
        output_file = f'{SHEET_NAME}_combined.csv'
        combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nCombined data has been saved to: {output_file}")
        return combined_df
    else:
        print("No data was processed successfully.")
        return None

if __name__ == "__main__":
    df = main() 