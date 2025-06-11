# Data Cleaning Documentation - FZ3.1

## 1. Project Overview
**Business Problem and Context:**
- This script processes KBA (Kraftfahrt-Bundesamt) vehicle registration data from sheet FZ3.1
- Data contains vehicle registrations by municipalities (Gemeinden) and registration districts
- Key challenges include handling municipality codes, postal codes, and regional data consistency
- Expected output is a cleaned dataset with standardized headers and consistent data format across years

## 2. Data Inconsistencies and Solutions

### 2.1 Header Format Inconsistencies
- **Problem**: Common header issues identified:
  - Multi-line headers with line breaks
  - Inconsistent spacing and special characters
  - Mixed language terminology
  - "nan:" prefixes in headers
  - Inconsistent naming conventions for similar fields
  - Multiple variations of municipality column names

- **Solution**: Header normalization implemented:
```python
# Define expected columns for all years
EXPECTED_COLUMNS = [
    'Land',
    'Zulassungsbezirk',
    'Gemeinde (PLZ)',
    'Krafträder',
    'Personenkraftwagen: insgesamt',
    # ... additional columns
]

# Define possible header variations
COLUMN_VARIANTS = {
    'Gemeinde (PLZ)': ['Gemeinde (PLZ)', 'Gemeinde', 'Gemeinde (Postleitzahl)', ': PLZ, Gemeinde'],
    # ... additional variants
}

def clean_header(df):
    """Clean and format the dataframe headers."""
    df.columns = df.columns.str.replace('\n', ' ', regex=False)
    df.columns = df.columns.str.replace('\t', ' ', regex=False)
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace('^Und zwar: ', '', regex=True)
    return df
```

### 2.2 Data Type Standardization
- **Problem**: Data type issues identified:
  - Merged cells in key columns
  - Inconsistent numeric formats
  - Special characters in text fields
  - Mixed data types in columns
  - Different formats for municipality codes across years

- **Solution**: Type handling code:
```python
def extract_columns(df, source_column, target_columns, first_part_length, is_numeric=True, year=None):
    """Extract and split columns based on specified patterns."""
    # Handle different formats based on year
    if year in ['2020', '2021', '2022']:
        # Format: "STUTTGART,STADT (08111)"
        pattern = r'^(.*?)\s*\((\d+)\)$'
    else:
        # Format: "08111 STUTTGART,STADT"
        pattern = r'^(\d+)\s+(.*?)$'
    
    matches = df[source_column].str.extract(pattern)
    if not matches.empty and matches.shape[1] == 2:
        df[target_columns[0]] = matches[0]  # Number
        df[target_columns[1]] = matches[1]  # Name
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
    mask = pd.Series(True, index=df.index)
    for column in df.columns:
        try:
            column_series = df[column].squeeze()
            if isinstance(column_series, pd.Series):
                column_mask = ~column_series.fillna('').astype(str).str.contains(
                    filter_words, case=False, regex=True)
                mask = mask & column_mask
        except Exception as e:
            print(f"Error processing column {column}: {str(e)}")
    return df[mask].reset_index(drop=True)
```

### 2.4 Data Quality Checks
- **Problem**: Data quality issues identified:
  - Inconsistent header naming across years
  - Missing required fields
  - Duplicate entries
  - Inconsistent formatting
  - Different municipality code formats

- **Solution**: Quality validation code:
```python
def check_dataframes():
    """Validate data consistency across years."""
    # Implementation for data validation
    # Checks consistency across years
    # Generates validation report
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
    # 6. Apply manual replacements
    # 7. Add year column
    # 8. Combine and align data
    # 9. Save cleaned data
```

## 3. Usage Example
```python
# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024', '2025']

# Define columns for data cleaning
COLUMNS_TO_FILL = ['Land', 'Zulassungsbezirk']

# Define columns that need to be split
SOURCE_COLUMNS = {
    'Zulassungsbezirk': (
        ['Bezirk_Nummer', 'Bezirk_Name'],
        5,
        True
    ),
    'Gemeinde (PLZ)': (
        ['Gemeinde_Nummer', 'Gemeinde_Name'],
        8,
        True
    )
}

# Run the cleaning process
if __name__ == "__main__":
    final_df = process_data()
```

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