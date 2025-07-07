import pandas as pd

csv_file = "Attendance Sheet June 2025 (1).csv"
cleaned_file = "Attendance_Cleaned.csv"

df = pd.read_csv(csv_file)

columns_to_keep = ['Emp No.', 'AC-No.', 'Name', 'Date', 'Clock In', 'Clock Out']
df_cleaned = df[columns_to_keep]

df_cleaned.to_csv(cleaned_file, index=False)

print(f"Cleaned data saved to {cleaned_file}")
print(f"Original columns: {len(df.columns)}")
print(f"Cleaned columns: {len(df_cleaned.columns)}")
print(f"Shape: {df_cleaned.shape}")