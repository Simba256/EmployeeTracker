import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io

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
                
                # If time <= 11:00, keep only check-in
                if first_hour <= datetime.strptime('11:00', '%H:%M').time():
                    return first_original, None
                # If time > 11:00, keep only check-out
                else:
                    return None, last_original
        except:
            pass
    
    return first_original, last_original

def calculate_time_difference(start_time, end_time):
    """Calculate time difference in hours between two time strings"""
    if pd.isna(start_time) or pd.isna(end_time):
        return 0
    
    try:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        
        # Handle overnight shifts
        if end < start:
            end += timedelta(days=1)
        
        diff = end - start
        return diff.total_seconds() / 3600  # Convert to hours
    except:
        return 0

def generate_employee_summary(df):
    """Generate employee summary with attendance statistics"""
    
    # Extract month from date
    df['Date'] = pd.to_datetime(df['Date'])
    df['Month'] = df['Date'].dt.strftime('%b')
    
    # Calculate total working days (days when any employee checked in)
    total_working_days = len(df[df['Clock In'].notna()]['Date'].dt.date.unique())
    
    summary_data = []
    
    for employee in df.groupby(['Emp No.', 'AC-No.', 'Name']):
        emp_data = employee[1]
        
        # Basic info
        emp_no = emp_data['Emp No.'].iloc[0]
        ac_no = emp_data['AC-No.'].iloc[0]
        name = emp_data['Name'].iloc[0]
        month = emp_data['Month'].iloc[0]
        
        # Count check-ins and check-outs
        total_checkins = emp_data['Clock In'].notna().sum()
        total_checkouts = emp_data['Clock Out'].notna().sum()
        
        # Calculate employee attendance days
        employee_checkin_days = len(emp_data[emp_data['Clock In'].notna()]['Date'].dt.date.unique())
        employee_checkout_days = len(emp_data[emp_data['Clock Out'].notna()]['Date'].dt.date.unique())
        employee_attendance_days = max(employee_checkin_days, employee_checkout_days)
        
        # Calculate absences
        absences = total_working_days - employee_attendance_days
        
        # Late check-ins (after 19:00)
        late_checkins = 0
        for _, row in emp_data.iterrows():
            if pd.notna(row['Clock In']):
                checkin_time = datetime.strptime(row['Clock In'], '%H:%M').time()
                if checkin_time > datetime.strptime('19:00', '%H:%M').time():
                    late_checkins += 1
        
        # Early checkouts (before 04:00)
        early_checkouts = 0
        for _, row in emp_data.iterrows():
            if pd.notna(row['Clock Out']):
                checkout_time = datetime.strptime(row['Clock Out'], '%H:%M').time()
                if checkout_time < datetime.strptime('04:00', '%H:%M').time():
                    early_checkouts += 1
        
        # Calculate undertime and overtime
        total_undertime = 0
        total_overtime = 0
        
        for _, row in emp_data.iterrows():
            if pd.notna(row['Clock In']) and pd.notna(row['Clock Out']):
                checkin_time = datetime.strptime(row['Clock In'], '%H:%M').time()
                checkout_time = datetime.strptime(row['Clock Out'], '%H:%M').time()
                
                # Undertime calculation
                # Late check-in after 19:00
                if checkin_time > datetime.strptime('19:00', '%H:%M').time():
                    late_minutes = (datetime.combine(datetime.today(), checkin_time) - 
                                  datetime.combine(datetime.today(), datetime.strptime('19:00', '%H:%M').time())).total_seconds() / 60
                    total_undertime += late_minutes / 60
                
                # Early checkout before 04:00
                if checkout_time < datetime.strptime('04:00', '%H:%M').time():
                    early_minutes = (datetime.combine(datetime.today(), datetime.strptime('04:00', '%H:%M').time()) - 
                                   datetime.combine(datetime.today(), checkout_time)).total_seconds() / 60
                    total_undertime += early_minutes / 60
                
                # Overtime calculation
                # Early check-in before 19:00
                if checkin_time < datetime.strptime('19:00', '%H:%M').time():
                    early_minutes = (datetime.combine(datetime.today(), datetime.strptime('19:00', '%H:%M').time()) - 
                                   datetime.combine(datetime.today(), checkin_time)).total_seconds() / 60
                    total_overtime += early_minutes / 60
                
                # Late checkout after 04:00
                if checkout_time > datetime.strptime('04:00', '%H:%M').time():
                    late_minutes = (datetime.combine(datetime.today(), checkout_time) - 
                                  datetime.combine(datetime.today(), datetime.strptime('04:00', '%H:%M').time())).total_seconds() / 60
                    total_overtime += late_minutes / 60
        
        # Net overtime
        net_overtime = total_overtime - total_undertime
        
        summary_data.append({
            'Emp No.': emp_no,
            'AC-No.': ac_no,
            'Name': name,
            'Month': month,
            'Total Check-ins': total_checkins,
            'Total Check-outs': total_checkouts,
            'Absences': absences,
            'Late Check-ins': late_checkins,
            'Early Checkouts': early_checkouts,
            'Undertime (hrs)': round(total_undertime, 2),
            'Overtime (hrs)': round(total_overtime, 2),
            'Net Overtime (hrs)': round(net_overtime, 2)
        })
    
    return pd.DataFrame(summary_data)

def process_attendance_file(uploaded_file):
    try:
        # Read Excel file
        df = pd.read_excel(uploaded_file)
        
        # Extract clock times
        df[['Extracted_Clock_In', 'Extracted_Clock_Out']] = df.apply(
            lambda row: pd.Series(extract_clock_times(row['Clock-in/out Time'], row['Clock Out'])), axis=1
        )
        
        # Select required columns
        columns_to_keep = ['Emp No.', 'AC-No.', 'Name', 'Date', 'Extracted_Clock_In', 'Extracted_Clock_Out']
        df_cleaned = df[columns_to_keep].copy()
        
        # Rename columns
        df_cleaned.columns = ['Emp No.', 'AC-No.', 'Name', 'Date', 'Clock In', 'Clock Out']
        
        # Filter out rows with no clock in or clock out
        df_filtered = df_cleaned.dropna(subset=['Clock In', 'Clock Out'], how='all')
        
        # Generate employee summary
        df_summary = generate_employee_summary(df_filtered)
        
        return df_filtered, df_summary, None
        
    except Exception as e:
        return None, None, str(e)

def main():
    st.set_page_config(page_title="Attendance Data Processor", page_icon="📊", layout="wide")
    
    st.title("📊 Attendance Data Processor")
    st.markdown("Upload an Excel attendance file and get a cleaned CSV with proper clock-in/out times")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Choose an Excel file", 
        type=['xlsx', 'xls'],
        help="Upload your attendance Excel file"
    )
    
    if uploaded_file is not None:
        st.success(f"File uploaded: {uploaded_file.name}")
        
        # Process the file
        with st.spinner("Processing attendance data..."):
            df_processed, df_summary, error = process_attendance_file(uploaded_file)
        
        if error:
            st.error(f"Error processing file: {error}")
        else:
            st.success("✅ File processed successfully!")
            
            # Display statistics
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Records", len(df_processed))
            with col2:
                records_with_clock_in = df_processed['Clock In'].notna().sum()
                st.metric("Records with Clock In", records_with_clock_in)
            with col3:
                records_with_clock_out = df_processed['Clock Out'].notna().sum()
                st.metric("Records with Clock Out", records_with_clock_out)
            with col4:
                # Get total working days from summary (it's the same for all employees)
                total_working_days = df_summary['Total Working Days'].iloc[0] if not df_summary.empty else 0
                st.metric("Total Working Days", total_working_days)
            
            # Create tabs for different views
            tab1, tab2 = st.tabs(["📋 Attendance Data", "📊 Employee Summary"])
            
            with tab1:
                st.subheader("📋 Attendance Data Preview")
                st.dataframe(df_processed.head(10), use_container_width=True)
                
                # Download button for attendance data
                csv_buffer = io.StringIO()
                df_processed.to_csv(csv_buffer, index=False)
                csv_data = csv_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Cleaned CSV",
                    data=csv_data,
                    file_name="attendance_cleaned.csv",
                    mime="text/csv",
                    type="primary"
                )
            
            with tab2:
                st.subheader("📊 Employee Summary")
                st.dataframe(df_summary, use_container_width=True)
                
                # Download button for summary
                summary_buffer = io.StringIO()
                df_summary.to_csv(summary_buffer, index=False)
                summary_data = summary_buffer.getvalue()
                
                st.download_button(
                    label="📥 Download Summary CSV",
                    data=summary_data,
                    file_name="employee_summary.csv",
                    mime="text/csv",
                    type="secondary"
                )
            
            # Show processing info
            with st.expander("ℹ️ Processing Information"):
                st.markdown("""
                **What this app does:**
                1. Reads your Excel attendance file
                2. Collects all times from both 'Clock-in/out Time' and 'Clock Out' columns
                3. Adds 9 hours to each time for comparison purposes only (to determine chronological order)
                4. Sorts all times chronologically using the normalized times
                5. Returns the original (non-normalized) times in the output
                6. Takes the first (earliest) time as check-in and last (latest) time as check-out
                7. If check-in and check-out are within 1 hour of each other:
                   - If time ≤ 11:00, keep only check-in
                   - If time > 11:00, keep only check-out
                8. Removes days with no clock-in or clock-out entries
                9. Returns a clean CSV with: Emp No., AC-No., Name, Date, Clock In, Clock Out
                10. Generates employee summary with:
                   - Total working days (days when any employee checked in)
                   - Total check-ins and check-outs
                   - Absences (working days - employee attendance days)
                   - Late check-ins (after 19:00)
                   - Early checkouts (before 04:00)
                   - Undertime for late arrivals and early departures
                   - Overtime for early arrivals and late departures
                   - Net overtime (overtime - undertime)
                """)
    
    else:
        st.info("👆 Please upload an Excel file to get started")
        
        # Show sample format
        with st.expander("📋 Expected File Format"):
            st.markdown("""
            Your Excel file should contain these columns:
            - **Emp No.**: Employee number
            - **AC-No.**: Access control number
            - **Name**: Employee name
            - **Date**: Date of attendance
            - **Clock-in/out Time**: Space-separated time entries (e.g., "19:07 04:15")
            - **Clock Out**: Single clock-out time (optional)
            """)

if __name__ == "__main__":
    main()