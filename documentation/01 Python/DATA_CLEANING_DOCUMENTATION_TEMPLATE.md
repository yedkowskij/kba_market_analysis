# Data Cleaning Documentation Template

## 1. Project Overview
**Business Problem and Context:**
- Brief description of the data source and format
- Key challenges and objectives
- Expected output format and use cases
- Any specific business requirements or constraints

## 2. Data Inconsistencies and Solutions

### 2.1 Header Format Inconsistencies
- **Problem**: Document common header issues:
  - Line breaks within cells
  - Inconsistent spacing
  - Mixed language terminology
  - Special characters
  - Other specific issues

- **Solution**: Include code for header normalization:
```python
def _normalize_header(header):
    """Normalize header text by removing special characters and standardizing format."""
    # Implementation details
    pass

def _process_headers(df):
    """Process all column headers in a dataframe."""
    # Implementation details
    pass
```

### 2.2 Data Type Standardization
- **Problem**: List data type issues:
  - Mixed numeric formats
  - Inconsistent date formats
  - Special characters in text fields
  - Hidden formulas
  - Other specific issues

- **Solution**: Include data type handling code:
```python
def _standardize_numeric(value):
    """Convert various numeric formats to standard format."""
    # Implementation details
    pass

def _standardize_date(value):
    """Convert various date formats to standard format."""
    # Implementation details
    pass

def _clean_text(value):
    """Standardize text fields and handle special characters."""
    # Implementation details
    pass
```

### 2.3 Sheet Structure Validation
- **Problem**: Document structure issues:
  - Varying number of columns
  - Different header positions
  - Missing or extra rows
  - Inconsistent data blocks
  - Other specific issues

- **Solution**: Include structure validation code:
```python
def _validate_sheet_structure(df, expected_columns):
    """Validate sheet structure against expected format."""
    # Implementation details
    pass

def _fix_sheet_structure(df, expected_columns):
    """Fix common sheet structure issues."""
    # Implementation details
    pass
```

### 2.4 Data Quality Checks
- **Problem**: List data quality issues:
  - Outliers in numeric fields
  - Inconsistent categorical values
  - Missing required fields
  - Invalid date ranges
  - Other specific issues

- **Solution**: Include data quality validation code:
```python
def _validate_numeric_range(df, column, min_val=None, max_val=None):
    """Validate numeric values are within expected range."""
    # Implementation details
    pass

def _validate_categorical_values(df, column, allowed_values):
    """Validate categorical values are in allowed set."""
    # Implementation details
    pass

def _validate_date_range(df, date_column, min_date=None, max_date=None):
    """Validate dates are within expected range."""
    # Implementation details
    pass
```

### 2.5 Data Transformation Pipeline
- **Problem**: Describe the need for consistent processing
- **Solution**: Include pipeline implementation:
```python
def process_sheet(file_path, sheet_name, expected_columns):
    """Process a single sheet with all cleaning steps."""
    # Implementation details
    pass
```

## 3. Usage Example
```python
# Define expected structure
expected_columns = [
    # List of expected column names
]

# Define validation rules
numeric_ranges = {
    # Column name: (min_value, max_value)
}

categorical_values = {
    # Column name: [allowed_values]
}

date_ranges = {
    # Column name: (min_date, max_date)
}

# Process a file
file_path = 'path/to/file.xlsx'
sheet_name = 'Sheet Name'

df, issues = process_sheet(
    file_path,
    sheet_name,
    expected_columns
)

# Export cleaned data
if not issues:
    df.to_csv('cleaned_data.csv', index=False)
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

## 5. Required Sections for Each Documentation
1. **Project Overview**
   - Clear description of the data source
   - Business context and objectives
   - Expected output format

2. **Data Inconsistencies**
   - Detailed list of known issues
   - Specific examples of problematic data
   - Impact on downstream processes

3. **Technical Solutions**
   - Complete code examples
   - Step-by-step processing logic
   - Error handling approach

4. **Validation Rules**
   - Data type constraints
   - Value range restrictions
   - Required field specifications
   - Format requirements

5. **Quality Metrics**
   - Data completeness measures
   - Accuracy indicators
   - Consistency checks
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
   - Include sample data
   - Show expected outputs
   - Demonstrate error cases
   - Provide use cases

4. **Maintenance**
   - Update frequency
   - Change log
   - Version control
   - Review process 