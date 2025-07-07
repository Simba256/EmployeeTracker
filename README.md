# Attendance Data Processor

A Streamlit web application for processing and analyzing employee attendance data from Excel files.

## Features

- **Excel to CSV Conversion**: Upload Excel attendance files and get cleaned CSV output
- **Smart Time Processing**: Handles complex attendance data with multiple check-in/out times
- **Employee Summary**: Generates comprehensive statistics for each employee including:
  - Total check-ins and check-outs
  - Absences calculation
  - Late check-ins and early checkouts
  - Overtime and undertime calculations
  - Net overtime analysis

## How It Works

1. **Data Collection**: Extracts all times from both 'Clock-in/out Time' and 'Clock Out' columns
2. **Time Normalization**: Adds 9 hours to each time for comparison purposes (to handle night shifts)
3. **Chronological Sorting**: Sorts all times to determine check-in (first) and check-out (last)
4. **Duplicate Handling**: If check-in and check-out are within 1 hour:
   - Times ≤ 11:00: Keep only check-in
   - Times > 11:00: Keep only check-out
5. **Original Time Preservation**: Returns original (non-normalized) times in output

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd attendance-processor
```

2. Install required packages:
```bash
pip install streamlit pandas openpyxl
```

## Usage

1. Run the Streamlit app:
```bash
streamlit run attendance_app.py
```

2. Open your web browser and go to the displayed URL (usually `http://localhost:8501`)

3. Upload your Excel attendance file

4. Download the processed CSV files:
   - **Cleaned Attendance Data**: Individual attendance records
   - **Employee Summary**: Statistical analysis per employee

## File Structure

- `attendance_app.py` - Main Streamlit application
- `extract_clock_times.py` - Standalone script for time extraction
- `test_new_logic.py` - Test script for validation
- Sample processing scripts for development

## Expected Excel Format

Your Excel file should contain these columns:
- **Emp No.**: Employee number
- **AC-No.**: Access control number  
- **Name**: Employee name
- **Date**: Date of attendance
- **Clock-in/out Time**: Space-separated time entries (e.g., "19:07 04:15")
- **Clock Out**: Single clock-out time (optional)

## Example

Input times: `01:35` and `04:50`
- After normalization: `10:35` and `13:50` 
- Chronological order: `01:35` (check-in), `04:50` (check-out)
- Output: Original times preserved

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is open source and available under the MIT License.