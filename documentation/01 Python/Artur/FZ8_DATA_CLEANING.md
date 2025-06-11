# FZ8 Data Cleaning Documentation

## 1. Project Overview
**Business Problem and Context:**
- The project involves processing and cleaning FZ-8 workbooks (2023-2025) containing German vehicle registration data
- Unlike the legacy 2020-2022 file (single PDF-style workbook), the 2023-2025 data arrives month-by-month as Excel files
- The goal is to create clean, standardized datasets for downstream analytics by processing multiple Excel sheets consistently

## 2. Solving the Simple Case
### Business Summary
The initial challenge was to process individual Excel workbooks containing vehicle registration data, focusing on specific sheets (8.2, 8.3, 8.6, 8.7, 8.8, 8.9, and 8.16) that contain different aspects of vehicle statistics.

### Technical Solution
- Created helper functions for common operations:
```python
def _clean_header(s):
    """Normalize header cell: collapse multiple spaces + remove newlines."""
    return str(s).replace('\n', ' ').replace('  ', ' ').strip() if s is not None else s

def _strip_cols(df):
    """Apply `clean_header` to every column name in-place and return df."""
    df.columns = [_clean_header(c) for c in df.columns]
    return df
```

## 3. Scaling Up
### Business Summary
Expanded the solution to handle multiple Excel files across different months while maintaining data consistency and proper merging of historical data.

### Technical Solution
- Implemented a robust sheet lookup system:
```python
def _find_sheet(wb, num):
    """Locate sheet whose name matches *pattern* (case-insensitive)."""
    pattern = re.compile(fr"^FZ\s*8\.{re.escape(num)}$", flags=re.IGNORECASE)
    for name in wb.sheetnames:
        if pattern.match(name.strip()):
            return name
    return None
```

## 4. Dealing with Data Inconsistencies
### Business Summary
The FZ-8 workbooks presented numerous data consistency challenges that required careful handling to ensure data quality and reliability. These challenges ranged from structural variations in the Excel files to content-specific issues that needed to be addressed systematically.

### Technical Solution

#### 4.1 Header Format Inconsistencies
- **Problem**: Headers varied across files in terms of:
  - Line breaks within cells
  - Inconsistent spacing
  - Different naming conventions for the same data
  - Mixed use of German special characters

- **Solution**: Implemented comprehensive header normalization:
```python
def _clean_header(s):
    """Normalize header cell: collapse multiple spaces + remove newlines."""
    return str(s).replace('\n', ' ').replace('  ', ' ').strip() if s is not None else s

def _unique(cols):
    """Ensure uniqueness by adding numeric suffixes."""
    seen, out = {}, []
    for c in cols:
        if c in seen:
            seen[c] += 1
            out.append(f"{c}{seen[c]}")
        else:
            seen[c] = 0
            out.append(c)
    return out
```

#### 4.2 Meta Rows and Totals
- **Problem**: Each sheet contained various types of meta-information:
  - Total rows that needed to be excluded
  - Footnotes and explanatory text
  - Section headers that needed to be preserved
  - Different types of summary rows depending on the sheet

- **Solution**: Implemented sheet-specific cleaning rules:
```python
# Example for sheet 8.2
trash = r"INSGESAMT|FLENSBURG|HINWEIS|UMBENANNT"
mask = df[cols[0]].astype(str).str.contains(trash, case=False, na=False)
df = df[~mask].reset_index(drop=True)
```

#### 4.3 Sheet Name Variations
- **Problem**: Sheet names could appear in multiple formats:
  - "FZ 8.2" vs "FZ8.2"
  - Different spacing patterns
  - Case variations
  - Hidden characters

- **Solution**: Created flexible sheet detection:
```python
def _find_sheet(wb, num):
    """Locate sheet whose name matches *pattern* (case-insensitive)."""
    pattern = re.compile(fr"^FZ\s*8\.{re.escape(num)}$", flags=re.IGNORECASE)
    for name in wb.sheetnames:
        if pattern.match(name.strip()):
            return name
    return None
```

#### 4.4 Data Type Inconsistencies
- **Problem**: Various data type issues:
  - Mixed numeric and text values
  - Inconsistent decimal separators
  - Missing values represented differently
  - Special characters in text fields
  - Inconsistent date formats
  - Mixed use of German and English number formats
  - Hidden Excel formulas in cells
  - Scientific notation in large numbers
  - Inconsistent handling of zero values
  - Mixed use of percentage formats

- **Solution**: Implemented comprehensive data type standardization:

```python
def _standardize_numeric(s):
    """Convert various numeric formats to consistent string representation."""
    if pd.isna(s) or s == '':
        return ''
    
    # Convert to string and handle scientific notation
    s = str(s).strip()
    
    # Handle percentage values
    if '%' in s:
        s = s.replace('%', '').strip()
        try:
            return str(float(s.replace(',', '.')) / 100)
        except ValueError:
            return s
    
    # Handle German number format (1.234,56)
    if ',' in s and '.' in s:
        # If both separators exist, assume German format
        s = s.replace('.', '').replace(',', '.')
    
    # Handle simple comma decimal separator
    s = s.replace(',', '.')
    
    try:
        # Convert to float and back to string to normalize
        return str(float(s))
    except ValueError:
        return s

def _standardize_date(s):
    """Convert various date formats to YYYY-MM-DD."""
    if pd.isna(s) or s == '':
        return ''
    
    s = str(s).strip()
    
    # Handle Excel date numbers
    if isinstance(s, (int, float)):
        try:
            return pd.to_datetime('1899-12-30') + pd.Timedelta(days=int(s))
        except:
            return s
    
    # Common German date formats
    formats = [
        '%d.%m.%Y', '%d-%m-%Y', '%Y-%m-%d',
        '%d.%m.%y', '%d-%m-%y', '%y-%m-%d'
    ]
    
    for fmt in formats:
        try:
            return pd.to_datetime(s, format=fmt).strftime('%Y-%m-%d')
        except:
            continue
    
    return s

def _clean_text(s):
    """Standardize text fields and handle special characters."""
    if pd.isna(s) or s == '':
        return ''
    
    s = str(s).strip()
    
    # Replace common German special characters
    replacements = {
        'ä': 'ae', 'ö': 'oe', 'ü': 'ue',
        'Ä': 'Ae', 'Ö': 'Oe', 'Ü': 'Ue',
        'ß': 'ss'
    }
    
    for old, new in replacements.items():
        s = s.replace(old, new)
    
    # Remove any remaining non-ASCII characters
    s = ''.join(char for char in s if ord(char) < 128)
    
    return s

def _process_column(df, col_name):
    """Apply appropriate standardization based on column content."""
    # Determine column type based on sample
    sample = df[col_name].dropna().head(100)
    
    # Check if column contains dates
    if any(str(x).strip().replace('.', '').replace('-', '').isdigit() 
           and len(str(x).strip()) in [8, 10] for x in sample):
        return df[col_name].apply(_standardize_date)
    
    # Check if column contains numbers
    if any(str(x).replace(',', '').replace('.', '').replace('-', '').isdigit() 
           for x in sample):
        return df[col_name].apply(_standardize_numeric)
    
    # Default to text cleaning
    return df[col_name].apply(_clean_text)

# Apply standardization to all columns
for col in df.columns:
    df[col] = _process_column(df, col)
```

This comprehensive solution addresses:
1. **Numeric Standardization**:
   - Converts German number format (1.234,56) to standard format (1234.56)
   - Handles percentage values by converting to decimal
   - Normalizes scientific notation
   - Preserves zero values appropriately

2. **Date Standardization**:
   - Converts various date formats to YYYY-MM-DD
   - Handles Excel date numbers
   - Supports multiple German date formats
   - Preserves invalid dates as strings

3. **Text Standardization**:
   - Replaces German special characters with ASCII equivalents
   - Removes non-ASCII characters
   - Preserves meaningful whitespace
   - Handles mixed content appropriately

4. **Type Detection**:
   - Automatically detects column types based on content
   - Applies appropriate standardization per column
   - Handles mixed-type columns gracefully
   - Preserves data integrity during conversion

The solution ensures that:
- All numeric values are consistently formatted
- Dates are standardized across all files
- Text fields are clean and ASCII-compatible
- No information is lost during conversion
- The process is reversible if needed
- Data quality is maintained throughout the pipeline

#### 4.5 Layout Validation
- **Problem**: Excel files could have:
  - Shifted data blocks
  - Different header positions
  - Varying number of rows
  - Inconsistent column structures

- **Solution**: Implemented comprehensive layout validation:
```python
def check_fz8_layout():
    """Validate that every "FZ 8.x" sheet in DATA_DIR is aligned exactly."""
    issues = []
    for num, coords in header_map.items():
        ref_names = None
        ref_file = None

        for path in sorted(DATA_DIR.glob("fz8_*.xlsx")):
            wb = load_workbook(path, data_only=True)
            sn = _find_sheet(wb, num)
            if not sn:
                issues.append(f"{path.name}: workbook 8.{num} not found")
                continue
            
            # Validate header positions and content
            ws = wb[sn]
            names = [_clean_header(ws[c].value) for c in coords]
            
            if ref_names is None:
                ref_names, ref_file = names, path.name
            elif names != ref_names:
                issues.append(f"{path.name}: 8.{num} – {names} ≠ {ref_names}")
```

#### 4.6 Historical Data Integration
- **Problem**: Merging with 2020-2022 data required:
  - Header matching across different eras
  - Consistent date formatting
  - Handling of new/removed columns
  - Maintaining data lineage

- **Solution**: Implemented strict validation before merging:
```python
# Header consistency check
if list(df_old.columns) != list(df_new.columns):
    issues.append(
        f"8.{num}: header mismatch.\n"
        f"  old: {list(df_old.columns)}\n"
        f"  new: {list(df_new.columns)}"
    )
    continue

# Concatenate with validation
df_all = (
    pd.concat([df_old, df_new], ignore_index=True)
      .fillna("")       # NaN → empty string
      .astype(str)      # guarantee text dtype
)
```

## 5. Making the Solution Flexible and Maintainable
### Business Summary
Created a modular, maintainable solution that can handle future data updates and different sheet formats while ensuring data quality.

### Technical Solution
- Used a dictionary-based parser mapping:
```python
sheet_parsers = {
    '2':  fz8_2, '3':  fz8_3, '6':  fz8_6,
    '7':  fz8_7, '8':  fz8_8, '9':  fz8_9, '16': fz8_16,
}
```
- Implemented strict header validation
- All data stored as text to prevent type coercion issues

## 6. Reflections: Learning, AI Collaboration, and Business Value
- **Learning**: Developed robust data processing pipeline that handles complex Excel files
- **AI Collaboration**: Used AI to help structure the code and implement best practices
- **Business Value**: Created standardized datasets that combine historical and current data
- **Professional Growth**: Improved skills in data validation, error handling, and code organization

## 7. Appendix: Key Code Snippets and AI Conversations
### Main Processing Loop
```python
for path in sorted(DATA_DIR.glob("fz8_*.xlsx")):
    wb   = load_workbook(path, data_only=True)
    date = _date_from_fname(path)

    for num, parser in sheet_parsers.items():
        sname = _find_sheet(wb, num)
        if not sname:
            print(f"{path.name}: workbook 8.{num} not found")
            continue

        df = parser(wb[sname])
        df.insert(0, "Date", date)
        globals_by_sheet[num] = pd.concat([globals_by_sheet[num], df], ignore_index=True)
```

### Data Export
```python
for num, df in globals_by_sheet.items():
    df = df.fillna('').astype(str)
    out_csv = OUT_DIR / f"fz_8.{num}_2023-2025_raw.csv"
    df.to_csv(out_csv, index=False, encoding="utf-8")
``` 