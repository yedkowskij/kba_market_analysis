# Header Analysis Documentation

## 1. Project Overview
**Business Problem and Context:**
- The project involves analyzing and standardizing headers across multiple Excel files containing KBA (Kraftfahrt-Bundesamt) vehicle registration data
- Data is organized in different sheets (FZ 2.2, FZ 2.4, FZ 3.1) with varying header formats and structures
- Key challenges include inconsistent header naming, multi-line headers, and special character handling
- Expected output is a standardized header format that can be used consistently across all years (2020-2024)

## 2. Data Inconsistencies and Solutions

### 2.1 Header Format Inconsistencies
- **Problem**: Common header issues identified:
  - Multi-line headers with line breaks
  - Inconsistent spacing and special characters
  - Mixed language terminology (German/English)
  - "nan:" prefixes in headers
  - Inconsistent naming conventions for similar fields
  - Varying header positions across years

- **Solution**: Header normalization implemented in three main scripts:
```python
# Common header cleaning functions across scripts
def clean_header(df):
    """Clean and format the dataframe headers."""
    df.columns = df.columns.str.replace('\n', ' ', regex=False)
    df.columns = df.columns.str.replace('\t', ' ', regex=False)
    df.columns = df.columns.str.strip()
    return df

# Header standardization with mappings
HEADER_MAPPINGS = {
    'nan: Hersteller\n': 'Hersteller',
    'Hersteller\n': 'Hersteller',
    'nan: Handelsname': 'Handelsname',
    # ... additional mappings
}
```

### 2.2 Data Type Standardization
- **Problem**: Data type issues identified:
  - NaN values in headers
  - Mixed numeric and text formats
  - Inconsistent handling of empty cells
  - Special characters in text fields

- **Solution**: Type handling code:
```python
def standardize_header(header):
    """Standardize header names using the mapping dictionary."""
    if pd.isna(header) or isinstance(header, (np.float64, float)):
        return ''
    header = str(header)
    if header.lower() == 'nan':
        return ''
    return HEADER_MAPPINGS.get(header, header)
```

### 2.3 Sheet Structure Validation
- **Problem**: Structure issues identified:
  - Varying number of columns across years
  - Different header positions (rows 7-9)
  - Inconsistent multi-line header combinations
  - Missing or extra columns

- **Solution**: Structure validation code:
```python
def determine_header(file_path, sheet_name):
    """Determine and combine headers from two potential header rows."""
    header_rows = pd.read_excel(file_path, 
                              sheet_name=sheet_name, 
                              skiprows=6, 
                              nrows=2)
    header_row1 = header_rows.iloc[0]
    header_row2 = header_rows.iloc[1]
    # Combine headers based on presence of values
    combined_headers = []
    for col1, col2 in zip(header_row1, header_row2):
        if pd.notna(col2):
            combined_headers.append(f"{col1}: {col2}")
        else:
            combined_headers.append(col1)
    return combined_headers
```

### 2.4 Data Quality Checks
- **Problem**: Data quality issues identified:
  - Inconsistent header naming across years
  - Missing required fields
  - Duplicate headers
  - Inconsistent formatting

- **Solution**: Quality validation code:
```python
def analyze_headers():
    """Analyze headers across all years and verify consistency."""
    header_info = {}
    all_standardized_headers = set()
    
    for year in YEARS_TO_PROCESS:
        # Process headers for each year
        combined_headers = determine_header(file_path, SHEET_NAME)
        standardized_headers = [standardize_header(h) for h in combined_headers]
        
        # Store and compare headers
        header_info[year] = {
            'original': combined_headers,
            'standardized': standardized_headers
        }
        all_standardized_headers.add(tuple(standardized_headers))
    
    # Check consistency
    return len(all_standardized_headers) == 1
```

### 2.5 Data Transformation Pipeline
- **Problem**: Need for consistent header processing across multiple files
- **Solution**: Pipeline implementation:
```python
def process_headers():
    """Process headers for all years and sheets."""
    # 1. Read headers from Excel files
    # 2. Clean and standardize headers
    # 3. Validate consistency
    # 4. Generate comparison report
    # 5. Save standardized headers
```

## 3. Usage Example
```python
# Define years to process
YEARS_TO_PROCESS = ['2020', '2021', '2022', '2023', '2024']

# Define sheet-specific parameters
SHEET_NAME = 'FZ 2.2'  # or 'FZ 2.4' or 'FZ 3.1'
BASE_PATH = 'kba_market_analysis/data_source/Bestand/...'

# Run header analysis
headers_consistent = analyze_headers()

# Check results
if headers_consistent:
    print("Headers are consistent across all years")
else:
    print("Header inconsistencies found - check the analysis file")
```

## 4. Best Practices
1. Always validate header consistency before processing data
2. Use standardized header mappings for each sheet type
3. Handle special characters and encodings carefully
4. Implement comprehensive error logging
5. Document all header transformations
6. Keep original headers intact and create new standardized versions
7. Use consistent naming conventions across all files
8. Generate detailed comparison reports for verification

## 5. Required Sections for Each Documentation
1. **Project Overview**
   - Clear description of the data source
   - Business context and objectives
   - Expected output format

2. **Data Inconsistencies**
   - Detailed list of known issues
   - Specific examples of problematic headers
   - Impact on downstream processes

3. **Technical Solutions**
   - Complete code examples
   - Step-by-step processing logic
   - Error handling approach

4. **Validation Rules**
   - Header format constraints
   - Required field specifications
   - Naming convention requirements

5. **Quality Metrics**
   - Header consistency measures
   - Standardization success rate
   - Error rate tracking

6. **Usage Guidelines**
   - Setup instructions
   - Configuration options
   - Common pitfalls
   - Troubleshooting tips

## 6. Documentation Standards
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
   - Include sample headers
   - Show expected outputs
   - Demonstrate error cases
   - Provide use cases

4. **Maintenance**
   - Update frequency
   - Change log
   - Version control
   - Review process 