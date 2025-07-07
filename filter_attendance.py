import pandas as pd

csv_file = "Attendance_Cleaned_with_Times.csv"
filtered_file = "Attendance_Filtered.csv"

df = pd.read_csv(csv_file)

# Remove rows where both Clock In and Clock Out are empty/NaN
df_filtered = df.dropna(subset=['Clock In', 'Clock Out'], how='all')

df_filtered.to_csv(filtered_file, index=False)

print(f"Original rows: {len(df)}")
print(f"Filtered rows: {len(df_filtered)}")
print(f"Removed rows: {len(df) - len(df_filtered)}")
print(f"Filtered data saved to {filtered_file}")