import pandas as pd
from datetime import datetime, timedelta

def extract_clock_times(clock_in_out_time, clock_out_column):
    clock_in_times = []
    clock_out_times = []
    
    # Process Clock Out column first
    if not pd.isna(clock_out_column) and clock_out_column != '':
        try:
            time_obj = datetime.strptime(str(clock_out_column), '%H:%M')
            clock_out_times.append(str(clock_out_column))
        except ValueError:
            pass
    
    # Process Clock-in/out Time column
    if not pd.isna(clock_in_out_time) and clock_in_out_time != '':
        times = str(clock_in_out_time).split()
        for time_str in times:
            try:
                time_obj = datetime.strptime(time_str, '%H:%M')
                hour = time_obj.hour
                
                # If there's already a checkout time from Clock Out column,
                # and this time is early morning (0-6), treat it as check-in
                if clock_out_times and 0 <= hour <= 6:
                    clock_in_times.append(time_str)
                elif hour < 12:
                    clock_out_times.append(time_str)
                else:
                    clock_in_times.append(time_str)
            except ValueError:
                continue
    
    earliest_clock_in = min(clock_in_times) if clock_in_times else None
    latest_clock_out = max(clock_out_times) if clock_out_times else None
    
    # Check if clock-in and clock-out are within 1 hour of each other
    if earliest_clock_in and latest_clock_out:
        try:
            checkin_time = datetime.strptime(earliest_clock_in, '%H:%M')
            checkout_time = datetime.strptime(latest_clock_out, '%H:%M')
            
            # Handle overnight case (checkout next day)
            if checkout_time < checkin_time:
                checkout_time += timedelta(days=1)
            
            time_diff = abs((checkout_time - checkin_time).total_seconds() / 3600)
            
            # If within 1 hour, keep only one based on the rule
            if time_diff <= 1:
                checkin_hour = checkin_time.hour
                checkout_hour = datetime.strptime(latest_clock_out, '%H:%M').hour
                
                # If both are < 12:00, keep only check-out
                if checkin_hour < 12 and checkout_hour < 12:
                    earliest_clock_in = None
                # If both are >= 12:00, keep only check-in
                elif checkin_hour >= 12 and checkout_hour >= 12:
                    latest_clock_out = None
        except:
            pass
    
    return earliest_clock_in, latest_clock_out

csv_file = "Attendance Sheet June 2025 (1).csv"
cleaned_file = "Attendance_Cleaned_with_Times.csv"

df = pd.read_csv(csv_file)

df[['Extracted_Clock_In', 'Extracted_Clock_Out']] = df.apply(
    lambda row: pd.Series(extract_clock_times(row['Clock-in/out Time'], row['Clock Out'])), axis=1
)

columns_to_keep = ['Emp No.', 'AC-No.', 'Name', 'Date', 'Extracted_Clock_In', 'Extracted_Clock_Out']
df_cleaned = df[columns_to_keep]

df_cleaned.columns = ['Emp No.', 'AC-No.', 'Name', 'Date', 'Clock In', 'Clock Out']

df_cleaned.to_csv(cleaned_file, index=False)

print(f"Cleaned data with extracted times saved to {cleaned_file}")
print(f"Shape: {df_cleaned.shape}")
print("\nSample of extracted times:")
print(df_cleaned[df_cleaned['Clock In'].notna()].head(10))