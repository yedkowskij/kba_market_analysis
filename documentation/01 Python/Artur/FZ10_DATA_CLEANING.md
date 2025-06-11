# FZ10 Data Cleaning Documentation

## 1. Project Overview
**Business Problem and Context:**
- The project involves processing and cleaning FZ-10 workbooks containing German vehicle registration data
- Data comes in Excel format with multiple sheets containing different aspects of vehicle statistics
- The goal is to create clean, standardized datasets for downstream analytics

## 2. Data Inconsistencies and Solutions

### 2.1 Header Format Inconsistencies
- **Problem**: Headers in FZ-10 files often contain:
  - Line breaks within cells
  - Inconsistent spacing
  - Mixed German and English terminology
  - Special characters

- **Solution**: Implemented header normalization:
```python
def _normalize_header(header):
    """Normalize header text by removing special characters and standardizing format."""
    if pd.isna(header):
        return ''
    
    # Convert to string and remove line breaks
    header = str(header).replace('\n', ' ').strip()
    
    # Replace common German terms with English equivalents
    replacements = {
        'Fahrzeugklasse': 'Vehicle Class',
        'Kraftstoffart': 'Fuel Type',
        'Getriebeart': 'Transmission Type',
        'Schadstoffklasse': 'Emission Class'
    }
    
    for de, en in replacements.items():
        header = header.replace(de, en)
    
    # Remove special characters and normalize spaces
    header = re.sub(r'[^\w\s]', '', header)
    header = re.sub(r'\s+', ' ', header)
    
    return header.strip()

def _process_headers(df):
    """Process all column headers in a dataframe."""
    df.columns = [_normalize_header(col) for col in df.columns]
    return df
```

### 2.2 Data Type Standardization
- **Problem**: Various data type issues:
  - Mixed numeric formats (German vs. English)
  - Inconsistent date formats
  - Special characters in text fields
  - Hidden Excel formulas
  - Percentage values in different formats

- **Solution**: Comprehensive data type handling:
```python
def _standardize_numeric(value):
    """Convert various numeric formats to float."""
    if pd.isna(value) or value == '':
        return None
    
    # Convert to string and clean
    value = str(value).strip()
    
    # Handle percentage values
    if '%' in value:
        value = value.replace('%', '').strip()
        try:
            return float(value.replace(',', '.')) / 100
        except ValueError:
            return None
    
    # Handle German number format (1.234,56)
    if ',' in value and '.' in value:
        value = value.replace('.', '').replace(',', '.')
    else:
        value = value.replace(',', '.')
    
    try:
        return float(value)
    except ValueError:
        return None

def _standardize_date(value):
    """Convert various date formats to YYYY-MM-DD."""
    if pd.isna(value) or value == '':
        return None
    
    value = str(value).strip()
    
    # Handle Excel date numbers
    if isinstance(value, (int, float)):
        try:
            return (pd.to_datetime('1899-12-30') + 
                   pd.Timedelta(days=int(value))).strftime('%Y-%m-%d')
        except:
            return None
    
    # Common German date formats
    formats = [
        '%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d',
        '%d.%m.%y', '%d-%m-%y', '%y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            return pd.to_datetime(value, format=fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    return None

def _clean_text(value):
    """Standardize text fields and handle special characters."""
    if pd.isna(value) or value == '':
        return ''
    
    value = str(value).strip()
    
    # Replace German special characters
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'ß': 'ss'
    }
    
    for old, new in replacements.items():
        value = value.replace(old, new)
    
    # Remove non-ASCII characters
    value = ''.join(char for char in value if ord(char) < 128)
    
    return value.strip()
```

### 2.3 Sheet Structure Validation
- **Problem**: Inconsistent sheet structures:
  - Varying number of columns
  - Different header positions
  - Missing or extra rows
  - Inconsistent data blocks

- **Solution**: Implemented structure validation:
```python
def _validate_sheet_structure(df, expected_columns):
    """Validate sheet structure against expected format."""
    issues = []
    
    # Check column presence
    missing_cols = set(expected_columns) - set(df.columns)
    if missing_cols:
        issues.append(f"Missing columns: {missing_cols}")
    
    # Check for empty rows
    empty_rows = df[df.isna().all(axis=1)].index.tolist()
    if empty_rows:
        issues.append(f"Empty rows found at indices: {empty_rows}")
    
    # Check for duplicate headers
    if len(df.columns) != len(set(df.columns)):
        issues.append("Duplicate column names found")
    
    return issues

def _fix_sheet_structure(df, expected_columns):
    """Fix common sheet structure issues."""
    # Remove empty rows
    df = df.dropna(how='all')
    
    # Ensure all expected columns exist
    for col in expected_columns:
        if col not in df.columns:
            df[col] = None
    
    # Reorder columns to match expected order
    df = df[expected_columns]
    
    return df
```

### 2.4 Data Quality Checks
- **Problem**: Various data quality issues:
  - Outliers in numeric fields
  - Inconsistent categorical values
  - Missing required fields
  - Invalid date ranges

- **Solution**: Implemented data quality validation:
```python
def _validate_numeric_range(df, column, min_val=None, max_val=None):
    """Validate numeric values are within expected range."""
    issues = []
    
    # Convert to numeric, handling errors
    numeric_values = pd.to_numeric(df[column], errors='coerce')
    
    if min_val is not None:
        below_min = numeric_values < min_val
        if below_min.any():
            issues.append(f"Values below minimum {min_val}: {below_min.sum()}")
    
    if max_val is not None:
        above_max = numeric_values > max_val
        if above_max.any():
            issues.append(f"Values above maximum {max_val}: {above_max.sum()}")
    
    return issues

def _validate_categorical_values(df, column, allowed_values):
    """Validate categorical values are in allowed set."""
    issues = []
    
    invalid_values = df[column].isin(allowed_values)
    if not invalid_values.all():
        issues.append(f"Invalid values found: {df[~invalid_values][column].unique()}")
    
    return issues

def _validate_date_range(df, date_column, min_date=None, max_date=None):
    """Validate dates are within expected range."""
    issues = []
    
    # Convert to datetime
    dates = pd.to_datetime(df[date_column], errors='coerce')
    
    if min_date is not None:
        before_min = dates < pd.to_datetime(min_date)
        if before_min.any():
            issues.append(f"Dates before {min_date}: {before_min.sum()}")
    
    if max_date is not None:
        after_max = dates > pd.to_datetime(max_date)
        if after_max.any():
            issues.append(f"Dates after {max_date}: {after_max.sum()}")
    
    return issues
```

### 2.5 Data Transformation Pipeline
- **Problem**: Need to apply all cleaning steps consistently across multiple files

- **Solution**: Implemented a comprehensive pipeline:
```python
def process_fz10_sheet(file_path, sheet_name, expected_columns):
    """Process a single FZ-10 sheet with all cleaning steps."""
    # Read the sheet
    df = pd.read_excel(file_path, sheet_name=sheet_name)
    
    # Step 1: Header normalization
    df = _process_headers(df)
    
    # Step 2: Structure validation and fixing
    structure_issues = _validate_sheet_structure(df, expected_columns)
    if structure_issues:
        print(f"Structure issues found: {structure_issues}")
        df = _fix_sheet_structure(df, expected_columns)
    
    # Step 3: Data type standardization
    for col in df.columns:
        if col in date_columns:
            df[col] = df[col].apply(_standardize_date)
        elif col in numeric_columns:
            df[col] = df[col].apply(_standardize_numeric)
        else:
            df[col] = df[col].apply(_clean_text)
    
    # Step 4: Data quality validation
    quality_issues = []
    
    # Validate numeric ranges
    for col, (min_val, max_val) in numeric_ranges.items():
        issues = _validate_numeric_range(df, col, min_val, max_val)
        quality_issues.extend(issues)
    
    # Validate categorical values
    for col, allowed_values in categorical_values.items():
        issues = _validate_categorical_values(df, col, allowed_values)
        quality_issues.extend(issues)
    
    # Validate date ranges
    for col, (min_date, max_date) in date_ranges.items():
        issues = _validate_date_range(df, col, min_date, max_date)
        quality_issues.extend(issues)
    
    if quality_issues:
        print(f"Quality issues found: {quality_issues}")
    
    return df, quality_issues
```

## 3. Usage Example
```python
# Define expected structure
expected_columns = [
    'Vehicle Class', 'Fuel Type', 'Transmission Type',
    'Emission Class', 'Registration Date', 'Count'
]

# Define validation rules
numeric_ranges = {
    'Count': (0, 1000000)
}

categorical_values = {
    'Vehicle Class': ['Car', 'Truck', 'Bus', 'Motorcycle'],
    'Fuel Type': ['Petrol', 'Diesel', 'Electric', 'Hybrid']
}

date_ranges = {
    'Registration Date': ('2020-01-01', '2025-12-31')
}

# Process a file
file_path = 'path/to/fz10_2023.xlsx'
sheet_name = 'FZ 10.1'

df, issues = process_fz10_sheet(
    file_path,
    sheet_name,
    expected_columns
)

# Export cleaned data
if not issues:
    df.to_csv('cleaned_fz10_data.csv', index=False)
else:
    print("Data quality issues found, manual review required")
```

## 4. Best Practices
1. Always validate data structure before processing
2. Handle special characters and encodings carefully
3. Implement comprehensive error logging
4. Use type hints for better code maintainability
5. Document all data transformations
6. Keep original data intact and create new cleaned versions
7. Implement data quality metrics and monitoring
8. Use consistent naming conventions across all files 