# FZ8 2020-2022 Data Cleaning Documentation

## 1. Project Overview
**Business Problem and Context:**
- The project involves processing the legacy FZ-8 workbook (2020-2022) containing German vehicle registration data
- Unlike the 2023-2025 data (monthly Excel files), this data was delivered as a single "PDF-layout" Excel file
- The goal is to convert each sheet into a raw CSV format for later merging with the 2023-2025 data
- Key challenge: Maintaining data integrity while converting from PDF-style layout to CSV format

## 2. Solving the Simple Case
### Business Summary
The initial challenge was to process the legacy FZ-8 workbook containing vehicle registration data from 2020-2022, focusing on converting each sheet into a standardized CSV format.

### Technical Solution
- Created a simple conversion process:
```python
# Extract sheet names and convert to CSV
for sheet in wb.sheetnames:
    df = pd.read_excel(XLSX, sheet_name=sheet, dtype=str, header=None)
    
    # Sheet name looks like "8.2 DONE" → take "8.2" part
    number = sheet.split()[0]
    csv_name = f"fz_8.{number.split('.')[1]}_2020-2022_raw.csv"
    
    out_path = DATA_DIR / "csv" / csv_name
    df.to_csv(out_path, index=False, header=False)
```

## 3. Scaling Up
### Business Summary
The solution was designed to handle multiple sheets within the workbook, ensuring consistent output format for each sheet while maintaining data integrity.

### Technical Solution
- Implemented a systematic sheet processing approach:
  - Process all sheets in the workbook
  - Maintain consistent naming convention
  - Store all data as text to prevent type coercion issues
  - Remove headers to match downstream processing requirements

## 4. Dealing with Data Inconsistencies
### Business Summary
The legacy FZ-8 workbook presented several data consistency challenges that required careful handling to ensure data quality and reliability.

### Technical Solution

#### 4.1 PDF-Style Layout
- **Problem**: The workbook was in PDF-style layout:
  - Complex formatting
  - Merged cells
  - Non-standard headers
  - Mixed data types

- **Solution**: Implemented raw data extraction:
```python
# Read Excel without headers and as string type
df = pd.read_excel(XLSX, sheet_name=sheet, dtype=str, header=None)
```

#### 4.2 Sheet Naming Conventions
- **Problem**: Sheet names contained additional information:
  - Format: "8.2 DONE", "8.3 DONE", etc.
  - Needed to extract just the sheet number

- **Solution**: Implemented name parsing:
```python
# Extract sheet number from name
number = sheet.split()[0]  # "8.2 DONE" → "8.2"
csv_name = f"fz_8.{number.split('.')[1]}_2020-2022_raw.csv"
```

#### 4.3 Data Type Consistency
- **Problem**: Mixed data types in the workbook:
  - Numbers
  - Text
  - Dates
  - Special characters

- **Solution**: Standardized all data as text:
```python
# Force string type for all cells
df = pd.read_excel(XLSX, sheet_name=sheet, dtype=str, header=None)
```

## 5. Making the Solution Flexible and Maintainable
### Business Summary
Created a simple, maintainable solution that preserves raw data for downstream processing while ensuring consistency with the 2023-2025 data format.

### Technical Solution
- Used pandas for reliable Excel reading
- Implemented consistent file naming
- Stored all data as text to prevent type coercion
- Removed headers to match downstream processing requirements

## 6. Reflections: Learning, AI Collaboration, and Business Value
- **Learning**: Developed understanding of handling legacy data formats
- **AI Collaboration**: Used AI to help structure the code and implement best practices
- **Business Value**: Created standardized raw data format for historical data
- **Professional Growth**: Improved skills in data conversion and standardization

## 7. Appendix: Key Code Snippets and AI Conversations
### Main Processing Loop
```python
# Process each sheet in the workbook
for sheet in wb.sheetnames:
    df = pd.read_excel(XLSX, sheet_name=sheet, dtype=str, header=None)
    
    # Extract sheet number and create output filename
    number = sheet.split()[0]
    csv_name = f"fz_8.{number.split('.')[1]}_2020-2022_raw.csv"
    
    # Save as CSV without headers
    out_path = DATA_DIR / "csv" / csv_name
    df.to_csv(out_path, index=False, header=False)
```

### File Structure
```python
# Paths setup
DATA_DIR = Path("../data/raw/fz8")
XLSX     = DATA_DIR / "_fz8_pdf_2020-2022.xlsx"
``` 