import csv
import json
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
SOLAR_INPUT = BASE_DIR / "filtered_solar_panel_data.json"
SEVEN_DAY_INPUT = BASE_DIR / "filtered_7day_values.json"

SMB_CSV = BASE_DIR / "smb_data_table.csv"
SMB_JSON = BASE_DIR / "smb_data_table.json"
SEVEN_DAY_CSV = BASE_DIR / "last_7day_values_table.csv"
SEVEN_DAY_JSON = BASE_DIR / "last_7day_values_table.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_csv(path: Path, rows: list[dict], columns: list[str]):
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)


def build_smb_rows(solar_data: dict) -> list[dict]:
    extraction = solar_data.get("data_extraction_info", {})
    extraction_date = extraction.get("extraction_date", "")
    last_update = extraction.get("last_update", "")

    timestamp = ""
    day_name = ""
    if last_update:
        try:
            dt = datetime.fromisoformat(last_update.replace("Z", "+00:00"))
            timestamp = dt.strftime("%H:%M:%S")
            day_name = dt.strftime("%A")
        except ValueError:
            pass

    smbboxes = solar_data.get("device_status", {}).get("smbboxes", {})

    rows = []
    for smb_name in sorted(smbboxes.keys()):
        smb_data = smbboxes.get(smb_name, {})
        power_w = float(smb_data.get("power_w", 0) or 0)
        rows.append(
            {
                "Date": extraction_date,
                "Day": day_name,
                "Time": timestamp,
                "SMB": smb_name,
                "Status": smb_data.get("status", "Unknown"),
                "Status Code": smb_data.get("status_code", 0),
                "User Status": smb_data.get("user_status", 0),
                "Power Output (W)": round(power_w, 2),
                "Power Output (kW)": round(power_w / 1000, 3),
            }
        )

    return rows


def build_last_7day_rows(seven_day_data: dict) -> list[dict]:
    daily_values = seven_day_data.get("daily_values", {})
    rows = []

    for date_key in sorted(daily_values.keys()):
        block = daily_values.get(date_key, {})
        date_formatted = block.get("date_formatted", "")
        records = block.get("records", [])

        for record in records:
            value_wh = float(record.get("value", 0) or 0)
            rows.append(
                {
                    "Date": record.get("date", date_key),
                    "Date Formatted": date_formatted,
                    "Time": record.get("time", ""),
                    "Start Value": record.get("start_value", 0),
                    "End Value": record.get("end_value", 0),
                    "Generation (Wh)": value_wh,
                    "Generation (kWh)": round(value_wh / 1000, 3),
                }
            )

    rows.sort(key=lambda r: (r["Date"], r["Time"]))
    return rows


def main():
    solar_data = load_json(SOLAR_INPUT)
    seven_day_data = load_json(SEVEN_DAY_INPUT)

    smb_rows = build_smb_rows(solar_data)
    smb_columns = [
        "Date",
        "Day",
        "Time",
        "SMB",
        "Status",
        "Status Code",
        "User Status",
        "Power Output (W)",
        "Power Output (kW)",
    ]

    seven_day_rows = build_last_7day_rows(seven_day_data)
    seven_day_columns = [
        "Date",
        "Date Formatted",
        "Time",
        "Start Value",
        "End Value",
        "Generation (Wh)",
        "Generation (kWh)",
    ]

    write_csv(SMB_CSV, smb_rows, smb_columns)
    write_csv(SEVEN_DAY_CSV, seven_day_rows, seven_day_columns)

    with SMB_JSON.open("w", encoding="utf-8") as f:
        json.dump({"table": smb_rows}, f, indent=2)

    with SEVEN_DAY_JSON.open("w", encoding="utf-8") as f:
        json.dump({"table": seven_day_rows}, f, indent=2)

    print(f"SMB table: {SMB_CSV.name} ({len(smb_rows)} rows)")
    print(f"SMB table JSON: {SMB_JSON.name}")
    print(f"7-day table: {SEVEN_DAY_CSV.name} ({len(seven_day_rows)} rows)")
    print(f"7-day table JSON: {SEVEN_DAY_JSON.name}")


if __name__ == "__main__":
    main()
