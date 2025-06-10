# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import glob
import os

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/06 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Herstellern und Typen (FZ 6)'
SHEET_NAME = 'FZ 6.1'

# Configuration dictionary mapping years to header row(s) or structure
HEADER_CONFIG = {
    '2020': {'header_rows': [8, 9, 10], 'data_start': 11},  # rows 9,10,11 as header, data starts at 12 (0-indexed)
    '2021': {'header_row': 8},  # row 9 as header (0-indexed)
    '2022': {'header_row': 7},
    '2023': {'header_row': 7},
    '2024': {'header_row': 7},
    '2025': {'header_row': 7},
}

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
    # Clean column names: remove newlines, tabs, extra spaces, and unify spelling
    df.columns = (
        df.columns
        .str.replace('\n', ' ', regex=False)
        .str.replace('\t', ' ', regex=False)
        .str.replace(' +', ' ', regex=True)
        .str.replace('^Und zwar: ', '', regex=True)
        .str.replace('-', '', regex=False)  # remove hyphens
        .str.replace('–', '', regex=False)  # remove en-dashes
        .str.replace(' ', '', regex=False)  # remove spaces
        .str.lower()  # lowercase for robustness
        .str.strip()
    )
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
    
    # Print DataFrame info for debugging
    print("DataFrame shape:", df.shape)
    print("DataFrame columns:", df.columns.tolist())
    
    # Create a mask for rows to keep
    mask = pd.Series(True, index=df.index)
    
    # Filter all columns in the dataframe
    for column in df.columns:
        print(f"\nProcessing column: {column}")
        print(f"Column type: {type(df[column])}")
        print(f"Column shape: {df[column].shape if hasattr(df[column], 'shape') else 'No shape'}")
        
        # Try to get the column as a Series
        try:
            column_series = df[column].squeeze()  # Try to convert to Series
            if isinstance(column_series, pd.Series):
                column_mask = ~column_series.fillna('').astype(str).str.contains(filter_words, case=False, regex=True)
                mask = mask & column_mask
            else:
                print(f"Warning: Column {column} could not be converted to Series")
        except Exception as e:
            print(f"Error processing column {column}: {str(e)}")
    
    # Apply the mask and reset index
    df = df[mask].reset_index(drop=True)
    
    return df

def process_single_file(file_path):
    """
    Process a single Excel file and return the cleaned dataframe with year column.
    
    Parameters:
    -----------
    file_path : str
        Path to the Excel file
        
    Returns:
    --------
    pandas.DataFrame
        The cleaned dataframe with year column
    """
    year = re.search(r'fz6_(\d{4})\.xlsx', file_path).group(1)
    print(f"\nProcessing file for year {year}")

    config = HEADER_CONFIG.get(year, {'header_row': 7})  # default to 7 if not found

    if 'header_rows' in config:
        # Multi-row header (e.g., 2020)
        header_rows = pd.read_excel(file_path, sheet_name=SHEET_NAME, skiprows=config['header_rows'][0], nrows=len(config['header_rows']), header=None)
        combined_headers = [
            ' '.join([str(header_rows.iloc[i, col]) for i in range(len(config['header_rows'])) if pd.notna(header_rows.iloc[i, col])]).strip()
            for col in range(header_rows.shape[1])
        ]
        # Read the actual data, starting from the first data row (do not treat any row as header)
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=None, skiprows=config['data_start'])
        df.columns = combined_headers
    else:
        df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=config['header_row'])

    df = clean_header(df)
    df = df.loc[:, ~df.columns.str.startswith('unnamed')]
    header_row = list(df.columns)
    df = df[~df.apply(lambda row: list(row.values) == header_row, axis=1)]
    df = remove_sum_rows(df)
    df['year'] = year
    return df

def main():
    # Get list of all Excel files in the directory
    excel_files = glob.glob(os.path.join(BASE_PATH, 'fz6_*.xlsx'))
    
    # Process each file and combine results
    all_data = []
    for file_path in excel_files:
        try:
            df = process_single_file(file_path)
            all_data.append(df)
            print(f"Successfully processed {file_path}")
        except Exception as e:
            print(f"Error processing {file_path}: {str(e)}")
    
    # Combine all dataframes
    if all_data:
        combined_df = pd.concat(all_data, ignore_index=True)
        
        # Save the combined data to CSV
        output_file = f'{SHEET_NAME}_combined.csv'
        combined_df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"\nCombined data has been saved to: {output_file}")
        return combined_df
    else:
        print("No data was processed successfully")
        return None

if __name__ == "__main__":
    df = main() 