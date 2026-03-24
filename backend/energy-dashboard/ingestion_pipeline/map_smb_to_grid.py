import json
import csv
from datetime import datetime
from pathlib import Path

def map_smb_data_to_grid():
    """
    Maps SMB data from filtered_solar_panel_data.json into a data grid format
    matching the table structure: Date, Day, Time, Solar Units Generated (kWh), 
    Inverter Status, SMB1 (kWh), SMB2 (kWh), SMB3 (kWh), SMB4 (kWh), SMB5 (kWh)
    """
    
    # Load the solar panel data
    input_file = Path("filtered_solar_panel_data.json")
    if not input_file.exists():
        print("Error: filtered_solar_panel_data.json not found")
        return
    
    with open(input_file, 'r') as f:
        data = json.load(f)
    
    # Extract relevant information
    extraction_info = data.get("data_extraction_info", {})
    extraction_date = extraction_info.get("extraction_date", "")
    last_update = extraction_info.get("last_update", "")
    
    # Parse datetime
    if last_update:
        dt = datetime.fromisoformat(last_update.replace('Z', '+00:00'))
        time_str = dt.strftime("%H:%M:%S")
        day_str = dt.strftime("%A")  # Full day name
    else:
        time_str = ""
        day_str = ""
    
    # Get generation data
    generation_summary = data.get("generation_summary", {})
    today_generation_kwh = generation_summary.get("today_generation_kWh", 0)
    
    # Get inverter status
    device_status = data.get("device_status", {})
    plant_status = device_status.get("plant_status", {})
    inverter_status = plant_status.get("status", "Unknown")
    
    # Get SMB data - convert from Watts to kWh (power in Watts, so we'll use as-is for W or convert)
    smbboxes = device_status.get("smbboxes", {})
    
    # Create grid row
    grid_row = {
        "Date": extraction_date,
        "Day": day_str,
        "Time": time_str,
        "Solar Units Generated (kWh)": today_generation_kwh,
        "Inverter Status": inverter_status,
        "SMB1 (kW)": smbboxes.get("SMB_1", {}).get("power_w", 0) / 1000,  # Convert W to kW
        "SMB2 (kW)": smbboxes.get("SMB_2", {}).get("power_w", 0) / 1000,
        "SMB3 (kW)": smbboxes.get("SMB_3", {}).get("power_w", 0) / 1000,
        "SMB4 (kW)": smbboxes.get("SMB_4", {}).get("power_w", 0) / 1000,
        "SMB5 (kW)": smbboxes.get("SMB_5", {}).get("power_w", 0) / 1000,
    }
    
    print("\n=== SMB DATA MAPPED TO GRID ===\n")
    print(f"Date: {grid_row['Date']}")
    print(f"Day: {grid_row['Day']}")
    print(f"Time: {grid_row['Time']}")
    print(f"Solar Units Generated: {grid_row['Solar Units Generated (kWh)']} kWh")
    print(f"Inverter Status: {grid_row['Inverter Status']}")
    print(f"\nSMB Power Output (kW):")
    print(f"  SMB1: {grid_row['SMB1 (kW)']:.2f} kW")
    print(f"  SMB2: {grid_row['SMB2 (kW)']:.2f} kW")
    print(f"  SMB3: {grid_row['SMB3 (kW)']:.2f} kW")
    print(f"  SMB4: {grid_row['SMB4 (kW)']:.2f} kW")
    print(f"  SMB5: {grid_row['SMB5 (kW)']:.2f} kW")
    
    # Save to CSV
    output_csv = Path("smb_data_grid.csv")
    with open(output_csv, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=grid_row.keys())
        writer.writeheader()
        writer.writerow(grid_row)
    
    print(f"\n✓ Grid data saved to: {output_csv}")
    
    # Also save as JSON for reference
    output_json = Path("smb_data_grid.json")
    with open(output_json, 'w') as f:
        json.dump([grid_row], f, indent=2)
    
    print(f"✓ Grid data saved to: {output_json}")
    
    # Create summary statistics
    create_smb_summary(data)

def create_smb_summary(data):
    """Create a detailed SMB summary report"""
    device_status = data.get("device_status", {})
    smbboxes = device_status.get("smbboxes", {})
    
    print("\n=== SMB DETAILED STATUS ===\n")
    
    total_power = 0
    for smb_name, smb_data in smbboxes.items():
        power_w = smb_data.get("power_w", 0)
        status = smb_data.get("status", "Unknown")
        power_kw = power_w / 1000
        total_power += power_kw
        
        print(f"{smb_name}:")
        print(f"  Status: {status}")
        print(f"  Power Output: {power_kw:.2f} kW ({power_w} W)")
        print()
    
    print(f"Total System Power: {total_power:.2f} kW\n")

if __name__ == "__main__":
    map_smb_data_to_grid()
