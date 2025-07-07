import pandas as pd
from datetime import datetime, timedelta

def extract_clock_times(clock_in_out_time, clock_out_column):
    all_times = []
    original_times = []
    
    # Collect all times from Clock-in/out Time column
    if not pd.isna(clock_in_out_time) and clock_in_out_time != '':
        times = str(clock_in_out_time).split()
        for time_str in times:
            try:
                time_obj = datetime.strptime(time_str, '%H:%M')
                all_times.append(time_obj)
                original_times.append(time_str)
            except ValueError:
                continue
    
    # Collect time from Clock Out column
    if not pd.isna(clock_out_column) and clock_out_column != '':
        try:
            time_obj = datetime.strptime(str(clock_out_column), '%H:%M')
            all_times.append(time_obj)
            original_times.append(str(clock_out_column))
        except ValueError:
            pass
    
    if not all_times:
        return None, None
    
    # Add 9 hours to all times for comparison purposes only
    normalized_times = []
    for i, time_obj in enumerate(all_times):
        # Add 9 hours
        new_time = time_obj + timedelta(hours=9)
        
        # If it goes over 23:59, subtract 24 hours to bring it back in range
        if new_time.day > time_obj.day:
            new_time = new_time - timedelta(hours=24)
        
        normalized_times.append((new_time, original_times[i]))
    
    # Sort by normalized times
    normalized_times.sort(key=lambda x: x[0])
    
    # Get original times for first (check-in) and last (check-out)
    first_original = normalized_times[0][1]
    last_original = normalized_times[-1][1] if len(normalized_times) > 1 else None
    
    # If there's only one time, treat it as check-in
    if len(normalized_times) == 1:
        return first_original, None
    
    # Check if check-in and check-out are within 1 hour of each other
    if first_original and last_original:
        try:
            first_time = datetime.strptime(first_original, '%H:%M')
            last_time = datetime.strptime(last_original, '%H:%M')
            
            # Handle overnight case for time difference calculation
            if last_time < first_time:
                last_time += timedelta(days=1)
            
            time_diff = abs((last_time - first_time).total_seconds() / 3600)
            
            # If within 1 hour, apply the rule
            if time_diff <= 1:
                # Convert to hour for comparison
                first_hour = datetime.strptime(first_original, '%H:%M').time()
                
                # If time is between 02:00 and 18:00, keep only check-out
                if datetime.strptime('02:00', '%H:%M').time() <= first_hour <= datetime.strptime('18:00', '%H:%M').time():
                    return None, last_original
                # If time is outside 02:00-18:00 range (18:01-01:59), keep only check-in
                else:
                    return first_original, None
        except:
            pass
    
    return first_original, last_original

# Test cases
test_cases = [
    ("01:35", "04:50", "Maher's case"),
    ("20:07 20:07", "02:30", "Multiple times"),
    ("19:07", "", "Only check-in time"),
    ("", "04:15", "Only check-out time"),
    ("22:09 22:09 22:09 22:09", "22:09", "Many identical times"),
    ("01:30", "02:00", "Within 1hr, time outside 02:00-18:00 range (should keep check-in only)"),
    ("10:00", "10:30", "Within 1hr, time in 02:00-18:00 range (should keep check-out only)"),
    ("19:00", "19:30", "Within 1hr, time outside 02:00-18:00 range (should keep check-in only)"),
]

print("Testing new simplified logic:")
print("=" * 50)

for clock_in_out, clock_out, description in test_cases:
    result = extract_clock_times(clock_in_out, clock_out)
    print(f"{description}:")
    print(f"  Input: clock_in_out='{clock_in_out}', clock_out='{clock_out}'")
    print(f"  Result: check_in={result[0]}, check_out={result[1]}")
    print()