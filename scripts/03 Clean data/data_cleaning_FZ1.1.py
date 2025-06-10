# Import required libraries
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re
import glob
import os

# Define base path and sheet name
BASE_PATH = 'kba_market_analysis/data_source/Bestand/01 Kraftfahrzeuge und Kraftfahrzeuganhänger nach Zulassungsbezirken (FZ 1)'
SHEET_NAME = 'FZ1.1'

# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024', '2025']

# Define columns for data cleaning
COLUMNS_TO_FILL = ['Land', 'Regierungsbezirk']

# Define columns that need to be split (empty dict if no columns need splitting)
# Format: 'source_column': (target_columns, first_part_length, is_numeric)
SOURCE_COLUMNS = {
    # Split into two columns, first part is letters (2 characters)
     'Regierungsbezirk': (
         ['Regierungs_Bezirk', 'Bezirk_Name'],
         2,
         False
     ),
     # Split into two columns, first part is numeric (5 digits)
     'Statistische Kennziffer und Zulassungsbezirk': (
         ['Statistische Kennziffer', 'Zulassungsbezirk'],
         5,
         True
     )
}  # Empty by default, add columns here when needed

#region Example Column Splits
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
#endregion

# Define header standardization mappings
HEADER_MAPPINGS = {
    'darunter \nweibliche \nHalter': 'darunter \nHalterinnen',
    'und zwar \nweibliche\nHalter': 'und zwar\nHalterinnen',
    'und zwar \ngewerbliche\nHalter': 'und zwar \ngewerbliche\nHalterinnen\nund Halter',
    'nan: Kraft-\nomni-\nbusse': 'nan: Kraftomni-\nbusse',
    'nan: Kraftfahr-\nzeug-\nanhänger': 'nan: Kraftfahrzeug-\nanhänger',
    'darunter\nland-/forst-\nwirtschaft-\nliche Zug-\nmaschinen': 'davon\nland-/forst-\nwirtschaft-\nliche Zug-\nmaschinen',
    'land-/forst-\nwirtschaft-\nliche Zug-\nmaschinen\nbeinhalten\nleichte Zug-maschinen': 'davon\nsonstige Zug-\nmaschinen',
    'darunter \nSattelzug-\nmaschinen': 'davon\nSattelzug-\nmaschinen'
}

def standardize_header(header):
    """
    Standardize header names to ensure consistency across years.
    
    Parameters:
    -----------
    header : str
        The header to standardize
        
    Returns:
    --------
    str
        The standardized header
    """
    # Convert to string and handle NaN
    if pd.isna(header):
        return ''
    
    header = str(header)
    
    # Apply standardizations from mapping
    for old, new in HEADER_MAPPINGS.items():
        if header == old:
            return new
    
    return header

def determine_header(file_path, sheet_name='FZ1.1'):
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
    
    # Use line 9 as base, add line 8's value if it exists
    combined_headers = []
    for col1, col2 in zip(header_row1, header_row2):
        if pd.notna(col1):  # If line 8 has a value
            combined_headers.append(f"{col2}: {col1}")
        else:
            combined_headers.append(col2)
            
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
    # Clean column names: remove newlines, tabs, extra spaces, and standardize
    df.columns = (
        df.columns
        .map(standardize_header)  # Apply standardization first
        .str.replace('\n', ' ', regex=False)
        .str.replace('\t', ' ', regex=False)
        .str.replace(' +', ' ', regex=True)
        .str.replace('^Und zwar: ', '', regex=True)
        .str.replace('^nan: ', '', regex=True)
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
    print("Available columns:", df.columns.tolist())
    print("Columns to fill:", columns_to_fill)
    
    for col in columns_to_fill:
        if col in df.columns:
            df[col] = df[col].fillna(method='ffill')
        else:
            print(f"Warning: Column '{col}' not found in DataFrame")
    
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
    year = re.search(r'fz1_(\d{4})\.xlsx', file_path).group(1)
    print(f"\nProcessing file for year {year}")

    # 1) Get and apply combined headers
    combined_headers = determine_header(file_path, SHEET_NAME)
    df = pd.read_excel(file_path, sheet_name=SHEET_NAME, header=7)  # Start from line 8
    df.columns = combined_headers
    df = df.reset_index(drop=True)  # Reset index without dropping first row
    
    # 2) Clean headers
    df = clean_header(df)

    # 3) Clean sum lines
    df = remove_sum_rows(df)

    # 4) Deal with merged Columns in values
    df = fill_merged_cells(df, COLUMNS_TO_FILL)

    # 5) Separate merged values in columns (only if SOURCE_COLUMNS is not empty)
    if SOURCE_COLUMNS:
        for source_col, params in SOURCE_COLUMNS.items():
            df = extract_columns(
                df,
                source_col,
                params[0],
                params[1],
                params[2]
            )
    
    # 6) Apply manual replacements
    df = manual_replacements(df)
    
    # Add year column
    df['year'] = year
    
    return df

def validate_headers():
    """
    Validate headers across all files to ensure consistency.
    This function will:
    1. Read headers from each file
    2. Compare them to identify any differences
    3. Print a report of any inconsistencies found
    
    Returns:
    --------
    dict
        Dictionary containing header information for each year
    """
    print("\nValidating headers across files...")
    header_info = {}
    
    for year in YEARS_TO_PROCESS:
        file_path = os.path.join(BASE_PATH, f'fz1_{year}.xlsx')
        if not os.path.exists(file_path):
            print(f"Warning: File for year {year} not found at {file_path}")
            continue
            
        try:
            # Get headers for this file
            combined_headers = determine_header(file_path, SHEET_NAME)
            # Standardize headers
            combined_headers = [standardize_header(h) for h in combined_headers]
            header_info[year] = combined_headers
            print(f"\nHeaders for {year}:")
            print(combined_headers)
        except Exception as e:
            print(f"Error reading headers for {year}: {str(e)}")
    
    # Compare headers across years
    if len(header_info) > 1:
        print("\nAnalyzing header differences...")
        all_headers = set()
        for headers in header_info.values():
            all_headers.update(headers)
        
        # Check for missing headers in each year
        for year, headers in header_info.items():
            missing_headers = all_headers - set(headers)
            if missing_headers:
                print(f"\nYear {year} is missing these headers:")
                for header in sorted(missing_headers):
                    print(f"  - {header}")
        
        # Check for extra headers in each year
        for year, headers in header_info.items():
            extra_headers = set(headers) - all_headers
            if extra_headers:
                print(f"\nYear {year} has extra headers:")
                for header in sorted(extra_headers):
                    print(f"  - {header}")
    
    return header_info

def main():
    # First validate headers across all files
    header_info = validate_headers()
    
    # Get list of all Excel files in the directory for the specified years
    excel_files = []
    for year in YEARS_TO_PROCESS:
        file_path = os.path.join(BASE_PATH, f'fz1_{year}.xlsx')
        if os.path.exists(file_path):
            excel_files.append(file_path)
    
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