# Data Cleaning Documentation - FZ2.4

## 1. Project Overview
**Business Problem and Context:**
- This script processes KBA (Kraftfahrt-Bundesamt) vehicle registration data from sheet FZ2.4
- Data contains vehicle registrations by manufacturers and model names with additional regional information
- Key challenges include handling manufacturer and model name standardization, merged cells, and regional data consistency
- Expected output is a cleaned dataset with standardized headers and consistent data format across years

## 2. Data Inconsistencies and Solutions

### 2.1 Header Format Inconsistencies
- **Problem**: Common header issues identified:
  - Multi-line headers with line breaks
  - Inconsistent spacing and special characters
  - Mixed language terminology
  - "nan:" prefixes in headers
  - Inconsistent naming conventions for similar fields
  - Special case for Brandenburg column name

- **Solution**: Header normalization implemented:
```python
def clean_header(df):
    """Clean and format the dataframe headers."""
    df.columns = df.columns.str.replace('\n', ' ', regex=False)
    df.columns = df.columns.str.replace('\t', ' ', regex=False)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('nan:', 'Und zwar:')
    df.columns = df.columns.str.replace('Branden- burg', 'Brandenburg')
    return df
```

### 2.2 Data Type Standardization
- **Problem**: Data type issues identified:
  - Merged cells in manufacturer and model name columns
  - Inconsistent numeric formats
  - Special characters in text fields
  - Mixed data types in columns

- **Solution**: Type handling code:
```python
def fill_merged_cells(df, columns_to_fill):
    """Fill merged cells in specified columns."""
    for col in columns_to_fill:
        df[col] = df[col].fillna(method='ffill')
    return df

def extract_columns(df, source_column, target_columns, first_part_length, is_numeric=True):
    """Extract and split data from source column into target columns."""
    # Implementation for splitting columns based on length and type
```

### 2.3 Sheet Structure Validation
- **Problem**: Structure issues identified:
  - Varying number of columns across years
  - Different header positions
  - Sum rows that need to be removed
  - Inconsistent data blocks

- **Solution**: Structure validation code:
```python
def remove_sum_rows(df, filter_words='zusammen|insgesamt'):
    """Remove rows that contain sum-related words."""
    df = df.iloc[:, 1:]  # Drop empty columns
    for column in df.columns:
        df = df[~df[column].astype(str).str.lower().str.contains(
            filter_words.lower(), case=False, na=False)].reset_index(drop=True)
    return df
```

### 2.4 Data Quality Checks
- **Problem**: Data quality issues identified:
  - Inconsistent header naming across years
  - Missing required fields
  - Duplicate entries
  - Inconsistent formatting

- **Solution**: Quality validation code:
```python
def process_data():
    """Process and combine data from all years."""
    # Initialize list to store DataFrames
    dfs = []
    
    # Process each year and validate
    for year in YEARS_TO_PROCESS:
        # Read and process data
        # Validate headers and structure
        # Store processed data
```

### 2.5 Data Transformation Pipeline
- **Problem**: Need for consistent data processing across multiple files
- **Solution**: Pipeline implementation:
```python
def process_data():
    """Process and combine data from all years."""
    # 1. Read Excel file
    # 2. Clean headers
    # 3. Remove sum rows
    # 4. Fill merged cells
    # 5. Extract and split columns
    # 6. Add year column
    # 7. Combine and align data
    # 8. Save cleaned data
```

## 3. Usage Example
```python
# Import required libraries
import pandas as pd
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_cleaning.log'),
        logging.StreamHandler()
    ]
)

# Define constants and configurations
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024', '2025']
INPUT_DIR = Path('data/raw')
OUTPUT_DIR = Path('data/processed')
COLUMNS_TO_FILL = ['Land', 'Regierungsbezirk']

# Define header mappings for standardization
HEADER_MAPPINGS = {
    'darunter \nweibliche \nHalter': 'darunter \nHalterinnen',
    'und zwar \nweibliche\nHalter': 'und zwar\nHalterinnen',
    'und zwar \ngewerbliche\nHalter': 'und zwar \ngewerbliche\nHalterinnen\nund Halter',
    # Add more mappings as needed
}

# Define columns that need to be split
SOURCE_COLUMNS = {
    'Regierungsbezirk': (
        ['Regierungs_Bezirk', 'Bezirk_Name'],
        2,
        False
    ),
    'Statistische Kennziffer und Zulassungsbezirk': (
        ['Statistische Kennziffer', 'Zulassungsbezirk'],
        5,
        True
    )
}

def process_single_file(file_path: Path) -> pd.DataFrame:
    """
    Process a single data file with all cleaning steps.
    
    Args:
        file_path (Path): Path to the input Excel file
        
    Returns:
        pd.DataFrame: Cleaned and processed dataframe
    """
    try:
        # 1. Read Excel file
        df = pd.read_excel(file_path, sheet_name='FZ2.4')
        logging.info(f"Successfully read file: {file_path}")
        
        # 2. Clean headers
        df = clean_header(df)
        logging.info("Headers cleaned successfully")
        
        # 3. Remove sum rows
        df = remove_sum_rows(df)
        logging.info("Sum rows removed")
        
        # 4. Fill merged cells
        df = fill_merged_cells(df, COLUMNS_TO_FILL)
        logging.info("Merged cells filled")
        
        # 5. Extract and split columns
        for source_col, (target_cols, length, is_numeric) in SOURCE_COLUMNS.items():
            df = extract_columns(df, source_col, target_cols, length, is_numeric)
        logging.info("Columns extracted and split")
        
        # 6. Apply manual replacements
        df = apply_manual_replacements(df)
        logging.info("Manual replacements applied")
        
        return df
        
    except Exception as e:
        logging.error(f"Error processing file {file_path}: {str(e)}")
        raise

def main():
    """
    Main function to process all files for specified years.
    """
    try:
        # Create output directory if it doesn't exist
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        
        # Process each year
        for year in YEARS_TO_PROCESS:
            input_file = INPUT_DIR / f'FZ2.4_{year}.xlsx'
            output_file = OUTPUT_DIR / f'FZ2.4_{year}_cleaned.csv'
            
            if not input_file.exists():
                logging.warning(f"File not found: {input_file}")
                continue
                
            # Process the file
            df = process_single_file(input_file)
            
            # Save the cleaned data
            df.to_csv(output_file, index=False, encoding='utf-8')
            logging.info(f"Cleaned data saved to: {output_file}")
            
            # Generate validation report
            validation_report = generate_validation_report(df)
            report_file = OUTPUT_DIR / f'FZ2.4_{year}_validation_report.txt'
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(validation_report)
            logging.info(f"Validation report saved to: {report_file}")
            
    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()
```

### Example Output
After running the script, you'll get:
1. Cleaned CSV files for each year in the `data/processed` directory
2. Validation reports for each processed file
3. A log file (`data_cleaning.log`) with detailed processing information

### Sample Validation Report
```
Data Validation Report - FZ2.4_2023
==================================
1. Data Completeness
   - Total rows: 15,432
   - Missing values: 0.02%
   - Complete columns: 98%

2. Data Consistency
   - Header standardization: 100%
   - Numeric format consistency: 100%
   - Date format consistency: 100%

3. Data Quality
   - Duplicate entries: 0
   - Invalid values: 0
   - Outliers detected: 12

4. Processing Summary
   - Processing time: 2.3 seconds
   - Memory usage: 156 MB
   - Files processed: 1
```

### Common Issues and Solutions
1. **Memory Issues**
   - If processing large files, use `chunk_size` parameter in `pd.read_excel()`
   - Implement garbage collection after processing each file

2. **Encoding Problems**
   - Use `encoding='utf-8'` for file operations
   - Handle special characters with `errors='replace'`

3. **Performance Optimization**
   - Use `dtype` parameter to specify column types
   - Implement parallel processing for multiple files
   - Use `swifter` for faster apply operations

4. **Error Handling**
   - Implement retry mechanism for file operations
   - Add timeout for external API calls
   - Use context managers for file operations

## 4. Best Practices
1. Always validate headers before processing data
2. Use standardized header mappings
3. Handle special characters and encodings carefully
4. Implement comprehensive error logging
5. Document all data transformations
6. Keep original data intact
7. Use consistent naming conventions
8. Generate detailed validation reports

## 5. Documentation Standards
1. **Code Formatting**
   - Use consistent indentation
   - Include type hints
   - Add docstrings
   - Follow PEP 8 guidelines

2. **Documentation Structure**
   - Clear section hierarchy
   - Consistent formatting
   - Cross-references where needed
   - Version history

3. **Examples**
   - Include sample data
   - Show expected outputs
   - Demonstrate error cases
   - Provide use cases

4. **Maintenance**
   - Update frequency
   - Change log
   - Version control
   - Review process 