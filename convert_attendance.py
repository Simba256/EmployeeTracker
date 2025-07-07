import pandas as pd

xlsx_file = "Attendance Sheet June 2025 (1).xlsx"
csv_file = "Attendance Sheet June 2025 (1).csv"

df = pd.read_excel(xlsx_file)
df.to_csv(csv_file, index=False)

print(f"Converted {xlsx_file} to {csv_file}")