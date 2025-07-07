import pandas as pd
from datetime import datetime, timedelta

def extract_clock_times(clock_in_out_time, clock_out_column):
    clock_in_times = []
    clock_out_times = []
    
    print(f"Processing: clock_in_out_time='{clock_in_out_time}', clock_out_column='{clock_out_column}'")
    
    # Process Clock Out column first
    if not pd.isna(clock_out_column) and clock_out_column != '':
        try:
            time_obj = datetime.strptime(str(clock_out_column), '%H:%M')
            clock_out_times.append(str(clock_out_column))
            print(f"  Added {clock_out_column} to clock_out_times from Clock Out column")
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
                    print(f"  Added {time_str} to clock_in_times (early morning with existing checkout)")
                elif hour < 12:
                    clock_out_times.append(time_str)
                    print(f"  Added {time_str} to clock_out_times (< 12)")
                else:
                    clock_in_times.append(time_str)
                    print(f"  Added {time_str} to clock_in_times (>= 12)")
            except ValueError:
                continue
    
    print(f"  clock_in_times: {clock_in_times}")
    print(f"  clock_out_times: {clock_out_times}")
    
    earliest_clock_in = min(clock_in_times) if clock_in_times else None
    latest_clock_out = max(clock_out_times) if clock_out_times else None
    
    print(f"  Result: clock_in={earliest_clock_in}, clock_out={latest_clock_out}")
    
    return earliest_clock_in, latest_clock_out

# Test the specific case
result = extract_clock_times("01:35", "04:50")
print(f"Final result: {result}")