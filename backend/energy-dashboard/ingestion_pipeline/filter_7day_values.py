import json
from datetime import datetime

TARGET_TIME = "06:00:30"

# Load the filtered 30-day data
with open('filtered_30day_data.json', 'r') as f:
    data_30day = json.load(f)

print("=" * 60)
print("FILTERING LAST 7 DAYS - VALUES ONLY")
print("=" * 60)

# Extract last 7 days from daily_timeline
daily_timeline = data_30day.get('daily_timeline', {})

# Get dates sorted by days_ago
dates_sorted = sorted(
    daily_timeline.items(),
    key=lambda x: x[1]['days_ago']
)

# Get last 7 days
last_7_days = dates_sorted[:7]

print(f"\n📅 Processing {len(last_7_days)} days...\n")

# Build filtered data
filtered_data = {
    "extraction_info": {
        "source": "filtered_30day_data.json",
        "period": "Last 7 Days",
        "timestamp_filter": TARGET_TIME,
        "last_update": datetime.now().isoformat(),
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "fields_included": ["date", "start_value", "end_value", "value"]
    },
    "daily_values": {}
}

total_records = 0

# Process each day
for date_str, day_data in last_7_days:
    all_readings = day_data.get('all_readings', [])
    daily_records = []
    
    # Extract values from each reading
    for reading in all_readings:
        try:
            reading_time = reading.get('time')
            if reading_time != TARGET_TIME:
                continue

            record = {
                "date": reading.get('date'),
                "start_value": reading.get('start_value'),
                "end_value": reading.get('end_value'),
                "value": reading.get('generation_wh'),  # This is the generation value
                "time": reading_time
            }
            daily_records.append(record)
            total_records += 1
        except Exception as e:
            continue
    
    if daily_records:
        filtered_data['daily_values'][date_str] = {
            "date_formatted": day_data.get('date'),
            "records_count": len(daily_records),
            "records": daily_records
        }
        
        print(f"📅 {date_str}: {len(daily_records)} records")
        for record in daily_records:
            print(f"   ├─ {record['time']}: start={record['start_value']}, end={record['end_value']}, value={record['value']} Wh")

# Save filtered output
output_file = 'filtered_7day_values.json'
with open(output_file, 'w') as f:
    json.dump(filtered_data, f, indent=2)

print("\n" + "=" * 60)
print("✓ FILTERING COMPLETE")
print("=" * 60)

print(f"\n📊 SUMMARY:")
print(f"  Time Filter: {TARGET_TIME}")
print(f"  Total Records: {total_records}")
print(f"  Days Processed: {len(filtered_data['daily_values'])}")
print(f"  Output File: {output_file}\n")
